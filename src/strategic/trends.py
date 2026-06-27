"""Multi-year trend analysis — CAGR and direction for headline measures."""
from __future__ import annotations

from dataclasses import dataclass

from src.di import warehouse_api as W


@dataclass
class Trend:
    measure: str
    unit: str
    series: list      # [(fy, value)]
    cagr_pct: float | None
    direction: str    # rising | falling | flat | recovering | softening
    note: str


def _cagr(first, last, years):
    if first and first > 0 and years > 0:
        return round(((last / first) ** (1 / years) - 1) * 100, 1)
    return None


def _direction(vals) -> str:
    if len(vals) < 2:
        return "flat"
    first, last, peak = vals[0], vals[-1], max(vals)
    if last >= peak * 0.99:
        return "rising" if last > first else "flat"
    if last < first * 0.97:
        return "falling"
    if last > vals[-2]:
        return "recovering"
    return "softening"


def _trend(measure, unit, pairs) -> Trend:
    vals = [v for _, v in pairs]
    cagr = _cagr(vals[0], vals[-1], len(vals) - 1)
    d = _direction(vals)
    note = {"recovering": "below the earlier peak but rebounding",
            "falling": "in multi-year decline", "rising": "in sustained growth",
            "softening": "easing from recent levels", "flat": "broadly stable"}[d]
    return Trend(measure, unit, pairs, cagr, d, note)


def analyze() -> list[Trend]:
    s = W.sales_by_fy()
    p = W.purchases_by_fy()
    out = [
        _trend("Revenue", "₹", [(r.fy, round(float(r.revenue))) for r in s.itertuples()]),
        _trend("Gross profit", "₹", [(r.fy, round(float(r.profit))) for r in s.itertuples()]),
        _trend("Purchases", "₹", [(r.fy, round(float(r.purchases))) for r in p.itertuples()]),
        _trend("Bills", "count", [(r.fy, int(r.bills)) for r in s.itertuples()]),
    ]
    # margin trend
    margin = [(r.fy, round(100 * float(r.profit) / float(r.billed), 2) if r.billed else 0)
              for r in s.itertuples()]
    out.append(_trend("Gross margin", "%", margin))
    return out
