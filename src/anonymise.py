"""PII anonymisation layer — the foundation of the SHAREABLE output.

Builds a SECURE, append-only lookup mapping real identities (customer / supplier
/ salesman names) to stable anonymous codes (Customer_0001 …). The lookup is the
ONLY bridge between real identities and codes and lives in data/secure/
(gitignored). Analysis can then run on codes so nothing personal is ever shared.

Design principles
- Append-only & stable: once an identity gets a code, it keeps it forever, even
  as future ERP exports add new identities. Safe to re-run any time.
- Config-driven: which columns are which entity comes from
  config/anonymisation.yaml, never hardcoded.
- Deterministic order: new codes assigned in sorted order for reproducibility.

CLI:
  python -m src.anonymise --build     # (re)build lookup from data/raw, print stats + masked sample
  python -m src.anonymise --status    # show lookup stats only
"""
from __future__ import annotations

import argparse
import re

import pandas as pd
import yaml

from src.utils import (
    CONFIG_DIR,
    RAW_DIR,
    SECURE_DIR,
    mask_email,
    mask_id,
    mask_mobile,
    mask_text_blob,
)

LOOKUP_PATH = SECURE_DIR / "pii_lookup.csv"
CONFIG_PATH = CONFIG_DIR / "anonymisation.yaml"


def load_config() -> dict:
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))


# ERP reports embed footer/summary rows ("Totals:", "Opening balance") inside the
# data area. These are NOT identities — exclude them from the lookup. Phase 2
# cleaning strips them from the data itself; this keeps the lookup clean now.
JUNK_IDENTITIES = {
    "TOTAL", "TOTALS", "GRAND TOTAL", "SUB TOTAL", "SUBTOTAL",
    "OPENING", "CLOSING", "OPENING BALANCE", "CLOSING BALANCE",
    "BALANCE", "NAN", "NONE", "NULL", "CASH", "N A", "NA",
}


def is_junk_identity(norm_key: str) -> bool:
    """True for footer/summary labels and values lacking real name content."""
    if not norm_key or norm_key in JUNK_IDENTITIES:
        return True
    if not re.search(r"[A-Z]", norm_key):   # no letters → not a name
        return True
    if len(norm_key.replace(" ", "")) < 3:  # too short to be an identity
        return True
    return False


