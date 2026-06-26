# ERP Data Discovery Report

> **Firm:** Sukhakarta Distributors · pharmaceutical distribution.  
> All personal/commercial identifiers below are **MASKED**. No raw PII appears in this document.  
> Generated: 2026-06-26 · Source: `data/raw/` (read-only).

## Summary

| File | Size (KB) | Rows | Cols | Date range | Recover? |
|---|--:|--:|--:|---|:--:|
| `Masters/Area_List_24-25.xlsx` | 7.4 | 83 | 2 | — | no |
| `Masters/Area_List_25-26.xlsx` | 7.4 | 83 | 2 | — | no |
| `Masters/Company_Master.xlsx` | 43.4 | 867 | 8 | — | no |
| `Masters/Customer_Master.xlsx` | 142.8 | 2168 | 9 | — | no |
| `Masters/Product_Master.xlsx` | 1435.6 | 29799 | 12 | — | ⚠️ yes |
| `Masters/Salesman_Master.xlsx` | 56.8 | 1045 | 5 | — | no |
| `Masters/Supplier_Master.xlsx` | 18.5 | 233 | 6 | — | no |
| `Masters/Zone_List_24-25.xlsx` | 6.3 | 23 | 2 | — | no |
| `Masters/Zone_List_25-26.xlsx` | 7.4 | 83 | 2 | — | no |
| `Outstanding/Outstanding_BillWise_22-23.xlsx` | 6.8 | 12 | 8 | 2021-02-03 → 2023-03-29 (col: Bill dt) | no |
| `Outstanding/Outstanding_BillWise_23-24.xlsx` | 7.4 | 17 | 8 | 2023-04-08 → 2024-03-29 (col: Bill dt) | no |
| `Outstanding/Outstanding_BillWise_24-25.xlsx` | 8.0 | 27 | 8 | 2023-04-08 → 2025-03-05 (col: Bill dt) | no |
| `Outstanding/Outstanding_BillWise_25-26.xlsx` | 20.9 | 303 | 8 | 2023-04-08 → 2026-03-31 (col: Bill dt) | no |
| `Outstanding/Outstanding_CustomerWise_22-23.xlsx` | 8.2 | 27 | 7 | — | no |
| `Outstanding/Outstanding_CustomerWise_23-24.xlsx` | 9.4 | 47 | 7 | — | no |
| `Outstanding/Outstanding_CustomerWise_24-25.xlsx` | 11.8 | 87 | 7 | — | no |
| `Outstanding/Outstanding_CustomerWise_25-26.xlsx` | 14.3 | 125 | 7 | — | no |
| `Outstanding/Payables_Ageing_BillWise_22-23.xlsx` | 6.5 | 2 | 14 | — | no |
| `Outstanding/Payables_Ageing_BillWise_23-24.xlsx` | 12.0 | 83 | 14 | 2023-04-01 → 2024-03-26 (col: Bill date) | no |
| `Outstanding/Payables_Ageing_BillWise_24-25.xlsx` | 28.2 | 325 | 14 | 2023-04-15 → 2025-03-31 (col: Bill date) | no |
| `Outstanding/Payables_Ageing_BillWise_25-26.xlsx` | 41.3 | 518 | 14 | 2023-04-15 → 2026-03-31 (col: Bill date) | no |
| `Outstanding/Payables_Ageing_SupplierWise_22-23.xlsx` | 6.3 | 2 | 9 | — | no |
| `Outstanding/Payables_Ageing_SupplierWise_23-24.xlsx` | 6.8 | 10 | 9 | — | no |
| `Outstanding/Payables_Ageing_SupplierWise_24-25.xlsx` | 28.2 | 325 | 14 | 2023-04-15 → 2025-03-31 (col: Bill date) | no |
| `Outstanding/Payables_Ageing_SupplierWise_25-26.xlsx` | 9.1 | 49 | 9 | — | no |
| `Outstanding/Payables_SupplierWise_22-23.xlsx` | 6.4 | 4 | 6 | — | no |
| `Outstanding/Payables_SupplierWise_23-24.xlsx` | 6.8 | 10 | 9 | — | no |
| `Outstanding/Payables_SupplierWise_24-25.xlsx` | 22.8 | 325 | 8 | 2023-04-15 → 2025-03-31 (col: Bill dt) | no |
| `Outstanding/Payables_SupplierWise_25-26.xlsx` | 15.8 | 159 | 6 | — | no |
| `Outstanding/Receivables_Ageing_CustomerWise_22-23.xlsx` | 6.5 | 4 | 9 | — | no |
| `Outstanding/Receivables_Ageing_CustomerWise_23-24.xlsx` | 6.8 | 8 | 9 | — | no |
| `Outstanding/Receivables_Ageing_CustomerWise_24-25.xlsx` | 6.9 | 11 | 9 | — | no |
| `Outstanding/Receivables_Ageing_CustomerWise_25-26.xlsx` | 8.5 | 38 | 9 | — | no |
| `Profit/P_and_L_22-23.xlsx` | 11.0 | 129 | 6 | — | no |
| `Profit/P_and_L_23-24.xlsx` | 6.4 | 8 | 4 | — | no |
| `Profit/P_and_L_24-25.xlsx` | 6.4 | 8 | 4 | — | no |
| `Profit/P_and_L_25-26.xlsx` | 6.4 | 9 | 4 | — | no |
| `Profit/Profit_AllBills_22-23.xlsx` | 2412.9 | 39011 | 8 | 2022-04-01 → 2023-03-31 (col: Date) | no |
| `Profit/Profit_AllBills_23-24.xlsx` | 2421.7 | 40256 | 8 | 2023-04-01 → 2024-03-31 (col: Date) | no |
| `Profit/Profit_AllBills_24-25.xlsx` | 2503.2 | 41215 | 8 | 2024-04-01 → 2025-03-31 (col: Date) | no |
| `Profit/Profit_AllBills_25-26.xlsx` | 2602.0 | 42848 | 8 | 2025-04-01 → 2026-03-31 (col: Date) | no |
| `Profit/Profit_MonthlySummary_22-23.xlsx` | 7.0 | 14 | 5 | — | no |
| `Profit/Profit_MonthlySummary_23-24.xlsx` | 7.0 | 14 | 5 | — | no |
| `Profit/Profit_MonthlySummary_24-25.xlsx` | 7.0 | 14 | 5 | — | no |
| `Profit/Profit_MonthlySummary_25-26.xlsx` | 6.9 | 14 | 5 | — | no |
| `Profit/Profit_ProductWise_22-23.xlsx` | 530.8 | 7501 | 8 | — | no |
| `Profit/Profit_ProductWise_23-24.xlsx` | 486.1 | 7082 | 8 | — | no |
| `Profit/Profit_ProductWise_24-25.xlsx` | 280.6 | 4245 | 8 | — | no |
| `Profit/Profit_ProductWise_25-26.xlsx` | 483.5 | 7067 | 8 | — | no |
| `Purchases/PTR_Changed_Purchase_22-23.xlsx` | 612.8 | 10868 | 11 | 2022-04-01 → 2023-03-29 (col: Date) | no |
| `Purchases/PTR_Changed_Purchase_23-24.xlsx` | 369.6 | 6534 | 11 | 2023-04-03 → 2024-03-28 (col: Date) | no |
| `Purchases/PTR_Changed_Purchase_24-25.xlsx` | 298.2 | 5236 | 11 | 2024-04-01 → 2025-03-29 (col: Date) | no |
| `Purchases/PTR_Changed_Purchase_25-26.xlsx` | 432.0 | 7687 | 11 | 2025-04-01 → 2026-03-31 (col: Date) | no |
| `Purchases/Purchase_MonthWise_22-23.xlsx` | 6.3 | 14 | 2 | — | no |
| `Purchases/Purchase_MonthWise_23-24.xlsx` | 6.3 | 14 | 2 | — | no |
| `Purchases/Purchase_MonthWise_24-25.xlsx` | 6.3 | 14 | 2 | — | no |
| `Purchases/Purchase_MonthWise_25-26.xlsx` | 6.2 | 14 | 2 | — | no |
| `Purchases/Purchase_ProductDetails_22-23.xlsx` | 2568.6 | 46337 | 11 | — | no |
| `Purchases/Purchase_ProductDetails_23-24.xlsx` | 2109.8 | 37675 | 11 | — | no |
| `Purchases/Purchase_ProductDetails_24-25.xlsx` | 2153.2 | 38447 | 11 | — | no |
| `Purchases/Purchase_ProductDetails_25-26.xlsx` | 2279.0 | 40553 | 11 | — | no |
| `Purchases/Purchase_Report_22-23.xlsx` | 123.3 | 3009 | 6 | 2022-04-01 → 2023-03-31 (col: Date) | no |
| `Purchases/Purchase_Report_23-24.xlsx` | 110.1 | 2679 | 6 | 2023-04-01 → 2024-03-28 (col: Date) | no |
| `Purchases/Purchase_Report_24-25.xlsx` | 115.3 | 2841 | 6 | 2024-04-01 → 2025-03-29 (col: Date) | no |
| `Purchases/Purchase_Report_25-26.xlsx` | 116.5 | 2886 | 6 | 2025-04-01 → 2026-03-31 (col: Date) | no |
| `Purchases/SupplierWise_Purchase_22-23.xlsx` | 8.5 | 74 | 3 | — | no |
| `Purchases/SupplierWise_Purchase_23-24.xlsx` | 8.5 | 76 | 3 | — | no |
| `Purchases/SupplierWise_Purchase_24-25.xlsx` | 8.1 | 65 | 3 | — | no |
| `Purchases/SupplierWise_Purchase_25-26.xlsx` | 8.2 | 66 | 3 | — | no |
| `Sales/Area_Sales_22-23.xlsx` | 7.4 | 38 | 4 | — | no |
| `Sales/Area_Sales_23-24.xlsx` | 7.4 | 37 | 4 | — | no |
| `Sales/Area_Sales_24-25.xlsx` | 7.3 | 34 | 4 | — | no |
| `Sales/Area_Sales_25-26.xlsx` | 7.3 | 34 | 4 | — | no |
| `Sales/Customer_Sales_22-23.xlsx` | 1196.0 | 39683 | 6 | 2022-04-01 → 2023-03-31 (col: Vch date) | no |
| `Sales/Customer_Sales_23-24.xlsx` | 1235.9 | 40939 | 6 | 2023-04-01 → 2024-03-31 (col: Vch date) | no |
| `Sales/Customer_Sales_24-25.xlsx` | 1333.4 | 43412 | 6 | 2024-04-01 → 2025-03-31 (col: Vch date) | no |
| `Sales/Customer_Sales_25-26.xlsx` | 1374.3 | 44807 | 6 | 2025-04-01 → 2026-03-31 (col: Vch date) | no |
| `Sales/Sales_22-23.xlsx` | 1120.9 | 39011 | 5 | 2022-04-01 → 2023-03-31 (col: Date) | no |
| `Sales/Sales_23-24.xlsx` | 1160.8 | 40256 | 5 | 2023-04-01 → 2024-03-31 (col: Date) | no |
| `Sales/Sales_24-25.xlsx` | 1212.4 | 41215 | 5 | 2024-04-01 → 2025-03-31 (col: Date) | no |
| `Sales/Sales_25-26.xlsx` | 1258.4 | 42848 | 5 | 2025-04-01 → 2026-03-31 (col: Date) | no |
| `Sales/Sales_ProductWise_22-23.xlsx` | 374.2 | 7501 | 9 | — | no |
| `Sales/Sales_ProductWise_23-24.xlsx` | 353.2 | 7082 | 9 | — | no |
| `Sales/Sales_ProductWise_24-25.xlsx` | 341.4 | 6804 | 9 | — | no |
| `Sales/Sales_ProductWise_25-26.xlsx` | 354.3 | 7067 | 9 | — | no |
| `Sales/Salesman_Sale_22-23.xlsx` | 12.7 | 112 | 8 | — | no |
| `Sales/Salesman_Sale_23-24.xlsx` | 12.9 | 118 | 8 | — | no |
| `Sales/Salesman_Sale_24-25.xlsx` | 12.7 | 115 | 8 | — | no |
| `Sales/Salesman_Sale_25-26.xlsx` | 12.0 | 98 | 8 | — | no |
| `Stock/ClosingStock_22-23.xlsx` | 11.5 | 47 | 22 | 2007-07-20 → 2023-01-18 (col: StkIn dt) | no |
| `Stock/ClosingStock_23-24.xlsx` | 11.7 | 94 | 11 | 2026-09-01 → 2037-11-30 (col: ExpDt) | no |
| `Stock/ClosingStock_24-25.xlsx` | 57.1 | 924 | 11 | 2026-09-01 → 2037-11-30 (col: ExpDt) | no |
| `Stock/ClosingStock_25-26.xlsx` | 547.8 | 10312 | 11 | 2026-09-01 → 2045-02-28 (col: ExpDt) | no |
| `Stock/Stock_CategoryWise_22-23.xlsx` | 6.2 | 5 | 3 | — | no |
| `Stock/Stock_CategoryWise_23-24.xlsx` | 6.2 | 5 | 3 | — | no |
| `Stock/Stock_CategoryWise_24-25.xlsx` | 6.2 | 5 | 3 | — | no |
| `Stock/Stock_CategoryWise_25-26.xlsx` | 6.2 | 5 | 3 | — | no |
| `Stock/Stock_CompanyWise_22-23.xlsx` | 22.9 | 529 | 3 | — | no |
| `Stock/Stock_CompanyWise_23-24.xlsx` | 22.4 | 524 | 3 | — | no |
| `Stock/Stock_CompanyWise_24-25.xlsx` | 22.0 | 511 | 3 | — | no |
| `Stock/Stock_CompanyWise_25-26.xlsx` | 22.0 | 510 | 3 | — | no |
| `Stock/Stock_InOutSummary_22-23.xlsx` | 35.9 | 829 | 5 | — | no |
| `Stock/Stock_InOutSummary_23-24.xlsx` | 35.6 | 827 | 5 | — | no |
| `Stock/Stock_InOutSummary_24-25.xlsx` | 35.6 | 827 | 5 | — | no |
| `Stock/Stock_InOutSummary_25-26.xlsx` | 35.6 | 827 | 5 | — | no |
| `Stock/Stock_ProductWise_22-23.xlsx` | 339.0 | 6680 | 7 | — | no |
| `Stock/Stock_ProductWise_23-24.xlsx` | 308.8 | 6082 | 7 | — | no |
| `Stock/Stock_ProductWise_24-25.xlsx` | 320.5 | 6296 | 7 | — | no |
| `Stock/Stock_ProductWise_25-26.xlsx` | 314.5 | 6145 | 7 | — | no |

**109 files scanned · 1 required XML recovery · 0 unreadable.**

## File details

### `Masters/Area_List_24-25.xlsx`

- Size: 7.4 KB · Sheets: Report
- Rows: 83 · Columns (2): `Area name`, `Zone name`
- Date range: —

Masked sample (first 3 rows):

| Area name   | Zone name   |
|:------------|:------------|
| Name_1***   | Name_D***   |
| Name_3***   | Name_D***   |
| Name_A***   | Name_D***   |

### `Masters/Area_List_25-26.xlsx`

- Size: 7.4 KB · Sheets: Report
- Rows: 83 · Columns (2): `Area name`, `Zone name`
- Date range: —

Masked sample (first 3 rows):

