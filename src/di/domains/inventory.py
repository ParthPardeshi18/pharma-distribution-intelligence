"""Inventory domain — value, turnover, days on hand, buildup/dead-stock signals."""
from __future__ import annotations

from src.di import warehouse_api as W
from src.di.base import DomainReport, ExecutiveSummary
from src.di.engines import (
    insight_engine, make_metric, opportunity, rank_recommendations, recommend,
    risk, scorecard_from_metrics,
)

DOMAIN = "inventory"


def analyze() -> DomainReport:
    cur, pri = W.CURRENT_FY, W.PRIOR_FY
    s = W.sales_by_fy().set_index("fy")
    cogs = float(s.loc[cur, "cost"]); cogs_p = float(s.loc[pri, "cost"])
    inv = W.inventory_value(cur); inv_p = W.inventory_value(pri)
    turnover = round(cogs / inv, 1) if inv else None
    turnover_p = round(cogs_p / inv_p, 1) if inv_p else None
    days = round(365 / turnover, 0) if turnover else None
    days_p = round(365 / turnover_p, 0) if turnover_p else None

    metrics = [
        make_metric("inventory_value_inr", round(inv), round(inv_p)),
        make_metric("inventory_turnover", turnover, turnover_p),
        make_metric("inventory_days", days, days_p),
    ]
    insights = insight_engine(metrics)

    root = []
    if turnover and turnover_p:
        if turnover > turnover_p:
            root.append(f"Inventory turnover improved {turnover_p}x→{turnover}x "
                        f"(~{days:.0f} days on hand), freeing working capital.")
        elif turnover < turnover_p:
            root.append(f"Inventory turnover slowed {turnover_p}x→{turnover}x — stock "
                        "is sitting longer.")
    if inv > inv_p * 1.1:
        root.append(f"Closing inventory grew {W.yoy_pct(inv, inv_p):+.1f}% YoY to "
                    f"₹{inv:,.0f} — watch for buildup outpacing sales.")

    # ---- risks ----
    risks = []
    if turnover and turnover < 6:
        risks.append(risk("Slow inventory turnover",
                          f"Turnover of {turnover}x (~{days:.0f} days) ties up cash.",
                          min(100, (6 - turnover) * 18), {"turnover": turnover}))
    if inv > inv_p * 1.15:
        risks.append(risk("Inventory buildup",
                          f"Stock value up {W.yoy_pct(inv, inv_p):+.1f}% YoY.",
                          min(100, 30 + (W.yoy_pct(inv, inv_p) or 0)), {"inventory": inv}))

    # ---- opportunities ----
    opps = []
    if days and days > 45:
        target_days = 40
        release = inv * (1 - target_days / days)
        opps.append(opportunity(
            "Release cash by trimming inventory days",
            f"Cutting days on hand from {days:.0f} to {target_days} would free "
            f"≈₹{release:,.0f} of working capital.",
            impact_inr=release, confidence=0.5, evidence={"days": days}))

    recs = [recommend(
        "Set reorder levels by SKU velocity to cut slow-mover stock.",
        rationale="Right-sizing stock to demand releases cash without stockouts.",
        impact="high", effort="medium", confidence=0.6)]

    sc = scorecard_from_metrics("Inventory", metrics,
                                weights={"inventory_turnover": 2.0, "inventory_days": 1.5})
    ex = ExecutiveSummary(
        what_happened=f"Closing inventory ₹{inv:,.0f}; turnover {turnover}x "
                      f"(~{days:.0f} days).",
        why="Turnover reflects how tightly stock is matched to demand.",
        business_impact="Every excess day of stock is cash locked up.",
        recommended_actions=[r.text for r in rank_recommendations(recs)[:2]],
        priority="medium", confidence=0.6)

    return DomainReport(
        domain=DOMAIN,
        summary={"inventory_value": round(inv), "turnover": turnover, "days": days},
        metrics=metrics, insights=insights, root_causes=root, risks=risks,
        opportunities=opps, recommendations=rank_recommendations(recs),
        scorecard=sc, executive_summary=ex)
