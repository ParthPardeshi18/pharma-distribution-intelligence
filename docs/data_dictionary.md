# Data Dictionary

> Generated 2026-06-26 from `src/warehouse/schema.py`. Do not edit by hand — regenerate with `python -m src.warehouse.catalog`.

Every business table also carries the **standard lineage/audit/quality columns** listed once at the end.

## `dim_date` — dimension

*Conformed date dimension spanning all transactional data.*  
**Grain:** one calendar day  
**Source:** generated

| Column | Type | Key | Description |
|---|---|:--:|---|
| `date_key` | INTEGER | 🔑 | Surrogate key YYYYMMDD |
| `date` | DATE |  | Calendar date |
| `financial_year` | TEXT |  | Indian FY label (Apr–Mar), e.g. 25-26 |
| `year` | INTEGER |  | Calendar year |
| `month` | INTEGER |  | Calendar month 1–12 |
| `month_name` | TEXT |  | Month name |
| `quarter` | INTEGER |  | Calendar quarter 1–4 |
| `fy_month_no` | INTEGER |  | Month number within FY (Apr=1) |
| `is_month_end` | INTEGER |  | 1 if last day of month |

## `dim_customer` — dimension

*Customers, resolved from transaction names to master where possible.*  
**Grain:** one customer  
**Source:** Masters/Customer_Master + resolved transaction names

| Column | Type | Key | Description |
|---|---|:--:|---|
| `customer_key` | INTEGER | 🔑 | Surrogate key |
| `customer_code` | TEXT |  | Anonymous code (shareable) / name (internal) |
| `source_id` | TEXT |  | ERP stable id if exposed (else null) |
| `area_key` | INTEGER | FK | FK to dim_territory |
| `trade_type` | TEXT |  | Cash/Credit trade type |
| `discount_pct` | REAL |  | Default discount % |
| `match_tier` | TEXT |  | source_id | master_exact | master_fuzzy | unresolved |
| `match_confidence` | REAL |  | 0–1 confidence of name match |

## `dim_supplier` — dimension

*Suppliers (100% exact-match to master).*  
**Grain:** one supplier  
**Source:** Masters/Supplier_Master

| Column | Type | Key | Description |
|---|---|:--:|---|
| `supplier_key` | INTEGER | 🔑 | Surrogate key |
| `supplier_code` | TEXT |  | Anonymous code / name |
| `source_id` | TEXT |  | ERP stable id if exposed |
| `discount_pct` | REAL |  | Default discount % |

## `dim_product` — dimension

*Products (100% exact-match to master).*  
**Grain:** one product  
**Source:** Masters/Product_Master

| Column | Type | Key | Description |
|---|---|:--:|---|
| `product_key` | INTEGER | 🔑 | Surrogate key |
| `product_code` | TEXT |  | Product name/code (pharma brand — not PII) |
| `company_key` | INTEGER | FK | FK to dim_company |
| `unit` | TEXT |  | Pack/unit |
| `tax_pct` | REAL |  | GST % |
| `reorder_level` | REAL |  | Reorder level |

## `dim_company` — dimension

*Pharma manufacturers / principal companies.*  
**Grain:** one manufacturer  
**Source:** Masters/Company_Master

| Column | Type | Key | Description |
|---|---|:--:|---|
| `company_key` | INTEGER | 🔑 | Surrogate key |
| `company_code` | TEXT |  | Company name/code |
| `short_name` | TEXT |  | Short name |

## `dim_salesman` — dimension

*Sales representatives.*  
**Grain:** one salesman  
**Source:** Masters/Salesman_Master

| Column | Type | Key | Description |
|---|---|:--:|---|
| `salesman_key` | INTEGER | 🔑 | Surrogate key |
| `salesman_code` | TEXT |  | Anonymous code / name |

## `dim_territory` — dimension

*Geographic hierarchy: area within zone.*  
**Grain:** one area (with its zone)  
**Source:** Masters/Area_List + Masters/Zone_List

| Column | Type | Key | Description |
|---|---|:--:|---|
| `area_key` | INTEGER | 🔑 | Surrogate key |
| `area_name` | TEXT |  | Area / town |
| `zone_name` | TEXT |  | Zone |

## `fact_sales` — fact

*Sales bills enriched with cost/profit from the profit register.*  
**Grain:** one sales bill (header)  
**Source:** Sales/Sales ⋈ Profit/Profit_AllBills on (financial_year, voucher_no)

| Column | Type | Key | Description |
|---|---|:--:|---|
| `date_key` | INTEGER | FK | FK to dim_date |
| `customer_key` | INTEGER | FK | FK to dim_customer |
| `voucher_no` | TEXT | 🔑 | ERP voucher number |
| `financial_year` | TEXT | 🔑 | Financial year |
| `net_amount_inr` | REAL |  | Net sale (post return/scheme), INR *(INR)* |
| `billed_amount_inr` | REAL |  | Gross billed amount, INR *(INR)* |
| `cost_amount_inr` | REAL |  | Cost of goods, INR *(INR)* |
| `profit_amount_inr` | REAL |  | Gross profit, INR *(INR)* |
| `profit_pct` | REAL |  | Profit % (reference) |

