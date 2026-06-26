"""Cash flow domain — inflow vs outflow trend and an operating-cash proxy.

True cash flow needs payment-level data the ERP does not export cleanly. We
approximate operating cash as gross profit minus the increase in working capital
(receivables + inventory − payables). Documented as an approximation.
"""
from __future__ import annotations

from src.di import warehouse_api as W
from src.di.base import DomainReport, ExecutiveSummary
from src.di.engines import (
    insight_engine, make_metric, rank_recommendations, recommend, risk,
    scorecard_from_metrics,
)

DOMAIN = "cash_flow"


def _wc(fy):
    return W.ar_balance(fy) + W.inventory_value(fy) - W.ap_balance(fy)


def analyze() -> DomainReport:
    cur, pri = W.CURRENT_FY, W.PRIOR_FY
    s = W.sales_by_fy().set_index("fy")
    p = W.purchases_by_fy().set_index("fy")
    profit = float(s.loc[cur, "profit"])
    wc_cur, wc_pri = _wc(cur), _wc(pri)
    d_wc = wc_cur - wc_pri
    op_cash = profit - d_wc   # proxy: profit less the cash absorbed by working capital

    inflow = [(fy, round(float(s.loc[fy, "revenue"]))) for fy in s.index]
    outflow = [(fy, round(float(p.loc[fy, "purchases"]))) for fy in p.index if fy in p.index]

    rev = float(s.loc[cur, "revenue"])
    cash_margin = round(100 * op_cash / rev, 2) if rev else None
    metrics = [make_metric("operating_cash_proxy_inr", round(op_cash)),
               make_metric("operating_cash_margin_pct", cash_margin)]
    insights = insight_engine(metrics)

    root = [f"Operating cash proxy ≈ ₹{op_cash:,.0f}: gross profit ₹{profit:,.0f} "
            f"{'less' if d_wc>=0 else 'plus'} ₹{abs(d_wc):,.0f} "
            f"{'absorbed by' if d_wc>=0 else 'released from'} working capital."]
    net_trend = float(s.loc[cur, 'revenue'] - p.loc[cur, 'purchases'])
    root.append(f"Sales (₹{s.loc[cur,'revenue']:,.0f}) vs purchases "
                f"(₹{p.loc[cur,'purchases']:,.0f}) gives a gross trading inflow of "
                f"₹{net_trend:,.0f} this year.")

    risks = []
    if d_wc > profit:
        risks.append(risk("Cash absorbed by working capital",
                          "Working-capital growth exceeded gross profit, pressuring cash.",
                          min(100, 40 + (d_wc - profit) / max(1, profit) * 30),
                          {"delta_wc": round(d_wc), "profit": round(profit)}))

    recs = [recommend(
        "Track the cash conversion cycle monthly to keep working capital from "
        "outrunning profit.", rationale="Operating cash hinges on the cash cycle.",
        impact="medium", effort="low", confidence=0.6)]

    ex = ExecutiveSummary(
        what_happened=f"Operating cash proxy ≈ ₹{op_cash:,.0f}.",
        why=f"Working capital {'absorbed' if d_wc>=0 else 'released'} "
            f"₹{abs(d_wc):,.0f} of the ₹{profit:,.0f} gross profit.",
        business_impact="Cash generation depends on holding the working-capital line.",
        recommended_actions=[r.text for r in rank_recommendations(recs)[:1]],
        priority="medium", confidence=0.5)

    return DomainReport(
        domain=DOMAIN,
        summary={"operating_cash_proxy": round(op_cash), "delta_working_capital": round(d_wc),
                 "inflow_trend": inflow, "outflow_trend": outflow},
        metrics=metrics, insights=insights, root_causes=root, risks=risks,
        opportunities=[], recommendations=rank_recommendations(recs),
        scorecard=scorecard_from_metrics("Cash flow", metrics),
        executive_summary=ex)
