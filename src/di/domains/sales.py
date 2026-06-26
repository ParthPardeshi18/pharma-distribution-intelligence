"""Sales domain — revenue level, growth, volume vs price, multi-year trend."""
from __future__ import annotations

from src.di import warehouse_api as W
from src.di.base import DomainReport, ExecutiveSummary
from src.di.engines import (
    insight_engine, make_metric, rank_recommendations, recommend, risk, scorecard_from_metrics,
)

DOMAIN = "sales"


def analyze() -> DomainReport:
    s = W.sales_by_fy().set_index("fy")
    cur, pri = W.CURRENT_FY, W.PRIOR_FY
    rev = float(s.loc[cur, "revenue"]); rev_p = float(s.loc[pri, "revenue"])
    bills = int(s.loc[cur, "bills"]); bills_p = int(s.loc[pri, "bills"])
    abv = rev / bills if bills else 0
    abv_p = rev_p / bills_p if bills_p else 0
    rev_trend = [(fy, round(float(s.loc[fy, "revenue"]))) for fy in s.index]

    metrics = [
        make_metric("revenue_inr", round(rev), round(rev_p), rev_trend),
        make_metric("revenue_growth_pct", W.yoy_pct(rev, rev_p)),
        make_metric("avg_bill_value", round(abv), round(abv_p)),
        make_metric("bill_count", bills, bills_p),
    ]
    insights = insight_engine(metrics)

    # ---- root cause: decompose revenue change into volume vs price ----
    root = []
    d_rev = rev - rev_p
    d_vol = (bills - bills_p) * abv_p          # volume effect at last year's price
    d_price = (abv - abv_p) * bills            # price/mix effect at this year's volume
    if abs(d_rev) > 1:
        root.append(
            f"Revenue moved ₹{d_rev:,.0f} YoY: ≈₹{d_vol:,.0f} from bill volume "
            f"({bills-bills_p:+,} bills) and ≈₹{d_price:,.0f} from average bill "
            f"value ({W.yoy_pct(abv, abv_p):+.1f}%).")

    # ---- multi-year context ----
    peak = max(rev_trend, key=lambda x: x[1])
    if rev < peak[1] * 0.98:
        root.append(f"Revenue (₹{rev:,.0f}) is still below the {peak[0]} peak of "
                    f"₹{peak[1]:,.0f}, despite the recent recovery.")

    # ---- risks ----
    risks = []
    g = W.yoy_pct(rev, rev_p) or 0
    if g < 0:
        risks.append(risk("Sales decline",
                          "Revenue is contracting year-on-year.",
                          min(100, 40 + abs(g) * 3), {"growth_pct": g}))

    # ---- opportunities & recommendations ----
    opps, recs = [], []
    if abv < abv_p:
        recs.append(recommend(
            "Lift average bill value via basket/cross-sell prompts at billing.",
            rationale="Average bill value fell YoY, dragging revenue.",
            impact="high", effort="medium", confidence=0.6))
    if g > 0:
        recs.append(recommend(
            "Protect the recovery: secure top-decile customers with service SLAs.",
            rationale="Revenue is recovering; retention compounds the gain.",
            impact="high", effort="low", confidence=0.65))

    sc = scorecard_from_metrics("Sales", metrics,
                                weights={"revenue_growth_pct": 2.0, "bill_count": 1.0,
                                         "avg_bill_value": 1.0})
    ex = ExecutiveSummary(
        what_happened=f"Revenue {'grew' if g>=0 else 'fell'} {abs(g):.1f}% YoY to ₹{rev:,.0f} "
                      f"across {bills:,} bills.",
        why="Driven by " + ("higher" if bills >= bills_p else "lower") +
            " bill volume and " + ("higher" if abv >= abv_p else "lower") +
            " average bill value.",
        business_impact=f"₹{d_rev:,.0f} change in top-line revenue.",
        recommended_actions=[r.text for r in rank_recommendations(recs)[:2]],
        priority="high" if abs(g) >= 8 else "medium",
        confidence=0.7)

    return DomainReport(
        domain=DOMAIN,
        summary={"revenue": round(rev), "growth_pct": g, "bills": bills,
                 "avg_bill_value": round(abv), "trend": rev_trend},
        metrics=metrics, insights=insights, root_causes=root, risks=risks,
        opportunities=opps, recommendations=rank_recommendations(recs),
        scorecard=sc, executive_summary=ex)