def normalize(value: str) -> str:
    """Normalised matching key: upper, collapse whitespace, strip punctuation.
    Used to dedupe trivially-different spellings of the SAME identity.
    (Full fuzzy entity resolution comes in Phase 1/2; this catches exact &
    whitespace/case variants.)"""
    s = str(value).upper().strip()
    s = re.sub(r"[^A-Z0-9 ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _columns_for(df: pd.DataFrame, hints: list[str]) -> list[str]:
    return [c for c in df.columns
            if any(h in str(c).lower() for h in hints)]


def collect_identities(cfg: dict) -> dict[str, set[str]]:
    """Scan every raw file, gather distinct real values per entity type."""
    from src.utils import read_erp_excel  # local import to avoid cycle at import time

    found: dict[str, set[str]] = {et: set() for et in cfg["entity_types"]}
    for path in sorted(RAW_DIR.rglob("*.xlsx")):
        try:
            df = read_erp_excel(path)
        except Exception:
            continue
        for et, spec in cfg["entity_types"].items():
            for col in _columns_for(df, spec["column_hints"]):
                for v in df[col].dropna().astype(str):
                    v = v.strip()
                    if v and not is_junk_identity(normalize(v)):
                        found[et].add(v)
    return found


def load_lookup() -> pd.DataFrame:
    if LOOKUP_PATH.exists():
        return pd.read_csv(LOOKUP_PATH, dtype=str).fillna("")
    return pd.DataFrame(columns=["entity_type", "norm_key", "real_value", "anon_code"])


def build_lookup(print_sample: bool = True) -> pd.DataFrame:
    cfg = load_config()
    width = int(cfg.get("code_width", 4))
    SECURE_DIR.mkdir(parents=True, exist_ok=True)

    existing = load_lookup()
    # next counter per entity (append-only: continue from current max)
    counters: dict[str, int] = {}
    for et, spec in cfg["entity_types"].items():
        codes = existing.loc[existing.entity_type == et, "anon_code"]
        nums = [int(re.sub(r"\D", "", c) or 0) for c in codes]
        counters[et] = max(nums) if nums else 0

    known_keys = set(zip(existing.entity_type, existing.norm_key))
    found = collect_identities(cfg)

    new_rows = []
    for et, spec in cfg["entity_types"].items():
        prefix = spec["code_prefix"]
        # map norm_key -> first real spelling seen (sorted for determinism)
        by_key: dict[str, str] = {}
        for real in sorted(found[et]):
            by_key.setdefault(normalize(real), real)
        for norm_key, real in sorted(by_key.items()):
            if (et, norm_key) in known_keys:
                continue
            counters[et] += 1
            code = f"{prefix}_{counters[et]:0{width}d}"
            new_rows.append({"entity_type": et, "norm_key": norm_key,
                             "real_value": real, "anon_code": code})

    lookup = pd.concat([existing, pd.DataFrame(new_rows)], ignore_index=True)
    lookup.to_csv(LOOKUP_PATH, index=False, encoding="utf-8")

    print(f"PII lookup written: {LOOKUP_PATH}")
    print(f"  (+{len(new_rows)} new identities this run)")
    for et in cfg["entity_types"]:
        n = int((lookup.entity_type == et).sum())
        print(f"  {et:10s}: {n:>5d} identities")

    if print_sample and not lookup.empty:
        print("\nMasked sample of the lookup (real values masked here for display only):")
        sample = lookup.groupby("entity_type", group_keys=False).head(2).copy()
        sample["real_value"] = sample["real_value"].map(lambda s: mask_text_blob(str(s)[:1] + "***"))
        print(sample[["entity_type", "real_value", "anon_code"]].to_string(index=False))
    return lookup


def load_code_map(entity_type: str) -> dict[str, str]:
    """norm_key -> anon_code for one entity type (from the secure lookup).
    Used by the warehouse to assign anonymous dimension codes (customer/supplier/
    salesman). Products/companies/areas are not PII and keep real names."""
    lookup = load_lookup()
    sub = lookup[lookup.entity_type == entity_type]
    return dict(zip(sub.norm_key, sub.anon_code))


def _build_maps(cfg: dict) -> dict[str, dict[str, str]]:
    lookup = load_lookup()
    maps: dict[str, dict[str, str]] = {}
    for et in cfg["entity_types"]:
        sub = lookup[lookup.entity_type == et]
        maps[et] = dict(zip(sub.norm_key, sub.anon_code))
    return maps


def anonymise_df(df: pd.DataFrame, cfg: dict | None = None,
                 maps: dict | None = None) -> pd.DataFrame:
    """Return a copy with identities replaced by codes and other PII masked.
    Unmapped identities become '<entity>_UNMAPPED' (never the real value)."""
    cfg = cfg or load_config()
    maps = maps or _build_maps(cfg)
    out = df.copy()

    for et, spec in cfg["entity_types"].items():
        for col in _columns_for(out, spec["column_hints"]):
            out[col] = out[col].map(
                lambda v: maps[et].get(normalize(v),
                                       f"{spec['code_prefix']}_UNMAPPED")
                if pd.notna(v) and str(v).strip() else v)

    for col in out.columns:
        low = str(col).lower()
        if any(h in low for h in cfg["pii_mask"]["mobile"]):
            out[col] = out[col].map(mask_mobile)
        elif any(h in low for h in cfg["pii_mask"]["email"]):
            out[col] = out[col].map(mask_email)
        elif any(h in low for h in cfg["pii_mask"]["id"]):
            out[col] = out[col].map(mask_id)
        elif any(h in low for h in cfg["pii_mask"]["address"]):
            out[col] = out[col].map(lambda v: mask_text_blob(str(v)) if pd.notna(v) else v)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="PII anonymisation layer")
    ap.add_argument("--build", action="store_true", help="rebuild lookup from data/raw")
    ap.add_argument("--status", action="store_true", help="show lookup stats")
    args = ap.parse_args()

    if args.build or not args.status:
        build_lookup()
    else:
        lk = load_lookup()
        print(f"Lookup rows: {len(lk)}")
        print(lk.entity_type.value_counts().to_string() if not lk.empty else "(empty)")


if __name__ == "__main__":
    main()
