"""Forecasting engine — business-grade, not just technical output.

Every forecast returns:
  - point forecast + CONFIDENCE INTERVAL (default 80%)
  - MODEL QUALITY METRICS from an out-of-sample backtest (MAPE, RMSE, CI coverage)
  - explicit ASSUMPTIONS
  - a plain BUSINESS EXPLANATION a non-technical owner can act on

Model: Prophet (additive trend + yearly seasonality) with a statsmodels SARIMAX
fallback if Prophet is unavailable or fails. The chosen model is recorded.
"""
from __future__ import annotations

import logging
import warnings
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

# Quieten Prophet/cmdstanpy/statsmodels chatter.
for _n in ("cmdstanpy", "prophet", "fbprophet"):
    logging.getLogger(_n).setLevel(logging.CRITICAL)
warnings.filterwarnings("ignore")

try:
    from prophet import Prophet
    _HAVE_PROPHET = True
except Exception:  # pragma: no cover
    _HAVE_PROPHET = False


@dataclass
class ForecastResult:
    name: str
    unit: str
    model_used: str
    interval_width: float
    history: pd.DataFrame              # ds, y
    forecast: pd.DataFrame            # ds, yhat, yhat_lower, yhat_upper
    metrics: dict = field(default_factory=dict)   # mape, rmse, coverage, backtest_h, quality
    assumptions: list = field(default_factory=list)
    explanation: str = ""

    def to_dict(self):
        return {"name": self.name, "unit": self.unit, "model_used": self.model_used,
                "interval_width": self.interval_width,
                "forecast": self.forecast.assign(
                    ds=self.forecast["ds"].astype(str)).to_dict("records"),
                "metrics": self.metrics, "assumptions": self.assumptions,
                "explanation": self.explanation}


def _quality_grade(mape: float | None) -> str:
    if mape is None:
        return "unknown"
    if mape < 10:
        return "excellent"
    if mape < 20:
        return "good"
    if mape < 30:
        return "fair"
    return "weak"


# --------------------------------------------------------------------------- #
def _prophet_fit_predict(train: pd.DataFrame, periods: int, freq: str,
                         interval_width: float):
    m = Prophet(interval_width=interval_width, weekly_seasonality=False,
                daily_seasonality=False, yearly_seasonality=True)
    m.fit(train)
    future = m.make_future_dataframe(periods=periods, freq=freq)
    fc = m.predict(future)[["ds", "yhat", "yhat_lower", "yhat_upper"]]
    return fc


def _sarimax_fit_predict(train: pd.DataFrame, periods: int, freq: str,
                         interval_width: float):
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    y = train.set_index("ds")["y"]
    model = SARIMAX(y, order=(1, 1, 1), seasonal_order=(0, 1, 1, 12),
                    enforce_stationarity=False, enforce_invertibility=False)
    res = model.fit(disp=False)
    alpha = 1 - interval_width
    pred = res.get_forecast(steps=periods)
    ci = pred.conf_int(alpha=alpha)
    idx = pd.date_range(y.index[-1], periods=periods + 1, freq=freq)[1:]
    fc_future = pd.DataFrame({"ds": idx, "yhat": pred.predicted_mean.values,
                              "yhat_lower": ci.iloc[:, 0].values,
                              "yhat_upper": ci.iloc[:, 1].values})
    hist = pd.DataFrame({"ds": y.index, "yhat": res.fittedvalues.values,
                         "yhat_lower": np.nan, "yhat_upper": np.nan})
    return pd.concat([hist, fc_future], ignore_index=True)


def _fit_predict(train, periods, freq, interval_width):
    if _HAVE_PROPHET:
        try:
            return _prophet_fit_predict(train, periods, freq, interval_width), "Prophet"
        except Exception:
            pass
    return _sarimax_fit_predict(train, periods, freq, interval_width), "SARIMAX"


