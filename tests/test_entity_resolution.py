"""Entity resolution tests: tiers, confidence, no-silent-merge guarantee."""
from src.entity_resolution import EntityResolver, stable_key


def test_stable_key_deterministic():
    assert stable_key("customer", "ABC MEDICAL") == stable_key("customer", "ABC MEDICAL")
    assert stable_key("customer", "ABC MEDICAL") != stable_key("customer", "XYZ MEDICAL")


def test_exact_match_tier():
    r = EntityResolver("customer")
    res = r.resolve(["ABC Medical"], ["ABC MEDICAL"])
    out = res[r.normalize_match("ABC Medical")]
    assert out.tier == "master_exact"
    assert out.confidence == 1.0


def test_route_marker_stripped_enables_match():
    r = EntityResolver("customer")
    # "VEDANTA (A) MEDICAL" should match master "VEDANTA MEDICAL"
    res = r.resolve(["VEDANTA (A) MEDICAL"], ["VEDANTA MEDICAL"])
    out = res[r.normalize_match("VEDANTA (A) MEDICAL")]
    assert out.tier in ("master_exact", "master_fuzzy")
    assert out.matched_master is not None


def test_unrelated_name_is_unresolved_not_merged():
    r = EntityResolver("customer")
    res = r.resolve(["COMPLETELY DIFFERENT XYZ"], ["ABC MEDICAL", "PQR PHARMA"])
    out = res[r.normalize_match("COMPLETELY DIFFERENT XYZ")]
    # never silently merged into an unrelated master
    assert out.tier in ("unresolved", "review")
    assert out.matched_master is None


def test_summary_counts_tiers():
    r = EntityResolver("customer")
    res = r.resolve(["ABC Medical", "XYZ Unknown"], ["ABC MEDICAL"])
    summ = EntityResolver.summarize(res)
    assert summ.get("master_exact", 0) == 1
