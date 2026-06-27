"""RFM customer segmentation (Recency, Frequency, Monetary).

Recency  = days since last order (frequency-aware churn context from src.di.churn)
Frequency= lifetime order count
Monetary = lifetime revenue

Each scored 1-5 by quintile, then mapped to actionable segments (Champions,
Loyal, Potential Loyalists, At Risk, Hibernating, Lost) tuned for a route-based
distributor.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.di import warehouse_api as W


@dataclass
class RFMResult:
    customers: pd.DataFrame    # customer_key, recency_days, frequency, monetary, R,F,M, segment
    segments: pd.DataFrame     # segment, n, monetary, pct_customers, pct_value
    reference_date: pd.Timestamp


def _quintile_score(s: pd.Series, reverse: bool = False) -> pd.Series:
    """1-5 score by quintile. reverse=True => lower value scores higher (recency)."""
    try:
        q = pd.qcut(s.rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
    except ValueError:
        q = pd.Series(3, index=s.index)
    q = q.astype(int)
    return 6 - q if reverse else q


def _segment(r: int, f: int, m: int) -> str:
    if r >= 4 and f >= 4:
        return "Champions"
    if r >= 3 and f >= 3:
        return "Loyal"
    if r >= 4 and f <= 2:
        return "Potential Loyalists"
    if r == 3:
        return "Needs Attention"
    if r == 2:
        return "At Risk"
    if r == 1 and m >= 4:
        return "Can't Lose Them"
    return "Hibernating / Lost"


def analyze() -> RFMResult:
    orders = W.customer_orders()
    ref = orders["order_date"].max()
    agg = orders.groupby("customer_key").agg(
        recency_days=("order_date", lambda s: (ref - s.max()).days),
        frequency=("order_date", "count"),
        monetary=("amount", "sum")).reset_index()
    agg = agg[agg["monetary"] > 0]

    agg["R"] = _quintile_score(agg["recency_days"], reverse=True)
    agg["F"] = _quintile_score(agg["frequency"])
    agg["M"] = _quintile_score(agg["monetary"])
    agg["segment"] = agg.apply(lambda x: _segment(x["R"], x["F"], x["M"]), axis=1)

    total_val = agg["monetary"].sum()
    seg = agg.groupby("segment").agg(n=("customer_key", "count"),
                                     monetary=("monetary", "sum")).reset_index()
    seg["pct_customers"] = (seg["n"] / len(agg) * 100).round(1)
    seg["pct_value"] = (seg["monetary"] / total_val * 100).round(1)
    seg = seg.sort_values("monetary", ascending=False).reset_index(drop=True)
    return RFMResult(customers=agg, segments=seg, reference_date=ref)
