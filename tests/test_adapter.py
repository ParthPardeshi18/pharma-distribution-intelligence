"""ERP Adapter tests: canonical contract, type coercion, multi-year stacking."""
from src.adapters import get_adapter


def test_lists_all_report_types():
    a = get_adapter()
    reports = a.list_reports()
    assert len(reports) == 32
    assert "Sales/Sales" in reports
    assert "Profit/Profit_AllBills" in reports


def test_every_report_loads():
    a = get_adapter()
    failures = []
    for rk in a.list_reports():
        try:
            cf = a.load(rk)
            assert cf.report_key == rk
        except Exception as exc:  # pragma: no cover
            failures.append((rk, str(exc)))
    assert not failures, failures


def test_canonical_columns_no_erp_names():
    a = get_adapter()
    cf = a.load("Sales/Sales")
    assert list(cf.data.columns) == [
        "txn_date", "voucher_no", "customer_name", "address", "net_amount"]
    # canonical types
    assert str(cf.data["txn_date"].dtype).startswith("datetime64")
    assert str(cf.data["net_amount"].dtype) == "float64"


def test_ambiguous_override_party_name_to_supplier():
    a = get_adapter()
    cf = a.load("Outstanding/Payables_SupplierWise")
    assert "supplier_name" in cf.data.columns       # 'Party name' overridden
    assert "customer_name" not in cf.data.columns


def test_stable_id_detected_when_present():
    a = get_adapter()
    cf = a.load("Masters/Customer_Master")
    # ie_code is populated -> surfaced for future auto-adoption
    assert "ie_code" in cf.source_id_columns.values()


def test_load_all_years_stacks_and_tags():
    a = get_adapter()
    cf = a.load_all_years("Sales/Sales")
    assert {"22-23", "23-24", "24-25", "25-26"} <= set(cf.data["financial_year"].unique())
    assert len(cf.data) > 150_000
