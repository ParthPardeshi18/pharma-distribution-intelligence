"""ABC / Pareto classification for customers, products, and suppliers.

A = the vital few driving the top ~80% of value, B = next ~15%, C = final ~5%.
Returns counts, value share, and the Pareto ratio (e.g. "20% of customers = 80%
of revenue").
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.di import warehouse_api as W


@dataclass
class ABCResult:
    entity: str
    classes: pd.DataFrame      # class, n, value, pct_of_entities, pct_of_value
    pareto_ratio: str          # "Top 18% of customers = 80% of revenue"
    total_value: float
    n: int


def classify(values: pd.Series, labels=("A", "B", "C"),
             cuts=(0.80, 0.95)) -> pd.Series:
    s = values.sort_values(ascending=False)
    cum = s.cumsum() / s.sum()
    cls = pd.Series(labels[2], index=s.index)
    cls[cum <= cuts[1]] = labels[1]
    cls[cum <= cuts[0]] = labels[0]
    return cls


def analyze(entity: str, df: pd.DataFrame, value_col: str) -> ABCResult:
    d = df[df[value_col] > 0].copy()
    d["class"] = classify(d[value_col])
    total = float(d[value_col].sum())
    g = d.groupby("class")[value_col].agg(["count", "sum"]).reindex(["A", "B", "C"]).fillna(0)
    g["pct_of_entities"] = (g["count"] / len(d) * 100).round(1)
    g["pct_of_value"] = (g["sum"] / total * 100).round(1)
    g = g.reset_index().rename(columns={"count": "n", "sum": "value"})
    # Pareto ratio: % of entities making the top 80% of value
    a = g[g["class"] == "A"].iloc[0]
    pareto = f"Top {a['pct_of_entities']:.0f}% of {entity} drive {a['pct_of_value']:.0f}% of value"
    return ABCResult(entity=entity, classes=g, pareto_ratio=pareto,
                     total_value=total, n=len(d))


def customers(fy: str | None = None) -> ABCResult:
    fy = fy or W.CURRENT_FY
    df = W.sales_by_customer(fy)
    return analyze("customers", df, "revenue")


def products(fy: str | None = None) -> ABCResult:
    fy = fy or W.CURRENT_FY
    df = W.product_perf(fy)
    return analyze("products", df, "revenue")


def suppliers(fy: str | None = None) -> ABCResult:
    fy = fy or W.CURRENT_FY
    df = W.purchases_by_supplier(fy)
    return analyze("suppliers", df, "spend")
