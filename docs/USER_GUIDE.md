# User Guide (Business Owner / Analyst)

This platform answers: *How is the business doing, why, and what should I do?* —
without you reading raw dashboards.

## Run it
```bash
python run_pipeline.py --mode internal --currency INR
```
One command produces everything below in a few minutes.

## What you get (and which question it answers)

| Output | File | Answers |
|---|---|---|
| **Business Health Report** | `reports/internal/business_health_report.docx` | Overall verdict + top risks/opportunities/actions |
| **Decision Intelligence** | `reports/decision_intelligence.md` | Per-domain what/why/impact + Business Health Index |
| **Strategic Analysis** | `reports/strategic_analysis.md` | ABC/RFM, seasonality, lifecycle, **forecasts** |
| **Geographic Intelligence** | `reports/geo_intelligence.md` + `dashboards/geo/geo_intelligence_map.html` | Where sales come from; routes; coverage; expansion |
| **Data Quality dashboard** | `reports/data_quality_dashboard.html` | Is the data trustworthy this month? |
| **Power BI data** | `data/warehouse/exports/internal/` | Build/refresh your dashboards |

## Reading the key outputs

- **Business Health Index (0–100)** — one number for overall health, with a grade
  and the components that drive it. Switch the *weight profile* (Balanced, Cash
  Preservation, Growth, Profit, Conservative) to judge the business through
  different strategic lenses: `python -m src.di.run --profile cash_preservation`.
- **Risks / Opportunities / Recommendations** — ranked. Recommendations are
  ordered by impact × confidence ÷ effort, each with an expected ₹ impact.
- **Forecasts** — read the **confidence interval**, not the single number, and
  note the stated accuracy (e.g. "±11%") and assumptions.
- **Churn call list** — established retailers who've gone silent vs their own
  ordering cadence; hand it to route salesmen.
- **Interactive map** — open the HTML in a browser; toggle layers (sales
  choropleth, routes, customer density, coverage rings, expansion targets).

## Reporting currency
Add `--currency GBP` (or USD/EUR/AED) — the analysis is identical; only the
displayed currency changes (INR remains the stored source of truth).

## Portfolio / sharing
Use `--mode shareable` for an anonymised version safe to show externally, then run
`python -m src.pii_audit --shareable`. A ready anonymised sample lives in
`samples/`.

## Tips
- Re-run monthly after the ERP export; compare the Health Index over time.
- If a number looks wrong, check `reports/data_validation.md` — totals reconcile
  to the ERP to the rupee, so discrepancies point to the source export.
