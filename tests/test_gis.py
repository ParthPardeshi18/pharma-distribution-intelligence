"""GIS tests: GeoJSON model, canonical layers, hierarchy, warehouse spatial load."""
import json

import pytest

from src.geo.gis.geojson import (
    Feature, FeatureCollection, is_valid_geojson, linestring, point, polygon,
)
from src.warehouse.db import DB_PATH

_skip = pytest.mark.skipif(not DB_PATH.exists(), reason="no warehouse db")


# --------------------------- GeoJSON model (no DB) ----------------------- #
def test_geojson_constructors_rfc7946():
    assert point(74.37, 18.82)["type"] == "Point"
    assert point(74.37, 18.82)["coordinates"] == [74.37, 18.82]   # [lon, lat]
    assert linestring([(0, 0), (1, 1)])["type"] == "LineString"
    assert polygon([[(0, 0), (1, 0), (1, 1), (0, 0)]])["type"] == "Polygon"


def test_feature_collection_valid_and_serialisable():
    fc = FeatureCollection(name="t")
    fc.add(Feature(point(74, 18), {"name": "x", "sales_inr": 10}, id="village:x"))
    d = fc.to_dict()
    assert is_valid_geojson(d)
    assert json.loads(json.dumps(d))["features"][0]["properties"]["name"] == "x"


# --------------------------- canonical layers (DB) ----------------------- #
@_skip
def test_build_all_layers_present_and_valid():
    from src.geo.gis import layers
    cols = layers.build_all()
    for need in ["districts", "talukas", "villages", "territories", "routes",
                 "customers", "warehouses"]:
        assert need in cols and len(cols[need]) >= 1
        assert is_valid_geojson(cols[need].to_dict())
    # boundary hierarchy: villages >= talukas >= districts
    assert len(cols["villages"]) >= len(cols["talukas"]) >= len(cols["districts"])


@_skip
def test_polygons_are_valid_shapely():
    from shapely.geometry import shape
    from src.geo.gis import layers
    cols = layers.build_all()
    for f in cols["villages"].features + cols["districts"].features:
        assert shape(f.geometry).is_valid


@_skip
def test_warehouse_spatial_layer_loaded():
    import pandas as pd
    from src.geo.gis import run as gis_run
    from src.warehouse.db import make_engine
    n = gis_run.load_to_warehouse(gis_run.gis_layers.build_all())
    assert n > 0
    layers = pd.read_sql("SELECT DISTINCT layer FROM dim_geo_feature", make_engine())
    assert {"villages", "districts", "routes"} <= set(layers["layer"])
