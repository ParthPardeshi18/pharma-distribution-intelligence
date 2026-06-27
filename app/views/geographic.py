"""Geographic intelligence — interactive GeoJSON maps (pydeck/deck.gl) over the
canonical spatial layers, plus territory productivity and concentration analytics."""
from __future__ import annotations

import pandas as pd
import pydeck as pdk
import streamlit as st

from app import components as C
from app import data, theme

# Operating heartland centroid (Shirur / Pune, Maharashtra) as a sensible default.
_DEFAULT_VIEW = {"lat": 18.83, "lon": 74.37, "zoom": 8}

# Which numeric property to theme each layer by.
_VALUE_PROP = {
    "districts": "sales_inr", "talukas": "sales_inr", "villages": "sales_inr",
    "territories": "sales_inr", "customers": "sales_inr",
    "routes": "sales_inr", "warehouses": None,
}
_POINT_LAYERS = {"customers", "warehouses"}


def _ramp(value: float, lo: float, hi: float) -> list:
    """Navy→amber→red-free sequential ramp returning [r,g,b,a]."""
    if hi <= lo:
        t = 0.5
    else:
        t = max(0.0, min(1.0, (value - lo) / (hi - lo)))
    # light blue (low) → navy (high)
    r = int(198 + (31 - 198) * t)
    g = int(216 + (58 - 216) * t)
    b = int(233 + (95 - 233) * t)
    return [r, g, b, 170]


def _themed(collection: dict, prop: str | None) -> dict:
    feats = collection.get("features", [])
    if prop:
        vals = [f["properties"].get(prop) or 0 for f in feats]
        lo, hi = (min(vals), max(vals)) if vals else (0, 1)
        for f in feats:
            f["properties"]["_fill"] = _ramp(f["properties"].get(prop) or 0, lo, hi)
    else:
        for f in feats:
            f["properties"]["_fill"] = [31, 58, 95, 200]
    return collection


def _centroid(collection: dict) -> tuple[float, float]:
    xs, ys = [], []
    for f in collection.get("features", []):
        g = f.get("geometry") or {}
        _collect_coords(g.get("coordinates"), xs, ys)
    if xs and ys:
        return (sum(ys) / len(ys), sum(xs) / len(xs))
    return (_DEFAULT_VIEW["lat"], _DEFAULT_VIEW["lon"])


def _collect_coords(coords, xs, ys):
    if not coords:
        return
    if isinstance(coords[0], (int, float)):
        xs.append(coords[0]); ys.append(coords[1])
    else:
        for c in coords:
            _collect_coords(c, xs, ys)


def _deck(collection: dict, layer: str):
    is_point = layer in _POINT_LAYERS
    lat, lon = _centroid(collection)
    geo_layer = pdk.Layer(
        "GeoJsonLayer",
        data=collection,
        pickable=True,
        stroked=True,
        filled=True,
        extruded=False,
        get_fill_color="properties._fill",
        get_line_color=[255, 255, 255, 140] if not is_point else [31, 58, 95, 220],
        line_width_min_pixels=1,
        get_point_radius=900,
        point_radius_min_pixels=4,
        point_radius_max_pixels=18,
    )
    view = pdk.ViewState(latitude=lat, longitude=lon,
                         zoom=_DEFAULT_VIEW["zoom"] if not is_point else 8.5)
    tooltip = {"html": _tooltip_html(collection),
               "style": {"backgroundColor": theme.NAVY, "color": "white"}}
    return pdk.Deck(layers=[geo_layer], initial_view_state=view,
                    map_provider="carto", map_style="light", tooltip=tooltip)


def _tooltip_html(collection: dict) -> str:
    feats = collection.get("features", [])
    if not feats:
        return "{}"
    props = [k for k in feats[0]["properties"].keys() if not k.startswith("_")]
    rows = "".join(f"<b>{p}</b>: {{{p}}}<br/>" for p in props[:6])
    return rows


def render(opts: dict) -> None:
    currency, fy = opts["currency"], opts["fy"]

    st.markdown("## Geographic intelligence")
    st.caption("Canonical GeoJSON layers — boundaries, territories, routes, and "
               "customer/warehouse points — rendered with deck.gl.")

    layers = data.geojson_layers()
    if not layers:
        st.warning("No GeoJSON layers found. Run the GIS stage of the pipeline "
                   "(`python -m src.geo.gis.run`).")
        return

    layer = st.selectbox("Spatial layer", layers,
                         format_func=lambda s: s.replace("_", " ").title())
    fc = data.geojson(layer)
    if not fc or not fc.get("features"):
        st.info("That layer has no features.")
        return

    fc = _themed(fc, _VALUE_PROP.get(layer))
    st.pydeck_chart(_deck(fc, layer), width="stretch")
    st.caption(f"{len(fc['features'])} features · shaded by "
               f"{_VALUE_PROP.get(layer) or 'category'}.")

    # Feature attribute table + download
    rows = [dict(f["properties"]) for f in fc["features"]]
    for r in rows:
        r.pop("_fill", None)
    df = pd.DataFrame(rows)
    with st.expander(f"Attribute table — {layer} ({len(df)} rows)"):
        st.dataframe(df, width="stretch", hide_index=True)
        C.download_df(df, f"{layer}.csv", f"⬇ Download {layer} attributes (CSV)")

    # ── Territory productivity + concentration ──────────────────────────────
    if not data.warehouse_exists():
        return
    C.section("Territory & concentration analytics")
    terr = data.territory(fy)
    conc = data.geo_concentration(fy)

    cols = st.columns(4)
    cols[0].metric("Total territory sales", data.compact_inr(terr.total_sales))
    cols[1].metric("Geocode match", f"{terr.matched_pct:.0f}%")
    cols[2].metric("Concentration (HHI)", f"{conc.hhi:.0f}",
                   help=conc.hhi_label)
    cols[3].metric("Top-5 route share", f"{conc.top5_share_pct:.0f}%")
    if terr.data_note:
        st.caption(terr.data_note)

    t1, t2 = st.tabs(["Routes", "Distance bands"])
    with t1:
        st.dataframe(terr.routes, width="stretch", hide_index=True)
        C.download_df(terr.routes, "territory_routes.csv", "⬇ Download routes (CSV)")
    with t2:
        st.dataframe(conc.distance_bands, width="stretch", hide_index=True)
        cband = st.columns(2)
        cband[0].metric("Within 30 km", f"{conc.local_share_pct:.0f}%")
        cband[1].metric("Beyond 80 km", f"{conc.outstation_share_pct:.0f}%")

    if conc.insights:
        st.markdown("**Geographic insights**")
        for ins in conc.insights:
            st.markdown(f"- {ins}")
