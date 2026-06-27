"""Geographic visualisations (matplotlib). Best-effort: skips if plotting fails.

Produces a lat/lon bubble map of routes (size = sales, colour = district), a
distance-band bar, and a delivery-day bar. No external basemap is required.
"""
from __future__ import annotations

from src.utils import PROJECT_ROOT

CHARTS = PROJECT_ROOT / "outputs" / "charts"


def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    return plt


def render(territory_result, concentration_result) -> list[str]:
    try:
        plt = _plt()
    except Exception:
        return []
    CHARTS.mkdir(parents=True, exist_ok=True)
    made = []
    t = territory_result
    geo = t.routes[t.routes["matched"]].copy()
    base_lat, base_lon = 18.8268, 74.3733

    # 1. bubble map
    try:
        fig, ax = plt.subplots(figsize=(8, 7))
        districts = geo["district"].fillna("?").unique()
        cmap = plt.get_cmap("tab10")
        colors = {d: cmap(i % 10) for i, d in enumerate(districts)}
        sizes = (geo["sale_amount"] / geo["sale_amount"].max() * 1500 + 40)
        for d in districts:
            sub = geo[geo["district"] == d]
            ax.scatter(sub["lon"], sub["lat"],
                       s=(sub["sale_amount"] / geo["sale_amount"].max() * 1500 + 40),
                       color=colors[d], alpha=0.6, edgecolors="white", label=d)
        ax.scatter([base_lon], [base_lat], marker="*", s=420, color="#b11b1b",
                   edgecolors="black", zorder=5, label="Base (Shirur)")
        for _, r in geo.sort_values("sale_amount", ascending=False).head(10).iterrows():
            ax.annotate(str(r["display_name"]), (r["lon"], r["lat"]),
                        fontsize=7, alpha=0.8)
        ax.set_xlabel("Longitude"); ax.set_ylabel("Latitude")
        ax.set_title(f"Route sales by location (FY {t.fy}) — bubble = sales")
        ax.legend(fontsize=7, loc="best")
        p = CHARTS / "geo_bubble_map.png"
        fig.tight_layout(); fig.savefig(p, dpi=110); plt.close(fig)
        made.append(str(p))
    except Exception:
        pass

    # 2. distance-band bar
    try:
        b = concentration_result.distance_bands
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(b["distance_band"].astype(str), b["share_pct"], color="#2a7ab0")
        ax.set_ylabel("% of sales"); ax.set_title("Sales by distance from base")
        plt.xticks(rotation=25, ha="right", fontsize=8)
        p = CHARTS / "geo_distance_bands.png"
        fig.tight_layout(); fig.savefig(p, dpi=110); plt.close(fig)
        made.append(str(p))
    except Exception:
        pass

    # 3. delivery-day bar
    try:
        d = t.by_day.sort_values("sales", ascending=False)
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(d["delivery_day"], d["sales"] / 1e6, color="#1e7e34")
        ax.set_ylabel("Sales (₹ million)"); ax.set_title("Sales by delivery day (route schedule)")
        p = CHARTS / "geo_delivery_day.png"
        fig.tight_layout(); fig.savefig(p, dpi=110); plt.close(fig)
        made.append(str(p))
    except Exception:
        pass
    return made
