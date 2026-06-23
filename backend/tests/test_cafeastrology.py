"""Comprehensive end-to-end test against cafeastrology.com reference data.

Verifies Astrololo positions match cafeastrology for 3 independently
verified dates. Covers: planets, houses, angles, nodes, aspects.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from astrololo.models.subject import AstrologicalSubject
from astrololo.analysis.natal import create_natal_chart

# ---------------------------------------------------------------------------
# Reference data -- verified against cafeastrology.com HTML output
# Format: (name, year, month, day, hour, min, lat, lon, tz, ref_planets, ref_houses, ref_angles)
# ref_planets: {key: (sign, deg_float, house, retro)}
# ref_houses: {house_num: sign_key}
# ref_angles: {key: (sign, deg_float)}
# ---------------------------------------------------------------------------

Reference = dict


def ref(name, year, month, day, hour, minute, lat, lon, tz,
        planets=None, houses=None, angles=None, aspects=None):
    """Build reference dict."""
    return {
        "name": name, "year": year, "month": month, "day": day,
        "hour": hour, "minute": minute,
        "lat": lat, "lon": lon, "tz": tz,
        "planets": planets or {},
        "houses": houses or {},
        "angles": angles or {},
        "aspects": aspects or [],
    }


def _d(d, m):
    """Degrees + minutes to float."""
    return d + m / 60.0


# --- Reference: 19/10/2022 16:40 Hanoi (verified via test_20221019.py) ---
R20221019 = ref(
    name="20221019", year=2022, month=10, day=19, hour=16, minute=40,
    lat=21.0285, lon=105.8542, tz="Asia/Ho_Chi_Minh",
    planets={
        "sun":     ("libra",      _d(25, 59), 7, False),
        "moon":    ("leo",        _d(14, 25), 5, False),
        "mercury": ("libra",      _d(12, 31), 7, False),
        "venus":   ("libra",      _d(25, 5),  7, False),
        "mars":    ("gemini",     _d(24, 45), 3, False),
        "jupiter": ("aries",      _d(0, 52),  12, True),
        "saturn":  ("aquarius",   _d(18, 36), 11, True),
        "uranus":  ("taurus",     _d(17, 45), 2, True),
        "neptune": ("pisces",     _d(23, 11), 12, True),
        "pluto":   ("capricorn",  _d(26, 9),  10, False),
    },
    houses={1:"aries",2:"taurus",3:"gemini",4:"cancer",5:"leo",6:"virgo",
            7:"libra",8:"scorpio",9:"sagittarius",10:"capricorn",11:"aquarius",12:"pisces"},
    angles={
        "ascendant": ("aries", _d(11, 21)),
        "mc":        ("capricorn", _d(7, 59)),
    },
)

# --- Reference: 15/11/1989 12:00 Hanoi (verified 15/11/1989) ---
R19891115 = ref(
    name="19891115", year=1989, month=11, day=15, hour=12, minute=0,
    lat=21.0285, lon=105.8542, tz="Asia/Ho_Chi_Minh",
    planets={
        "sun":     ("scorpio",    _d(22, 48), 9, False),
        "moon":    ("gemini",     _d(20, 23), 4, False),
        "mercury": ("scorpio",    _d(25, 24), 9, False),
        "venus":   ("capricorn",  _d(9, 42),  11, False),
        "mars":    ("scorpio",    _d(7, 23),  9, False),
        "jupiter": ("cancer",     _d(10, 23), 5, True),
        "saturn":  ("capricorn",  _d(10, 31), 11, False),
        "uranus":  ("capricorn",  _d(3, 6),   11, False),
        "neptune": ("capricorn",  _d(10, 25), 11, False),
        "pluto":   ("scorpio",    _d(15, 25), 9, False),
    },
    houses={1:"aquarius",2:"pisces",3:"aries",4:"taurus",5:"gemini",6:"cancer",
            7:"leo",8:"virgo",9:"libra",10:"scorpio",11:"sagittarius",12:"capricorn"},
    angles={
        "ascendant": ("aquarius", _d(16, 22)),
        "mc":        ("scorpio", _d(27, 24)),
    },
)

# --- Reference: 19/01/2022 16:35 Hanoi (user-provided cafeastrology) ---
R20220119 = ref(
    name="20220119", year=2022, month=1, day=19, hour=16, minute=35,
    lat=21.0285, lon=105.8542, tz="Asia/Ho_Chi_Minh",
    planets={
        "sun":     ("capricorn",  _d(29, 17), 7, False),
        "moon":    ("leo",        _d(15, 9),  2, False),
        "mercury": ("aquarius",   _d(8, 1),   7, True),
        "venus":   ("capricorn",  _d(13, 8),  6, True),
        "mars":    ("sagittarius",_d(26, 18), 6, False),
        "jupiter": ("pisces",     _d(4, 23),  8, False),
        "saturn":  ("aquarius",   _d(13, 59), 8, False),
        "uranus":  ("taurus",     _d(10, 50), 10, False),
        "neptune": ("pisces",     _d(21, 6),  9, False),
        "pluto":   ("capricorn",  _d(26, 42), 7, False),
    },
    houses={1:"cancer",2:"leo",3:"virgo",4:"libra",5:"scorpio",6:"sagittarius",
            7:"capricorn",8:"aquarius",9:"pisces",10:"aries",11:"taurus",12:"gemini"},
    angles={
        "ascendant": ("cancer", _d(16, 14)),
        "mc":        ("aries", _d(9, 11)),
    },
)

ALL_REFS = [R20221019, R19891115, R20220119]


def _generate(ref_data):
    s = AstrologicalSubject(
        name=ref_data["name"],
        year=ref_data["year"], month=ref_data["month"], day=ref_data["day"],
        hour=ref_data["hour"], minute=ref_data["minute"],
        latitude=ref_data["lat"], longitude=ref_data["lon"],
        timezone_str=ref_data["tz"],
    )
    chart = create_natal_chart(s, lang="vi")
    return chart


# ===========================================================================
# TESTS
# ===========================================================================

class TestCafeastrologyComparison:
    """Compare Astrololo positions against cafeastrology.com for 3 dates."""

    @pytest.fixture(params=ALL_REFS, ids=[r["name"] for r in ALL_REFS])
    def ref_data(self, request):
        return request.param

    @pytest.fixture
    def chart(self, ref_data):
        return _generate(ref_data)

    def test_validation_passes(self, chart):
        """All 7 validation checks pass."""
        assert chart.validation["passed"], f"Validation failed: {chart.validation}"

    def test_16_bodies_present(self, chart):
        """Chart has 22 bodies (16 planets + 2 nodes + 4 angles)."""
        assert len(chart.planets) == 22, f"Expected 22 bodies (16 planets + 2 nodes + 4 angles), got {len(chart.planets)}"
        types = {}
        for b in chart.planets:
            types[b.body_type] = types.get(b.body_type, 0) + 1
        assert types.get("planet") == 16, f"Expected 16 planets, got {types.get('planet')}"
        assert types.get("node") == 2, f"Expected 2 nodes, got {types.get('node')}"
        assert types.get("angle") == 4, f"Expected 4 angles, got {types.get('angle')}"

    def test_planet_signs(self, ref_data, chart):
        """All planet signs match cafeastrology reference."""
        errors = []
        for key, (exp_sign, exp_deg, exp_house, exp_retro) in ref_data["planets"].items():
            body = next((b for b in chart.planets if b.name == key), None)
            assert body is not None, f"{key} not found in chart"
            if body.sign != exp_sign:
                errors.append(f"{key}: expected sign {exp_sign}, got {body.sign}")
        assert not errors, "\n".join(errors)

    def test_planet_degrees(self, ref_data, chart):
        """Planet degree differences < 0.2° from cafeastrology."""
        max_diff = 0.0
        worst = ""
        for key, (exp_sign, exp_deg, exp_house, exp_retro) in ref_data["planets"].items():
            body = next((b for b in chart.planets if b.name == key), None)
            act_deg = body.longitude % 30
            diff = abs(act_deg - exp_deg)
            if diff > max_diff:
                max_diff = diff
                worst = f"{key}: expected {exp_deg:.2f}°, got {act_deg:.2f}° (diff={diff:.3f}°)"
        assert max_diff < 0.2, f"Degree diff too large: {worst}"

    def test_planet_houses(self, ref_data, chart):
        """All planet house assignments match cafeastrology."""
        errors = []
        for key, (exp_sign, exp_deg, exp_house, exp_retro) in ref_data["planets"].items():
            body = next((b for b in chart.planets if b.name == key), None)
            if body.house != exp_house:
                errors.append(f"{key}: expected H{exp_house}, got H{body.house}")
        assert not errors, "\n".join(errors)

    def test_planet_retrograde(self, ref_data, chart):
        """All retrograde flags match cafeastrology."""
        errors = []
        for key, (exp_sign, exp_deg, exp_house, exp_retro) in ref_data["planets"].items():
            body = next((b for b in chart.planets if b.name == key), None)
            if body.is_retrograde != exp_retro:
                status = "R" if body.is_retrograde else "D"
                errors.append(f"{key}: expected retro={exp_retro}, got {status}")
        assert not errors, "\n".join(errors)

    def test_angle_signs(self, ref_data, chart):
        """ASC and MC signs match cafeastrology."""
        errors = []
        for key, (exp_sign, exp_deg) in ref_data["angles"].items():
            body = next((b for b in chart.planets if b.name == key), None)
            assert body is not None, f"{key} not found"
            if body.sign != exp_sign:
                errors.append(f"{key}: expected sign {exp_sign}, got {body.sign}")
        assert not errors, "\n".join(errors)

    def test_angle_degrees(self, ref_data, chart):
        """ASC and MC degree differences < 0.2°."""
        max_diff = 0.0
        for key, (exp_sign, exp_deg) in ref_data["angles"].items():
            body = next((b for b in chart.planets if b.name == key), None)
            act_deg = body.longitude % 30
            diff = abs(act_deg - exp_deg)
            if diff > max_diff:
                max_diff = diff
        assert max_diff < 0.2, f"Angle diff too large: {max_diff:.3f}°"

    def test_house_signs(self, ref_data, chart):
        """All 12 house cusp signs match cafeastrology."""
        errors = []
        for hn in range(1, 13):
            h = chart.houses[hn - 1]
            exp_sign = ref_data["houses"][hn]
            if h.sign != exp_sign:
                errors.append(f"H{hn}: expected {exp_sign}, got {h.sign}")
        assert not errors, "\n".join(errors)

    def test_aspects_count(self, chart):
        """Chart has at least 50 major aspects (planet-planet + nodes + angles)."""
        assert len(chart.aspects) >= 50, f"Expected >=50 aspects, got {len(chart.aspects)}"

    def test_body_types_correct(self, chart):
        """Verify body_type is correct for each body."""
        for b in chart.planets:
            if b.name in ("sun","moon","mercury","venus","mars","jupiter","saturn","uranus","neptune","pluto"):
                assert b.body_type == "planet", f"{b.name} should be planet, got {b.body_type}"
            elif b.name in ("north_node","south_node"):
                assert b.body_type == "node", f"{b.name} should be node, got {b.body_type}"
            elif b.name in ("ascendant","mc","descendant","ic"):
                assert b.body_type == "angle", f"{b.name} should be angle, got {b.body_type}"

    def test_bilingual_names(self, chart):
        """Body has both VI and EN names."""
        for b in chart.planets:
            assert b.name_vi, f"{b.name} missing name_vi"
            assert b.sign_name_vi, f"{b.name} missing sign_name_vi"

    def test_asc_equals_house1(self, chart):
        """ASC longitude == House I cusp (validation check 1)."""
        asc_body = next(b for b in chart.planets if b.name == "ascendant")
        h1 = chart.houses[0]
        diff = abs(asc_body.longitude - h1.cusp_degree)
        assert diff < 0.01, f"ASC={asc_body.longitude:.4f} != H1={h1.cusp_degree:.4f}"

    def test_mc_equals_house10(self, chart):
        """MC longitude == House X cusp (validation check 2)."""
        mc_body = next(b for b in chart.planets if b.name == "mc")
        h10 = chart.houses[9]
        diff = abs(mc_body.longitude - h10.cusp_degree)
        assert diff < 0.01, f"MC={mc_body.longitude:.4f} != H10={h10.cusp_degree:.4f}"

    def test_axis_opposition_180(self, chart):
        """ASC-DSC and MC-IC are exactly 180° apart."""
        asc = next(b.longitude for b in chart.planets if b.name == "ascendant")
        dsc = next(b.longitude for b in chart.planets if b.name == "descendant")
        mc = next(b.longitude for b in chart.planets if b.name == "mc")
        ic = next(b.longitude for b in chart.planets if b.name == "ic")
        diff_ad = min(abs(asc - dsc), 360 - abs(asc - dsc))
        diff_mi = min(abs(mc - ic), 360 - abs(mc - ic))
        assert abs(diff_ad - 180) < 0.01, f"ASC-DSC={diff_ad:.4f} != 180"
        assert abs(diff_mi - 180) < 0.01, f"MC-IC={diff_mi:.4f} != 180"

    def test_all_bodies_orb_formatted(self, chart):
        """Every aspect has orb_formatted in dms format."""
        for a in chart.aspects:
            assert a.orb_formatted, f"Aspect {a.planet1}-{a.planet2} missing orb_formatted"
            assert "\u00b0" in a.orb_formatted, f"Bad format: {a.orb_formatted}"
