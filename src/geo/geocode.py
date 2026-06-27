"""Geocoder — turn ERP route names into geography.

A route like ``WED-2-RANJANGAON KAREGAON`` is parsed into:
  delivery_day = Wednesday
  town         = Ranjangaon (matched to the geo reference)
  lat/lon, district, distance_from_base_km

Matching is by longest reference place-name found as a word in the cleaned route
string, so multi-town routes resolve to a known place. Administrative routes
(MR ORDER, OUTSTANDING PARTIES…) are flagged non-geographic.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from functools import lru_cache

import pandas as pd
import yaml

from src.utils import CONFIG_DIR, PROJECT_ROOT


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return r * 2 * math.asin(math.sqrt(a))


@dataclass
class GeoPoint:
    area_name: str
    delivery_day: str | None
    town: str | None
    display_name: str | None
    lat: float | None
    lon: float | None
    district: str | None
    distance_km: float | None
    distance_band: str | None
    is_geographic: bool
    matched: bool


class Geocoder:
    def __init__(self):
        self.cfg = yaml.safe_load((CONFIG_DIR / "geo.yaml").read_text(encoding="utf-8"))
        self.base = self.cfg["base"]
        self.weekdays = {k.upper(): v for k, v in self.cfg["weekday_tokens"].items()}
        self.non_geo = [p.upper() for p in self.cfg["non_geographic_patterns"]]
        self.bands = self.cfg["distance_bands_km"]
        self.band_labels = self.cfg["distance_band_labels"]
        ref = pd.read_csv(PROJECT_ROOT / self.cfg["geo_reference_path"])
        self.ref = ref
        # place_key -> row; sort keys by length desc for longest-match
        self._keys = sorted(ref["place_key"].str.upper().tolist(), key=len, reverse=True)
        self._by_key = {r.place_key.upper(): r for r in ref.itertuples()}

    # ------------------------------------------------------------------ #
    @staticmethod
    def _norm(s: str) -> str:
        s = re.sub(r"[^A-Z0-9 ]", " ", str(s).upper())
        return re.sub(r"\s+", " ", s).strip()

    def _band(self, km: float | None) -> str | None:
        if km is None:
            return None
        for i in range(len(self.bands) - 1):
            if self.bands[i] <= km < self.bands[i + 1]:
                return self.band_labels[i]
        return self.band_labels[-1]

    def parse(self, area_name: str) -> tuple[str | None, str, bool]:
        """Return (delivery_day, cleaned_town_string, is_geographic)."""
        norm = self._norm(area_name)
        is_geo = not any(p in norm for p in self.non_geo)
        tokens = norm.split()
        day = None
        if tokens and tokens[0] in self.weekdays:
            day = self.weekdays[tokens[0]]
            tokens = tokens[1:]
        # drop leading route numbers and stray digits
        tokens = [t for t in tokens if not t.isdigit()]
        return day, " ".join(tokens), is_geo

    @lru_cache(maxsize=512)
    def geocode(self, area_name: str) -> GeoPoint:
        day, town_str, is_geo = self.parse(area_name)
        matched_key = None
        if is_geo and town_str:
            padded = f" {town_str} "
            for key in self._keys:                       # longest first
                if f" {key} " in padded or town_str == key:
                    matched_key = key
                    break
        if matched_key is None:
            return GeoPoint(area_name, day, town_str or None, None, None, None,
                            None, None, None, is_geo, False)
        r = self._by_key[matched_key]
        km = round(haversine_km(self.base["lat"], self.base["lon"], r.lat, r.lon), 1)
        return GeoPoint(area_name, day, matched_key, r.display_name, r.lat, r.lon,
                        r.district, km, self._band(km), is_geo, True)

    def geocode_frame(self, area_names) -> pd.DataFrame:
        recs = [self.geocode(a).__dict__ for a in area_names]
        return pd.DataFrame(recs)
