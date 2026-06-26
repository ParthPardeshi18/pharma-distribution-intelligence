"""Shared utilities: PII masking, robust ERP-Excel reading, paths, logging.

These helpers are used across every phase. Two non-negotiable concerns live here:

1. PII masking — NEVER print full personal data to console/logs. Use the mask_*
   helpers whenever a sample of real data is shown.
2. Robust ingestion — ERP exports carry a multi-row firm banner before the real
   header, and some files (e.g. Product_Master.xlsx) contain invalid UTF-8 bytes
   that break standard parsers. read_erp_excel() handles both.
"""
from __future__ import annotations

import io
import re
import sys
import zipfile
from pathlib import Path

import pandas as pd

# Windows consoles default to cp1252 and crash on Unicode (₹, ✅, →). Force UTF-8
# so every script that imports this module can print symbols safely.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    except Exception:
        pass

# --------------------------------------------------------------------------- #
# Paths (project-root relative; resolved from this file's location)
# --------------------------------------------------------------------------- #
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
WAREHOUSE_DIR = PROJECT_ROOT / "data" / "warehouse"
SECURE_DIR = PROJECT_ROOT / "data" / "secure"
REFERENCE_DIR = PROJECT_ROOT / "data" / "reference"
CONFIG_DIR = PROJECT_ROOT / "config"
DOCS_DIR = PROJECT_ROOT / "docs"
LOGS_DIR = PROJECT_ROOT / "logs"

# --------------------------------------------------------------------------- #
# PII masking helpers — mandatory before showing any real-data sample
# --------------------------------------------------------------------------- #
_PHONE_RE = re.compile(r"\d{6,}")
_EMAIL_RE = re.compile(r"([A-Za-z0-9._%+-])[A-Za-z0-9._%+-]*(@[A-Za-z0-9.-]+\.[A-Za-z]{2,})")


def mask_mobile(value: object) -> str:
    """Show first 2 + last 2 digits only: 9822270199 -> 98XXXXXX99."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    digits = re.sub(r"\D", "", str(value))
    if len(digits) < 4:
        return "X" * len(digits)
    return f"{digits[:2]}{'X' * (len(digits) - 4)}{digits[-2:]}"


def mask_name(value: object, prefix: str = "Name") -> str:
    """Mask a free-text name as <prefix>_<first char>***. Real codes come from the
    anonymisation lookup; this is only for ad-hoc console samples."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    s = str(value).strip()
    if not s:
        return ""
    return f"{prefix}_{s[0].upper()}***"


def mask_email(value: object) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    return _EMAIL_RE.sub(lambda m: f"{m.group(1)}***{m.group(2)}", str(value))


def mask_id(value: object) -> str:
    """Any ID/PAN/GST: last 4 chars only."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    s = str(value).strip()
    return ("*" * max(0, len(s) - 4)) + s[-4:] if s else ""


def mask_text_blob(text: str) -> str:
    """Mask phone-like and email-like substrings inside an arbitrary string
    (used for masking the firm banner / free-text cells in samples)."""
    if not isinstance(text, str):
        return text
    text = _EMAIL_RE.sub(lambda m: f"{m.group(1)}***{m.group(2)}", text)
    text = _PHONE_RE.sub(lambda m: mask_mobile(m.group(0)), text)
    return text


# --------------------------------------------------------------------------- #
# Robust ERP Excel reading
# --------------------------------------------------------------------------- #
# XML 1.0 illegal control chars (keep tab/lf/cr)
_ILLEGAL_XML = re.compile(rb"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def _recover_xlsx_bytes(path: Path) -> io.BytesIO:
    """Rebuild an .xlsx whose XML parts contain invalid UTF-8 bytes or illegal
    control chars (e.g. ERP wrote raw Latin-1 0xA0 into a UTF-8 stream).

    Each XML member is decoded as UTF-8 with replacement, illegal control chars
    stripped, then re-encoded. Returns an in-memory sanitized copy. Non-XML parts
    are copied verbatim.
    """
    src = zipfile.ZipFile(path)
    out_buf = io.BytesIO()
    with zipfile.ZipFile(out_buf, "w", zipfile.ZIP_DEFLATED) as dst:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename.endswith(".xml") or item.filename.endswith(".rels"):
                data = data.decode("utf-8", errors="replace").encode("utf-8")
                data = _ILLEGAL_XML.sub(b" ", data)
            dst.writestr(item, data)
    src.close()
    out_buf.seek(0)
    return out_buf


def file_needs_recovery(path: Path) -> bool:
    """Cheap check: does any XML part fail strict UTF-8 decoding?"""
    try:
        with zipfile.ZipFile(path) as z:
            for name in z.namelist():
                if name.endswith((".xml", ".rels")):
                    try:
                        z.read(name).decode("utf-8")
                    except UnicodeDecodeError:
                        return True
    except zipfile.BadZipFile:
        return False
    return False


def _read_raw(path: Path, sheet_name=0, nrows=None) -> pd.DataFrame:
    """read_excel with automatic recovery fallback for malformed files."""
    try:
        return pd.read_excel(path, sheet_name=sheet_name, header=None,
                             nrows=nrows, engine="openpyxl")
    except Exception:
        buf = _recover_xlsx_bytes(Path(path))
        return pd.read_excel(buf, sheet_name=sheet_name, header=None,
                             nrows=nrows, engine="openpyxl")


def detect_header_row(df_raw: pd.DataFrame, scan: int = 30) -> int:
    """Locate the real header row beneath the ERP banner.

    Heuristic: the header is the first row that (a) reaches the table's full
    width (max non-null count seen in the scan window) and (b) is entirely
    text — data rows below it contain dates/numbers, banner rows above it have
    only 1-2 populated cells.
    """
    window = df_raw.head(scan)
    non_null = window.notna().sum(axis=1)
    full_width = int(non_null.max())
    for idx in window.index:
        row = window.loc[idx]
        values = [v for v in row.tolist() if pd.notna(v)]
        if len(values) >= max(2, full_width - 1) and all(isinstance(v, str) for v in values):
            return int(idx)
    # Fallback: first row reaching full width
    return int(non_null.idxmax())


def _dedupe_columns(names: list[str]) -> list[str]:
    """Make column names unique (ERP T-format reports repeat e.g. 'Amount')."""
    seen: dict[str, int] = {}
    out: list[str] = []
    for n in names:
        if n in seen:
            seen[n] += 1
            out.append(f"{n}.{seen[n]}")
        else:
            seen[n] = 0
            out.append(n)
    return out


def read_erp_excel(path: str | Path, sheet_name=0, header_row: int | None = None) -> pd.DataFrame:
    """Read an ERP export into a clean DataFrame with the real header applied.

    - Strips the firm banner / title rows automatically (or uses header_row).
    - Recovers malformed (invalid-UTF-8) workbooks transparently.
    - Returns rows below the header; trailing all-empty rows dropped.
    """
    path = Path(path)
    raw = _read_raw(path, sheet_name=sheet_name)
    hdr = header_row if header_row is not None else detect_header_row(raw)
    header = [str(c).strip() if pd.notna(c) else f"col_{i}"
              for i, c in enumerate(raw.iloc[hdr].tolist())]
    header = _dedupe_columns(header)
    df = raw.iloc[hdr + 1:].copy()
    df.columns = header
    df = df.dropna(how="all").reset_index(drop=True)
    return df
