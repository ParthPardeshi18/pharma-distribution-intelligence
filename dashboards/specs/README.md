# Executive Dashboard Specifications (Power BI)

Detailed build specs for the stakeholder dashboards. Dashboards are built in
**Power BI Desktop** on the star-schema CSVs exported by the pipeline
(`data/warehouse/exports/{internal|shareable}/`). The model and visuals are
identical in both modes — only identity labels differ (real vs anonymised).

## Read first
- [powerbi_data_model.md](powerbi_data_model.md) — relationships, the reporting-
  currency pattern (`dim_rate`), and the DAX measures library.

## Stakeholder dashboards
1. [Owner / CEO](01_owner_ceo.md) — Business Health Index, trend, top risks/actions
2. [Finance](02_finance.md) — P&L, margins, working capital, cash
3. [Sales](03_sales.md) — performance, RFM, churn/win-back call lists, territory
4. [Inventory](04_inventory.md) — turnover, ageing/expiry, lifecycle, dead stock
5. [Procurement](05_procurement.md) — spend, supplier dependency, price changes
6. [Operations](06_operations.md) — throughput, route/territory coverage
7. [Working Capital](07_working_capital.md) — debtor/creditor/inventory days, CCC

## Build order
1. Run `python run_pipeline.py --mode internal` → builds warehouse + exports.
2. In Power BI, load the export folder, set relationships, mark `dim_date`.
3. Add the DAX measures, then build pages per spec.
4. For the portfolio version, point Power BI at the `shareable/` folder instead.

## Consistency
All KPI thresholds and definitions trace to `src/di/kpis.py`, so dashboard numbers
match the Decision-Intelligence and Strategic reports. Conditional-formatting bands
use the same anchors.
