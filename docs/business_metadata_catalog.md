# Business Metadata Catalog

> Generated 2026-06-26. The business-facing companion to the data dictionary: what each table means, its KPIs, how it links, and which ERP report it comes from.

## Tables at a glance

| Table | Role | Grain | Source ERP report |
|---|---|---|---|
| `dim_date` | dimension | one calendar day | generated |
| `dim_customer` | dimension | one customer | Masters/Customer_Master + resolved transaction names |
| `dim_supplier` | dimension | one supplier | Masters/Supplier_Master |
| `dim_product` | dimension | one product | Masters/Product_Master |
| `dim_company` | dimension | one manufacturer | Masters/Company_Master |
| `dim_salesman` | dimension | one salesman | Masters/Salesman_Master |
| `dim_territory` | dimension | one area (with its zone) | Masters/Area_List + Masters/Zone_List |
| `fact_sales` | fact | one sales bill (header) | Sales/Sales ⋈ Profit/Profit_AllBills on (financial_year, voucher_no) |
| `fact_purchases` | fact | one purchase bill (header) | Purchases/Purchase_Report |
| `fact_sales_product` | fact | one product per financial year | Sales/Sales_ProductWise |
| `fact_purchase_product` | fact | one product per financial year | Purchases/Purchase_ProductDetails |
| `fact_product_profit` | fact | one product per financial year | Profit/Profit_ProductWise |
| `fact_stock_snapshot` | fact | one product at period end | Stock/Stock_ProductWise |
| `fact_stock_movement` | fact | one company per financial year | Stock/Stock_InOutSummary |
| `fact_ar_outstanding` | fact | one open receivable bill | Outstanding/Outstanding_BillWise |
| `fact_ap_outstanding` | fact | one open payable bill | Outstanding/Payables_Ageing_BillWise |
| `fact_price_change` | fact | one price-change line | Purchases/PTR_Changed_Purchase |
| `meta_import_batch` | meta | one warehouse build run | pipeline |

## Headline business measures (KPIs)

| Measure | Table | Definition |
|---|---|---|
| `net_amount_inr` | `fact_sales` | Net sale (post return/scheme), INR |
| `profit_amount_inr` | `fact_sales` | Gross profit, INR |
| `net_amount_inr` | `fact_purchases` | Net purchase amount, INR |
| `quantity` | `fact_sales_product` | Units sold |
| `sale_amount_inr` | `fact_sales_product` | Sales value, INR |
| `purchase_amount_inr` | `fact_purchase_product` | Purchase value, INR |
| `profit_amount_inr` | `fact_product_profit` | Profit, INR |
| `value_inr` | `fact_stock_snapshot` | Stock value, INR |
| `balance_amount_inr` | `fact_ar_outstanding` | Outstanding balance, INR |
| `balance_amount_inr` | `fact_ap_outstanding` | Outstanding balance, INR |

## Relationships

| From | Foreign key | To dimension |
|---|---|---|
| `dim_customer` | `area_key` | `dim_territory` |
| `dim_product` | `company_key` | `dim_company` |
| `fact_sales` | `date_key` | `dim_date` |
| `fact_sales` | `customer_key` | `dim_customer` |
| `fact_purchases` | `date_key` | `dim_date` |
| `fact_purchases` | `supplier_key` | `dim_supplier` |
| `fact_sales_product` | `product_key` | `dim_product` |
| `fact_purchase_product` | `product_key` | `dim_product` |
| `fact_product_profit` | `product_key` | `dim_product` |
| `fact_stock_snapshot` | `product_key` | `dim_product` |
| `fact_stock_movement` | `company_key` | `dim_company` |
| `fact_ar_outstanding` | `customer_key` | `dim_customer` |
| `fact_ar_outstanding` | `bill_date_key` | `dim_date` |
| `fact_ap_outstanding` | `supplier_key` | `dim_supplier` |
| `fact_ap_outstanding` | `bill_date_key` | `dim_date` |
| `fact_price_change` | `product_key` | `dim_product` |
| `fact_price_change` | `date_key` | `dim_date` |

