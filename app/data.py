"""Cached data-access layer.

Every function here is a thin, cached wrapper over an existing engine in ``src/``.
**No business logic lives in this module** — it only memoises results so the UI
stays responsive. Expensive, read-only computations use ``@st.cache_data``;
long-lived handles (DB engine, currency converter) use ``@st.cache_resource``.

**Mode-keyed caching.** The platform serves two warehouses — ``internal`` (real
identities) and ``shareable`` (anonymised). The active mode is part of every
cache key (passed explicitly to the cached implementation), so the two modes can
never serve each other's rows. ``bind_mode()`` sets the engine target; the public
accessors resolve the active mode and thread it into the cache key.

If the warehouse for the active mode has not been built, accessors raise
``WarehouseMissing`` so views can show a friendly message instead of a traceback.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import streamlit as st

from src.warehouse.db import current_db_path, make_engine

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GEO_DIR = PROJECT_ROOT / "data" / "geo"

# Cache TTL for warehouse-derived results (seconds). The warehouse is rebuilt by
# a batch pipeline, not live, so an hour is comfortable.
_TTL = 3600


class WarehouseMissing(RuntimeError):
    """Raised when the SQLite warehouse for the active mode has not been built."""


# ── Mode ─────────────────────────────────────────────────────────────────────
def bind_mode(mode: str) -> None:
    """Point the engines at the warehouse file for ``mode`` (internal | shareable).

    Sets ``ERP_WAREHOUSE_MODE`` so every ``make_engine()`` in ``src/`` resolves to
    the right database. The app calls this once per run before any data access; in
    shareable mode the engines therefore **never** touch the real-name database.
    """
    os.environ["ERP_WAREHOUSE_MODE"] = mode


def active_mode() -> str:
    return os.environ.get("ERP_WAREHOUSE_MODE", "internal")


def active_db_path() -> Path:
    return current_db_path(active_mode())


def warehouse_exists() -> bool:
    return active_db_path().exists()


def _require_warehouse() -> None:
    if not warehouse_exists():
        raise WarehouseMissing(
            f"No warehouse found at {active_db_path().name}. Build it first — "
            "internal: `python run_pipeline.py --mode internal`; "
            "shareable (anonymised): `python run_pipeline.py --mode shareable`."
        )


# ── Long-lived resources (mode-keyed) ───────────────────────────────────────
@st.cache_resource
def _engine(mode: str):
    return make_engine(current_db_path(mode))


def engine():
    return _engine(active_mode())


@st.cache_resource
def converter():
    from src.currency import CurrencyConverter

    return CurrencyConverter()


# ── Decision Intelligence ───────────────────────────────────────────────────
@st.cache_data(ttl=_TTL, show_spinner="Running Decision Intelligence…")
def _domain_reports(mode: str):
    _require_warehouse()
    from src.di.domains import ALL

    return [m.analyze() for m in ALL]


def domain_reports():
    """list[DomainReport] — runs all nine domain analyzers for the active mode."""
    return _domain_reports(active_mode())


def domain_report(domain: str):
    for r in domain_reports():
        if r.domain == domain:
            return r
    return None


@st.cache_data(ttl=_TTL, show_spinner=False)
def _health(mode: str, profile: str | None):
    from src.di import health_index

    return health_index.compute(_domain_reports(mode), profile=profile)


def health(profile: str | None = None):
    return _health(active_mode(), profile)


@st.cache_data(ttl=_TTL, show_spinner=False)
def _profile_scores(mode: str) -> dict:
    from src.di import health_index

    return health_index.compute_all_profiles(_domain_reports(mode))


def profile_scores() -> dict:
    return _profile_scores(active_mode())


@st.cache_data(ttl=_TTL, show_spinner=False)
def list_profiles() -> list[str]:
    from src.di import health_index

    return health_index.list_profiles()


# ── Warehouse facts / health ────────────────────────────────────────────────
@st.cache_data(ttl=_TTL, show_spinner=False)
def fiscal_years() -> list[str]:
    from src.di import warehouse_api as W

    return list(W.FYS)


def current_fy() -> str:
    from src.di import warehouse_api as W

    return W.CURRENT_FY


def prior_fy() -> str:
    from src.di import warehouse_api as W

    return W.PRIOR_FY


@st.cache_data(ttl=_TTL, show_spinner=False)
def _sales_by_fy(mode: str):
    _require_warehouse()
    from src.di import warehouse_api as W

    return W.sales_by_fy()


def sales_by_fy():
    return _sales_by_fy(active_mode())


@st.cache_data(ttl=_TTL, show_spinner=False)
def _purchases_by_fy(mode: str):
    _require_warehouse()
    from src.di import warehouse_api as W

    return W.purchases_by_fy()


def purchases_by_fy():
    return _purchases_by_fy(active_mode())


@st.cache_data(ttl=_TTL, show_spinner=False)
def _row_counts(mode: str) -> dict:
    _require_warehouse()
    from src.warehouse.metrics import table_row_counts

    return table_row_counts(engine())


def row_counts() -> dict:
    return _row_counts(active_mode())


@st.cache_data(ttl=_TTL, show_spinner=False)
def _orphans(mode: str) -> list:
    _require_warehouse()
    from src.warehouse.metrics import orphans as _o

    return _o(engine())


def orphans() -> list:
    return _orphans(active_mode())


@st.cache_data(ttl=_TTL, show_spinner=False)
def _quality_breakdown(mode: str):
    _require_warehouse()
    from src.warehouse.metrics import quality_status_breakdown

    return quality_status_breakdown(engine())


def quality_breakdown():
    return _quality_breakdown(active_mode())


def db_size_bytes() -> int:
    from src.warehouse.metrics import db_size_bytes as _sz

    return _sz()


# ── Strategic analytics ─────────────────────────────────────────────────────
@st.cache_data(ttl=_TTL, show_spinner=False)
def _abc(mode: str, entity: str, fy: str | None):
    _require_warehouse()
    from src.strategic import abc_pareto

    return {"customers": abc_pareto.customers,
            "products": abc_pareto.products,
            "suppliers": abc_pareto.suppliers}[entity](fy)


def abc(entity: str, fy: str | None = None):
    return _abc(active_mode(), entity, fy)


@st.cache_data(ttl=_TTL, show_spinner=False)
def _rfm(mode: str):
    _require_warehouse()
    from src.strategic import rfm as _r

    return _r.analyze()


def rfm():
    return _rfm(active_mode())


@st.cache_data(ttl=_TTL, show_spinner=False)
def _lifecycle(mode: str):
    _require_warehouse()
    from src.strategic import lifecycle as _lc

    return _lc.analyze()


def lifecycle():
    return _lifecycle(active_mode())


@st.cache_data(ttl=_TTL, show_spinner=False)
def _seasonality(mode: str):
    _require_warehouse()
    from src.strategic import seasonality as _se

    return _se.analyze()


def seasonality():
    return _seasonality(active_mode())


@st.cache_data(ttl=_TTL, show_spinner=False)
def _trends(mode: str):
    _require_warehouse()
    from src.strategic import trends as _tr

    return _tr.analyze()


def trends():
    return _trends(active_mode())


@st.cache_data(ttl=_TTL, show_spinner=False)
def _inventory_ageing(mode: str):
    _require_warehouse()
    from src.strategic import inventory_ageing as _ia

    return _ia.analyze()


def inventory_ageing():
    return _inventory_ageing(active_mode())


@st.cache_data(ttl=_TTL, show_spinner=False)
def _profitability(mode: str, entity: str, fy: str | None, n: int):
    _require_warehouse()
    from src.strategic import profitability_ranking as _pr

    return {"customers": _pr.customers, "products": _pr.products,
            "suppliers": _pr.suppliers, "territories": _pr.territories}[entity](fy, n)


def profitability(entity: str, fy: str | None = None, n: int = 10):
    return _profitability(active_mode(), entity, fy, n)


# ── Forecasting (heavier — Prophet/SARIMAX) ─────────────────────────────────
@st.cache_data(ttl=_TTL, show_spinner="Fitting sales forecast…")
def _forecast_sales(mode: str, periods: int):
    _require_warehouse()
    from src.strategic import forecasting

    return forecasting.forecast_sales(periods)


def forecast_sales(periods: int = 6):
    return _forecast_sales(active_mode(), periods)


@st.cache_data(ttl=_TTL, show_spinner="Fitting purchases forecast…")
def _forecast_purchases(mode: str, periods: int):
    _require_warehouse()
    from src.strategic import forecasting

    return forecasting.forecast_purchases(periods)


def forecast_purchases(periods: int = 6):
    return _forecast_purchases(active_mode(), periods)


# ── Geographic / GIS ────────────────────────────────────────────────────────
@st.cache_data(ttl=_TTL, show_spinner=False)
def _territory(mode: str, fy: str | None):
    _require_warehouse()
    from src.geo import territory as _t

    return _t.analyze(fy)


def territory(fy: str | None = None):
    return _territory(active_mode(), fy)


@st.cache_data(ttl=_TTL, show_spinner=False)
def _geo_concentration(mode: str, fy: str | None):
    _require_warehouse()
    from src.geo import concentration as _c

    return _c.analyze(fy)


def geo_concentration(fy: str | None = None):
    return _geo_concentration(active_mode(), fy)


def geojson_layers() -> list[str]:
    """Available GeoJSON layer names under data/geo/. Town-aggregated, not PII —
    identical across modes."""
    if not GEO_DIR.exists():
        return []
    return sorted(p.stem for p in GEO_DIR.glob("*.geojson"))


@st.cache_data(ttl=_TTL, show_spinner=False)
def geojson(layer: str) -> dict | None:
    """Load a canonical GeoJSON FeatureCollection (RFC 7946) as a dict."""
    path = GEO_DIR / f"{layer}.geojson"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


# ── Currency presentation helpers ───────────────────────────────────────────
def money(amount_inr, currency: str = "INR", fy: str | None = None) -> str:
    """Convert an INR amount to the presentation currency and format it.

    INR remains the source of truth; this only affects display.
    """
    if amount_inr is None:
        return "—"
    conv = converter()
    try:
        value = conv.convert(amount_inr, currency, fy) if currency != "INR" else amount_inr
        return conv.format(value, currency)
    except Exception:
        # Unsupported currency or missing rate → fall back to compact INR.
        return compact_inr(amount_inr)


def compact_inr(amount) -> str:
    """₹ in lakh/crore shorthand for dashboard tiles."""
    if amount is None:
        return "—"
    a = float(amount)
    sign = "-" if a < 0 else ""
    a = abs(a)
    if a >= 1e7:
        return f"{sign}₹{a / 1e7:.2f} Cr"
    if a >= 1e5:
        return f"{sign}₹{a / 1e5:.2f} L"
    return f"{sign}₹{a:,.0f}"
