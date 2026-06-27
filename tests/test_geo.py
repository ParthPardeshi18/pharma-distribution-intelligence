"""Geographic intelligence tests: geocoding, distance, territory, concentration."""
import pytest

from src.geo.geocode import Geocoder, haversine_km
from src.warehouse.db import DB_PATH

_skip = pytest.mark.skipif(not DB_PATH.exists(), reason="no warehouse db")


# --------------------------- geocoder (no DB) ---------------------------- #
def test_haversine_known_distance():
    # Shirur -> Pune ~ 60 km (straight line)
    d = haversine_km(18.8268, 74.3733, 18.5204, 73.8567)
    assert 50 < d < 75


def test_parse_day_prefixed_route():
    g = Geocoder()
    day, town, is_geo = g.parse("WED-2-RANJANGAON KAREGAON")
    assert day == "Wednesday"
    assert "RANJANGAON" in town
    assert is_geo


def test_non_geographic_route_flagged():
    g = Geocoder()
    _, _, is_geo = g.parse("MR ORDER")
    assert is_geo is False


def test_geocode_matches_town_and_distance():
    g = Geocoder()
    p = g.geocode("MON-PARNER")
    assert p.matched and p.town == "PARNER"
    assert p.delivery_day == "Monday"
    assert p.distance_km and p.distance_km > 0
    assert p.distance_band


def test_base_geocodes_to_zero_distance():
    g = Geocoder()
    p = g.geocode("SHIRUR-I")
    assert p.matched and p.distance_km == 0.0


# --------------------------- DB-backed ----------------------------------- #
@_skip
def test_territory_geocode_rate_high():
    from src.geo import territory
    t = territory.analyze()
    assert t.matched_pct >= 90        # nearly all geographic routes geocoded
    assert t.total_sales > 0


@_skip
def test_concentration_bands_and_hhi():
    from src.geo import concentration
    c = concentration.analyze()
    assert 0 <= c.hhi <= 10000
    assert 0 <= c.local_share_pct <= 100
    assert not c.distance_bands.empty
