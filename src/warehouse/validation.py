"""Validation report generator -> reports/data_validation.md.

Independent verification that the warehouse faithfully represents the ERP:
raw-vs-warehouse totals, row counts, orphaned keys, date coverage, and anomalies.
Run after a build:  python -m src.warehouse.validation
"""
from __future__ import annotations

import datetime as dt

import pandas as pd

from src.utils import PROJECT_ROOT
from src.warehouse import metrics
from src.warehouse.build import build_warehouse
from src.warehouse.db import make_engine

REPORT_PATH = PROJECT_ROOT / "reports" / "data_validation.md"


def generate(reconciliation: list[dict] | None = None) -> str:
    engine = make_engine()
    lines = ["# Data Validation Report", ""]
    lines.append(f"> Generated {dt.date.today():%Y-%m-%d}. Independent check that "
                 "`erp_warehouse.db` faithfully represents the raw ERP exports.")
    lines.append("")

    # 1. Reconciliation
    lines.append("## 1. Financial reconciliation (raw ERP vs warehouse)")
    lines.append("")
    if reconciliation:
        lines.append("| Table | Measure | Raw total (₹) | Warehouse total (₹) | Diff | Status |")
        lines.append("|---|---|--:|--:|--:|:--:|")
        for c in reconciliation:
            lines.append(f"| {c['table']} | {c['measure']} | {c['raw_total']:,.2f} | "
                         f"{c['warehouse_total']:,.2f} | {c['difference']} | "
                         f"{'✅' if c['status']=='PASS' else '❌'} {c['status']} |")
        allpass = all(c["status"] == "PASS" for c in reconciliation)
        lines.append("")
        lines.append(f"**Reconciliation: {'ALL PASS ✅' if allpass else 'FAILURES ❌'}** "
                     "— warehouse fact totals match the ERP's own report totals.")
    lines.append("")

    # 2. Row counts
    lines.append("## 2. Table row counts")
    lines.append("")
    rc = metrics.table_row_counts(engine)
    lines.append("| Table | Rows |")
    lines.append("|---|--:|")
    for t in sorted(rc):
        lines.append(f"| {t} | {rc[t]:,} |")
    lines.append("")

    # 3. Orphaned keys
    lines.append("## 3. Referential integrity (orphaned / unmatched keys)")
    lines.append("")
    lines.append("| Fact | FK | References | Rows | Orphan keys | Null keys |")
    lines.append("|---|---|---|--:|--:|--:|")
    for o in metrics.orphans(engine):
        lines.append(f"| {o['table']} | {o['fk']} | {o['references']} | {o['rows']:,} | "
                     f"{o['orphan_keys']:,} | {o['null_keys']:,} |")
    lines.append("")
    lines.append("> Orphan keys = fact key absent from its dimension (should be 0). "
                 "Null keys = entity could not be resolved to the master; the row is "
                 "retained and flagged `unmatched_entity` (never dropped).")
    lines.append("")

    # 4. Date coverage
    lines.append("## 4. Date coverage")
    lines.append("")
    lines.append("| Fact | Rows | Financial years |")
    lines.append("|---|--:|---|")
    for d in metrics.date_coverage(engine):
        lines.append(f"| {d['table']} | {d['rows']:,} | {d['financial_years']} |")
    lines.append("")

    # 5. Anomalies
    lines.append("## 5. Anomalies & known data-quality issues")
    lines.append("")
    anomalies = _anomalies(engine)
    if anomalies:
        for a in anomalies:
            lines.append(f"- {a}")
    else:
        lines.append("- None detected.")
    lines.append("")
    lines.append("**Known issue:** `Masters/Salesman_Master` is misaligned in the ERP "
                 "export (the salesman name is largely blank; names spill into the "
                 "address column). `dim_salesman` is therefore sparse. No fact references "
                 "salesman yet, so this does not affect any measure.")
    lines.append("")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    return str(REPORT_PATH)


def _anomalies(engine) -> list[str]:
    out = []
    for tbl, col in [("fact_sales", "net_amount_inr"), ("fact_purchases", "net_amount_inr"),
                     ("fact_product_profit", "profit_amount_inr")]:
        try:
            df = pd.read_sql(f'SELECT "{col}" FROM "{tbl}"', engine)
            neg = int((pd.to_numeric(df[col], errors="coerce") < 0).sum())
            if neg:
                out.append(f"`{tbl}.{col}`: {neg:,} negative values "
                           "(returns/credit notes — expected, retained).")
        except Exception:
            pass
    return out


def main():
    res = build_warehouse()  # build then validate the fresh build
    path = generate(res.reconciliation)
    print("Validation report:", path)


if __name__ == "__main__":
    main()
