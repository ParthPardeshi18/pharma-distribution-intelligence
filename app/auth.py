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
    """The signed-in (staff) user, if any."""
    import streamlit as st

    return st.session_state.get(_SESSION_KEY)


def guest_user():  # -> User | None
    """Synthetic guest from auth.guest_role, or None if open access is disabled."""
    role = (config.app_config().get("auth", {}).get("guest_role") or "").strip()
    if not role:
        return None
    return User(username="guest", name="Guest", role=role)


def is_guest(user) -> bool:
    return user is not None and user.username == "guest"


def logout() -> None:
    import streamlit as st

    st.session_state.pop(_SESSION_KEY, None)
    st.cache_data.clear()
    st.cache_resource.clear()


def login_gate():  # -> User
    """Resolve the active user without a login wall.

    Order: signed-in staff → guest (open access) → full-page login (only when no
    guest role is configured). Staff elevate via the sidebar control instead.
    If auth is disabled entirely, returns a synthetic admin.
    """
    import streamlit as st

    if not config.app_config().get("auth", {}).get("enabled", True):
        return User(username="local", name="Local User", role="admin")

    user = current_user()
    if user is not None:
        return user

    guest = guest_user()
    if guest is not None:
        return guest  # open access — no stop

    # No guest role configured → require a login.
    return _full_page_login()


def _full_page_login():  # -> User (or st.stop)
    import streamlit as st

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
    st.stop()


def sidebar_login(user) -> None:
    """Staff sign-in / sign-out control for the sidebar.

    A guest sees a collapsed 'Staff sign in' expander; signed-in staff see a
    'Sign out' button (returns to the guest experience)."""
    import streamlit as st

    if is_guest(user):
        with st.expander("🔐 Staff sign in"):
            with st.form("pdi_staff_login", clear_on_submit=False):
                username = st.text_input("Username", autocomplete="username")
                password = st.text_input("Password", type="password",
                                         autocomplete="current-password")
                submitted = st.form_submit_button("Sign in", type="primary")
            if submitted:
                u = verify(username.strip(), password)
                if u is None:
                    st.error("Invalid username or password.")
                else:
                    st.session_state[_SESSION_KEY] = u
                    st.cache_data.clear()
                    st.rerun()
    else:
        if st.button("Sign out", width="stretch"):
            logout()
            st.rerun()
