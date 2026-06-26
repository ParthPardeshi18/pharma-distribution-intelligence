"""Reusable entity-resolution service.

Resolves free-text transaction names (customer/supplier/product) to master
identities, producing a STABLE key, a resolution TIER, and a CONFIDENCE score.

Governance guarantees (requirement: never silently merge uncertain matches):
- Manual overrides win and are honoured first.
- Exact normalized match -> confidence 1.0.
- Fuzzy match auto-accepted ONLY when score >= auto_accept AND unambiguous.
- Scores in the review band go to a REVIEW QUEUE and are treated as UNRESOLVED
  until a human confirms (or adds an override) — they are never merged.
- Anything below the floor gets its own stable surrogate key (analysis proceeds).

Files (gitignored with data/):
- data/reference/<entity>_overrides.csv   norm_name,master_name   (human-editable)
- data/secure/<entity>_match_review.csv   review queue (contains real names)
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

import pandas as pd
import yaml

from src.anonymise import normalize
from src.utils import CONFIG_DIR, REFERENCE_DIR, SECURE_DIR

try:
    from rapidfuzz import fuzz, process
    _HAVE_RAPIDFUZZ = True
except Exception:  # pragma: no cover
    _HAVE_RAPIDFUZZ = False

_SINGLE_LETTER_TOKEN = re.compile(r"\b[A-Z]\b")


@dataclass
class Resolution:
    source_norm: str
    canonical_norm: str   # master norm if matched, else own norm
    tier: str             # manual | master_exact | master_fuzzy | unresolved | review
    confidence: float     # 0–1
    matched_master: str | None


def stable_key(entity_type: str, canonical_norm: str) -> int:
    """Deterministic surrogate key from the resolved identity.

    Kept under 2**52 so it is representable EXACTLY as a float64. This matters
    because a fact key column containing any null is coerced to float64 by pandas;
    a 60-bit key would lose precision there and break joins to the int64 dimension.
    2**52 leaves ample space (~4.5e15) for tens of thousands of entities with
    negligible collision risk.
    """
    h = hashlib.sha1(f"{entity_type}::{canonical_norm}".encode("utf-8")).hexdigest()
    return int(h[:15], 16) % (2 ** 52)  # float64-safe, stable across runs


class EntityResolver:
    def __init__(self, entity_type: str, config_path=None):
        cfg = yaml.safe_load(
            (config_path or (CONFIG_DIR / "entity_resolution.yaml")).read_text(encoding="utf-8"))
        self.entity_type = entity_type
        self.auto_accept = float(cfg["auto_accept"])
        self.review_floor = float(cfg["review_floor"])
        self.ambiguity_margin = float(cfg["ambiguity_margin"])
        self.strip_markers = bool(cfg.get("strip_route_markers", True))
        self._review_rows: list[dict] = []
        self.overrides = self._load_overrides()

    # ------------------------------------------------------------------ #
    def normalize_match(self, name: str) -> str:
        """Match key: normalize then optionally drop single-letter route markers."""
        n = normalize(name)
        if self.strip_markers:
            n = _SINGLE_LETTER_TOKEN.sub(" ", n)
            n = re.sub(r"\s+", " ", n).strip()
        return n

    def _load_overrides(self) -> dict[str, str]:
        path = REFERENCE_DIR / f"{self.entity_type}_overrides.csv"
        if not path.exists():
            return {}
        df = pd.read_csv(path, dtype=str).fillna("")
        return {self.normalize_match(r["norm_name"]): self.normalize_match(r["master_name"])
                for _, r in df.iterrows() if r.get("master_name")}

    # ------------------------------------------------------------------ #
    def resolve(self, source_names, master_names) -> dict[str, Resolution]:
        """Resolve each distinct source name. Returns {source_norm: Resolution}."""
        # master norm -> representative master norm (dedup)
        master_norms = {}
        for m in master_names:
            mn = self.normalize_match(m)
            if mn:
                master_norms.setdefault(mn, mn)
        master_keys = list(master_norms)
        # blocking by first token for fuzzy efficiency
        blocks: dict[str, list[str]] = {}
        for mn in master_keys:
            blocks.setdefault(mn.split(" ")[0], []).append(mn)

        results: dict[str, Resolution] = {}
        for src in source_names:
            sn = self.normalize_match(src)
            if not sn or sn in results:
                continue
            results[sn] = self._resolve_one(sn, master_norms, blocks)
        return results

    def _resolve_one(self, sn, master_norms, blocks) -> Resolution:
        # 1) manual override
        if sn in self.overrides:
            tgt = self.overrides[sn]
            return Resolution(sn, tgt, "manual", 1.0, tgt)
        # 2) exact
        if sn in master_norms:
            return Resolution(sn, sn, "master_exact", 1.0, sn)
        # 3) fuzzy within block (+ first-token block)
        candidates = blocks.get(sn.split(" ")[0], [])
        if not candidates:
            candidates = list(master_norms)  # fall back to full set
        best, second = self._best_two(sn, candidates)
        if best is None:
            return Resolution(sn, sn, "unresolved", 0.0, None)
        best_name, best_score = best
        ambiguous = second is not None and (best_score - second[1]) < self.ambiguity_margin
        if best_score >= self.auto_accept and not ambiguous:
            return Resolution(sn, best_name, "master_fuzzy", best_score / 100.0, best_name)
        if best_score >= self.review_floor:
            self._review_rows.append({
                "source_norm": sn, "best_master": best_name,
                "score": round(best_score, 1),
                "second_master": second[0] if second else "",
                "second_score": round(second[1], 1) if second else "",
                "ambiguous": ambiguous,
            })
            # treated as UNRESOLVED until a human confirms — never merged
            return Resolution(sn, sn, "review", best_score / 100.0, None)
        return Resolution(sn, sn, "unresolved", best_score / 100.0, None)

    def _best_two(self, sn, candidates):
        if not candidates:
            return None, None
        if _HAVE_RAPIDFUZZ:
            top = process.extract(sn, candidates, scorer=fuzz.token_set_ratio, limit=2)
            best = (top[0][0], top[0][1]) if top else None
            second = (top[1][0], top[1][1]) if len(top) > 1 else None
            return best, second
        # pure-python Jaccard fallback
        sset = set(sn.split())
        scored = sorted(
            ((c, 100.0 * len(sset & set(c.split())) / max(1, len(sset | set(c.split()))))
             for c in candidates), key=lambda x: x[1], reverse=True)
        best = scored[0] if scored else None
        second = scored[1] if len(scored) > 1 else None
        return best, second

    # ------------------------------------------------------------------ #
    def flush_review_queue(self) -> int:
        """Write the review queue (contains real names -> secure, gitignored)."""
        if not self._review_rows:
            return 0
        SECURE_DIR.mkdir(parents=True, exist_ok=True)
        path = SECURE_DIR / f"{self.entity_type}_match_review.csv"
        pd.DataFrame(self._review_rows).to_csv(path, index=False, encoding="utf-8")
        return len(self._review_rows)

    @staticmethod
    def summarize(resolutions: dict[str, Resolution]) -> dict[str, int]:
        out: dict[str, int] = {}
        for r in resolutions.values():
            out[r.tier] = out.get(r.tier, 0) + 1
        return out