| Area name   | Zone name   |
|:------------|:------------|
| Name_1***   | Name_D***   |
| Name_3***   | Name_D***   |
| Name_A***   | Name_D***   |

### `Masters/Company_Master.xlsx`

- Size: 43.4 KB · Sheets: Report
- Rows: 867 · Columns (8): `Company name`, `Short`, `Mobile no.`, `Email ids`, `OR`, `OP`, `CL`, `SS`
- Date range: —

Masked sample (first 3 rows):

| Company name    | Short   | Mobile no.   | Email ids   |   OR |   OP | CL   | SS   |
|:----------------|:--------|:-------------|:------------|-----:|-----:|:-----|:-----|
| ***********LTH) | AABBO   |              |             |  1.5 |    2 | N    | N    |
| **********VID)  | AALBE   |              |             |  1.5 |    2 | N    | N    |
| ***KEM)         | ALCHE   |              |             |  1.5 |    2 | N    | N    |

### `Masters/Customer_Master.xlsx`

- Size: 142.8 KB · Sheets: Report
- Rows: 2168 · Columns (9): `Customer name`, `Address`, `Alias`, `TT`, `Disc%`, `SP`, `Mobile`, `Telephone`, `IE code`
- Date range: —

Masked sample (first 3 rows):

| Customer name   | Address   | Alias   | TT          |   Disc% |   SP | Mobile               | Telephone                  | IE code     |
|:----------------|:----------|:--------|:------------|--------:|-----:|:---------------------|:---------------------------|:------------|
| Name_****       | SHIRUR    |         | Cash/Credit |     3.5 |    8 | 94XXXXXXXXXXXXXXXX09 | 22XXXXXXXXXXXXXXXXXXXXXX62 | *******R106 |
| Name_****       | SHIRUR    |         | Cash/Credit |     3.5 |    8 |                      |                            | *******A957 |
| Name_****       | SHIRUR    |         | Credit      |   nan   |    8 | 92XXXXXXXXXXXXXXXX06 | 92XXXXXX06                 | ******MA86  |

### `Masters/Product_Master.xlsx`

- Size: 1435.6 KB · Sheets: (recovered)
- ⚠️ **Malformed XML** (invalid UTF-8 bytes from ERP export) — read via sanitizing recovery reader.
- Rows: 29799 · Columns (12): `Product name`, `Unit`, `Com`, `Alias`, `Shelf`, `Re-ord`, `Refill`, `DPCO`, `CL`, `SS`, `Tax%`, `Disc%`
- Date range: —

Masked sample (first 3 rows):

