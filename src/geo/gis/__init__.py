"""GIS layer — GeoJSON is the CANONICAL geographic representation.

Lat/lon (config/geo_reference.csv) is now only a GEOCODING CACHE that seeds point
geometries; every spatial feature (district / taluka / village boundaries, sales
territories, delivery routes, customer & warehouse locations) is represented as
GeoJSON (RFC 7946) and stored as the source of truth. Layers are written to
data/geo/ and exported for Power BI Shape Maps, Leaflet, Mapbox, Azure Maps, and
deck.gl. The schema reserves GPS-trace, vehicle-route, and spatial-AI extension
points so those drop in without a redesign.
"""
from src.geo.gis.geojson import Feature, FeatureCollection

__all__ = ["Feature", "FeatureCollection"]
