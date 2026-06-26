"""Phase 0 ingestion tests: header detection, dedupe, malformed-file recovery."""
import pandas as pd

from src.utils import (
    RAW_DIR,
    _dedupe_columns,
    detect_header_row,
    file_needs_recovery,
    read_erp_excel,
)


def test_dedupe_columns():
    assert _dedupe_columns(["Debit", "Amount", "Credit", "Amount"]) == \
        ["Debit", "Amount", "Credit", "Amount.1"]


def test_header_detection_skips_banner():
    df = read_erp_excel(RAW_DIR / "Sales" / "Sales_25-26.xlsx")
    assert list(df.columns)[:3] == ["Date", "Vch no", "Customer name"]
    assert len(df) > 40000


def test_malformed_product_master_recovers():
    path = RAW_DIR / "Masters" / "Product_Master.xlsx"
    assert file_needs_recovery(path) is True
    df = read_erp_excel(path)            # must not raise
    assert "Product name" in df.columns
    assert len(df) > 20000


def test_all_raw_files_readable():
    failures = []
    for f in sorted(RAW_DIR.rglob("*.xlsx")):
        try:
            read_erp_excel(f)
        except Exception as exc:  # pragma: no cover
            failures.append((f.name, str(exc)))
    assert not failures, f"unreadable files: {failures}"
