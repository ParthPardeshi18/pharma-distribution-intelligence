"""Reports & downloads — generate the executive Business Health Report (.docx),
and download GeoJSON layers and warehouse-derived datasets."""
from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from app import components as C
from app import data

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _docx_section(app_mode: str):
    C.section("Executive Business Health Report (.docx)",
              "Board-ready document: health verdict, trends, findings, ranked risks "
              "and ₹-opportunities, and an impact-vs-effort recommendation matrix.")
    if app_mode == "shareable":
        # Public view: only the anonymised report may be generated here.
        st.caption("Public mode — only the **anonymised** report is available.")
        mode = "shareable"
    else:
        mode = st.radio(
            "Mode", ["shareable", "internal"], horizontal=True,
            help="internal = real firm name + figures · shareable = anonymised (portfolio-safe)",
        )
    if st.button("Generate report", type="primary"):
        with st.spinner("Rendering .docx…"):
            try:
                from src.report.health_report import generate_health_report

                path = Path(generate_health_report(mode))
            except Exception as exc:  # noqa: BLE001
                st.error(f"Report generation failed: {exc}")
                return
        st.success(f"Generated: {path.name}")
        st.session_state[f"report_path_{mode}"] = str(path)

    path_str = st.session_state.get(f"report_path_{mode}")
    if path_str and Path(path_str).exists():
        content = Path(path_str).read_bytes()
        C.download_bytes(
            content, f"business_health_report_{mode}.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "⬇ Download report (.docx)",
        )


def _geojson_section():
    C.section("GeoJSON spatial layers", "Canonical RFC 7946 layers for GIS tools "
              "(Power BI Shape Maps, Leaflet, Mapbox, deck.gl).")
    layers = data.geojson_layers()
    if not layers:
        st.caption("No GeoJSON layers found.")
        return
    cols = st.columns(2)
    for i, layer in enumerate(layers):
        fc = data.geojson(layer)
        if not fc:
            continue
        with cols[i % 2]:
            C.download_bytes(
                json.dumps(fc).encode("utf-8"), f"{layer}.geojson",
                "application/geo+json", f"⬇ {layer}.geojson",
            )


def _datasets_section(currency, fy):
    C.section("Warehouse datasets", "Star-schema aggregates as CSV.")
    if not data.warehouse_exists():
        st.caption("Build the warehouse first.")
        return
    c1, c2 = st.columns(2)
    with c1:
        C.download_df(data.sales_by_fy(), "sales_by_fy.csv", "⬇ Sales by fiscal year")
        C.download_df(data.purchases_by_fy(), "purchases_by_fy.csv", "⬇ Purchases by fiscal year")
    with c2:
        C.download_df(data.rfm().customers, "rfm_customers.csv", "⬇ RFM (per customer)")
        C.download_df(data.profitability("customers", fy, 50).top,
                      "top_customers.csv", "⬇ Top customers by profit")


def render(opts: dict) -> None:
    st.markdown("## Reports & downloads")
    st.caption("Generate the executive report and export data for Power BI or "
               "other downstream tools. Power BI remains an optional reporting layer.")

    _docx_section(opts.get("mode", "internal"))
    _geojson_section()
    _datasets_section(opts["currency"], opts["fy"])

    # Pointer to the optional Power BI layer.
    C.section("Power BI (optional)")
    st.markdown(
        "This Streamlit app is the primary interface. Power BI is supported as an "
        "**optional** reporting layer — star-schema CSV exports live under "
        "`data/warehouse/exports/`, and per-stakeholder specs in `dashboards/specs/`."
    )
