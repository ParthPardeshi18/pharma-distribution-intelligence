"""Demo-data bootstrap for public deployments.

On a hosted public demo (e.g. Streamlit Community Cloud) the repository carries no
warehouse — real data is gitignored and never published. Instead, the **anonymised**
warehouse is published once as a GitHub Release asset, and this module downloads it
into the runtime on first start.

It runs only in ``shareable`` mode and only when a demo URL is configured, so it can
never pull real data and is a no-op on a normal internal install.
"""
from __future__ import annotations

import os
import tempfile
import urllib.request
from pathlib import Path

import streamlit as st

from app import config, data


def _demo_url() -> str | None:
    # secrets → env → config
    try:
        if "demo" in st.secrets and "db_url" in st.secrets["demo"]:
            return str(st.secrets["demo"]["db_url"])
    except Exception:
        pass
    return os.environ.get("DEMO_DB_URL") or config.app_config().get("demo", {}).get("db_url")


def _download(url: str, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".part")
    req = urllib.request.Request(url, headers={"User-Agent": "pdi-demo-bootstrap"})
    with urllib.request.urlopen(req, timeout=120) as resp, open(tmp, "wb") as fh:  # noqa: S310
        while chunk := resp.read(1 << 20):  # 1 MiB
            fh.write(chunk)
    os.replace(tmp, target)  # atomic


def ensure_demo_data(mode: str) -> None:
    """If running the public demo and the anonymised warehouse is absent, fetch it.

    No-op unless: mode is ``shareable``, the warehouse file is missing, and a demo
    URL is configured. Shows a one-time spinner; on failure shows a clear message
    and stops (never falls back to real data — there is none on a public host)."""
    if mode != "shareable" or data.warehouse_exists():
        return
    url = _demo_url()
    if not url:
        return  # let the page show its normal "warehouse not built" notice

    target = data.active_db_path()
    # Guard against concurrent cold-start sessions double-downloading.
    lock = target.with_suffix(".lock")
    if lock.exists():
        return
    try:
        lock.parent.mkdir(parents=True, exist_ok=True)
        lock.write_text("downloading", encoding="utf-8")
        with st.spinner("Loading anonymised demo data (first run only)…"):
            _download(url, target)
    except Exception as exc:  # noqa: BLE001
        st.error(f"Could not load demo data from the configured URL.\n\n`{exc}`")
        st.stop()
    finally:
        try:
            lock.unlink()
        except OSError:
            pass
    # Fresh download → clear any cached "missing warehouse" state.
    st.cache_data.clear()
