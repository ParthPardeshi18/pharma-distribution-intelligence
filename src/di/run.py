"""Decision Intelligence runner — assemble all domains into one narrative.

Produces:
  reports/decision_intelligence.md    — the full DI report (narrative, not charts)
  reports/decision_intelligence.json  — structured feed for dashboards
  outputs/charts/*.png                — supporting charts (revenue, margin, BHI)

The report leads with the Business Health Index and a cross-domain priority list
(top risks, opportunities, recommendations), then a section per domain with its
executive summary, KPIs, insights, root cause, risks, opportunities, and recs.

Run:  python -m src.di.run
"""
from __future__ import annotations

import datetime as dt
import json

from src.di import health_index
from src.di.domains import ALL
from src.di.kpis import get_spec
from src.utils import PROJECT_ROOT

REPORT_MD = PROJECT_ROOT / "reports" / "decision_intelligence.md"
REPORT_JSON = PROJECT_ROOT / "reports" / "decision_intelligence.json"
CHARTS_DIR = PROJECT_ROOT / "outputs" / "charts"

_SEV_ICON = {"positive": "🟢", "info": "🔵", "warning": "🟡", "critical": "🔴"}


def _fmt_metric(m) -> str:
    spec = get_spec(m.name)
    v = spec.format(m.value)
    yoy = f"{m.yoy_pct:+.1f}%" if m.yoy_pct is not None else "—"
    score = f"{m.score:.0f}" if m.score is not None else "—"
    return f"| {m.label} | {v} | {yoy} | {score} |"


def render_markdown(reports, bhi) -> str:
    L = ["# Decision Intelligence Report", ""]
    L.append(f"> Sukhakarta Distributors · generated {dt.date.today():%Y-%m-%d}. "
             "A system that explains the business and recommends actions.")
    L.append("")

    # --- Business Health Index ---
    L.append(f"## Business Health Index: {bhi.score}/100  (grade {bhi.grade})")
    L.append("")
    L.append("| Component | KPI value | Score | Weight | Contribution |")
    L.append("|---|--:|--:|--:|--:|")
    for c in bhi.components:
        spec = get_spec(c["kpi"])
        L.append(f"| {c['name'].replace('_',' ').title()} | {spec.format(c['value'])} "
                 f"| {c['score']:.0f} | {c['weight']:.2f} | {c['contribution']:.1f} |")
    if bhi.note:
        L.append("")
        L.append(f"> {bhi.note}")
    L.append("")

    # --- cross-domain priorities ---
    all_risks = sorted((r for rep in reports for r in rep.risks),
                       key=lambda r: r.score, reverse=True)[:5]
    all_opps = sorted((o for rep in reports for o in rep.opportunities),
                      key=lambda o: o.potential_impact_inr or 0, reverse=True)[:5]
    all_recs = sorted((r for rep in reports for r in rep.recommendations),
                      key=lambda r: r.priority_score, reverse=True)[:6]

    L.append("## Top priorities across the business")
    L.append("")
    L.append("**Highest risks**")
    for r in all_risks:
        L.append(f"- {_SEV_ICON.get(r.severity,'')} **{r.name}** (score {r.score:.0f}/100) — {r.description}")
    L.append("")
    L.append("**Biggest opportunities**")
    for o in all_opps:
        imp = f" (~₹{o.potential_impact_inr:,.0f})" if o.potential_impact_inr else ""
        L.append(f"- **{o.name}**{imp} — {o.description}")
    L.append("")
    L.append("**Do-first recommendations** (ranked by impact × confidence ÷ effort)")
    L.append("")
    L.append("| # | Recommendation | Impact | Effort | Confidence | Priority |")
    L.append("|--:|---|:--:|:--:|--:|--:|")
    for i, r in enumerate(all_recs, 1):
        L.append(f"| {i} | {r.text} | {r.impact} | {r.effort} | "
                 f"{r.confidence:.0%} | {r.priority_score} |")
    L.append("")

    # --- per-domain ---
    L.append("## Domain analyses")
    L.append("")
    for rep in reports:
        L.append(f"### {rep.domain.replace('_',' ').title()}")
        ex = rep.executive_summary
        if ex:
            L.append("")
            L.append(f"**Executive summary** — _priority: {ex.priority}, "
                     f"confidence: {ex.confidence:.0%}_")
            L.append(f"- **What happened:** {ex.what_happened}")
            L.append(f"- **Why:** {ex.why}")
            L.append(f"- **Business impact:** {ex.business_impact}")
            if ex.recommended_actions:
                L.append(f"- **Recommended actions:** " +
                         "; ".join(ex.recommended_actions))
        if rep.scorecard:
            L.append(f"- **Scorecard:** {rep.scorecard.score}/100 (grade {rep.scorecard.grade})")
        L.append("")
        if rep.metrics:
            L.append("| KPI | Value | YoY | Health |")
            L.append("|---|--:|--:|--:|")
            for m in rep.metrics:
                L.append(_fmt_metric(m))
            L.append("")
        if rep.insights:
            L.append("**Insights**")
            for ins in rep.insights:
                L.append(f"- {_SEV_ICON.get(ins.severity,'')} {ins.text}")
            L.append("")
        if rep.root_causes:
            L.append("**Root cause**")
            for rc in rep.root_causes:
                L.append(f"- {rc}")
            L.append("")
        if rep.risks:
            L.append("**Risks**")
            for r in rep.risks:
                L.append(f"- {_SEV_ICON.get(r.severity,'')} {r.name} ({r.score:.0f}/100): {r.description}")
            L.append("")
        if rep.opportunities:
            L.append("**Opportunities**")
            for o in rep.opportunities:
                imp = f" (~₹{o.potential_impact_inr:,.0f})" if o.potential_impact_inr else ""
                L.append(f"- {o.name}{imp} — {o.description}")
            L.append("")
        if rep.recommendations:
            L.append("**Recommendations**")
            for r in rep.recommendations:
                L.append(f"- [{r.priority_score}] {r.text} "
                         f"_(impact {r.impact}, effort {r.effort}, conf {r.confidence:.0%})_")
            L.append("")
    L.append("---")
    L.append("*Generated by the Decision Intelligence layer (src/di). KPIs and "
             "thresholds: src/di/kpis.py · Health Index weights: config/health_index.yaml.*")
    return "\n".join(L)


