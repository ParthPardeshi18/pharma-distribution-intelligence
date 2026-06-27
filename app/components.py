"""Reusable UI components: KPI cards, sidebar filters, narrative/AI box, and
download buttons. These are pure presentation — they format values produced by
``app.data`` and never compute business metrics themselves.
"""
from __future__ import annotations

import streamlit as st

from app import data, theme


# ── Value formatting ────────────────────────────────────────────────────────
def fmt_metric(m, currency: str = "INR", fy: str | None = None) -> str:
    """Format a DI ``Metric`` for display, honouring its unit and the presentation
    currency for ₹ values."""
    v = m.value
    if v is None:
        return "—"
    unit = (m.unit or "").strip()
    if unit == "₹":
        return data.money(v, currency, fy)
    if unit == "%":
        return f"{v:,.1f}%"
    if unit == "days":
        return f"{v:,.0f} days"
    if unit in ("x", "×"):
        return f"{v:,.1f}×"
    if unit == "count":
        return f"{v:,.0f}"
    return f"{v:,.2f}{(' ' + unit) if unit else ''}"


def fmt_delta(yoy_pct) -> tuple[str, str]:
    """Return (text, status) for a YoY % change."""
    if yoy_pct is None:
        return ("", "neutral")
    arrow = "▲" if yoy_pct > 0 else ("▼" if yoy_pct < 0 else "▬")
    status = "positive" if yoy_pct > 0 else ("critical" if yoy_pct < 0 else "neutral")
    return (f"{arrow} {abs(yoy_pct):.1f}% YoY", status)


# ── KPI cards ───────────────────────────────────────────────────────────────
def kpi_card(label: str, value: str, *, delta: str = "", delta_status: str = "neutral",
             desc: str = "", accent: str | None = None) -> None:
    accent = accent or theme.NAVY
    delta_html = (
        f'<div class="delta" style="color:{theme.status_color(delta_status)}">{delta}</div>'
        if delta else ""
    )
    desc_html = f'<div class="desc">{desc}</div>' if desc else ""
    st.markdown(
        f'<div class="pdi-card" style="border-left-color:{accent}">'
        f'<div class="label">{label}</div>'
        f'<div class="value">{value}</div>{delta_html}{desc_html}</div>',
        unsafe_allow_html=True,
    )


def metric_card(m, currency: str = "INR", fy: str | None = None) -> None:
    """Render a DI ``Metric`` as a KPI card with YoY delta and health colour."""
    delta_text, delta_status = fmt_delta(getattr(m, "yoy_pct", None))
    kpi_card(
        m.label,
        fmt_metric(m, currency, fy),
        delta=delta_text,
        delta_status=delta_status,
        desc=m.description or "",
        accent=theme.status_color(getattr(m, "status", "info")),
    )


def kpi_row(metrics, currency: str = "INR", fy: str | None = None, per_row: int = 4) -> None:
    """Lay out a list of DI Metrics in a responsive grid of KPI cards."""
    metrics = list(metrics)
    for i in range(0, len(metrics), per_row):
        cols = st.columns(per_row)
        for col, m in zip(cols, metrics[i:i + per_row]):
            with col:
                metric_card(m, currency, fy)


# ── Section helpers ─────────────────────────────────────────────────────────
def section(title: str, subtitle: str = "") -> None:
    st.markdown(f"### {title}")
    if subtitle:
        st.caption(subtitle)
    st.markdown('<hr class="pdi-rule">', unsafe_allow_html=True)


def grade_badge(grade: str, score: float | None = None) -> None:
    label = f"{grade}" + (f" · {score:.0f}/100" if score is not None else "")
    st.markdown(theme.badge(label, _grade_status(grade)), unsafe_allow_html=True)


def _grade_status(grade: str) -> str:
    g = (grade or "C")[:1].upper()
    return {"A": "positive", "B": "positive", "C": "warning",
            "D": "warning", "E": "critical", "F": "critical"}.get(g, "info")


# ── Sidebar filters ─────────────────────────────────────────────────────────
def privacy_banner(mode: str) -> None:
    """Top-of-page banner making the active data mode unmistakable."""
    if mode == "shareable":
        st.markdown(
            f'<div class="pdi-summary" style="border-left:5px solid {theme.GREEN};'
            f'background:#E8F5E9">🔓 <b>Public / anonymised mode</b> — customer, '
            f'supplier, and salesman identities are shown as stable codes '
            f'(<code>Customer_0001</code>…). No real names are read or displayed.'
            f'</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="pdi-summary" style="border-left:5px solid {theme.RED};'
            f'background:#FBE9E7">🔒 <b>Internal mode</b> — real company data '
            f'(confidential). Do not share screenshots externally.</div>',
            unsafe_allow_html=True)


