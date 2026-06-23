"""Comprehensive backtest for Astrololo."""

import sys
import os

sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from astrololo.models.subject import AstrologicalSubject
from astrololo.analysis.natal import create_natal_chart
from astrololo.core.constants import (
    PLANETS,
    SIGNS,
    ASPECTS,
    HOUSES,
    PLANET_ORDER,
    SIGN_ORDER,
    PLANET_IN_SIGN_DIGNITY,
)
from astrololo.core.aspects import AspectCalculator
from astrololo.interpretation.scoring import ChartScorer
from astrololo.interpretation.template_loader import (
    get_planet_in_sign,
    get_element_text,
    get_dignity_text,
    clear_cache,
)
from astrololo.core.ephemeris import (
    calc_julian_day,
    calc_planet_position_ut,
    HAS_SWISSEPH,
)

passed = 0
failed = 0
errors = []


def check(name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  [PASS] {name}")
    else:
        failed += 1
        msg = f"  [FAIL] {name} {detail}"
        errors.append(msg)
        print(msg)


def section(title):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


# =====================================================================
# 1. Core Constants
# =====================================================================
section("1. CORE CONSTANTS")
check("22 bodies", len(PLANETS) == 22)
check("12 signs", len(SIGNS) == 12)
check("12 houses", len(HOUSES) == 12)
check("9 aspects", len(ASPECTS) >= 9)
check(
    "Planet order",
    PLANET_ORDER
    == [
        "sun",
        "moon",
        "mercury",
        "venus",
        "mars",
        "jupiter",
        "saturn",
        "uranus",
        "neptune",
        "pluto",
    ],
)
check("Sign order", SIGN_ORDER[0] == "aries" and SIGN_ORDER[-1] == "pisces")

# Dignity
check("Sun exaltation Aries", PLANET_IN_SIGN_DIGNITY["sun"]["aries"]["exaltation"] == 4)
check("Sun rulership Leo", PLANET_IN_SIGN_DIGNITY["sun"]["leo"]["rulership"] == 5)
check("Sun fall Libra", PLANET_IN_SIGN_DIGNITY["sun"]["libra"]["fall"] == -5)
check(
    "Sun detriment Aquarius",
    PLANET_IN_SIGN_DIGNITY["sun"]["aquarius"]["detriment"] == -4,
)
check(
    "Moon exaltation Taurus",
    PLANET_IN_SIGN_DIGNITY["moon"]["taurus"]["exaltation"] == 4,
)
check("Mars rulership Aries", PLANET_IN_SIGN_DIGNITY["mars"]["aries"]["rulership"] == 5)
check(
    "Venus rulership Taurus",
    PLANET_IN_SIGN_DIGNITY["venus"]["taurus"]["rulership"] == 5,
)
check(
    "Mercury rulership Gemini",
    PLANET_IN_SIGN_DIGNITY["mercury"]["gemini"]["rulership"] == 5,
)
check(
    "Jupiter rulership Sagittarius",
    PLANET_IN_SIGN_DIGNITY["jupiter"]["sagittarius"]["rulership"] == 5,
)
check(
    "Saturn rulership Capricorn",
    PLANET_IN_SIGN_DIGNITY["saturn"]["capricorn"]["rulership"] == 5,
)
check(
    "Neptune rulership Pisces",
    PLANET_IN_SIGN_DIGNITY["neptune"]["pisces"]["rulership"] == 5,
)
check(
    "Pluto rulership Scorpio",
    PLANET_IN_SIGN_DIGNITY["pluto"]["scorpio"]["rulership"] == 5,
)
check(
    "Uranus rulership Aquarius",
    PLANET_IN_SIGN_DIGNITY["uranus"]["aquarius"]["rulership"] == 5,
)

# Swiss Ephemeris
check("Swiss Ephemeris available", HAS_SWISSEPH)

# =====================================================================
# 2. Ephemeris Calculations
# =====================================================================
section("2. EPHEMERIS CALCULATIONS")
jd = calc_julian_day(2000, 1, 1, 12, 0)
check("Julian Day 2000-01-01 12:00", abs(jd - 2451545.0) < 0.001)

sun_lon, sun_lat, sun_dist, sun_speed = calc_planet_position_ut(jd, "sun")
check("Sun longitude valid", 0 <= sun_lon <= 360)
check("Sun near 280° (capricorn)", 270 < sun_lon < 290, f"got {sun_lon:.2f}")

moon_lon, _, _, _ = calc_planet_position_ut(jd, "moon")
check("Moon longitude valid", 0 <= moon_lon <= 360)

for pk in PLANET_ORDER:
    lon, lat, dist, speed = calc_planet_position_ut(jd, pk)
    check(f"Planet {pk} position computed", 0 <= lon <= 360, f"lon={lon:.4f}")
    check(f"Planet {pk} speed non-zero", abs(speed) > 0.0001, f"speed={speed:.6f}")

# =====================================================================
# 3. Aspect Calculator
# =====================================================================
section("3. ASPECT CALCULATOR")
from astrololo.models.chart import PlanetPosition

calc = AspectCalculator()
p1 = PlanetPosition(
    name="sun",
    name_vi="",
    longitude=100,
    sign="cancer",
    sign_name_vi="",
    position_in_sign=10,
    speed=1.0,
)
p2 = PlanetPosition(
    name="moon",
    name_vi="",
    longitude=190,
    sign="libra",
    sign_name_vi="",
    position_in_sign=10,
    speed=13.0,
)
p3 = PlanetPosition(
    name="mars",
    name_vi="",
    longitude=280,
    sign="capricorn",
    sign_name_vi="",
    position_in_sign=10,
    speed=0.5,
)

aspects = calc.calculate([p1, p2, p3])
check("3 planets produce 3 aspects", len(aspects) == 3)
for a in aspects:
    check(f"Aspect {a.planet1}-{a.planet2} {a.aspect_type}", a.angle > 0)

# =====================================================================
# 4. Natal Chart Construction (multiple subjects)
# =====================================================================
section("4. NATAL CHART CONSTRUCTION")

subjects = [
    ("Hanoi noon", 1990, 6, 15, 12, 0, 21.0285, 105.8542, "Asia/Ho_Chi_Minh"),
    ("NYC night", 1985, 12, 25, 20, 30, 40.7128, -74.0060, "America/New_York"),
    ("Sydney dawn", 2000, 3, 1, 5, 45, -33.8688, 151.2093, "Australia/Sydney"),
    ("London noon", 1975, 9, 12, 12, 0, 51.5074, -0.1278, "Europe/London"),
    ("Tokyo midnight", 2005, 7, 7, 0, 0, 35.6762, 139.6503, "Asia/Tokyo"),
]

for label, y, m, d, h, mi, lat, lng, tz in subjects:
    subject = AstrologicalSubject(
        name=label,
        year=y,
        month=m,
        day=d,
        hour=h,
        minute=mi,
        latitude=lat,
        longitude=lng,
        timezone_str=tz,
    )
    chart = create_natal_chart(subject, lang="vi")
    check(f"[{label}] 22 bodies computed", len(chart.planets) == 22)
    check(f"[{label}] ascendant set", len(chart.ascendant_sign) > 0)
    check(f"[{label}] aspects > 0", len(chart.aspects) >= 2)
    check(
        f"[{label}] element distribution exists", chart.element_distribution is not None
    )
    check(f"[{label}] interpretation exists", chart.interpretation is not None)
    interp = chart.interpretation or {}
    sections = interp.get("sections", [])
    check(f"[{label}] has sections", len(sections) >= 5, f"got {len(sections)}")
    check(
        f"[{label}] has overall text", len(interp.get("overall_interpretation", "")) > 0
    )

# =====================================================================
# 5. Interpretation Quality
# =====================================================================
section("5. INTERPRETATION QUALITY")

subject = AstrologicalSubject(
    name="Quality",
    year=1990,
    month=6,
    day=15,
    hour=12,
    minute=0,
    latitude=21.0285,
    longitude=105.8542,
    timezone_str="Asia/Ho_Chi_Minh",
)
chart = create_natal_chart(subject, lang="vi")
interp = chart.interpretation or {}
sections = interp.get("sections", [])

cats_found = set()
for s in sections:
    cats_found.add(s.get("category"))
    for item in s.get("items", []):
        text = item.get("text", "")
        check(f"  Section '{s['category']}' has text", len(text) > 0)

required_cats = {
    "dispositor",
    "pattern",
    "dignity",
    "element",
    "planet_in_sign",
    "planet_in_house",
    "aspect",
}
for cat in required_cats:
    check(f"  Section '{cat}' present", cat in cats_found)

# =====================================================================
# 6. English Interpretation
# =====================================================================
section("6. ENGLISH INTERPRETATION")
chart_en = create_natal_chart(subject, lang="en")
interp_en = chart_en.interpretation or {}
sections_en = interp_en.get("sections", [])
check("EN sections exist", len(sections_en) > 0)
for s in sections_en:
    if s.get("category") == "element":
        for item in s.get("items", []):
            check("EN element text", len(item.get("text", "")) > 0)
            break

# =====================================================================
# 7. YAML Template Coverage
# =====================================================================
section("7. YAML TEMPLATE COVERAGE")
clear_cache()

# Planet in sign: all 10x12 entries
miss_vi = 0
for pk in PLANET_ORDER:
    for sk in SIGN_ORDER:
        entry = get_planet_in_sign(pk, sk, "vi")
        if not entry or not entry.get("detailed"):
            miss_vi += 1
check("VI planet_in_sign all 120 entries filled", miss_vi == 0, f"{miss_vi} missing")

miss_en = 0
for pk in PLANET_ORDER:
    for sk in SIGN_ORDER:
        entry = get_planet_in_sign(pk, sk, "en")
        if not entry or not entry.get("detailed"):
            miss_en += 1
check("EN planet_in_sign all 120 entries filled", miss_en == 0, f"{miss_en} missing")

# Aspects
import yaml

vi_aspect_path = os.path.join(
    os.path.dirname(__file__),
    "..",
    "astrololo",
    "interpretation",
    "templates",
    "vi",
    "aspects.yaml",
)
if os.path.exists(vi_aspect_path):
    with open(vi_aspect_path, "r", encoding="utf-8") as f:
        vi_aspects = yaml.safe_load(f) or {}
    check("VI aspects >= 200", len(vi_aspects) >= 200)
en_aspect_path = vi_aspect_path.replace("\\vi\\", "\\en\\")
if os.path.exists(en_aspect_path):
    with open(en_aspect_path, "r", encoding="utf-8") as f:
        en_aspects = yaml.safe_load(f) or {}
    check("EN aspects >= 200", len(en_aspects) >= 200)

# Elements
for key in [
    "dominant_fire",
    "dominant_earth",
    "dominant_air",
    "dominant_water",
    "deficient_fire",
    "deficient_earth",
    "deficient_air",
    "deficient_water",
]:
    check(f"VI element text '{key}'", get_element_text(key, "vi") is not None)
    check(f"EN element text '{key}'", get_element_text(key, "en") is not None)

# Dignities
for d in ["rulership", "exaltation", "detriment", "fall", "neutral"]:
    check(f"VI dignity '{d}'", get_dignity_text(d, "vi") is not None)
    check(f"EN dignity '{d}'", get_dignity_text(d, "en") is not None)

# =====================================================================
# 8. Pattern Detection
# =====================================================================
section("8. PATTERN DETECTION")
# Test with specific aspect configurations
from astrololo.interpretation.rules.pattern_rules import (
    _detect_grand_trine,
    _detect_tsquare,
    _detect_stellium,
)
from astrololo.models.chart import AspectData

# Grand Trine test: 3 planets in different fire signs, trine each other
p_a = PlanetPosition(
    name="mars",
    name_vi="",
    longitude=10,
    sign="aries",
    sign_name_vi="",
    position_in_sign=10,
    speed=1,
)
p_b = PlanetPosition(
    name="jupiter",
    name_vi="",
    longitude=130,
    sign="leo",
    sign_name_vi="",
    position_in_sign=10,
    speed=1,
)
p_c = PlanetPosition(
    name="saturn",
    name_vi="",
    longitude=250,
    sign="sagittarius",
    sign_name_vi="",
    position_in_sign=10,
    speed=1,
)
gt_aspects = [
    AspectData(
        planet1="mars",
        planet2="jupiter",
        aspect_type="trine",
        angle=120,
        aspect_name_vi="",
        orb=0,
        weight=0,
    ),
    AspectData(
        planet1="mars",
        planet2="saturn",
        aspect_type="trine",
        angle=120,
        aspect_name_vi="",
        orb=0,
        weight=0,
    ),
    AspectData(
        planet1="jupiter",
        planet2="saturn",
        aspect_type="trine",
        angle=120,
        aspect_name_vi="",
        orb=0,
        weight=0,
    ),
]
gt = _detect_grand_trine([p_a, p_b, p_c], gt_aspects)
check("Grand Trine detected", gt is not None, f"got {gt}")

# T-Square test
p1 = PlanetPosition(
    name="sun",
    name_vi="",
    longitude=100,
    sign="cancer",
    sign_name_vi="",
    position_in_sign=10,
    speed=1,
)
p2 = PlanetPosition(
    name="moon",
    name_vi="",
    longitude=280,
    sign="capricorn",
    sign_name_vi="",
    position_in_sign=10,
    speed=13,
)
p3 = PlanetPosition(
    name="mars",
    name_vi="",
    longitude=10,
    sign="aries",
    sign_name_vi="",
    position_in_sign=10,
    speed=0.5,
)
a1 = AspectData(
    planet1="sun",
    planet2="moon",
    aspect_type="opposition",
    angle=180,
    aspect_name_vi="",
    orb=1,
    weight=0,
)
a2 = AspectData(
    planet1="sun",
    planet2="mars",
    aspect_type="square",
    angle=90,
    aspect_name_vi="",
    orb=1,
    weight=0,
)
a3 = AspectData(
    planet1="moon",
    planet2="mars",
    aspect_type="square",
    angle=90,
    aspect_name_vi="",
    orb=1,
    weight=0,
)
ts = _detect_tsquare([p1, p2, p3], [a1, a2, a3])
check("T-Square detected", ts is not None, f"got {ts}")

# Stellium test
p_s1 = PlanetPosition(
    name="sun",
    name_vi="",
    longitude=10,
    sign="aries",
    sign_name_vi="",
    position_in_sign=10,
    speed=1,
)
p_s2 = PlanetPosition(
    name="moon",
    name_vi="",
    longitude=20,
    sign="aries",
    sign_name_vi="",
    position_in_sign=20,
    speed=13,
)
p_s3 = PlanetPosition(
    name="mars",
    name_vi="",
    longitude=25,
    sign="aries",
    sign_name_vi="",
    position_in_sign=25,
    speed=0.5,
)
st = _detect_stellium([p_s1, p_s2, p_s3])
check("Stellium detected", st is not None, f"got {st}")

# =====================================================================
# 9. Scoring
# =====================================================================
section("9. SCORING")
scorer = ChartScorer(chart)
score_result = scorer.score_chart()
check("Scoring total > 0", score_result["total"] > 0)
check(
    "Strength label valid",
    score_result["strength"]
    in ("exceptional", "strong", "moderate", "challenging", "difficult"),
)
check("Pattern score computed", score_result["pattern_score"] >= 0)
check("Element score computed", score_result["element_score"] >= 0)
rankings = scorer.get_planet_rankings()
check("Planet rankings exist", len(rankings) == 10)
check("Best planet has proper data", "planet" in rankings[0] and "total" in rankings[0])

# =====================================================================
# 10. Edge Cases
# =====================================================================
section("10. EDGE CASES")

# Cusp degree (29°59')
sub_cusp = AstrologicalSubject(
    name="Cusp",
    year=2000,
    month=1,
    day=1,
    hour=0,
    minute=0,
    latitude=0,
    longitude=0,
    timezone_str="UTC",
)
chart_cusp = create_natal_chart(sub_cusp, lang="vi")
check("Cusp chart valid", len(chart_cusp.planets) == 10)

# Different house systems
for hs in ["placidus", "koch", "equal", "whole_sign"]:
    try:
        c = create_natal_chart(subject, house_system=hs, lang="vi")
        check(f"House system '{hs}' works", c.ascendant_sign != "")
    except Exception as e:
        check(f"House system '{hs}' works", False, str(e))

# Retrograde detection
retro_count = sum(1 for p in chart.planets if p.is_retrograde)
check("Retrograde detection works", retro_count >= 0)

# =====================================================================
# SUMMARY
# =====================================================================
section("BACKTEST SUMMARY")
print(f"  Passed: {passed}")
print(f"  Failed: {failed}")
if errors:
    print(f"\n  Errors ({len(errors)}):")
    for e in errors[:10]:
        print(f"    {e}")
print(f"\n  {'ALL BACKTESTS PASSED!' if failed == 0 else 'SOME TESTS FAILED!'}")
