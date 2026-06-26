"""Working capital domain — debtor/creditor/inventory days and the cash cycle."""
from __future__ import annotations

from src.di import warehouse_api as W
from src.di.base import DomainReport, ExecutiveSummary
from src.di.engines import (
    insight_engine, make_metric, rank_recommendations, recommend, risk, scorecard_from_metrics,
)

DOMAIN = "working_capital"


def _days(numerator, denominator):
    return round(365 * numerator / denominator, 0) if denominator else None


def analyze() -> DomainReport:
    cur, pri = W.CURRENT_FY, W.PRIOR_FY
    s = W.sales_by_fy().set_index("fy")
    p = W.purchases_by_fy().set_index("fy")
    rev = float(s.loc[cur, "revenue"]); cogs = float(s.loc[cur, "cost"])
    purch = float(p.loc[cur, "purchases"])
    ar = W.ar_balance(cur); ap = W.ap_balance(cur); inv = W.inventory_value(cur)

    debtor_days = _days(ar, rev)
    creditor_days = _days(ap, purch)
    inv_days = _days(inv, cogs)
    ccc = (debtor_days or 0) + (inv_days or 0) - (creditor_days or 0)

    # prior CCC
    rev_p = float(s.loc[pri, "revenue"]); cogs_p = float(s.loc[pri, "cost"])
    purch_p = float(p.loc[pri, "purchases"])
    ccc_p = ((_days(W.ar_balance(pri), rev_p) or 0)
             + (_days(W.inventory_value(pri), cogs_p) or 0)
             - (_days(W.ap_balance(pri), purch_p) or 0))

    metrics = [
        make_metric("debtor_days", debtor_days),
        make_metric("creditor_days", creditor_days),
        make_metric("inventory_days", inv_days),
        make_metric("ccc_days", round(ccc), round(ccc_p)),
    ]
    insights = insight_engine(metrics)

    root = [f"Cash conversion cycle ≈ {ccc:.0f} days "
            f"(debtor {debtor_days:.0f} + inventory {inv_days:.0f} − creditor "
            f"{creditor_days:.0f})."]
    if debtor_days is not None and debtor_days < 15:
        root.append(f"Very low debtor days ({debtor_days:.0f}) confirm a largely "
                    "cash/counter sales model — collections are not a constraint.")

    # ---- risks ----
    risks = []
    if debtor_days and debtor_days > 45:
        risks.append(risk("Collection delays",
                          f"Debtor days at {debtor_days:.0f} tie up receivables.",
                          min(100, (debtor_days - 30) * 2), {"debtor_days": debtor_days}))
    if ccc > ccc_p + 5:
        risks.append(risk("Working capital pressure",
                          f"Cash cycle lengthened {ccc_p:.0f}→{ccc:.0f} days YoY.",
                          min(100, 30 + (ccc - ccc_p) * 2), {"ccc": ccc}))

    recs = []
    if inv_days and inv_days > (debtor_days or 0) + (creditor_days or 0):
        recs.append(recommend(
            "Focus cash-cycle improvement on inventory, the dominant component.",
            rationale="Inventory days dominate the cash conversion cycle here.",
            impact="high", effort="medium", confidence=0.6))
    recs.append(recommend(
        "Negotiate longer supplier credit to extend creditor days where relationships allow.",
        rationale="Extending payables funds the cycle at no cost.",
        impact="medium", effort="low", confidence=0.55))

    sc = scorecard_from_metrics("Working capital", metrics,
                                weights={"ccc_days": 2.0, "debtor_days": 1.5,
                                         "inventory_days": 1.5})
    ex = ExecutiveSummary(
        what_happened=f"Cash conversion cycle ≈{ccc:.0f} days "
                      f"({'up' if ccc>ccc_p else 'down'} from {ccc_p:.0f}).",
        why="Inventory days dominate; receivables are minimal (cash-heavy model).",
        business_impact="The cash cycle sets how much working capital the business ties up.",
        recommended_actions=[r.text for r in rank_recommendations(recs)[:2]],
        priority="high" if ccc > ccc_p + 5 else "medium", confidence=0.65)

    return DomainReport(
        domain=DOMAIN,
        summary={"debtor_days": debtor_days, "creditor_days": creditor_days,
                 "inventory_days": inv_days, "ccc_days": round(ccc)},
        metrics=metrics, insights=insights, root_causes=root, risks=risks,
        opportunities=[], recommendations=rank_recommendations(recs),
        scorecard=sc, executive_summary=ex)
