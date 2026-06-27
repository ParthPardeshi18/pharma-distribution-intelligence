# Developer Guide

How the codebase is organised and how to extend it safely.

## Layout
```
src/
  adapters/     ERP Adapter layer (base + MediVisionAdapter)
  warehouse/    schema registry, db, build, metrics, validation, stats, catalog
  di/           Decision Intelligence: kpis, engines, churn, health_index,
                domains/, run
  strategic/    ABC/RFM/lifecycle/seasonality/trends/ageing/forecasting/run
  geo/          geocoding + territory/concentration; gis/ = GeoJSON layers + maps
  powerbi/      star-schema CSV + GeoJSON exports
  report/       Business Health Report (.docx)
  anonymise.py, pii_audit.py, currency.py, entity_resolution.py, utils.py
config/         all YAML config + geo_reference.csv
docs/           architecture, roadmaps, guides, generated dictionary/catalog
tests/          pytest suite (81 tests)
run_pipeline.py one-command orchestrator (10 stages)
```

## Core contracts (don't break these)
- **Adapter → everything:** modules above the adapter consume only
  `CanonicalFrame` (canonical columns). New ERP = new adapter (see
  `docs/ERP_EXPANSION.md`).
- **Schema-as-data:** `src/warehouse/schema.py` is the single source of truth;
  the data dictionary, business catalog, and physical tables are generated from
  it. Add columns/tables there, not ad hoc.
- **KPI registry:** `src/di/kpis.py` defines units/thresholds/scoring once; DI,
  scorecards, and the Health Index all read it.
- **GeoJSON canonical:** spatial features live in `dim_geo_feature` as GeoJSON;
  lat/lon is only a cache.
- **INR source of truth:** never store converted money; convert at presentation
  (`src/currency.py`).

## How to add things
- **A KPI:** add a `KPISpec` to the registry; reference it in a domain analyzer.
- **A domain analyzer:** add `src/di/domains/<x>.py` exposing `analyze()`; append
  to `ALL`.
- **A warehouse table:** add a `TableSpec` (build_now True/False); write a builder
  in `build.py` if it loads data.
- **A strategic analysis:** add `src/strategic/<x>.py`; surface in `strategic/run.py`.
- **A GeoJSON layer:** build a `FeatureCollection` in `src/geo/gis/layers.py`.
- **An AI model (v2.0):** read warehouse views, write a `fact_<x>_prediction`
  table with standard lineage columns; register in `config/ai_models.yaml`.

## Testing & quality
- `python -m pytest -q` — DB-backed tests skip cleanly if no warehouse yet.
- Every phase adds tests; keep reconciliation and PII-audit green.
- Run `python -m src.pii_audit --shareable` before sharing outputs.
- Conventions: stdlib + the pinned stack; config over hardcoding; mask PII in any
  console/log output; reconcile to raw on every load.

## Build & docs
- Regenerate docs: `python -m src.warehouse.catalog`.
- Full run: `python run_pipeline.py --mode internal --currency INR`.
