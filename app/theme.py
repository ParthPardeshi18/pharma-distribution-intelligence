"""Visual identity for the app — palette, status colours, and CSS injection.

Colours mirror the executive ``.docx`` report (``src/report/health_report.py``)
so the live app and the printed report are visibly one product.
"""
from __future__ import annotations

import streamlit as st

# Core palette (hex) — matches the report's RGBColor constants.
NAVY = "#1F3A5F"
SLATE = "#55585F"
GREEN = "#1E7E34"
AMBER = "#B06A00"
RED = "#B11B1B"
GREY = "#8A8F98"

# Status → colour. DI uses positive | info | warning | critical (+ good/ok/poor
# from KPI scoring). Map them all so any engine vocabulary renders consistently.
STATUS_COLORS = {
    "positive": GREEN, "good": GREEN, "excellent": GREEN, "ok": AMBER,
    "info": NAVY, "neutral": SLATE,
    "warning": AMBER, "watch": AMBER, "fair": AMBER, "poor": AMBER,
    "critical": RED, "bad": RED,
}

# Letter grade → colour for Business Health Index / scorecards.
GRADE_COLORS = {
    "A": GREEN, "B": GREEN, "C": AMBER, "D": AMBER, "E": RED, "F": RED,
}


def status_color(status: str | None) -> str:
    return STATUS_COLORS.get((status or "info").lower(), SLATE)


def grade_color(grade: str | None) -> str:
    return GRADE_COLORS.get((grade or "C")[:1].upper(), SLATE)


def inject_css() -> None:
    """Inject the shared stylesheet once per page render."""
    st.markdown(
        f"""
        <style>
          .block-container {{ padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1280px; }}
          /* KPI cards */
          .pdi-card {{
              border: 1px solid #E6E9EE; border-left: 5px solid {NAVY};
              border-radius: 10px; padding: 0.85rem 1.05rem; background: #FFFFFF;
              box-shadow: 0 1px 3px rgba(16,24,40,0.04); height: 100%;
          }}
          .pdi-card .label {{ color: {SLATE}; font-size: 0.78rem; font-weight: 600;
              text-transform: uppercase; letter-spacing: 0.03em; }}
          .pdi-card .value {{ color: {NAVY}; font-size: 1.7rem; font-weight: 700;
              line-height: 1.15; margin: 0.15rem 0; }}
          .pdi-card .delta {{ font-size: 0.85rem; font-weight: 600; }}
          .pdi-card .desc  {{ color: {GREY}; font-size: 0.72rem; margin-top: 0.25rem; }}
          /* Pills / badges */
          .pdi-badge {{ display: inline-block; padding: 0.12rem 0.6rem; border-radius: 999px;
              font-size: 0.72rem; font-weight: 700; color: #FFFFFF; }}
          /* AI / narrative box */
          .pdi-summary {{ border: 1px solid #E6E9EE; border-radius: 10px;
              background: {("#F4F6F9")}; padding: 1rem 1.2rem; }}
          .pdi-summary h4 {{ margin: 0 0 0.4rem 0; color: {NAVY}; }}
          /* Section rule */
          .pdi-rule {{ border: none; border-top: 2px solid {NAVY}; opacity: 0.15; margin: 0.4rem 0 1.1rem; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def badge(text: str, status: str = "info") -> str:
    """Return an inline HTML pill (caller renders with unsafe_allow_html)."""
    return f'<span class="pdi-badge" style="background:{status_color(status)}">{text}</span>'
