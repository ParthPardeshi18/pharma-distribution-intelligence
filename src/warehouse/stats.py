"""Warehouse statistics generator -> reports/warehouse_statistics.md.

Post-load operational statistics: row counts, storage size, relationship counts,
orphan detection, processing duration, and the reconciliation summary.
"""
from __future__ import annotations

import datetime as dt

from src.utils import PROJECT_ROOT
from src.warehouse import metrics
from src.warehouse.db import make_engine

REPORT_PATH = PROJECT_ROOT / "reports" / "warehouse_statistics.md"


def generate(build_result=None) -> str:
    engine = make_engine()
    rc = metrics.table_row_counts(engine)
    size = metrics.db_size_bytes()
    batch = metrics.latest_batch(engine)
    orph = metrics.orphans(engine)

    lines = ["# Warehouse Statistics", ""]
    lines.append(f"> Generated {dt.date.today():%Y-%m-%d} from `erp_warehouse.db`.")
    lines.append("")

    # Build summary
    lines.append("## Build summary (latest batch)")
    lines.append("")
    if batch:
        dur = _duration(batch.get("started_at"), batch.get("finished_at"))
        lines.append(f"- Batch id: `{batch.get('import_batch_id')}`")
        lines.append(f"- Mode: **{batch.get('mode')}** · reporting currency: "
                     f"**{batch.get('reporting_currency')}**")
        lines.append(f"- Status: **{batch.get('status')}**")
        lines.append(f"- Processing duration: **{dur}**")
        lines.append(f"- Tables: {batch.get('n_tables')} · rows: {batch.get('n_rows'):,}")
    lines.append(f"- Storage size: **{size/1024/1024:.2f} MB** ({size:,} bytes)")
    lines.append("")

    # Row counts
    dims = {t: n for t, n in rc.items() if t.startswith("dim_")}
    facts = {t: n for t, n in rc.items() if t.startswith("fact_")}
    lines.append("## Row counts")
    lines.append("")
    lines.append(f"- Dimensions: {len(dims)} tables, {sum(dims.values()):,} rows")
    lines.append(f"- Facts: {len(facts)} tables, {sum(facts.values()):,} rows")
    lines.append("")
    lines.append("| Table | Rows |")
    lines.append("|---|--:|")
    for t in sorted(rc):
        lines.append(f"| {t} | {rc[t]:,} |")
    lines.append("")

    # Relationships
    lines.append("## Relationships & orphan detection")
    lines.append("")
    total_links = sum(o["rows"] - o["null_keys"] for o in orph)
    total_orphans = sum(o["orphan_keys"] for o in orph)
    total_unmatched = sum(o["null_keys"] for o in orph)
    lines.append(f"- Fact→dimension foreign keys checked: **{len(orph)}**")
    lines.append(f"- Resolved relationships (non-null keys): **{total_links:,}**")
    lines.append(f"- Orphan keys (key not in dim): **{total_orphans:,}** "
                 f"{'✅' if total_orphans == 0 else '⚠️'}")
    lines.append(f"- Unmatched (null) keys: **{total_unmatched:,}**")
    lines.append("")
    lines.append("| Fact | FK | Rows | Resolved | Null | Orphan |")
    lines.append("|---|---|--:|--:|--:|--:|")
    for o in orph:
        lines.append(f"| {o['table']} | {o['fk']} | {o['rows']:,} | "
                     f"{o['rows']-o['null_keys']:,} | {o['null_keys']:,} | {o['orphan_keys']:,} |")
    lines.append("")

    # Reconciliation
    if build_result and build_result.reconciliation:
        lines.append("## Reconciliation summary")
        lines.append("")
        npass = sum(c["status"] == "PASS" for c in build_result.reconciliation)
        lines.append(f"- **{npass}/{len(build_result.reconciliation)} checks PASS** "
                     "(warehouse fact totals == raw ERP totals).")
        lines.append("")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    return str(REPORT_PATH)


def _duration(start, end) -> str:
    try:
        s = dt.datetime.fromisoformat(str(start))
        e = dt.datetime.fromisoformat(str(end))
        return f"{(e - s).total_seconds():.1f}s"
    except Exception:
        return "—"


if __name__ == "__main__":
    print("Statistics report:", generate())
