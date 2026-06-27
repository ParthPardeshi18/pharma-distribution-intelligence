"""Read-only analytics API over the warehouse.

A thin, well-named query layer so domain analyzers never write SQL inline. All
amounts are INR (warehouse source of truth); the currency layer converts only at
presentation time. Results are cached per process for speed.
"""
from __future__ import annotations

from functools import lru_cache

import pandas as pd

from src.warehouse.db import make_engine

# Financial years present, ordered. Current = latest complete FY.
FYS = ["22-23", "23-24", "24-25", "25-26"]
CURRENT_FY = "25-26"
PRIOR_FY = "24-25"


def _eng():
    return make_engine()


def q(sql: str) -> pd.DataFrame:
    return pd.read_sql(sql, _eng())


# --------------------------- Sales / profit ------------------------------- #
@lru_cache(maxsize=1)
def sales_by_fy() -> pd.DataFrame:
    return q("""SELECT financial_year AS fy,
                       COUNT(*) AS bills,
                       SUM(net_amount_inr) AS revenue,
                       SUM(billed_amount_inr) AS billed,
                       SUM(cost_amount_inr) AS cost,
                       SUM(profit_amount_inr) AS profit
                FROM fact_sales GROUP BY 1 ORDER BY 1""")


@lru_cache(maxsize=1)
def purchases_by_fy() -> pd.DataFrame:
    return q("""SELECT financial_year AS fy, COUNT(*) AS bills,
                       SUM(net_amount_inr) AS purchases
                FROM fact_purchases GROUP BY 1 ORDER BY 1""")


def sales_by_customer(fy: str) -> pd.DataFrame:
    return q(f"""SELECT s.customer_key, c.customer_code,
                        SUM(s.net_amount_inr) AS revenue,
                        SUM(s.profit_amount_inr) AS profit, COUNT(*) AS bills
                 FROM fact_sales s LEFT JOIN dim_customer c
                   ON s.customer_key=c.customer_key
                 WHERE s.financial_year='{fy}' AND s.customer_key IS NOT NULL
                 GROUP BY 1,2 ORDER BY revenue DESC""")


def customer_orders() -> pd.DataFrame:
    """One row per (customer, order date) across all years — for recency/frequency
    churn analysis. date_key (YYYYMMDD) is converted to a real date."""
    df = q("""SELECT customer_key, date_key, SUM(net_amount_inr) AS amount
              FROM fact_sales
              WHERE customer_key IS NOT NULL AND date_key IS NOT NULL
              GROUP BY customer_key, date_key""")
    df["order_date"] = pd.to_datetime(df["date_key"].astype(int).astype(str),
                                      format="%Y%m%d")
    return df


def customers_active(fy: str) -> set:
    df = q(f"""SELECT DISTINCT customer_key FROM fact_sales
               WHERE financial_year='{fy}' AND customer_key IS NOT NULL""")
    return set(df["customer_key"])


def product_perf(fy: str) -> pd.DataFrame:
    return q(f"""SELECT p.product_key, d.product_code,
                        SUM(p.sale_amount_inr) AS revenue, SUM(p.quantity) AS qty
                 FROM fact_sales_product p LEFT JOIN dim_product d
                   ON p.product_key=d.product_key
                 WHERE p.financial_year='{fy}' GROUP BY 1,2 ORDER BY revenue DESC""")


def product_profit(fy: str) -> pd.DataFrame:
    return q(f"""SELECT product_key,
                        SUM(billed_amount_inr) AS billed, SUM(cost_amount_inr) AS cost,
                        SUM(profit_amount_inr) AS profit, SUM(quantity) AS qty
                 FROM fact_product_profit
                 WHERE financial_year='{fy}' GROUP BY 1""")


def purchases_by_supplier(fy: str) -> pd.DataFrame:
    return q(f"""SELECT s.supplier_key, d.supplier_code,
                        SUM(s.net_amount_inr) AS spend, COUNT(*) AS bills
                 FROM fact_purchases s LEFT JOIN dim_supplier d
                   ON s.supplier_key=d.supplier_key
                 WHERE s.financial_year='{fy}' AND s.supplier_key IS NOT NULL
                 GROUP BY 1,2 ORDER BY spend DESC""")


# --------------------------- Inventory ------------------------------------ #
def inventory_value(fy: str) -> float:
    v = q(f"""SELECT SUM(value_inr) AS v FROM fact_stock_snapshot
              WHERE financial_year='{fy}'""")["v"].iloc[0]
    return float(v) if v is not None else 0.0


def stock_by_product(fy: str) -> pd.DataFrame:
    return q(f"""SELECT product_key, SUM(quantity) AS qty, SUM(value_inr) AS value
                 FROM fact_stock_snapshot WHERE financial_year='{fy}'
                 GROUP BY 1 ORDER BY value DESC""")


# --------------------------- Outstanding ---------------------------------- #
def ar_balance(fy: str) -> float:
    v = q(f"""SELECT SUM(balance_amount_inr) AS v FROM fact_ar_outstanding
              WHERE financial_year='{fy}'""")["v"].iloc[0]
    return float(v) if v is not None else 0.0


def ap_balance(fy: str) -> float:
    v = q(f"""SELECT SUM(balance_amount_inr) AS v FROM fact_ap_outstanding
              WHERE financial_year='{fy}'""")["v"].iloc[0]
    return float(v) if v is not None else 0.0


def ap_ageing(fy: str) -> dict:
    df = q(f"""SELECT
                 SUM(ageing_0_30_inr) a0, SUM(ageing_31_60_inr) a1,
                 SUM(ageing_61_90_inr) a2, SUM(ageing_91_120_inr) a3,
                 SUM(ageing_120_plus_inr) a4
               FROM fact_ap_outstanding WHERE financial_year='{fy}'""")
    r = df.iloc[0]
    return {"0-30": r.a0 or 0, "31-60": r.a1 or 0, "61-90": r.a2 or 0,
            "91-120": r.a3 or 0, "120+": r.a4 or 0}


# --------------------------- Territory ------------------------------------ #
def territory_sales(fy: str) -> pd.DataFrame:
    """Area-level sales come from the ERP Area_Sales aggregate (no clean
    customer→area key in the warehouse), loaded via the adapter."""
    from src.adapters import get_adapter
    a = get_adapter()
    try:
        d = a.load("Sales/Area_Sales", fy).data
        return d.rename(columns={"sale_amount": "revenue"})[["area_name", "revenue"]]
    except Exception:
        return pd.DataFrame(columns=["area_name", "revenue"])


# --------------------------- helpers -------------------------------------- #
def concentration_share(values: pd.Series, top_n: int) -> float:
    s = values.sort_values(ascending=False)
    total = s.sum()
    return round(100.0 * s.head(top_n).sum() / total, 1) if total else 0.0


def yoy_pct(curr, prior) -> float | None:
    if prior in (None, 0) or curr is None:
        return None
    return round(100.0 * (curr - prior) / abs(prior), 1)
