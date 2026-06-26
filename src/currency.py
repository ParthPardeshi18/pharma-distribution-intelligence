"""Currency reporting service — INR is the source of truth; convert at the edge.

The warehouse stores every amount in INR. This module is the ONLY place money is
converted, and it runs in the reporting/presentation layer. Analytics, KPIs, and
the warehouse never see converted values, so results are identical regardless of
the chosen reporting currency.

Usage:
    cur = CurrencyConverter()
    cur.convert(1000.0, "GBP", financial_year="25-26")     # INR -> GBP
    df2 = cur.convert_frame(df, ["net_amount_inr"], "USD")  # adds *_usd columns
    cur.format(910.0, "GBP")                                 # "£910.00"
"""
from __future__ import annotations

import pandas as pd
import yaml

from src.utils import CONFIG_DIR, PROJECT_ROOT


class CurrencyError(RuntimeError):
    pass


class CurrencyConverter:
    def __init__(self, config_path=None, rates_path=None):
        cfg_path = config_path or (CONFIG_DIR / "currency_config.yaml")
        self.cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
        self.base = self.cfg["base_currency"]
        self.supported = set(self.cfg["supported_currencies"])
        self.strategy = self.cfg.get("rate_strategy", "fy_average")
        self.on_missing = self.cfg.get("on_missing_rate", "error")
        rp = rates_path or (PROJECT_ROOT / self.cfg["rates_path"])
        self.rates = pd.read_csv(rp, dtype={"financial_year": str})
        # index: (fy, currency) -> units_per_inr
        self._rate = {(r.financial_year, r.currency): float(r.units_per_inr)
                      for r in self.rates.itertuples()}

    # --------------------------------------------------------------- #
    def is_supported(self, currency: str) -> bool:
        return currency in self.supported

    def rate(self, currency: str, financial_year: str | None = None) -> float:
        """Units of `currency` per 1 INR."""
        if currency == self.base:
            return 1.0
        if currency not in self.supported:
            raise CurrencyError(f"Unsupported currency '{currency}'. "
                                f"Supported: {sorted(self.supported)}")
        key = (financial_year, currency)
        if key in self._rate:
            return self._rate[key]
        # fall back to any available year's rate for the currency
        candidates = [v for (fy, c), v in self._rate.items() if c == currency]
        if candidates:
            msg = f"No rate for {currency} FY {financial_year}; using fallback."
            if self.on_missing == "error":
                raise CurrencyError(msg)
            return sum(candidates) / len(candidates)
        raise CurrencyError(f"No exchange rate available for '{currency}'.")

    def convert(self, amount_inr, currency: str, financial_year: str | None = None):
        if amount_inr is None or (isinstance(amount_inr, float) and pd.isna(amount_inr)):
            return amount_inr
        return float(amount_inr) * self.rate(currency, financial_year)

    def convert_frame(self, df: pd.DataFrame, inr_columns: list[str], currency: str,
                      fy_column: str = "financial_year") -> pd.DataFrame:
        """Return a copy with converted columns added (suffix _<cur>). For INR,
        returns the frame unchanged. Uses per-row FY rate when available."""
        if currency == self.base:
            return df.copy()
        out = df.copy()
        suffix = currency.lower()
        has_fy = fy_column in out.columns
        for col in inr_columns:
            if col not in out.columns:
                continue
            new_col = col.replace("_inr", "") + f"_{suffix}"
            if has_fy:
                out[new_col] = [
                    self.convert(v, currency, fy)
                    for v, fy in zip(out[col], out[fy_column])
                ]
            else:
                r = self.rate(currency, financial_year=None)
                out[new_col] = out[col] * r
        return out

    def format(self, amount, currency: str) -> str:
        disp = self.cfg.get("display", {}).get(currency, {})
        symbol = disp.get("symbol", "")
        decimals = int(disp.get("decimals", 2))
        if amount is None or (isinstance(amount, float) and pd.isna(amount)):
            return ""
        return f"{symbol}{amount:,.{decimals}f}"