def sidebar_filters(user, mode: str = "internal") -> dict:
    """Render the shared sidebar (identity, mode, currency, BHI profile, FY) and
    return the selected presentation options."""
    from app import config, data

    cfg = config.app_config()
    with st.sidebar:
        st.markdown(f"#### {cfg.get('app', {}).get('short_name', 'PDI')}")
        st.caption(f"v{cfg.get('app', {}).get('version', '1.1.0')} · signed in as "
                   f"**{user.name}** ({user.role})")

        # ── Data mode ────────────────────────────────────────────────────────
        if mode == "shareable":
            st.success("🔓 Public / anonymised data", icon="🔓")
        else:
            st.error("🔒 Internal · real data", icon="🔒")

        # Admins may preview the other mode (only if that warehouse is present).
        if user.role == "admin":
            choice = st.radio(
                "Data mode", ["internal", "shareable"],
                index=0 if mode == "internal" else 1, horizontal=True,
                help="Preview the anonymised public view. Public deployments are "
                     "pinned to 'shareable' via config/env and cannot switch here.",
            )
            if choice != mode:
                # Block switching to a mode whose warehouse isn't built.
                from src.warehouse.db import current_db_path
                target = current_db_path(choice)
                if not target.exists():
                    st.warning(f"`{target.name}` not built yet. Run "
                               f"`python run_pipeline.py --mode {choice}`.")
                else:
                    st.session_state["pdi_mode_override"] = choice
                    st.cache_data.clear()
                    st.cache_resource.clear()
                    st.rerun()
        st.divider()

        currency = st.selectbox(
            "Presentation currency", config.currency_options(),
            help="INR is the source of truth; this converts figures at display time only.",
        )

        try:
            profiles = data.list_profiles()
        except Exception:
            profiles = [config.default_profile()]
        default_profile = config.default_profile()
        profile = st.selectbox(
            "Health Index profile", profiles,
            index=profiles.index(default_profile) if default_profile in profiles else 0,
            help="Weight profile for the Business Health Index.",
        )

        try:
            fys = data.fiscal_years()
            fy = st.selectbox("Fiscal year (where applicable)", fys,
                              index=len(fys) - 1)
        except Exception:
            fy = None

        st.divider()
        if st.button("↻ Refresh data", width="stretch",
                     help="Clear caches and re-read the warehouse."):
            st.cache_data.clear()
            st.rerun()
        if st.button("Sign out", width="stretch"):
            from app import auth
            auth.logout()
            st.rerun()

    return {"currency": currency, "profile": profile, "fy": fy, "mode": mode}


# ── Narrative / AI summary box ──────────────────────────────────────────────
def narrative_box(executive_summary, *, title: str = "Executive summary",
                  context: str = "") -> None:
    """Render a DI ``ExecutiveSummary`` as a narrative, with an optional one-click
    Claude rewrite (only when ai_summary.enabled in config)."""
    from app import ai, config

    es = executive_summary
    if es is None:
        return

    base_md = (
        f"**What happened.** {es.what_happened}\n\n"
        f"**Why.** {es.why}\n\n"
        f"**Business impact.** {es.business_impact}"
    )
    actions = getattr(es, "recommended_actions", []) or []

    with st.container():
        st.markdown(f'<div class="pdi-summary"><h4>{title}</h4>', unsafe_allow_html=True)
        st.markdown(base_md)
        if actions:
            st.markdown("**Recommended actions**")
            for a in actions:
                st.markdown(f"- {a}")
        st.markdown("</div>", unsafe_allow_html=True)

        if config.app_config().get("ai_summary", {}).get("enabled", False):
            if st.button("✨ Polish with Claude", key=f"ai_{title}"):
                with st.spinner("Generating polished narrative…"):
                    polished = ai.enhance(base_md, context=context)
                if polished:
                    st.info(polished)


# ── Downloads ───────────────────────────────────────────────────────────────
def download_df(df, filename: str, label: str | None = None) -> None:
    st.download_button(
        label or f"⬇ Download {filename}",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=filename, mime="text/csv", width="stretch",
    )


def download_bytes(content: bytes, filename: str, mime: str, label: str | None = None) -> None:
    st.download_button(
        label or f"⬇ Download {filename}", data=content,
        file_name=filename, mime=mime, width="stretch",
    )
