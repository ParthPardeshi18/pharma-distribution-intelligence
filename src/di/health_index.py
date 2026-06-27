"""Business Health Index — a single composite 0-100 score for the whole business.

BHI = weighted average of component KPI health-scores. Weighting is a configurable
PROFILE (config/health_index.yaml): balanced, conservative, growth,
cash_preservation, profit_optimization, custom. Each component's score comes from
that KPI's registry thresholds, so the index is fully traceable to named KPIs.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import yaml

from src.di.base import grade
from src.utils import CONFIG_DIR

CONFIG_PATH = CONFIG_DIR / "health_index.yaml"


@dataclass
class HealthIndex:
    score: float
    grade: str
    profile: str
    components: list = field(default_factory=list)
    note: str = ""

    def to_dict(self):
        return {"score": self.score, "grade": self.grade, "profile": self.profile,
                "components": self.components, "note": self.note}


def _load_config() -> dict:
    return yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))


def list_profiles() -> list[str]:
    return list(_load_config().get("profiles", {}).keys())


def _metric_lookup(domain_reports) -> dict:
    out = {}
    for r in domain_reports:
        for m in r.metrics:
            out.setdefault(m.name, m)
    return out


def compute(domain_reports, profile: str | None = None) -> HealthIndex:
    cfg = _load_config()
    profile = profile or cfg.get("default_profile", "balanced")
    weights = cfg["profiles"][profile]
    comp_kpi = cfg["components"]
    metrics = _metric_lookup(domain_reports)

    comps, total_w, weighted, missing = [], 0.0, 0.0, []
    for name, w in weights.items():
        kpi = comp_kpi.get(name)
        m = metrics.get(kpi) if kpi else None
        sc = m.score if m else None
        if sc is None:
            missing.append(name)
            continue
        total_w += w
        weighted += sc * w
        comps.append({"name": name, "kpi": kpi, "value": m.value,
                      "score": round(sc, 1), "weight": w})
    score = round(weighted / total_w, 1) if total_w else 0.0
    for c in comps:
        c["contribution"] = round(c["score"] * c["weight"] / total_w, 1)
    comps.sort(key=lambda c: c["contribution"], reverse=True)
    note = ("Components excluded (no score): " + ", ".join(missing)) if missing else ""
    return HealthIndex(score=score, grade=grade(score), profile=profile,
                       components=comps, note=note)


def compute_all_profiles(domain_reports) -> dict[str, float]:
    """BHI under every profile — for the sensitivity table in the report."""
    return {p: compute(domain_reports, p).score for p in list_profiles()}
