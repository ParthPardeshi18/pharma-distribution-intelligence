"""Customers domain — concentration, retention, growth, churn signals."""
from __future__ import annotations

from src.di import warehouse_api as W
from src.di.base import DomainReport, ExecutiveSummary
from src.di.engines import (
    insight_engine, make_metric, opportunity, rank_recommendations, recommend,
    risk, scorecard_from_metrics,
)

DOMAIN = "customers"


def analyze() -> DomainReport:
    cur, pri = W.CURRENT_FY, W.PRIOR_FY
    c = W.sales_by_customer(cur)
    cp = W.sales_by_customer(pri)
    active = len(c); active_p = len(cp)
    top10 = W.concentration_share(c["revenue"], 10)
    top10_p = W.concentration_share(cp["revenue"], 10)

    prev_set = set(cp["customer_key"]); now_set = set(c["customer_key"])
    retained = len(prev_set & now_set)
    retention = round(100.0 * retained / len(prev_set), 1) if prev_set else None
    churned = len(prev_set - now_set)

    metrics = [
        make_metric("active_customers", active, active_p),
        make_metric("top10_customer_share_pct", top10, top10_p),
        make_metric("customer_retention_pct", retention),
    ]
    insights = insight_engine(metrics)

    # ---- root cause / growth analysis ----
    merged = c.merge(cp[["customer_key", "revenue"]], on="customer_key",
                     how="left", suffixes=("", "_prior")).fillna({"revenue_prior": 0})
    merged["growth"] = merged["revenue"] - merged["revenue_prior"]
    growers = merged.sort_values("growth", ascending=False).head(5)
    decliners = merged[merged["revenue_prior"] > 0].sort_values("growth").head(5)
    root = []
    if top10 > top10_p + 1:
        root.append(f"Customer concentration rose ({top10_p:.1f}%→{top10:.1f}% top-10 "
                    "share) — revenue is leaning on fewer accounts.")
    root.append(f"{churned:,} customers active in {pri} did not buy in {cur} "
                f"(retention {retention}%).")

    # ---- risks ----
    risks = []
    conc_score = max(0, min(100, (top10 - 20) / (45 - 20) * 100))
    if conc_score > 30:
        risks.append(risk("Customer concentration",
                          f"Top-10 customers account for {top10:.1f}% of revenue.",
                          conc_score, {"top10_share_pct": top10}))
    if retention is not None and retention < 75:
        risks.append(risk("Customer churn",
                          f"Only {retention:.0f}% of last year's customers returned.",
                          min(100, (75 - retention) * 2.5), {"retention_pct": retention}))

    # ---- opportunities ----
    opps = []
    if not growers.empty:
        top_grow_val = float(growers["growth"].head(3).sum())
        opps.append(opportunity(
            "Nurture high-growth customers",
            f"The 3 fastest-growing customers added ₹{top_grow_val:,.0f} this year; "
            "deepen share-of-wallet with them.",
            impact_inr=top_grow_val, confidence=0.6,
            evidence={"top_growers": growers["customer_code"].head(3).tolist()}))
    if churned:
        lost = float(decliners["revenue_prior"].sum())
        opps.append(opportunity(
            "Win back lapsed customers",
            f"{churned:,} customers lapsed; the top decliners alone represented "
            f"₹{lost:,.0f} last year.", impact_inr=lost, confidence=0.45))

    # ---- recommendations ----
    recs = [recommend(
        "Launch a structured win-back campaign for lapsed top customers.",
        rationale=f"{churned:,} customers churned YoY.",
        impact="high", effort="medium", confidence=0.55)]
    if conc_score > 30:
        recs.append(recommend(
            "Diversify the customer base to reduce reliance on the top-10 accounts.",
            rationale="Concentration risk is elevated.",
            impact="medium", effort="high", confidence=0.5))

    sc = scorecard_from_metrics("Customers", metrics,
                                weights={"top10_customer_share_pct": 1.5,
                                         "customer_retention_pct": 2.0,
                                         "active_customers": 1.0})
    ex = ExecutiveSummary(
        what_happened=f"{active:,} active customers; top-10 concentration {top10:.1f}%; "
                      f"retention {retention}%.",
        why=f"{churned:,} customers lapsed while the base "
            f"{'concentrated' if top10>top10_p else 'broadened'}.",
        business_impact="Revenue durability depends on retaining and diversifying accounts.",
        recommended_actions=[r.text for r in rank_recommendations(recs)[:2]],
        priority="high" if conc_score > 50 or (retention or 100) < 70 else "medium",
        confidence=0.65)

    return DomainReport(
        domain=DOMAIN,
        summary={"active_customers": active, "top10_share_pct": top10,
                 "retention_pct": retention, "churned": churned},
        metrics=metrics, insights=insights, root_causes=root, risks=risks,
        opportunities=opps, recommendations=rank_recommendations(recs),
        scorecard=sc, executive_summary=ex)