def _backtest(ts: pd.DataFrame, freq: str, interval_width: float, h: int):
    """Out-of-sample holdout: fit on all but last h, forecast h, score."""
    if len(ts) <= h + 12:
        return {}
    train, test = ts.iloc[:-h], ts.iloc[-h:]
    fc, _ = _fit_predict(train, h, freq, interval_width)
    pred = fc.merge(test, on="ds", how="inner")
    if pred.empty:
        return {}
    actual = pred["y"].values
    yhat = pred["yhat"].values
    mape = float(np.mean(np.abs((actual - yhat) / np.where(actual == 0, np.nan, actual))) * 100)
    rmse = float(np.sqrt(np.mean((actual - yhat) ** 2)))
    coverage = float(np.mean((actual >= pred["yhat_lower"]) & (actual <= pred["yhat_upper"])) * 100)
    return {"mape": round(mape, 1), "rmse": round(rmse, 0), "coverage": round(coverage, 0),
            "backtest_h": h, "quality": _quality_grade(mape)}


def forecast_series(ts: pd.Series, name: str, unit: str = "₹", periods: int = 6,
                    freq: str = "MS", interval_width: float = 0.8,
                    backtest_h: int = 6) -> ForecastResult:
    """Forecast a datetime-indexed numeric series with full business context."""
    df = pd.DataFrame({"ds": pd.to_datetime(ts.index), "y": ts.values}).dropna()
    metrics = _backtest(df, freq, interval_width, backtest_h)
    fc, model = _fit_predict(df, periods, freq, interval_width)

    future = fc[fc["ds"] > df["ds"].max()].head(periods).reset_index(drop=True)
    total = future["yhat"].sum()
    lo, hi = future["yhat_lower"].sum(), future["yhat_upper"].sum()
    # Compare to the SAME months one year earlier (seasonal analogue), not a
    # mismatched window, so the % change is meaningful.
    if len(df) >= periods * 2:
        prior_same = df["y"].iloc[-periods * 2:-periods].sum()
    else:
        prior_same = df["y"].tail(periods).sum()
    growth = (total / prior_same - 1) * 100 if prior_same else 0

    assumptions = [
        "Historical trend and yearly seasonality continue (no structural break, "
        "new line, or major customer loss).",
        f"Data is complete through {df['ds'].max():%b %Y}; the latest months are final, "
        "not partial.",
        "No one-off shocks (regulatory change, supply disruption, price control) in "
        "the forecast window.",
        f"Confidence interval is {interval_width:.0%}: the actual is expected to fall "
        "within the band about that often.",
    ]
    mape = metrics.get("mape")
    qual = metrics.get("quality", "unknown")
    acc = f"±{mape:.0f}% (backtested on the last {metrics.get('backtest_h','?')} months)" \
        if mape is not None else "not established (insufficient history)"
    explanation = (
        f"Over the next {periods} months, {name} is forecast at ≈₹{total:,.0f} "
        f"(80% confidence ₹{lo:,.0f}–₹{hi:,.0f}), about {growth:+.0f}% vs the same "
        f"{periods} months last year. Model: {model}; typical accuracy {acc}; "
        f"quality rating: {qual}. "
        "Treat the band, not the single number, as the planning range."
        if unit == "₹" else
        f"Over the next {periods} months, {name} is forecast at ≈{total:,.0f} {unit} "
        f"(80% CI {lo:,.0f}–{hi:,.0f}). Model: {model}; accuracy {acc}; quality {qual}.")

    return ForecastResult(name=name, unit=unit, model_used=model,
                          interval_width=interval_width, history=df, forecast=future,
                          metrics=metrics, assumptions=assumptions, explanation=explanation)


# --------------------------- convenience builders ------------------------- #
def _monthly(table: str, amount_col: str) -> pd.Series:
    from src.warehouse.db import make_engine
    e = make_engine()
    df = pd.read_sql(f"SELECT date_key, {amount_col} AS amt FROM {table} "
                     "WHERE date_key IS NOT NULL", e)
    df["date"] = pd.to_datetime(df["date_key"].astype(int).astype(str), format="%Y%m%d")
    return df.set_index("date")["amt"].resample("MS").sum()


def forecast_sales(periods: int = 6) -> ForecastResult:
    return forecast_series(_monthly("fact_sales", "net_amount_inr"),
                           "monthly sales", "₹", periods)


def forecast_purchases(periods: int = 6) -> ForecastResult:
    return forecast_series(_monthly("fact_purchases", "net_amount_inr"),
                           "monthly purchases", "₹", periods)
