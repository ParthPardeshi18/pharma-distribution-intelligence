# Warehouse Maintenance Guide

This guide lets another developer understand, run, and maintain the warehouse
**without reading the code**. For column-level detail see
[data_dictionary.md](data_dictionary.md); for business meaning see
[business_metadata_catalog.md](business_metadata_catalog.md).

## 1. What the warehouse is

A SQLite star-schema warehouse (`data/warehouse/erp_warehouse.db`) built from
MediVision Platinum ERP Excel exports. Conformed dimensions + facts at their true
grain. All money is stored in **INR** (the source of truth); currency conversion
happens only in the reporting layer.

## 2. The layers (data flow)

```
data/raw/*.xlsx  ──►  ERP Adapter  ──►  Warehouse Builder  ──►  erp_warehouse.db
 (immutable)        src/adapters/        src/warehouse/build.py     (star schema)
                    canonical columns    resolve keys, dims,
                    (ERP-agnostic)       facts, lineage, reconcile
```

- **ERP Adapter** (`src/adapters/`) — the ONLY place that knows the ERP's quirks
  (banner rows, header detection, footer/total stripping, column names). It emits
  canonical, ERP-agnostic frames. If the ERP changes, change only this layer.
- **Warehouse Builder** (`src/warehouse/build.py`) — resolves entity keys, builds
  dimensions and facts, stamps lineage/audit/quality on every row, reconciles
  totals against the raw ERP, and writes the database + an import-batch audit row.

## 3. How to refresh the warehouse

1. Drop new ERP exports into `data/raw/<Domain>/` (same filename pattern, e.g.
   `Sales_26-27.xlsx`). Raw files are read-only and never modified.
2. Run the pipeline:
   ```
   python run_pipeline.py --mode internal --currency INR
   ```
3. Review the generated reports:
   - `reports/data_validation.md` — totals must reconcile (raw == warehouse).
   - `reports/warehouse_statistics.md` — row counts, size, orphans, duration.
   - `reports/data_quality_dashboard.html` — completeness, duplicates, unmatched.
4. If reconciliation fails, STOP and investigate the adapter (usually a new
   column name or a new footer variant). Do not ship a failed reconciliation.

## 4. Configuration (no code changes needed)

| Concern | File |
|---|---|
| Raw header→canonical column names | `config/column_mappings.yaml` |
| Per-report grain / role / overrides | `config/report_specs.yaml` |
| Entity-resolution thresholds | `config/entity_resolution.yaml` |
| Currencies & exchange rates | `config/currency_config.yaml`, `data/reference/exchange_rates.csv` |
| Anonymisation rules | `config/anonymisation.yaml` |

To onboard a **new report**: add its key to `report_specs.yaml` (role, grain,
column overrides). The adapter and builder pick it up automatically.

## 5. Internal vs shareable mode

- `--mode internal` — `*_code` columns hold real names (local only; DB gitignored).
- `--mode shareable` — `*_code` columns hold anonymous codes (`Customer_0001`).
- **Keys are identical in both modes**, so all analytics/dashboards are identical;
  only the displayed identity differs. Run `python -m src.pii_audit --shareable`
  before sharing anything.

## 6. Entity resolution (customer names)

Suppliers and products match the master ~100% by name. Customers use the resolver
(`src/entity_resolution.py`): exact → fuzzy (≥92, unambiguous) → review queue →
unresolved surrogate. Uncertain matches are **never auto-merged**; they land in
`data/secure/customer_match_review.csv` for a human, and overrides go in
`data/reference/customer_overrides.csv`. Unresolved customers still get a stable
key so analysis is never blocked.

## 7. Standard columns on every table

`src_report, src_year, src_file` (lineage) · `import_batch_id, processed_at`
(audit) · `record_quality, quality_flags` (governance). Join `import_batch_id` to
`meta_import_batch` to see which build produced any row.

## 8. Known data-quality issues

- **No sales/purchase line items** in the ERP → no bill×product grain; customer×
  product analysis is not possible until the ERP exports a register with lines.
  The schema reserves `fact_sales_line` / `fact_purchase_line` for that day.
- **`Salesman_Master` is misaligned** in the export (name column largely blank);
  `dim_salesman` is sparse. No fact references salesman, so no measure is affected.

## 9. Decision Intelligence calibration (business-tuned)

The DI layer (`src/di/`) is calibrated to **route-based pharma distribution**, not
generic statistics:
- **KPI thresholds** live in `src/di/kpis.py` (e.g. healthy gross margin 6%,
  inventory turnover 9×). Adjust there if the business profile changes.
- **Customer churn** is recency + frequency based (`src/di/churn.py`,
  `config/decision_intelligence.yaml`): a retailer is "churned" when silent beyond
  a multiple of *their own* ordering cadence — cash vs credit is NOT split (both
  are repeat route customers; cash just means paid-on-delivery).
- **Business Health Index** supports weight **profiles**
  (`config/health_index.yaml`): balanced, conservative, growth, cash_preservation,
  profit_optimization, custom. Run `python -m src.di.run --profile cash_preservation`.

## 10. Regenerating documentation

```
python -m src.warehouse.catalog     # data dictionary + business catalog
python -m src.warehouse.validation  # validation report (rebuilds + validates)
python -m src.warehouse.stats       # statistics report
python -m src.quality               # data quality dashboard (HTML + CSV)
```
