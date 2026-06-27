# Power BI Template Blueprint (`.pbit`)

A `.pbit` is authored in Power BI Desktop (binary). This blueprint is the
specification to build it from — load it, follow the steps, and "Save As → Power
BI template" to produce `pharma_distribution_intelligence.pbit`.

## 1. Data source
Folder connector → `data/warehouse/exports/{internal|shareable}/` (or `samples/`
for a demo). Load all `*.csv` + `dim_route_geo.csv`; add `geo/*.geojson` for Shape
Maps. Parameterise the folder path as a template parameter `ExportFolder`.

## 2. Model
- Relationships and the reporting-currency (`dim_rate`) pattern: see
  `powerbi_data_model.md`.
- Mark `dim_date` as the date table.
- Add the DAX measures library from `powerbi_data_model.md` §4.

## 3. Pages (one per stakeholder spec)
Build the 8 pages from `dashboards/specs/`:
Owner/CEO · Finance · Sales · Inventory · Procurement · Operations · Working
Capital · Geographic. Each spec lists visuals, measures, slicers, and
drill-throughs.

## 4. Theme
Apply the brand theme (navy `#1F3A5F`, accent `#2A7AB0`, green `#1E7E34`, amber
`#B06A00`, red `#B11B1B`). Conditional-formatting bands from the KPI registry
(margin 6%/3%, turnover 9×, debtor days 15/60, CCC 20/75).

## 5. Parameters (template)
- `ExportFolder` (text) — path to the export set.
- `ReportingCurrency` (from `dim_rate[currency]`).
- `FinancialYear` (default latest).

## 6. Save
File → Export → Power BI template (`.pbit`). Ship the `.pbit` alongside this repo;
opening it prompts for `ExportFolder` and loads the full model.

> The template is intentionally a blueprint: the model, measures, relationships,
> and page specs are all version-controlled here, so the `.pbit` is fully
> reproducible and stays in sync with the data contract.
