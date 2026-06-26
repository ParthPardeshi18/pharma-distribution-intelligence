"""Generate documentation from the schema registry (single source of truth):
- docs/data_dictionary.md          — every table & column, types, descriptions
- docs/business_metadata_catalog.md — business view: KPIs, relationships,
                                       definitions, source ERP report per table

Because both are generated from `SCHEMA`, they can never drift from the database.
Run:  python -m src.warehouse.catalog
"""
from __future__ import annotations

import datetime as dt

from src.utils import DOCS_DIR
from src.warehouse.schema import SCHEMA, STANDARD_COLUMNS, buildable_tables


def _gen_data_dictionary() -> str:
    lines = ["# Data Dictionary", ""]
    lines.append(f"> Generated {dt.date.today():%Y-%m-%d} from `src/warehouse/schema.py`. "
                 "Do not edit by hand — regenerate with `python -m src.warehouse.catalog`.")
    lines.append("")
    lines.append("Every business table also carries the **standard lineage/audit/quality "
                 "columns** listed once at the end.")
    lines.append("")
    for t in SCHEMA:
        tag = "" if t.build_now else " · *(future extension point — not built yet)*"
        lines.append(f"## `{t.name}` — {t.role}{tag}")
        lines.append("")
        lines.append(f"*{t.description}*  ")
        lines.append(f"**Grain:** {t.grain}  ")
        lines.append(f"**Source:** {t.source_report}")
        lines.append("")
        lines.append("| Column | Type | Key | Description |")
        lines.append("|---|---|:--:|---|")
        for c in t.columns:
            k = "🔑" if c.is_key else ("FK" if c.is_fk else "")
            unit = " *(INR)*" if c.currency_inr else ""
            lines.append(f"| `{c.name}` | {c.sqltype} | {k} | {c.description}{unit} |")
        lines.append("")
    # standard columns once
    lines.append("## Standard columns (on every business table)")
    lines.append("")
    lines.append("| Column | Type | Purpose |")
    lines.append("|---|---|---|")
    for c in STANDARD_COLUMNS:
        lines.append(f"| `{c.name}` | {c.sqltype} | {c.description} |")
    lines.append("")
    return "\n".join(lines)


def _gen_business_catalog() -> str:
    lines = ["# Business Metadata Catalog", ""]
    lines.append(f"> Generated {dt.date.today():%Y-%m-%d}. The business-facing companion "
                 "to the data dictionary: what each table means, its KPIs, how it links, "
                 "and which ERP report it comes from.")
    lines.append("")

    # Overview table
    lines.append("## Tables at a glance")
    lines.append("")
    lines.append("| Table | Role | Grain | Source ERP report |")
    lines.append("|---|---|---|---|")
    for t in SCHEMA:
        if not t.build_now:
            continue
        lines.append(f"| `{t.name}` | {t.role} | {t.grain} | {t.source_report} |")
    lines.append("")

    # KPIs
    lines.append("## Headline business measures (KPIs)")
    lines.append("")
    lines.append("| Measure | Table | Definition |")
    lines.append("|---|---|---|")
    for t in buildable_tables():
        for c in t.columns:
            if c.kpi:
                defn = c.business_definition or c.description
                lines.append(f"| `{c.name}` | `{t.name}` | {defn} |")
    lines.append("")

    # Relationships
    lines.append("## Relationships")
    lines.append("")
    lines.append("| From | Foreign key | To dimension |")
    lines.append("|---|---|---|")
    for t in buildable_tables():
        for c in t.columns:
            if c.is_fk and c.is_fk.startswith("dim"):
                lines.append(f"| `{t.name}` | `{c.name}` | `{c.is_fk}` |")
    lines.append("")

    # Per-table business definitions
    lines.append("## Table definitions & business context")
    lines.append("")
    for t in buildable_tables():
        lines.append(f"### `{t.name}`")
        lines.append("")
        lines.append(f"- **What it is:** {t.description}")
        lines.append(f"- **Grain:** {t.grain}")
        lines.append(f"- **Source:** {t.source_report}")
        kpis = [c.name for c in t.columns if c.kpi]
        if kpis:
            lines.append(f"- **KPIs:** {', '.join('`'+k+'`' for k in kpis)}")
        if t.relationships:
            lines.append(f"- **Links:** {'; '.join(t.relationships)}")
        defined = [c for c in t.columns if c.business_definition]
        if defined:
            lines.append("- **Key business definitions:**")
            for c in defined:
                lines.append(f"  - `{c.name}` — {c.business_definition}")
        lines.append("")
    return "\n".join(lines)


def generate() -> list[str]:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    out = []
    for name, text in [("data_dictionary.md", _gen_data_dictionary()),
                       ("business_metadata_catalog.md", _gen_business_catalog())]:
        path = DOCS_DIR / name
        path.write_text(text, encoding="utf-8")
        out.append(str(path))
    return out


if __name__ == "__main__":
    for p in generate():
        print("Generated:", p)
