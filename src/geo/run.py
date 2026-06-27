"""Geographic Intelligence runner -> reports/geo_intelligence.md (+ .json, maps).

Assembles route geocoding, territory performance, geographic concentration,
distance-band coverage, delivery-day productivity, and white-space into a
geo-intelligence report with maps.

Run:  python -m src.geo.run
"""
from __future__ import annotations

import datetime as dt
import json

from src.geo import concentration as conc
from src.geo import maps as geo_maps
from src.geo import territory as terr
from src.utils import PROJECT_ROOT

REPORT_MD = PROJECT_ROOT / "reports" / "geo_intelligence.md"
REPORT_JSON = PROJECT_ROOT / "reports" / "geo_intelligence.json"


def _r(x):
    return f"₹{x:,.0f}"


def generate() -> dict:
    t = terr.analyze()
    c = conc.analyze()
    charts = geo_maps.render(t, c)

    L = ["# Geographic Intelligence & Territory Analytics", ""]
    L.append(f"> {('Sukhakarta Distributors')} · route-based pharmaceutical distribution "
             f"from Shirur (Pune district). Generated {dt.date.today():%Y-%m-%d}, FY {t.fy}.")
    L.append("")
    if t.data_note:
        L.append(f"> ⚠️ Data note: {t.data_note}")
        L.append("")

    # 1. Footprint
    L.append("## 1. Distribution footprint")
    L.append("")
    L.append(f"- {len(t.routes)} delivery routes · {t.matched_pct:.0f}% geocoded to towns "
             f"· total route sales {_r(t.total_sales)}.")
    L.append(f"- Geographic concentration (HHI): **{c.hhi:.0f}** — {c.hhi_label}. "
             f"Top-5 routes = {c.top5_share_pct:.1f}% of sales.")
    L.append(f"- **{c.local_share_pct:.1f}%** of revenue within 30 km of base; "
             f"**{c.outstation_share_pct:.1f}%** outstation (>80 km).")
    L.append("")
    if charts:
        L.append(f"![Route bubble map](../outputs/charts/geo_bubble_map.png)")
        L.append("")

    # 2. Top routes
    L.append("## 2. Top routes (current FY)")
    L.append("")
    L.append("| Route | Town | Day | Dist (km) | Customers | Drops/cust | Avg bill | Sales | YoY |")
    L.append("|---|---|---|--:|--:|--:|--:|--:|--:|")
    for _, r in t.routes.head(12).iterrows():
        L.append(f"| {r['area_name']} | {r['display_name'] or '—'} | "
                 f"{r['delivery_day'] or '—'} | "
                 f"{r['distance_km'] if r['distance_km'] is not None else '—'} | "
                 f"{int(r['num_customers'])} | {r['bills_per_customer']} | "
                 f"{_r(r['avg_bill_value'])} | {_r(r['sale_amount'])} | "
                 f"{('%+.1f%%' % r['yoy_pct']) if r['yoy_pct'] is not None else '—'} |")
    L.append("")

    # 3. By district
    L.append("## 3. By district")
    L.append("")
    L.append("| District | Routes | Customers | Bills | Sales | Share |")
    L.append("|---|--:|--:|--:|--:|--:|")
    for _, r in t.by_district.iterrows():
        L.append(f"| {r['district']} | {int(r['routes'])} | {int(r['customers'])} | "
                 f"{int(r['bills'])} | {_r(r['sales'])} | {r['share_pct']:.1f}% |")
    L.append("")

    # 4. Distance bands
    L.append("## 4. Sales by distance from base")
    L.append("")
    L.append("| Distance band | Routes | Customers | Sales | Share |")
    L.append("|---|--:|--:|--:|--:|")
    for _, r in c.distance_bands.iterrows():
        L.append(f"| {r['distance_band']} | {int(r['routes'])} | {int(r['customers'])} | "
                 f"{_r(r['sales'])} | {r['share_pct']:.1f}% |")
    L.append("")
    if charts:
        L.append("![Distance bands](../outputs/charts/geo_distance_bands.png)")
        L.append("")

    # 5. Delivery-day productivity
    L.append("## 5. Delivery-day productivity (route schedule)")
    L.append("")
    L.append("| Day | Routes | Customers | Bills | Sales | Avg bill |")
    L.append("|---|--:|--:|--:|--:|--:|")
    for _, r in t.by_day.sort_values("sales", ascending=False).iterrows():
        L.append(f"| {r['delivery_day']} | {int(r['routes'])} | {int(r['customers'])} | "
                 f"{int(r['bills'])} | {_r(r['sales'])} | {_r(r['avg_bill'])} |")
    L.append("")
    if charts:
        L.append("![Delivery day](../outputs/charts/geo_delivery_day.png)")
        L.append("")

    # 6. Insights & white-space
    L.append("## 6. Geographic insights & opportunities")
    L.append("")
    for ins in c.insights:
        L.append(f"- {ins}")
    L.append("")
    if c.white_space:
        L.append("**Coverage white-space — routes with low drop-frequency (re-engage / "
                 "add visits):**")
        L.append("")
        L.append("| Town | Customers | Drops/customer | Sales |")
        L.append("|---|--:|--:|--:|")
        for w in c.white_space:
            L.append(f"| {w['display_name']} | {int(w['num_customers'])} | "
                     f"{w['bills_per_customer']} | {_r(w['sale_amount'])} |")
        L.append("")
    L.append("> **So what:** the business is a dense local network (62% of sales within "
             "30 km) anchored on Shirur, with the Wednesday Ranjangaon belt as the single "
             "biggest delivery cluster. Growth levers are (a) lifting drop-frequency in "
             "under-served towns and (b) deepening the high-growth outer routes "
             "(Shrigonda, Parner) without over-extending the route network.")
    L.append("")
    L.append("---")
    L.append("*Coordinates are from a curated geocoding reference "
             "(`data/reference/geo_reference.csv`) for the firm's towns; refine with a "
             "formal geocoding pass for street-level precision.*")

    # Power BI map feed: geocoded route table (town names public; aggregate ₹ only)
    geo_cols = ["area_name", "display_name", "delivery_day", "district", "lat", "lon",
                "distance_km", "distance_band", "num_customers", "num_bills",
                "bills_per_customer", "avg_bill_value", "sale_amount", "yoy_pct"]
    route_geo = t.routes[[c for c in geo_cols if c in t.routes.columns]]
    for mode in ("internal", "shareable"):
        d = PROJECT_ROOT / "data" / "warehouse" / "exports" / mode
        d.mkdir(parents=True, exist_ok=True)
        route_geo.to_csv(d / "dim_route_geo.csv", index=False, encoding="utf-8")

    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    REPORT_MD.write_text("\n".join(L), encoding="utf-8")
    REPORT_JSON.write_text(json.dumps({
        "generated": str(dt.date.today()), "fy": t.fy,
        "hhi": c.hhi, "top5_share_pct": c.top5_share_pct,
        "local_share_pct": c.local_share_pct, "outstation_share_pct": c.outstation_share_pct,
        "by_district": t.by_district.to_dict("records"),
        "by_day": t.by_day.to_dict("records"),
        "distance_bands": c.distance_bands.astype({"distance_band": str}).to_dict("records"),
        "white_space": c.white_space,
    }, indent=2, default=str), encoding="utf-8")
    return {"md": str(REPORT_MD), "json": str(REPORT_JSON), "charts": charts,
            "hhi": c.hhi, "local_share_pct": c.local_share_pct}


def main():
    out = generate()
    print("Geo intelligence:", out["md"])
    print(f"HHI {out['hhi']:.0f} · {out['local_share_pct']:.0f}% local · "
          f"{len(out['charts'])} maps")


if __name__ == "__main__":
    main()
