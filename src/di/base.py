"""Core data structures for the Decision Intelligence layer.

Every domain analyzer returns a `DomainReport` built from these. They are plain
dataclasses (serializable to dict/JSON) so the same objects drive the markdown
report, the JSON feed, and dashboards.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field

# severity / rating vocabularies (shared)
SEVERITY = ["positive", "info", "warning", "critical"]
LEVELS = {"high": 3, "medium": 2, "low": 1}


def grade(score: float) -> str:
    """0-100 -> letter grade."""
    if score is None:
        return "—"
    for cut, g in [(90, "A"), (80, "B"), (70, "C"), (60, "D"), (50, "E")]:
        if score >= cut:
            return g
    return "F"


def status_from_score(score: float) -> str:
    if score is None:
        return "info"
    if score >= 75:
        return "positive"
    if score >= 50:
        return "info"
    if score >= 35:
        return "warning"
    return "critical"


@dataclass
class Metric:
    name: str
    label: str
    value: float | None
    unit: str = ""                 # ₹ | % | days | x | count
    prior_value: float | None = None
    yoy_pct: float | None = None
    trend: list = field(default_factory=list)   # [(fy, value), ...]
    score: float | None = None     # 0-100 health score for this KPI
    status: str = "info"
    description: str = ""

    def to_dict(self):
        return asdict(self)


@dataclass
class Insight:
    text: str
    severity: str = "info"         # positive | info | warning | critical
    evidence: dict = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


@dataclass
class Risk:
    name: str
    description: str
    score: float                   # 0-100 (higher = more severe)
    severity: str = "warning"
    evidence: dict = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


@dataclass
class Opportunity:
    name: str
    description: str
    potential_impact_inr: float | None = None
    confidence: float = 0.5        # 0-1
    evidence: dict = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


@dataclass
class Recommendation:
    text: str
    rationale: str = ""
    impact: str = "medium"         # high | medium | low
    effort: str = "medium"         # high | medium | low
    confidence: float = 0.6        # 0-1

    @property
    def priority_score(self) -> float:
        """Higher = do first. Favours high impact, low effort, high confidence."""
        return round(LEVELS[self.impact] * self.confidence / LEVELS[self.effort], 3)

    def to_dict(self):
        d = asdict(self)
        d["priority_score"] = self.priority_score
        return d


@dataclass
class Scorecard:
    name: str
    score: float                   # 0-100
    components: list = field(default_factory=list)  # [(label, score, weight)]

    @property
    def grade(self) -> str:
        return grade(self.score)

    def to_dict(self):
        return {"name": self.name, "score": self.score, "grade": self.grade,
                "components": self.components}


@dataclass
class ExecutiveSummary:
    what_happened: str
    why: str
    business_impact: str
    recommended_actions: list = field(default_factory=list)
    priority: str = "medium"
    confidence: float = 0.6

    def to_dict(self):
        return asdict(self)


@dataclass
class DomainReport:
    domain: str
    summary: dict = field(default_factory=dict)
    metrics: list = field(default_factory=list)         # [Metric]
    insights: list = field(default_factory=list)        # [Insight]
    root_causes: list = field(default_factory=list)     # [str]
    risks: list = field(default_factory=list)           # [Risk]
    opportunities: list = field(default_factory=list)   # [Opportunity]
    recommendations: list = field(default_factory=list)  # [Recommendation]
    scorecard: Scorecard | None = None
    executive_summary: ExecutiveSummary | None = None

    def to_dict(self):
        return {
            "domain": self.domain,
            "summary": self.summary,
            "metrics": [m.to_dict() for m in self.metrics],
            "insights": [i.to_dict() for i in self.insights],
            "root_causes": self.root_causes,
            "risks": [r.to_dict() for r in self.risks],
            "opportunities": [o.to_dict() for o in self.opportunities],
            "recommendations": [r.to_dict() for r in self.recommendations],
            "scorecard": self.scorecard.to_dict() if self.scorecard else None,
            "executive_summary": self.executive_summary.to_dict()
            if self.executive_summary else None,
        }
