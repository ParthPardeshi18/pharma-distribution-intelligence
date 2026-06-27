# Changelog

All notable changes to this project. Format based on *Keep a Changelog*;
this project uses phase-based development culminating in semantic versions.

## [1.1.0] — 2026-06-27

**Streamlit application — the platform's primary user interface.** A modular,
multi-page web app that consumes the existing warehouse, Decision Intelligence
engine, Strategic Analytics, GIS layer, forecasting, KPI registry, and Business
Health Index **without duplicating any business logic** — every figure is still
computed in `src/` and is merely cached and rendered by the app.

### Added — `app/` package + `streamlit_app.py`
- **Authentication & RBAC** — login gate with SHA-256 (salted) credentials in a
  gitignored `config/app_users.yaml`; three roles (admin / analyst / viewer) map
  to allowed pages in `config/app_config.yaml`.
- **Cached data layer** (`app/data.py`) — `@st.cache_data` / `@st.cache_resource`
  wrappers over every `src/` engine; **zero logic duplication**.
- **Seven pages** — Overview/BHI (gauge, headline KPIs, per-profile scores, top
  risks/opportunities), Decision Intelligence drill-down (metrics, insights,
  root-cause, risks, opportunities, prioritised recommendation matrix, scorecard),
  Strategic Analytics (ABC, RFM, lifecycle, seasonality, trends, ageing,
  profitability), Forecasting (confidence-interval charts + model quality +
  assumptions), Geographic (native **pydeck GeoJSON** maps + territory &
  concentration analytics), Reports & Downloads (.docx report, GeoJSON, CSV
  exports), and Data Quality (row counts, orphan keys, quality breakdown).
- **Interactive controls** — presentation-currency selector (INR source of truth),
  Business Health Index weight-profile selector, fiscal-year filter, drill-down
  navigation, and one-click downloads (.docx / CSV / GeoJSON).
- **AI summaries** — executive narratives always come from the local DI engine
  (offline, always available); an **optional** Claude (`claude-opus-4-8`)
  enhancer (`app/ai.py`) polishes them into board-ready prose when enabled in
  config — off by default, degrades silently.
- **Theme** (`.streamlit/config.toml` + `app/theme.py`) — navy/slate palette
  matching the executive `.docx` report.
- **Tests** — `tests/test_streamlit_app.py`: auth/RBAC/config/formatter unit tests
  plus `streamlit.testing` AppTest coverage of the auth gate and every page
  rendering against the real warehouse.

### Privacy — internal vs public data modes
- **Two physically separate warehouses**: `erp_warehouse.db` (internal, real
  identities) and `erp_warehouse_shareable.db` (anonymous codes). Surrogate keys
  are identical across both, so every engine works unchanged on either.
  `src/warehouse/db.py` resolves the active file from `ERP_WAREHOUSE_MODE` /
  `ERP_WAREHOUSE_DB`; the builder writes each mode to its own file.
- **The app is mode-aware end to end.** `app/data.bind_mode()` binds the engines;
  mode is part of **every cache key** so the two modes can never serve each
  other's rows. In public (`shareable`) mode the app never opens the real-name
  database, and the DI narratives — which interpolate the now-anonymous codes —
  are anonymised automatically.
- **Controls & guardrails** — `PDI_MODE` env / `app.mode` config selects the mode
  (default `internal`); an admin can preview the other mode from the sidebar
  (cache-cleared on switch); a coloured banner marks every page (🔒 internal /
  🔓 anonymised); the Reports page generates only the anonymised `.docx` in public
  mode. New tests assert that shareable mode returns only `Customer_/Supplier_/
  Salesman_` codes and that pages render leak-free.
- `run_pipeline.py` binds `ERP_WAREHOUSE_MODE` so all stages read the right file.

### Positioning
- The Streamlit app is the **primary interface**. Power BI is retained as an
  **optional** reporting layer (star-schema CSV exports + stakeholder specs).

## [1.0.0] — 2026-06-27

First production release. Built phase by phase, each gated by review,
reconciliation, tests, and a PII audit.

### Phase 0 — Discovery, setup & PII protection
- Project scaffold; immutable raw-data copy; discovery report (PII masked).
- Anonymisation layer + PII audit; security guardrails (`.gitignore`, `SECURITY.md`).

### Phase 1 — Data model & ERP Adapter
- ERP Adapter layer (single ERP boundary); canonical column mapping for 32 report
  types; data model (ERD) and star-schema design; entity-resolution strategy.

### Phase 2 — Cleaning, validation & warehouse
- SQLite star schema with lineage/audit/quality on every row; entity resolution
  (confidence + review queue); currency service (INR base); validation,
  statistics, and Data Quality dashboard; data dictionary + business catalog.
- Caught & fixed: ERP footer rows inflating totals 2×; float64 key precision.

### Phase 3 — Decision Intelligence (+ calibration)
- KPI registry, reusable engines (insight/risk/opportunity/recommendation/
  scorecard), 9 domain analyzers, configurable **Business Health Index**.
- Owner-calibrated: recency+frequency churn, margin/turnover thresholds, BHI
  weight profiles.

### Phase 4 — Strategic analyses
- ABC/Pareto, RFM, product lifecycle, seasonality, multi-year trends, inventory
  ageing, profitability ranking; forecasting with CI + model quality + assumptions
  + business explanations.

### Phase 5 — Executive dashboard specifications
- Power BI star-schema CSV exporter (internal + anonymised shareable);
  data-model + DAX guide; 7 stakeholder dashboard specs.

### Phase 6 — Business Health Report
- Executive `.docx` report (internal + shareable) with 2×2 impact-vs-effort
  recommendations and embedded charts.

### Phase 6.5 — Geographic Intelligence
- Route geocoding, territory & concentration analytics, distance bands,
  delivery-day productivity, static maps.

### Phase 6.6 — GIS architecture
- **GeoJSON canonical** spatial layers (boundaries/territories/routes/points);
  `dim_geo_feature` warehouse table; interactive Leaflet map; GPS/vehicle-route
  extension points.

### Phase 7 — v1.0 platform vision & release
- Architecture, AI/GIS roadmaps, ERP expansion, SaaS vision, maturity model;
  full documentation suite; portfolio deliverables; **v1.0.0**.

### Tooling
- Migrated runtime to **Python 3.11** (full scientific + geospatial stack:
  matplotlib, Prophet, scikit-learn, statsmodels, shapely, scipy).

## [Unreleased]
See `docs/AI_ROADMAP.md`, `docs/GIS_ROADMAP.md`, `docs/MATURITY_MODEL.md`.
