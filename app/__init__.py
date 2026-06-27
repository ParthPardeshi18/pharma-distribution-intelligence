"""Streamlit application package (v1.1) — the primary user interface for the
Pharmaceutical Distribution Intelligence Platform.

This package is a thin presentation layer. It consumes the existing warehouse,
Decision Intelligence engine, Strategic Analytics, GIS layer, forecasting, KPI
registry, and Business Health Index **without duplicating business logic** — every
number shown here is computed by ``src/`` and merely cached and rendered by ``app/``.

Modules
-------
config      load app_config.yaml + app_users.yaml
theme       palette, CSS, status colours/badges
auth        login form + role-based access control (RBAC)
data        ``@st.cache_data`` / ``@st.cache_resource`` accessors over ``src/``
components  reusable widgets: KPI cards, filters, AI-summary box, downloads
ai          optional Claude enhancer for executive narratives (off by default)
views/      one render function per page
"""

__version__ = "1.1.0"
