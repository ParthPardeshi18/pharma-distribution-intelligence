"""Power BI integration: star-schema CSV exports for dashboard building.

Exports the warehouse as clean, BI-ready CSVs in two sets:
- internal/   real identities (gitignored, local only)
- shareable/  anonymised identities, safe to share/commit

Both sets carry a dim_rate table so a Power BI report can switch reporting
currency with a slicer while the model stays in INR (the source of truth).
"""
from src.powerbi.exports import export_for_powerbi

__all__ = ["export_for_powerbi"]
