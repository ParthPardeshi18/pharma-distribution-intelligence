"""Export the warehouse as Power BI-ready star-schema CSVs.

internal/  — real identities (gitignored)
shareable/ — anonymised: customer/supplier/salesman codes replaced with anon
             codes, ID/PII helper columns dropped. Safe to share.

A dim_rate table (date-aware exchange rates) is included so the dashboard can
present any reporting currency from the INR model. A manifest.json records row
counts for reconciliation against the warehouse.
"""
from __future__ import annotations

import json

import pandas as pd

import re
from functools import lru_cache

from src.anonymise import load_code_map, load_lookup, normalize as anon_normalize
from src.utils import PROJECT_ROOT, WAREHOUSE_DIR
from src.warehouse.db import make_engine
from src.warehouse.metrics import read_table
from src.warehouse.schema import buildable_tables

EXPORT_ROOT = WAREHOUSE_DIR / "exports"

# Dimension code columns that are PII and must be anonymised in shareable mode.
_PII_CODE = {"dim_customer": ("customer", "customer_code"),
             "dim_supplier": ("supplier", "supplier_code"),
             "dim_salesman": ("salesman", "salesman_code")}
# Columns dropped from shareable exports: re-identifying IDs and commercial
# document references (supplier invoice numbers) that add no analytical value.
_SHAREABLE_DROP = {"source_id", "src_file", "bill_no"}


@lru_cache(maxsize=1)
def _anonymised_identity_norms() -> frozenset:
    """Normalised forms of every anonymised identity (customer/supplier/salesman).
    Used to scrub collisions where one of these names also appears as a product or
    company name (a manufacturer that is also a supplier, or a firm mis-entered in
    the product master)."""
    lk = load_lookup()
    return frozenset(lk["norm_key"].tolist())


def _shareable_clean(name: str, df: pd.DataFrame) -> pd.DataFrame:
    """Make a table safe to share: anonymise identity codes, scrub name collisions
    with anonymised entities, and drop re-identifying columns."""
    df = df.copy()
    # 1. anonymise the dimension's own PII identity code
    if name in _PII_CODE:
        entity, col = _PII_CODE[name]
        code_map = load_code_map(entity)
        df[col] = df[col].map(
            lambda v: code_map.get(anon_normalize(str(v)),
                                   f"{entity.title()}_UNMAPPED") if pd.notna(v) else v)
    # 2. companies (= manufacturers, often also suppliers) -> anonymise consistently
    if name == "dim_company":
        df["company_code"] = df["company_key"].map(lambda k: f"Company_{int(k) % 10000:04d}")
    # 3. scrub product names that collide with an anonymised identity at the WORD
    #    level (e.g. a supplier mis-entered in the product master), keeping the
    #    genuine public drug brands.
    if name == "dim_product":
        codes = df["product_code"].fillna("").astype(str)
        blob = " " + " ".join(codes).upper() + " "
        identities = [n.upper() for n in load_lookup()["real_value"].tolist()
                      if len(str(n).strip()) >= 5]
        present = [n for n in identities
                   if n in blob and re.search(rf"\b{re.escape(n)}\b", blob)]
        if present:
            pat = re.compile(r"\b(?:" + "|".join(re.escape(p) for p in present) + r")\b")
            mask = codes.str.upper().str.contains(pat)
            df.loc[mask, "product_code"] = df.loc[mask, "product_key"].map(
                lambda k: f"Product_{int(k) % 100000:05d}")
    drop = [c for c in df.columns if c in _SHAREABLE_DROP]
    return df.drop(columns=drop)


def _dim_rate() -> pd.DataFrame:
    return pd.read_csv(PROJECT_ROOT / "data" / "reference" / "exchange_rates.csv",
                       dtype={"financial_year": str})


def export_for_powerbi(mode: str = "internal") -> dict:
    assert mode in ("internal", "shareable")
    engine = make_engine()
    out_dir = EXPORT_ROOT / mode
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = {"mode": mode, "tables": {}}
    for tspec in buildable_tables():
        df = read_table(engine, tspec.name)
        if mode == "shareable":
            df = _shareable_clean(tspec.name, df)
        path = out_dir / f"{tspec.name}.csv"
        df.to_csv(path, index=False, encoding="utf-8")
        manifest["tables"][tspec.name] = len(df)

    # currency rate table for the reporting-currency slicer
    rate = _dim_rate()
    rate.to_csv(out_dir / "dim_rate.csv", index=False, encoding="utf-8")
    manifest["tables"]["dim_rate"] = len(rate)

    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def export_both() -> dict:
    return {m: export_for_powerbi(m) for m in ("internal", "shareable")}
