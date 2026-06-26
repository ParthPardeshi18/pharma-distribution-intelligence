"""Warehouse integrity tests against the last build.

These do NOT rebuild (slow); they verify the most recent build's artifacts:
reconciliation passed and there are zero orphan keys. Skipped if no build has
been run yet (e.g. fresh checkout) so the suite stays green without raw data.
"""
import json

import pytest

from src.utils import LOGS_DIR
from src.warehouse.db import DB_PATH, make_engine

_LOG = LOGS_DIR / "last_build.json"


@pytest.mark.skipif(not _LOG.exists(), reason="no build yet")
def test_last_build_reconciled():
    summary = json.loads(_LOG.read_text(encoding="utf-8"))
    recon = summary.get("reconciliation", [])
    assert recon, "no reconciliation recorded"
    failed = [c for c in recon if c["status"] != "PASS"]
    assert not failed, f"reconciliation failures: {failed}"


@pytest.mark.skipif(not DB_PATH.exists(), reason="no warehouse db yet")
def test_no_orphan_keys():
    from src.warehouse import metrics
    engine = make_engine()
    orph = metrics.orphans(engine)
    offenders = [(o["table"], o["fk"], o["orphan_keys"])
                 for o in orph if o["orphan_keys"] > 0]
    assert not offenders, f"orphan keys present: {offenders}"


@pytest.mark.skipif(not DB_PATH.exists(), reason="no warehouse db yet")
def test_keys_are_float64_safe():
    """Every surrogate key must be < 2**53 so float64 coercion stays exact."""
    import pandas as pd
    engine = make_engine()
    for tbl, key in [("dim_customer", "customer_key"), ("dim_product", "product_key"),
                     ("dim_supplier", "supplier_key")]:
        ks = pd.read_sql(f'SELECT MAX("{key}") AS m FROM "{tbl}"', engine)["m"].iloc[0]
        assert ks is None or ks < 2 ** 53
