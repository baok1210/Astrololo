"""Unit tests for keyword enrichment."""
import sys
import os

sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from astrololo.interpretation.keywords import (
    SIGN_KEYWORDS_VI, HOUSE_KEYWORDS_VI, SIGN_NAME_VI,
    HOUSE_NAME_VI, SIGN_ELEMENT_VI, SIGN_QUALITY_VI,
    PLANET_FUNCTIONS_VI, get_sign_keywords, get_house_keywords,
    get_planet_function, get_sign_description, get_sign_short_description,
    get_sign_potential_issues, get_house_description, get_house_title,
)

from astrololo.interpretation.template_loader import (
    get_planet_in_sign, get_planet_in_house, get_dignity_text,
    _enrich_sign_entry, _enrich_house_entry, _enrich_dignity_text,
    clear_cache,
)


def test_keywords_data_integrity():
    assert len(SIGN_KEYWORDS_VI) == 12
    assert len(HOUSE_KEYWORDS_VI) == 12
    assert len(PLANET_FUNCTIONS_VI) == 16
    assert len(SIGN_NAME_VI) == 12
    assert len(HOUSE_NAME_VI) == 12
    assert len(SIGN_ELEMENT_VI) == 12
    assert len(SIGN_QUALITY_VI) == 12
    print("[PASS] Keyword data structures complete")


def test_sign_keyword_structure():
    for sign, data in SIGN_KEYWORDS_VI.items():
        assert "positive" in data
        assert "negative" in data
        assert "core" in data
        assert "short_description" in data
        assert data["positive"]
        assert data["negative"]
        assert data["core"]
        assert sign in SIGN_ELEMENT_VI
        assert sign in SIGN_QUALITY_VI
        assert sign in SIGN_NAME_VI
    print("[PASS] All 12 signs have complete keyword structure")


def test_house_keyword_structure():
    for num, data in HOUSE_KEYWORDS_VI.items():
        assert "keywords" in data
        assert "description" in data
        assert "title" in data
        assert data["keywords"]
        assert data["description"]
        assert num in HOUSE_NAME_VI
    print("[PASS] All 12 houses have complete keyword structure")


def test_planet_function_structure():
    for planet, func in PLANET_FUNCTIONS_VI.items():
        assert func
        assert len(func) > 50
    print("[PASS] All 10 planets have meaningful function descriptions")


def test_get_sign_keywords():
    aries = get_sign_keywords("aries")
    assert aries["positive"][0] == "bộc trực, thẳng thắn"
    assert "ích kỷ" in " ".join(aries["negative"])
    assert get_sign_keywords("nonexistent") == {}
    print("[PASS] get_sign_keywords works correctly")


def test_get_house_keywords():
    h1 = get_house_keywords(1)
    assert "tự hình dung về mình" in h1["keywords"]
    assert get_house_keywords(99) == {}
    print("[PASS] get_house_keywords works correctly")


def test_get_planet_function():
    sun = get_planet_function("sun")
    assert "Mặt Trời" in sun
    assert "sức sống" in sun
    assert get_planet_function("nonexistent") == ""
    print("[PASS] get_planet_function works correctly")


def test_get_sign_description():
    desc = get_sign_description("aries")
    assert "Tích cực" in desc
    assert "Thách thức" in desc
    print("[PASS] get_sign_description works correctly")


def test_get_sign_short_description():
    desc = get_sign_short_description("aries")
    assert "Bộc trực" in desc
    assert get_sign_short_description("nonexistent") == ""
    print("[PASS] get_sign_short_description works correctly")


def test_get_sign_potential_issues():
    issues = get_sign_potential_issues("aries")
    assert "Nóng nảy" in issues
    assert get_sign_potential_issues("nonexistent") == ""
    print("[PASS] get_sign_potential_issues works correctly")


def test_get_house_description():
    desc = get_house_description(1)
    assert ("cái tôi" or "bản thân" or "bản sắc") in desc.lower()
    assert get_house_description(99) == ""
    print("[PASS] get_house_description works correctly")


def test_get_house_title():
    title = get_house_title(1)
    assert "Bản Thân" in title
    assert get_house_title(99) == "Nhà 99"
    print("[PASS] get_house_title works correctly")


def test_planet_in_sign_enrichment():
    clear_cache()
    entry = get_planet_in_sign("sun", "aries")
    assert entry is not None
    detailed = entry.get("detailed", "")
    assert "Tích cực:" in detailed
    assert "Khuynh hướng:" in detailed
    assert "Lưu ý:" in detailed
    print("[PASS] planet_in_sign enrichment adds sign keywords")


def test_planet_in_sign_enrichment_virgo():
    clear_cache()
    entry = get_planet_in_sign("mercury", "virgo")
    assert entry is not None
    detailed = entry.get("detailed", "")
    assert "Tích cực:" in detailed
    print("[PASS] virgo keyword enrichment works")


