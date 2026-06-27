"""Product lifecycle analysis — classify products by their multi-year volume path.

Stages (from quantity across financial years):
  New        — first sold only in the most recent year(s)
  Growth     — volume rising materially
  Mature     — volume broadly stable
  Decline    — volume falling materially
  Dormant    — no sales in the most recent year
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.di import warehouse_api as W
from src.warehouse.db import make_engine


@dataclass
class LifecycleResult:
    products: pd.DataFrame    # product_key, stages + qty by fy
    summary: pd.DataFrame     # stage, n, revenue_share
    decline_value: float      # current-year revenue tied up in declining products


def analyze(growth_threshold: float = 0.15) -> LifecycleResult:
    e = make_engine()
    df = pd.read_sql("SELECT product_key, financial_year, "
                     "SUM(quantity) qty, SUM(sale_amount_inr) revenue "
                     "FROM fact_sales_product GROUP BY product_key, financial_year", e)
    fys = W.FYS
    piv = df.pivot_table(index="product_key", columns="financial_year",
                         values="qty", fill_value=0)
    for fy in fys:
        if fy not in piv.columns:
            piv[fy] = 0
    piv = piv[fys]
    cur, pri = fys[-1], fys[-2]
    rev = df[df.financial_year == cur].set_index("product_key")["revenue"]

    def stage(row):
        c, p = row[cur], row[pri]
        active_hist = (row[fys[0]] > 0) or (row[fys[1]] > 0)
        if c == 0:
            return "Dormant"
        if not active_hist and (row[fys[2]] > 0 or row[fys[3]] > 0):
            return "New"
        if p == 0:
            return "New" if c > 0 else "Dormant"
        change = (c - p) / p
        if change >= growth_threshold:
            return "Growth"
        if change <= -growth_threshold:
            return "Decline"
        return "Mature"

    piv["stage"] = piv.apply(stage, axis=1)
    piv["cur_revenue"] = piv.index.map(rev).fillna(0)
    total_rev = piv["cur_revenue"].sum()
    summ = piv.groupby("stage").agg(n=("stage", "size"),
                                    revenue=("cur_revenue", "sum")).reset_index()
    summ["revenue_share"] = (summ["revenue"] / total_rev * 100).round(1) if total_rev else 0
    summ = summ.sort_values("revenue", ascending=False).reset_index(drop=True)
    decline_value = float(piv.loc[piv["stage"] == "Decline", "cur_revenue"].sum())
    return LifecycleResult(products=piv.reset_index(), summary=summ,
                           decline_value=decline_value)
