import sys
import os
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from astrololo.models.subject import AstrologicalSubject
from astrololo.analysis.natal import create_natal_chart
from astrololo.core.constants import PLANETS, SIGNS, ASPECTS, HOUSES, PLANET_IN_SIGN_DIGNITY
from astrololo.core.aspects import AspectCalculator
from astrololo.interpretation.scoring import ChartScorer


def test_constants():
    assert len(PLANETS) == 22, f"Expected 22 bodies (16 planets + 2 nodes + 4 angles), got {len(PLANETS)}"
    assert len(SIGNS) == 12, f"Expected 12 signs, got {len(SIGNS)}"
    assert len(ASPECTS) >= 5, f"Expected at least 5 aspects, got {len(ASPECTS)}"
    assert len(HOUSES) == 12, f"Expected 12 houses, got {len(HOUSES)}"
    print(f"[PASS] Core constants loaded: {len(PLANETS)} bodies, 12 signs, aspects, 12 houses")


def test_dignity():
    assert PLANET_IN_SIGN_DIGNITY["sun"]["aries"]["exaltation"] == 4
    assert PLANET_IN_SIGN_DIGNITY["sun"]["leo"]["rulership"] == 5
    assert PLANET_IN_SIGN_DIGNITY["sun"]["libra"]["fall"] == -5
    assert PLANET_IN_SIGN_DIGNITY["sun"]["aquarius"]["detriment"] == -4
    assert PLANET_IN_SIGN_DIGNITY["moon"]["taurus"]["exaltation"] == 4
    assert PLANET_IN_SIGN_DIGNITY["mars"]["aries"]["rulership"] == 5
    print("[PASS] Dignity tables correct")


def test_coordinates():
    from astrololo.core.coordinates import (
        abs_to_sign, decimal_to_rounded_dms,
        lon_to_sign_display,
    )
    # Sun at Libra 25.9833 = 205.9833
    sign, pos = abs_to_sign(205.9833)
    assert sign == "libra"
    assert abs(pos - 25.9833) < 0.001
    d, m = decimal_to_rounded_dms(205.9833)
    assert d == 205
    assert m == 59  # 58.998 min, seconds 59.88 >= 30 → round up
    sd, sd_deg, sd_min = lon_to_sign_display(205.9833)
    assert sd == "libra"
    assert sd_deg == 25
    assert sd_min == 59
    # Pluto at Capricorn 26.1432 = 296.1432
    sd2, sd2_deg, sd2_min = lon_to_sign_display(296.1432)
    assert sd2 == "capricorn"
    assert sd2_deg == 26
    assert sd2_min == 9  # 8.592 min, seconds 35.5 >= 30 → round up
    print("[PASS] Coordinates: 205.9833→libra 25°59', 296.1432→capricorn 26°09'")


def test_body_type():
    from astrololo.models.chart import BodyPosition
    p = BodyPosition(name="sun", name_vi="Mặt Trời", longitude=100, sign="cancer",
                     sign_name_vi="Cự Giải", position_in_sign=10, speed=1.0)
    assert p.body_type == "planet"
    n = BodyPosition(body_type="node", name="north_node", name_vi="La Hầu",
                     longitude=44.1, sign="taurus", sign_name_vi="Kim Ngưu",
                     position_in_sign=14.1)
    assert n.body_type == "node"
    a = BodyPosition(body_type="angle", name="ascendant", name_vi="Cung Mọc",
                     longitude=11.35, sign="aries", sign_name_vi="Bạch Dương",
                     position_in_sign=11.35)
    assert a.body_type == "angle"
    print("[PASS] BodyType: planet/node/angle all correct")


def test_interpretation():
    subject = AstrologicalSubject(
        name="Test Subject",
        year=1990, month=6, day=15,
        hour=14, minute=30,
        latitude=21.0285, longitude=105.8542,
        timezone_str="Asia/Ho_Chi_Minh",
    )

    chart = create_natal_chart(subject, lang="vi")

    assert chart.subject_name == "Test Subject"
    assert len(chart.planets) > 0, "No bodies calculated"
    assert chart.ascendant_sign != "", "No ascendant calculated"
    assert chart.interpretation is not None, "No interpretation generated"

    # Verify body_type distribution
    planets = [b for b in chart.planets if b.body_type == "planet"]
    nodes = [b for b in chart.planets if b.body_type == "node"]
    angles = [b for b in chart.planets if b.body_type == "angle"]
    assert len(planets) == 16, f"Expected 16 planets (10 Classical + 6 additional), got {len(planets)}"
    assert len(nodes) == 2, f"Expected 2 nodes, got {len(nodes)}"
    assert len(angles) == 4, f"Expected 4 angles, got {len(angles)}"
    assert len(chart.planets) == 22, f"Expected 22 total bodies, got {len(chart.planets)}"

    # Verify validation passed
    assert chart.validation["passed"], f"Validation failed: {chart.validation['errors']}"

    print(f"[PASS] Chart calculated for {chart.subject_name}")
    print(f"  Bodies: {len(chart.planets)} (16 planets + 2 nodes + 4 angles)")
    print(f"  Aspects: {len(chart.aspects)}")
    print(f"  Ascendant: {chart.ascendant_sign}")
    print(f"  MC: {chart.mc_sign}")
    print(f"  Daytime: {chart.is_daytime}")
    print(f"  Moon Phase: {chart.moon_phase}")
    print("  Validation: PASSED")

    if chart.element_distribution:
        ed = chart.element_distribution
        print(f"  Elements: Fire={ed.fire} Earth={ed.earth} Air={ed.air} Water={ed.water}")
        print(f"  Dominant: {ed.dominant}")


