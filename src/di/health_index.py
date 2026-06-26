"""Business Health Index — a single composite 0-100 score for the whole business.

BHI = weighted average of component KPI health-scores, with weights configured in
config/health_index.yaml. Each component's score comes from that KPI's registry
thresholds, so the index is fully traceable to named, documented KPIs.
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
    components: list = field(default_factory=list)  # [{name,kpi,value,score,weight,contribution}]
    note: str = ""

    def to_dict(self):
        return {"score": self.score, "grade": self.grade,
                "components": self.components, "note": self.note}


def _metric_lookup(domain_reports) -> dict:
    """kpi_key -> Metric, across all domain reports."""
    out = {}
    for r in domain_reports:
        for m in r.metrics:
            out.setdefault(m.name, m)
    return out


def compute(domain_reports) -> HealthIndex:
    cfg = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    metrics = _metric_lookup(domain_reports)

    comps, total_w, weighted = [], 0.0, 0.0
    missing = []
    for name, spec in cfg["components"].items():
        kpi = spec["kpi"]; w = float(spec["weight"])
        m = metrics.get(kpi)
        sc = m.score if m else None
        if sc is None:
            missing.append(name)
            continue
        total_w += w
        weighted += sc * w
        comps.append({"name": name, "kpi": kpi,
                      "value": m.value, "score": round(sc, 1), "weight": w})
    score = round(weighted / total_w, 1) if total_w else 0.0
    # contribution after renormalisation
    for c in comps:
        c["contribution"] = round(c["score"] * c["weight"] / total_w, 1)
    comps.sort(key=lambda c: c["contribution"], reverse=True)
    note = ("Components excluded (no score): " + ", ".join(missing)) if missing else ""
    return HealthIndex(score=score, grade=grade(score), components=comps, note=note)
