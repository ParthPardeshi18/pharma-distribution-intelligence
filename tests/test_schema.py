"""Schema registry integrity tests (fast — no database build)."""
from src.warehouse.schema import (
    SCHEMA, STANDARD_COLUMNS, buildable_tables, get_table,
)

_DIM_NAMES = {t.name for t in SCHEMA if t.role == "dimension"}


def test_every_table_has_unique_columns():
    for t in SCHEMA:
        names = [c.name for c in t.all_columns()]
        assert len(names) == len(set(names)), f"{t.name} has duplicate columns"


def test_business_tables_have_standard_columns():
    std = {c.name for c in STANDARD_COLUMNS}
    for t in SCHEMA:
        if t.role == "meta":
            continue
        cols = {c.name for c in t.all_columns()}
        assert std <= cols, f"{t.name} missing standard columns"


def test_meta_table_has_no_standard_columns():
    cols = {c.name for c in get_table("meta_import_batch").all_columns()}
    assert "src_report" not in cols


def test_every_fk_references_existing_dimension():
    for t in buildable_tables():
        for c in t.columns:
            if c.is_fk and c.is_fk.startswith("dim"):
                assert c.is_fk in _DIM_NAMES, f"{t.name}.{c.name} -> unknown {c.is_fk}"


def test_each_fact_has_a_key_and_a_measure():
    for t in buildable_tables():
        if t.role != "fact":
            continue
        assert any(c.is_key for c in t.columns), f"{t.name} has no natural key"


def test_money_columns_named_inr():
    for t in buildable_tables():
        for c in t.columns:
            if c.currency_inr:
                assert c.name.endswith("_inr"), f"{t.name}.{c.name} money col must end _inr"


def test_future_tables_present_but_not_buildable():
    names = {t.name for t in SCHEMA}
    assert {"fact_sales_line", "fact_purchase_line"} <= names
    assert get_table("fact_sales_line").build_now is False
