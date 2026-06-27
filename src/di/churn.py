"""Recency + frequency customer churn model (business-calibrated).

For a route-based distributor selling to a fixed retailer network, a customer is
"churned" not by a flat cut-off but by sustained silence relative to their OWN
ordering cadence. We compute, per established customer:

  median_gap        — typical days between their orders
  days_since_last   — days from their last order to the reference date
  churn_threshold   — max(inactivity_days, frequency_multiple × median_gap)
  status            — active | at_risk | churned

Config: config/decision_intelligence.yaml -> churn.
"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import yaml

from src.di import warehouse_api as W
from src.utils import CONFIG_DIR


@dataclass
class ChurnResult:
    customers: pd.DataFrame    # per-customer: orders, last_order, median_gap, days_since, status
    reference_date: pd.Timestamp
    established: int
    active: int
    at_risk: int
    churned: int
    config: dict

    @property
    def retention_pct(self) -> float | None:
        return round(100 * self.active / self.established, 1) if self.established else None

    @property
    def churn_pct(self) -> float | None:
        return round(100 * self.churned / self.established, 1) if self.established else None


def _config() -> dict:
    cfg = yaml.safe_load((CONFIG_DIR / "decision_intelligence.yaml").read_text(encoding="utf-8"))
    return cfg.get("churn", {})


def analyze_churn(orders: pd.DataFrame | None = None) -> ChurnResult:
    cfg = _config()
    inactivity = float(cfg.get("inactivity_days", 120))
    freq_mult = float(cfg.get("frequency_multiple", 3.0))
    at_risk_frac = float(cfg.get("at_risk_fraction", 0.6))
    min_orders = int(cfg.get("min_orders_established", 2))

    orders = orders if orders is not None else W.customer_orders()
    ref_cfg = cfg.get("reference", "data_max")
    ref = orders["order_date"].max() if ref_cfg == "data_max" else pd.Timestamp(ref_cfg)

    rows = []
    for ck, grp in orders.groupby("customer_key"):
        dates = grp["order_date"].sort_values()
        n = len(dates)
        gaps = dates.diff().dropna().dt.days
        median_gap = float(gaps.median()) if len(gaps) else None
        last = dates.iloc[-1]
        days_since = (ref - last).days
        # frequency-aware threshold (falls back to flat inactivity for sparse buyers)
        thr = max(inactivity, freq_mult * median_gap) if median_gap else inactivity
        established = n >= min_orders
        if not established:
            status = "new_or_sparse"
        elif days_since > thr:
            status = "churned"
        elif days_since > at_risk_frac * thr:
            status = "at_risk"
        else:
            status = "active"
        rows.append({"customer_key": ck, "orders": n, "last_order": last,
                     "median_gap_days": round(median_gap, 1) if median_gap else None,
                     "days_since_last": days_since, "churn_threshold_days": round(thr, 0),
                     "status": status, "revenue": float(grp["amount"].sum())})

    df = pd.DataFrame(rows)
    est = df[df["status"] != "new_or_sparse"]
    counts = est["status"].value_counts().to_dict()
    return ChurnResult(
        customers=df, reference_date=ref, established=len(est),
        active=counts.get("active", 0), at_risk=counts.get("at_risk", 0),
        churned=counts.get("churned", 0),
        config={"inactivity_days": inactivity, "frequency_multiple": freq_mult,
                "min_orders_established": min_orders, "reference": str(ref.date())})
