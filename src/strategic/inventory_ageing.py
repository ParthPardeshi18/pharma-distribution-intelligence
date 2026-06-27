"""Inventory turnover & ageing — including batch expiry (pharma-critical).

Turnover/days come from the warehouse (COGS / closing stock). Expiry ageing comes
from the ERP ClosingStock report (batch + ExpDt), which the warehouse snapshot
does not carry at batch grain — read via the adapter. Near-expiry and expired
stock is money at risk of write-off.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.adapters import get_adapter
from src.di import warehouse_api as W


@dataclass
class AgeingResult:
    turnover: float | None
    inventory_days: float | None
    expiry_buckets: pd.DataFrame      # bucket, batches, value
    at_risk_value: float              # expired + expiring < 90 days
    reference_date: pd.Timestamp
    note: str = ""


def analyze(fy: str | None = None) -> AgeingResult:
    fy = fy or W.CURRENT_FY
    s = W.sales_by_fy().set_index("fy")
    cogs = float(s.loc[fy, "cost"]) if fy in s.index else None
    inv = W.inventory_value(fy)
    turnover = round(cogs / inv, 1) if inv and cogs else None
    days = round(365 / turnover, 0) if turnover else None

    a = get_adapter()
    try:
        cs = a.load("Stock/ClosingStock", fy).data.copy()
    except Exception:
        return AgeingResult(turnover, days, pd.DataFrame(), 0.0,
                            pd.Timestamp.today(), "ClosingStock unavailable.")

    cs["expiry_date"] = pd.to_datetime(cs.get("expiry_date"), errors="coerce")
    cs["quantity"] = pd.to_numeric(cs.get("quantity"), errors="coerce").fillna(0)
    rate = pd.to_numeric(cs.get("sale_rate_2"), errors="coerce")
    if rate.isna().all():
        rate = pd.to_numeric(cs.get("mrp"), errors="coerce")
    cs["value"] = cs["quantity"] * rate.fillna(0)

    ref = cs["expiry_date"].dropna().min() if cs["expiry_date"].notna().any() else pd.Timestamp.today()
    # reference = end of the snapshot FY (Mar 31)
    yr = 2000 + int(fy.split("-")[1])
    ref = pd.Timestamp(year=yr, month=3, day=31)
    cs["days_to_expiry"] = (cs["expiry_date"] - ref).dt.days

    def bucket(d):
        if pd.isna(d):
            return "No expiry / unknown"
        if d < 0:
            return "Expired"
        if d <= 90:
            return "Expiring ≤90 days"
        if d <= 180:
            return "Expiring 91-180 days"
        if d <= 365:
            return "Expiring 181-365 days"
        return "Expiring >365 days"

    cs["bucket"] = cs["days_to_expiry"].map(bucket)
    order = ["Expired", "Expiring ≤90 days", "Expiring 91-180 days",
             "Expiring 181-365 days", "Expiring >365 days", "No expiry / unknown"]
    g = cs.groupby("bucket").agg(batches=("bucket", "size"),
                                 value=("value", "sum")).reindex(order).dropna(how="all").reset_index()
    g["value"] = g["value"].round(0)
    at_risk = float(cs.loc[cs["days_to_expiry"] <= 90, "value"].sum())
    return AgeingResult(turnover, days, g, at_risk, ref,
                        note=f"Expiry ageing as of {ref.date()} (FY {fy} close).")
