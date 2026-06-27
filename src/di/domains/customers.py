"""Customers domain — concentration, retention, growth, churn signals."""
from __future__ import annotations

from src.di import warehouse_api as W
from src.di.base import DomainReport, ExecutiveSummary, Insight
from src.di.churn import analyze_churn
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

    # ---- recency + frequency churn (route-based repeat retailers) ----
    ch = analyze_churn()
    retention = ch.retention_pct

    metrics = [
        make_metric("active_customers", active, active_p),
        make_metric("top10_customer_share_pct", top10, top10_p),
        make_metric("customer_retention_pct", retention),
    ]
    insights = insight_engine(metrics)
    insights.append(Insight(
        f"Of {ch.established:,} established repeat customers, {ch.active:,} are active, "
        f"{ch.at_risk:,} at-risk and {ch.churned:,} churned (silent beyond "
        f"{ch.config['frequency_multiple']:.0f}× their normal ordering gap, as of "
        f"{ch.config['reference']}).",
        severity="warning" if ch.churn_pct and ch.churn_pct > 25 else "info",
        evidence={"established": ch.established, "churn_pct": ch.churn_pct}))

    # ---- growth analysis ----
    merged = c.merge(cp[["customer_key", "revenue"]], on="customer_key",
                     how="left", suffixes=("", "_prior")).fillna({"revenue_prior": 0})
    merged["growth"] = merged["revenue"] - merged["revenue_prior"]
    growers = merged.sort_values("growth", ascending=False).head(5)

    # win-back value = prior-year revenue of churned established customers
    churned_keys = set(ch.customers.loc[ch.customers.status == "churned", "customer_key"])
    winback_val = float(cp.loc[cp["customer_key"].isin(churned_keys), "revenue"].sum())

    root = []
    if top10 > top10_p + 1:
        root.append(f"Customer concentration rose ({top10_p:.1f}%→{top10:.1f}% top-10 "
                    "share) — revenue is leaning on fewer accounts.")
    root.append(f"{ch.churned:,} of {ch.established:,} established retailers have gone "
                f"silent beyond their usual ordering cadence — a route-coverage / "
                f"service signal, not one-off walk-ins.")

    # ---- risks ----
    risks = []
    conc_score = max(0, min(100, (top10 - 20) / (45 - 20) * 100))
    if conc_score > 30:
        risks.append(risk("Customer concentration",
                          f"Top-10 customers account for {top10:.1f}% of revenue.",
                          conc_score, {"top10_share_pct": top10}))
    if ch.churn_pct and ch.churn_pct > 15:
        risks.append(risk("Customer churn",
                          f"{ch.churn_pct:.0f}% of established retailers have stopped "
                          "ordering relative to their own cadence.",
                          min(100, ch.churn_pct * 1.6),
                          {"churn_pct": ch.churn_pct, "churned": ch.churned}))

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
    if ch.churned:
        opps.append(opportunity(
            "Win back churned retailers",
            f"{ch.churned:,} established retailers lapsed; they billed ₹{winback_val:,.0f} "
            f"in {pri}. Route-level win-back could recover a large share.",
            impact_inr=winback_val, confidence=0.5,
            evidence={"churned_customers": ch.churned}))

    # ---- recommendations ----
    recs = [recommend(
        "Hand route salesmen a weekly churn/at-risk call list to re-engage silent retailers.",
        rationale=f"{ch.churned:,} established retailers have gone silent beyond their cadence.",
        impact="high", effort="low", confidence=0.6)]
    if ch.at_risk:
        recs.append(recommend(
            "Trigger proactive outreach when a retailer crosses its at-risk gap threshold.",
            rationale=f"{ch.at_risk:,} customers are approaching churn and are cheaper to retain.",
            impact="medium", effort="medium", confidence=0.55))
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
        what_happened=f"{active:,} customers billed this year; of {ch.established:,} "
                      f"established retailers, retention is {retention}% "
                      f"({ch.churned:,} churned, {ch.at_risk:,} at-risk).",
        why="Churn here is repeat retailers going silent vs their own ordering cadence "
            "— a route-coverage/service issue, not walk-in attrition.",
        business_impact=f"₹{winback_val:,.0f} of prior-year billings sit with churned "
                        "retailers who could be won back.",
        recommended_actions=[r.text for r in rank_recommendations(recs)[:2]],
        priority="high" if (ch.churn_pct or 0) > 25 or conc_score > 50 else "medium",
        confidence=0.65)

    return DomainReport(
        domain=DOMAIN,
        summary={"active_customers": active, "top10_share_pct": top10,
                 "retention_pct": retention, "established": ch.established,
                 "churned": ch.churned, "at_risk": ch.at_risk},
        metrics=metrics, insights=insights, root_causes=root, risks=risks,
        opportunities=opps, recommendations=rank_recommendations(recs),
        scorecard=sc, executive_summary=ex)
