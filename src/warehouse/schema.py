"""Warehouse schema registry — schema-as-data, the single source of truth.

Every physical table, the data dictionary, and the business metadata catalog are
generated from `SCHEMA` below, so documentation can never drift from the database.

Each table also carries STANDARD_COLUMNS: data lineage (source report/year/file,
import batch), audit metadata (processed_at), and a per-record quality status —
so every row is traceable back to the exact ERP export it came from.

Forward-compatibility: `fact_sales_line` / `fact_purchase_line` are declared here
as DESIGN-TIME extension points (build_now=False). When richer ERP exports appear,
flip build_now=True and add a loader — dimensions, KPIs, and dashboards are
unaffected because they already key off conformed dims.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ColumnSpec:
    name: str
    sqltype: str                     # INTEGER | REAL | TEXT | DATE | TIMESTAMP
    description: str
    business_definition: str = ""
    nullable: bool = True
    is_key: bool = False             # part of natural/business key
    is_fk: str | None = None         # referenced table, if foreign key
    source_column: str | None = None  # canonical adapter column it derives from
    kpi: bool = False                # is this a headline business measure?
    currency_inr: bool = False       # money column stored in INR (source of truth)


@dataclass(frozen=True)
class TableSpec:
    name: str
    role: str                        # dimension | fact | meta
    grain: str
    description: str
    source_report: str               # ERP report(s) this is built from
    columns: list[ColumnSpec]
    relationships: list[str] = field(default_factory=list)
    build_now: bool = True           # False = declared design-time extension point

    def business_columns(self) -> list[ColumnSpec]:
        return list(self.columns)

    def all_columns(self) -> list[ColumnSpec]:
        # meta tables are the audit anchor itself — no standard lineage columns.
        if self.role == "meta":
            return list(self.columns)
        return list(self.columns) + STANDARD_COLUMNS


# --------------------------------------------------------------------------- #
# Standard lineage / audit / quality columns on EVERY business table
# --------------------------------------------------------------------------- #
STANDARD_COLUMNS: list[ColumnSpec] = [
    ColumnSpec("src_report", "TEXT", "Source ERP report key (e.g. 'Sales/Sales')",
               "Data lineage: which ERP export produced this row", nullable=False),
    ColumnSpec("src_year", "TEXT", "Source financial year (e.g. '25-26')",
               "Data lineage: financial year of the source export"),
    ColumnSpec("src_file", "TEXT", "Source file path under data/raw/",
               "Data lineage: exact file of origin"),
    ColumnSpec("import_batch_id", "INTEGER", "FK to meta_import_batch",
               "Audit: the build run that loaded this row", is_fk="meta_import_batch"),
    ColumnSpec("processed_at", "TIMESTAMP", "UTC timestamp this row was loaded",
               "Audit: processing timestamp"),
    ColumnSpec("record_quality", "TEXT",
               "Quality status: ok | reconciled | unmatched_entity | "
               "duplicate_removed | imputed | quarantined",
               "Record quality flag for governance & the DQ dashboard", nullable=False),
    ColumnSpec("quality_flags", "TEXT", "Optional pipe-separated quality notes",
               "Detailed quality annotations, if any"),
]


def _money(name, desc, src=None, kpi=False):
    return ColumnSpec(name, "REAL", desc, nullable=True, source_column=src,
                      kpi=kpi, currency_inr=True)


# --------------------------------------------------------------------------- #
# DIMENSIONS
# --------------------------------------------------------------------------- #
_DIMENSIONS = [
    TableSpec(
        "dim_date", "dimension", "one calendar day",
        "Conformed date dimension spanning all transactional data.",
        "generated",
        [
            ColumnSpec("date_key", "INTEGER", "Surrogate key YYYYMMDD",
                       "Join key for all dated facts", nullable=False, is_key=True),
            ColumnSpec("date", "DATE", "Calendar date", nullable=False),
            ColumnSpec("financial_year", "TEXT", "Indian FY label (Apr–Mar), e.g. 25-26"),
            ColumnSpec("year", "INTEGER", "Calendar year"),
            ColumnSpec("month", "INTEGER", "Calendar month 1–12"),
            ColumnSpec("month_name", "TEXT", "Month name"),
            ColumnSpec("quarter", "INTEGER", "Calendar quarter 1–4"),
            ColumnSpec("fy_month_no", "INTEGER", "Month number within FY (Apr=1)"),
            ColumnSpec("is_month_end", "INTEGER", "1 if last day of month"),
        ],
    ),
    TableSpec(
        "dim_customer", "dimension", "one customer",
        "Customers, resolved from transaction names to master where possible.",
        "Masters/Customer_Master + resolved transaction names",
        [
            ColumnSpec("customer_key", "INTEGER", "Surrogate key", nullable=False, is_key=True),
            ColumnSpec("customer_code", "TEXT", "Anonymous code (shareable) / name (internal)",
                       "Customer identity; anonymised in shareable mode", nullable=False),
            ColumnSpec("source_id", "TEXT", "ERP stable id if exposed (else null)",
                       "Tier-1 key source for future auto-adoption", source_column="ie_code"),
            ColumnSpec("area_key", "INTEGER", "FK to dim_territory", is_fk="dim_territory"),
            ColumnSpec("trade_type", "TEXT", "Cash/Credit trade type", source_column="trade_type"),
            ColumnSpec("discount_pct", "REAL", "Default discount %", source_column="discount_pct"),
            ColumnSpec("match_tier", "TEXT", "source_id | master_exact | master_fuzzy | unresolved",
                       "Which resolution tier produced this customer"),
            ColumnSpec("match_confidence", "REAL", "0–1 confidence of name match",
                       "Entity-resolution confidence; 1.0 for exact/source_id"),
        ],
        relationships=["dim_customer.area_key -> dim_territory.area_key"],
    ),
    TableSpec(
        "dim_supplier", "dimension", "one supplier",
        "Suppliers (100% exact-match to master).",
        "Masters/Supplier_Master",
        [
            ColumnSpec("supplier_key", "INTEGER", "Surrogate key", nullable=False, is_key=True),
            ColumnSpec("supplier_code", "TEXT", "Anonymous code / name", nullable=False),
            ColumnSpec("source_id", "TEXT", "ERP stable id if exposed"),
            ColumnSpec("discount_pct", "REAL", "Default discount %", source_column="discount_pct"),
        ],
    ),
    TableSpec(
        "dim_product", "dimension", "one product",
        "Products (100% exact-match to master).",
        "Masters/Product_Master",
        [
            ColumnSpec("product_key", "INTEGER", "Surrogate key", nullable=False, is_key=True),
            ColumnSpec("product_code", "TEXT", "Product name/code (pharma brand — not PII)",
                       nullable=False),
            ColumnSpec("company_key", "INTEGER", "FK to dim_company", is_fk="dim_company"),
            ColumnSpec("unit", "TEXT", "Pack/unit", source_column="unit"),
            ColumnSpec("tax_pct", "REAL", "GST %", source_column="tax_pct"),
            ColumnSpec("reorder_level", "REAL", "Reorder level", source_column="reorder_level"),
        ],
        relationships=["dim_product.company_key -> dim_company.company_key"],
    ),
    TableSpec(
        "dim_company", "dimension", "one manufacturer",
        "Pharma manufacturers / principal companies.",
        "Masters/Company_Master",
        [
            ColumnSpec("company_key", "INTEGER", "Surrogate key", nullable=False, is_key=True),
            ColumnSpec("company_code", "TEXT", "Company name/code", nullable=False),
            ColumnSpec("short_name", "TEXT", "Short name", source_column="short_name"),
        ],
    ),
    TableSpec(
        "dim_salesman", "dimension", "one salesman",
        "Sales representatives.",
        "Masters/Salesman_Master",
        [
            ColumnSpec("salesman_key", "INTEGER", "Surrogate key", nullable=False, is_key=True),
            ColumnSpec("salesman_code", "TEXT", "Anonymous code / name", nullable=False),
        ],
    ),
    TableSpec(
        "dim_territory", "dimension", "one area (with its zone)",
        "Geographic hierarchy: area within zone.",
        "Masters/Area_List + Masters/Zone_List",
        [
            ColumnSpec("area_key", "INTEGER", "Surrogate key", nullable=False, is_key=True),
            ColumnSpec("area_name", "TEXT", "Area / town", nullable=False, source_column="area_name"),
            ColumnSpec("zone_name", "TEXT", "Zone", source_column="zone_name"),
        ],
    ),
]

# --------------------------------------------------------------------------- #
# FACTS
# --------------------------------------------------------------------------- #
_FACTS = [
    TableSpec(
        "fact_sales", "fact", "one sales bill (header)",
        "Sales bills enriched with cost/profit from the profit register.",
        "Sales/Sales ⋈ Profit/Profit_AllBills on (financial_year, voucher_no)",
        [
            ColumnSpec("date_key", "INTEGER", "FK to dim_date", is_fk="dim_date"),
            ColumnSpec("customer_key", "INTEGER", "FK to dim_customer", is_fk="dim_customer"),
            ColumnSpec("voucher_no", "TEXT", "ERP voucher number", is_key=True,
                       source_column="voucher_no"),
            ColumnSpec("financial_year", "TEXT", "Financial year", is_key=True),
            _money("net_amount_inr", "Net sale (post return/scheme), INR", "net_amount", kpi=True),
            _money("billed_amount_inr", "Gross billed amount, INR", "sale_billed_amount"),
            _money("cost_amount_inr", "Cost of goods, INR", "cost_amount"),
            _money("profit_amount_inr", "Gross profit, INR", "profit_amount", kpi=True),
            ColumnSpec("profit_pct", "REAL", "Profit % (reference)", source_column="profit_pct"),
        ],
    ),
    TableSpec(
        "fact_purchases", "fact", "one purchase bill (header)",
        "Purchase bills by supplier.",
        "Purchases/Purchase_Report",
        [
            ColumnSpec("date_key", "INTEGER", "FK to dim_date", is_fk="dim_date"),
            ColumnSpec("supplier_key", "INTEGER", "FK to dim_supplier", is_fk="dim_supplier"),
            ColumnSpec("voucher_no", "TEXT", "ERP voucher number", is_key=True),
            ColumnSpec("bill_no", "TEXT", "Supplier bill number", source_column="bill_no"),
            ColumnSpec("financial_year", "TEXT", "Financial year", is_key=True),
            _money("net_amount_inr", "Net purchase amount, INR", "net_amount", kpi=True),
        ],
    ),
    TableSpec(
        "fact_sales_product", "fact", "one product per financial year",
        "Annual product sales totals (no customer/bill — see data_model.md §2).",
        "Sales/Sales_ProductWise",
        [
            ColumnSpec("product_key", "INTEGER", "FK to dim_product", is_fk="dim_product"),
            ColumnSpec("financial_year", "TEXT", "Financial year", is_key=True),
            ColumnSpec("quantity", "REAL", "Units sold", source_column="quantity", kpi=True),
            ColumnSpec("scheme_qty", "REAL", "Scheme units", source_column="scheme_qty"),
            _money("sale_amount_inr", "Sales value, INR", "sale_amount", kpi=True),
            _money("scheme_value_inr", "Scheme value, INR", "scheme_value"),
        ],
    ),
    TableSpec(
        "fact_purchase_product", "fact", "one product per financial year",
        "Annual product purchase details.",
        "Purchases/Purchase_ProductDetails",
        [
            ColumnSpec("product_key", "INTEGER", "FK to dim_product", is_fk="dim_product"),
            ColumnSpec("financial_year", "TEXT", "Financial year", is_key=True),
            ColumnSpec("quantity", "REAL", "Units purchased", source_column="quantity"),
            ColumnSpec("scheme_qty", "REAL", "Scheme units", source_column="scheme_qty"),
            _money("purchase_amount_inr", "Purchase value, INR", "purchase_amount", kpi=True),
            _money("purchase_rate_inr", "Purchase rate, INR", "purchase_rate"),
            _money("sale_rate_inr", "Sale rate, INR", "sale_rate"),
            _money("mrp_inr", "MRP, INR", "mrp"),
        ],
    ),
    TableSpec(
        "fact_product_profit", "fact", "one product per financial year",
        "Annual product profitability.",
        "Profit/Profit_ProductWise",
        [
            ColumnSpec("product_key", "INTEGER", "FK to dim_product", is_fk="dim_product"),
            ColumnSpec("financial_year", "TEXT", "Financial year", is_key=True),
            ColumnSpec("quantity", "REAL", "Units", source_column="quantity"),
            _money("billed_amount_inr", "Billed amount, INR", "sale_billed_amount"),
            _money("cost_amount_inr", "Cost, INR", "cost_amount"),
            _money("profit_amount_inr", "Profit, INR", "profit_amount", kpi=True),
            ColumnSpec("profit_pct", "REAL", "Profit %", source_column="profit_pct"),
        ],
    ),
    TableSpec(
        "fact_stock_snapshot", "fact", "one product at period end",
        "Closing stock valuation by product.",
        "Stock/Stock_ProductWise",
        [
            ColumnSpec("product_key", "INTEGER", "FK to dim_product", is_fk="dim_product"),
            ColumnSpec("financial_year", "TEXT", "Snapshot financial year", is_key=True),
            ColumnSpec("quantity", "REAL", "Units in stock", source_column="quantity"),
            _money("rate_inr", "Valuation rate, INR", "rate"),
            _money("value_inr", "Stock value, INR", "value", kpi=True),
        ],
    ),
    TableSpec(
        "fact_stock_movement", "fact", "one company per financial year",
        "Stock in/out movement summary by manufacturer.",
        "Stock/Stock_InOutSummary",
        [
            ColumnSpec("company_key", "INTEGER", "FK to dim_company", is_fk="dim_company"),
            ColumnSpec("financial_year", "TEXT", "Financial year", is_key=True),
            _money("opening_value_inr", "Opening stock value, INR", "opening_value"),
            _money("stock_in_value_inr", "Stock-in value, INR", "stock_in_value"),
            _money("stock_out_value_inr", "Stock-out value, INR", "stock_out_value"),
            _money("closing_value_inr", "Closing stock value, INR", "closing_value"),
        ],
    ),
    TableSpec(
        "fact_ar_outstanding", "fact", "one open receivable bill",
        "Accounts receivable — open customer bills with ageing.",
        "Outstanding/Outstanding_BillWise",
        [
            ColumnSpec("customer_key", "INTEGER", "FK to dim_customer", is_fk="dim_customer"),
            ColumnSpec("bill_date_key", "INTEGER", "FK to dim_date (bill date)", is_fk="dim_date"),
            ColumnSpec("bill_no", "TEXT", "Bill number", is_key=True, source_column="bill_no"),
            ColumnSpec("financial_year", "TEXT", "Financial year", is_key=True),
            _money("bill_amount_inr", "Bill amount, INR", "bill_amount"),
            _money("balance_amount_inr", "Outstanding balance, INR", "balance_amount", kpi=True),
            ColumnSpec("overdue_days", "REAL", "Days overdue", source_column="overdue_days"),
        ],
    ),
    TableSpec(
        "fact_ap_outstanding", "fact", "one open payable bill",
        "Accounts payable — open supplier bills with ageing buckets.",
        "Outstanding/Payables_Ageing_BillWise",
        [
            ColumnSpec("supplier_key", "INTEGER", "FK to dim_supplier", is_fk="dim_supplier"),
            ColumnSpec("bill_date_key", "INTEGER", "FK to dim_date (bill date)", is_fk="dim_date"),
            ColumnSpec("bill_no", "TEXT", "Bill number", is_key=True, source_column="bill_no"),
            ColumnSpec("financial_year", "TEXT", "Financial year", is_key=True),
            _money("bill_amount_inr", "Bill amount, INR", "bill_amount"),
            _money("balance_amount_inr", "Outstanding balance, INR", "balance_amount", kpi=True),
            ColumnSpec("overdue_days", "REAL", "Days overdue", source_column="overdue_days"),
            _money("ageing_0_30_inr", "Ageing 0–30 days, INR", "ageing_0_30"),
            _money("ageing_31_60_inr", "Ageing 31–60 days, INR", "ageing_31_60"),
            _money("ageing_61_90_inr", "Ageing 61–90 days, INR", "ageing_61_90"),
            _money("ageing_91_120_inr", "Ageing 91–120 days, INR", "ageing_91_120"),
            _money("ageing_120_plus_inr", "Ageing >120 days, INR", "ageing_120_plus"),
        ],
    ),
    TableSpec(
        "fact_price_change", "fact", "one price-change line",
        "PTR/MRP/scheme price-change events on purchase vouchers.",
        "Purchases/PTR_Changed_Purchase",
        [
            ColumnSpec("product_key", "INTEGER", "FK to dim_product", is_fk="dim_product"),
            ColumnSpec("date_key", "INTEGER", "FK to dim_date", is_fk="dim_date"),
            ColumnSpec("voucher_no", "TEXT", "Voucher number", source_column="voucher_no"),
            ColumnSpec("financial_year", "TEXT", "Financial year", is_key=True),
            _money("prev_ptr_inr", "Previous PTR, INR", "prev_ptr"),
            _money("new_ptr_inr", "New PTR, INR", "new_ptr"),
            _money("prev_mrp_inr", "Previous MRP, INR", "prev_mrp"),
            _money("new_mrp_inr", "New MRP, INR", "new_mrp"),
        ],
    ),
]

# --------------------------------------------------------------------------- #
# META
# --------------------------------------------------------------------------- #
_META = [
    TableSpec(
        "meta_import_batch", "meta", "one warehouse build run",
        "Audit log of every warehouse build (lineage anchor for import_batch_id).",
        "pipeline",
        [
            ColumnSpec("import_batch_id", "INTEGER", "Batch id", nullable=False, is_key=True),
            ColumnSpec("started_at", "TIMESTAMP", "Build start (UTC)"),
            ColumnSpec("finished_at", "TIMESTAMP", "Build end (UTC)"),
            ColumnSpec("mode", "TEXT", "internal | shareable"),
            ColumnSpec("reporting_currency", "TEXT", "Currency requested at build time"),
            ColumnSpec("status", "TEXT", "running | success | failed"),
            ColumnSpec("n_tables", "INTEGER", "Tables written"),
            ColumnSpec("n_rows", "INTEGER", "Total rows written"),
            ColumnSpec("git_commit", "TEXT", "Code version, if available"),
            ColumnSpec("notes", "TEXT", "Free-text notes"),
        ],
    ),
]

# --------------------------------------------------------------------------- #
# FUTURE extension points (declared, not built — backward-compatible by design)
# --------------------------------------------------------------------------- #
_FUTURE = [
    TableSpec(
        "fact_sales_line", "fact", "one product line within a sales bill",
        "FUTURE: line-level sales (bill × product). Unlocks customer×product "
        "analysis. Build only when the ERP exports a sales register with line "
        "items. Keys off existing dims — no dimension/KPI/dashboard redesign.",
        "FUTURE: Sales register with line items",
        [
            ColumnSpec("date_key", "INTEGER", "FK to dim_date", is_fk="dim_date"),
            ColumnSpec("customer_key", "INTEGER", "FK to dim_customer", is_fk="dim_customer"),
            ColumnSpec("product_key", "INTEGER", "FK to dim_product", is_fk="dim_product"),
            ColumnSpec("voucher_no", "TEXT", "Voucher number", is_key=True),
            ColumnSpec("financial_year", "TEXT", "Financial year", is_key=True),
            ColumnSpec("quantity", "REAL", "Units"),
            _money("line_amount_inr", "Line amount, INR"),
        ],
        build_now=False,
    ),
    TableSpec(
        "fact_purchase_line", "fact", "one product line within a purchase bill",
        "FUTURE: line-level purchases (bill × product). Build only when the ERP "
        "exports a purchase register with line items. Backward-compatible.",
        "FUTURE: Purchase register with line items",
        [
            ColumnSpec("date_key", "INTEGER", "FK to dim_date", is_fk="dim_date"),
            ColumnSpec("supplier_key", "INTEGER", "FK to dim_supplier", is_fk="dim_supplier"),
            ColumnSpec("product_key", "INTEGER", "FK to dim_product", is_fk="dim_product"),
            ColumnSpec("voucher_no", "TEXT", "Voucher number", is_key=True),
            ColumnSpec("financial_year", "TEXT", "Financial year", is_key=True),
            ColumnSpec("quantity", "REAL", "Units"),
            _money("line_amount_inr", "Line amount, INR"),
        ],
        build_now=False,
    ),
]

SCHEMA: list[TableSpec] = _DIMENSIONS + _FACTS + _META + _FUTURE


def get_table(name: str) -> TableSpec:
    for t in SCHEMA:
        if t.name == name:
            return t
    raise KeyError(name)


def buildable_tables() -> list[TableSpec]:
    return [t for t in SCHEMA if t.build_now]


_SQLA_TYPE = {"INTEGER": "Integer", "REAL": "Float", "TEXT": "String",
              "DATE": "Date", "TIMESTAMP": "DateTime"}