## `fact_purchases` — fact

*Purchase bills by supplier.*  
**Grain:** one purchase bill (header)  
**Source:** Purchases/Purchase_Report

| Column | Type | Key | Description |
|---|---|:--:|---|
| `date_key` | INTEGER | FK | FK to dim_date |
| `supplier_key` | INTEGER | FK | FK to dim_supplier |
| `voucher_no` | TEXT | 🔑 | ERP voucher number |
| `bill_no` | TEXT |  | Supplier bill number |
| `financial_year` | TEXT | 🔑 | Financial year |
| `net_amount_inr` | REAL |  | Net purchase amount, INR *(INR)* |

## `fact_sales_product` — fact

*Annual product sales totals (no customer/bill — see data_model.md §2).*  
**Grain:** one product per financial year  
**Source:** Sales/Sales_ProductWise

| Column | Type | Key | Description |
|---|---|:--:|---|
| `product_key` | INTEGER | FK | FK to dim_product |
| `financial_year` | TEXT | 🔑 | Financial year |
| `quantity` | REAL |  | Units sold |
| `scheme_qty` | REAL |  | Scheme units |
| `sale_amount_inr` | REAL |  | Sales value, INR *(INR)* |
| `scheme_value_inr` | REAL |  | Scheme value, INR *(INR)* |

## `fact_purchase_product` — fact

*Annual product purchase details.*  
**Grain:** one product per financial year  
**Source:** Purchases/Purchase_ProductDetails

| Column | Type | Key | Description |
|---|---|:--:|---|
| `product_key` | INTEGER | FK | FK to dim_product |
| `financial_year` | TEXT | 🔑 | Financial year |
| `quantity` | REAL |  | Units purchased |
| `scheme_qty` | REAL |  | Scheme units |
| `purchase_amount_inr` | REAL |  | Purchase value, INR *(INR)* |
| `purchase_rate_inr` | REAL |  | Purchase rate, INR *(INR)* |
| `sale_rate_inr` | REAL |  | Sale rate, INR *(INR)* |
| `mrp_inr` | REAL |  | MRP, INR *(INR)* |

## `fact_product_profit` — fact

*Annual product profitability.*  
**Grain:** one product per financial year  
**Source:** Profit/Profit_ProductWise

| Column | Type | Key | Description |
|---|---|:--:|---|
| `product_key` | INTEGER | FK | FK to dim_product |
| `financial_year` | TEXT | 🔑 | Financial year |
| `quantity` | REAL |  | Units |
| `billed_amount_inr` | REAL |  | Billed amount, INR *(INR)* |
| `cost_amount_inr` | REAL |  | Cost, INR *(INR)* |
| `profit_amount_inr` | REAL |  | Profit, INR *(INR)* |
| `profit_pct` | REAL |  | Profit % |

## `fact_stock_snapshot` — fact

*Closing stock valuation by product.*  
**Grain:** one product at period end  
**Source:** Stock/Stock_ProductWise

| Column | Type | Key | Description |
|---|---|:--:|---|
| `product_key` | INTEGER | FK | FK to dim_product |
| `financial_year` | TEXT | 🔑 | Snapshot financial year |
| `quantity` | REAL |  | Units in stock |
| `rate_inr` | REAL |  | Valuation rate, INR *(INR)* |
| `value_inr` | REAL |  | Stock value, INR *(INR)* |

## `fact_stock_movement` — fact

*Stock in/out movement summary by manufacturer.*  
**Grain:** one company per financial year  
**Source:** Stock/Stock_InOutSummary

| Column | Type | Key | Description |
|---|---|:--:|---|
| `company_key` | INTEGER | FK | FK to dim_company |
| `financial_year` | TEXT | 🔑 | Financial year |
| `opening_value_inr` | REAL |  | Opening stock value, INR *(INR)* |
| `stock_in_value_inr` | REAL |  | Stock-in value, INR *(INR)* |
| `stock_out_value_inr` | REAL |  | Stock-out value, INR *(INR)* |
| `closing_value_inr` | REAL |  | Closing stock value, INR *(INR)* |

## `fact_ar_outstanding` — fact

*Accounts receivable — open customer bills with ageing.*  
**Grain:** one open receivable bill  
**Source:** Outstanding/Outstanding_BillWise

| Column | Type | Key | Description |
|---|---|:--:|---|
| `customer_key` | INTEGER | FK | FK to dim_customer |
| `bill_date_key` | INTEGER | FK | FK to dim_date (bill date) |
| `bill_no` | TEXT | 🔑 | Bill number |
| `financial_year` | TEXT | 🔑 | Financial year |
| `bill_amount_inr` | REAL |  | Bill amount, INR *(INR)* |
| `balance_amount_inr` | REAL |  | Outstanding balance, INR *(INR)* |
| `overdue_days` | REAL |  | Days overdue |

## `fact_ap_outstanding` — fact

*Accounts payable — open supplier bills with ageing buckets.*  
**Grain:** one open payable bill  
**Source:** Outstanding/Payables_Ageing_BillWise

