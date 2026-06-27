"""Optional Claude-powered narrative enhancer.

The app's executive narratives **always** come from the local Decision
Intelligence engine and need no network. This module is a strictly optional
polish layer: when ``ai_summary.enabled`` is true in ``config/app_config.yaml``
and an Anthropic API key is available, it rewrites the engine's bullet narrative
into board-ready prose. It degrades silently (returns ``None``) whenever the
``anthropic`` SDK is absent, no key is configured, or the call fails — the
engine narrative is never blocked on it.

Implements the Claude API per the official Anthropic Python SDK: model
``claude-opus-4-8`` with adaptive thinking.
"""
from __future__ import annotations

import os

from app import config


def _api_key() -> str | None:
    try:
        import streamlit as st

        if "anthropic" in st.secrets and "api_key" in st.secrets["anthropic"]:
            return str(st.secrets["anthropic"]["api_key"])
    except Exception:
        pass
    return os.environ.get("ANTHROPIC_API_KEY")


def available() -> bool:
    cfg = config.app_config().get("ai_summary", {})
    if not cfg.get("enabled", False):
        return False
    if _api_key() is None:
        return False
    try:
        import anthropic  # noqa: F401
    except Exception:
        return False
    return True


def enhance(narrative_md: str, *, context: str = "") -> str | None:
    """Rewrite an engine narrative into polished executive prose. Returns ``None``
    if the enhancer is unavailable or the call fails (caller keeps the original)."""
    if not available():
        return None

    cfg = config.app_config().get("ai_summary", {})
    model = cfg.get("model", "claude-opus-4-8")
    max_tokens = int(cfg.get("max_tokens", 1024))

    system = (
        "You are an executive business-writing assistant for a pharmaceutical "
        "distribution company. Rewrite the analyst's findings into a concise, "
        "board-ready briefing of 2-4 short paragraphs. Preserve every number and "
        "fact exactly; do not invent figures or recommendations. Plain, direct "
        "prose — no markdown headers, no bullet lists."
    )
    user = narrative_md if not context else f"Context: {context}\n\nFindings:\n{narrative_md}"

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=_api_key())
        resp = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            thinking={"type": "adaptive"},
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        if getattr(resp, "stop_reason", None) == "refusal":
            return None
        return "".join(b.text for b in resp.content if getattr(b, "type", None) == "text").strip() or None
    except Exception:
        return None
