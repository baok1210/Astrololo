"""Unit tests for individual interpretation rules and template loader."""
import sys
import os
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from astrololo.models.subject import AstrologicalSubject
from astrololo.analysis.natal import create_natal_chart
from astrololo.interpretation.chart_synthesis import (
    enrich_aspect_with_chart,
    make_combination_synthesis,
    is_placeholder_combination,
)
from astrololo.interpretation.template_loader import (
    get_planet_in_sign, get_aspect, get_house_cusp, get_combination,
    get_dignity_text, get_element_text, get_quality_text,
    _make_fallback_planet_in_sign, _make_fallback_planet_in_sign_en,
    _make_fallback_planet_in_house, _make_fallback_planet_in_house_en,
    _make_fallback_aspect,
)
from astrololo.interpretation.rules.ascendant_rule import AscendantSignRule
from astrololo.interpretation.rules.mc_rule import MCSignRule
from astrololo.interpretation.rules.pof_rule import PartOfFortuneRule
from astrololo.interpretation.rules.planet_in_sign_rule import PlanetInSignRule
from astrololo.interpretation.rules.planet_in_house_rule import PlanetInHouseRule
from astrololo.interpretation.rules.aspect_rules import AspectRule
from astrololo.interpretation.rules.dignity_rules import DignityRule
from astrololo.interpretation.rules.retrograde_rule import RetrogradeRule
from astrololo.interpretation.rules.moon_phase_rule import MoonPhaseRule
from astrololo.interpretation.rules.hemisphere_rule import HemisphereRule
from astrololo.interpretation.rules.house_ruler_rule import HouseRulerRule
from astrololo.interpretation.rules.declination_rule import DeclinationRule
from astrololo.interpretation.rules.house_cusp_rule import HouseCuspRule
from astrololo.interpretation.rules.house_placement_rule import HousePlacementRule
from astrololo.interpretation.rules.element_rules import ElementRule
from astrololo.interpretation.rules.quality_rules import QualityRule
from astrololo.interpretation.rules.dispositor_rules import DispositorRule
from astrololo.interpretation.rules.pattern_rules import PatternRule
from astrololo.interpretation.rules.combination_rules import CombinationRule
from astrololo.interpretation.rules.synthesis_rules import SynthesisRule
from astrololo.interpretation.rules.midpoint_rule import MidpointRule
from astrololo.models.chart import ChartData


def _make_chart(lang="vi"):
    subject = AstrologicalSubject(
        name="Test Subject", year=1990, month=6, day=15,
        hour=14, minute=30, latitude=21.0285, longitude=105.8542,
        timezone_str="Asia/Ho_Chi_Minh",
    )
    return create_natal_chart(subject, lang=lang)


def _r(result, lang="vi"):
    """Extract title/text from a RuleResult or list."""
    if result is None:
        return None, None
    if isinstance(result, list):
        return result, None
    title = result.title_vi if lang == "vi" else result.title_en
    text = result.text_vi if lang == "vi" else result.text_en
    return title, text


# ─── Template Loader Tests ───────────────────────────────────────────────────

