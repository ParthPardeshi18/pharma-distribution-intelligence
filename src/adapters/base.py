"""Adapter contract: the canonical interface the warehouse depends on.

Any ERP (Marg, Tally, Busy, a future system) is integrated by subclassing
`ERPAdapter`. Downstream code calls only these methods and receives
`CanonicalFrame`s with canonical column names — it never knows which ERP, file
format, or header quirks produced the data.

Stable-ID forward-compatibility
-------------------------------
Today transactions have no stable customer/product codes. `report_specs.yaml`
lists `id_candidates` per report. When a future export includes one of those
columns populated, the adapter surfaces it as `<entity>_source_id` in the
canonical frame; the warehouse loader prefers a present source id over the
name-based surrogate key automatically — so adopting real IDs requires NO
downstream change. See `resolve_entity_key()` in the warehouse layer (Phase 2).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import pandas as pd


@dataclass
class CanonicalFrame:
    """A loaded report with canonical columns plus provenance and metadata."""
    data: pd.DataFrame
    report_key: str
    role: str                       # fact | dimension | aggregate | snapshot | event | statement
    grain: str
    financial_year: str | None      # e.g. "25-26" or None for FY-less masters
    source_file: str
    links: list[str] = field(default_factory=list)
    source_id_columns: dict[str, str] = field(default_factory=dict)  # entity -> column when present
    dropped_rows: int = 0           # footer/total rows removed (reconciliation)

    def __repr__(self) -> str:  # concise, no data dump
        return (f"<CanonicalFrame {self.report_key} fy={self.financial_year} "
                f"rows={len(self.data)} role={self.role}>")


class ERPAdapter(ABC):
    """Abstract base every ERP integration implements."""

    name: str = "abstract"

    @abstractmethod
    def list_reports(self) -> list[str]:
        """All report keys this adapter can produce (e.g. 'Sales/Sales')."""

    @abstractmethod
    def available_years(self, report_key: str) -> list[str]:
        """Financial years available on disk for a report key."""

    @abstractmethod
    def load(self, report_key: str, financial_year: str | None = None) -> CanonicalFrame:
        """Load one report (one FY, or the only file) as a CanonicalFrame."""

    def load_all_years(self, report_key: str) -> CanonicalFrame:
        """Load and vertically stack every FY for a report key, tagging each row
        with its financial_year. Returns a single CanonicalFrame."""
        years = self.available_years(report_key)
        frames: list[pd.DataFrame] = []
        dropped = 0
        first: CanonicalFrame | None = None
        for fy in years:
            cf = self.load(report_key, fy)
            first = first or cf
            df = cf.data.copy()
            df["financial_year"] = fy
            frames.append(df)
            dropped += cf.dropped_rows
        if first is None:
            raise FileNotFoundError(f"No files for report '{report_key}'")
        combined = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
        return CanonicalFrame(
            data=combined, report_key=report_key, role=first.role, grain=first.grain,
            financial_year=None, source_file=f"{report_key} (all years)",
            links=first.links, source_id_columns=first.source_id_columns,
            dropped_rows=dropped,
        )
