"""Authentication + role-based access control for the Streamlit app.

The pure helpers (``hash_password``, ``verify``) carry no Streamlit dependency so
they can be unit-tested directly. The UI helpers (``login_gate``, ``current_user``,
``logout``) drive ``st.session_state``.
"""
from __future__ import annotations

import hashlib
import hmac
from dataclasses import dataclass

from app import config


# ── Pure logic (testable without Streamlit) ─────────────────────────────────
def hash_password(password: str, salt: str) -> str:
    return hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()


def verify(username: str, password: str, *, salt: str | None = None,
           store: dict | None = None) -> "User | None":
    """Return a :class:`User` on success, else ``None``. Constant-time compare."""
    salt = config.auth_salt() if salt is None else salt
    store = config.users() if store is None else store
    rec = store.get(username)
    if not rec:
        return None
    expected = str(rec.get("password_sha256", ""))
    got = hash_password(password, salt)
    if not expected or not hmac.compare_digest(expected, got):
        return None
    return User(username=username, name=rec.get("name", username),
                role=rec.get("role", "viewer"))


@dataclass(frozen=True)
class User:
    username: str
    name: str
    role: str

    @property
    def pages(self) -> list[str]:
        return config.role_pages(self.role)

    def can(self, page_key: str) -> bool:
        return page_key in self.pages


# ── Streamlit UI / session ──────────────────────────────────────────────────
_SESSION_KEY = "pdi_user"


def current_user():  # -> User | None
    import streamlit as st

    return st.session_state.get(_SESSION_KEY)


def logout() -> None:
    import streamlit as st

    st.session_state.pop(_SESSION_KEY, None)
    st.cache_data.clear()


def login_gate():  # -> User
    """Render the login form and block until authenticated. Returns the User.

    If auth is disabled in config, returns a synthetic admin so the app is
    usable in trusted, single-user deployments.
    """
    import streamlit as st

    if not config.app_config().get("auth", {}).get("enabled", True):
        return User(username="local", name="Local User", role="admin")

    user = current_user()
    if user is not None:
        return user

    cfg = config.app_config().get("app", {})
    st.markdown(f"## {cfg.get('name', 'Platform')} — Sign in")
    st.caption("Pharmaceutical Distribution Intelligence Platform · v1.1")

    with st.form("pdi_login", clear_on_submit=False):
        username = st.text_input("Username", autocomplete="username")
        password = st.text_input("Password", type="password", autocomplete="current-password")
        submitted = st.form_submit_button("Sign in", type="primary")

    if submitted:
        u = verify(username.strip(), password)
        if u is None:
            st.error("Invalid username or password.")
        else:
            st.session_state[_SESSION_KEY] = u
            st.rerun()

    with st.expander("Demo credentials"):
        st.markdown(
            "- **admin / admin123** — full access\n"
            "- **analyst / analyst123** — all analytics, no admin pages\n"
            "- **viewer / viewer123** — read-only dashboards\n\n"
            "_Change these before any real deployment (see "
            "`config/app_users.example.yaml`)._"
        )
    st.stop()