| Column | Type | Key | Description |
|---|---|:--:|---|
| `supplier_key` | INTEGER | FK | FK to dim_supplier |
| `bill_date_key` | INTEGER | FK | FK to dim_date (bill date) |
| `bill_no` | TEXT | 🔑 | Bill number |
| `financial_year` | TEXT | 🔑 | Financial year |
| `bill_amount_inr` | REAL |  | Bill amount, INR *(INR)* |
| `balance_amount_inr` | REAL |  | Outstanding balance, INR *(INR)* |
| `overdue_days` | REAL |  | Days overdue |
| `ageing_0_30_inr` | REAL |  | Ageing 0–30 days, INR *(INR)* |
| `ageing_31_60_inr` | REAL |  | Ageing 31–60 days, INR *(INR)* |
| `ageing_61_90_inr` | REAL |  | Ageing 61–90 days, INR *(INR)* |
| `ageing_91_120_inr` | REAL |  | Ageing 91–120 days, INR *(INR)* |
| `ageing_120_plus_inr` | REAL |  | Ageing >120 days, INR *(INR)* |

## `fact_price_change` — fact

*PTR/MRP/scheme price-change events on purchase vouchers.*  
**Grain:** one price-change line  
**Source:** Purchases/PTR_Changed_Purchase

| Column | Type | Key | Description |
|---|---|:--:|---|
| `product_key` | INTEGER | FK | FK to dim_product |
| `date_key` | INTEGER | FK | FK to dim_date |
| `voucher_no` | TEXT |  | Voucher number |
| `financial_year` | TEXT | 🔑 | Financial year |
| `prev_ptr_inr` | REAL |  | Previous PTR, INR *(INR)* |
| `new_ptr_inr` | REAL |  | New PTR, INR *(INR)* |
| `prev_mrp_inr` | REAL |  | Previous MRP, INR *(INR)* |
| `new_mrp_inr` | REAL |  | New MRP, INR *(INR)* |

## `meta_import_batch` — meta

*Audit log of every warehouse build (lineage anchor for import_batch_id).*  
**Grain:** one warehouse build run  
**Source:** pipeline

| Column | Type | Key | Description |
|---|---|:--:|---|
| `import_batch_id` | INTEGER | 🔑 | Batch id |
| `started_at` | TIMESTAMP |  | Build start (UTC) |
| `finished_at` | TIMESTAMP |  | Build end (UTC) |
| `mode` | TEXT |  | internal | shareable |
| `reporting_currency` | TEXT |  | Currency requested at build time |
| `status` | TEXT |  | running | success | failed |
| `n_tables` | INTEGER |  | Tables written |
| `n_rows` | INTEGER |  | Total rows written |
| `git_commit` | TEXT |  | Code version, if available |
| `notes` | TEXT |  | Free-text notes |

## `fact_sales_line` — fact · *(future extension point — not built yet)*

*FUTURE: line-level sales (bill × product). Unlocks customer×product analysis. Build only when the ERP exports a sales register with line items. Keys off existing dims — no dimension/KPI/dashboard redesign.*  
**Grain:** one product line within a sales bill  
**Source:** FUTURE: Sales register with line items

| Column | Type | Key | Description |
|---|---|:--:|---|
| `date_key` | INTEGER | FK | FK to dim_date |
| `customer_key` | INTEGER | FK | FK to dim_customer |
| `product_key` | INTEGER | FK | FK to dim_product |
| `voucher_no` | TEXT | 🔑 | Voucher number |
| `financial_year` | TEXT | 🔑 | Financial year |
| `quantity` | REAL |  | Units |
| `line_amount_inr` | REAL |  | Line amount, INR *(INR)* |

## `fact_purchase_line` — fact · *(future extension point — not built yet)*

*FUTURE: line-level purchases (bill × product). Build only when the ERP exports a purchase register with line items. Backward-compatible.*  
**Grain:** one product line within a purchase bill  
**Source:** FUTURE: Purchase register with line items

| Column | Type | Key | Description |
|---|---|:--:|---|
| `date_key` | INTEGER | FK | FK to dim_date |
| `supplier_key` | INTEGER | FK | FK to dim_supplier |
| `product_key` | INTEGER | FK | FK to dim_product |
| `voucher_no` | TEXT | 🔑 | Voucher number |
| `financial_year` | TEXT | 🔑 | Financial year |
| `quantity` | REAL |  | Units |
| `line_amount_inr` | REAL |  | Line amount, INR *(INR)* |

## Standard columns (on every business table)

| Column | Type | Purpose |
|---|---|---|
| `src_report` | TEXT | Source ERP report key (e.g. 'Sales/Sales') |
| `src_year` | TEXT | Source financial year (e.g. '25-26') |
| `src_file` | TEXT | Source file path under data/raw/ |
| `import_batch_id` | INTEGER | FK to meta_import_batch |
| `processed_at` | TIMESTAMP | UTC timestamp this row was loaded |
| `record_quality` | TEXT | Quality status: ok | reconciled | unmatched_entity | duplicate_removed | imputed | quarantined |
| `quality_flags` | TEXT | Optional pipe-separated quality notes |
