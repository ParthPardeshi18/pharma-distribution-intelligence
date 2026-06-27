"""Seasonality analysis — monthly seasonal indices, peak/trough months.

Seasonal index for a month = average sales that calendar month ÷ overall monthly
average. Index > 1.0 means that month runs above trend. Computed across all
financial years so the pattern is stable, not a single-year artifact.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.warehouse.db import make_engine


@dataclass
class SeasonalityResult:
    monthly_index: pd.DataFrame   # month, month_name, avg_sales, index
    peak_month: str
    trough_month: str
    swing_pct: float              # peak-to-trough swing
    n_years: int


_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def analyze() -> SeasonalityResult:
    e = make_engine()
    df = pd.read_sql("SELECT date_key, net_amount_inr FROM fact_sales "
                     "WHERE date_key IS NOT NULL", e)
    df["date"] = pd.to_datetime(df["date_key"].astype(int).astype(str), format="%Y%m%d")
    monthly = df.set_index("date")["net_amount_inr"].resample("MS").sum()
    n_years = round(len(monthly) / 12, 1)

    by_month = monthly.groupby(monthly.index.month).mean()
    overall = monthly.mean()
    idx = (by_month / overall).round(3)
    tab = pd.DataFrame({"month": idx.index,
                        "month_name": [_MONTHS[m - 1] for m in idx.index],
                        "avg_sales": by_month.round(0).values,
                        "index": idx.values})
    peak = tab.loc[tab["index"].idxmax()]
    trough = tab.loc[tab["index"].idxmin()]
    swing = round((peak["index"] / trough["index"] - 1) * 100, 0)
    return SeasonalityResult(monthly_index=tab, peak_month=peak["month_name"],
                             trough_month=trough["month_name"], swing_pct=swing,
                             n_years=n_years)
