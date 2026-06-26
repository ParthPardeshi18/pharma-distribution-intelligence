"""Data Quality Dashboard generator.

Produces a self-contained HTML dashboard + a CSV metrics export for Power BI:
- completeness (% non-null) per table
- duplicate rates on natural keys
- unmatched entities (null fact keys + customer match-tier breakdown)
- reconciliation status
- processing statistics

Outputs:
  reports/data_quality_dashboard.html
  data/warehouse/exports/quality_metrics.csv
Run:  python -m src.quality
"""
from __future__ import annotations

import datetime as dt
import json

import pandas as pd

from src.utils import LOGS_DIR, PROJECT_ROOT, WAREHOUSE_DIR
from src.warehouse import metrics
from src.warehouse.db import make_engine
from src.warehouse.schema import buildable_tables

HTML_PATH = PROJECT_ROOT / "reports" / "data_quality_dashboard.html"
CSV_PATH = WAREHOUSE_DIR / "exports" / "quality_metrics.csv"


def load_build_summary() -> dict:
    p = LOGS_DIR / "last_build.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {}


def collect_metrics(engine) -> dict:
    rc = metrics.table_row_counts(engine)
    orph = metrics.orphans(engine)
    summary = load_build_summary()

    # completeness per table (avg over columns)
    completeness_rows = []
    for tspec in buildable_tables():
        df = metrics.read_table(engine, tspec.name)
        if df.empty:
            continue
        avg = round(float(df.notna().mean().mean()) * 100, 1)
        completeness_rows.append({"table": tspec.name, "completeness_pct": avg})

    # duplicate rates
    dup_rows = [dict(table=t.name, **metrics.duplicate_rate(engine, t.name))
                for t in buildable_tables() if t.role in ("fact", "dimension")]

    # unmatched entities
    unmatched = [{"table": o["table"], "fk": o["fk"], "null_keys": o["null_keys"],
                  "rows": o["rows"],
                  "unmatched_pct": round(100 * o["null_keys"] / max(1, o["rows"]), 2)}
                 for o in orph]

    # customer match-tier breakdown
    tiers = {}
    try:
        cust = metrics.read_table(engine, "dim_customer")
        if "match_tier" in cust.columns:
            tiers = cust["match_tier"].value_counts().to_dict()
    except Exception:
        pass

    return {"row_counts": rc, "completeness": completeness_rows, "duplicates": dup_rows,
            "unmatched": unmatched, "match_tiers": tiers, "orphans": orph,
            "build": summary, "db_mb": round(metrics.db_size_bytes() / 1024 / 1024, 2)}


def _kpi_cards(m: dict) -> str:
    recon = m["build"].get("reconciliation", [])
    npass = sum(c["status"] == "PASS" for c in recon)
    total_orphans = sum(o["orphan_keys"] for o in m["orphans"])
    total_rows = sum(m["row_counts"].values())
    avg_complete = round(sum(r["completeness_pct"] for r in m["completeness"])
                         / max(1, len(m["completeness"])), 1)
    cards = [
        ("Total rows", f"{total_rows:,}", "ok"),
        ("Reconciliation", f"{npass}/{len(recon)} PASS" if recon else "n/a",
         "ok" if recon and npass == len(recon) else "warn"),
        ("Orphan keys", f"{total_orphans:,}", "ok" if total_orphans == 0 else "bad"),
        ("Avg completeness", f"{avg_complete}%", "ok" if avg_complete > 85 else "warn"),
        ("DB size", f"{m['db_mb']} MB", "ok"),
    ]
    return "".join(
        f'<div class="card {c}"><div class="v">{v}</div><div class="l">{l}</div></div>'
        for l, v, c in cards)


