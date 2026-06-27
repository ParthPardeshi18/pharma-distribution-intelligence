"""Strategic analysis runner -> reports/strategic_analysis.md (+ .json).

Assembles multi-year trends, seasonality, ABC/Pareto, RFM segmentation, product
lifecycle, inventory turnover & ageing, profitability rankings, and forecasts.
Forecasts carry confidence intervals, assumptions, model-quality metrics, and a
plain business explanation.

Run:  python -m src.strategic.run
"""
from __future__ import annotations

import datetime as dt
import json

from src.strategic import (
    abc_pareto, forecasting, inventory_ageing, lifecycle, profitability_ranking as pr,
    rfm, seasonality, trends,
)
from src.utils import PROJECT_ROOT

REPORT_MD = PROJECT_ROOT / "reports" / "strategic_analysis.md"
REPORT_JSON = PROJECT_ROOT / "reports" / "strategic_analysis.json"


def _rupees(x):
    return f"₹{x:,.0f}"


def _forecast_section(fc) -> list:
    L = [f"### {fc.name.title()} — {fc.forecast['ds'].dt.strftime('%b %Y').iloc[0]} to "
         f"{fc.forecast['ds'].dt.strftime('%b %Y').iloc[-1]}", ""]
    L.append(f"**Plain English:** {fc.explanation}")
    L.append("")
    L.append("| Month | Forecast | 80% confidence interval |")
    L.append("|---|--:|--:|")
    for _, r in fc.forecast.iterrows():
        L.append(f"| {r['ds']:%b %Y} | {_rupees(r['yhat'])} | "
                 f"{_rupees(r['yhat_lower'])} – {_rupees(r['yhat_upper'])} |")
    L.append("")
    m = fc.metrics
    if m:
        L.append(f"**Model quality** (out-of-sample backtest, last {m.get('backtest_h')} months): "
                 f"accuracy ±{m.get('mape')}% (MAPE), RMSE {_rupees(m.get('rmse',0))}, "
                 f"interval coverage {m.get('coverage')}% — rating **{m.get('quality')}**. "
                 f"Model: {fc.model_used}.")
    else:
        L.append(f"**Model quality:** backtest not run (insufficient history). Model: {fc.model_used}.")
    L.append("")
    L.append("**Assumptions:**")
    for a in fc.assumptions:
        L.append(f"- {a}")
    L.append("")
    return L


