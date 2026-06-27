"""Central KPI registry — the single source of truth for every business KPI.

Each KPI declares its unit, business description, direction, and the scoring
anchors (the value that scores 100 = `good`, the value that scores 0 = `bad`).
The same anchors drive KPI health scores, scorecards, and the Business Health
Index, so thresholds are defined once and used everywhere.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class KPISpec:
    key: str
    domain: str
    label: str
    unit: str                      # ₹ | % | days | x | count
    description: str
    direction: str = "up_good"     # up_good | down_good | neutral
    good: float | None = None      # value that scores 100
    bad: float | None = None       # value that scores 0
    fmt: str = "{:,.0f}"

    def format(self, value) -> str:
        if value is None:
            return "—"
        try:
            s = self.fmt.format(value)
        except Exception:
            s = str(value)
        return {"₹": f"₹{s}", "%": f"{s}%", "days": f"{s} days",
                "x": f"{s}x"}.get(self.unit, s)

    def score(self, value) -> float | None:
        """Map a value to 0-100 using the good/bad anchors (clamped)."""
        if value is None or self.direction == "neutral" or self.good is None or self.bad is None:
            return None
        if self.direction == "up_good":
            s = 100.0 * (value - self.bad) / (self.good - self.bad)
        else:  # down_good (bad > good)
            s = 100.0 * (self.bad - value) / (self.bad - self.good)
        return round(max(0.0, min(100.0, s)), 1)


def _k(*a, **kw) -> KPISpec:
    return KPISpec(*a, **kw)


# --------------------------------------------------------------------------- #
# Registry — grouped by domain. Anchors tuned for Indian pharma distribution
# (thin margins, cash-heavy retail).
# --------------------------------------------------------------------------- #
REGISTRY: dict[str, KPISpec] = {s.key: s for s in [
    # ---- Sales ----
    _k("revenue_inr", "sales", "Revenue", "₹",
       "Total net sales for the year", "up_good"),
    _k("revenue_growth_pct", "sales", "Revenue growth (YoY)", "%",
       "Year-on-year change in net sales", "up_good", good=12, bad=-8, fmt="{:+,.1f}"),
    _k("avg_bill_value", "sales", "Average bill value", "₹",
       "Net sales divided by number of bills", "up_good", fmt="{:,.0f}"),
    _k("bill_count", "sales", "Bills", "count",
       "Number of sales bills", "up_good"),

    # ---- Profitability ----
    _k("gross_margin_pct", "profitability", "Gross margin", "%",
       "Gross profit as % of billed sales", "up_good", good=6, bad=3, fmt="{:,.2f}"),
    _k("gross_profit_inr", "profitability", "Gross profit", "₹",
       "Billed sales minus cost of goods", "up_good"),
    _k("profit_growth_pct", "profitability", "Profit growth (YoY)", "%",
       "Year-on-year change in gross profit", "up_good", good=12, bad=-8, fmt="{:+,.1f}"),

    # ---- Customers ----
    _k("active_customers", "customers", "Active customers", "count",
       "Customers with at least one bill this year", "up_good"),
    _k("top10_customer_share_pct", "customers", "Top-10 customer concentration", "%",
       "Share of revenue from the 10 largest customers", "down_good",
       good=20, bad=45, fmt="{:,.1f}"),
    _k("customer_retention_pct", "customers", "Customer retention", "%",
       "Customers active last year who are still active", "up_good",
       good=85, bad=55, fmt="{:,.1f}"),

    # ---- Products ----
    _k("active_products", "products", "Active products", "count",
       "Products sold this year", "up_good"),
    _k("top10_product_share_pct", "products", "Top-10 product concentration", "%",
       "Share of revenue from the 10 largest products", "down_good",
       good=25, bad=55, fmt="{:,.1f}"),

    # ---- Suppliers ----
    _k("active_suppliers", "suppliers", "Active suppliers", "count",
       "Suppliers purchased from this year", "up_good"),
    _k("top5_supplier_share_pct", "suppliers", "Top-5 supplier dependency", "%",
       "Share of purchases from the 5 largest suppliers", "down_good",
       good=40, bad=75, fmt="{:,.1f}"),

    # ---- Inventory ----
    _k("inventory_value_inr", "inventory", "Closing inventory value", "₹",
       "Valuation of closing stock", "neutral"),
    _k("inventory_turnover", "inventory", "Inventory turnover", "x",
       "Cost of goods sold / closing inventory", "up_good", good=9, bad=4, fmt="{:,.1f}"),
    _k("inventory_days", "inventory", "Inventory days", "days",
       "Days of stock on hand (365 / turnover)", "down_good", good=40, bad=90, fmt="{:,.0f}"),

    # ---- Working capital ----
    _k("debtor_days", "working_capital", "Debtor days", "days",
       "Receivables / sales × 365 — how fast customers pay", "down_good",
       good=15, bad=60, fmt="{:,.0f}"),
    _k("creditor_days", "working_capital", "Creditor days", "days",
       "Payables / purchases × 365 — how long we take to pay", "neutral", fmt="{:,.0f}"),
    _k("ccc_days", "working_capital", "Cash conversion cycle", "days",
       "Debtor days + inventory days − creditor days", "down_good",
       good=20, bad=75, fmt="{:,.0f}"),

    # ---- Cash flow ----
    _k("operating_cash_proxy_inr", "cash_flow", "Operating cash proxy", "₹",
       "Gross profit − increase in working capital (approximation)", "up_good"),
    _k("operating_cash_margin_pct", "cash_flow", "Operating cash margin", "%",
       "Operating cash proxy as % of revenue", "up_good", good=5, bad=0, fmt="{:,.2f}"),

    # ---- Territory ----
    _k("active_territories", "territory", "Active territories", "count",
       "Areas with sales activity", "up_good"),
    _k("top5_territory_share_pct", "territory", "Top-5 territory concentration", "%",
       "Share of sales from the 5 largest areas", "down_good",
       good=45, bad=80, fmt="{:,.1f}"),
]}


def get_spec(key: str) -> KPISpec:
    return REGISTRY[key]


def by_domain(domain: str) -> list[KPISpec]:
    return [s for s in REGISTRY.values() if s.domain == domain]


def score(key: str, value) -> float | None:
    return REGISTRY[key].score(value) if key in REGISTRY else None
