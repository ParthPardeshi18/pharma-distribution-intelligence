"""Decision Intelligence tests: KPI scoring, engines, health index, domains."""
import pytest

from src.di.base import Recommendation, grade
from src.di.engines import make_metric, rank_recommendations, scorecard
from src.di.kpis import REGISTRY, get_spec, score


# --------------------------- KPI registry & scoring ---------------------- #
def test_registry_directions_valid():
    for s in REGISTRY.values():
        assert s.direction in ("up_good", "down_good", "neutral"), s.key


def test_specs_with_anchors_score_in_range():
    # KPIs that declare both anchors must score within 0-100 at the anchors.
    for s in REGISTRY.values():
        if s.good is not None and s.bad is not None:
            assert s.score(s.good) == 100.0, s.key
            assert s.score(s.bad) == 0.0, s.key


def test_level_kpis_return_no_score():
    # Level metrics (e.g. revenue) intentionally have no anchors -> no score.
    assert get_spec("revenue_inr").score(1_000_000) is None


def test_up_good_scoring_monotonic():
    s = get_spec("revenue_growth_pct")  # good=12, bad=-8
    assert s.score(12) == 100.0
    assert s.score(-8) == 0.0
    assert s.score(2) == pytest.approx(50.0, abs=1)


def test_down_good_scoring_inverted():
    s = get_spec("debtor_days")  # good=15, bad=60 (lower better)
    assert s.score(15) == 100.0
    assert s.score(60) == 0.0
    assert s.score(8) == 100.0       # clamped


def test_score_clamped_0_100():
    assert score("gross_margin_pct", 100) == 100.0
    assert score("gross_margin_pct", -50) == 0.0


# --------------------------- engines ------------------------------------- #
def test_make_metric_computes_yoy_and_score():
    m = make_metric("revenue_growth_pct", 6.4)
    assert m.score is not None
    m2 = make_metric("gross_profit_inr", 100, prior=80)
    assert m2.yoy_pct == pytest.approx(25.0)


def test_scorecard_weighted():
    sc = scorecard("X", [("a", 100, 1), ("b", 0, 1)])
    assert sc.score == 50.0
    assert sc.grade in list("ABCDEF")


def test_recommendation_priority_ranking():
    a = Recommendation("hi", impact="high", effort="low", confidence=0.9)
    b = Recommendation("lo", impact="low", effort="high", confidence=0.3)
    assert a.priority_score > b.priority_score
    assert rank_recommendations([b, a])[0] is a


def test_grade_bands():
    assert grade(95) == "A" and grade(72) == "C" and grade(10) == "F"


# --------------------------- health index & domains (need warehouse) ----- #
from src.warehouse.db import DB_PATH  # noqa: E402

_skip = pytest.mark.skipif(not DB_PATH.exists(), reason="no warehouse db")


@_skip
def test_all_domains_analyze():
    from src.di.domains import ALL
    for mod in ALL:
        rep = mod.analyze()
        assert rep.domain
        assert rep.metrics or rep.summary


@_skip
def test_business_health_index_in_range():
    from src.di import health_index
    from src.di.domains import ALL
    bhi = health_index.compute([m.analyze() for m in ALL])
    assert 0 <= bhi.score <= 100
    assert bhi.grade in list("ABCDEF")
    assert bhi.components
