"""Physical SQLite schema, materialised from the schema registry.

Tables, columns, and indices are generated from `SCHEMA` (schema.py) so the
database structure can never drift from the documentation generated alongside it.
"""
from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import (
    Column, Date, DateTime, Float, Integer, MetaData, String, Table, create_engine, text,
)

from src.utils import WAREHOUSE_DIR
from src.warehouse.schema import SCHEMA, buildable_tables

_TYPE = {"INTEGER": Integer, "REAL": Float, "TEXT": String,
         "DATE": Date, "TIMESTAMP": DateTime}

# Per-mode physical databases. Surrogate keys are IDENTICAL across modes (see
# build.py), so the same engines/queries work unchanged on either file:
#   internal  → real customer/supplier/salesman names
#   shareable → stable anonymous codes (Customer_0001 …); safe to publish
_DB_NAMES = {"internal": "erp_warehouse.db", "shareable": "erp_warehouse_shareable.db"}

# Back-compat: the historical default path (internal mode).
DB_PATH = WAREHOUSE_DIR / _DB_NAMES["internal"]


def current_db_path(mode: str | None = None) -> Path:
    """Resolve the active warehouse file.

    Precedence: explicit ``mode`` arg → ``ERP_WAREHOUSE_DB`` (full-path override)
    → ``ERP_WAREHOUSE_MODE`` env → internal default. This is the single switch the
    app flips so the *public* build reads anonymised data without any engine code
    needing to know about modes.
    """
    if mode is None:
        explicit = os.environ.get("ERP_WAREHOUSE_DB")
        if explicit:
            return Path(explicit)
        mode = os.environ.get("ERP_WAREHOUSE_MODE", "internal")
    return WAREHOUSE_DIR / _DB_NAMES.get(mode, _DB_NAMES["internal"])


def make_engine(db_path=None, echo: bool = False):
    WAREHOUSE_DIR.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{db_path or current_db_path()}", echo=echo, future=True)


def build_metadata() -> MetaData:
    md = MetaData()
    for tspec in SCHEMA:
        if not tspec.build_now:
            continue  # future extension points are not physically created
        cols = [Column(c.name, _TYPE.get(c.sqltype, String),
                       primary_key=False, nullable=c.nullable)
                for c in tspec.all_columns()]
        Table(tspec.name, md, *cols)
    return md


def create_all(engine, drop_first: bool = True) -> None:
    md = build_metadata()
    if drop_first:
        md.drop_all(engine)
    md.create_all(engine)
    # helpful indices on every *_key and date_key column
    with engine.begin() as conn:
        for tspec in buildable_tables():
            for c in tspec.all_columns():
                if c.name.endswith("_key"):
                    idx = f"ix_{tspec.name}_{c.name}"
                    conn.execute(text(
                        f'CREATE INDEX IF NOT EXISTS "{idx}" '
                        f'ON "{tspec.name}" ("{c.name}")'))
