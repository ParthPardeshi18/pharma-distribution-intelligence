# Changelog

All notable changes to this project. Format based on *Keep a Changelog*;
this project uses phase-based development culminating in semantic versions.

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