| Product name   | Unit   | Com   |   Alias |   Shelf |   Re-ord |   Refill | DPCO   | CL   | SS   |   Tax% |   Disc% |
|:---------------|:-------|:------|--------:|--------:|---------:|---------:|:-------|:-----|:-----|-------:|--------:|
| Name_A***      | 10 TAB | MICRO |         |     nan |      nan |      nan | N      | N    | N    |      5 |     nan |
| Name_M***      | 10TAB  | MEDCE |     694 |     nan |      nan |      nan | N      | N    | N    |      5 |     nan |
| Name_(***      | 1      | MANKI |         |     nan |      nan |      nan | N      | N    | N    |    nan |     nan |

### `Masters/Salesman_Master.xlsx`

- Size: 56.8 KB · Sheets: Report
- Rows: 1045 · Columns (5): `Salesman name`, `Address`, `Mobile no.`, `Email ids`, `AlwInSl`
- Date range: —
- Key totals: `Salesman name` = 3.00

Masked sample (first 3 rows):

| Salesman name   | Address               | Mobile no.   | Email ids   | AlwInSl   |
|:----------------|:----------------------|:-------------|:------------|:----------|
| Name_D***       |                       |              |             | Y         |
| Name_****       | 0                     | X            |             | Y         |
| Name_****       | KULDIP,k***@gmail.com | 95XXXXXX14   |             | Y         |

### `Masters/Supplier_Master.xlsx`

- Size: 18.5 KB · Sheets: Report
- Rows: 233 · Columns (6): `Supplier name`, `Short address`, `Alias`, `Disc%`, `Mobile`, `Telephone`
- Date range: —

Masked sample (first 3 rows):

| Supplier name   | Short address   | Alias            |   Disc% | Mobile     | Telephone            |
|:----------------|:----------------|:-----------------|--------:|:-----------|:---------------------|
| Name_****       | BHIVANDI        |                  |     nan | 99XXXXXX55 | 02XXXXXXX24          |
| Name_A***       | WADAKI-PUNE     | ************2868 |     nan | 98XXXXXX08 | 89XXXXXXXXXXXXXXXX67 |
| Name_A***       | BHIWANDI        | ****RGAN         |     nan |            |                      |

### `Masters/Zone_List_24-25.xlsx`

- Size: 6.3 KB · Sheets: Report
- Rows: 23 · Columns (2): `Zone name`, `State name`
- Date range: —

Masked sample (first 3 rows):

| Zone name   | State name   |
|:------------|:-------------|
| Name_A***   | Name_M***    |
| Name_C***   | Name_M***    |
| Name_D***   | Name_M***    |

### `Masters/Zone_List_25-26.xlsx`

- Size: 7.4 KB · Sheets: Report
- Rows: 83 · Columns (2): `Area name`, `Zone name`
- Date range: —

Masked sample (first 3 rows):

| Area name   | Zone name   |
|:------------|:------------|
| Name_1***   | Name_D***   |
| Name_3***   | Name_D***   |
| Name_A***   | Name_D***   |

### `Outstanding/Outstanding_BillWise_22-23.xlsx`

- Size: 6.8 KB · Sheets: Report
- Rows: 12 · Columns (8): `Customer name`, `Address`, `Bill dt`, `Bill no`, `Bill amt`, `Bal amt`, `Due dt`, `O/d`
- Date range: 2021-02-03 → 2023-03-29 (col: Bill dt)
- Key totals: `Bill amt` = 117,807.00 · `Bal amt` = 108,807.00

Masked sample (first 3 rows):

| Customer name   | Address            | Bill dt             | Bill no   |   Bill amt |   Bal amt | Due dt              |   O/d |
|:----------------|:-------------------|:--------------------|:----------|-----------:|----------:|:--------------------|------:|
| Name_****       | RANJANGAON GANPATI | ***************0:00 | ***6319   |       5700 |      5700 | 2023-03-29 00:00:00 |  1185 |
| Name_M***       |                    |                     |           |       5700 |      5700 | nan                 |   nan |
| Name_S***       | SHIKRAPUR          | ***************0:00 | ***7318   |       4346 |      1346 | 2021-02-03 00:00:00 |  1969 |

### `Outstanding/Outstanding_BillWise_23-24.xlsx`

- Size: 7.4 KB · Sheets: Report
- Rows: 17 · Columns (8): `Customer name`, `Address`, `Bill dt`, `Bill no`, `Bill amt`, `Bal amt`, `Due dt`, `O/d`
- Date range: 2023-04-08 → 2024-03-29 (col: Bill dt)
- Key totals: `Bill amt` = 2,679,750.00 · `Bal amt` = 221,677.20

Masked sample (first 3 rows):

| Customer name   | Address      | Bill dt             | Bill no   | Bill amt   |   Bal amt | Due dt              |   O/d |
|:----------------|:-------------|:--------------------|:----------|:-----------|----------:|:--------------------|------:|
| Name_D***       | WARJE (PUNE) | ***************0:00 | ****5836  | 971        |       971 | 2024-03-29 00:00:00 |   803 |
| Name_M***       |              |                     |           | 971        |       971 | nan                 |   nan |
| Name_M***       | CHINCHAWAD   | ***************0:00 | **/122    | **3508     |        22 | 2023-04-09 00:00:00 |  1158 |

### `Outstanding/Outstanding_BillWise_24-25.xlsx`

- Size: 8.0 KB · Sheets: Report
- Rows: 27 · Columns (8): `Customer name`, `Address`, `Bill dt`, `Bill no`, `Bill amt`, `Bal amt`, `Due dt`, `O/d`
- Date range: 2023-04-08 → 2025-03-05 (col: Bill dt)
- Key totals: `Bill amt` = 822,879.00 · `Bal amt` = 303,094.20

Masked sample (first 3 rows):

| Customer name   | Address       | Bill dt             | Bill no   |   Bill amt |   Bal amt | Due dt              |   O/d |
|:----------------|:--------------|:--------------------|:----------|-----------:|----------:|:--------------------|------:|
| Name_D***       | KAWATHE YEMAI | ***************0:00 | ***4933   |       1046 |      1046 | 2024-12-04 00:00:00 |   553 |
| Name_M***       |               |                     |           |       1046 |      1046 | nan                 |   nan |
| Name_M***       | KOLGAON       | ***************0:00 | ***8465   |       7509 |      5627 | 2024-07-30 00:00:00 |   680 |

### `Outstanding/Outstanding_BillWise_25-26.xlsx`

- Size: 20.9 KB · Sheets: Report
- Rows: 303 · Columns (8): `Customer name`, `Address`, `Bill dt`, `Bill no`, `Bill amt`, `Bal amt`, `Due dt`, `O/d`
- Date range: 2023-04-08 → 2026-03-31 (col: Bill dt)
- Key totals: `Bill amt` = 5,324,781.00 · `Bal amt` = 4,622,869.20

Masked sample (first 3 rows):

| Customer name   | Address   | Bill dt             | Bill no   |   Bill amt |   Bal amt | Due dt              |   O/d |
|:----------------|:----------|:--------------------|:----------|-----------:|----------:|:--------------------|------:|
| Name_B***       | SHRIGONGA | ***************0:00 | ****6405  |       1509 |      1509 | 2026-03-25 00:00:00 |    77 |
| Name_M***       |           | ***************0:00 | ****6569  |       3868 |      3868 | 2026-03-28 00:00:00 |    74 |
|                 |           | ***************0:00 | ****6573  |       5548 |      5548 | 2026-03-28 00:00:00 |    74 |

### `Outstanding/Outstanding_CustomerWise_22-23.xlsx`

- Size: 8.2 KB · Sheets: Report
- Rows: 27 · Columns (7): `Party name`, `Address`, `Area`, `Tel/Mobile`, `Tot bill amt`, `Tot bal amt`, `Tot due amt`
- Date range: —
- Key totals: `Tot bill amt` = 1,052,933.36 · `Tot bal amt` = 932,323.06 · `Tot due amt` = 932,323.06

Masked sample (first 3 rows):

| Party name   | Address            | Area                        | Tel/Mobile                                    | Tot bill amt   |   Tot bal amt |   Tot due amt |
|:-------------|:-------------------|:----------------------------|:----------------------------------------------|:---------------|--------------:|--------------:|
| Name_****    | RANJANGAON GANPATI | WED-4-RANJANGAON RANJANGAON | 90XXXXXXXXXXXXXXXX67                          | 5700           |       5700    |       5700    |
| Name_A***    | NASHIK             | MON UNDERCUTTER PARTIES     | 02XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX20 | **9.25         |        349.25 |        349.25 |
| Name_A***    | URULI DEVACHI      | URULIKANCHAN                | 02XXXXXXX91                                   | 604            |        431    |        431    |

### `Outstanding/Outstanding_CustomerWise_23-24.xlsx`

- Size: 9.4 KB · Sheets: Report
- Rows: 47 · Columns (7): `Party name`, `Address`, `Area`, `Tel/Mobile`, `Tot bill amt`, `Tot bal amt`, `Tot due amt`
- Date range: —
- Key totals: `Tot bill amt` = 3,948,437.36 · `Tot bal amt` = 1,774,907.86 · `Tot due amt` = 1,774,907.86

Masked sample (first 3 rows):

| Party name   | Address   | Area                    | Tel/Mobile                                    | Tot bill amt   |   Tot bal amt |   Tot due amt |
|:-------------|:----------|:------------------------|:----------------------------------------------|:---------------|--------------:|--------------:|
| Name_****    | BHIVANDI  | BHIWANDI                | 02XXXXXXXXXXXXXXXXX55                         | 85             |         85    |         85    |
| Name_A***    | NASHIK    | MON UNDERCUTTER PARTIES | 02XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX20 | **9.25         |        349.25 |        349.25 |
| Name_A***    | WADKI     | PUNE                    | 84XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX03      | 411            |        411    |        411    |

### `Outstanding/Outstanding_CustomerWise_24-25.xlsx`

- Size: 11.8 KB · Sheets: Report
- Rows: 87 · Columns (7): `Party name`, `Address`, `Area`, `Tel/Mobile`, `Tot bill amt`, `Tot bal amt`, `Tot due amt`
- Date range: —
- Key totals: `Tot bill amt` = 9,325,667.06 · `Tot bal amt` = 8,955,031.86 · `Tot due amt` = 8,955,031.86

Masked sample (first 3 rows):

| Party name   | Address     | Area                    | Tel/Mobile                                    | Tot bill amt   |   Tot bal amt |   Tot due amt |
|:-------------|:------------|:------------------------|:----------------------------------------------|:---------------|--------------:|--------------:|
| Name_****    | BHIVANDI    | BHIWANDI                | 02XXXXXXXXXXXXXXXXX55                         | 85             |         85    |         85    |
| Name_A***    | WADAKI-PUNE | PUNE                    | 89XXXXXXXXXXXXXXXXXXXXXXXXXX08                | 324            |        324    |        324    |
| Name_A***    | NASHIK      | MON UNDERCUTTER PARTIES | 02XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX20 | **9.25         |        349.25 |        349.25 |

### `Outstanding/Outstanding_CustomerWise_25-26.xlsx`

- Size: 14.3 KB · Sheets: Report
- Rows: 125 · Columns (7): `Party name`, `Address`, `Area`, `Tel/Mobile`, `Tot bill amt`, `Tot bal amt`, `Tot due amt`
- Date range: —
- Key totals: `Tot bill amt` = 13,771,529.06 · `Tot bal amt` = 13,279,475.86 · `Tot due amt` = 13,279,475.86

Masked sample (first 3 rows):

| Party name   | Address     | Area                    | Tel/Mobile                                    | Tot bill amt   |   Tot bal amt |   Tot due amt |
|:-------------|:------------|:------------------------|:----------------------------------------------|:---------------|--------------:|--------------:|
| Name_****    | BHIVANDI    | BHIWANDI                | 02XXXXXXXXXXXXXXXXX55                         | 85             |         85    |         85    |
| Name_A***    | WADAKI-PUNE | PUNE                    | 89XXXXXXXXXXXXXXXXXXXXXXXXXX08                | 324            |        324    |        324    |
| Name_A***    | NASHIK      | MON UNDERCUTTER PARTIES | 02XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX20 | **9.25         |        349.25 |        349.25 |

### `Outstanding/Payables_Ageing_BillWise_22-23.xlsx`

- Size: 6.5 KB · Sheets: Report
- Rows: 2 · Columns (14): `Supplier name`, `Address`, `Bill date`, `Vch no`, `Bill no`, `Bill amt`, `Bal amt`, `Due dt`, `O/d`, `OD days upto 30`, `OD days upto 60`, `OD days upto 90`, `OD days upto 120`, `OD days > 120`
- Date range: —
- Key totals: `Bill amt` = 0.00 · `Bal amt` = 0.00

Masked sample (first 3 rows):

| Supplier name   | Address   | Bill date   |   Vch no | Bill no   |   Bill amt |   Bal amt |   Due dt |   O/d |   OD days upto 30 |   OD days upto 60 |   OD days upto 90 |   OD days upto 120 |   OD days > 120 |
|:----------------|:----------|:------------|---------:|:----------|-----------:|----------:|---------:|------:|------------------:|------------------:|------------------:|-------------------:|----------------:|
|                 |           |             |      nan | ***als:   |          0 |         0 |      nan |   nan |                 0 |                 0 |                 0 |                  0 |               0 |
| Name_G***       |           |             |      nan |           |            |       nan |      nan |   nan |               nan |               nan |               nan |                nan |             nan |

### `Outstanding/Payables_Ageing_BillWise_23-24.xlsx`

- Size: 12.0 KB · Sheets: Report
- Rows: 83 · Columns (14): `Supplier name`, `Address`, `Bill date`, `Vch no`, `Bill no`, `Bill amt`, `Bal amt`, `Due dt`, `O/d`, `OD days upto 30`, `OD days upto 60`, `OD days upto 90`, `OD days upto 120`, `OD days > 120`
- Date range: 2023-04-01 → 2024-03-26 (col: Bill date)
- Key totals: `Bill amt` = 8,558,388.00 · `Bal amt` = 8,318,444.00

Masked sample (first 3 rows):

| Supplier name   | Address      | Bill date           | Vch no   | Bill no        | Bill amt   |   Bal amt | Due dt              |   O/d |   OD days upto 30 |   OD days upto 60 |   OD days upto 90 |   OD days upto 120 |   OD days > 120 |
|:----------------|:-------------|:--------------------|:---------|:---------------|:-----------|----------:|:--------------------|------:|------------------:|------------------:|------------------:|-------------------:|----------------:|
| Name_M***       | URALIDEVACHI | ***************0:00 | PURC/24  | ***********DKM | 4533       |      2626 | 2023-04-01 00:00:00 |  1166 |               nan |               nan |               nan |                nan |            2626 |
| Name_H***       | MALEGAON     | ***************0:00 | PURC/127 | *****1760      | *7637      |     27637 | 2023-04-13 00:00:00 |  1154 |               nan |               nan |               nan |                nan |           27637 |
| Name_S***       | MANCHAR      | ***************0:00 | PURC/94  | 8807           | **9972     |    339972 | 2023-04-15 00:00:00 |  1152 |               nan |               nan |               nan |                nan |          339972 |

### `Outstanding/Payables_Ageing_BillWise_24-25.xlsx`

- Size: 28.2 KB · Sheets: Report
- Rows: 325 · Columns (14): `Supplier name`, `Address`, `Bill date`, `Vch no`, `Bill no`, `Bill amt`, `Bal amt`, `Due dt`, `O/d`, `OD days upto 30`, `OD days upto 60`, `OD days upto 90`, `OD days upto 120`, `OD days > 120`
- Date range: 2023-04-15 → 2025-03-31 (col: Bill date)
- Key totals: `Bill amt` = 29,279,956.00 · `Bal amt` = 12,294,200.00

Masked sample (first 3 rows):

| Supplier name   | Address   | Bill date           | Vch no   |   Bill no | Bill amt   |   Bal amt | Due dt              |   O/d |   OD days upto 30 |   OD days upto 60 |   OD days upto 90 |   OD days upto 120 |   OD days > 120 |
|:----------------|:----------|:--------------------|:---------|----------:|:-----------|----------:|:--------------------|------:|------------------:|------------------:|------------------:|-------------------:|----------------:|
| Name_S***       | MANCHAR   | ***************0:00 | PURC/94  |      8807 | **9972     |    339972 | 2023-04-15 00:00:00 |  1152 |               nan |               nan |               nan |                nan |          339972 |
| Name_S***       | MANCHAR   | ***************0:00 | PURC/95  |      8808 | *6261      |     16261 | 2023-04-15 00:00:00 |  1152 |               nan |               nan |               nan |                nan |           16261 |
| Name_S***       | MANCHAR   | ***************0:00 | PURC/106 |      9389 | *4381      |     74381 | 2023-04-17 00:00:00 |  1150 |               nan |               nan |               nan |                nan |           74381 |

### `Outstanding/Payables_Ageing_BillWise_25-26.xlsx`

- Size: 41.3 KB · Sheets: Report
- Rows: 518 · Columns (14): `Supplier name`, `Address`, `Bill date`, `Vch no`, `Bill no`, `Bill amt`, `Bal amt`, `Due dt`, `O/d`, `OD days upto 30`, `OD days upto 60`, `OD days upto 90`, `OD days upto 120`, `OD days > 120`
- Date range: 2023-04-15 → 2026-03-31 (col: Bill date)
- Key totals: `Bill amt` = 45,920,318.00 · `Bal amt` = 18,853,060.00

Masked sample (first 3 rows):

| Supplier name   | Address   | Bill date           | Vch no   |   Bill no | Bill amt   |   Bal amt | Due dt              |   O/d |   OD days upto 30 |   OD days upto 60 |   OD days upto 90 |   OD days upto 120 |   OD days > 120 |
|:----------------|:----------|:--------------------|:---------|----------:|:-----------|----------:|:--------------------|------:|------------------:|------------------:|------------------:|-------------------:|----------------:|
| Name_S***       | MANCHAR   | ***************0:00 | PURC/94  |      8807 | **9972     |    339972 | 2023-04-15 00:00:00 |  1152 |               nan |               nan |               nan |                nan |          339972 |
| Name_S***       | MANCHAR   | ***************0:00 | PURC/95  |      8808 | *6261      |     16261 | 2023-04-15 00:00:00 |  1152 |               nan |               nan |               nan |                nan |           16261 |
| Name_S***       | MANCHAR   | ***************0:00 | PURC/106 |      9389 | *4381      |     74381 | 2023-04-17 00:00:00 |  1150 |               nan |               nan |               nan |                nan |           74381 |

### `Outstanding/Payables_Ageing_SupplierWise_22-23.xlsx`

- Size: 6.3 KB · Sheets: Report
- Rows: 2 · Columns (9): `Supplier name`, `Address`, `Tot bill amt`, `Tot bal amt`, `OD days upto 30`, `OD days upto 60`, `OD days upto 90`, `OD days upto 120`, `OD days > 120`
- Date range: —
- Key totals: `Tot bill amt` = 0.00 · `Tot bal amt` = 0.00

Masked sample (first 3 rows):

| Supplier name   | Address   |   Tot bill amt |   Tot bal amt |   OD days upto 30 |   OD days upto 60 |   OD days upto 90 |   OD days upto 120 |   OD days > 120 |
|:----------------|:----------|---------------:|--------------:|------------------:|------------------:|------------------:|-------------------:|----------------:|
|                 | Totals:   |              0 |             0 |                 0 |                 0 |                 0 |                  0 |               0 |
| Name_G***       |           |                |           nan |               nan |               nan |               nan |                nan |             nan |

### `Outstanding/Payables_Ageing_SupplierWise_23-24.xlsx`

- Size: 6.8 KB · Sheets: Report
- Rows: 10 · Columns (9): `Supplier name`, `Address`, `Tot bill amt`, `Tot bal amt`, `OD days upto 30`, `OD days upto 60`, `OD days upto 90`, `OD days upto 120`, `OD days > 120`
- Date range: —
- Key totals: `Tot bill amt` = 8,558,388.00 · `Tot bal amt` = 8,318,444.00

Masked sample (first 3 rows):

| Supplier name   | Address       | Tot bill amt   |   Tot bal amt |   OD days upto 30 |   OD days upto 60 |   OD days upto 90 |   OD days upto 120 |   OD days > 120 |
|:----------------|:--------------|:---------------|--------------:|------------------:|------------------:|------------------:|-------------------:|----------------:|
| Name_A***       | CHINCHWAD     | *7554          |         97554 |               nan |               nan |               nan |                nan |           97554 |
| Name_B***       | PUNE          | 6336           |          6336 |               nan |               nan |               nan |                nan |            6336 |
| Name_B***       | URULI DEVACHI | **7330         |        152451 |               nan |               nan |               nan |                nan |          152451 |

### `Outstanding/Payables_Ageing_SupplierWise_24-25.xlsx`

- Size: 28.2 KB · Sheets: Report
- Rows: 325 · Columns (14): `Supplier name`, `Address`, `Bill date`, `Vch no`, `Bill no`, `Bill amt`, `Bal amt`, `Due dt`, `O/d`, `OD days upto 30`, `OD days upto 60`, `OD days upto 90`, `OD days upto 120`, `OD days > 120`
- Date range: 2023-04-15 → 2025-03-31 (col: Bill date)
- Key totals: `Bill amt` = 29,279,956.00 · `Bal amt` = 12,294,200.00

Masked sample (first 3 rows):

| Supplier name   | Address   | Bill date           | Vch no   |   Bill no | Bill amt   |   Bal amt | Due dt              |   O/d |   OD days upto 30 |   OD days upto 60 |   OD days upto 90 |   OD days upto 120 |   OD days > 120 |
|:----------------|:----------|:--------------------|:---------|----------:|:-----------|----------:|:--------------------|------:|------------------:|------------------:|------------------:|-------------------:|----------------:|
| Name_S***       | MANCHAR   | ***************0:00 | PURC/94  |      8807 | **9972     |    339972 | 2023-04-15 00:00:00 |  1152 |               nan |               nan |               nan |                nan |          339972 |
| Name_S***       | MANCHAR   | ***************0:00 | PURC/95  |      8808 | *6261      |     16261 | 2023-04-15 00:00:00 |  1152 |               nan |               nan |               nan |                nan |           16261 |
| Name_S***       | MANCHAR   | ***************0:00 | PURC/106 |      9389 | *4381      |     74381 | 2023-04-17 00:00:00 |  1150 |               nan |               nan |               nan |                nan |           74381 |

### `Outstanding/Payables_Ageing_SupplierWise_25-26.xlsx`

- Size: 9.1 KB · Sheets: Report
- Rows: 49 · Columns (9): `Supplier name`, `Address`, `Tot bill amt`, `Tot bal amt`, `OD days upto 30`, `OD days upto 60`, `OD days upto 90`, `OD days upto 120`, `OD days > 120`
- Date range: —
- Key totals: `Tot bill amt` = 45,920,318.00 · `Tot bal amt` = 18,853,060.00

Masked sample (first 3 rows):

| Supplier name   | Address     | Tot bill amt   |   Tot bal amt |   OD days upto 30 |   OD days upto 60 |   OD days upto 90 |   OD days upto 120 |   OD days > 120 |
|:----------------|:------------|:---------------|--------------:|------------------:|------------------:|------------------:|-------------------:|----------------:|
| Name_A***       | WADAKI-PUNE | **3993         |        313167 |               nan |               nan |             28695 |              16171 |          268301 |
| Name_A***       | WADKI       | *7761          |         42127 |               nan |               nan |             23691 |                nan |           18436 |
| Name_A***       | PUNE        | **6693         |         52378 |               nan |               nan |               nan |                nan |           52378 |

### `Outstanding/Payables_SupplierWise_22-23.xlsx`

- Size: 6.4 KB · Sheets: Report
- Rows: 4 · Columns (6): `Party name`, `Address`, `Area`, `Tel/Mobile`, `Tot bal amt`, `Tot due amt`
- Date range: —
- Key totals: `Tot bal amt` = 8,286.00 · `Tot due amt` = 8,286.00

Masked sample (first 3 rows):

| Party name   | Address            | Area                        | Tel/Mobile                     |   Tot bal amt |   Tot due amt |
|:-------------|:-------------------|:----------------------------|:-------------------------------|--------------:|--------------:|
| Name_****    | RANJANGAON GANPATI | WED-4-RANJANGAON RANJANGAON | 90XXXXXXXXXXXXXXXX67           |          2608 |          2608 |
| Name_V***    | SHIKRAPUR          | WED-6-SHIKRAPUR             | 72XXXXXXXXXXXXXXXXXXXXXXXXXX87 |          1535 |          1535 |
|              |                    |                             |                                |          4143 |          4143 |

### `Outstanding/Payables_SupplierWise_23-24.xlsx`

- Size: 6.8 KB · Sheets: Report
- Rows: 10 · Columns (9): `Supplier name`, `Address`, `Tot bill amt`, `Tot bal amt`, `OD days upto 30`, `OD days upto 60`, `OD days upto 90`, `OD days upto 120`, `OD days > 120`
- Date range: —
- Key totals: `Tot bill amt` = 8,558,388.00 · `Tot bal amt` = 8,318,444.00

Masked sample (first 3 rows):

| Supplier name   | Address       | Tot bill amt   |   Tot bal amt |   OD days upto 30 |   OD days upto 60 |   OD days upto 90 |   OD days upto 120 |   OD days > 120 |
|:----------------|:--------------|:---------------|--------------:|------------------:|------------------:|------------------:|-------------------:|----------------:|
| Name_A***       | CHINCHWAD     | *7554          |         97554 |               nan |               nan |               nan |                nan |           97554 |
| Name_B***       | PUNE          | 6336           |          6336 |               nan |               nan |               nan |                nan |            6336 |
| Name_B***       | URULI DEVACHI | **7330         |        152451 |               nan |               nan |               nan |                nan |          152451 |

### `Outstanding/Payables_SupplierWise_24-25.xlsx`

- Size: 22.8 KB · Sheets: Report
- Rows: 325 · Columns (8): `Supplier name`, `Bill dt`, `Vch no`, `Bill no`, `Bill amt`, `Bal amt`, `Due dt`, `OD`
- Date range: 2023-04-15 → 2025-03-31 (col: Bill dt)
- Key totals: `Bill amt` = 29,279,956.00 · `Bal amt` = 12,294,200.00

Masked sample (first 3 rows):

| Supplier name   | Bill dt             | Vch no   |   Bill no | Bill amt   |   Bal amt | Due dt              |   OD |
|:----------------|:--------------------|:---------|----------:|:-----------|----------:|:--------------------|-----:|
| Name_S***       | ***************0:00 | PURC/94  |      8807 | **9972     |    339972 | 2023-04-15 00:00:00 | 1152 |
| Name_S***       | ***************0:00 | PURC/95  |      8808 | *6261      |     16261 | 2023-04-15 00:00:00 | 1152 |
| Name_S***       | ***************0:00 | PURC/106 |      9389 | *4381      |     74381 | 2023-04-17 00:00:00 | 1150 |

### `Outstanding/Payables_SupplierWise_25-26.xlsx`

- Size: 15.8 KB · Sheets: Report
- Rows: 159 · Columns (6): `Party name`, `Address`, `Area`, `Tel/Mobile`, `Tot bal amt`, `Tot due amt`
- Date range: —
- Key totals: `Tot bal amt` = 19,083,847.88 · `Tot due amt` = 19,083,847.88

Masked sample (first 3 rows):

| Party name   | Address     | Area                        | Tel/Mobile                                                   |   Tot bal amt |   Tot due amt |
|:-------------|:------------|:----------------------------|:-------------------------------------------------------------|--------------:|--------------:|
| Name_A***    | SANASWADI   | WED-8-SANASWADI PERANE FATA | 99XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX87 |           319 |           319 |
| Name_A***    | WADAKI-PUNE | PUNE                        | 89XXXXXXXXXXXXXXXXXXXXXXXXXX08                               |        313167 |        313167 |
| Name_A***    | WADKI       | PUNE                        | 84XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX03                     |         42127 |         42127 |

### `Outstanding/Receivables_Ageing_CustomerWise_22-23.xlsx`

- Size: 6.5 KB · Sheets: Report
- Rows: 4 · Columns (9): `Customer name`, `Address`, `Tot bill amt`, `Tot bal amt`, `OD days upto 30`, `OD days upto 60`, `OD days upto 90`, `OD days upto 120`, `OD days > 120`
- Date range: —
- Key totals: `Tot bill amt` = 78,538.00 · `Tot bal amt` = 72,538.00

Masked sample (first 3 rows):

| Customer name   | Address            | Tot bill amt   |   Tot bal amt |   OD days upto 30 |   OD days upto 60 |   OD days upto 90 |   OD days upto 120 |   OD days > 120 |
|:----------------|:-------------------|:---------------|--------------:|------------------:|------------------:|------------------:|-------------------:|----------------:|
| Name_****       | RANJANGAON GANPATI | 5700           |          5700 |               nan |               nan |               nan |                nan |            5700 |
| Name_S***       | SHIKRAPUR          | *3569          |         30569 |               nan |               nan |               nan |                nan |           30569 |
|                 | Totals:            | *9269          |         36269 |                 0 |                 0 |                 0 |                  0 |           36269 |

### `Outstanding/Receivables_Ageing_CustomerWise_23-24.xlsx`

- Size: 6.8 KB · Sheets: Report
- Rows: 8 · Columns (9): `Customer name`, `Address`, `Tot bill amt`, `Tot bal amt`, `OD days upto 30`, `OD days upto 60`, `OD days upto 90`, `OD days upto 120`, `OD days > 120`
- Date range: —
- Key totals: `Tot bill amt` = 1,786,500.00 · `Tot bal amt` = 147,784.80

Masked sample (first 3 rows):

| Customer name   | Address        | Tot bill amt   |   Tot bal amt |   OD days upto 30 |   OD days upto 60 |   OD days upto 90 |   OD days upto 120 |   OD days > 120 |
|:----------------|:---------------|:---------------|--------------:|------------------:|------------------:|------------------:|-------------------:|----------------:|
| Name_D***       | WARJE (PUNE)   | 971            |           971 |               nan |               nan |               nan |                nan |             971 |
| Name_M***       | CHINCHAWAD     | **3508         |            22 |               nan |               nan |               nan |                nan |              22 |
| Name_P***       | RALEGAN SIDDHI | *9359          |         25652 |               nan |               nan |               nan |                nan |           25652 |

### `Outstanding/Receivables_Ageing_CustomerWise_24-25.xlsx`

- Size: 6.9 KB · Sheets: Report
- Rows: 11 · Columns (9): `Customer name`, `Address`, `Tot bill amt`, `Tot bal amt`, `OD days upto 30`, `OD days upto 60`, `OD days upto 90`, `OD days upto 120`, `OD days > 120`
- Date range: —
- Key totals: `Tot bill amt` = 548,586.00 · `Tot bal amt` = 202,062.80

Masked sample (first 3 rows):

| Customer name   | Address       | Tot bill amt   |   Tot bal amt |   OD days upto 30 |   OD days upto 60 |   OD days upto 90 |   OD days upto 120 |   OD days > 120 |
|:----------------|:--------------|:---------------|--------------:|------------------:|------------------:|------------------:|-------------------:|----------------:|
| Name_D***       | KAWATHE YEMAI | 1046           |          1046 |               nan |               nan |               nan |                nan |            1046 |
| Name_M***       | KOLGAON       | *1390          |          7000 |               nan |               nan |               nan |                nan |            7000 |
| Name_M***       | MALTHAN       | 6224           |          6224 |               nan |               nan |               nan |                nan |            6224 |

### `Outstanding/Receivables_Ageing_CustomerWise_25-26.xlsx`

- Size: 8.5 KB · Sheets: Report
- Rows: 38 · Columns (9): `Customer name`, `Address`, `Tot bill amt`, `Tot bal amt`, `OD days upto 30`, `OD days upto 60`, `OD days upto 90`, `OD days upto 120`, `OD days > 120`
- Date range: —
- Key totals: `Tot bill amt` = 3,549,854.00 · `Tot bal amt` = 3,081,912.80

Masked sample (first 3 rows):

| Customer name   | Address   | Tot bill amt   |   Tot bal amt |   OD days upto 30 |   OD days upto 60 |   OD days upto 90 |   OD days upto 120 |   OD days > 120 |
|:----------------|:----------|:---------------|--------------:|------------------:|------------------:|------------------:|-------------------:|----------------:|
| Name_B***       | SHRIGONGA | *0925          |         10925 |               nan |               nan |             10925 |                nan |             nan |
| Name_D***       | SANASWADI | *6768          |         24158 |               nan |               nan |             24158 |                nan |             nan |
| Name_D***       | MALTHAN   | 5787           |          4014 |               nan |               nan |              4014 |                nan |             nan |

### `Profit/P_and_L_22-23.xlsx`

- Size: 11.0 KB · Sheets: Report
- Rows: 129 · Columns (6): `Debit`, `col_1`, `Amount`, `Credit`, `col_4`, `Amount.1`
- Date range: —
- Key totals: `Amount` = 308,470,768.53 · `Amount.1` = 308,470,768.53

Masked sample (first 3 rows):

| Debit             |   col_1 |        Amount | Credit           |   col_4 |      Amount.1 |
|:------------------|--------:|--------------:|:-----------------|--------:|--------------:|
| Opening Stock     |     nan |   1.75266e+07 | Sales Accounts   |     nan |   1.25206e+08 |
| Purchase Accounts |     nan |   1.14693e+08 | BHANGAR SALE     |     nan | nan           |
| Discount Received |     nan | nan           | Discount Allowed |    4604 | nan           |

### `Profit/P_and_L_23-24.xlsx`

- Size: 6.4 KB · Sheets: Report
- Rows: 8 · Columns (4): `Debit`, `Amount`, `Credit`, `Amount.1`
- Date range: —
- Key totals: `Amount` = 280,554,800.23 · `Amount.1` = 280,554,800.23

Masked sample (first 3 rows):

| Debit             |      Amount | Credit            |        Amount.1 |
|:------------------|------------:|:------------------|----------------:|
| Opening Stock     | 1.58959e+07 | Sales Accounts    |     1.15445e+08 |
| Purchase Accounts | 1.04684e+08 | Expenses (Direct) | 18976.6         |
| Gross Profit      | 9.84862e+06 | Closing Stock     |     1.49641e+07 |

### `Profit/P_and_L_24-25.xlsx`

- Size: 6.4 KB · Sheets: Report
- Rows: 8 · Columns (4): `Debit`, `Amount`, `Credit`, `Amount.1`
- Date range: —
- Key totals: `Amount` = 275,265,058.65 · `Amount.1` = 275,265,058.65

Masked sample (first 3 rows):

| Debit             |      Amount | Credit            |        Amount.1 |
|:------------------|------------:|:------------------|----------------:|
| Opening Stock     | 1.49641e+07 | Sales Accounts    |     1.12836e+08 |
| Purchase Accounts | 1.0658e+08  | Expenses (Direct) | 45303           |
| Gross Profit      | 8.04425e+06 | Closing Stock     |     1.67072e+07 |

### `Profit/P_and_L_25-26.xlsx`

- Size: 6.4 KB · Sheets: Report
- Rows: 9 · Columns (4): `Debit`, `Amount`, `Credit`, `Amount.1`
- Date range: —
- Key totals: `Amount` = 291,754,342.81 · `Amount.1` = 291,754,342.81

Masked sample (first 3 rows):

| Debit             |         Amount | Credit         |      Amount.1 |
|:------------------|---------------:|:---------------|--------------:|
| Opening Stock     |    1.67072e+07 | Sales Accounts |   1.2338e+08  |
| Purchase Accounts |    1.14259e+08 | Closing Stock  |   1.50427e+07 |
| Expenses (Direct) | 2501.24        | nan            | nan           |

### `Profit/Profit_AllBills_22-23.xlsx`

- Size: 2412.9 KB · Sheets: Report
- Rows: 39011 · Columns (8): `Date`, `Vch no`, `Cust name`, `Address`, `Sale/Billed amt`, `Cost amt`, `Profit amt`, `Profit %`
- Date range: 2022-04-01 → 2023-03-31 (col: Date)
- Key totals: `Sale/Billed amt` = 284,253,132.68 · `Cost amt` = 242,953,281.84 · `Profit amt` = 12,821,224.62 · `Profit %` = 257,345.48

Masked sample (first 3 rows):

| Date                | Vch no      | Cust name   | Address                | Sale/Billed amt   |   Cost amt |   Profit amt |   Profit % |
|:--------------------|:------------|:------------|:-----------------------|:------------------|-----------:|-------------:|-----------:|
| 2022-04-01 00:00:00 | DCCA/21-221 | Name_M***   | SHIRUR (BABURAO NAGAR) | **9.88            |    250.554 |      33.3464 |   11.5035  |
| 2022-04-01 00:00:00 | DCCA/21-222 | Name_S***   | SHIRUR                 | *14.4             |    563.929 |      20.0314 |    3.26032 |
| 2022-04-01 00:00:00 | DCCC/21-221 | Name_S***   | SHRIGONDA              | ***1.91           |   2011.69  |     314.293  |    9.3209  |

### `Profit/Profit_AllBills_23-24.xlsx`

- Size: 2421.7 KB · Sheets: Report
- Rows: 40256 · Columns (8): `Date`, `Vch no`, `Cust name`, `Address`, `Sale/Billed amt`, `Cost amt`, `Profit amt`, `Profit %`
- Date range: 2023-04-01 → 2024-03-31 (col: Date)
- Key totals: `Sale/Billed amt` = 258,640,394.76 · `Cost amt` = 218,632,942.09 · `Profit amt` = 12,671,230.99 · `Profit %` = 273,877.75

Masked sample (first 3 rows):

| Date                | Vch no      | Cust name   | Address                | Sale/Billed amt   |   Cost amt |   Profit amt |   Profit % |
|:--------------------|:------------|:------------|:-----------------------|:------------------|-----------:|-------------:|-----------:|
| 2023-04-01 00:00:00 | DCCA/23-241 | Name_D***   | SHIRUR (BABURAO NAGAR) | ***0.44           |    3222.88 |       188.58 |    5.46539 |
| 2023-04-01 00:00:00 | DCCA/23-242 | Name_M***   | SHIRUR                 | **8.58            |     265.54 |        79.16 |   22.076   |
| 2023-04-01 00:00:00 | DCCC/23-241 | Name_S***   | SHIRUR                 | ***2.04           |    1067.37 |        63.91 |    5.45289 |

### `Profit/Profit_AllBills_24-25.xlsx`

- Size: 2503.2 KB · Sheets: Report
- Rows: 41215 · Columns (8): `Date`, `Vch no`, `Cust name`, `Address`, `Sale/Billed amt`, `Cost amt`, `Profit amt`, `Profit %`
- Date range: 2024-04-01 → 2025-03-31 (col: Date)
- Key totals: `Sale/Billed amt` = 254,154,745.76 · `Cost amt` = 213,819,880.54 · `Profit amt` = 13,457,405.96 · `Profit %` = 303,502.74

Masked sample (first 3 rows):

| Date                | Vch no   | Cust name   | Address   | Sale/Billed amt   |   Cost amt |   Profit amt |   Profit % |
|:--------------------|:---------|:------------|:----------|:------------------|-----------:|-------------:|-----------:|
| 2024-04-01 00:00:00 | CA/1     | Name_M***   | SHIRUR    | 1124              |     997.09 |        56.33 |    5.01157 |
| 2024-04-01 00:00:00 | CC/1     | Name_W***   | SHIKRAPUR | **90.6            |    2132.16 |       129.48 |    4.81231 |
| 2024-04-01 00:00:00 | CC/2     | Name_A***   | PARNER    | ****5.81          |   12155.3  |       565.8  |    3.90051 |

### `Profit/Profit_AllBills_25-26.xlsx`

- Size: 2602.0 KB · Sheets: Report
- Rows: 42848 · Columns (8): `Date`, `Vch no`, `Cust name`, `Address`, `Sale/Billed amt`, `Cost amt`, `Profit amt`, `Profit %`
- Date range: 2025-04-01 → 2026-03-31 (col: Date)
- Key totals: `Sale/Billed amt` = 279,225,212.76 · `Cost amt` = 234,862,705.18 · `Profit amt` = 14,388,413.44 · `Profit %` = 308,631.21

Masked sample (first 3 rows):

| Date                | Vch no   | Cust name   | Address            | Sale/Billed amt   |   Cost amt |   Profit amt |   Profit % |
|:--------------------|:---------|:------------|:-------------------|:------------------|-----------:|-------------:|-----------:|
| 2025-04-01 00:00:00 | CR/1     | Name_V***   | SHIRUR (JOSHIWADI) | 7268              |    3270.5  |       182.22 |    2.50715 |
| 2025-04-01 00:00:00 | CA/1     | Name_B***   | SHIRUR             | ***0.46           |    4715.95 |       399.27 |    7.27207 |
| 2025-04-01 00:00:00 | CA/2     | Name_S***   | SHIRUR             | ***6.51           |    2142.6  |        94.9  |    4.0443  |

### `Profit/Profit_MonthlySummary_22-23.xlsx`

- Size: 7.0 KB · Sheets: Report
- Rows: 14 · Columns (5): `Month`, `Sale/Billed amt`, `Cost amt`, `Profit amt`, `Profit %`
- Date range: —
- Key totals: `Sale/Billed amt` = 284,253,132.68 · `Cost amt` = 242,953,281.84 · `Profit amt` = 12,821,224.62 · `Profit %` = 59.57

Masked sample (first 3 rows):

| Month    | Sale/Billed amt   |    Cost amt |   Profit amt |   Profit % |
|:---------|:------------------|------------:|-------------:|-----------:|
| Apr-2022 | *************9995 | 6.36482e+06 |       382235 |    5.1329  |
| May-2022 | *************9996 | 8.04976e+06 |       436504 |    4.73071 |
| Jun-2022 | *************0005 | 6.44929e+06 |       396599 |    5.27854 |

### `Profit/Profit_MonthlySummary_23-24.xlsx`

- Size: 7.0 KB · Sheets: Report
- Rows: 14 · Columns (5): `Month`, `Sale/Billed amt`, `Cost amt`, `Profit amt`, `Profit %`
- Date range: —
- Key totals: `Sale/Billed amt` = 258,640,394.76 · `Cost amt` = 218,632,942.09 · `Profit amt` = 12,671,230.99 · `Profit %` = 63.75

Masked sample (first 3 rows):

| Month    | Sale/Billed amt   |    Cost amt |   Profit amt |   Profit % |
|:---------|:------------------|------------:|-------------:|-----------:|
| Apr-2023 | *************0003 | 9.17842e+06 |       450809 |    4.2243  |
| May-2023 | *************0009 | 7.35981e+06 |       439777 |    5.11076 |
| Jun-2023 | *************9996 | 7.86929e+06 |       439125 |    4.78196 |

### `Profit/Profit_MonthlySummary_24-25.xlsx`

- Size: 7.0 KB · Sheets: Report
- Rows: 14 · Columns (5): `Month`, `Sale/Billed amt`, `Cost amt`, `Profit amt`, `Profit %`
- Date range: —
- Key totals: `Sale/Billed amt` = 254,154,745.76 · `Cost amt` = 213,819,880.54 · `Profit amt` = 13,457,405.96 · `Profit %` = 68.94

Masked sample (first 3 rows):

| Month    | Sale/Billed amt   |    Cost amt |   Profit amt |   Profit % |
|:---------|:------------------|------------:|-------------:|-----------:|
| Apr-2024 | *************0015 | 7.78406e+06 |       499985 |    5.38193 |
| May-2024 | *************0001 | 8.12887e+06 |       478945 |    4.92899 |
| Jun-2024 | *************0004 | 9.14575e+06 |       539865 |    4.99372 |

### `Profit/Profit_MonthlySummary_25-26.xlsx`

- Size: 6.9 KB · Sheets: Report
- Rows: 14 · Columns (5): `Month`, `Sale/Billed amt`, `Cost amt`, `Profit amt`, `Profit %`
- Date range: —
- Key totals: `Sale/Billed amt` = 279,225,212.76 · `Cost amt` = 234,862,705.18 · `Profit amt` = 14,388,413.44 · `Profit %` = 66.96

Masked sample (first 3 rows):

| Month    | Sale/Billed amt   |    Cost amt |   Profit amt |   Profit % |
|:---------|:------------------|------------:|-------------:|-----------:|
| Apr-2025 | *************9999 | 8.77804e+06 |       528991 |    5.07102 |
| May-2025 | *************0001 | 8.5626e+06  |       521999 |    5.16439 |
| Jun-2025 | *************9999 | 1.00849e+07 |       630407 |    5.3046  |

### `Profit/Profit_ProductWise_22-23.xlsx`

- Size: 530.8 KB · Sheets: Report
- Rows: 7501 · Columns (8): `Prod name`, `Unit`, `Comp`, `Qty`, `Sale/Billed amt`, `Cost amt`, `Profit amt`, `Profit %`
- Date range: —
- Key totals: `Qty` = 1,995,628.00 · `Sale/Billed amt` = 255,777,095.74 · `Cost amt` = 242,953,281.84 · `Profit amt` = 12,823,813.90 · `Profit %` = 48,074.07

Masked sample (first 3 rows):

| Prod name   | Unit   | Comp   |   Qty | Sale/Billed amt   |   Cost amt |   Profit amt |   Profit % |
|:------------|:-------|:-------|------:|:------------------|-----------:|-------------:|-----------:|
| Name_(***   | 1      | MAN    |   120 | ***7.52           |     6664.8 |       132.72 |    1.95248 |
| Name_(***   | 1      | MAN    |     1 | 0.1               |        0.1 |       nan    |  nan       |
| Name_****   | 10 TAB | ADORN  |    30 | 3600              |     3375   |       225    |    6.25    |

### `Profit/Profit_ProductWise_23-24.xlsx`

- Size: 486.1 KB · Sheets: Report
- Rows: 7082 · Columns (8): `Prod name`, `Unit`, `Comp`, `Qty`, `Sale/Billed amt`, `Cost amt`, `Profit amt`, `Profit %`
- Date range: —
- Key totals: `Qty` = 1,566,291.00 · `Sale/Billed amt` = 231,303,885.14 · `Cost amt` = 218,632,942.09 · `Profit amt` = 12,670,943.05 · `Profit %` = 44,906.69

Masked sample (first 3 rows):

| Prod name   | Unit   | Comp       |   Qty | Sale/Billed amt   |   Cost amt |   Profit amt |   Profit % |
|:------------|:-------|:-----------|------:|:------------------|-----------:|-------------:|-----------:|
| Name_****   | 10 TAB | ADORN      |   162 | ****5.42          |   19175.1  |       570.36 |    2.88857 |
| Name_****   | Bott   | GLA        |    30 | ****1.95          |    9748.14 |       553.81 |    5.37578 |
| Name_****   | 10 TAB | MANKIND-PH |   505 | *************9999 |   28299.8  |      1613.37 |    5.39351 |

### `Profit/Profit_ProductWise_24-25.xlsx`

- Size: 280.6 KB · Sheets: Report
- Rows: 4245 · Columns (8): `Prod name`, `Unit`, `Comp`, `Qty`, `Sale/Billed amt`, `Cost amt`, `Profit amt`, `Profit %`
- Date range: —
- Key totals: `Qty` = 134,791.00 · `Sale/Billed amt` = 18,844,994.74 · `Cost amt` = 17,734,407.74 · `Profit amt` = 1,110,587.00 · `Profit %` = 29,035.24

Masked sample (first 3 rows):

| Prod name   | Unit   | Comp   |   Qty | Sale/Billed amt   |   Cost amt |   Profit amt |   Profit % |
|:------------|:-------|:-------|------:|:------------------|-----------:|-------------:|-----------:|
| Name_****   | 15 ML  | CIPLA  |     1 | *6.38             |      29.2  |         7.18 |   19.7361  |
| Name_****   | 15 ML  | ALE    |     2 | 78.5              |      75.12 |         3.38 |    4.30573 |
| Name_****   | 10 TAB | CIPLA  |    24 | 485               |     450    |        35    |    7.21649 |

### `Profit/Profit_ProductWise_25-26.xlsx`

- Size: 483.5 KB · Sheets: Report
- Rows: 7067 · Columns (8): `Prod name`, `Unit`, `Comp`, `Qty`, `Sale/Billed amt`, `Cost amt`, `Profit amt`, `Profit %`
- Date range: —
- Key totals: `Qty` = 1,509,393.00 · `Sale/Billed amt` = 249,251,087.48 · `Cost amt` = 234,862,705.18 · `Profit amt` = 14,388,382.30 · `Profit %` = 44,896.97

Masked sample (first 3 rows):

| Prod name   | Unit   | Comp   |   Qty | Sale/Billed amt   |   Cost amt |   Profit amt |   Profit % |
|:------------|:-------|:-------|------:|:------------------|-----------:|-------------:|-----------:|
| Name_****   | 10 TAB | ADORN  |   137 | *7286             |   15736.6  |      1549.44 |    8.96355 |
| Name_****   | 15 ML  | ALE    |   118 | *************9999 |    4451.88 |       256.76 |    5.45295 |
| Name_****   | 10 TAB | CIPLA  |    96 | ***1.14           |    1782.39 |       438.75 |   19.7534  |

### `Purchases/PTR_Changed_Purchase_22-23.xlsx`

- Size: 612.8 KB · Sheets: Report
- Rows: 10868 · Columns (11): `Date`, `Vch no`, `Product`, `Unit`, `Comp`, `Prev PTR`, `New PTR`, `Prev MRP`, `New MRP`, `Prev Scm %`, `New Scm %`
- Date range: 2022-04-01 → 2023-03-29 (col: Date)

Masked sample (first 3 rows):

| Date                | Vch no    | Product           | Unit   | Comp       |   Prev PTR |   New PTR |   Prev MRP |   New MRP |   Prev Scm % |   New Scm % |
|:--------------------|:----------|:------------------|:-------|:-----------|-----------:|----------:|-----------:|----------:|-------------:|------------:|
| 2022-08-31 00:00:00 | PURC/1307 | **ADKAST FA TAB   | 10 TAB | ADORN      |     150    |    159.29 |     196.87 |    209.06 |      nan     |     16.6667 |
| 2022-04-16 00:00:00 | PURC/82   | **GUDGESIC AA TAB | 10 TAB | MANKIND-PH |     nan    |    nan    |     nan    |    nan    |      200.017 |     10      |
| 2022-08-11 00:00:00 | PURC/1047 | **GUDGESIC AA TAB | 10 TAB | MANKIND-PH |      66.55 |     67.86 |      87.35 |     89.06 |      nan     |    nan      |

### `Purchases/PTR_Changed_Purchase_23-24.xlsx`

- Size: 369.6 KB · Sheets: Report
- Rows: 6534 · Columns (11): `Date`, `Vch no`, `Product`, `Unit`, `Comp`, `Prev PTR`, `New PTR`, `Prev MRP`, `New MRP`, `Prev Scm %`, `New Scm %`
- Date range: 2023-04-03 → 2024-03-28 (col: Date)

Masked sample (first 3 rows):

| Date                | Vch no    | Product           | Unit   | Comp       |   Prev PTR |   New PTR |   Prev MRP |   New MRP |   Prev Scm % |   New Scm % |
|:--------------------|:----------|:------------------|:-------|:-----------|-----------:|----------:|-----------:|----------:|-------------:|------------:|
| 2023-08-31 00:00:00 | PURC/1099 | **ADKAST FA TAB   | 10 TAB | ADORN      |     nan    |    nan    |     nan    |    nan    |      33.3333 |     16.6667 |
| 2024-01-20 00:00:00 | PURC/2156 | **ADKAST FA TAB   | 10 TAB | ADORN      |     nan    |    nan    |     nan    |    nan    |      16.6667 |     31.8182 |
| 2023-06-20 00:00:00 | PURC/493  | **GUDGESIC AA TAB | 10 TAB | MANKIND-PH |      67.86 |     74.64 |      89.06 |     97.97 |      10      |     10      |

### `Purchases/PTR_Changed_Purchase_24-25.xlsx`

- Size: 298.2 KB · Sheets: Report
- Rows: 5236 · Columns (11): `Date`, `Vch no`, `Product`, `Unit`, `Comp`, `Prev PTR`, `New PTR`, `Prev MRP`, `New MRP`, `Prev Scm %`, `New Scm %`
- Date range: 2024-04-01 → 2025-03-29 (col: Date)

Masked sample (first 3 rows):

| Date                | Vch no    | Product         | Unit   | Comp   |   Prev PTR |   New PTR |   Prev MRP |   New MRP |   Prev Scm % |   New Scm % |
|:--------------------|:----------|:----------------|:-------|:-------|-----------:|----------:|-----------:|----------:|-------------:|------------:|
| 2024-07-31 00:00:00 | PURC/1041 | **ADKAST FA TAB | 10 TAB | ADORN  |        nan |       nan |        nan |       nan |      33.3333 |     16.6667 |
| 2024-11-16 00:00:00 | PURC/1769 | **ADKAST FA TAB | 10 TAB | ADORN  |        nan |       nan |        nan |       nan |      16.6667 |     33.3333 |
| 2025-01-24 00:00:00 | PURC/2348 | **ADKAST FA TAB | 10 TAB | ADORN  |        nan |       nan |        nan |       nan |      33.3333 |     23.0769 |

### `Purchases/PTR_Changed_Purchase_25-26.xlsx`

- Size: 432.0 KB · Sheets: Report
- Rows: 7687 · Columns (11): `Date`, `Vch no`, `Product`, `Unit`, `Comp`, `Prev PTR`, `New PTR`, `Prev MRP`, `New MRP`, `Prev Scm %`, `New Scm %`
- Date range: 2025-04-01 → 2026-03-31 (col: Date)

Masked sample (first 3 rows):

| Date                | Vch no    | Product                        | Unit     | Comp   |   Prev PTR |   New PTR |   Prev MRP |   New MRP |   Prev Scm % |   New Scm % |
|:--------------------|:----------|:-------------------------------|:---------|:-------|-----------:|----------:|-----------:|----------:|-------------:|------------:|
| 2025-05-27 00:00:00 | PURC/401  | **ADKAST FA TAB                | 10 TAB   | ADORN  |     nan    |    nan    |     nan    |    nan    |      23.0769 |    100      |
| 2025-09-19 00:00:00 | PURC/1371 | *COFSILS GINGER LEMON 10'S  AL | 10 TAB   | CIPLA  |      25    |     27.14 |      32.81 |     35.63 |      16.6705 |     16.6701 |
| 2025-09-04 00:00:00 | PURC/1276 | *CRESAR 40 TABLETS             | 2 X 15'S | CIPLA  |      81.11 |     82.56 |     106.46 |    108.36 |     nan      |    nan      |

### `Purchases/Purchase_MonthWise_22-23.xlsx`

- Size: 6.3 KB · Sheets: Report
- Rows: 14 · Columns (2): `Month name`, `Amount`
- Date range: —
- Key totals: `Amount` = 272,393,014.04

Masked sample (first 3 rows):

| Month name   |   Amount |
|:-------------|---------:|
| Name_A***    |  7392758 |
| Name_M***    |  8488554 |
| Name_J***    |  8514166 |

### `Purchases/Purchase_MonthWise_23-24.xlsx`

- Size: 6.3 KB · Sheets: Report
- Rows: 14 · Columns (2): `Month name`, `Amount`
- Date range: —
- Key totals: `Amount` = 239,504,466.72

Masked sample (first 3 rows):

| Month name   |      Amount |
|:-------------|------------:|
| Name_A***    | 1.06517e+07 |
| Name_M***    | 8.27959e+06 |
| Name_J***    | 9.68662e+06 |

### `Purchases/Purchase_MonthWise_24-25.xlsx`

- Size: 6.3 KB · Sheets: Report
- Rows: 14 · Columns (2): `Month name`, `Amount`
- Date range: —
- Key totals: `Amount` = 246,629,846.00

Masked sample (first 3 rows):

| Month name   |   Amount |
|:-------------|---------:|
| Name_A***    | 11461535 |
| Name_M***    | 11445021 |
| Name_J***    |  9443957 |

### `Purchases/Purchase_MonthWise_25-26.xlsx`

- Size: 6.2 KB · Sheets: Report
- Rows: 14 · Columns (2): `Month name`, `Amount`
- Date range: —
- Key totals: `Amount` = 254,437,264.00

Masked sample (first 3 rows):

| Month name   |   Amount |
|:-------------|---------:|
| Name_A***    | 11819225 |
| Name_M***    |  9029791 |
| Name_J***    | 10130827 |

### `Purchases/Purchase_ProductDetails_22-23.xlsx`

- Size: 2568.6 KB · Sheets: Report
- Rows: 46337 · Columns (11): `Product name`, `Unit`, `Company name`, `Qty`, `Scm qty`, `MRP`, `Tax%`, `Purc rate`, `PTR`, `Sale rate`, `Amount`
- Date range: —
- Key totals: `Qty` = 2,402,124.00 · `Scm qty` = 55,099.00 · `Sale rate` = 4,599,768.45 · `Amount` = 405,679,171.17

Masked sample (first 3 rows):

| Product name   | Unit          | Company name         |   Qty |   Scm qty |    MRP |   Tax% |   Purc rate |    PTR |   Sale rate |    Amount |
|:---------------|:--------------|:---------------------|------:|----------:|-------:|-------:|------------:|-------:|------------:|----------:|
| Name_M***      | 01-04, PURC/1 | ****************7*CN |   nan |       nan | nan    |    nan |      nan    | nan    |      nan    | 289405    |
| Name_A***      | 1*6.5 GM      | MAN                  |  1005 |       201 |  42.28 |     12 |       28.99 |  32.21 |       32.21 |  29135    |
| Name_B***      | 5GM           | MAN                  |    11 |         1 |  46.84 |     12 |       32.12 |  35.69 |       35.69 |    353.32 |

### `Purchases/Purchase_ProductDetails_23-24.xlsx`

- Size: 2109.8 KB · Sheets: Report
- Rows: 37675 · Columns (11): `Product name`, `Unit`, `Company name`, `Qty`, `Scm qty`, `MRP`, `Tax%`, `Purc rate`, `PTR`, `Sale rate`, `Amount`
- Date range: —
- Key totals: `Qty` = 1,954,464.00 · `Scm qty` = 39,948.00 · `Sale rate` = 3,866,024.98 · `Amount` = 359,140,270.85

Masked sample (first 3 rows):

| Product name   | Unit          | Company name      |   Qty |   Scm qty |    MRP |   Tax% |   Purc rate |    PTR |   Sale rate |    Amount |
|:---------------|:--------------|:------------------|------:|----------:|-------:|-------:|------------:|-------:|------------:|----------:|
| Name_C***      | 01-04, PURC/1 | *************9988 |   nan |       nan | nan    |    nan |      nan    | nan    |      nan    | 166459    |
| Name_D***      | 1X10'S        | *IPLA             |    21 |       nan | 178.12 |     12 |      122.14 | 135.71 |      135.71 |   2564.94 |
| Name_C***      | 15 TAB        | CIP               |    50 |       nan |  88.31 |     12 |       60.56 |  67.29 |       67.29 |   3028    |

### `Purchases/Purchase_ProductDetails_24-25.xlsx`

- Size: 2153.2 KB · Sheets: Report
- Rows: 38447 · Columns (11): `Product name`, `Unit`, `Company name`, `Qty`, `Scm qty`, `MRP`, `Tax%`, `Purc rate`, `PTR`, `Sale rate`, `Amount`
- Date range: —
- Key totals: `Qty` = 1,846,273.00 · `Scm qty` = 53,659.00 · `Sale rate` = 4,166,130.51 · `Amount` = 364,756,897.15

Masked sample (first 3 rows):

| Product name   | Unit          | Company name       |   Qty |   Scm qty |    MRP |   Tax% |   Purc rate |    PTR |   Sale rate |   Amount |
|:---------------|:--------------|:-------------------|------:|----------:|-------:|-------:|------------:|-------:|------------:|---------:|
| Name_M***      | 01-04, PURC/1 | **************91** |   nan |       nan | nan    |    nan |      nan    | nan    |      nan    | 84198    |
| Name_G***      | 5ML           | *ANKI              |    50 |       nan |  74.87 |     12 |       51.34 |  57.04 |       57.04 |  2567    |
| Name_L***      | 10 ML         | *ANKI              |    25 |       nan | 299.06 |     12 |      205.07 | 227.86 |      227.86 |  5126.75 |

### `Purchases/Purchase_ProductDetails_25-26.xlsx`

- Size: 2279.0 KB · Sheets: Report
- Rows: 40553 · Columns (11): `Product name`, `Unit`, `Company name`, `Qty`, `Scm qty`, `MRP`, `Tax%`, `Purc rate`, `PTR`, `Sale rate`, `Amount`
- Date range: —
- Key totals: `Qty` = 1,729,161.00 · `Scm qty` = 162,100.00 · `Sale rate` = 4,781,935.80 · `Amount` = 375,651,039.90

Masked sample (first 3 rows):

| Product name   | Unit          | Company name      |   Qty |   Scm qty |    MRP |   Tax% |   Purc rate |    PTR |   Sale rate |   Amount |
|:---------------|:--------------|:------------------|------:|----------:|-------:|-------:|------------:|-------:|------------:|---------:|
| Name_C***      | 01-04, PURC/1 | *************1764 |   nan |       nan | nan    |    nan |      nan    | nan    |      nan    | 282817   |
| Name_A***      | 10 TAB        | *IPLA             |    50 |       nan |  79.9  |     12 |       54.79 |  60.88 |       60.88 |   2739.5 |
| Name_A***      | 10 GM         | *IPLA             |    25 |       nan | 166.08 |     12 |      113.88 | 126.54 |      126.54 |   2847   |

### `Purchases/Purchase_Report_22-23.xlsx`

- Size: 123.3 KB · Sheets: Report
- Rows: 3009 · Columns (6): `Date`, `Vch no`, `Bill no`, `Supplier name`, `Address`, `Net`
- Date range: 2022-04-01 → 2023-03-31 (col: Date)
- Key totals: `Net` = 272,393,014.04

Masked sample (first 3 rows):

| Date                | Vch no   | Bill no              | Supplier name   | Address       |    Net |
|:--------------------|:---------|:---------------------|:----------------|:--------------|-------:|
| 2022-04-01 00:00:00 | PURC/1   | *********7*CN        | Name_M***       | URALIDEVACHI  | 289405 |
| 2022-04-01 00:00:00 | PURC/2   | **********SHRN       | Name_M***       | URALIDEVACHI  |  45614 |
| 2022-04-01 00:00:00 | PURC/3   | ****************SHRN | Name_M***       | URULI DEVACHI |      3 |

### `Purchases/Purchase_Report_23-24.xlsx`

- Size: 110.1 KB · Sheets: Report
- Rows: 2679 · Columns (6): `Date`, `Vch no`, `Bill no`, `Supplier name`, `Address`, `Net`
- Date range: 2023-04-01 → 2024-03-28 (col: Date)
- Key totals: `Net` = 239,504,466.72

Masked sample (first 3 rows):

| Date                | Vch no   | Bill no         | Supplier name   | Address       |    Net |
|:--------------------|:---------|:----------------|:----------------|:--------------|-------:|
| 2023-04-01 00:00:00 | PURC/1   | ******9988      | Name_C***       | WADAKI,PUNE   | 166459 |
| 2023-04-01 00:00:00 | PURC/2   | ******7180      | Name_C***       | WADAKI,PUNE   |   4115 |
| 2023-04-01 00:00:00 | PURC/3   | ***********SHRN | Name_M***       | URULI DEVACHI |  48461 |

### `Purchases/Purchase_Report_24-25.xlsx`

- Size: 115.3 KB · Sheets: Report
- Rows: 2841 · Columns (6): `Date`, `Vch no`, `Bill no`, `Supplier name`, `Address`, `Net`
- Date range: 2024-04-01 → 2025-03-29 (col: Date)
- Key totals: `Net` = 246,629,846.00

Masked sample (first 3 rows):

| Date                | Vch no   | Bill no       | Supplier name   | Address      |   Net |
|:--------------------|:---------|:--------------|:----------------|:-------------|------:|
| 2024-04-01 00:00:00 | PURC/1   | *******91**   | Name_M***       | URALIDEVACHI | 84198 |
| 2024-04-01 00:00:00 | PURC/2   | *****4610     | Name_M***       | WADAKI       | 25544 |
| 2024-04-01 00:00:00 | PURC/4   | ***********MR | Name_M***       | URALIDEVACHI | 29484 |

### `Purchases/Purchase_Report_25-26.xlsx`

- Size: 116.5 KB · Sheets: Report
- Rows: 2886 · Columns (6): `Date`, `Vch no`, `Bill no`, `Supplier name`, `Address`, `Net`
- Date range: 2025-04-01 → 2026-03-31 (col: Date)
- Key totals: `Net` = 254,437,264.00

Masked sample (first 3 rows):

| Date                | Vch no   | Bill no    | Supplier name   | Address     |    Net |
|:--------------------|:---------|:-----------|:----------------|:------------|-------:|
| 2025-04-01 00:00:00 | PURC/1   | ******1764 | Name_C***       | WADAKI,PUNE | 282817 |
| 2025-04-01 00:00:00 | PURC/2   | ******1968 | Name_C***       | WADAKI,PUNE |   4145 |
| 2025-04-01 00:00:00 | PURC/3   | ******0008 | Name_M***       | WADAKI      | 132789 |

### `Purchases/SupplierWise_Purchase_22-23.xlsx`

- Size: 8.5 KB · Sheets: Report
- Rows: 74 · Columns (3): `Supplier name`, `Short address`, `Amount`
- Date range: —
- Key totals: `Amount` = 272,393,014.04

Masked sample (first 3 rows):

| Supplier name   | Short address      |   Amount |
|:----------------|:-------------------|---------:|
| Name_A***       | WADAKI-PUNE        |   420152 |
| Name_A***       | URULI DEVACHI      |   254555 |
| Name_A***       | SADASHIV PETH PUNE |   457675 |

### `Purchases/SupplierWise_Purchase_23-24.xlsx`

- Size: 8.5 KB · Sheets: Report
- Rows: 76 · Columns (3): `Supplier name`, `Short address`, `Amount`
- Date range: —
- Key totals: `Amount` = 239,504,466.72

Masked sample (first 3 rows):

| Supplier name   | Short address   |   Amount |
|:----------------|:----------------|---------:|
| Name_A***       | WADAKI-PUNE     |   586174 |
| Name_A***       | WADKI           |    82889 |
| Name_A***       | BHIVANDI        |    33456 |

### `Purchases/SupplierWise_Purchase_24-25.xlsx`

- Size: 8.1 KB · Sheets: Report
- Rows: 65 · Columns (3): `Supplier name`, `Short address`, `Amount`
- Date range: —
- Key totals: `Amount` = 246,629,846.00

Masked sample (first 3 rows):

| Supplier name   | Short address   |   Amount |
|:----------------|:----------------|---------:|
| Name_A***       | WADAKI-PUNE     |   356149 |
| Name_A***       | WADKI           |   175031 |
| Name_A***       | BHIVANDI        |   184858 |

### `Purchases/SupplierWise_Purchase_25-26.xlsx`

- Size: 8.2 KB · Sheets: Report
- Rows: 66 · Columns (3): `Supplier name`, `Short address`, `Amount`
- Date range: —
- Key totals: `Amount` = 254,437,264.00

Masked sample (first 3 rows):

| Supplier name   | Short address     |   Amount |
|:----------------|:------------------|---------:|
| Name_A***       | WADAKI-PUNE       |   412058 |
| Name_A***       | WADKI             |   165226 |
| Name_A***       | CHINCHWAD STATION |    17560 |

### `Sales/Area_Sales_22-23.xlsx`

- Size: 7.4 KB · Sheets: Report
- Rows: 38 · Columns (4): `Area name`, `No of customers`, `No of bills`, `Sale amount`
- Date range: —
- Key totals: `Sale amount` = 283,629,372.00

Masked sample (first 3 rows):

| Area name   |   No of customers |   No of bills |   Sale amount |
|:------------|------------------:|--------------:|--------------:|
| Name_A***   |                 1 |             2 |         71148 |
| Name_A***   |                 1 |            54 |         39796 |
| Name_B***   |                 1 |             1 |         40890 |

### `Sales/Area_Sales_23-24.xlsx`

- Size: 7.4 KB · Sheets: Report
- Rows: 37 · Columns (4): `Area name`, `No of customers`, `No of bills`, `Sale amount`
- Date range: —
- Key totals: `Sale amount` = 256,642,036.00

Masked sample (first 3 rows):

| Area name   |   No of customers |   No of bills |   Sale amount |
|:------------|------------------:|--------------:|--------------:|
| Name_A***   |                 1 |             5 |         33426 |
| Name_A***   |                 1 |            36 |         24697 |
| Name_D***   |                 2 |             2 |         13582 |

### `Sales/Area_Sales_24-25.xlsx`

- Size: 7.3 KB · Sheets: Report
- Rows: 34 · Columns (4): `Area name`, `No of customers`, `No of bills`, `Sale amount`
- Date range: —
- Key totals: `Sale amount` = 250,318,112.00

Masked sample (first 3 rows):

| Area name   |   No of customers |   No of bills |   Sale amount |
|:------------|------------------:|--------------:|--------------:|
| Name_1***   |                 1 |             3 |          4338 |
| Name_A***   |                 1 |             3 |         62419 |
| Name_A***   |                 1 |            22 |         13737 |

### `Sales/Area_Sales_25-26.xlsx`

- Size: 7.3 KB · Sheets: Report
- Rows: 34 · Columns (4): `Area name`, `No of customers`, `No of bills`, `Sale amount`
- Date range: —
- Key totals: `Sale amount` = 250,318,112.00

Masked sample (first 3 rows):

| Area name   |   No of customers |   No of bills |   Sale amount |
|:------------|------------------:|--------------:|--------------:|
| Name_1***   |                 1 |             3 |          4338 |
| Name_A***   |                 1 |             3 |         62419 |
| Name_A***   |                 1 |            22 |         13737 |

### `Sales/Customer_Sales_22-23.xlsx`

- Size: 1196.0 KB · Sheets: Report
- Rows: 39683 · Columns (6): `Customer name`, `Address`, `Vch date`, `Vch no`, `Tran type`, `Amount`
- Date range: 2022-04-01 → 2023-03-31 (col: Vch date)
- Key totals: `Amount` = 425,837,691.00

Masked sample (first 3 rows):

| Customer name   | Address   | Vch date            | Vch no   | Tran type   |   Amount |
|:----------------|:----------|:--------------------|:---------|:------------|---------:|
| Name_****       | NIGHOJ    | nan                 | nan      | nan         |      382 |
|                 |           | 2022-09-15 00:00:00 | CC/2738  | Cash        |      382 |
| Name_****       | KAREGAON  | nan                 | nan      | nan         |     6139 |

### `Sales/Customer_Sales_23-24.xlsx`

- Size: 1235.9 KB · Sheets: Report
- Rows: 40939 · Columns (6): `Customer name`, `Address`, `Vch date`, `Vch no`, `Tran type`, `Amount`
- Date range: 2023-04-01 → 2024-03-31 (col: Vch date)
- Key totals: `Amount` = 384,975,087.00

Masked sample (first 3 rows):

| Customer name   | Address            | Vch date            | Vch no   | Tran type   |   Amount |
|:----------------|:-------------------|:--------------------|:---------|:------------|---------:|
| Name_****       | VARVAND            | nan                 | nan      | nan         |      780 |
|                 |                    | 2023-04-21 00:00:00 | CA/1241  | Cash        |      780 |
| Name_****       | RANJANGAON GANPATI | nan                 | nan      | nan         |    85334 |

### `Sales/Customer_Sales_24-25.xlsx`

- Size: 1333.4 KB · Sheets: Report
- Rows: 43412 · Columns (6): `Customer name`, `Address`, `Vch date`, `Vch no`, `Tran type`, `Amount`
- Date range: 2024-04-01 → 2025-03-31 (col: Vch date)
- Key totals: `Amount` = 378,222,552.00

Masked sample (first 3 rows):

| Customer name   | Address   | Vch date            | Vch no   | Tran type   |   Amount |
|:----------------|:----------|:--------------------|:---------|:------------|---------:|
| Name_M***       | SHIRUR    | nan                 | nan      | nan         |       60 |
|                 |           | 2024-11-03 00:00:00 | R/*1024  | Cash        |       60 |
| Name_M***       | SHIRUR    | nan                 | nan      | nan         |     2155 |

### `Sales/Customer_Sales_25-26.xlsx`

- Size: 1374.3 KB · Sheets: Report
- Rows: 44807 · Columns (6): `Customer name`, `Address`, `Vch date`, `Vch no`, `Tran type`, `Amount`
- Date range: 2025-04-01 → 2026-03-31 (col: Vch date)
- Key totals: `Amount` = 402,479,310.00

Masked sample (first 3 rows):

| Customer name   | Address   | Vch date            | Vch no   | Tran type   |   Amount |
|:----------------|:----------|:--------------------|:---------|:------------|---------:|
| Name_C***       | Shirur    | nan                 | nan      | nan         |      154 |
|                 |           | 2025-12-01 00:00:00 | R/*1068  | Cash        |      154 |
| Name_M***       | SHIRUR    | nan                 | nan      | nan         |      274 |

### `Sales/Sales_22-23.xlsx`

- Size: 1120.9 KB · Sheets: Report
- Rows: 39011 · Columns (5): `Date`, `Vch no`, `Customer name`, `Address`, `Net`
- Date range: 2022-04-01 → 2023-03-31 (col: Date)
- Key totals: `Net` = 283,891,794.00

Masked sample (first 3 rows):

| Date                | Vch no      | Customer name   | Address                |   Net |
|:--------------------|:------------|:----------------|:-----------------------|------:|
| 2022-04-01 00:00:00 | DCCA/21-221 | Name_M***       | SHIRUR (BABURAO NAGAR) |   318 |
| 2022-04-01 00:00:00 | DCCA/21-222 | Name_S***       | SHIRUR                 |   654 |
| 2022-04-01 00:00:00 | DCCC/21-221 | Name_S***       | SHRIGONDA              |  2547 |

### `Sales/Sales_23-24.xlsx`

- Size: 1160.8 KB · Sheets: Report
- Rows: 40256 · Columns (5): `Date`, `Vch no`, `Customer name`, `Address`, `Net`
- Date range: 2023-04-01 → 2024-03-31 (col: Date)
- Key totals: `Net` = 256,650,058.00

Masked sample (first 3 rows):

| Date                | Vch no      | Customer name   | Address                |   Net |
|:--------------------|:------------|:----------------|:-----------------------|------:|
| 2023-04-01 00:00:00 | DCCA/23-241 | Name_D***       | SHIRUR (BABURAO NAGAR) |  3997 |
| 2023-04-01 00:00:00 | DCCA/23-242 | Name_M***       | SHIRUR                 |   386 |
| 2023-04-01 00:00:00 | DCCC/23-241 | Name_S***       | SHIRUR                 |  1267 |

### `Sales/Sales_24-25.xlsx`

- Size: 1212.4 KB · Sheets: Report
- Rows: 41215 · Columns (5): `Date`, `Vch no`, `Customer name`, `Address`, `Net`
- Date range: 2024-04-01 → 2025-03-31 (col: Date)
- Key totals: `Net` = 252,148,368.00

Masked sample (first 3 rows):

| Date                | Vch no   | Customer name   | Address   |   Net |
|:--------------------|:---------|:----------------|:----------|------:|
| 2024-04-01 00:00:00 | CA/1     | Name_M***       | SHIRUR    |  1170 |
| 2024-04-01 00:00:00 | CC/1     | Name_W***       | SHIKRAPUR |  2533 |
| 2024-04-01 00:00:00 | CC/2     | Name_A***       | PARNER    | 14203 |

### `Sales/Sales_25-26.xlsx`

- Size: 1258.4 KB · Sheets: Report
- Rows: 42848 · Columns (5): `Date`, `Vch no`, `Customer name`, `Address`, `Net`
- Date range: 2025-04-01 → 2026-03-31 (col: Date)
- Key totals: `Net` = 268,319,540.00

Masked sample (first 3 rows):

| Date                | Vch no   | Customer name   | Address            |   Net |
|:--------------------|:---------|:----------------|:-------------------|------:|
| 2025-04-01 00:00:00 | CR/1     | Name_V***       | SHIRUR (JOSHIWADI) |  3867 |
| 2025-04-01 00:00:00 | CA/1     | Name_B***       | SHIRUR             |  5722 |
| 2025-04-01 00:00:00 | CA/2     | Name_S***       | SHIRUR             |  2506 |

### `Sales/Sales_ProductWise_22-23.xlsx`

- Size: 374.2 KB · Sheets: Report
- Rows: 7501 · Columns (9): `Product`, `Unit`, `Com`, `Qty`, `Scm qty`, `Scm value`, `Tot SD`, `Tot ID`, `Tot amt`
- Date range: —
- Key totals: `Qty` = 4,861,726.00 · `Scm qty` = 2,592.00 · `Scm value` = 81,985.86 · `Tot amt` = 284,253,132.68

Masked sample (first 3 rows):

| Product                        | Unit   | Com   |   Qty |   Scm qty |   Scm value |   Tot SD |   Tot ID |   Tot amt |
|:-------------------------------|:-------|:------|------:|----------:|------------:|---------:|---------:|----------:|
| (ANJALI MULTI DICER-SPL - Qty  | 1      | MAN   |   120 |       nan |         nan |   755.28 |      nan |    7552.8 |
| (STEEL GLASS SET 02PCS(WORLDFA | 1      | MAN   |     1 |       nan |         nan |   nan    |      nan |       0.1 |
| **ADKAST FA TAB                | 10 TAB | ADORN |    30 |       nan |         nan |   750    |      nan |    4500   |

### `Sales/Sales_ProductWise_23-24.xlsx`

- Size: 353.2 KB · Sheets: Report
- Rows: 7082 · Columns (9): `Product`, `Unit`, `Com`, `Qty`, `Scm qty`, `Scm value`, `Tot SD`, `Tot ID`, `Tot amt`
- Date range: —
- Key totals: `Qty` = 3,941,296.00 · `Scm qty` = 6,630.00 · `Scm value` = 367,117.56 · `Tot amt` = 258,640,394.76

Masked sample (first 3 rows):

| Product           | Unit   | Com        |   Qty |   Scm qty |   Scm value |   Tot SD |   Tot ID |   Tot amt |
|:------------------|:-------|:-----------|------:|----------:|------------:|---------:|---------:|----------:|
| **ADKAST FA TAB   | 10 TAB | ADORN      |   162 |       nan |         nan |  7187.45 |      nan |   27078.3 |
| **CCM 30T/40T H   | Bott   | GLA        |    30 |       nan |         nan |   nan    |      nan |   10629.7 |
| **GUDGESIC AA TAB | 10 TAB | MANKIND-PH |   505 |       nan |         nan |  4265.05 |      nan |   34860.1 |

### `Sales/Sales_ProductWise_24-25.xlsx`

- Size: 341.4 KB · Sheets: Report
- Rows: 6804 · Columns (9): `Product`, `Unit`, `Com`, `Qty`, `Scm qty`, `Scm value`, `Tot SD`, `Tot ID`, `Tot amt`
- Date range: —
- Key totals: `Qty` = 3,750,068.00 · `Scm qty` = 21,226.00 · `Scm value` = 1,167,301.94 · `Tot amt` = 254,154,745.76

Masked sample (first 3 rows):

| Product                                | Unit   | Com   |   Qty |   Scm qty |   Scm value |   Tot SD |   Tot ID |   Tot amt |
|:---------------------------------------|:-------|:------|------:|----------:|------------:|---------:|---------:|----------:|
| **ADKAST FA TAB                        | 10 TAB | ADORN |   252 |       nan |         nan | 13204.9  |      nan |  42121.8  |
| *ALERID COLD TAB 10S (NEW FORMULATION) | 10 TAB | CIPLA |    86 |       nan |         nan |   689.87 |      nan |   4975.24 |
| *ALERID D TAB                          | 10 TAB | CIPLA |  1149 |       nan |         nan |  8096.47 |      nan |  51371.4  |

### `Sales/Sales_ProductWise_25-26.xlsx`

- Size: 354.3 KB · Sheets: Report
- Rows: 7067 · Columns (9): `Product`, `Unit`, `Com`, `Qty`, `Scm qty`, `Scm value`, `Tot SD`, `Tot ID`, `Tot amt`
- Date range: —
- Key totals: `Qty` = 3,810,146.00 · `Scm qty` = 29,038.00 · `Scm value` = 1,229,337.06 · `Tot amt` = 279,225,212.76

Masked sample (first 3 rows):

| Product                        | Unit   | Com   |   Qty |   Scm qty |   Scm value |   Tot SD |   Tot ID |   Tot amt |
|:-------------------------------|:-------|:------|------:|----------:|------------:|---------:|---------:|----------:|
| **ADKAST FA TAB                | 10 TAB | ADORN |   137 |       nan |         nan |  5114.79 |      nan |  22899.5  |
| *AZITHRAL 200 MG SUSP          | 15 ML  | ALE   |   118 |       nan |         nan |   nan    |      nan |   4848.68 |
| *COFSILS GINGER LEMON 10'S  AL | 10 TAB | CIPLA |    96 |       nan |         nan |   158.56 |      nan |   2451.36 |

### `Sales/Salesman_Sale_22-23.xlsx`

- Size: 12.7 KB · Sheets: Report
- Rows: 112 · Columns (8): `Salesman name`, `Cash sale`, `Ca/Cr sale`, `Credit sale`, `DC sale amt`, `Total sale`, `Sale return`, `Net sale`
- Date range: —
- Key totals: `Salesman name` = 3.00 · `Cash sale` = 99,480,156.38 · `Ca/Cr sale` = 35,821,031.16 · `Credit sale` = 120,472,646.08 · `DC sale amt` = 0.00 · `Total sale` = 255,773,833.62 · `Sale return` = 4,292,375.00 · `Net sale` = 251,481,458.62

Masked sample (first 3 rows):

| Salesman name   |   Cash sale |   Ca/Cr sale |   Credit sale |   DC sale amt |   Total sale |   Sale return |   Net sale |
|:----------------|------------:|-------------:|--------------:|--------------:|-------------:|--------------:|-----------:|
| Name_(***       |      nan    |       nan    |        nan    |           nan |        nan   |      19425.4  |   -19425.4 |
| Name_****       |     1900.43 |       797.17 |      11031.3  |           nan |      13728.9 |        354.08 |    13374.8 |
| Name_3***       |    29036.1  |     19464.8  |       7225.99 |           nan |      55726.9 |        nan    |    55726.9 |

### `Sales/Salesman_Sale_23-24.xlsx`

- Size: 12.9 KB · Sheets: Report
- Rows: 118 · Columns (8): `Salesman name`, `Cash sale`, `Ca/Cr sale`, `Credit sale`, `DC sale amt`, `Total sale`, `Sale return`, `Net sale`
- Date range: —
- Key totals: `Salesman name` = 3.00 · `Cash sale` = 96,784,147.88 · `Ca/Cr sale` = 40,343,600.16 · `Credit sale` = 94,176,025.20 · `DC sale amt` = 0.00 · `Total sale` = 231,303,773.24 · `Sale return` = 2,968,182.84 · `Net sale` = 228,335,590.40

Masked sample (first 3 rows):

| Salesman name   |   Cash sale |   Ca/Cr sale |   Credit sale |   DC sale amt |   Total sale |   Sale return |   Net sale |
|:----------------|------------:|-------------:|--------------:|--------------:|-------------:|--------------:|-----------:|
| Name_(***       |      nan    |       nan    |        nan    |           nan |       nan    |         21309 |  -21309    |
| Name_****       |      949.84 |      2506.95 |        nan    |           nan |      3456.79 |           nan |    3456.79 |
| Name_3***       |     3620.99 |       635.49 |        762.28 |           nan |      5018.76 |           nan |    5018.76 |

### `Sales/Salesman_Sale_24-25.xlsx`

- Size: 12.7 KB · Sheets: Report
- Rows: 115 · Columns (8): `Salesman name`, `Cash sale`, `Ca/Cr sale`, `Credit sale`, `DC sale amt`, `Total sale`, `Sale return`, `Net sale`
- Date range: —
- Key totals: `Salesman name` = 3.00 · `Cash sale` = 104,477,813.72 · `Ca/Cr sale` = 44,419,029.50 · `Credit sale` = 78,380,008.80 · `DC sale amt` = 0.00 · `Total sale` = 227,276,852.02 · `Sale return` = 3,447,871.12 · `Net sale` = 223,828,980.90

Masked sample (first 3 rows):

| Salesman name   |   Cash sale |   Ca/Cr sale |   Credit sale |   DC sale amt |   Total sale |   Sale return |   Net sale |
|:----------------|------------:|-------------:|--------------:|--------------:|-------------:|--------------:|-----------:|
| Name_(***       |      nan    |          nan |           nan |           nan |       nan    |         18464 |  -18464    |
| Name_****       |      408.96 |          nan |           nan |           nan |       408.96 |           nan |     408.96 |
| Name_3***       |      189.41 |          nan |           nan |           nan |       189.41 |           nan |     189.41 |

### `Sales/Salesman_Sale_25-26.xlsx`

- Size: 12.0 KB · Sheets: Report
- Rows: 98 · Columns (8): `Salesman name`, `Cash sale`, `Ca/Cr sale`, `Credit sale`, `DC sale amt`, `Total sale`, `Sale return`, `Net sale`
- Date range: —
- Key totals: `Salesman name` = 3.00 · `Cash sale` = 116,354,510.60 · `Ca/Cr sale` = 47,488,404.52 · `Credit sale` = 85,408,014.44 · `DC sale amt` = 0.00 · `Total sale` = 249,250,929.56 · `Sale return` = 2,928,470.80 · `Net sale` = 246,322,458.76

Masked sample (first 3 rows):

| Salesman name   |   Cash sale |   Ca/Cr sale |   Credit sale |   DC sale amt |   Total sale |   Sale return |   Net sale |
|:----------------|------------:|-------------:|--------------:|--------------:|-------------:|--------------:|-----------:|
| Name_(***       |      nan    |          nan |        nan    |           nan |       nan    |       17997.3 |  -17997.3  |
| Name_D***       |      nan    |          nan |       1551.16 |           nan |      1551.16 |         nan   |    1551.16 |
| Name_****       |      159.99 |          nan |        nan    |           nan |       159.99 |         nan   |     159.99 |

### `Stock/ClosingStock_22-23.xlsx`

- Size: 11.5 KB · Sheets: Report
- Rows: 47 · Columns (22): `Product name`, `Unit`, `Alias`, `Com`, `Shelf`, `Tax%`, `StkIn dt`, `Batch no`, `ExpDt`, `Purc rate`, `PTR`, `MRP`, `Sale rate 1`, `Sale rate 2`, `Sale rate 3`, `Qty`, `Value`, `Godown`, `Profit amt`, `Profit %`, `Purc scm`, `Sale scm`
- Date range: 2007-07-20 → 2023-01-18 (col: StkIn dt)
- Key totals: `Sale rate 1` = 28,203.05 · `Sale rate 2` = 27,987.88 · `Sale rate 3` = 28,936.40 · `Qty` = 537.00 · `Value` = 117,420.66 · `Profit amt` = 3,685.03 · `Profit %` = 750.30

Masked sample (first 3 rows):

| Product name   | Unit    | Alias   | Com   |   Shelf |   Tax% | StkIn dt            |   Batch no |   ExpDt |   Purc rate |    PTR |   MRP |   Sale rate 1 |   Sale rate 2 | Sale rate 3   |   Qty |    Value | Godown   |   Profit amt |   Profit % |   Purc scm |   Sale scm |
|:---------------|:--------|:--------|:------|--------:|-------:|:--------------------|-----------:|--------:|------------:|-------:|------:|--------------:|--------------:|:--------------|------:|---------:|:---------|-------------:|-----------:|-----------:|-----------:|
| Name_A***      | 500 GM  |         | SUR   |       0 |      5 | 2009-08-06 00:00:00 |          3 |     nan |          62 | 145.31 |   155 |        143.93 |        145.31 | 63.94         |     9 | 518.223  | SHOP     |       777.15 |      59.99 |          9 |        nan |
|                | nan     |         | nan   |     nan |    nan | nan                 |        nan |     nan |         nan | nan    |   nan |        nan    |        nan    | Totals:       |     9 | 518.223  | nan      |       nan    |     nan    |        nan |        nan |
| Name_C***      | 15CM*2Y |         | SUR   |     nan |      5 | 2009-09-01 00:00:00 |         10 |     nan |          24 |  84.37 |    90 |         83.58 |         84.37 | 25.88         |     2 |  40.1429 | SHOP     |       127.02 |      75.99 |          2 |        nan |

### `Stock/ClosingStock_23-24.xlsx`

- Size: 11.7 KB · Sheets: Report
- Rows: 94 · Columns (11): `Product name`, `Unit`, `Alias`, `Com`, `Shelf`, `Batch no`, `ExpDt`, `MRP`, `Sale rate 2`, `Sale rate 3`, `Qty`
- Date range: 2026-09-01 → 2037-11-30 (col: ExpDt)
- Key totals: `Sale rate 2` = 31,638.71 · `Sale rate 3` = 32,586.33 · `Qty` = 1,653.00

Masked sample (first 3 rows):

| Product name   | Unit   | Alias   | Com   | Shelf   | Batch no   | ExpDt               |    MRP |   Sale rate 2 | Sale rate 3   |   Qty |
|:---------------|:-------|:--------|:------|:--------|:-----------|:--------------------|-------:|--------------:|:--------------|------:|
| Name_A***      | 500 GM |         | SUR   | 00      | 03         | nan                 | 155    |        145.31 | 63.94         |     9 |
|                | nan    |         | nan   | nan     | nan        | nan                 | nan    |        nan    | Totals:       |     9 |
| Name_A***      | 15 TAB |         | ERIS  | CH6     | GATA24001  | 2026-12-31 00:00:00 | 460.63 |        350.96 | 350.96        |     7 |

### `Stock/ClosingStock_24-25.xlsx`

- Size: 57.1 KB · Sheets: Report
- Rows: 924 · Columns (11): `Product name`, `Unit`, `Alias`, `Com`, `Shelf`, `Batch no`, `ExpDt`, `MRP`, `Sale rate 2`, `Sale rate 3`, `Qty`
- Date range: 2026-09-01 → 2037-11-30 (col: ExpDt)
- Key totals: `Sale rate 2` = 96,054.97 · `Sale rate 3` = 97,002.60 · `Qty` = 28,977.00

Masked sample (first 3 rows):

| Product name   | Unit      |   Alias | Com   | Shelf   | Batch no   | ExpDt               |    MRP |   Sale rate 2 | Sale rate 3   |   Qty |
|:---------------|:----------|--------:|:------|:--------|:-----------|:--------------------|-------:|--------------:|:--------------|------:|
| Name_8***      | 1 X 30 GM |     176 | CIPLA | CS1-2-3 | 4R014      | 2026-11-30 00:00:00 | 230.28 |        175.45 | 175.45        |    15 |
|                | nan       |         | nan   | nan     | nan        | nan                 | nan    |        nan    | Totals:       |    15 |
| Name_A***      | 10 TAB    |         | FIDEL | D-6     | GT501094A  | 2026-12-31 00:00:00 |  98.44 |         75.43 | 75.43         |     4 |

### `Stock/ClosingStock_25-26.xlsx`

- Size: 547.8 KB · Sheets: Report
- Rows: 10312 · Columns (11): `Product name`, `Unit`, `Alias`, `Com`, `Shelf`, `Batch no`, `ExpDt`, `MRP`, `Sale rate 2`, `Sale rate 3`, `Qty`
- Date range: 2026-09-01 → 2045-02-28 (col: ExpDt)
- Key totals: `Sale rate 2` = 922,470.62 · `Sale rate 3` = 923,347.42 · `Qty` = 256,227.00

Masked sample (first 3 rows):

| Product name   | Unit   | Alias   | Com   | Shelf   | Batch no   | ExpDt               |    MRP |   Sale rate 2 | Sale rate 3   |   Qty |
|:---------------|:-------|:--------|:------|:--------|:-----------|:--------------------|-------:|--------------:|:--------------|------:|
| Name_1***      | 10 TAB |         | FDC   | BS1-2   | 075H033    | 2027-07-31 00:00:00 |  35.72 |         27.21 | 27.21         |    95 |
|                | nan    |         | nan   | nan     | nan        | nan                 | nan    |        nan    | Totals:       |    95 |
| Name_1***      | 60 ML  |         | FDC   | BS1-2   | 585L001    | 2027-11-30 00:00:00 |  93.56 |         71.28 | 71.28         |    28 |

### `Stock/Stock_CategoryWise_22-23.xlsx`

- Size: 6.2 KB · Sheets: Report
- Rows: 5 · Columns (3): `Particulars`, `No of products`, `Value`
- Date range: —
- Key totals: `Value` = 31,794,054.45

Masked sample (first 3 rows):

| Particulars   |   No of products |            Value |
|:--------------|-----------------:|-----------------:|
| Allopathic    |             6366 |      1.52382e+07 |
| AYURVEDIC     |               63 | 107666           |
| SCHEDULE H1   |              249 | 551115           |

### `Stock/Stock_CategoryWise_23-24.xlsx`

- Size: 6.2 KB · Sheets: Report
- Rows: 5 · Columns (3): `Particulars`, `No of products`, `Value`
- Date range: —
- Key totals: `Value` = 29,935,364.06

Masked sample (first 3 rows):

| Particulars   |   No of products |            Value |
|:--------------|-----------------:|-----------------:|
| Allopathic    |             5822 |      1.43444e+07 |
| AYURVEDIC     |               52 |  61546.8         |
| SCHEDULE H1   |              206 | 561746           |

### `Stock/Stock_CategoryWise_24-25.xlsx`

- Size: 6.2 KB · Sheets: Report
- Rows: 5 · Columns (3): `Particulars`, `No of products`, `Value`
- Date range: —
- Key totals: `Value` = 33,419,097.29

Masked sample (first 3 rows):

| Particulars   |   No of products |            Value |
|:--------------|-----------------:|-----------------:|
| Allopathic    |             6036 |      1.60892e+07 |
| AYURVEDIC     |               41 |  68878.3         |
| SCHEDULE H1   |              217 | 551468           |

### `Stock/Stock_CategoryWise_25-26.xlsx`

- Size: 6.2 KB · Sheets: Report
- Rows: 5 · Columns (3): `Particulars`, `No of products`, `Value`
- Date range: —
- Key totals: `Value` = 30,104,158.17

Masked sample (first 3 rows):

| Particulars   |   No of products |            Value |
|:--------------|-----------------:|-----------------:|
| Allopathic    |             5855 |      1.43512e+07 |
| AYURVEDIC     |               57 |  89257.6         |
| SCHEDULE H1   |              231 | 611611           |

### `Stock/Stock_CompanyWise_22-23.xlsx`

- Size: 22.9 KB · Sheets: Report
- Rows: 529 · Columns (3): `Particulars`, `No of products`, `Value`
- Date range: —
- Key totals: `Value` = 31,794,054.45

Masked sample (first 3 rows):

| Particulars               |   No of products |     Value |
|:--------------------------|-----------------:|----------:|
| **MED MANOR               |                3 |   26.9732 |
| *CIPLAA-LTD.(RESP TEAM 2) |                1 | 1051.14   |
| *SHOP UTILITIES           |                1 | 7806.78   |

### `Stock/Stock_CompanyWise_23-24.xlsx`

- Size: 22.4 KB · Sheets: Report
- Rows: 524 · Columns (3): `Particulars`, `No of products`, `Value`
- Date range: —
- Key totals: `Value` = 29,935,364.06

Masked sample (first 3 rows):

| Particulars               |   No of products |     Value |
|:--------------------------|-----------------:|----------:|
| **MED MANOR               |                3 |   26.9732 |
| *CIPLAA-LTD.(RESP TEAM 2) |                1 | 1892.06   |
| *SHOP UTILITIES           |                1 | 7806.78   |

### `Stock/Stock_CompanyWise_24-25.xlsx`

- Size: 22.0 KB · Sheets: Report
- Rows: 511 · Columns (3): `Particulars`, `No of products`, `Value`
- Date range: —
- Key totals: `Value` = 33,419,097.29

Masked sample (first 3 rows):

| Particulars               |   No of products |   Value |
|:--------------------------|-----------------:|--------:|
| *CIPLAA-LTD.(RESP TEAM 2) |                1 | 5010.46 |
| *SHOP UTILITIES           |                1 | 7806.78 |
| .                         |                1 | 4050.4  |

### `Stock/Stock_CompanyWise_25-26.xlsx`

- Size: 22.0 KB · Sheets: Report
- Rows: 510 · Columns (3): `Particulars`, `No of products`, `Value`
- Date range: —
- Key totals: `Value` = 30,104,158.17

Masked sample (first 3 rows):

| Particulars               |   No of products |   Value |
|:--------------------------|-----------------:|--------:|
| **MED MANOR               |                1 | 5317.58 |
| *CIPLAA-LTD.(RESP TEAM 2) |                2 | 8879.22 |
| *SHOP UTILITIES           |                1 | 7806.78 |

### `Stock/Stock_InOutSummary_22-23.xlsx`

- Size: 35.9 KB · Sheets: Report
- Rows: 829 · Columns (5): `Company`, `Opening value`, `Stock-in value`, `Stock-out value`, `Closing value`
- Date range: —
- Key totals: `Opening value` = 29,845,066.00 · `Stock-in value` = 252,924,268.00 · `Stock-out value` = 291,551,908.00 · `Closing value` = 31,791,750.00

Masked sample (first 3 rows):

| Company         |   Opening value |   Stock-in value |   Stock-out value |   Closing value |
|:----------------|----------------:|-----------------:|------------------:|----------------:|
| ***********LTH) |             nan |              nan |               nan |             nan |
| **********VID)  |             nan |              nan |               nan |             nan |
| ***KEM)         |             nan |              nan |               nan |             nan |

### `Stock/Stock_InOutSummary_23-24.xlsx`

- Size: 35.6 KB · Sheets: Report
- Rows: 827 · Columns (5): `Company`, `Opening value`, `Stock-in value`, `Stock-out value`, `Closing value`
- Date range: —
- Key totals: `Opening value` = 31,791,754.00 · `Stock-in value` = 224,721,686.00 · `Stock-out value` = 266,130,798.00 · `Closing value` = 29,928,308.00

Masked sample (first 3 rows):

| Company         |   Opening value |   Stock-in value |   Stock-out value |   Closing value |
|:----------------|----------------:|-----------------:|------------------:|----------------:|
| ***********LTH) |             nan |              nan |               nan |             nan |
| **********VID)  |             nan |              nan |               nan |             nan |
| ***KEM)         |             nan |              nan |               nan |             nan |

### `Stock/Stock_InOutSummary_24-25.xlsx`

- Size: 35.6 KB · Sheets: Report
- Rows: 827 · Columns (5): `Company`, `Opening value`, `Stock-in value`, `Stock-out value`, `Closing value`
- Date range: —
- Key totals: `Opening value` = 29,928,338.00 · `Stock-in value` = 223,742,444.00 · `Stock-out value` = 260,727,138.00 · `Closing value` = 33,414,410.00

Masked sample (first 3 rows):

| Company         |   Opening value |   Stock-in value |   Stock-out value |   Closing value |
|:----------------|----------------:|-----------------:|------------------:|----------------:|
| ***********LTH) |             nan |              nan |               nan |             nan |
| **********VID)  |             nan |              nan |               nan |             nan |
| ***KEM)         |             nan |              nan |               nan |             nan |

### `Stock/Stock_InOutSummary_25-26.xlsx`

- Size: 35.6 KB · Sheets: Report
- Rows: 827 · Columns (5): `Company`, `Opening value`, `Stock-in value`, `Stock-out value`, `Closing value`
- Date range: —
- Key totals: `Opening value` = 33,414,416.00 · `Stock-in value` = 237,705,414.00 · `Stock-out value` = 285,317,684.00 · `Closing value` = 30,085,454.00

Masked sample (first 3 rows):

| Company         |   Opening value |   Stock-in value |   Stock-out value |   Closing value |
|:----------------|----------------:|-----------------:|------------------:|----------------:|
| ***********LTH) |             nan |              nan |               nan |             nan |
| **********VID)  |             nan |              nan |               nan |             nan |
| ***KEM)         |             nan |              nan |               nan |             nan |

### `Stock/Stock_ProductWise_22-23.xlsx`

- Size: 339.0 KB · Sheets: Report
- Rows: 6680 · Columns (7): `Product name`, `Unit`, `Company`, `Tax%`, `Qty`, `Rate`, `Value`
- Date range: —
- Key totals: `Qty` = 245,973.00 · `Value` = 31,794,054.45

Masked sample (first 3 rows):

| Product name   | Unit   | Company   |   Tax% |   Qty |    Rate |   Value |
|:---------------|:-------|:----------|-------:|------:|--------:|--------:|
| Name_(***      | 1      | MED       |      5 |     3 |   1     |     3   |
| Name_(***      | 1      | MAN       |      5 |    12 |   1     |    12   |
| Name_****      | Bott   | GLA       |      5 |    44 | 324.939 | 14297.3 |

### `Stock/Stock_ProductWise_23-24.xlsx`

- Size: 308.8 KB · Sheets: Report
- Rows: 6082 · Columns (7): `Product name`, `Unit`, `Company`, `Tax%`, `Qty`, `Rate`, `Value`
- Date range: —
- Key totals: `Qty` = 239,506.00 · `Value` = 29,935,364.06

Masked sample (first 3 rows):

| Product name   | Unit   | Company   |   Tax% |   Qty |      Rate |     Value |
|:---------------|:-------|:----------|-------:|------:|----------:|----------:|
| Name_****      | 10 TAB | *DORN     |      5 |    42 | 102.56    | 4307.52   |
| Name_****      | Bott   | GLA       |      5 |    17 | 324.94    | 5523.98   |
| Name_****      | 01     | **MED     |      5 |    18 |   0.81498 |   14.6696 |

### `Stock/Stock_ProductWise_24-25.xlsx`

- Size: 320.5 KB · Sheets: Report
- Rows: 6296 · Columns (7): `Product name`, `Unit`, `Company`, `Tax%`, `Qty`, `Rate`, `Value`
- Date range: —
- Key totals: `Qty` = 241,212.00 · `Value` = 33,419,097.29

Masked sample (first 3 rows):

| Product name   | Unit   | Company   |   Tax% |   Qty |     Rate |   Value |
|:---------------|:-------|:----------|-------:|------:|---------:|--------:|
| Name_****      | 10 TAB | *DORN     |      5 |    72 | 109.456  | 7880.8  |
| Name_****      | 15 ML  | ALE       |      5 |    88 |  37.56   | 3305.28 |
| Name_****      | 10 TAB | *IPLA     |      5 |    24 |  17.9688 |  431.25 |

### `Stock/Stock_ProductWise_25-26.xlsx`

- Size: 314.5 KB · Sheets: Report
- Rows: 6145 · Columns (7): `Product name`, `Unit`, `Company`, `Tax%`, `Qty`, `Rate`, `Value`
- Date range: —
- Key totals: `Qty` = 204,079.00 · `Value` = 30,104,158.17

Masked sample (first 3 rows):

| Product name   | Unit     | Company   |   Tax% |   Qty |   Rate |   Value |
|:---------------|:---------|:----------|-------:|------:|-------:|--------:|
| Name_****      | 2 X 15'S | *IPLA     |      5 |     5 | 134.7  |  673.5  |
| Name_****      | 5 ML     | CIP       |      5 |     5 |  53.4  |  267    |
| Name_1***      | 10 TAB   | FDC       |      5 |   199 |  25.03 | 4980.97 |