def _charts(reports, bhi):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return []
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    made = []
    rep = {r.domain: r for r in reports}

    # revenue + margin trend
    s = rep["sales"].summary.get("trend", [])
    mt = rep["profitability"].summary.get("margin_trend", [])
    if s and mt:
        fig, ax1 = plt.subplots(figsize=(7, 4))
        fys = [x[0] for x in s]
        ax1.bar(fys, [x[1] / 1e6 for x in s], color="#38bdf8", alpha=.8)
        ax1.set_ylabel("Revenue (₹ million)", color="#0369a1")
        ax2 = ax1.twinx()
        ax2.plot(fys, [x[1] for x in mt], color="#ef4444", marker="o", lw=2)
        ax2.set_ylabel("Gross margin (%)", color="#b91c1c")
        ax1.set_title("Revenue & gross margin trend")
        p = CHARTS_DIR / "revenue_margin_trend.png"
        fig.tight_layout(); fig.savefig(p, dpi=110); plt.close(fig)
        made.append(str(p))

    # BHI component contributions
    if bhi.components:
        fig, ax = plt.subplots(figsize=(7, 4))
        names = [c["name"].replace("_", " ") for c in bhi.components]
        ax.barh(names, [c["score"] for c in bhi.components], color="#22c55e", alpha=.8)
        ax.set_xlim(0, 100); ax.set_xlabel("Health score (0-100)")
        ax.set_title(f"Business Health Index components (BHI {bhi.score}/100)")
        ax.invert_yaxis()
        p = CHARTS_DIR / "bhi_components.png"
        fig.tight_layout(); fig.savefig(p, dpi=110); plt.close(fig)
        made.append(str(p))
    return made


def generate() -> dict:
    reports = [m.analyze() for m in ALL]
    bhi = health_index.compute(reports)

    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    REPORT_MD.write_text(render_markdown(reports, bhi), encoding="utf-8")
    REPORT_JSON.write_text(json.dumps(
        {"generated": str(dt.date.today()),
         "business_health_index": bhi.to_dict(),
         "domains": [r.to_dict() for r in reports]},
        indent=2, default=str), encoding="utf-8")
    charts = _charts(reports, bhi)
    return {"bhi": bhi.score, "grade": bhi.grade, "md": str(REPORT_MD),
            "json": str(REPORT_JSON), "charts": charts}


def main():
    out = generate()
    print(f"Business Health Index: {out['bhi']}/100 ({out['grade']})")
    print("Report:", out["md"])
    print("JSON:  ", out["json"])
    for c in out["charts"]:
        print("Chart: ", c)


if __name__ == "__main__":
    main()
