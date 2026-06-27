"""Strategic analytics — ABC/Pareto, RFM, lifecycle, seasonality, multi-year
trends, inventory ageing, and profitability rankings."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app import components as C
from app import data, theme


def _abc_tab(currency, fy):
    entity = st.radio("Entity", ["customers", "products", "suppliers"],
                      horizontal=True, key="abc_entity")
    res = data.abc(entity, fy)
    st.markdown(f"**{res.pareto_ratio}**")
    cls = res.classes.copy()
    c1, c2 = st.columns([1, 1])
    with c1:
        fig = px.bar(cls, x="class", y="value", color="class",
                     color_discrete_map={"A": theme.GREEN, "B": theme.AMBER, "C": theme.RED},
                     text=cls["pct_of_value"].astype(str) + "%")
        fig.update_layout(height=320, showlegend=False, yaxis_title="Value (₹)",
                          margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, width="stretch")
    with c2:
        disp = cls.rename(columns={"n": "Count", "value": "Value (₹)",
                                   "pct_of_entities": "% of entities",
                                   "pct_of_value": "% of value"})
        st.dataframe(disp, width="stretch", hide_index=True)
    C.download_df(cls, f"abc_{entity}.csv", "⬇ Download ABC classes (CSV)")


def _rfm_tab(currency):
    res = data.rfm()
    st.caption(f"Reference date: {res.reference_date:%d %b %Y}")
    seg = res.segments.copy()
    c1, c2 = st.columns([1.2, 1])
    with c1:
        fig = px.bar(seg.sort_values("monetary"), x="monetary", y="segment",
                     orientation="h", color="monetary",
                     color_continuous_scale=["#FBE9E7", theme.NAVY])
        fig.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10),
                          xaxis_title="Monetary value (₹)", coloraxis_showscale=False)
        st.plotly_chart(fig, width="stretch")
    with c2:
        st.dataframe(seg, width="stretch", hide_index=True)
    C.download_df(res.customers, "rfm_customers.csv", "⬇ Download per-customer RFM (CSV)")


def _lifecycle_tab(currency, fy):
    res = data.lifecycle()
    C.kpi_card("Revenue tied up in declining products",
               data.money(res.decline_value, currency, fy), accent=theme.RED)
    fig = px.bar(res.summary, x="stage", y="revenue_share", color="stage",
                 text="n")
    fig.update_layout(height=340, showlegend=False, yaxis_title="Revenue share (%)",
                      margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, width="stretch")
    st.dataframe(res.summary, width="stretch", hide_index=True)


def _seasonality_tab():
    res = data.seasonality()
    cols = st.columns(3)
    cols[0].metric("Peak month", res.peak_month)
    cols[1].metric("Trough month", res.trough_month)
    cols[2].metric("Peak-to-trough swing", f"{res.swing_pct:.0f}%")
    mi = res.monthly_index
    fig = go.Figure(go.Scatter(x=mi["month_name"], y=mi["index"], mode="lines+markers",
                               line=dict(color=theme.NAVY, width=3)))
    fig.add_hline(y=1.0, line_dash="dash", line_color=theme.GREY,
                  annotation_text="average month")
    fig.update_layout(height=340, yaxis_title="Seasonality index (1.0 = avg)",
                      margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, width="stretch")
    st.caption(f"Based on {res.n_years} years of monthly sales.")


def _trends_tab(currency):
    trends = data.trends()
    for t in trends:
        s = pd.DataFrame(t.series, columns=["fy", "value"])
        c1, c2 = st.columns([2, 1])
        with c1:
            fig = go.Figure(go.Scatter(x=s["fy"], y=s["value"], mode="lines+markers",
                                       line=dict(color=theme.NAVY, width=3)))
            fig.update_layout(height=220, title=t.measure, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig, width="stretch")
        with c2:
            cagr = f"{t.cagr_pct:+.1f}%" if t.cagr_pct is not None else "—"
            st.metric(f"{t.measure} CAGR", cagr, help=t.note)
            st.caption(f"Direction: **{t.direction}**")


def _ageing_tab(currency, fy):
    res = data.inventory_ageing()
    cols = st.columns(3)
    cols[0].metric("Inventory turnover",
                   f"{res.turnover:.1f}×" if res.turnover is not None else "—")
    cols[1].metric("Inventory days",
                   f"{res.inventory_days:.0f}" if res.inventory_days is not None else "—")
    cols[2].metric("At-risk value (≤90d / expired)",
                   data.compact_inr(res.at_risk_value))
    if res.note:
        st.caption(res.note)
    if res.expiry_buckets is not None and not res.expiry_buckets.empty:
        fig = px.bar(res.expiry_buckets, x="bucket", y="value", text="batches",
                     color="value", color_continuous_scale=["#E8F5E9", theme.RED])
        fig.update_layout(height=320, coloraxis_showscale=False,
                          yaxis_title="Value (₹)", margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, width="stretch")
        st.dataframe(res.expiry_buckets, width="stretch", hide_index=True)


def _profitability_tab(currency, fy):
    entity = st.radio("Entity", ["customers", "products", "suppliers", "territories"],
                      horizontal=True, key="profit_entity")
    n = st.slider("Top / bottom N", 5, 25, 10, key="profit_n")
    res = data.profitability(entity, fy, n)
    if res.note:
        st.caption(res.note)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**Most profitable {entity}**")
        st.dataframe(res.top, width="stretch", hide_index=True)
    with c2:
        st.markdown(f"**Least profitable {entity}**")
        st.dataframe(res.bottom, width="stretch", hide_index=True)


def render(opts: dict) -> None:
    currency, profile, fy = opts["currency"], opts["profile"], opts["fy"]

    st.markdown("## Strategic analytics")
    st.caption("Segmentation, lifecycle, seasonality, and profitability — the levers "
               "behind the headline numbers.")

    if not data.warehouse_exists():
        st.warning("Build the warehouse first (`python run_pipeline.py`).")
        return

    tabs = st.tabs(["ABC / Pareto", "RFM segments", "Product lifecycle",
                    "Seasonality", "Multi-year trends", "Inventory ageing",
                    "Profitability"])
    with tabs[0]:
        _abc_tab(currency, fy)
    with tabs[1]:
        _rfm_tab(currency)
    with tabs[2]:
        _lifecycle_tab(currency, fy)
    with tabs[3]:
        _seasonality_tab()
    with tabs[4]:
        _trends_tab(currency)
    with tabs[5]:
        _ageing_tab(currency, fy)
    with tabs[6]:
        _profitability_tab(currency, fy)
