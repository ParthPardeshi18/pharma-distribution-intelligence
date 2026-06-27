# Power BI Data Model & DAX Measures

How to wire the exported star-schema CSVs into a Power BI model, switch reporting
currency, and define the measures the stakeholder dashboards use.

## 1. Loading the data

Exports are produced by `python -m src.powerbi.exports` (run by the pipeline) into:

```
data/warehouse/exports/internal/    # REAL identities — local only, never published
data/warehouse/exports/shareable/   # anonymised — safe for demos / portfolio
```

Load every `*.csv` from one folder (Get Data → Text/CSV, or Folder). Use **internal**
for running the firm, **shareable** for the portfolio version — the model and all
visuals are identical; only identity labels differ.

## 2. Relationships (star schema)

Set these relationships (single-direction, one-to-many from dimension to fact):

| Dimension (1) | Key | Fact (many) |
|---|---|---|
| `dim_date` | `date_key` | `fact_sales`, `fact_purchases`, `fact_price_change`; `bill_date_key` on `fact_ar_outstanding`, `fact_ap_outstanding` |
| `dim_customer` | `customer_key` | `fact_sales`, `fact_ar_outstanding` |
| `dim_supplier` | `supplier_key` | `fact_purchases`, `fact_ap_outstanding` |
| `dim_product` | `product_key` | `fact_sales_product`, `fact_purchase_product`, `fact_product_profit`, `fact_stock_snapshot`, `fact_price_change` |
| `dim_company` | `company_key` | `dim_product`, `fact_stock_movement` |
| `dim_territory` | `area_key` | `dim_customer` (and `fact_area_sales` if added) |

Mark `dim_date` as the official **Date table** (Modeling → Mark as Date Table → `date`).

> **Grain note (important for correct visuals):** `fact_sales`/`fact_purchases` are
> at BILL grain (no product); `fact_sales_product`/`fact_product_profit` are at
> PRODUCT × YEAR grain (no customer/date). Do **not** build visuals that cross
> these grains (e.g. customer × product) — the ERP has no line items. See
> `docs/data_model.md`.

## 3. Reporting currency (INR model, any display currency)

The model stays in INR (source of truth). `dim_rate.csv` holds
`financial_year, currency, units_per_inr`.

1. Load `dim_rate`. Create a slicer on `dim_rate[currency]` (single-select).
2. A measure converts at display time using the selected currency's rate:

```DAX
Selected Currency = SELECTEDVALUE ( dim_rate[currency], "INR" )

Rate (selected) =
VAR cur = [Selected Currency]
RETURN
    IF ( cur = "INR", 1,
        CALCULATE ( AVERAGE ( dim_rate[units_per_inr] ),
                    dim_rate[currency] = cur ) )

Revenue (reporting ccy) = [Revenue INR] * [Rate (selected)]
```

For FY-accurate conversion, relate `dim_rate[financial_year]` to a FY column and
use the per-year rate instead of the average.

## 4. Core DAX measures library

These mirror the KPI registry (`src/di/kpis.py`) so dashboard numbers match the
Decision-Intelligence reports. INR base measures:

```DAX
Revenue INR        = SUM ( fact_sales[net_amount_inr] )
Billed INR         = SUM ( fact_sales[billed_amount_inr] )
COGS INR           = SUM ( fact_sales[cost_amount_inr] )
Gross Profit INR   = SUM ( fact_sales[profit_amount_inr] )
Gross Margin %     = DIVIDE ( [Gross Profit INR], [Billed INR] )
Bills              = DISTINCTCOUNT ( fact_sales[voucher_no] )
Avg Bill Value     = DIVIDE ( [Revenue INR], [Bills] )

Purchases INR      = SUM ( fact_purchases[net_amount_inr] )
AR Balance INR     = SUM ( fact_ar_outstanding[balance_amount_inr] )
AP Balance INR     = SUM ( fact_ap_outstanding[balance_amount_inr] )
Inventory Value INR= SUM ( fact_stock_snapshot[value_inr] )

Revenue YoY %      =
VAR cur = [Revenue INR]
VAR prev = CALCULATE ( [Revenue INR], DATEADD ( dim_date[date], -1, YEAR ) )
RETURN DIVIDE ( cur - prev, prev )

Inventory Turnover = DIVIDE ( [COGS INR], [Inventory Value INR] )
Inventory Days     = DIVIDE ( 365, [Inventory Turnover] )
Debtor Days        = DIVIDE ( [AR Balance INR], [Revenue INR] ) * 365
Creditor Days      = DIVIDE ( [AP Balance INR], [Purchases INR] ) * 365
Cash Conversion Cycle = [Debtor Days] + [Inventory Days] - [Creditor Days]

Top 10 Customer Share % =
VAR top10 =
    TOPN ( 10, VALUES ( dim_customer[customer_key] ), [Revenue INR], DESC )
RETURN DIVIDE ( CALCULATE ( [Revenue INR], top10 ), [Revenue INR] )
```

## 5. Conditional formatting thresholds

Use the registry anchors so colour matches the health scores in the reports:
Gross Margin % green ≥ 6%, amber 3-6%, red < 3%; Inventory Turnover green ≥ 9×;
Debtor Days green ≤ 15, red ≥ 60; CCC green ≤ 20, red ≥ 75.

## 6. Refresh

Re-run `python run_pipeline.py --mode internal` to rebuild the warehouse and
re-export; Power BI → Refresh picks up the new CSVs. Schedule monthly (after the
ERP export) or on demand.
