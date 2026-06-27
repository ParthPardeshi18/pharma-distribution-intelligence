"""Strategic analysis tests: forecasting rigor, ABC, RFM, seasonality, lifecycle."""
import numpy as np
import pandas as pd
import pytest

from src.strategic import abc_pareto
from src.strategic.forecasting import forecast_series
from src.warehouse.db import DB_PATH

_skip = pytest.mark.skipif(not DB_PATH.exists(), reason="no warehouse db")


# --------------------------- forecasting (no DB needed) ------------------ #
def _synthetic_series(n=48):
    idx = pd.date_range("2022-04-01", periods=n, freq="MS")
    trend = np.linspace(100, 140, n)
    seasonal = 10 * np.sin(np.arange(n) / 12 * 2 * np.pi)
    y = trend + seasonal + np.random.default_rng(0).normal(0, 3, n)
    return pd.Series(y, index=idx)


def test_forecast_has_intervals_assumptions_quality_explanation():
    fc = forecast_series(_synthetic_series(), "test metric", unit="units", periods=6)
    # confidence interval present and ordered
    assert {"yhat", "yhat_lower", "yhat_upper"} <= set(fc.forecast.columns)
    assert (fc.forecast["yhat_lower"] <= fc.forecast["yhat"]).all()
    assert (fc.forecast["yhat"] <= fc.forecast["yhat_upper"]).all()
    # model quality metrics from backtest
    assert "mape" in fc.metrics and "quality" in fc.metrics
    # assumptions + business explanation
    assert len(fc.assumptions) >= 3
    assert fc.explanation and "forecast" in fc.explanation.lower()
    assert fc.model_used in ("Prophet", "SARIMAX")


def test_abc_classify_orders_by_value():
    s = pd.Series([100, 50, 30, 10, 5, 3, 2])
    cls = abc_pareto.classify(s)
    assert cls.iloc[0] == "A"          # largest is class A
    assert set(cls.unique()) <= {"A", "B", "C"}


# --------------------------- DB-backed -------------------------------- #
@_skip
def test_abc_customers_pareto():
    r = abc_pareto.customers()
    a = r.classes[r.classes["class"] == "A"].iloc[0]
    assert a["pct_of_value"] >= 60        # vital few drive most value
    assert a["pct_of_entities"] < 50


@_skip
def test_rfm_segments_partition_customers():
    from src.strategic import rfm
    r = rfm.analyze()
    assert r.segments["n"].sum() == len(r.customers)
    assert r.segments["pct_value"].sum() == pytest.approx(100, abs=1)


@_skip
def test_seasonality_indices_average_to_one():
    from src.strategic import seasonality
    s = seasonality.analyze()
    assert abs(s.monthly_index["index"].mean() - 1.0) < 0.05
    assert s.peak_month and s.trough_month


@_skip
def test_lifecycle_stages_cover_all_products():
    from src.strategic import lifecycle
    lc = lifecycle.analyze()
    assert lc.summary["n"].sum() > 0
    assert set(lc.summary["stage"]) <= {"New", "Growth", "Mature", "Decline", "Dormant"}
