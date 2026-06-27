"""Tests for the Streamlit application layer (v1.1).

Two tiers:
  * Pure logic — auth hashing/verification, RBAC, config, and the data-layer
    formatters — run without a Streamlit runtime.
  * AppTest — drives the real app via streamlit.testing to exercise the auth
    gate, role-based navigation, and an authenticated render end-to-end.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import auth, config  # noqa: E402


def _shareable_db_available() -> bool:
    from src.warehouse.db import current_db_path

    return current_db_path("shareable").exists()


SALT = "test-salt"
STORE = {
    "alice": {"name": "Alice", "role": "admin",
              "password_sha256": auth.hash_password("wonderland", SALT)},
    "bob": {"name": "Bob", "role": "viewer",
            "password_sha256": auth.hash_password("builder", SALT)},
}


# ── Pure auth logic ─────────────────────────────────────────────────────────
def test_hash_is_deterministic_and_salted():
    a = auth.hash_password("pw", "s1")
    b = auth.hash_password("pw", "s1")
    c = auth.hash_password("pw", "s2")
    assert a == b
    assert a != c
    assert len(a) == 64  # sha256 hex


def test_verify_accepts_correct_password():
    u = auth.verify("alice", "wonderland", salt=SALT, store=STORE)
    assert u is not None
    assert u.username == "alice"
    assert u.role == "admin"


def test_verify_rejects_wrong_password():
    assert auth.verify("alice", "nope", salt=SALT, store=STORE) is None


def test_verify_rejects_unknown_user():
    assert auth.verify("ghost", "x", salt=SALT, store=STORE) is None


# ── RBAC ────────────────────────────────────────────────────────────────────
def test_admin_can_see_admin_pages():
    admin = auth.User("alice", "Alice", "admin")
    assert admin.can("data_quality")
    assert admin.can("reports")


def test_viewer_is_restricted():
    viewer = auth.User("bob", "Bob", "viewer")
    assert viewer.can("overview")
    assert not viewer.can("data_quality")
    assert not viewer.can("reports")
    assert not viewer.can("forecasting")


# ── Role → data-mode gate (PII visibility) ──────────────────────────────────
def test_viewer_is_forced_to_anonymised_data():
    # A viewer must NEVER see real identities, even when the app is internal.
    assert config.effective_mode("viewer", "internal") == "shareable"
    assert config.effective_mode("viewer", "shareable") == "shareable"


def test_trusted_roles_see_configured_mode():
    assert config.effective_mode("admin", "internal") == "internal"
    # analyst is a real-data role by default config
    assert config.effective_mode("analyst", "internal") == "internal"
    # but everyone collapses to shareable when the app itself is public
    assert config.effective_mode("admin", "shareable") == "shareable"


def test_real_data_roles_excludes_viewer():
    assert "viewer" not in config.real_data_roles()


def test_every_role_has_pages_and_keys_are_known():
    known = {"overview", "decision_intelligence", "strategic", "forecasting",
             "geographic", "reports", "data_quality"}
    roles = config.app_config()["auth"]["roles"]
    assert set(roles) == {"admin", "analyst", "viewer"}
    for role, pages in roles.items():
        assert pages, f"{role} has no pages"
        assert set(pages) <= known, f"{role} references unknown page keys"


# ── Config ──────────────────────────────────────────────────────────────────
def test_app_config_shape():
    cfg = config.app_config()
    assert cfg["app"]["version"]
    assert "INR" in config.currency_options()
    assert config.default_profile()


def test_default_user_store_loads():
    users = config.users()
    assert {"admin", "analyst", "viewer"} <= set(users)


# ── Data-layer formatters (no warehouse needed) ─────────────────────────────
def test_compact_inr_shorthand():
    from app import data

    assert data.compact_inr(15_000_000) == "₹1.50 Cr"
    assert data.compact_inr(250_000) == "₹2.50 L"
    assert data.compact_inr(900) == "₹900"
    assert data.compact_inr(None) == "—"


# ── AppTest end-to-end ──────────────────────────────────────────────────────
def _app():
    from streamlit.testing.v1 import AppTest

    return AppTest.from_file(str(PROJECT_ROOT / "streamlit_app.py"))


def test_unauthenticated_shows_login_gate():
    at = _app().run(timeout=60)
    assert not at.exception
    # Login form fields present; no page content rendered yet.
    assert len(at.text_input) >= 2
    joined = " ".join(m.value for m in at.markdown)
    assert "Sign in" in joined


def test_invalid_login_shows_error():
    at = _app().run(timeout=60)
    at.text_input[0].set_value("admin").run(timeout=60)
    at.text_input[1].set_value("wrongpass")
    at.button[0].click().run(timeout=60)
    assert not at.exception
    assert any("Invalid" in e.value for e in at.error)


@pytest.mark.slow
def test_admin_login_renders_overview():
    at = _app().run(timeout=120)
    at.text_input[0].set_value("admin")
    at.text_input[1].set_value("admin123")
    at.button[0].click().run(timeout=300)
    assert not at.exception
    assert "pdi_user" in at.session_state
    user = at.session_state["pdi_user"]
    assert user is not None and user.role == "admin"


@pytest.mark.slow
@pytest.mark.skipif(not _shareable_db_available(), reason="shareable warehouse not built")
def test_viewer_login_is_pinned_to_shareable():
    """End-to-end: a viewer session resolves to anonymised data."""
    at = _app().run(timeout=120)
    at.text_input[0].set_value("viewer")
    at.text_input[1].set_value("viewer123")
    at.button[0].click().run(timeout=300)
    assert not at.exception
    assert "pdi_opts" in at.session_state
    assert at.session_state["pdi_opts"]["mode"] == "shareable"


# Render each page in isolation against the real warehouse to catch view-level
# rendering errors that the login-only smoke test would miss.
def _render_page(page_module: str, mode: str = "internal"):  # runs inside AppTest.from_function
    import sys
    from pathlib import Path

    root = Path.cwd()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    import importlib

    from app import config, data, theme

    data.bind_mode(mode)
    theme.inject_css()
    opts = {"currency": "INR", "profile": config.default_profile(),
            "fy": None, "mode": mode}
    try:
        opts["fy"] = data.fiscal_years()[-1]
    except Exception:
        opts["fy"] = None
    mod = importlib.import_module(f"app.views.{page_module}")
    mod.render(opts)


@pytest.mark.slow
@pytest.mark.parametrize("page", [
    "decision_intelligence", "strategic", "forecasting",
    "geographic", "reports", "data_quality",
])
def test_each_page_renders(page):
    from streamlit.testing.v1 import AppTest

    at = AppTest.from_function(_render_page, kwargs={"page_module": page})
    at.run(timeout=600)
    assert not at.exception, f"{page} raised: {at.exception}"


# ── Privacy / anonymisation (public mode must never show real identities) ────
import re  # noqa: E402

_ANON = re.compile(r"^(Customer|Supplier|Salesman)_(U?\d+|UNMAPPED)$")


@pytest.mark.slow
@pytest.mark.skipif(not _shareable_db_available(),
                    reason="shareable warehouse not built")
def test_shareable_mode_anonymises_identities():
    """In shareable mode the data layer must return only anonymous identity codes
    — never a real customer/supplier name."""
    from app import data

    data.bind_mode("shareable")
    data.warehouse_exists.clear() if hasattr(data.warehouse_exists, "clear") else None
    try:
        # Customer-facing frames
        cust = data.profitability("customers", None, 50)
        codes = list(cust.top["customer_code"]) + list(cust.bottom["customer_code"])
        assert codes, "no customer rows returned"
        leaks = [c for c in codes if not _ANON.match(str(c))]
        assert not leaks, f"real customer names leaked in shareable mode: {leaks[:5]}"

        # ABC by supplier
        sup = data.abc("suppliers", None)
        # ABC returns aggregates by class, not names — just assert it runs clean.
        assert sup.n >= 0
    finally:
        data.bind_mode("internal")


@pytest.mark.slow
@pytest.mark.skipif(not _shareable_db_available(),
                    reason="shareable warehouse not built")
def test_pages_render_in_shareable_mode():
    from streamlit.testing.v1 import AppTest

    for page in ("decision_intelligence", "strategic", "geographic", "reports"):
        at = AppTest.from_function(_render_page,
                                   kwargs={"page_module": page, "mode": "shareable"})
        at.run(timeout=600)
        assert not at.exception, f"{page} (shareable) raised: {at.exception}"
