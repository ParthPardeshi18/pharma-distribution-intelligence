"""Geographic Intelligence & Territory Analytics.

A geospatial pillar for the route-based distribution business: it parses
day-prefixed delivery routes, geocodes them to Maharashtra towns, computes
distance from the Shirur base, and analyses territory performance, geographic
concentration, distance-band coverage, and route productivity — with maps.
"""
from src.geo.geocode import Geocoder, haversine_km

__all__ = ["Geocoder", "haversine_km"]
