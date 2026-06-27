"""Geographic concentration, distance-band coverage, and penetration analytics."""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from src.geo.territory import TerritoryResult, analyze as territory_analyze


@dataclass
class GeoConcentration:
    hhi: float                       # 0-10000 (Herfindahl on route sales share)
    hhi_label: str
    top5_share_pct: float
    distance_bands: pd.DataFrame     # band, routes, customers, sales, share
    local_share_pct: float           # share within 30 km
    outstation_share_pct: float      # share beyond 80 km
    penetration: pd.DataFrame        # route, customers, sales_per_customer, bills_per_customer
    white_space: list = field(default_factory=list)   # under-served routes
    insights: list = field(default_factory=list)


def _hhi_label(hhi: float) -> str:
    if hhi < 1500:
        return "low (well diversified geographically)"
    if hhi < 2500:
        return "moderate"
    return "high (revenue geographically concentrated)"


def analyze(fy: str | None = None) -> GeoConcentration:
    t: TerritoryResult = territory_analyze(fy)
    df = t.routes
    total = t.total_sales

    shares = (df["sale_amount"] / total)
    hhi = round(float((shares ** 2).sum()) * 10000, 0)
    top5 = round(float(df["sale_amount"].head(5).sum()) / total * 100, 1)

    band_order = ["≤15 km (local)", "15-30 km", "30-50 km", "50-80 km",
                  "80-150 km", ">150 km (outstation)"]
    geo = df[df["matched"]]
    bands = geo.groupby("distance_band", as_index=False).agg(
        routes=("area_name", "count"), customers=("num_customers", "sum"),
        sales=("sale_amount", "sum"))
    bands["share_pct"] = (bands["sales"] / total * 100).round(1)
    bands["distance_band"] = pd.Categorical(bands["distance_band"], band_order, ordered=True)
    bands = bands.sort_values("distance_band")

    local = round(float(geo.loc[geo["distance_km"] <= 30, "sale_amount"].sum()) / total * 100, 1)
    outstation = round(float(geo.loc[geo["distance_km"] > 80, "sale_amount"].sum()) / total * 100, 1)

    pen = df[["area_name", "display_name", "num_customers", "sales_per_customer",
              "bills_per_customer", "sale_amount", "distance_km"]].copy()
    # white space: routes with few customers but real distance footprint, or low
    # drop frequency (bills per customer) relative to the median.
    med_freq = df["bills_per_customer"].median()
    ws = df[(df["matched"]) & (df["num_customers"] >= 5) &
            (df["bills_per_customer"] < 0.6 * med_freq)]
    white_space = ws.sort_values("sale_amount", ascending=False)[
        ["display_name", "num_customers", "bills_per_customer", "sale_amount"]
    ].head(8).to_dict("records")

    insights = [
        f"Geographic HHI is {hhi:.0f} — {_hhi_label(hhi)}.",
        f"The top-5 routes carry {top5:.1f}% of sales.",
        f"{local:.1f}% of revenue is within 30 km of the Shirur base; "
        f"{outstation:.1f}% is outstation (>80 km).",
    ]
    if not ws.empty:
        insights.append(f"{len(ws)} routes show low drop-frequency (<60% of the median "
                        "visits per customer) — coverage/service white-space.")

    return GeoConcentration(
        hhi=hhi, hhi_label=_hhi_label(hhi), top5_share_pct=top5,
        distance_bands=bands, local_share_pct=local, outstation_share_pct=outstation,
        penetration=pen, white_space=white_space, insights=insights)
