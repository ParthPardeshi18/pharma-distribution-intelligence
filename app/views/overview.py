"""Overview — Business Health Index, headline KPIs, and the firm-wide narrative."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app import components as C
from app import data, theme


def _gauge(score: float, grade: str) -> go.Figure:
    color = theme.grade_color(grade)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": "/100", "font": {"size": 34, "color": theme.NAVY}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1},
            "bar": {"color": color, "thickness": 0.28},
            "steps": [
                {"range": [0, 40], "color": "#FBE9E7"},
                {"range": [40, 60], "color": "#FFF3E0"},
                {"range": [60, 80], "color": "#FFFDE7"},
                {"range": [80, 100], "color": "#E8F5E9"},
            ],
        },
    ))
    fig.update_layout(height=240, margin=dict(l=20, r=20, t=10, b=10))
    return fig


def render(opts: dict) -> None:
    currency, profile, fy = opts["currency"], opts["profile"], opts["fy"]

    st.markdown("## Business overview")
    st.caption("Single-glance health of the distribution business, computed by the "
               "Decision Intelligence engine.")

    if not data.warehouse_exists():
        st.warning("The warehouse has not been built yet. Run "
                   "`python run_pipeline.py --mode internal --currency INR` and reload.")
        return

    bhi = data.health(profile)
    scores = data.profile_scores()
    reports = data.domain_reports()

    # ── Health index + headline financials ──────────────────────────────────
    left, right = st.columns([1, 1.6])
    with left:
        C.section("Business Health Index", f"Profile: {profile}")
        st.plotly_chart(_gauge(bhi.score, bhi.grade), width="stretch")
        C.grade_badge(bhi.grade, bhi.score)
        if bhi.note:
            st.caption(bhi.note)

    with right:
        C.section("Headline (current year)")
        s = data.sales_by_fy().set_index("fy")
        cur, prior = data.current_fy(), data.prior_fy()
        if cur in s.index:
            row = s.loc[cur]
            prow = s.loc[prior] if prior in s.index else None

            def yoy(col):
                if prow is None or not prow[col]:
                    return None
                return round((row[col] - prow[col]) / prow[col] * 100, 1)

            margin = (row["profit"] / row["billed"] * 100) if row["billed"] else 0
            pmargin = (prow["profit"] / prow["billed"] * 100) if prow is not None and prow["billed"] else None
            tiles = st.columns(2)
            with tiles[0]:
                d, dsx = C.fmt_delta(yoy("revenue"))
                C.kpi_card("Revenue", data.money(row["revenue"], currency, cur),
                           delta=d, delta_status=dsx, accent=theme.NAVY)
                d, dsx = C.fmt_delta(yoy("profit"))
                C.kpi_card("Gross profit", data.money(row["profit"], currency, cur),
                           delta=d, delta_status=dsx, accent=theme.GREEN)
            with tiles[1]:
                d, dsx = C.fmt_delta(round(margin - pmargin, 1) if pmargin is not None else None)
                # margin delta is pp, label accordingly
                C.kpi_card("Gross margin", f"{margin:.2f}%",
                           delta=(d.replace("% YoY", " pp") if d else ""),
                           delta_status=dsx, accent=theme.AMBER)
                d, dsx = C.fmt_delta(yoy("bills"))
                C.kpi_card("Bills", f"{int(row['bills']):,}",
                           delta=d, delta_status=dsx, accent=theme.SLATE)

    # ── BHI across weight profiles ──────────────────────────────────────────
    C.section("Health across weight profiles",
              "The same business scored under different strategic priorities.")
    pf = pd.DataFrame({"profile": list(scores.keys()), "score": list(scores.values())})
    pf = pf.sort_values("score", ascending=True)
    fig = go.Figure(go.Bar(
        x=pf["score"], y=pf["profile"], orientation="h",
        marker_color=[theme.NAVY if p == profile else theme.GREY for p in pf["profile"]],
        text=pf["score"].round(0), textposition="outside",
    ))
    fig.update_layout(height=max(220, 38 * len(pf)), xaxis_range=[0, 100],
                      margin=dict(l=10, r=30, t=10, b=10), xaxis_title="BHI score")
    st.plotly_chart(fig, width="stretch")

    # ── Top risks & opportunities firm-wide ─────────────────────────────────
    risks, opps = [], []
    for r in reports:
        for rk in r.risks:
            risks.append((r.domain, rk))
        for op in r.opportunities:
            opps.append((r.domain, op))
    risks.sort(key=lambda t: t[1].score, reverse=True)
    opps.sort(key=lambda t: (t[1].potential_impact_inr or 0), reverse=True)

    c1, c2 = st.columns(2)
    with c1:
        C.section("Top risks")
        for dom, rk in risks[:5]:
            st.markdown(f"{theme.badge(dom, rk.severity)} **{rk.name}** — {rk.description}",
                        unsafe_allow_html=True)
    with c2:
        C.section("Biggest opportunities")
        for dom, op in opps[:5]:
            impact = data.money(op.potential_impact_inr, currency, fy) if op.potential_impact_inr else ""
            tag = f" · {impact}" if impact else ""
            st.markdown(f"{theme.badge(dom, 'positive')} **{op.name}**{tag} — {op.description}",
                        unsafe_allow_html=True)

    # ── Firm-wide executive narrative (from the 'sales' domain summary) ──────
    C.section("Executive narrative")
    sales = data.domain_report("sales")
    if sales and sales.executive_summary:
        C.narrative_box(sales.executive_summary, title="What the numbers say",
                        context="firm-wide overview for a pharmaceutical distributor")