class TestTemplateLoader:
    def test_get_planet_in_sign_real_content(self):
        entry = get_planet_in_sign("sun", "aries")
        assert entry is not None
        assert "title" in entry
        assert "short" in entry
        assert "detailed" in entry

    def test_get_planet_in_sign_fallback_vi(self):
        entry = get_planet_in_sign("lilith", "virgo", "vi")
        assert entry is not None
        assert "title" in entry

    def test_get_planet_in_sign_fallback_en(self):
        entry = get_planet_in_sign("lilith", "virgo", "en")
        assert entry is not None
        assert "title" in entry

    def test_get_planet_in_sign_all_planets_vi(self):
        for pk in ("sun", "moon", "venus", "jupiter", "chiron", "lilith", "north_node", "south_node"):
            entry = get_planet_in_sign(pk, "aries", "vi")
            assert entry is not None, f"Missing VI entry for {pk} in aries"
            assert entry.get("title"), f"No title for {pk} in aries"
            assert entry.get("detailed"), f"No detailed text for {pk} in aries"

    def test_get_aspect_real_content(self):
        entry = get_aspect("mars", "jupiter", "conjunction")
        assert entry is not None
        assert "title" in entry
        assert "detailed" in entry

    def test_get_aspect_fallback(self):
        entry = get_aspect("mercury", "sun", "semisextile")
        assert entry is not None
        assert "title" in entry
        assert "detailed" in entry

    def test_get_aspect_en(self):
        entry = get_aspect("mars", "venus", "trine", "en")
        assert entry is not None
        assert entry.get("detailed"), "EN aspect missing detailed text"

    def test_get_dignity_text_all_types(self):
        for dign in ("rulership", "exaltation", "detriment", "fall"):
            text = get_dignity_text(dign, "vi", "sun", "leo")
            assert text is not None, f"Missing dignity text for {dign}"

    def test_get_dignity_text_en(self):
        text = get_dignity_text("rulership", "en", "sun", "leo")
        assert text is not None
        assert "Sun" in text or "rulership" in text.lower()

    def test_get_combination(self):
        entry = get_combination("sun", "leo", 1)
        assert entry is not None
        assert "title" in entry
        assert len(entry.get("text", "")) > 80

    def test_get_combination_synthesis_with_chart(self):
        chart = _make_chart()
        entry = get_combination("sun", "leo", 1, chart=chart)
        assert entry is not None
        assert "Tổng hợp" in entry.get("text", "")

    def test_combination_not_placeholder(self):
        chart = _make_chart()
        rule = CombinationRule()
        results = rule.interpret(chart, "vi")
        assert results is not None
        assert len(results) > 0
        deep = [r for r in results if "Tổng hợp" in r.text_vi]
        assert len(deep) > 0, "Combination texts should include synthesis paragraphs"

    def test_aspect_chart_context(self):
        chart = _make_chart()
        rule = AspectRule()
        results = rule.interpret(chart, "vi")
        assert results is not None
        assert any("Trong lá số của bạn" in r.text_vi for r in results)

    def test_aspect_chart_context_en(self):
        chart = _make_chart()
        rule = AspectRule()
        results = rule.interpret(chart, "en")
        assert results is not None
        assert any("In your chart" in r.text_en for r in results)

    def test_is_placeholder_combination(self):
        assert is_placeholder_combination({"text": "sự kết hợp đặc biệt mang ý nghĩa quan trọng"})
        assert not is_placeholder_combination({"text": "Mars in Aries in the first house brings bold initiative."})

    def test_get_house_cusp(self):
        entry = get_house_cusp("aries", 1)
        if entry is not None:
            assert "title" in entry

    def test_element_text_not_empty(self):
        for el in ("fire", "earth", "air", "water"):
            text = get_element_text(el, "vi")
            if text is not None:
                assert len(text) > 0

    def test_quality_text_not_empty(self):
        for q in ("cardinal", "fixed", "mutable"):
            text = get_quality_text(q, "vi")
            if text is not None:
                assert len(text) > 0


# ─── Rule Tests ──────────────────────────────────────────────────────────────

class TestAscendantSignRule:
    def test_returns_content(self):
        chart = _make_chart()
        rule = AscendantSignRule()
        result = rule.interpret(chart, "vi")
        assert result is not None
        assert result.title_vi
        assert result.text_vi

    def test_returns_content_en(self):
        chart = _make_chart()
        rule = AscendantSignRule()
        result = rule.interpret(chart, "en")
        assert result is not None
        assert result.text_en or result.title_en

    def test_no_chart_match(self):
        rule = AscendantSignRule()
        empty = ChartData(ascendant_sign="")
        assert rule.matches(empty) is False

    def test_match_with_ascendant(self):
        chart = _make_chart()
        rule = AscendantSignRule()
        assert rule.matches(chart) is True


class TestMCSignRule:
    def test_returns_content(self):
        chart = _make_chart()
        rule = MCSignRule()
        result = rule.interpret(chart, "vi")
        assert result is not None
        assert result.text_vi

    def test_returns_content_en(self):
        chart = _make_chart()
        rule = MCSignRule()
        result = rule.interpret(chart, "en")
        assert result is not None
        assert result.text_en or result.title_en


class TestPartOfFortuneRule:
    def test_returns_content(self):
        chart = _make_chart()
        rule = PartOfFortuneRule()
        result = rule.interpret(chart, "vi")
        assert result is not None
        assert result.text_vi

    def test_returns_content_en(self):
        chart = _make_chart()
        rule = PartOfFortuneRule()
        result = rule.interpret(chart, "en")
        assert result is not None
        assert result.text_en or result.title_en


class TestPlanetInSignRule:
    def test_returns_all_bodies(self):
        chart = _make_chart()
        rule = PlanetInSignRule()
        results = rule.interpret(chart, "vi")
        assert results is not None
        assert isinstance(results, list)
        planets_with_houses = sum(1 for p in chart.planets if p.house > 0)
        assert len(results) >= planets_with_houses
        for r in results:
            assert r.text_vi

    def test_en_returns_all(self):
        chart = _make_chart()
        rule = PlanetInSignRule()
        results = rule.interpret(chart, "en")
        assert results is not None
        assert len(results) > 0


class TestPlanetInHouseRule:
    def test_returns_all_bodies(self):
        chart = _make_chart()
        rule = PlanetInHouseRule()
        results = rule.interpret(chart, "vi")
        assert results is not None
        assert isinstance(results, list)
        planets_with_houses = sum(1 for p in chart.planets if p.house > 0)
        assert len(results) >= planets_with_houses
        for r in results:
            assert r.text_vi

    def test_en_returns_all(self):
        chart = _make_chart()
        rule = PlanetInHouseRule()
        results = rule.interpret(chart, "en")
        assert results is not None
        assert len(results) > 0