def test_interpretation_text():
    subject = AstrologicalSubject(
        name="John Doe",
        year=1990, month=6, day=15,
        hour=14, minute=30,
        latitude=21.0285, longitude=105.8542,
        timezone_str="Asia/Ho_Chi_Minh",
    )

    chart = create_natal_chart(subject, lang="vi")

    interp = chart.interpretation
    assert interp is not None

    print("\n=== INTERPRETATION RESULT ===")
    print(f"Subject: {interp.get('chart_summary', {}).get('name', 'N/A')}")
    print(f"Ascendant: {interp.get('chart_summary', {}).get('ascendant_sign', 'N/A')}")

    sections = interp.get("sections", [])
    print(f"\nSections: {len(sections)}")
    for section in sections:
        cat = section.get("category", "?")
        title = section.get("title", "?")
        items = section.get("items", [])
        if items:
            first_item = items[0]
            print(f"\n[{cat}] {title}")
            print(f"  ├─ {first_item.get('title', '?')}")
            print(f"  └─ {first_item.get('text', '')[:100]}...")

    print("\n" + "=" * 60)
    print("OVERALL INTERPRETATION:")
    print(interp.get("overall_interpretation", "N/A"))


def test_aspect_calculator():
    from astrololo.models.chart import BodyPosition
    calc = AspectCalculator()

    p1 = BodyPosition(name="sun", name_vi="Mặt Trời", longitude=100, sign="cancer",
                      sign_name_vi="Cự Giải", position_in_sign=10, speed=1.0)
    p2 = BodyPosition(name="moon", name_vi="Mặt Trăng", longitude=190, sign="libra",
                      sign_name_vi="Thiên Bình", position_in_sign=10, speed=13.0)
    p3 = BodyPosition(name="mars", name_vi="Sao Hỏa", longitude=280, sign="capricorn",
                      sign_name_vi="Ma Kết", position_in_sign=10, speed=0.5)

    aspects = calc.calculate([p1, p2, p3])
    print(f"\n[Aspect Test] 3 planets: {len(aspects)} aspects found")
    for a in aspects:
        print(f"  {a.planet1} - {a.planet2}: {a.aspect_type} (angle={a.angle}°, orb={a.orb}°)")

    # Test with angle body (speed=0 should not crash)
    p4 = BodyPosition(body_type="angle", name="ascendant", name_vi="Cung Mọc",
                      longitude=11.35, sign="aries", sign_name_vi="Bạch Dương",
                      position_in_sign=11.35, speed=0.0)
    aspects2 = calc.calculate([p1, p4])
    print(f"  Angle aspect test: {len(aspects2)} aspects (should not crash with speed=0)")


def test_scoring():
    subject = AstrologicalSubject(
        name="Score Test",
        year=1990, month=6, day=15,
        hour=14, minute=30,
        latitude=21.0285, longitude=105.8542,
        timezone_str="Asia/Ho_Chi_Minh",
    )
    chart = create_natal_chart(subject)
    scorer = ChartScorer(chart)
    result = scorer.score_chart()

    print(f"\n[Scoring Test] Total: {result['total']}")
    print(f"  Strength: {result['strength']}")
    print(f"  Pattern Score: {result['pattern_score']}")
    print(f"  Element Score: {result['element_score']}")
    print(f"  Dispositor Score: {result['dispositor_score']}")

    rankings = scorer.get_planet_rankings()
    for r in rankings[:3]:
        print(f"  {r['planet']}: {r['total']} ({r['label']})")


if __name__ == "__main__":
    print("=" * 60)
    print("ASTROLOLO INTERPRETATION ENGINE TEST")
    print("=" * 60)

    test_coordinates()
    test_body_type()
    test_constants()
    test_dignity()
    test_aspect_calculator()
    print()
    test_interpretation()
    print()
    test_scoring()
    print()
    test_interpretation_text()

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED!")
    print("=" * 60)
