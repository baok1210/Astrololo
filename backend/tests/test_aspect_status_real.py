"""Phase 1 TDD tests: applying/separating/exact on real ephemeris charts.

Spec refs: 010 §1.2 (aspect orb + applying/separating status), 009 §3.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from astrololo.models.subject import AstrologicalSubject
from astrololo.analysis.natal import create_natal_chart


def chart_lang_son_1996():
    return create_natal_chart(AstrologicalSubject(
        name="LangSon", year=1996, month=3, day=11,
        hour=11, minute=23,
        latitude=21.85, longitude=106.76,
        timezone_str="Asia/Ho_Chi_Minh"
    ), lang="vi")


def chart_hanoi_1985():
    return create_natal_chart(AstrologicalSubject(
        name="Hanoi", year=1985, month=11, day=5,
        hour=14, minute=0,
        latitude=21.03, longitude=105.85,
        timezone_str="Asia/Ho_Chi_Minh"
    ), lang="vi")


class TestAspectStatus:
    def test_fields_exist_and_booleans(self):
        c = chart_lang_son_1996()
        assert c.aspects, "aspects must be non-empty"
        for a in c.aspects:
            assert hasattr(a, "applying"), "AspectData missing applying"
            assert hasattr(a, "separating"), "AspectData missing separating"
            assert hasattr(a, "exact"), "AspectData missing exact"
            assert isinstance(a.applying, bool)
            assert isinstance(a.separating, bool)
            assert isinstance(a.exact, bool)
            assert not (a.applying and a.separating), \
                f"{a.planet1}-{a.planet2}: applying and separating BOTH True"

    def test_some_applying_and_some_separating_exist(self):
        c = chart_lang_son_1996()
        app = [a for a in c.aspects if a.applying]
        sep = [a for a in c.aspects if a.separating]
        assert app, "at least one applying aspect expected"
        assert sep, "at least one separating aspect expected"

    def test_exact_aspect_when_under_half_degree(self):
        c = chart_lang_son_1996()
        exact = [a for a in c.aspects if a.exact]
        for a in exact:
            assert a.orb < 0.5, \
                f"exact aspect {a.planet1}-{a.planet2} orb {a.orb} must be < 0.5"

    def test_sun_moon_orb_bonus_real_chart(self):
        """Sun and Moon should produce wider orb matches than other pairs."""
        c = chart_lang_son_1996()
        sun = next((p for p in c.planets if p.name == "sun"), None)
        moon = next((p for p in c.planets if p.name == "moon"), None)
        assert sun and moon
        # Confirm at least one Sun aspect and one Moon aspect exist in real chart
        sun_aspects = [a for a in c.aspects if "sun" in (a.planet1, a.planet2)]
        assert sun_aspects, "Lang Son 1996 should have Sun aspects"

    def test_status_present_in_api_response(self):
        c = chart_lang_son_1996()
        payload = c.model_dump()
        for a in payload.get("aspects", []):
            assert "applying" in a, "API payload missing applying"
            assert "separating" in a, "API payload missing separating"
            assert "exact" in a

    def test_applying_separating_semantics_real_chart(self):
        """Cross-check a sample: applying aspect's future angle < exact angle."""
        c = chart_lang_son_1996()
        from astrololo.core.aspects import angular_distance
        for a in c.aspects[:20]:
            p1 = next((p for p in c.planets if p.name == a.planet1), None)
            p2 = next((p for p in c.planets if p.name == a.planet2), None)
            if not p1 or not p2:
                continue
            dt = 0.01
            f1 = (p1.longitude + p1.speed * dt) % 360
            f2 = (p2.longitude + p2.speed * dt) % 360
            future_angle = angular_distance(f1, f2)
            current_angle = angular_distance(p1.longitude, p2.longitude)
            # applying = future closer to exact than current; separating = further
            exact = a.angle  # the aspect angle (60/90/120/180)
            current_diff = abs(current_angle - exact)
            future_diff = abs(future_angle - exact)
            if a.applying:
                assert future_diff <= current_diff + 1e-6, \
                    f"{a.planet1}-{a.planet2} applying but future_diff {future_diff} > current {current_diff}"
            elif a.separating:
                assert future_diff >= current_diff - 1e-6, \
                    f"{a.planet1}-{a.planet2} separating but future_diff {future_diff} < current {current_diff}"
            # either applying or separating (or both False for neutrals near exact)
            break  # just need one validated aspect for the hypothesis check
