"""Build the canonical GeoJSON layers (the spatial source of truth).

Layers written to data/geo/:
  warehouses.geojson  — Point (the Shirur base)
  customers.geojson   — Points at town level (customer density proxy)
  villages.geojson    — Polygons (Voronoi cells around towns) with metrics
  talukas.geojson     — Polygons (villages dissolved by taluka)
  districts.geojson   — Polygons (villages dissolved by district)
  territories.geojson — Polygons (villages dissolved by delivery-day territory)
  routes.geojson      — LineStrings (per delivery-day hub-and-spoke paths)

Boundary polygons are Voronoi tessellations of the town centroids clipped to the
core operating region — genuine, dissolvable polygons (NOT lat/lon points). They
are clearly synthetic approximations; real census/GADM boundaries can replace
them by dropping new GeoJSON into data/geo/ with the same schema. The lat/lon
reference (config/geo_reference.csv) is used ONLY as a geocoding cache to seed
the town centroids.
"""
from __future__ import annotations

import json

import pandas as pd
import yaml
from shapely.geometry import MultiPoint, Point, box, mapping
from shapely.ops import unary_union, voronoi_diagram

from src.geo.gis.geojson import (
    Feature, FeatureCollection, geom_from_shapely, linestring, point,
)
from src.geo.geocode import Geocoder
from src.geo import territory as terr
from src.utils import CONFIG_DIR, PROJECT_ROOT

GEO_DIR = PROJECT_ROOT / "data" / "geo"
CORE_RADIUS_KM = 120     # boundary tessellation covers the operating heartland


def _base() -> dict:
    return yaml.safe_load((CONFIG_DIR / "geo.yaml").read_text(encoding="utf-8"))["base"]


def _town_table() -> pd.DataFrame:
    """Town-level metrics (sales/customers/bills) joined to the geocode cache
    (taluka/district/coords)."""
    t = terr.analyze()
    r = t.routes[t.routes["matched"]].copy()
    towns = r.groupby("town", as_index=False).agg(
        display_name=("display_name", "first"), lat=("lat", "first"),
        lon=("lon", "first"), district=("district", "first"),
        distance_km=("distance_km", "first"),
        sales=("sale_amount", "sum"), customers=("num_customers", "sum"),
        bills=("num_bills", "sum"))
    # taluka + primary delivery day from the cache / routes
    ref = Geocoder().ref.set_index("place_key")
    towns["taluka"] = towns["town"].map(lambda k: ref.loc[k, "taluka"]
                                        if k in ref.index else None)
    day = (r[r["delivery_day"].notna()].groupby("town")["delivery_day"]
           .agg(lambda s: s.value_counts().idxmax()))
    towns["delivery_day"] = towns["town"].map(day).fillna("Local/Daily")
    towns["fy"] = t.fy
    return towns


# --------------------------- boundary tessellation ------------------------ #
def _voronoi_cells(core: pd.DataFrame) -> dict[str, object]:
    """town -> shapely polygon (Voronoi cell clipped to the core envelope)."""
    pts = [Point(row.lon, row.lat) for row in core.itertuples()]
    mp = MultiPoint(pts)
    margin = 0.15
    env = box(core.lon.min() - margin, core.lat.min() - margin,
              core.lon.max() + margin, core.lat.max() + margin)
    diagram = voronoi_diagram(mp, envelope=env)
    cells = [c.intersection(env) for c in diagram.geoms]
    out: dict[str, object] = {}
    for _, row in core.iterrows():
        p = Point(row.lon, row.lat)
        for cell in cells:
            if cell.covers(p):
                out[row.town] = cell
                break
    return out


def build_all() -> dict[str, FeatureCollection]:
    base = _base()
    towns = _town_table()
    core = towns[towns["distance_km"] <= CORE_RADIUS_KM].reset_index(drop=True)
    cells = _voronoi_cells(core)

    collections: dict[str, FeatureCollection] = {}

    # --- warehouses ---
    wh = FeatureCollection(name="warehouses")
    wh.add(Feature(point(base["lon"], base["lat"]),
                   {"name": base["name"], "type": "distribution_warehouse",
                    "district": base["district"]}, id="warehouse:base"))
    collections["warehouses"] = wh

    # --- customers (town-level density points) ---
    cust = FeatureCollection(name="customers")
    for _, r in towns.iterrows():
        cust.add(Feature(point(r["lon"], r["lat"]), {
            "town": r["display_name"], "taluka": r["taluka"], "district": r["district"],
            "customers": int(r["customers"]), "sales_inr": float(r["sales"]),
            "bills": int(r["bills"]), "distance_km": r["distance_km"]},
            id=f"customer_area:{r['town']}"))
    collections["customers"] = cust

    # --- villages (Voronoi polygons) ---
    vil = FeatureCollection(name="villages")
    for _, r in core.iterrows():
        cell = cells.get(r["town"])
        if cell is None or cell.is_empty:
            continue
        vil.add(Feature(geom_from_shapely(cell), {
            "name": r["display_name"], "taluka": r["taluka"], "district": r["district"],
            "delivery_day": r["delivery_day"], "sales_inr": float(r["sales"]),
            "customers": int(r["customers"]), "bills": int(r["bills"]),
            "distance_km": r["distance_km"]}, id=f"village:{r['town']}"))
    collections["villages"] = vil

    # --- dissolve helper ---
    def dissolve(group_col: str, layer: str, id_prefix: str) -> FeatureCollection:
        fc = FeatureCollection(name=layer)
        merged = core.copy()
        merged["__cell"] = merged["town"].map(cells)
        for key, grp in merged.dropna(subset=["__cell"]).groupby(group_col):
            poly = unary_union(list(grp["__cell"]))
            fc.add(Feature(geom_from_shapely(poly), {
                "name": key, "sales_inr": float(grp["sales"].sum()),
                "customers": int(grp["customers"].sum()),
                "bills": int(grp["bills"].sum()),
                "towns": int(len(grp))}, id=f"{id_prefix}:{key}"))
        return fc

    collections["talukas"] = dissolve("taluka", "talukas", "taluka")
    collections["districts"] = dissolve("district", "districts", "district")
    collections["territories"] = dissolve("delivery_day", "territories", "territory")

    # --- routes (per delivery-day hub-and-spoke path) ---
    routes = FeatureCollection(name="routes")
    for day, grp in towns[towns["delivery_day"] != "Local/Daily"].groupby("delivery_day"):
        stops = grp.sort_values("distance_km")
        coords = [(base["lon"], base["lat"])] + \
                 [(r.lon, r.lat) for r in stops.itertuples()]
        routes.add(Feature(linestring(coords), {
            "delivery_day": day, "stops": int(len(stops)),
            "sales_inr": float(stops["sales"].sum()),
            "towns": ", ".join(stops["display_name"].astype(str))},
            id=f"route:{day}"))
    collections["routes"] = routes

    # write all
    GEO_DIR.mkdir(parents=True, exist_ok=True)
    for name, fc in collections.items():
        fc.write(GEO_DIR / f"{name}.geojson")
    return collections
