"""Currency service tests: INR identity, conversion, frame conversion, errors."""
import pandas as pd
import pytest

from src.currency import CurrencyConverter, CurrencyError


def test_inr_is_identity():
    c = CurrencyConverter()
    assert c.rate("INR", "25-26") == 1.0
    assert c.convert(1000, "INR", "25-26") == 1000


def test_convert_to_gbp_uses_fy_rate():
    c = CurrencyConverter()
    r = c.rate("GBP", "25-26")
    assert 0 < r < 1
    assert c.convert(100000, "GBP", "25-26") == pytest.approx(100000 * r)


def test_unsupported_currency_raises():
    c = CurrencyConverter()
    with pytest.raises(CurrencyError):
        c.rate("JPY", "25-26")


def test_convert_frame_adds_columns_per_fy():
    c = CurrencyConverter()
    df = pd.DataFrame({"net_amount_inr": [1000.0, 2000.0],
                       "financial_year": ["24-25", "25-26"]})
    out = c.convert_frame(df, ["net_amount_inr"], "USD")
    assert "net_amount_usd" in out.columns
    assert out["net_amount_usd"].iloc[0] == pytest.approx(1000 * c.rate("USD", "24-25"))
    # warehouse column untouched (INR remains source of truth)
    assert list(out["net_amount_inr"]) == [1000.0, 2000.0]


def test_convert_frame_inr_noop():
    c = CurrencyConverter()
    df = pd.DataFrame({"net_amount_inr": [5.0], "financial_year": ["25-26"]})
    out = c.convert_frame(df, ["net_amount_inr"], "INR")
    assert "net_amount_inr_inr" not in out.columns


def test_format():
    c = CurrencyConverter()
    assert c.format(910.0, "GBP") == "£910.00"
    assert c.format(1234567, "INR") == "₹1,234,567"