class TestAspectRule:
    def test_returns_aspects(self):
        chart = _make_chart()
        rule = AspectRule()
        results = rule.interpret(chart, "vi")
        assert results is not None
        assert isinstance(results, list)
        assert len(results) == len(chart.aspects)
        for r in results:
            assert r.text_vi

    def test_en_works(self):
        chart = _make_chart()
        rule = AspectRule()
        results = rule.interpret(chart, "en")
        assert results is not None
        assert len(results) > 0


class TestDignityRule:
    def test_returns_dignities(self):
        chart = _make_chart()
        rule = DignityRule()
        results = rule.interpret(chart, "vi")
        assert results is not None
        assert isinstance(results, list)
        assert len(results) > 0
        for r in results:
            assert r.text_vi

    def test_en_works(self):
        chart = _make_chart()
        rule = DignityRule()
        results = rule.interpret(chart, "en")
        assert results is not None
        assert len(results) > 0


class TestRetrogradeRule:
    def test_runs_without_error(self):
        chart = _make_chart()
        rule = RetrogradeRule()
        result = rule.interpret(chart, "vi")
        if rule.matches(chart):
            assert result is not None
            assert isinstance(result, list)

    def test_empty_chart(self):
        rule = RetrogradeRule()
        empty = ChartData()
        assert rule.matches(empty) is False


class TestMoonPhaseRule:
    def test_returns_moon_phase(self):
        chart = _make_chart()
        rule = MoonPhaseRule()
        result = rule.interpret(chart, "vi")
        assert result is not None
        assert result.text_vi

    def test_en_works(self):
        chart = _make_chart()
        rule = MoonPhaseRule()
        result = rule.interpret(chart, "en")
        assert result is not None
        assert result.text_en or result.title_en


class TestMidpointRule:
    def test_returns_content(self):
        chart = _make_chart()
        rule = MidpointRule()
        result = rule.interpret(chart, "vi")
        if result is not None:
            if isinstance(result, list):
                assert len(result) > 0

    def test_en_works(self):
        chart = _make_chart()
        rule = MidpointRule()
        result = rule.interpret(chart, "en")
        if result is not None:
            if isinstance(result, list):
                assert len(result) > 0


class TestHemisphereRule:
    def test_returns_content(self):
        chart = _make_chart()
        rule = HemisphereRule()
        result = rule.interpret(chart, "vi")
        assert result is not None
        assert result.text_vi

    def test_en_works(self):
        chart = _make_chart()
        rule = HemisphereRule()
        result = rule.interpret(chart, "en")
        assert result is not None


class TestHouseRulerRule:
    def test_returns_content(self):
        chart = _make_chart()
        rule = HouseRulerRule()
        result = rule.interpret(chart, "vi")
        assert result is not None
        assert isinstance(result, list)
        assert len(result) > 0
        assert result[0].text_vi

    def test_en_works(self):
        chart = _make_chart()
        rule = HouseRulerRule()
        result = rule.interpret(chart, "en")
        assert result is not None
        assert len(result) > 0


class TestDeclinationRule:
    def test_returns_content(self):
        chart = _make_chart()
        rule = DeclinationRule()
        result = rule.interpret(chart, "vi")
        if result is not None:
            assert isinstance(result, list)
            assert len(result) > 0

    def test_en_works(self):
        chart = _make_chart()
        rule = DeclinationRule()
        result = rule.interpret(chart, "en")
        if result is not None:
            assert len(result) > 0


class TestHouseCuspRule:
    def test_returns_all_houses(self):
        chart = _make_chart()
        rule = HouseCuspRule()
        results = rule.interpret(chart, "vi")
        assert results is not None
        assert isinstance(results, list)
        assert len(results) == 12
        for r in results:
            assert r.text_vi

    def test_en_works(self):
        chart = _make_chart()
        rule = HouseCuspRule()
        results = rule.interpret(chart, "en")
        assert results is not None
        assert len(results) == 12


class TestHousePlacementRule:
    def test_returns_content(self):
        chart = _make_chart()
        rule = HousePlacementRule()
        result = rule.interpret(chart, "vi")
        assert result is not None
        assert isinstance(result, list)
        assert len(result) > 0

    def test_en_works(self):
        chart = _make_chart()
        rule = HousePlacementRule()
        result = rule.interpret(chart, "en")
        assert result is not None


class TestElementRule:
    def test_returns_content(self):
        chart = _make_chart()
        rule = ElementRule()
        result = rule.interpret(chart, "vi")
        assert result is not None
        assert result.text_vi

    def test_en_works(self):
        chart = _make_chart()
        rule = ElementRule()
        result = rule.interpret(chart, "en")
        assert result is not None


