"""GIS orchestrator: build canonical GeoJSON, load the warehouse spatial layer,
export GeoJSON for BI/web consumers, and render the interactive map.

Run:  python -m src.geo.gis.run
"""
from __future__ import annotations

import datetime as dt
import json
import shutil

import pandas as pd
from shapely.geometry import shape

from src.geo.gis import layers as gis_layers
from src.geo.gis import maps_web
from src.utils import PROJECT_ROOT
from src.warehouse.db import make_engine

GEO_DIR = PROJECT_ROOT / "data" / "geo"
BASE = {"lat": 18.8268, "lon": 74.3733}


def _haversine(lat, lon):
    import math
    if lat is None or lon is None:
        return None
    r = 6371.0
    p1, p2 = math.radians(BASE["lat"]), math.radians(lat)
    dp, dl = math.radians(lat - BASE["lat"]), math.radians(lon - BASE["lon"])
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return round(r * 2 * math.asin(math.sqrt(a)), 1)


def load_to_warehouse(collections) -> int:
    """Materialise every GeoJSON feature into dim_geo_feature (geometry as the
    canonical GeoJSON text). Facts join by name/area; geometry is source of truth."""
    rows = []
    for layer, fc in collections.items():
        for f in fc.features:
            geom = f.geometry
            props = f.properties or {}
            try:
                c = shape(geom).centroid if geom else None
                clat, clon = (round(c.y, 6), round(c.x, 6)) if c else (None, None)
            except Exception:
                clat = clon = None
            rows.append({
                "geo_feature_id": f.id or f"{layer}:{props.get('name','')}",
                "layer": layer, "feature_type": geom["type"] if geom else None,
                "name": props.get("name") or props.get("town") or props.get("delivery_day"),
                "parent_taluka": props.get("taluka"),
                "parent_district": props.get("district"),
                "centroid_lat": clat, "centroid_lon": clon,
                "distance_km": props.get("distance_km", _haversine(clat, clon)),
                "geometry_geojson": json.dumps(geom, ensure_ascii=False),
                "properties_json": json.dumps(props, ensure_ascii=False),
            })
    df = pd.DataFrame(rows)
    df["src_report"] = "src/geo/gis"
    df["src_year"] = None
    df["src_file"] = "data/geo"
    df["import_batch_id"] = int(dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d%H%M%S"))
    df["processed_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
    df["record_quality"] = "ok"
    df["quality_flags"] = None

    engine = make_engine()
    from src.warehouse.db import build_metadata
    from src.warehouse.schema import get_table
    build_metadata().create_all(engine, checkfirst=True)   # create dim_geo_feature if missing
    cols = [c.name for c in get_table("dim_geo_feature").all_columns()]
    df = df[[c for c in cols if c in df.columns]]
    with engine.begin() as conn:
        conn.exec_driver_sql("DELETE FROM dim_geo_feature")
    df.to_sql("dim_geo_feature", engine, if_exists="append", index=False)
    return len(df)


def export_geojson() -> None:
    """Copy canonical layers to the Power BI / web export folders (both modes —
    town-level aggregates, no personal data)."""
    for mode in ("internal", "shareable"):
        dst = PROJECT_ROOT / "data" / "warehouse" / "exports" / mode / "geo"
        dst.mkdir(parents=True, exist_ok=True)
        for gj in GEO_DIR.glob("*.geojson"):
            shutil.copy(gj, dst / gj.name)


def generate() -> dict:
    collections = gis_layers.build_all()
    n_features = load_to_warehouse(collections)
    html = maps_web.generate()
    export_geojson()
    return {"layers": {k: len(v) for k, v in collections.items()},
            "features_loaded": n_features, "map": html,
            "geojson_dir": str(GEO_DIR)}


def main():
    out = generate()
    print("GeoJSON layers:", out["layers"])
    print("dim_geo_feature rows:", out["features_loaded"])
    print("Interactive map:", out["map"])


if __name__ == "__main__":
    main()
