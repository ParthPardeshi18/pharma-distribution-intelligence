"""Reusable Decision-Intelligence engines.

Generic, rule-driven helpers that every domain composes:
- make_metric():     build a scored Metric from a KPI key + current/prior values
- insight_engine():  auto-observations from metric movements & thresholds
- scorecard():       weighted 0-100 health score from a set of metrics
- rank_recommendations(): order by impact × confidence ÷ effort
- risk():/opportunity(): typed constructors with severity from score

Domains supply the *numbers and the domain-specific risk/opportunity/rec rules*;
these engines supply the consistent scoring, phrasing, and ranking.
"""
from __future__ import annotations

from src.di.base import (
    Insight, Metric, Opportunity, Recommendation, Risk, Scorecard, status_from_score,
)
from src.di.kpis import get_spec


def make_metric(key: str, value, prior=None, trend=None) -> Metric:
    spec = get_spec(key)
    from src.di.warehouse_api import yoy_pct
    yoy = yoy_pct(value, prior) if prior is not None else None
    sc = spec.score(value)
    return Metric(
        name=key, label=spec.label, value=value, unit=spec.unit,
        prior_value=prior, yoy_pct=yoy, trend=trend or [],
        score=sc, status=status_from_score(sc) if sc is not None else "info",
        description=spec.description,
    )


def insight_engine(metrics: list[Metric], threshold_pct: float = 5.0) -> list[Insight]:
    """Turn metric movements and threshold breaches into observations."""
    out: list[Insight] = []
    for m in metrics:
        spec = get_spec(m.name)
        # YoY movement insight
        if m.yoy_pct is not None and abs(m.yoy_pct) >= threshold_pct:
            up = m.yoy_pct > 0
            good_move = (up and spec.direction == "up_good") or \
                        (not up and spec.direction == "down_good")
            sev = "positive" if good_move else (
                "warning" if abs(m.yoy_pct) < 20 else "critical")
            direction = "increased" if up else "decreased"
            out.append(Insight(
                f"{m.label} {direction} {abs(m.yoy_pct):.1f}% YoY "
                f"(to {spec.format(m.value)}).",
                severity=sev if spec.direction != "neutral" else "info",
                evidence={"kpi": m.name, "value": m.value, "prior": m.prior_value,
                          "yoy_pct": m.yoy_pct}))
        # Threshold-level insight (only when a score exists and is poor/strong)
        if m.score is not None:
            if m.score <= 35:
                out.append(Insight(
                    f"{m.label} is in a weak range at {spec.format(m.value)} "
                    f"(health {m.score:.0f}/100).", severity="warning",
                    evidence={"kpi": m.name, "score": m.score}))
            elif m.score >= 85:
                out.append(Insight(
                    f"{m.label} is strong at {spec.format(m.value)} "
                    f"(health {m.score:.0f}/100).", severity="positive",
                    evidence={"kpi": m.name, "score": m.score}))
    return out


def scorecard(name: str, weighted: list[tuple[str, float, float]]) -> Scorecard:
    """weighted = [(label, score_0_100, weight), ...]; ignores None scores."""
    comp = [(lbl, sc, w) for lbl, sc, w in weighted if sc is not None]
    tw = sum(w for _, _, w in comp)
    score = round(sum(sc * w for _, sc, w in comp) / tw, 1) if tw else 0.0
    return Scorecard(name=name, score=score,
                     components=[[lbl, round(sc, 1), w] for lbl, sc, w in comp])


def scorecard_from_metrics(name: str, metrics: list[Metric],
                           weights: dict | None = None) -> Scorecard:
    weights = weights or {}
    weighted = [(m.label, m.score, weights.get(m.name, 1.0))
                for m in metrics if m.score is not None]
    return scorecard(name, weighted)


def rank_recommendations(recs: list[Recommendation]) -> list[Recommendation]:
    return sorted(recs, key=lambda r: r.priority_score, reverse=True)


def risk(name: str, description: str, score: float, evidence: dict | None = None) -> Risk:
    sev = "critical" if score >= 70 else ("warning" if score >= 40 else "info")
    return Risk(name=name, description=description, score=round(score, 1),
                severity=sev, evidence=evidence or {})


def opportunity(name, description, impact_inr=None, confidence=0.5,
                evidence=None) -> Opportunity:
    return Opportunity(name=name, description=description,
                       potential_impact_inr=impact_inr, confidence=confidence,
                       evidence=evidence or {})


def recommend(text, rationale="", impact="medium", effort="medium",
              confidence=0.6) -> Recommendation:
    return Recommendation(text=text, rationale=rationale, impact=impact,
                          effort=effort, confidence=confidence)