## Table definitions & business context

### `dim_date`

- **What it is:** Conformed date dimension spanning all transactional data.
- **Grain:** one calendar day
- **Source:** generated
- **Key business definitions:**
  - `date_key` — Join key for all dated facts

### `dim_customer`

- **What it is:** Customers, resolved from transaction names to master where possible.
- **Grain:** one customer
- **Source:** Masters/Customer_Master + resolved transaction names
- **Links:** dim_customer.area_key -> dim_territory.area_key
- **Key business definitions:**
  - `customer_code` — Customer identity; anonymised in shareable mode
  - `source_id` — Tier-1 key source for future auto-adoption
  - `match_tier` — Which resolution tier produced this customer
  - `match_confidence` — Entity-resolution confidence; 1.0 for exact/source_id

### `dim_supplier`

- **What it is:** Suppliers (100% exact-match to master).
- **Grain:** one supplier
- **Source:** Masters/Supplier_Master

### `dim_product`

- **What it is:** Products (100% exact-match to master).
- **Grain:** one product
- **Source:** Masters/Product_Master
- **Links:** dim_product.company_key -> dim_company.company_key

### `dim_company`

- **What it is:** Pharma manufacturers / principal companies.
- **Grain:** one manufacturer
- **Source:** Masters/Company_Master

### `dim_salesman`

- **What it is:** Sales representatives.
- **Grain:** one salesman
- **Source:** Masters/Salesman_Master

### `dim_territory`

- **What it is:** Geographic hierarchy: area within zone.
- **Grain:** one area (with its zone)
- **Source:** Masters/Area_List + Masters/Zone_List

### `fact_sales`

- **What it is:** Sales bills enriched with cost/profit from the profit register.
- **Grain:** one sales bill (header)
- **Source:** Sales/Sales ⋈ Profit/Profit_AllBills on (financial_year, voucher_no)
- **KPIs:** `net_amount_inr`, `profit_amount_inr`

### `fact_purchases`

- **What it is:** Purchase bills by supplier.
- **Grain:** one purchase bill (header)
- **Source:** Purchases/Purchase_Report
- **KPIs:** `net_amount_inr`

### `fact_sales_product`

- **What it is:** Annual product sales totals (no customer/bill — see data_model.md §2).
- **Grain:** one product per financial year
- **Source:** Sales/Sales_ProductWise
- **KPIs:** `quantity`, `sale_amount_inr`

### `fact_purchase_product`

- **What it is:** Annual product purchase details.
- **Grain:** one product per financial year
- **Source:** Purchases/Purchase_ProductDetails
- **KPIs:** `purchase_amount_inr`

### `fact_product_profit`

- **What it is:** Annual product profitability.
- **Grain:** one product per financial year
- **Source:** Profit/Profit_ProductWise
- **KPIs:** `profit_amount_inr`

### `fact_stock_snapshot`

- **What it is:** Closing stock valuation by product.
- **Grain:** one product at period end
- **Source:** Stock/Stock_ProductWise
- **KPIs:** `value_inr`

### `fact_stock_movement`

- **What it is:** Stock in/out movement summary by manufacturer.
- **Grain:** one company per financial year
- **Source:** Stock/Stock_InOutSummary

### `fact_ar_outstanding`

- **What it is:** Accounts receivable — open customer bills with ageing.
- **Grain:** one open receivable bill
- **Source:** Outstanding/Outstanding_BillWise
- **KPIs:** `balance_amount_inr`

### `fact_ap_outstanding`

- **What it is:** Accounts payable — open supplier bills with ageing buckets.
- **Grain:** one open payable bill
- **Source:** Outstanding/Payables_Ageing_BillWise
- **KPIs:** `balance_amount_inr`

### `fact_price_change`

- **What it is:** PTR/MRP/scheme price-change events on purchase vouchers.
- **Grain:** one price-change line
- **Source:** Purchases/PTR_Changed_Purchase

### `meta_import_batch`

- **What it is:** Audit log of every warehouse build (lineage anchor for import_batch_id).
- **Grain:** one warehouse build run
- **Source:** pipeline
