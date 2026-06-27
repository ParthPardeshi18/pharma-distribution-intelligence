"""RFC 7946 GeoJSON model — the canonical spatial representation.

Thin, dependency-light wrappers for Feature / FeatureCollection plus geometry
constructors and shapely <-> GeoJSON bridges. Coordinates are [lon, lat] per the
spec. Every layer the project produces is a FeatureCollection serialised here.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


# --------------------------- geometry constructors ------------------------ #
def point(lon: float, lat: float) -> dict:
    return {"type": "Point", "coordinates": [round(lon, 6), round(lat, 6)]}


def linestring(coords: list[tuple[float, float]]) -> dict:
    return {"type": "LineString",
            "coordinates": [[round(x, 6), round(y, 6)] for x, y in coords]}


def polygon(rings: list[list[tuple[float, float]]]) -> dict:
    return {"type": "Polygon",
            "coordinates": [[[round(x, 6), round(y, 6)] for x, y in ring] for ring in rings]}


def geom_from_shapely(geom) -> dict | None:
    """shapely geometry -> GeoJSON geometry dict."""
    if geom is None or geom.is_empty:
        return None
    from shapely.geometry import mapping
    g = mapping(geom)
    # round coordinates for compact, stable files
    return json.loads(json.dumps(g), parse_float=lambda s: round(float(s), 6))


def shapely_from_geojson(geom: dict):
    from shapely.geometry import shape
    return shape(geom)


# --------------------------- feature model -------------------------------- #
@dataclass
class Feature:
    geometry: dict | None
    properties: dict = field(default_factory=dict)
    id: str | int | None = None

    def to_dict(self) -> dict:
        d = {"type": "Feature", "geometry": self.geometry, "properties": self.properties}
        if self.id is not None:
            d["id"] = self.id
        return d


@dataclass
class FeatureCollection:
    features: list = field(default_factory=list)
    name: str = ""
    crs_note: str = "WGS84 (EPSG:4326)"

    def add(self, feature: Feature) -> None:
        self.features.append(feature)

    def to_dict(self) -> dict:
        return {"type": "FeatureCollection", "name": self.name,
                "metadata": {"crs": self.crs_note, "count": len(self.features)},
                "features": [f.to_dict() for f in self.features]}

    def write(self, path: str | Path) -> str:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), ensure_ascii=False), encoding="utf-8")
        return str(path)

    def __len__(self):
        return len(self.features)


def load(path: str | Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def is_valid_geojson(d: dict) -> bool:
    if d.get("type") != "FeatureCollection":
        return False
    for f in d.get("features", []):
        if f.get("type") != "Feature" or "geometry" not in f or "properties" not in f:
            return False
    return True
