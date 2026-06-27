# Pharmaceutical Distribution Intelligence Platform

**Version 1.1** · Python 3.11 · 100 automated tests · reconciled to the rupee · PII-safe

A production-quality decision-support platform that turns raw ERP exports from a
mid-size pharmaceutical distributor into a **trusted warehouse, decision
intelligence, strategic analytics, geographic intelligence, an interactive web
app, and an executive report** — from a single command. One codebase, two modes:
an **internal** tool on real data and a **shareable**, fully anonymised portfolio
version.

> **v1.1** adds a **Streamlit web application** as the platform's primary user
> interface (authentication, caching, drill-down, GeoJSON maps, downloadable
> reports). See [docs/STREAMLIT_APP.md](docs/STREAMLIT_APP.md). Power BI is
> retained as an optional reporting layer.

> ⚠️ **Real company data with sensitive PII.** Read [SECURITY.md](SECURITY.md).
> No raw, processed, or warehouse data is ever committed; shareable outputs are
> anonymised and pass an automated PII audit.

![Architecture](docs/diagrams/architecture_stack.png)

## What it does

| Layer | Capability |
|---|---|
| **ERP Adapter** | One ERP boundary; canonical, ERP-agnostic data (32 report types) |
| **Warehouse** | SQLite star schema; lineage/audit/quality on every row; **4/4 reconciliations exact, 0 orphan keys** |
| **Decision Intelligence** | Insights, risks, opportunities, ranked recommendations, scorecards, and a configurable **Business Health Index** |
| **Strategic Analytics** | ABC/Pareto, RFM, lifecycle, seasonality, trends, ageing, and **forecasting with confidence intervals + model quality + assumptions** |
| **Geographic Intelligence** | **GeoJSON-canonical GIS** — district/taluka/village boundaries, territories, routes, customer/warehouse points; interactive maps |
| **Web application (v1.1)** | **Streamlit** multi-page app — the primary UI: auth + RBAC, cached engines, drill-down, pydeck GeoJSON maps, downloadable reports |
| **Presentation** | Executive Business Health Report (`.docx`); Power BI star-schema CSV + GeoJSON exports (optional layer) |

## Quick start

```bash
py -3.11 -m venv venv && venv\Scripts\activate     # Windows (see docs/INSTALLATION.md)
pip install -r requirements.txt
python run_pipeline.py --mode internal --currency INR     # builds everything (10 stages)
python -m streamlit run streamlit_app.py                  # launch the app (sign in: admin / admin123)
```
No real data? Explore the anonymised **[samples/](samples/)** dataset (CSV + GeoJSON).
The web app is the primary interface — see **[docs/STREAMLIT_APP.md](docs/STREAMLIT_APP.md)**.

## Documentation

- **Architecture & vision:** [ARCHITECTURE.md](docs/ARCHITECTURE.md) ·
  [Platform Vision & Roadmap (.docx)](reports/shareable/Platform_Vision_and_Roadmap_v1.0.docx)
- **Roadmaps:** [AI_ROADMAP.md](docs/AI_ROADMAP.md) · [GIS_ROADMAP.md](docs/GIS_ROADMAP.md) ·
  [ERP_EXPANSION.md](docs/ERP_EXPANSION.md) · [SAAS_VISION.md](docs/SAAS_VISION.md) ·
  [MATURITY_MODEL.md](docs/MATURITY_MODEL.md)
- **Data model:** [data_model.md](docs/data_model.md) ·
  [warehouse_schema.md](docs/warehouse_schema.md) ·
  [data_dictionary.md](docs/data_dictionary.md) ·
  [business_metadata_catalog.md](docs/business_metadata_catalog.md)
- **Guides:** [Installation](docs/INSTALLATION.md) · [Deployment](docs/DEPLOYMENT.md) ·
  [User](docs/USER_GUIDE.md) · [Administrator](docs/ADMINISTRATOR_GUIDE.md) ·
  [Developer](docs/DEVELOPER_GUIDE.md) · [Maintenance](docs/warehouse_maintenance.md)
- **Dashboards (Power BI):** [dashboards/specs/](dashboards/specs/) (8 stakeholder specs + data model + DAX + template)
- **Release:** [RELEASE_NOTES.md](RELEASE_NOTES.md) · [CHANGELOG.md](CHANGELOG.md) ·
  [Known limitations](docs/KNOWN_LIMITATIONS.md)

## Key architectural decisions

- **Raw is immutable**; every load reconciles to the ERP's own totals to the rupee.
- **Config over code** — column maps, report specs, KPI thresholds, currency,
  health-index weights, churn rules, and geocoding all live in `config/`.
- **Schema-as-data** — the warehouse schema and KPI registry generate their own docs.
- **INR is the source of truth**; currency conversion is presentation-only.
- **GeoJSON is the canonical spatial format**; lat/lon is only a geocoding cache.
- **PII-first** — anonymisation + audit gate every shareable output.
- **Future-proofed** — reserved tables for line items, GPS traces, and vehicle
  routes mean v2.0/v3.0 add layers, never a redesign.

## Repository layout

```
src/        adapters · warehouse · di · strategic · geo(/gis) · powerbi · report
app/        Streamlit UI (v1.1) — auth · cached data layer · components · views
config/     YAML config + geo_reference.csv + app_config/app_users
data/        raw / warehouse / secure / reference / geo   (gitignored)
reports/    internal (gitignored) + shareable (anonymised)
dashboards/ specs/ (Power BI) + geo/ (interactive map, gitignored)
docs/       architecture, roadmaps, guides, generated dictionary/catalog, diagrams
samples/    anonymised demo dataset (CSV + GeoJSON)
tests/      pytest suite (100 tests)
streamlit_app.py  the web application entry point (primary UI)
run_pipeline.py   one-command pipeline (10 stages)
```

## Status — v1.1 (a platform, not a finished project)

Phases 0 → 7 complete (v1.0); the **Streamlit application** ships as v1.1 and is
the primary interface. See [MATURITY_MODEL.md](docs/MATURITY_MODEL.md) for the
v2.0 (predictive/AI) and v3.0 (autonomous/multi-tenant SaaS) roadmap.

*Built as a real business system and a portfolio demonstration of data
engineering, BI, decision intelligence, GIS, and platform architecture.*
