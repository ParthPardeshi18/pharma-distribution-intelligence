"""Concrete ERP adapter for the firm's ERP (Marg/Busy-style Excel exports).

Responsibilities (all ERP-specific logic is confined here):
- discover report files and their financial year from filenames
- detect the banner/header (via src.utils) and read the real table
- canonicalise column names: global synonyms -> per-report overrides -> snake_case
- coerce dates and numerics; strip embedded footer/total rows (reconciled)
- detect populated stable-ID columns and surface them for future auto-adoption
"""
from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

import pandas as pd
import yaml

from src.adapters.base import CanonicalFrame, ERPAdapter
from src.utils import CONFIG_DIR, RAW_DIR, read_erp_excel

_FY_RE = re.compile(r"_(\d\d-\d\d)\.xlsx$", re.IGNORECASE)
# Footer/summary rows the ERP embeds inside the data area.
_FOOTER_TOKENS = {"total", "totals", "grand total", "sub total", "subtotal",
                  "opening balance", "closing balance", "opening", "closing"}
_DATE_CANON = {"txn_date", "due_date", "expiry_date"}
_NUMERIC_HINTS = ("amount", "amt", "value", "qty", "rate", "pct", "ptr", "mrp",
                  "balance", "ageing", "sale", "cost", "profit", "days",
                  "_sd", "_id", "num_", "sp", "opening", "closing", "stock_")


def _snake(name: str) -> str:
    s = re.sub(r"[^0-9A-Za-z]+", "_", str(name).strip().lower())
    return re.sub(r"_+", "_", s).strip("_") or "col"


class MargAdapter(ERPAdapter):
    name = "marg"

    def __init__(self, raw_dir: Path = RAW_DIR, config_dir: Path = CONFIG_DIR):
        self.raw_dir = Path(raw_dir)
        self._mappings = yaml.safe_load(
            (config_dir / "column_mappings.yaml").read_text(encoding="utf-8"))
        self._specs = yaml.safe_load(
            (config_dir / "report_specs.yaml").read_text(encoding="utf-8"))
        # invert synonyms: raw header (lower) -> canonical
        self._syn: dict[str, str] = {}
        for canon, variants in self._mappings.get("synonyms", {}).items():
            for v in variants:
                self._syn[str(v).strip().lower()] = canon
        self._defaults = self._specs.get("defaults", {})
        self._reports = self._specs.get("reports", {})

    # ------------------------------------------------------------------ #
    @staticmethod
    def _report_key(path: Path) -> str:
        rtype = _FY_RE.sub("", path.name)
        rtype = re.sub(r"\.xlsx$", "", rtype, flags=re.IGNORECASE)
        return f"{path.parent.name}/{rtype}"

    @staticmethod
    def _fy(path: Path) -> str | None:
        m = _FY_RE.search(path.name)
        return m.group(1) if m else None

    @lru_cache(maxsize=1)
    def _index(self) -> dict[str, list[Path]]:
        idx: dict[str, list[Path]] = {}
        for f in sorted(self.raw_dir.rglob("*.xlsx")):
            idx.setdefault(self._report_key(f), []).append(f)
        return idx

    def list_reports(self) -> list[str]:
        return sorted(self._index().keys())

    def available_years(self, report_key: str) -> list[str]:
        files = self._index().get(report_key, [])
        return [self._fy(f) or "—" for f in files]

    # ------------------------------------------------------------------ #
    def _canon_columns(self, df: pd.DataFrame, report_key: str) -> tuple[pd.DataFrame, dict]:
        overrides = (self._reports.get(report_key, {}) or {}).get("columns", {}) or {}
        overrides_lc = {str(k).strip().lower(): v for k, v in overrides.items()}
        rename: dict[str, str] = {}
        used: dict[str, int] = {}
        for raw in df.columns:
            low = str(raw).strip().lower()
            canon = overrides_lc.get(low) or self._syn.get(low) or _snake(raw)
            # guard against collisions after canonicalisation
            if canon in used:
                used[canon] += 1
                canon = f"{canon}_{used[canon]}"
            else:
                used[canon] = 0
            rename[raw] = canon
        return df.rename(columns=rename), rename

    def _strip_footers(self, df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
        if not self._defaults.get("drop_footer_totals", True) or df.empty:
            return df, 0
        # check the first text-ish column for footer tokens
        text_cols = [c for c in df.columns
                     if df[c].dtype == object][:1]
        if not text_cols:
            return df, 0
        col = text_cols[0]
        mask = df[col].astype(str).str.strip().str.lower().isin(_FOOTER_TOKENS)
        return df[~mask].reset_index(drop=True), int(mask.sum())

    @staticmethod
    def _coerce_types(df: pd.DataFrame) -> pd.DataFrame:
        for c in df.columns:
            if c in _DATE_CANON or c.endswith("_date"):
                df[c] = pd.to_datetime(df[c], errors="coerce", dayfirst=True)
            elif any(h in c for h in _NUMERIC_HINTS):
                df[c] = pd.to_numeric(df[c], errors="coerce")
        return df

    def _detect_source_ids(self, df: pd.DataFrame, report_key: str) -> dict[str, str]:
        """If an id_candidate column exists AND is populated, surface it for the
        warehouse to prefer over the name-based surrogate key."""
        spec = self._reports.get(report_key, {}) or {}
        found: dict[str, str] = {}
        for cand in spec.get("id_candidates", []) or []:
            if cand in df.columns and df[cand].notna().mean() > 0.5:
                found[report_key.split("/")[0].lower()] = cand
        return found

    # ------------------------------------------------------------------ #
    def load(self, report_key: str, financial_year: str | None = None) -> CanonicalFrame:
        files = self._index().get(report_key)
        if not files:
            raise FileNotFoundError(f"Unknown report '{report_key}'")
        if financial_year:
            files = [f for f in files if self._fy(f) == financial_year]
            if not files:
                raise FileNotFoundError(f"{report_key} has no FY {financial_year}")
        path = files[0]

        df = read_erp_excel(path)
        df, _ = self._canon_columns(df, report_key)
        df, dropped = self._strip_footers(df)
        df = self._coerce_types(df)

        spec = self._reports.get(report_key, {}) or {}
        return CanonicalFrame(
            data=df, report_key=report_key,
            role=spec.get("role", "unknown"),
            grain=spec.get("grain", ""),
            financial_year=self._fy(path),
            source_file=str(path.relative_to(self.raw_dir)).replace("\\", "/"),
            links=spec.get("links", []) or [],
            source_id_columns=self._detect_source_ids(df, report_key),
            dropped_rows=dropped,
        )


@lru_cache(maxsize=1)
def get_adapter() -> MargAdapter:
    """Process-wide singleton adapter (the firm's ERP)."""
    return MargAdapter()
