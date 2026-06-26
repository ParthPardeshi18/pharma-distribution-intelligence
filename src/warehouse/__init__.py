"""Warehouse layer: schema registry, builder, validation, statistics.

The schema registry (`schema.py`) is the SINGLE SOURCE OF TRUTH — the physical
SQLite tables, the data dictionary, and the business metadata catalog are all
generated from it, so they can never drift apart.
"""
from src.warehouse.schema import SCHEMA, STANDARD_COLUMNS, ColumnSpec, TableSpec, get_table

__all__ = ["SCHEMA", "STANDARD_COLUMNS", "ColumnSpec", "TableSpec", "get_table"]