class TestQualityRule:
    def test_returns_content(self):
        chart = _make_chart()
        rule = QualityRule()
        result = rule.interpret(chart, "vi")
        assert result is not None
        assert result.text_vi

    def test_en_works(self):
        chart = _make_chart()
        rule = QualityRule()
        result = rule.interpret(chart, "en")
        assert result is not None


class TestDispositorRule:
    def test_returns_content(self):
        chart = _make_chart()
        rule = DispositorRule()
        result = rule.interpret(chart, "vi")
        assert result is not None
        assert result.text_vi

    def test_en_works(self):
        chart = _make_chart()
        rule = DispositorRule()
        result = rule.interpret(chart, "en")
        assert result is not None


class TestPatternRule:
    def test_returns_patterns(self):
        chart = _make_chart()
        rule = PatternRule()
        result = rule.interpret(chart, "vi")
        if result is not None:
            if isinstance(result, list):
                assert len(result) > 0
                assert result[0].text_vi


class TestCombinationRule:
    def test_returns_content(self):
        chart = _make_chart()
        rule = CombinationRule()
        results = rule.interpret(chart, "vi")
        if results is not None:
            assert isinstance(results, list)
            for r in results:
                assert r.text_vi

    def test_en_works(self):
        chart = _make_chart()
        rule = CombinationRule()
        results = rule.interpret(chart, "en")
        if results is not None:
            assert isinstance(results, list)


class TestSynthesisRule:
    def test_returns_content(self):
        chart = _make_chart()
        rule = SynthesisRule()
        result = rule.interpret(chart, "vi")
        assert result is not None
        assert isinstance(result, list)
        assert len(result) > 0
        assert result[0].text_vi

    def test_en_works(self):
        chart = _make_chart()
        rule = SynthesisRule()
        result = rule.interpret(chart, "en")
        assert result is not None
        assert len(result) > 0


# ─── Engine Integration Test ─────────────────────────────────────────────────

class TestEngineIntegration:
    def test_all_categories_present(self):
        chart = _make_chart()
        from astrololo.interpretation.engine import InterpretationEngine
        engine = InterpretationEngine(lang="vi")
        result = engine.interpret(chart)
        sections = result.sections
        categories = {s.get("category") for s in sections}
        required = {"synthesis", "planet_in_sign", "planet_in_house", "aspect", "house_cusp",
                    "element", "quality", "dignity", "dispositor", "house_placement",
                    "pattern", "house_distribution"}
        missing = required - categories
        assert len(missing) == 0, f"Missing required sections: {missing}"
        # Conditional sections that may or may not appear
        assert len(categories) >= len(required)

    def test_en_sections_have_content(self):
        chart = _make_chart(lang="en")
        from astrololo.interpretation.engine import InterpretationEngine
        engine = InterpretationEngine(lang="en")
        result = engine.interpret(chart)
        sections = result.sections
        assert len(sections) > 0
        for s in sections:
            items = s.get("items", [])
            for item in items:
                text = item.get("text", "") or ""
                if not text:
                    print(f"  [WARN] Empty EN text in {s.get('category')}: {item.get('title', '?')}")

    def test_overall_interpretation_present(self):
        chart = _make_chart()
        from astrololo.interpretation.engine import InterpretationEngine
        engine = InterpretationEngine(lang="vi")
        result = engine.interpret(chart)
        assert result.overall_interpretation


# ─── Fallback Generator Tests ────────────────────────────────────────────────

class TestFallbackGenerators:
    def test_planet_in_sign_fallback_vi(self):
        entry = _make_fallback_planet_in_sign("sun", "leo")
        assert "title" in entry
        assert "short" in entry
        assert "detailed" in entry

    def test_planet_in_sign_fallback_en(self):
        entry = _make_fallback_planet_in_sign_en("sun", "leo")
        assert "title" in entry
        assert "short" in entry
        assert "detailed" in entry

    def test_planet_in_house_fallback_vi(self):
        entry = _make_fallback_planet_in_house("sun", 1)
        assert "title" in entry
        assert "short" in entry
        assert "detailed" in entry

    def test_planet_in_house_fallback_en(self):
        entry = _make_fallback_planet_in_house_en("sun", 1)
        assert "title" in entry
        assert "short" in entry
        assert "detailed" in entry

    def test_aspect_fallback(self):
        entry = _make_fallback_aspect("sun", "moon", "conjunction")
        assert "title" in entry
        assert "short" in entry
        assert "detailed" in entry

    def test_fallback_contains_planet_names(self):
        entry = _make_fallback_aspect("sun", "moon", "conjunction")
        assert "Mặt Trời" in entry["detailed"]
        assert "Mặt Trăng" in entry["detailed"]
