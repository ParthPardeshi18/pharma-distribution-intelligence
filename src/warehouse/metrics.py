"""Reusable warehouse metrics — shared by validation, statistics, and the DQ
dashboard so all three report the same numbers from one implementation.
"""
from __future__ import annotations

import pandas as pd
from sqlalchemy import inspect, text

from src.warehouse.db import current_db_path, make_engine
from src.warehouse.schema import buildable_tables, get_table


def read_table(engine, name) -> pd.DataFrame:
    return pd.read_sql(f'SELECT * FROM "{name}"', engine)


def table_row_counts(engine) -> dict[str, int]:
    insp = inspect(engine)
    out = {}
    for t in insp.get_table_names():
        out[t] = pd.read_sql(f'SELECT COUNT(*) AS n FROM "{t}"', engine)["n"].iloc[0]
    return out


def db_size_bytes() -> int:
    p = current_db_path()
    return p.stat().st_size if p.exists() else 0


def completeness(engine, table) -> pd.DataFrame:
    df = read_table(engine, table)
    if df.empty:
        return pd.DataFrame(columns=["column", "non_null_pct"])
    pct = (df.notna().mean() * 100).round(1)
    return pct.reset_index().rename(columns={"index": "column", 0: "non_null_pct"})


def duplicate_rate(engine, table) -> dict:
    """Duplicate rate on the table's natural/business key (is_key columns)."""
    tspec = get_table(table)
    keys = [c.name for c in tspec.columns if c.is_key]
    df = read_table(engine, table)
    if df.empty or not keys:
        return {"key": keys, "rows": len(df), "duplicates": 0, "dup_pct": 0.0}
    dups = int(df.duplicated(subset=keys).sum())
    return {"key": keys, "rows": len(df), "duplicates": dups,
            "dup_pct": round(100 * dups / max(1, len(df)), 2)}


def orphans(engine) -> list[dict]:
    """Fact FK values that have no matching dimension row."""
    dim_key = {"dim_date": "date_key", "dim_customer": "customer_key",
               "dim_supplier": "supplier_key", "dim_product": "product_key",
               "dim_company": "company_key", "dim_salesman": "salesman_key",
               "dim_territory": "area_key"}
    dim_sets = {}
    for dim, key in dim_key.items():
        try:
            dim_sets[key] = set(read_table(engine, dim)[key].dropna())
        except Exception:
            dim_sets[key] = set()
    results = []
    for tspec in buildable_tables():
        if tspec.role != "fact":
            continue
        df = read_table(engine, tspec.name)
        for c in tspec.columns:
            if c.is_fk and c.name in df.columns and c.is_fk.startswith("dim"):
                refkey = dim_key.get(c.is_fk)
                valid = dim_sets.get(refkey, set())
                vals = df[c.name].dropna()
                orph = int((~vals.isin(valid)).sum()) if len(valid) else 0
                nulls = int(df[c.name].isna().sum())
                results.append({"table": tspec.name, "fk": c.name,
                                "references": c.is_fk, "rows": len(df),
                                "orphan_keys": orph, "null_keys": nulls})
    return results


def date_coverage(engine) -> list[dict]:
    out = []
    for tspec in buildable_tables():
        if tspec.role != "fact":
            continue
        df = read_table(engine, tspec.name)
        if "financial_year" in df.columns and not df.empty:
            fys = sorted(x for x in df["financial_year"].dropna().unique())
            out.append({"table": tspec.name, "rows": len(df),
                        "financial_years": ", ".join(fys)})
    return out


def quality_status_breakdown(engine) -> pd.DataFrame:
    frames = []
    for tspec in buildable_tables():
        df = read_table(engine, tspec.name)
        if "record_quality" in df.columns and not df.empty:
            vc = df["record_quality"].value_counts()
            for status, n in vc.items():
                frames.append({"table": tspec.name, "status": status, "rows": int(n)})
    return pd.DataFrame(frames)


def latest_batch(engine) -> dict:
    try:
        df = pd.read_sql(
            "SELECT * FROM meta_import_batch ORDER BY import_batch_id DESC LIMIT 1", engine)
        return df.iloc[0].to_dict() if not df.empty else {}
    except Exception:
        return {}
