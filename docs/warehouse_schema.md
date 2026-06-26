# Warehouse Star Schema (Phase 1 design)

Target: `data/warehouse/erp_warehouse.db` (SQLite via SQLAlchemy). Built in
Phase 2 from canonical adapter frames. **All money is stored in INR** (the single
source of truth); reporting-currency conversion happens only at the presentation
layer (see §6). Keys per `docs/entity_resolution_strategy.md`.

## 1. Design principles

- **Conformed dimensions** shared across facts (one `dim_customer`, one
  `dim_product`, one `dim_date`).
- **Facts modelled at their true grain** — we do **not** invent a bill×product
  grain that the data can't support (see data_model.md §2).
- **Surrogate keys** on every dimension; facts carry keys, not names.
- **Additive measures in INR**; ratios (margin %) stored for reference but
  recomputed from additive parts when aggregating.
- **Provenance** columns (`source_file`, `financial_year`, `load_ts`) on every
  table for traceability and reconciliation.

## 2. Dimensions

| Table | Grain | Key | Key attributes | Source |
|---|---|---|---|---|
| `dim_date` | one calendar day | `date_key` (YYYYMMDD) | date, financial_year, month, quarter, fy_month_no, is_month_end | generated over data span |
| `dim_customer` | one customer | `customer_key` | customer_code (anon), source_id, area_key, trade_type, discount_pct, match_tier | Customer_Master + resolved txn names |
| `dim_supplier` | one supplier | `supplier_key` | supplier_code, source_id, area | Supplier_Master |
| `dim_product` | one product | `product_key` | product_code, company_key, unit, tax_pct, dpco_flag, reorder_level | Product_Master |
| `dim_company` | one manufacturer | `company_key` | company_name(code), short_name | Company_Master |
| `dim_salesman` | one salesman | `salesman_key` | salesman_code | Salesman_Master |
| `dim_territory` | one area | `area_key` | area_name, zone_name | Area_List + Zone_List |

Identity attributes (`*_code`) are anonymous in shareable mode, real in internal
mode — same key either way, so analytics are identical (see dual-mode in README).

## 3. Fact tables (at true grain)

| Table | Grain | Keys | Measures (INR) | Source |
|---|---|---|---|---|
| `fact_sales` | one sales bill | date_key, customer_key, voucher_no | net_amount, billed_amount, cost_amount, profit_amount, profit_pct | `Sales` ⋈ `Profit_AllBills` on (fy, voucher_no) |
| `fact_purchases` | one purchase bill | date_key, supplier_key, voucher_no, bill_no | net_amount | `Purchase_Report` |
| `fact_sales_product` | product × FY | product_key, fy | quantity, scheme_qty, sale_amount, scheme_value | `Sales_ProductWise` |
| `fact_purchase_product` | product × FY | product_key, fy | quantity, scheme_qty, purchase_amount, purchase_rate, sale_rate, mrp | `Purchase_ProductDetails` |
| `fact_product_profit` | product × FY | product_key, fy | quantity, sale_billed_amount, cost_amount, profit_amount, profit_pct | `Profit_ProductWise` |
| `fact_stock_snapshot` | product (×batch) at period end | product_key, fy, batch_no | quantity, mrp, value, expiry_date | `Stock_ProductWise` / `ClosingStock` |
| `fact_stock_movement` | company × FY | company_key, fy | opening_value, stock_in_value, stock_out_value, closing_value | `Stock_InOutSummary` |
| `fact_ar_outstanding` | open receivable bill | customer_key, bill_date_key, bill_no | bill_amount, balance_amount, overdue_days, ageing buckets | `Outstanding_BillWise` + `Receivables_Ageing` |
| `fact_ap_outstanding` | open payable bill | supplier_key, bill_date_key, bill_no | bill_amount, balance_amount, overdue_days, ageing buckets | `Payables_Ageing_BillWise` |
| `fact_price_change` | price-change line | product_key, date_key, voucher_no | prev/new ptr, prev/new mrp, prev/new scheme_pct | `PTR_Changed_Purchase` |

**Aggregate reports** (`Area_Sales`, `Salesman_Sale`, `SupplierWise_Purchase`,
`Purchase_MonthWise`, `Profit_MonthlySummary`, `Stock_Company/CategoryWise`) are
stored as convenience marts and **reconciled against** the facts above (they are
the ERP's own totals — ideal validation checks).

**`P_and_L`** is parsed into a tidy `fin_pl_statement` table (account, side,
amount, fy) for the Finance dashboard — kept separate from facts.

## 4. Keys & integrity rules

- `(financial_year, voucher_no)` is the natural key for `fact_sales` /
  `fact_purchases`; de-duplicate on it during cleaning (a few repeats exist).
- Every fact key must resolve to a dimension; orphans are reported in
  `reports/data_validation.md`, never dropped.
- `dim_date` covers the full span (FY 22-23 → 25-26) with no gaps.

## 5. Reconciliation (Phase 2 gate)

For each fact, **raw total = warehouse total** must hold exactly:
- `fact_sales.net_amount` Σ == Σ of raw `Sales.Net` per FY.
- `fact_product_profit` Σ == `Profit_ProductWise` and == `Profit_MonthlySummary` Σ.
- `fact_ar_outstanding.balance_amount` Σ == `Outstanding_CustomerWise` Σ.
- Aggregate marts == facts (independent ERP cross-check).
Mismatches block Phase 2 sign-off.

## 6. Multi-currency layer (storage vs presentation)

- **Storage:** every money column is INR, suffixed `_inr` conceptually; the
  warehouse never stores converted values.
- **Presentation:** `src/currency.py` (Phase 2) converts at query/report time
  using date-aware rates in `data/reference/exchange_rates.csv`. Reports/dashboards
  take `--currency {INR|GBP|EUR|USD|…}`.
- **Power BI:** exports ship the INR fact plus a `dim_rate` table so the dashboard
  can switch reporting currency with a slicer — analytics stay currency-agnostic.

## 7. Physical build (Phase 2)

- SQLAlchemy Core; tables created from a typed schema module `src/warehouse/schema.py`.
- Loaders consume `CanonicalFrame`s from the adapter → resolve keys → upsert.
- Indices on every `*_key` and `date_key`. Star-schema CSV exports to
  `data/warehouse/exports/` (internal + shareable) for Power BI.
