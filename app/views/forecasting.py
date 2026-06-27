"""Forecasting — sales and purchases projections with confidence intervals,
model-quality metrics, assumptions, and a plain-language explanation."""
from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from app import components as C
from app import data, theme


def _forecast_chart(res) -> go.Figure:
    hist, fc = res.history, res.forecast
    fig = go.Figure()
    # Confidence band
    fig.add_trace(go.Scatter(
        x=list(fc["ds"]) + list(fc["ds"][::-1]),
        y=list(fc["yhat_upper"]) + list(fc["yhat_lower"][::-1]),
        fill="toself", fillcolor="rgba(31,58,95,0.12)", line=dict(color="rgba(0,0,0,0)"),
        hoverinfo="skip", name=f"{int(res.interval_width * 100)}% interval",
    ))
    fig.add_trace(go.Scatter(x=hist["ds"], y=hist["y"], mode="lines",
                             line=dict(color=theme.SLATE, width=2), name="Actual"))
    fig.add_trace(go.Scatter(x=fc["ds"], y=fc["yhat"], mode="lines+markers",
                             line=dict(color=theme.NAVY, width=3, dash="dot"),
                             name="Forecast"))
    fig.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10),
                      legend=dict(orientation="h", y=1.08),
                      yaxis_title=res.unit)
    return fig


def _render_forecast(res, currency):
    st.markdown(f"#### {res.name}")
    m = res.metrics or {}
    cols = st.columns(4)
    cols[0].metric("Model", res.model_used)
    quality = m.get("quality", "—")
    cols[1].metric("Backtest quality", str(quality).title())
    mape = m.get("mape")
    cols[2].metric("MAPE", f"{mape:.1f}%" if mape is not None else "—",
                   help="Mean absolute percentage error on a hold-out backtest.")
    cov = m.get("coverage")
    cols[3].metric("Interval coverage", f"{cov:.0%}" if cov is not None else "—",
                   help="Share of backtest actuals that fell within the predicted interval.")

    st.plotly_chart(_forecast_chart(res), width="stretch")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Assumptions**")
        for a in (res.assumptions or []):
            st.markdown(f"- {a}")
    with c2:
        st.markdown("**What this means**")
        st.info(res.explanation or "—")

    # Forecast table (ds + yhat band)
    tbl = res.forecast.copy()
    tbl["ds"] = tbl["ds"].astype(str)
    st.dataframe(tbl, width="stretch", hide_index=True)
    C.download_df(tbl, f"forecast_{res.name.lower().replace(' ', '_')}.csv",
                  "⬇ Download forecast (CSV)")


def render(opts: dict) -> None:
    currency = opts["currency"]

    st.markdown("## Forecasting")
    st.caption("Every projection ships with confidence intervals, model-quality "
               "metrics, assumptions, and a plain-language explanation.")

    if not data.warehouse_exists():
        st.warning("Build the warehouse first (`python run_pipeline.py`).")
        return

    series = st.radio("Series", ["Sales", "Purchases"], horizontal=True)
    periods = st.slider("Months ahead", 3, 12, 6)

    with st.spinner("Fitting model…"):
        res = data.forecast_sales(periods) if series == "Sales" else data.forecast_purchases(periods)

    _render_forecast(res, currency)
