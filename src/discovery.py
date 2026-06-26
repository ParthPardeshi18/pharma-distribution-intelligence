"""Phase 0 discovery scanner.

Walks data/raw/, profiles every ERP export (sheets, detected header row,
columns, row count, date coverage, key financial totals) and writes
docs/discovery_report.md with ALL personal data masked.

Run:  python -m src.discovery
"""
from __future__ import annotations

import datetime as dt
from pathlib import Path

import pandas as pd

from src.utils import (
    DOCS_DIR,
    RAW_DIR,
    file_needs_recovery,
    mask_email,
    mask_id,
    mask_mobile,
    mask_name,
    mask_text_blob,
    read_erp_excel,
)

# Columns treated as sensitive when displaying a sample row.
PII_COLUMNS = {
    "mobile": ("mobile", "telephone", "phone", "contact"),
    "email": ("email", "e-mail", "mail"),
    "id": ("alias", "ie code", "code", "gst", "pan", "tin",
           "bill no", "bill", "invoice", "inv no"),
    "name": ("customer name", "cust name", "supplier", "party", "salesman",
             "sales man", "account", "name"),
    "address": ("address", "addr", "city", "area", "place"),
}

# Column-name fragments that indicate a money amount, for key-total reconciliation.
AMOUNT_HINTS = ("net", "amount", "amt", "value", "sale", "purchase", "profit",
                "cost", "balance", "outstanding", "qty", "total", "billed")

DATE_HINTS = ("date", "dt")


def classify_pii(col: str) -> str | None:
    c = col.strip().lower()
    for kind, hints in PII_COLUMNS.items():
        if any(h in c for h in hints):
            # Avoid masking pure-numeric business columns that merely contain 'name'?
            return kind
    return None


def mask_value(kind: str, value: object) -> str:
    if kind == "mobile":
        return mask_mobile(value)
    if kind == "email":
        return mask_email(value)
    if kind == "id":
        return mask_id(value)
    if kind == "name":
        return mask_name(value)
    if kind == "address":
        return mask_text_blob(str(value)) if pd.notna(value) else ""
    return str(value)


def masked_sample(df: pd.DataFrame, n: int = 3) -> pd.DataFrame:
    out = df.head(n).copy()
    for col in out.columns:
        kind = classify_pii(col)
        if kind:
            out[col] = out[col].map(lambda v: mask_value(kind, v))
    return out


def find_date_range(df: pd.DataFrame) -> str:
    for col in df.columns:
        if any(h in col.lower() for h in DATE_HINTS):
            s = pd.to_datetime(df[col], errors="coerce")
            if s.notna().sum() > 0:
                return f"{s.min():%Y-%m-%d} → {s.max():%Y-%m-%d} (col: {col})"
    return "—"


def key_totals(df: pd.DataFrame) -> dict[str, float]:
    totals: dict[str, float] = {}
    for col in df.columns:
        if any(h in col.lower() for h in AMOUNT_HINTS):
            s = pd.to_numeric(df[col], errors="coerce")
            if s.notna().sum() > 0:
                totals[col] = round(float(s.sum()), 2)
    return totals


def scan_file(path: Path) -> dict:
    rel = path.relative_to(RAW_DIR)
    size_kb = path.stat().st_size / 1024
    info: dict = {
        "path": str(rel).replace("\\", "/"),
        "size_kb": round(size_kb, 1),
        "needs_recovery": file_needs_recovery(path),
        "error": None,
    }
    try:
        xl = pd.ExcelFile(path) if not info["needs_recovery"] else None
        info["sheets"] = xl.sheet_names if xl else ["(recovered)"]
    except Exception:
        info["sheets"] = ["(recovered)"]
    try:
        df = read_erp_excel(path)
        info["rows"] = len(df)
        info["columns"] = list(df.columns)
        info["date_range"] = find_date_range(df)
        info["key_totals"] = key_totals(df)
        info["sample"] = masked_sample(df)
    except Exception as exc:  # pragma: no cover - defensive
        info["error"] = f"{type(exc).__name__}: {exc}"
    return info


def render_report(results: list[dict]) -> str:
    lines: list[str] = []
    lines.append("# ERP Data Discovery Report")
    lines.append("")
    lines.append("> **Firm:** Sukhakarta Distributors · pharmaceutical distribution.  ")
    lines.append("> All personal/commercial identifiers below are **MASKED**. "
                 "No raw PII appears in this document.  ")
    lines.append(f"> Generated: {dt.date.today():%Y-%m-%d} · Source: `data/raw/` (read-only).")
    lines.append("")

    # Summary table
    lines.append("## Summary")
    lines.append("")
    lines.append("| File | Size (KB) | Rows | Cols | Date range | Recover? |")
    lines.append("|---|--:|--:|--:|---|:--:|")
    for r in sorted(results, key=lambda x: x["path"]):
        cols = len(r.get("columns", [])) if not r["error"] else "ERR"
        rows = r.get("rows", "ERR") if not r["error"] else "ERR"
        dr = r.get("date_range", "—") if not r["error"] else "—"
        flag = "⚠️ yes" if r["needs_recovery"] else "no"
        lines.append(f"| `{r['path']}` | {r['size_kb']} | {rows} | {cols} | {dr} | {flag} |")
    lines.append("")

    total_files = len(results)
    recovered = sum(1 for r in results if r["needs_recovery"])
    errored = sum(1 for r in results if r["error"])
    lines.append(f"**{total_files} files scanned · {recovered} required XML recovery · "
                 f"{errored} unreadable.**")
    lines.append("")

    # Per-file detail
    lines.append("## File details")
    lines.append("")
    for r in sorted(results, key=lambda x: x["path"]):
        lines.append(f"### `{r['path']}`")
        lines.append("")
        lines.append(f"- Size: {r['size_kb']} KB · Sheets: {', '.join(map(str, r['sheets']))}")
        if r["needs_recovery"]:
            lines.append("- ⚠️ **Malformed XML** (invalid UTF-8 bytes from ERP export) — "
                         "read via sanitizing recovery reader.")
        if r["error"]:
            lines.append(f"- ❌ **Unreadable:** {r['error']}")
            lines.append("")
            continue
        lines.append(f"- Rows: {r['rows']} · Columns ({len(r['columns'])}): "
                     + ", ".join(f"`{c}`" for c in r["columns"]))
        lines.append(f"- Date range: {r['date_range']}")
        if r["key_totals"]:
            kt = " · ".join(f"`{k}` = {v:,.2f}" for k, v in r["key_totals"].items())
            lines.append(f"- Key totals: {kt}")
        lines.append("")
        lines.append("Masked sample (first 3 rows):")
        lines.append("")
        lines.append(r["sample"].to_markdown(index=False))
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    files = sorted(RAW_DIR.rglob("*.xlsx"))
    print(f"Scanning {len(files)} files in {RAW_DIR} ...")
    results = []
    for f in files:
        r = scan_file(f)
        status = "ERR" if r["error"] else ("RECOVERED" if r["needs_recovery"] else "ok")
        print(f"  [{status:9s}] {r['path']:55s} rows={r.get('rows','-')}")
        results.append(r)

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    out = DOCS_DIR / "discovery_report.md"
    out.write_text(render_report(results), encoding="utf-8")
    print(f"\nDiscovery report written: {out}")
    print(f"Files: {len(results)} | recovered: {sum(r['needs_recovery'] for r in results)} | "
          f"errors: {sum(bool(r['error']) for r in results)}")


if __name__ == "__main__":
    main()