def _table(headers, rows) -> str:
    h = "".join(f"<th>{x}</th>" for x in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f"<table><thead><tr>{h}</tr></thead><tbody>{body}</tbody></table>"


def render_html(m: dict) -> str:
    recon = m["build"].get("reconciliation", [])
    recon_rows = [(c["table"], c["measure"], f"{c['raw_total']:,.0f}",
                   f"{c['warehouse_total']:,.0f}", c["status"]) for c in recon]
    comp_rows = [(r["table"], f"{r['completeness_pct']}%") for r in sorted(
        m["completeness"], key=lambda x: x["completeness_pct"])]
    dup_rows = [(d["table"], ",".join(d["key"]) or "—", d["rows"], d["duplicates"],
                 f"{d['dup_pct']}%") for d in m["duplicates"]]
    unm_rows = [(u["table"], u["fk"], u["null_keys"], f"{u['unmatched_pct']}%")
                for u in m["unmatched"] if u["null_keys"] > 0]
    tier_rows = [(k, f"{v:,}") for k, v in sorted(m["match_tiers"].items(),
                                                  key=lambda x: -x[1])]
    build = m["build"]
    return f"""<!doctype html><html><head><meta charset="utf-8">
<title>Data Quality Dashboard — ERP Warehouse</title>
<style>
 body{{font-family:'Segoe UI',Arial,sans-serif;margin:0;background:#0f172a;color:#e2e8f0}}
 header{{padding:24px 32px;background:#1e293b;border-bottom:3px solid #38bdf8}}
 h1{{margin:0;font-size:22px}} .sub{{color:#94a3b8;font-size:13px;margin-top:4px}}
 .cards{{display:flex;gap:16px;flex-wrap:wrap;padding:24px 32px}}
 .card{{background:#1e293b;border-radius:10px;padding:18px 22px;min-width:150px;border-left:4px solid #475569}}
 .card .v{{font-size:24px;font-weight:700}} .card .l{{color:#94a3b8;font-size:12px;margin-top:4px}}
 .card.ok{{border-left-color:#22c55e}} .card.warn{{border-left-color:#f59e0b}} .card.bad{{border-left-color:#ef4444}}
 section{{padding:8px 32px 24px}} h2{{font-size:16px;border-bottom:1px solid #334155;padding-bottom:6px}}
 table{{width:100%;border-collapse:collapse;font-size:13px;margin-top:8px}}
 th,td{{text-align:left;padding:7px 10px;border-bottom:1px solid #1e293b}}
 th{{color:#7dd3fc;font-weight:600}} td:nth-child(n+3){{text-align:right}}
 .footer{{padding:18px 32px;color:#64748b;font-size:12px}}
</style></head><body>
<header><h1>Data Quality Dashboard — ERP Warehouse</h1>
<div class="sub">Mode: {build.get('mode','?')} · Currency: {build.get('reporting_currency','?')}
 · Batch {build.get('batch_id','?')} · Generated {dt.date.today():%Y-%m-%d}</div></header>
<div class="cards">{_kpi_cards(m)}</div>
<section><h2>Reconciliation (raw ERP vs warehouse)</h2>
{_table(['Table','Measure','Raw ₹','Warehouse ₹','Status'], recon_rows) if recon_rows else '<p>No reconciliation data.</p>'}</section>
<section><h2>Customer entity resolution (match tiers)</h2>
{_table(['Tier','Count'], tier_rows) if tier_rows else '<p>n/a</p>'}</section>
<section><h2>Unmatched entities (null foreign keys)</h2>
{_table(['Fact','FK','Null keys','Unmatched %'], unm_rows) if unm_rows else '<p>None — all keys matched.</p>'}</section>
<section><h2>Completeness (avg % non-null per table)</h2>
{_table(['Table','Completeness'], comp_rows)}</section>
<section><h2>Duplicate rates (on natural key)</h2>
{_table(['Table','Natural key','Rows','Duplicates','Dup %'], dup_rows)}</section>
<div class="footer">Generated by src/quality.py from erp_warehouse.db. No PII — metrics only.</div>
</body></html>"""


def generate() -> tuple[str, str]:
    engine = make_engine()
    m = collect_metrics(engine)
    HTML_PATH.parent.mkdir(parents=True, exist_ok=True)
    HTML_PATH.write_text(render_html(m), encoding="utf-8")

    # CSV export for Power BI: long-format metric table
    rows = []
    for r in m["completeness"]:
        rows.append({"metric": "completeness_pct", "table": r["table"],
                     "value": r["completeness_pct"]})
    for d in m["duplicates"]:
        rows.append({"metric": "duplicate_pct", "table": d["table"], "value": d["dup_pct"]})
    for u in m["unmatched"]:
        rows.append({"metric": "unmatched_pct", "table": f"{u['table']}.{u['fk']}",
                     "value": u["unmatched_pct"]})
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(CSV_PATH, index=False, encoding="utf-8")
    return str(HTML_PATH), str(CSV_PATH)


if __name__ == "__main__":
    html, csv = generate()
    print("DQ dashboard:", html)
    print("Metrics CSV: ", csv)
