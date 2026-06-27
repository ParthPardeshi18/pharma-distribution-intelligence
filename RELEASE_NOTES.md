# Release Notes — v1.0.0

**Pharmaceutical Distribution Intelligence Platform — Version 1.0.0**
First production release. A reproducible, PII-safe decision-support platform that
turns ERP exports into reconciled analytics, decision intelligence, strategic
analysis, geographic intelligence, Power BI exports, and an executive report.

## Highlights

- **End-to-end pipeline** (`run_pipeline.py`) — one command builds the warehouse
  and every output, in `internal` (real) or `shareable` (anonymised) mode and any
  reporting currency.
- **Trusted warehouse** — SQLite star schema; financials reconcile to the ERP's
  own totals **to the rupee**; lineage/audit/quality on every row; **0 orphan
  keys**.
- **Decision Intelligence** — insights, root-cause, risks, opportunities, ranked
  recommendations, scorecards, and a configurable **Business Health Index**
  (5 weight profiles).
- **Strategic Analytics** — ABC/Pareto, RFM, product lifecycle, seasonality,
  multi-year trends, inventory ageing, and **forecasting with confidence
  intervals, model-quality metrics, assumptions, and business explanations**.
- **Geographic Intelligence (GIS)** — **GeoJSON as the canonical spatial format**;
  district/taluka/village boundaries, territories, routes, customer/warehouse
  points; warehouse `dim_geo_feature` table; an **interactive Leaflet map**.
- **Power BI** — clean star-schema CSV + GeoJSON exports (internal + anonymised),
  a data-model + DAX guide, and 8 stakeholder dashboard specs.
- **Executive Business Health Report** (`.docx`) — internal + shareable.
- **Security** — anonymisation layer + PII audit; raw data never committed.

## Metrics at release

- 4 financial years (FY 2022-23 → 2025-26) · ~488K warehouse rows.
- 4/4 financial reconciliations pass exactly; 0 orphan keys.
- **81 automated tests** passing on Python 3.11.
- Sales forecast backtest MAPE ≈ 11% (quality: good).

## Notable engineering decisions

- INR is the single source of truth; currency conversion is presentation-only.
- Schema-as-data: the warehouse schema and KPI registry generate their own docs.
- Float64-safe surrogate keys; recency+frequency churn tuned to route-based pharma
  distribution; ERP footer-row stripping (fixed a 2× total inflation).

See `CHANGELOG.md` for the full phase history and `docs/KNOWN_LIMITATIONS.md` for
current constraints.
