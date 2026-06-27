"""Territory / route performance — geocoded Area_Sales with productivity metrics."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.adapters import get_adapter
from src.di import warehouse_api as W
from src.geo.geocode import Geocoder


@dataclass
class TerritoryResult:
    routes: pd.DataFrame          # per route, current FY + geocoding + productivity + YoY
    by_district: pd.DataFrame
    by_day: pd.DataFrame          # delivery-day productivity
    fy: str
    comparison_fy: str | None
    total_sales: float
    matched_pct: float
    data_note: str = ""


def _area_sales(fy: str) -> pd.DataFrame:
    d = get_adapter().load("Sales/Area_Sales", fy).data.copy()
    for c in ("num_customers", "num_bills", "sale_amount"):
        d[c] = pd.to_numeric(d.get(c), errors="coerce").fillna(0)
    return d.groupby("area_name", as_index=False)[
        ["num_customers", "num_bills", "sale_amount"]].sum()


def analyze(fy: str | None = None) -> TerritoryResult:
    fy = fy or W.CURRENT_FY
    cur = _area_sales(fy)
    cur_total = float(cur["sale_amount"].sum())
    # Pick the most recent EARLIER FY whose total actually differs — the ERP's
    # Area_Sales export repeats identical figures for some years (a known anomaly),
    # so a naive prior-year YoY would read as 0%.
    idx = W.FYS.index(fy)
    prior = None
    data_note = ""
    for f in reversed(W.FYS[:idx]):
        if abs(float(_area_sales(f)["sale_amount"].sum()) - cur_total) > 1:
            prior = f
            break
    if idx > 0 and prior != W.FYS[idx - 1]:
        data_note = (f"ERP Area_Sales for {fy} and {W.FYS[idx-1]} are identical in the "
                     f"export (verify with the ERP); YoY is computed against {prior}.") \
            if prior else (f"ERP Area_Sales is identical across available years; "
                           "route YoY unavailable.")
    g = Geocoder()
    geo = g.geocode_frame(cur["area_name"].tolist())
    df = cur.merge(geo, on="area_name", how="left")

    # productivity metrics
    df["avg_bill_value"] = (df["sale_amount"] / df["num_bills"]).round(0)
    df["bills_per_customer"] = (df["num_bills"] / df["num_customers"]).round(1)  # visit/drop freq
    df["sales_per_customer"] = (df["sale_amount"] / df["num_customers"]).round(0)
    df["revenue_per_km"] = df.apply(
        lambda r: round(r["sale_amount"] / r["distance_km"], 0)
        if r["distance_km"] and r["distance_km"] > 0 else None, axis=1)

    # YoY growth per route (vs the chosen comparison FY)
    if prior:
        pr = _area_sales(prior)[["area_name", "sale_amount"]].rename(
            columns={"sale_amount": "sale_prior"})
        df = df.merge(pr, on="area_name", how="left")
        df["yoy_pct"] = df.apply(
            lambda r: round((r["sale_amount"] / r["sale_prior"] - 1) * 100, 1)
            if r.get("sale_prior") else None, axis=1)
    else:
        df["sale_prior"] = None
        df["yoy_pct"] = None

    total = float(df["sale_amount"].sum())
    df["share_pct"] = (df["sale_amount"] / total * 100).round(1)
    matched_pct = round(100 * df.loc[df["is_geographic"], "matched"].mean(), 0) \
        if df["is_geographic"].any() else 0

    geo_df = df[df["matched"]]
    by_district = geo_df.groupby("district", as_index=False).agg(
        routes=("area_name", "count"), customers=("num_customers", "sum"),
        bills=("num_bills", "sum"), sales=("sale_amount", "sum")).sort_values(
        "sales", ascending=False)
    by_district["share_pct"] = (by_district["sales"] / by_district["sales"].sum() * 100).round(1)

    by_day = df[df["delivery_day"].notna()].groupby("delivery_day", as_index=False).agg(
        routes=("area_name", "count"), customers=("num_customers", "sum"),
        bills=("num_bills", "sum"), sales=("sale_amount", "sum"))
    by_day["avg_bill"] = (by_day["sales"] / by_day["bills"]).round(0)

    return TerritoryResult(routes=df.sort_values("sale_amount", ascending=False),
                           by_district=by_district, by_day=by_day, fy=fy,
                           comparison_fy=prior, total_sales=total,
                           matched_pct=matched_pct, data_note=data_note)
