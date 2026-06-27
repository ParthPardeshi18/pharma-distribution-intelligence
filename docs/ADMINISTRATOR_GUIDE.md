# Administrator Guide

For whoever runs, configures, and safeguards the platform.

## Configuration (no code changes)

| Concern | File |
|---|---|
| Raw header → canonical column names | `config/column_mappings.yaml` |
| Per-report grain / role / overrides / grouped-report ffill | `config/report_specs.yaml` |
| Entity-resolution thresholds | `config/entity_resolution.yaml` |
| KPI thresholds | `src/di/kpis.py` (registry) |
| Business Health Index weight profiles | `config/health_index.yaml` |
| Churn rules (inactivity, frequency) | `config/decision_intelligence.yaml` |
| Currencies & exchange rates | `config/currency_config.yaml`, `data/reference/exchange_rates.csv` |
| Anonymisation rules + audit allowlist | `config/anonymisation.yaml` |
| Geography (base, distance bands, weekday routes) | `config/geo.yaml`, `config/geo_reference.csv` |

## Security & PII (critical)
- **Never commit data.** `.gitignore` excludes all `data/`, raw exports, and real
  reports. Verify with `git status` before any commit.
- `data/secure/pii_lookup.csv` is the **only** real↔code bridge — restrict access,
  back up separately, never share.
- Run `python -m src.pii_audit --shareable` before sharing/committing any output.
- Internal outputs (`reports/internal/`, real exports) stay local; shareable
  outputs are anonymised.

## Routine operations
- **Monthly refresh:** drop new exports in `data/raw/`, run the pipeline, confirm
  `4/4 reconciliation PASS` and 0 orphan keys (`reports/warehouse_statistics.md`).
- **Onboard a new report:** add it to `config/report_specs.yaml`; the adapter and
  builder pick it up.
- **Add a currency:** add rows to `data/reference/exchange_rates.csv`.
- **Adjust health weighting:** edit `config/health_index.yaml` profiles.
- **Re-tune churn / thresholds:** edit `config/decision_intelligence.yaml` /
  `src/di/kpis.py`.

## Data quality governance
- Review `reports/data_validation.md` (reconciliation, orphans, anomalies) and the
  Data Quality dashboard each cycle.
- Entity-resolution **review queue**: `data/secure/customer_match_review.csv` —
  confirm/override; overrides go in `data/reference/customer_overrides.csv`.

## Backup checklist
- [ ] `data/raw/` (immutable source) · [ ] `data/secure/` (lookup, overrides)
- [ ] the repo (code + config) · everything else regenerates via the pipeline.

See `docs/warehouse_maintenance.md` for warehouse-level detail.
