"""Territory domain — area concentration and underperformers.

Note: customer→area linkage is weak in the ERP master, so territory analysis uses
the ERP's own Area_Sales aggregate (via the adapter). Documented as a limitation.
"""
from __future__ import annotations

from src.di import warehouse_api as W
from src.di.base import DomainReport, ExecutiveSummary
from src.di.engines import (
    insight_engine, make_metric, opportunity, rank_recommendations, recommend,
    risk, scorecard_from_metrics,
)

DOMAIN = "territory"


def analyze() -> DomainReport:
    cur, pri = W.CURRENT_FY, W.PRIOR_FY
    t = W.territory_sales(cur)
    tp = W.territory_sales(pri)
    if t.empty:
        return DomainReport(domain=DOMAIN,
                            summary={"note": "No territory data available."},
                            root_causes=["Area_Sales report unavailable for this FY."])
    t = t.groupby("area_name", as_index=False)["revenue"].sum()
    active = len(t[t["revenue"] > 0])
    active_p = len(tp.groupby("area_name")["revenue"].sum().pipe(lambda s: s[s > 0])) \
        if not tp.empty else None
    top5 = W.concentration_share(t["revenue"], 5)
    total = float(t["revenue"].sum())

    metrics = [
        make_metric("active_territories", active, active_p),
        make_metric("top5_territory_share_pct", top5),
    ]
    insights = insight_engine(metrics)

    ranked = t.sort_values("revenue", ascending=False)
    top = ranked.head(3); bottom = ranked[ranked["revenue"] > 0].tail(3)
    root = [f"Top-5 of {active} areas drive {top5:.1f}% of ₹{total:,.0f} area sales."]

    risks = []
    if top5 > 70:
        risks.append(risk("Territory concentration",
                          f"Top-5 areas are {top5:.1f}% of sales.",
                          min(100, (top5 - 45) / (80 - 45) * 100),
                          {"top5_share_pct": top5}))

    opps = [opportunity(
        "Develop underperforming territories",
        f"The smallest active areas (e.g. {', '.join(bottom['area_name'].astype(str).head(3))}) "
        "are well below the leaders — targeted coverage could lift them.",
        confidence=0.4, evidence={"bottom_areas": bottom["area_name"].astype(str).tolist()})]

    recs = [recommend(
        "Run a coverage/route review for the bottom-quartile territories.",
        rationale="Low-performing areas may reflect coverage gaps, not demand gaps.",
        impact="medium", effort="medium", confidence=0.5)]

    sc = scorecard_from_metrics("Territory", metrics,
                                weights={"top5_territory_share_pct": 1.5,
                                         "active_territories": 1.0})
    ex = ExecutiveSummary(
        what_happened=f"{active} active areas; top-5 concentration {top5:.1f}%.",
        why="Sales are geographically concentrated around the core market.",
        business_impact="Geographic diversification is a growth lever.",
        recommended_actions=[r.text for r in rank_recommendations(recs)[:2]],
        priority="low", confidence=0.5)

    return DomainReport(
        domain=DOMAIN,
        summary={"active_territories": active, "top5_share_pct": top5,
                 "top_areas": top["area_name"].astype(str).tolist()},
        metrics=metrics, insights=insights, root_causes=root, risks=risks,
        opportunities=opps, recommendations=rank_recommendations(recs),
        scorecard=sc, executive_summary=ex)
