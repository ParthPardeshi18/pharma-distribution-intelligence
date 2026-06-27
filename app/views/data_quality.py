"""Data quality — warehouse row counts, referential-integrity (orphan keys),
quality-status breakdown, and database size. Admin-only page."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from app import components as C
from app import data, theme


def render(opts: dict) -> None:
    st.markdown("## Data quality")
    st.caption("Trust the numbers: row counts, referential integrity, and the "
               "lineage/quality metadata carried on every warehouse row.")

    if not data.warehouse_exists():
        st.warning("Build the warehouse first (`python run_pipeline.py`).")
        return

    counts = data.row_counts()
    orphans = data.orphans()
    total_rows = sum(counts.values())

    cols = st.columns(3)
    cols[0].metric("Tables", len(counts))
    cols[1].metric("Total rows", f"{total_rows:,}")
    cols[2].metric("Database size", f"{data.db_size_bytes() / 1e6:.1f} MB")

    # Orphan keys (referential integrity)
    C.section("Referential integrity")
    n_orphans = sum(o.get("orphan_rows", o.get("orphans", 0)) for o in orphans) if orphans else 0
    if not orphans or n_orphans == 0:
        st.success("0 orphan keys — every fact row resolves to its dimensions.")
    else:
        st.error(f"{n_orphans:,} orphan key(s) detected.")
        st.dataframe(pd.DataFrame(orphans), width="stretch", hide_index=True)

    # Row counts by table
    C.section("Row counts by table")
    rc = pd.DataFrame({"table": list(counts.keys()), "rows": list(counts.values())})
    rc = rc.sort_values("rows", ascending=True)
    fig = px.bar(rc, x="rows", y="table", orientation="h", color="rows",
                 color_continuous_scale=["#E6E9EE", theme.NAVY])
    fig.update_layout(height=max(300, 22 * len(rc)), coloraxis_showscale=False,
                      margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, width="stretch")
    C.download_df(rc.sort_values("rows", ascending=False), "row_counts.csv",
                  "⬇ Download row counts (CSV)")

    # Quality status breakdown
    try:
        qb = data.quality_breakdown()
        if qb is not None and not qb.empty:
            C.section("Quality-status breakdown",
                      "Every row carries a quality flag set during cleaning.")
            st.dataframe(qb, width="stretch", hide_index=True)
    except Exception:
        pass
