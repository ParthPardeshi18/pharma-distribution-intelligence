"""Suppliers domain — spend, dependency, negotiation opportunities."""
from __future__ import annotations

from src.di import warehouse_api as W
from src.di.base import DomainReport, ExecutiveSummary
from src.di.engines import (
    insight_engine, make_metric, opportunity, rank_recommendations, recommend,
    risk, scorecard_from_metrics,
)

DOMAIN = "suppliers"


def analyze() -> DomainReport:
    cur, pri = W.CURRENT_FY, W.PRIOR_FY
    s = W.purchases_by_supplier(cur)
    sp = W.purchases_by_supplier(pri)
    active = len(s); active_p = len(sp)
    top5 = W.concentration_share(s["spend"], 5)
    top5_p = W.concentration_share(sp["spend"], 5)
    total_spend = float(s["spend"].sum())

    metrics = [
        make_metric("active_suppliers", active, active_p),
        make_metric("top5_supplier_share_pct", top5, top5_p),
    ]
    insights = insight_engine(metrics)

    root = [f"Top-5 suppliers account for {top5:.1f}% of ₹{total_spend:,.0f} purchase "
            f"spend across {active:,} suppliers."]

    # ---- risks ----
    risks = []
    if top5 > 50:
        risks.append(risk("Supplier dependency",
                          f"Top-5 suppliers are {top5:.1f}% of purchases — a "
                          "continuity and bargaining-power risk.",
                          min(100, (top5 - 40) / (75 - 40) * 100),
                          {"top5_share_pct": top5}))

    # ---- opportunities ----
    opps = []
    if not s.empty:
        big = s.head(3)
        big_spend = float(big["spend"].sum())
        opps.append(opportunity(
            "Volume-based negotiation with largest suppliers",
            f"The top-3 suppliers represent ₹{big_spend:,.0f} of annual spend; a "
            f"1% improvement in terms is worth ≈₹{big_spend*0.01:,.0f}.",
            impact_inr=big_spend * 0.01, confidence=0.6,
            evidence={"top_suppliers": big["supplier_code"].tolist()}))

    recs = [recommend(
        "Open annual rate/scheme negotiations with the top-3 suppliers.",
        rationale="Concentrated spend gives leverage; small term gains compound.",
        impact="high", effort="low", confidence=0.65)]
    if top5 > 50:
        recs.append(recommend(
            "Qualify a secondary source for the most concentrated categories.",
            rationale="Reduce single-supplier continuity risk.",
            impact="medium", effort="high", confidence=0.5))

    sc = scorecard_from_metrics("Suppliers", metrics,
                                weights={"top5_supplier_share_pct": 2.0,
                                         "active_suppliers": 1.0})
    ex = ExecutiveSummary(
        what_happened=f"{active:,} active suppliers; top-5 dependency {top5:.1f}%.",
        why="Procurement is concentrated among a few principals.",
        business_impact="Negotiation leverage and continuity risk both sit with the top suppliers.",
        recommended_actions=[r.text for r in rank_recommendations(recs)[:2]],
        priority="high" if top5 > 60 else "medium", confidence=0.6)

    return DomainReport(
        domain=DOMAIN,
        summary={"active_suppliers": active, "top5_share_pct": top5,
                 "total_spend": round(total_spend)},
        metrics=metrics, insights=insights, root_causes=root, risks=risks,
        opportunities=opps, recommendations=rank_recommendations(recs),
        scorecard=sc, executive_summary=ex)