def test_planet_in_house_enrichment():
    clear_cache()
    entry = get_planet_in_house("moon", 4)
    assert entry is not None
    detailed = entry.get("detailed", "")
    assert "Từ khoá:" in detailed
    assert "Là nhà của" in detailed or "gia" in detailed.lower()
    print("[PASS] planet_in_house enrichment adds house keywords")


def test_planet_in_house_function():
    clear_cache()
    entry = get_planet_in_house("mars", 1)
    assert entry is not None
    detailed = entry.get("detailed", "")
    has_function = "Sao Hỏa" in detailed or "hành động" in detailed.lower()
    assert has_function
    print("[PASS] planet_in_house includes planet function")


def test_dignity_enrichment_exaltation():
    text = get_dignity_text("exaltation", "vi", "sun", "aries")
    assert text is not None
    assert "Bạn sở hữu các đặc điểm" in text
    print("[PASS] exaltation dignity enrichment works")


def test_dignity_enrichment_rulership():
    clear_cache()
    text = get_dignity_text("rulership", "vi", "mars", "scorpio")
    assert text is not None
    assert "Đây là cung" in text
    print("[PASS] rulership dignity enrichment works")


def test_dignity_enrichment_fall():
    clear_cache()
    text = get_dignity_text("fall", "vi", "jupiter", "taurus")
    assert text is not None
    assert "Bạn cần lưu ý các thách thức" in text
    print("[PASS] fall dignity enrichment works")


def test_dignity_enrichment_detriment():
    clear_cache()
    text = get_dignity_text("detriment", "vi", "venus", "scorpio")
    assert text is not None
    assert "Bạn cần lưu ý các" in text
    print("[PASS] detriment dignity enrichment works")


def test_dignity_neutral():
    clear_cache()
    text = get_dignity_text("neutral", "vi")
    assert text is not None
    assert "trung tính" in text
    print("[PASS] neutral dignity works without enrichment")


def test_enrich_sign_entry_direct():
    entry = {"detailed": "Original text.", "title": "Test"}
    enriched = _enrich_sign_entry(entry, "aries")
    assert "Original text" in enriched["detailed"]
    assert "phẩm chất nổi bật" in enriched["detailed"]
    assert enriched["title"] == "Test"
    print("[PASS] _enrich_sign_entry preserves original + adds flowing narrative")


def test_enrich_house_entry_direct():
    entry = {"detailed": "Original text.", "title": "Test", "short": "Short"}
    enriched = _enrich_house_entry(entry, "sun", 9)
    assert "Original text" in enriched["detailed"]
    assert "Từ khoá:" in enriched["detailed"]
    print("[PASS] _enrich_house_entry preserves original + adds keywords")


def test_enrich_dignity_text_direct():
    text = "Original dignity text with {planet} and {sign}."
    enriched = _enrich_dignity_text(text, "sun", "aries", "exaltation")
    assert enriched.startswith("Original dignity text")
    assert "Bạn sở hữu các đặc điểm" in enriched
    print("[PASS] _enrich_dignity_text works directly")


def test_element_quality_counts():
    elements = list(SIGN_ELEMENT_VI.values())
    assert elements.count("lửa") == 3
    assert elements.count("đất") == 3
    assert elements.count("khí") == 3
    assert elements.count("nước") == 3
    qualities = list(SIGN_QUALITY_VI.values())
    assert qualities.count("thống lĩnh") == 4
    assert qualities.count("cố định") == 4
    assert qualities.count("biến đổi") == 4
    print("[PASS] Element and quality counts correct (3 each, 4 each)")


def test_keyword_minimum_lengths():
    for sign, data in SIGN_KEYWORDS_VI.items():
        assert len(data["positive"]) >= 5
        assert len(data["negative"]) >= 3
        assert len(data["core"]) >= 3
    for num, data in HOUSE_KEYWORDS_VI.items():
        assert len(data["keywords"]) >= 5
    print("[PASS] Minimum keyword count requirements met")


if __name__ == "__main__":
    tests = [
        test_keywords_data_integrity,
        test_sign_keyword_structure,
        test_house_keyword_structure,
        test_planet_function_structure,
        test_get_sign_keywords,
        test_get_house_keywords,
        test_get_planet_function,
        test_get_sign_description,
        test_get_sign_short_description,
        test_get_sign_potential_issues,
        test_get_house_description,
        test_get_house_title,
        test_planet_in_sign_enrichment,
        test_planet_in_sign_enrichment_virgo,
        test_planet_in_house_enrichment,
        test_planet_in_house_function,
        test_dignity_enrichment_exaltation,
        test_dignity_enrichment_rulership,
        test_dignity_enrichment_fall,
        test_dignity_enrichment_detriment,
        test_dignity_neutral,
        test_enrich_sign_entry_direct,
        test_enrich_house_entry_direct,
        test_enrich_dignity_text_direct,
        test_element_quality_counts,
        test_keyword_minimum_lengths,
    ]

    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"[FAIL] {t.__name__}: {e}")
            failed += 1

    print(f"\n{'='*50}")
    print(f"  RESULTS: {passed} passed, {failed} failed, {len(tests)} total")
    print(f"{'='*50}")
