"""Application configuration loader.

Reads ``config/app_config.yaml`` (committed, no secrets) and the gitignored
``config/app_users.yaml`` (real credentials). The auth salt may be overridden
out-of-band by ``st.secrets['auth']['salt']`` or the ``AUTH_SALT`` env var so the
committed default never has to be the production salt.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "config"
APP_CONFIG = CONFIG_DIR / "app_config.yaml"
APP_USERS = CONFIG_DIR / "app_users.yaml"
APP_USERS_EXAMPLE = CONFIG_DIR / "app_users.example.yaml"


@lru_cache(maxsize=1)
def app_config() -> dict:
    with open(APP_CONFIG, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


@lru_cache(maxsize=1)
def users() -> dict:
    """User store. Falls back to the committed example if no local copy exists,
    so a fresh checkout still launches (with documented default passwords)."""
    path = APP_USERS if APP_USERS.exists() else APP_USERS_EXAMPLE
    with open(path, encoding="utf-8") as fh:
        return (yaml.safe_load(fh) or {}).get("users", {})


def auth_salt() -> str:
    """Resolve the password salt: secrets → env → config default."""
    # st.secrets access is deferred so this module imports cleanly outside a
    # Streamlit runtime (e.g. in pytest).
    try:
        import streamlit as st

        if "auth" in st.secrets and "salt" in st.secrets["auth"]:
            return str(st.secrets["auth"]["salt"])
    except Exception:
        pass
    return os.environ.get("AUTH_SALT") or app_config().get("auth", {}).get("salt", "")


def current_mode() -> str:
    """Resolve the data-presentation mode.

    Precedence: ``PDI_MODE`` env (deploy-time override) → ``app.mode`` in config.
      internal  → real customer/supplier/salesman identities (firm's own use)
      shareable → anonymised identities (Customer_0001 …); for public / LinkedIn

    A public deployment **must** run in ``shareable`` mode (and ship only the
    anonymised warehouse) so no real identity is ever served.
    """
    env = os.environ.get("PDI_MODE")
    if env in ("internal", "shareable"):
        return env
    mode = app_config().get("app", {}).get("mode", "internal")
    return mode if mode in ("internal", "shareable") else "internal"


def real_data_roles() -> list[str]:
    """Roles allowed to view real (internal) identities. Everyone else is forced
    to the anonymised warehouse."""
    return app_config().get("auth", {}).get("real_data_roles", ["admin"])


def effective_mode(role: str, base_mode: str) -> str:
    """The data mode a given role actually gets.

    A role NOT in ``real_data_roles`` is pinned to ``shareable`` no matter what the
    app is configured for — so a viewer can never be shown PII, even on the firm's
    internal deployment. Allowed roles get ``base_mode`` (config/env, default
    internal; an admin may further preview shareable).
    """
    if role in real_data_roles():
        return base_mode
    return "shareable"


def role_pages(role: str) -> list[str]:
    return app_config().get("auth", {}).get("roles", {}).get(role, [])


def currency_options() -> list[str]:
    return app_config().get("currency", {}).get("options", ["INR"])


def default_profile() -> str:
    return app_config().get("health_index", {}).get("default_profile", "balanced")
