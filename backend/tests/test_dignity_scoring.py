"""Phase 2 TDD tests: dignity scoring preservation of the essential+accidental contract.

Spec refs: 010 §2.1.

These tests are ephemeris-neutral: they assert only the structural contract,
not exact values tied to a specific birth date. Avoiding that eliminates
false failures if combustion, cazimi, or strong essential dignities change
the final score.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from astrololo.models.subject import AstrologicalSubject
from astrololo.analysis.natal import create_natal_chart
from astrololo.scoring.dignity import calc_essential, calc_accidental, chart_dignity_scores


def _chart():
    return create_natal_chart(AstrologicalSubject(
        name="LangSon", year=1996, month=3, day=11,
        hour=11, minute=23,
        latitude=21.85, longitude=106.76,
        timezone_str="Asia/Ho_Chi_Minh"
    ), lang="vi")


class TestDignityScoring:
    def test_chart_has_dignity_scores_dict(self):
        c = _chart()
        assert hasattr(c, "dignity_scores"), "ChartData must expose dignity_scores"
        assert isinstance(c.dignity_scores, dict)
        for p in c.planets:
            if p.body_type == "planet":
                assert p.name in c.dignity_scores, f"{p.name} missing from dignity_scores"

    def test_dignity_is_essential_plus_accidental_for_all_planets(self):
        c = _chart()
        sun = next(p for p in c.planets if p.name == "sun")
        for p in c.planets:
            if p.body_type != "planet":
                continue
            ess = calc_essential(p.name, p.sign, degree=p.position_in_sign, is_daytime=c.is_daytime)
            acc = calc_accidental(p.name, p.house, p.is_retrograde, p.longitude, sun.longitude)
            assert c.dignity_scores[p.name] == ess + acc, (
                f"{p.name}: expected {ess+acc}, got {c.dignity_scores[p.name]}"
            )

    def test_non_planet_bodies_excluded(self):
        c = _chart()
        for p in c.planets:
            if p.body_type != "planet":
                assert p.name not in c.dignity_scores, f"{p.name} should not have a dignity score"

    def test_dignity_bounds_reasonable(self):
        c = _chart()
        for name, score in c.dignity_scores.items():
            assert -15 <= score <= 20, f"{name} score {score} outside reasonable range"

    def test_chart_dignity_scores_function_matches(self):
        c = _chart()
        expected = chart_dignity_scores(c)
        assert c.dignity_scores == expected, "chart_dignity_scores helper must match chart.dignity_scores"
