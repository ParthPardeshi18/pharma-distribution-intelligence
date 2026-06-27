"""Power BI export tests: completeness, reconciliation, and shareable safety."""
import pandas as pd
import pytest

from src.powerbi.exports import EXPORT_ROOT, export_for_powerbi
from src.warehouse.db import DB_PATH, make_engine
from src.warehouse.metrics import table_row_counts

_skip = pytest.mark.skipif(not DB_PATH.exists(), reason="no warehouse db")


@_skip
def test_internal_export_row_counts_match_warehouse():
    manifest = export_for_powerbi("internal")
    rc = table_row_counts(make_engine())
    for table, n in manifest["tables"].items():
        if table == "dim_rate":
            continue
        assert n == rc[table], f"{table}: export {n} != warehouse {rc[table]}"


@_skip
def test_shareable_dims_are_anonymised():
    export_for_powerbi("shareable")
    d = pd.read_csv(EXPORT_ROOT / "shareable" / "dim_customer.csv", dtype=str)
    # every customer code is an anonymous code, no real names, no source_id
    assert d["customer_code"].str.startswith("Customer_").all()
    assert "source_id" not in d.columns


@_skip
def test_shareable_drops_bill_no():
    export_for_powerbi("shareable")
    fp = pd.read_csv(EXPORT_ROOT / "shareable" / "fact_purchases.csv")
    assert "bill_no" not in fp.columns


@_skip
def test_shareable_company_codes_anonymised():
    export_for_powerbi("shareable")
    dc = pd.read_csv(EXPORT_ROOT / "shareable" / "dim_company.csv", dtype=str)
    assert dc["company_code"].str.startswith("Company_").all()


@_skip
def test_dim_rate_exported():
    export_for_powerbi("internal")
    r = pd.read_csv(EXPORT_ROOT / "internal" / "dim_rate.csv")
    assert {"financial_year", "currency", "units_per_inr"} <= set(r.columns)
    assert "INR" in set(r["currency"])
