"""Profitability domain — gross margin, profit growth, margin vs volume."""
from __future__ import annotations

from src.di import warehouse_api as W
from src.di.base import DomainReport, ExecutiveSummary
from src.di.engines import (
    insight_engine, make_metric, rank_recommendations, recommend, risk, scorecard_from_metrics,
)

DOMAIN = "profitability"


def _margin(row):
    billed = float(row["billed"]) or 0
    return 100.0 * float(row["profit"]) / billed if billed else 0.0


def analyze() -> DomainReport:
    s = W.sales_by_fy().set_index("fy")
    cur, pri = W.CURRENT_FY, W.PRIOR_FY
    margin = _margin(s.loc[cur]); margin_p = _margin(s.loc[pri])
    profit = float(s.loc[cur, "profit"]); profit_p = float(s.loc[pri, "profit"])
    margin_trend = [(fy, round(_margin(s.loc[fy]), 2)) for fy in s.index]
    profit_trend = [(fy, round(float(s.loc[fy, "profit"]))) for fy in s.index]

    metrics = [
        make_metric("gross_margin_pct", round(margin, 2), round(margin_p, 2), margin_trend),
        make_metric("gross_profit_inr", round(profit), round(profit_p), profit_trend),
        make_metric("profit_growth_pct", W.yoy_pct(profit, profit_p)),
    ]
    insights = insight_engine(metrics)

    # ---- root cause: did profit move on margin or on volume? ----
    root = []
    rev = float(s.loc[cur, "revenue"]); rev_p = float(s.loc[pri, "revenue"])
    if margin > margin_p:
        root.append(f"Gross margin expanded {margin-margin_p:+.2f}pp YoY "
                    f"({margin_p:.2f}% → {margin:.2f}%), lifting profit even where "
                    "revenue was flat.")
    elif margin < margin_p:
        root.append(f"Gross margin compressed {margin-margin_p:+.2f}pp YoY — a "
                    "margin-erosion signal to watch.")
    if profit > profit_p and rev <= rev_p:
        root.append("Profit rose despite flat/lower revenue — a pricing/mix gain, "
                    "not a volume gain.")

    # ---- risks ----
    risks = []
    if margin < margin_p:
        risks.append(risk("Margin erosion",
                          "Gross margin is declining year-on-year.",
                          min(100, 40 + (margin_p - margin) * 20),
                          {"margin_now": margin, "margin_prior": margin_p}))
    if margin < 4:
        risks.append(risk("Thin margin",
                          "Gross margin is below a sustainable threshold for "
                          "distribution overheads.", 55, {"margin": margin}))

    # ---- recommendations ----
    recs = []
    if margin >= margin_p:
        recs.append(recommend(
            "Codify the pricing/mix discipline that drove margin gains into a "
            "standard pricing policy.", rationale="Margin expanded YoY.",
            impact="high", effort="low", confidence=0.7))
    recs.append(recommend(
        "Run a product-level margin review to prune chronically low-margin SKUs.",
        rationale="Distribution margins are thin; SKU mix drives profitability.",
        impact="medium", effort="medium", confidence=0.6))

    sc = scorecard_from_metrics("Profitability", metrics,
                                weights={"gross_margin_pct": 2.0, "profit_growth_pct": 1.5})
    ex = ExecutiveSummary(
        what_happened=f"Gross margin {margin:.2f}% (profit ₹{profit:,.0f}), "
                      f"{margin-margin_p:+.2f}pp YoY.",
        why="Margin movement reflects pricing/mix more than volume.",
        business_impact=f"₹{profit-profit_p:,.0f} change in gross profit.",
        recommended_actions=[r.text for r in rank_recommendations(recs)[:2]],
        priority="high" if abs(margin - margin_p) >= 0.5 else "medium",
        confidence=0.7)

    return DomainReport(
        domain=DOMAIN,
        summary={"gross_margin_pct": round(margin, 2), "gross_profit": round(profit),
                 "margin_trend": margin_trend},
        metrics=metrics, insights=insights, root_causes=root, risks=risks,
        opportunities=[], recommendations=rank_recommendations(recs),
        scorecard=sc, executive_summary=ex)
