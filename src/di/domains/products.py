"""Products domain — top/bottom sellers, concentration, pricing potential."""
from __future__ import annotations

from src.di import warehouse_api as W
from src.di.base import DomainReport, ExecutiveSummary
from src.di.engines import (
    insight_engine, make_metric, opportunity, rank_recommendations, recommend,
    risk, scorecard_from_metrics,
)

DOMAIN = "products"


def analyze() -> DomainReport:
    cur, pri = W.CURRENT_FY, W.PRIOR_FY
    p = W.product_perf(cur)
    pp = W.product_perf(pri)
    prof = W.product_profit(cur)
    active = len(p[p["revenue"] > 0]); active_p = len(pp[pp["revenue"] > 0])
    top10 = W.concentration_share(p["revenue"], 10)

    metrics = [
        make_metric("active_products", active, active_p),
        make_metric("top10_product_share_pct", top10),
    ]
    insights = insight_engine(metrics)

    # margin by product (billed vs cost)
    prof = prof.copy()
    prof["margin_pct"] = prof.apply(
        lambda r: 100 * r["profit"] / r["billed"] if r["billed"] else 0, axis=1)
    # high-volume, low-margin = pricing opportunity
    hv = prof[prof["billed"] > prof["billed"].quantile(0.9)]
    low_margin_hv = hv[hv["margin_pct"] < 3].sort_values("billed", ascending=False)

    root = [f"Top-10 products drive {top10:.1f}% of sales value; the long tail of "
            f"{active:,} active SKUs contributes the rest."]

    # ---- risks ----
    risks = []
    if top10 > 45:
        risks.append(risk("Product concentration",
                          f"Top-10 products are {top10:.1f}% of revenue.",
                          min(100, (top10 - 25) / (55 - 25) * 100),
                          {"top10_share_pct": top10}))

    # ---- opportunities ----
    opps = []
    if not low_margin_hv.empty:
        upside = float((low_margin_hv["billed"] * 0.01).sum())  # 1pt price = ~this
        opps.append(opportunity(
            "Pricing potential on high-volume, low-margin products",
            f"{len(low_margin_hv)} high-revenue SKUs run below 3% margin; a 1-point "
            f"price/discount correction is worth ≈₹{upside:,.0f}.",
            impact_inr=upside, confidence=0.5,
            evidence={"skus": int(len(low_margin_hv))}))

    # ---- recommendations ----
    recs = [recommend(
        "Review discount policy on the high-volume, low-margin SKUs identified.",
        rationale="A small price/discount correction on big sellers compounds.",
        impact="high", effort="medium", confidence=0.55),
        recommend("Rationalise the slow-moving long tail to cut carrying cost.",
                  rationale="A large SKU tail adds inventory and handling overhead.",
                  impact="medium", effort="medium", confidence=0.5)]

    sc = scorecard_from_metrics("Products", metrics,
                                weights={"top10_product_share_pct": 1.5,
                                         "active_products": 1.0})
    ex = ExecutiveSummary(
        what_happened=f"{active:,} products sold; top-10 concentration {top10:.1f}%.",
        why="Revenue rests on a core set of fast movers with a large slow tail.",
        business_impact="Pricing and SKU-mix decisions are the main profit levers here.",
        recommended_actions=[r.text for r in rank_recommendations(recs)[:2]],
        priority="medium", confidence=0.6)

    return DomainReport(
        domain=DOMAIN,
        summary={"active_products": active, "top10_share_pct": top10},
        metrics=metrics, insights=insights, root_causes=root, risks=risks,
        opportunities=opps, recommendations=rank_recommendations(recs),
        scorecard=sc, executive_summary=ex)
