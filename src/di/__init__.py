"""Decision Intelligence layer.

Turns the warehouse into a system that *explains the business and recommends
actions* — not just charts. A reusable, config-driven framework (KPI registry +
engines) that every business domain plugs into, producing for each domain:

  data summary · KPIs · insights · root-cause · risks · opportunities ·
  recommendations · scorecard · executive summary

plus a single composite Business Health Index (0-100) across the whole business.
"""
from src.di.base import (
    DomainReport, ExecutiveSummary, Insight, Metric, Opportunity,
    Recommendation, Risk, Scorecard,
)

__all__ = ["Metric", "Insight", "Risk", "Opportunity", "Recommendation",
           "Scorecard", "ExecutiveSummary", "DomainReport"]
