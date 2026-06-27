"""Profitability ranking — customers, products, suppliers, territories.

Ranks each entity by absolute profit/value and by margin, surfacing the top and
bottom performers. Where the data has no cost side (purchases), ranks by spend.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.di import warehouse_api as W


@dataclass
class Ranking:
    entity: str
    metric: str
    top: pd.DataFrame
    bottom: pd.DataFrame
    note: str = ""


def customers(fy: str | None = None, n: int = 10) -> Ranking:
    fy = fy or W.CURRENT_FY
    df = W.sales_by_customer(fy).copy()
    df["margin_pct"] = (df["profit"] / df["revenue"] * 100).round(2)
    df = df[["customer_code", "revenue", "profit", "margin_pct"]]
    top = df.sort_values("profit", ascending=False).head(n)
    bottom = df[df["revenue"] > 0].sort_values("profit").head(n)
    return Ranking("customers", "profit", top, bottom)


def products(fy: str | None = None, n: int = 10) -> Ranking:
    fy = fy or W.CURRENT_FY
    pp = W.product_profit(fy).copy()
    pp["margin_pct"] = (pp["profit"] / pp["billed"] * 100).round(2)
    pp = pp.merge(W.product_perf(fy)[["product_key", "product_code"]],
                  on="product_key", how="left")
    pp = pp[["product_code", "billed", "profit", "margin_pct"]]
    top = pp.sort_values("profit", ascending=False).head(n)
    # bottom: high-revenue but low/negative margin (the problem children)
    bottom = pp[pp["billed"] > pp["billed"].quantile(0.75)].sort_values("margin_pct").head(n)
    return Ranking("products", "profit", top, bottom,
                   note="Bottom = high-revenue products with the weakest margins.")


def suppliers(fy: str | None = None, n: int = 10) -> Ranking:
    fy = fy or W.CURRENT_FY
    df = W.purchases_by_supplier(fy)[["supplier_code", "spend", "bills"]]
    top = df.sort_values("spend", ascending=False).head(n)
    return Ranking("suppliers", "spend", top, df.tail(0),
                   note="No cost-of-purchase margin available; ranked by spend.")


def territories(fy: str | None = None, n: int = 10) -> Ranking:
    fy = fy or W.CURRENT_FY
    df = W.territory_sales(fy)
    if df.empty:
        return Ranking("territories", "revenue", df, df, note="No territory data.")
    df = df.groupby("area_name", as_index=False)["revenue"].sum()
    top = df.sort_values("revenue", ascending=False).head(n)
    bottom = df[df["revenue"] > 0].sort_values("revenue").head(n)
    return Ranking("territories", "revenue", top, bottom)
