# ERP Business Intelligence & Decision-Support System

A production-quality BI and decision-support system for **a mid-size
pharmaceutical distribution firm in India**, built from ERP exports. One codebase
produces two outputs: an **internal** decision tool on real data and a
**shareable**, fully anonymised portfolio version.

> ⚠️ **Real company data with sensitive PII.** Read [SECURITY.md](SECURITY.md)
> before doing anything. No raw, processed, or warehouse data is ever committed.

## Status

Built phase by phase (see `ERP_BI_PLAN.md` for the master spec):

- ✅ **Phase 0 — Discovery, setup & PII protection**
- ✅ **Phase 1 — Data model & relationship mapping** (ERP Adapter, ERD, star schema)
- ✅ **Phase 2 — Cleaning, validation & warehouse build**
- ✅ **Phase 3 — Decision Intelligence layer** (KPIs, insights, risks, opportunities, recommendations, scorecards, Business Health Index)
- ✅ **Phase 4 — Strategic analyses** (ABC/Pareto, RFM, lifecycle, seasonality, multi-year trends, inventory ageing, profitability ranking, forecasting with confidence intervals)
- ✅ **Phase 5 — Executive dashboard specifications** (7 Power BI stakeholder specs + star-schema CSV exports, internal + anonymized shareable) *(under review)*
- ⬜ Phase 6 — Business health report
- ⬜ Phase 7 — Roadmap & AI enhancement plan

## Architecture (key decisions)

- **Raw is immutable.** Exports copied to `data/raw/` (read-only); all cleaning emits new files; every step reconciles totals against raw.
- **Config over code.** Column mappings, report specs, anonymisation, and currency live in `config/*.yaml`.
- **PII-first.** Anonymisation (`src/anonymise.py`) + audit (`src/pii_audit.py`) are the foundation.
- **Star-schema warehouse** in SQLite (`data/warehouse/erp_warehouse.db`).
- **INR is the source of truth**; a configurable reporting-currency layer converts at presentation time (INR/GBP/EUR/USD …). Analytics are currency-agnostic.
- **Dual-mode:** `run_pipeline.py --mode {internal|shareable} --currency {INR|…}`.

## Setup

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

## Usage

```bash
# Phase 0 — discovery & PII
python -m src.discovery            # profile raw exports -> docs/discovery_report.md (PII masked)
python -m src.anonymise --build    # build secure lookup data/secure/pii_lookup.csv
python -m src.pii_audit --shareable  # gate before sharing

# Phase 2-3 — full pipeline: warehouse + validation + stats + DQ dashboard + decision intelligence
python run_pipeline.py --mode internal  --currency INR
python run_pipeline.py --mode shareable --currency GBP

# Decision intelligence only (reuses the existing warehouse)
python -m src.di.run        # -> reports/decision_intelligence.md + Business Health Index
```

**Decision Intelligence** (`src/di/`) turns the warehouse into a system that
*explains the business and recommends actions*: a central KPI registry
(`src/di/kpis.py`), reusable engines (insight / root-cause / risk / opportunity /
recommendation / scorecard), nine domain analyzers, and a configurable
**Business Health Index** (`config/health_index.yaml`).

Outputs: `data/warehouse/erp_warehouse.db`, `reports/data_validation.md`,
`reports/warehouse_statistics.md`, `reports/data_quality_dashboard.html`,
`docs/data_dictionary.md`, `docs/business_metadata_catalog.md`. See
[docs/warehouse_maintenance.md](docs/warehouse_maintenance.md).

## Repository layout

```
src/        pipeline modules (utils, discovery, anonymise, pii_audit, …)
config/     YAML config (column_mappings, report_specs, anonymisation, currency)
data/       raw / processed / warehouse / secure / reference   (ALL gitignored)
analysis/   per-domain analysis scripts
reports/    internal (gitignored) + shareable
dashboards/ internal (gitignored) + shareable  (Power BI specs)
docs/       discovery report, data model, schema, data dictionary
tests/      pytest suite
```