def generate(forecast_periods: int = 6) -> dict:
    T = trends.analyze()
    S = seasonality.analyze()
    abc = {"customers": abc_pareto.customers(), "products": abc_pareto.products(),
           "suppliers": abc_pareto.suppliers()}
    R = rfm.analyze()
    LC = lifecycle.analyze()
    AG = inventory_ageing.analyze()
    fc_sales = forecasting.forecast_sales(forecast_periods)
    fc_purch = forecasting.forecast_purchases(forecast_periods)

    L = ["# Strategic Analysis", ""]
    L.append(f"> Sukhakarta Distributors · generated {dt.date.today():%Y-%m-%d}. "
             "Multi-year strategy, segmentation, lifecycle, ageing, and forecasts "
             "(with confidence intervals and model quality).")
    L.append("")

    # 1. Multi-year trends
    L.append("## 1. Multi-year trends")
    L.append("")
    L.append("| Measure | " + " | ".join(fy for fy, _ in T[0].series) + " | CAGR | Direction |")
    L.append("|---|" + "--:|" * len(T[0].series) + "--:|---|")
    for t in T:
        vals = " | ".join(f"{v:,.0f}" if t.unit != "%" else f"{v:.2f}%" for _, v in t.series)
        L.append(f"| {t.measure} ({t.unit}) | {vals} | "
                 f"{t.cagr_pct:+.1f}% | {t.direction} |" if t.cagr_pct is not None
                 else f"| {t.measure} | {vals} | — | {t.direction} |")
    L.append("")
    rev = next(t for t in T if t.measure == "Revenue")
    prof = next(t for t in T if t.measure == "Gross profit")
    L.append(f"> **So what:** revenue is {rev.note} (CAGR {rev.cagr_pct:+.1f}%) while gross "
             f"profit is {prof.note} (CAGR {prof.cagr_pct:+.1f}%) — the business is trading "
             "lower volume at better margins.")
    L.append("")

    # 2. Seasonality
    L.append("## 2. Seasonality")
    L.append("")
    L.append(f"Peak month **{S.peak_month}**, trough **{S.trough_month}**, peak-to-trough "
             f"swing **{S.swing_pct:.0f}%** (over {S.n_years} years).")
    L.append("")
    L.append("| " + " | ".join(S.monthly_index["month_name"]) + " |")
    L.append("|" + "---|" * 12)
    L.append("| " + " | ".join(f"{i:.2f}" for i in S.monthly_index["index"]) + " |")
    L.append("")
    L.append(f"> **So what:** plan inventory and cash for the {S.peak_month} peak; the "
             f"{S.trough_month} trough is the natural window to clear slow stock and run "
             "collections.")
    L.append("")

    # 3. ABC / Pareto
    L.append("## 3. ABC / Pareto concentration")
    L.append("")
    for ent, res in abc.items():
        L.append(f"**{ent.title()}** — {res.pareto_ratio}.")
        L.append("")
        L.append("| Class | Count | % of " + ent + " | % of value |")
        L.append("|---|--:|--:|--:|")
        for _, r in res.classes.iterrows():
            L.append(f"| {r['class']} | {int(r['n']):,} | {r['pct_of_entities']:.1f}% | "
                     f"{r['pct_of_value']:.1f}% |")
        L.append("")
    L.append("> **So what:** focus service and credit on Class-A accounts/SKUs; manage the "
             "long Class-C tail by exception.")
    L.append("")

    # 4. RFM
    L.append("## 4. Customer segmentation (RFM)")
    L.append("")
    L.append("| Segment | Customers | % customers | % of value | Action |")
    L.append("|---|--:|--:|--:|---|")
    actions = {"Champions": "reward, upsell, protect", "Loyal": "deepen share of wallet",
               "Can't Lose Them": "urgent win-back — high value, lapsing",
               "At Risk": "re-engage before they churn",
               "Needs Attention": "targeted offers", "Potential Loyalists": "onboard, build frequency",
               "Hibernating / Lost": "low-cost reactivation only"}
    for _, r in R.segments.iterrows():
        L.append(f"| {r['segment']} | {int(r['n']):,} | {r['pct_customers']:.1f}% | "
                 f"{r['pct_value']:.1f}% | {actions.get(r['segment'],'')} |")
    L.append("")

    # 5. Lifecycle
    L.append("## 5. Product lifecycle")
    L.append("")
    L.append("| Stage | Products | Current-year revenue share |")
    L.append("|---|--:|--:|")
    for _, r in LC.summary.iterrows():
        L.append(f"| {r['stage']} | {int(r['n']):,} | {r['revenue_share']:.1f}% |")
    L.append("")
    L.append(f"> **So what:** {_rupees(LC.decline_value)} of current revenue sits in "
             "declining products — review pricing, promotion, or replacement.")
    L.append("")

    # 6. Inventory turnover & ageing
    L.append("## 6. Inventory turnover & ageing")
    L.append("")
    L.append(f"Turnover **{AG.turnover}×** (~{AG.inventory_days:.0f} days). {AG.note}")
    L.append("")
    if not AG.expiry_buckets.empty:
        L.append("| Expiry bucket | Batches | Stock value |")
        L.append("|---|--:|--:|")
        for _, r in AG.expiry_buckets.iterrows():
            L.append(f"| {r['bucket']} | {int(r['batches']):,} | {_rupees(r['value'])} |")
        L.append("")
        L.append(f"> **So what:** {_rupees(AG.at_risk_value)} of stock expires within 90 days "
                 "— prioritise it for sell-through or return-to-supplier.")
    L.append("")

    # 7. Profitability ranking
    L.append("## 7. Profitability ranking")
    L.append("")
    pc = pr.customers(); pp = pr.products()
    L.append("**Top customers by profit**")
    L.append("")
    L.append("| Customer | Revenue | Profit | Margin |")
    L.append("|---|--:|--:|--:|")
    for _, r in pc.top.head(5).iterrows():
        L.append(f"| {r['customer_code']} | {_rupees(r['revenue'])} | {_rupees(r['profit'])} "
                 f"| {r['margin_pct']:.2f}% |")
    L.append("")
    L.append(f"**Margin-drag products** ({pp.note})")
    L.append("")
    L.append("| Product | Billed | Profit | Margin |")
    L.append("|---|--:|--:|--:|")
    for _, r in pp.bottom.head(5).iterrows():
        L.append(f"| {r['product_code']} | {_rupees(r['billed'])} | {_rupees(r['profit'])} "
                 f"| {r['margin_pct']:.2f}% |")
    L.append("")

    # 8. Forecasts
    L.append("## 8. Forecasts (with confidence intervals & model quality)")
    L.append("")
    L += _forecast_section(fc_sales)
    L += _forecast_section(fc_purch)

    L.append("---")
    L.append("*Forecasts are decision support, not certainty: plan against the confidence "
             "interval and revisit monthly as actuals arrive.*")

    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    REPORT_MD.write_text("\n".join(L), encoding="utf-8")
    REPORT_JSON.write_text(json.dumps({
        "generated": str(dt.date.today()),
        "trends": [t.__dict__ for t in T],
        "seasonality": {"peak": S.peak_month, "trough": S.trough_month,
                        "swing_pct": S.swing_pct},
        "abc": {k: v.classes.to_dict("records") for k, v in abc.items()},
        "rfm_segments": R.segments.to_dict("records"),
        "lifecycle": LC.summary.to_dict("records"),
        "forecasts": [fc_sales.to_dict(), fc_purch.to_dict()],
    }, indent=2, default=str), encoding="utf-8")
    return {"md": str(REPORT_MD), "json": str(REPORT_JSON),
            "sales_forecast_quality": fc_sales.metrics.get("quality"),
            "peak_month": S.peak_month}


def main():
    out = generate()
    print("Strategic analysis:", out["md"])
    print("Sales forecast quality:", out["sales_forecast_quality"],
          "| peak month:", out["peak_month"])


if __name__ == "__main__":
    main()
