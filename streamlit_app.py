"""Pharmaceutical Distribution Intelligence Platform — Streamlit application (v1.1).

The primary user interface for the platform. It consumes the existing warehouse,
Decision Intelligence engine, Strategic Analytics, GIS layer, forecasting, KPI
registry, and Business Health Index **without duplicating business logic** —
every figure is computed in ``src/`` and merely cached and rendered here.

Run:
    streamlit run streamlit_app.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# Ensure the project root is importable so `import src...` / `import app...` work
# regardless of the working directory Streamlit is launched from.
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import auth, config, data, theme  # noqa: E402
from app import components as C  # noqa: E402
from app.views import (  # noqa: E402
    data_quality, decision_intelligence, forecasting, geographic, overview, reports, strategic,
)

# Page registry: key → (label, icon, render fn). Keys match the RBAC lists in
# config/app_config.yaml → auth.roles.
_PAGES = [
    ("overview", "Overview", "📊", overview.render),
    ("decision_intelligence", "Decision Intelligence", "🧭", decision_intelligence.render),
    ("strategic", "Strategic Analytics", "📈", strategic.render),
    ("forecasting", "Forecasting", "🔮", forecasting.render),
    ("geographic", "Geographic", "🗺️", geographic.render),
    ("reports", "Reports & Downloads", "📥", reports.render),
    ("data_quality", "Data Quality", "✅", data_quality.render),
]


def _make_runner(render_fn):
    """Wrap a view's render(opts) into a zero-arg callable for st.Page, reading the
    current sidebar selections from session state."""
    def _run():
        render_fn(st.session_state.get("pdi_opts", {}))
    _run.__name__ = render_fn.__module__.split(".")[-1]
    return _run


def main() -> None:
    app_cfg = config.app_config().get("app", {})
    st.set_page_config(
        page_title=app_cfg.get("name", "PDI Platform"),
        page_icon="💊",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    theme.inject_css()

    # Auth gate — blocks (st.stop) until signed in.
    user = auth.login_gate()

    # Resolve the data-presentation mode and bind the engines to the matching
    # warehouse BEFORE any data access. Two gates combine:
    #   1. Role gate — any role not in auth.real_data_roles is FORCED to the
    #      anonymised warehouse (a viewer can never be shown real identities).
    #   2. Admin preview — an admin allowed real data may toggle to shareable.
    base_mode = config.current_mode()
    override = st.session_state.get("pdi_mode_override")
    if override and user.role == "admin" and "admin" in config.real_data_roles():
        base_mode = override
    mode = config.effective_mode(user.role, base_mode)
    data.bind_mode(mode)

    # Public demo: fetch the anonymised warehouse on first run if it isn't present
    # (no-op on a normal internal install).
    from app import bootstrap
    bootstrap.ensure_demo_data(mode)

    # Shared sidebar filters; stash for the page runners.
    opts = C.sidebar_filters(user, mode)
    st.session_state["pdi_opts"] = opts

    # Build role-filtered navigation.
    pages = []
    for key, label, icon, fn in _PAGES:
        if user.can(key):
            pages.append(st.Page(_make_runner(fn), title=label, icon=icon,
                                 url_path=key, default=(key == "overview")))

    if not pages:
        st.error("Your account has no pages assigned. Contact an administrator.")
        st.stop()

    C.privacy_banner(mode)
    nav = st.navigation(pages, position="sidebar")
    nav.run()


if __name__ == "__main__":
    main()
