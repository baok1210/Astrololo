"""Phase 3 TDD tests: dominant planet weighted scoring.

Spec refs: 010 §3.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from astrololo.models.subject import AstrologicalSubject
from astrololo.analysis.natal import create_natal_chart
from astrololo.scoring.dominant import calc_dominant_score, chart_dominant_scores


def _chart():
    return create_natal_chart(AstrologicalSubject(
        name="LangSon", year=1996, month=3, day=11,
        hour=11, minute=23,
        latitude=21.85, longitude=106.76,
        timezone_str="Asia/Ho_Chi_Minh"
    ), lang="vi")


class TestDominantScoring:
    def test_chart_has_dominant_scores_dict(self):
        c = _chart()
        assert hasattr(c, "dominant_scores"), "ChartData must expose dominant_scores"
        assert isinstance(c.dominant_scores, dict)
        for p in c.planets:
            if p.body_type == "planet":
                assert p.name in c.dominant_scores, f"{p.name} missing from dominant_scores"

    def test_dominant_is_float(self):
        c = _chart()
        for name, score in c.dominant_scores.items():
            assert isinstance(score, float), f"{name} dominant score must be float"

    def test_luminaries_outrank_outer(self):
        c = _chart()
        assert c.dominant_scores["sun"] > c.dominant_scores.get("pluto", -1)
        assert c.dominant_scores["moon"] > c.dominant_scores.get("pluto", -1)

    def test_angular_boost_raises_dominant_over_same_dignity(self):
        c = _chart()
        sun = next(p for p in c.planets if p.name == "sun")
        mercury = next(p for p in c.planets if p.name == "mercury")
        if sun and mercury and sun.house in {1, 4, 7, 10}:
            assert c.dominant_scores["sun"] > c.dominant_scores["mercury"]

    def test_helper_matches_chart_attribute(self):
        c = _chart()
        expected = chart_dominant_scores(c)
        assert c.dominant_scores == expected
