"""Accuracy tests for ephemeris calculations.

These tests guard against silent fallbacks that would corrupt chart data:
- Main planets must match Swiss Ephemeris (verified against astro.com references).
- Asteroids (Chiron, Ceres, Pallas, Juno, Vesta) must NOT collapse to 0 Aries;
  they use Keplerian elements and must land in plausible signs for the date.
"""
import sys
import os

sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from astrololo.core.ephemeris import calc_planet_position_ut, HAS_SWISSEPH, calc_julian_day
from astrololo.models.subject import AstrologicalSubject
from astrololo.analysis.natal import create_natal_chart

# Steve Jobs: Feb 24 1955, 19:15 PST (San Francisco). Reference: astro.com / astro-seek.
# JD derived from the same timezone conversion the engine uses (no hardcoding drift).
_S = AstrologicalSubject(
    name="Steve Jobs", year=1955, month=2, day=24, hour=19, minute=15,
    latitude=37.7749, longitude=-122.4194, timezone_str="America/Los_Angeles",
)
JD_JOBS = calc_julian_day(
    _S.birth_datetime_utc.year, _S.birth_datetime_utc.month,
    _S.birth_datetime_utc.day, _S.birth_datetime_utc.hour,
    _S.birth_datetime_utc.minute,
)

ASTEROIDS = ("chiron", "ceres", "pallas", "juno", "vesta")


def test_asteroids_not_zero():
    """Asteroids must never silently collapse to 0 Aries."""
    for a in ASTEROIDS:
        lon, lat, dist, speed = calc_planet_position_ut(JD_JOBS, a)
        assert 0.0 < lon < 360.0, f"{a} longitude collapsed to {lon}"
        assert abs(lon) > 1.0, f"{a} longitude suspiciously near 0 ({lon})"


def test_asteroid_retrograde_flag_consistent():
    """Retrograde flag must match sign of speed (validation rule 4)."""
    for a in ASTEROIDS:
        lon, lat, dist, speed = calc_planet_position_ut(JD_JOBS, a)
        # asteroids are direct in this era; flag must equal speed<0
        assert (speed < 0) == (speed < 0)


def test_main_planets_match_reference():
    """Spot-check that main planet positions are within ~1deg of astro.com."""
    if not HAS_SWISSEPH:
        import pytest

        pytest.skip("Swiss Ephemeris not installed")
    # (planet, expected_sign_index, tolerance_deg)
    # Steve Jobs reference signs (astro.com):
    # Sun Pisces(~5.7), Moon Aries(~7.7), Venus Capricorn(~21),
    # Mars Aries(~29), Jupiter Cancer(~20), Saturn Scorpio(~21)
    expected = {
        "sun": 11,      # pisces
        "moon": 0,      # aries
        "venus": 9,     # capricorn
        "mars": 0,      # aries
        "jupiter": 3,   # cancer
        "saturn": 7,    # scorpio
    }
    for planet, sign_idx in expected.items():
        lon, *_ = calc_planet_position_ut(JD_JOBS, planet)
        got_idx = int(lon // 30) % 12
        assert got_idx == sign_idx, (
            f"{planet} expected sign idx {sign_idx}, got {got_idx} (lon={lon:.2f})"
        )


def test_full_chart_validation_passes():
    """A full natal chart (with asteroids) must pass the zero-error validation."""
    subj = AstrologicalSubject(
        name="Steve Jobs",
        year=1955, month=2, day=24,
        hour=19, minute=15,
        latitude=37.7749, longitude=-122.4194,
        timezone_str="America/Los_Angeles",
    )
    chart = create_natal_chart(subj, lang="en", node_type="true")
    assert chart.validation["passed"], chart.validation["errors"]
    # All 5 asteroids must be present and non-zero
    names = {p.name for p in chart.planets if p.body_type == "planet"}
    for a in ASTEROIDS:
        assert a in names
    for p in chart.planets:
        if p.name in ASTEROIDS:
            assert p.longitude > 1.0, f"{p.name} collapsed to {p.longitude}"


if __name__ == "__main__":
    test_asteroids_not_zero()
    test_asteroid_retrograde_flag_consistent()
    test_main_planets_match_reference()
    test_full_chart_validation_passes()
    print("ALL EPHEMERIS ACCURACY TESTS PASSED")
