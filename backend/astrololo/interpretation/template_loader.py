import os
import yaml
from typing import Optional, Dict, Any
from astrololo.core.constants import PLANETS, SIGNS, HOUSES, ASPECTS, get_dignity_label
from astrololo.interpretation.keywords import (
    get_sign_short_description,
    get_sign_keywords,
    get_house_keywords,
    get_planet_function,
    SIGN_KEYWORDS_VI,
    SIGN_NAME_VI,
    SIGN_ELEMENT_VI,
    SIGN_QUALITY_VI,
)
from astrololo.interpretation.knowledge_base import (
    enrich_planet_in_sign,
    enrich_planet_in_house,
    is_kb_available,
)
from astrololo.interpretation.knowledge_retriever import (
    retrieve_planet_in_sign as _kb_retrieve_sign,
    retrieve_planet_in_house as _kb_retrieve_house,
    retrieve_aspect as _kb_retrieve_aspect,
    is_available as _kb_retriever_available,
)

_ESOTERIC_MODE = True


def set_esoteric_mode(enabled: bool) -> None:
    global _ESOTERIC_MODE
    _ESOTERIC_MODE = enabled


PLANET_REPRESENTS_VI = {
    "sun": "người mà ta ngưỡng mộ, hình mẫu ta muốn trở thành",
    "moon": "người mẹ lý tưởng, chỗ dựa, nơi chốn bình yên",
    "mercury": "anh chị em, người đương thời, nhà văn, nhà báo",
    "venus": "phụ nữ, người yêu, người đại diện cho cái đẹp",
    "mars": "phái mạnh, người báo thù",
    "jupiter": "quý nhân, người thầy, người đại diện cho công lý",
    "saturn": "nhà cầm quyền, người già dặn, người đại diện cho pháp luật",
    "uranus": "người hoạt động xã hội, kẻ lập dị",
    "neptune": "người sống bằng đam mê, người cuồng tín",
    "pluto": "kẻ nắm quyền lực ngầm, người đại diện cho xã hội đen",
}

_TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")

_cache: Dict[str, Any] = {}


def _enrich_dignity_text(
    text: str, planet: str, sign: str, dignity: str
) -> str:
    if dignity == "neutral":
        return text

    sign_keywords = get_sign_keywords(sign)

    extra_parts = []

    if dignity == "rulership":
        element = SIGN_KEYWORDS_VI.get(sign, {}).get("element", "")
        quality = SIGN_KEYWORDS_VI.get(sign, {}).get("mode", "")
        extra_parts.append(f"Đây là cung {element} {quality} - {SIGN_NAME_VI.get(sign, '')}, nơi {PLANET_REPRESENTS_VI.get(planet, '')} thể hiện trọn vẹn nhất.")

    elif dignity == "exaltation":
        pos_keywords = sign_keywords.get("positive", [])[:3]
        if pos_keywords:
            extra_parts.append(f"Bạn sở hữu các đặc điểm: {'; '.join(pos_keywords)}.")

    elif dignity == "triplicity":
        element = SIGN_KEYWORDS_VI.get(sign, {}).get("element", "")
        extra_parts.append(f"{planet} thuộc cùng nhóm nguyên tố {element} với cung {sign}, tạo sự đồng điệu tự nhiên.")

    elif dignity == "term":
        extra_parts.append(f"{planet} nằm trong khoảng giới hạn (bounds) của mình tại cung {sign}, giúp tập trung năng lượng.")

    elif dignity == "face":
        extra_parts.append(f"{planet} ở một thập phân (decan) của cung {sign} mà nó quản lý, hỗ trợ nhẹ cho vị trí chính.")

    elif dignity == "detriment":
        neg_keywords = sign_keywords.get("negative", [])[:2]
        if neg_keywords:
            extra_parts.append(f"Bạn cần lưu ý các hạn chế: {'; '.join(neg_keywords)}.")

    elif dignity == "fall":
        neg_keywords = sign_keywords.get("negative", [])[:2]
        if neg_keywords:
            extra_parts.append(f"Bạn cần lưu ý các thách thức: {'; '.join(neg_keywords)}.")

    func_text = get_planet_function(planet)
    if func_text:
        func_short = func_text.split(".")[0] + "."
        extra_parts.append(func_short)

    if extra_parts:
        return text + "\n\n" + "\n".join(f"  • {p}" for p in extra_parts)
    return text


def _load_yaml(lang: str, filename: str) -> dict:
    cache_key = f"{lang}/{filename}"
    if cache_key not in _cache:
        filepath = os.path.join(_TEMPLATES_DIR, lang, filename)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                _cache[cache_key] = yaml.safe_load(f) or {}
        else:
            _cache[cache_key] = {}
    return _cache[cache_key]


def _load_baked_yaml(filename: str) -> dict:
    """Baked EN templates generated from the crawled corpus (durable, no runtime dep)."""
    return _load_yaml("en", filename)


def _normalize_sign_entry(entry, planet, sign, lang):
    """Convert string entry to dict format with title/short/detailed.

    Falls back to generated title if dict entry has empty/missing title.
    """
    if isinstance(entry, dict):
        if entry.get("title"):
            return entry
        entry = dict(entry)
        p = PLANETS.get(planet)
        s = SIGNS.get(sign)
        p_name = p.name_en if p and lang == "en" else p.name_vi if p else planet
        s_name = s.name_en if s and lang == "en" else s.name_vi if s else sign
        entry["title"] = f"{p_name} in {s_name}" if lang == "en" else f"{p_name} ở {s_name}"
        return entry
    p = PLANETS.get(planet)
    s = SIGNS.get(sign)
    p_name = p.name_en if p and lang == "en" else p.name_vi if p else planet
    s_name = s.name_en if s and lang == "en" else s.name_vi if s else sign
    title = f"{p_name} in {s_name}" if lang == "en" else f"{p_name} ở {s_name}"
    return {"title": title, "short": entry[:100] if entry else "", "detailed": entry or ""}


def get_planet_in_sign(planet: str, sign: str, lang: str = "vi") -> Optional[Dict[str, Any]]:
    data = _load_yaml(lang, "planet_in_sign.yaml")
    planet_data = data.get(planet, {})
    entry = planet_data.get(sign)
    if entry:
        entry = _normalize_sign_entry(entry, planet, sign, lang)
        if lang == "vi":
            entry = _enrich_sign_entry(entry, sign)
            entry = _enrich_via_kb_or_fallback(planet, sign, entry)
        return entry
    if lang == "en":
        # 1) curated EN template already returned above
        # 2) baked corpus YAML (durable)
        baked = _load_baked_yaml("planet_in_sign_baked.yaml")
        bentry = (baked.get(planet, {}) or {}).get(sign)
        if bentry and isinstance(bentry, dict):
            bentry = dict(bentry)
            p = PLANETS.get(planet); s = SIGNS.get(sign)
            bentry.setdefault("title", f"{p.name_en if p else planet} in {s.name_en if s else sign}")
            bentry.setdefault("short", bentry.get("title", ""))
            return bentry
        # 3) live retriever over corpus
        kb = _kb_retrieve_sign(planet, sign) if _kb_retriever_available() else None
        if kb:
            p = PLANETS.get(planet); s = SIGNS.get(sign)
            p_name = p.name_en if p else planet
            s_name = s.name_en if s else sign
            dignity = get_dignity_label(planet, sign)
            tag = f" ({dignity})" if dignity != "neutral" else ""
            return {
                "title": f"{p_name} in {s_name}{tag}",
                "short": f"{p_name} in {s_name}",
                "detailed": kb,
                "strength": "See description",
                "weakness": "See description",
            }
        return _make_fallback_planet_in_sign_en(planet, sign)
    return _make_fallback_planet_in_sign(planet, sign)


def _enrich_via_kb_or_fallback(planet: str, sign: str, entry: Dict[str, Any]) -> Dict[str, Any]:
    if _ESOTERIC_MODE and is_kb_available():
        enriched = enrich_planet_in_sign(planet, sign, entry.get("detailed", ""))
        if enriched != entry.get("detailed"):
            entry = dict(entry)
            entry["detailed"] = enriched
    return entry


def _enrich_sign_entry(entry: Dict[str, Any], sign: str) -> Dict[str, Any]:
    sign_data = get_sign_keywords(sign)
    pos = sign_data.get("positive", [])
    neg = sign_data.get("negative", [])
    behavior = sign_data.get("behavior", sign_data.get("core", []))
    element_vi = SIGN_ELEMENT_VI.get(sign, "")
    quality_vi = SIGN_QUALITY_VI.get(sign, "")

    extra = []
    existing = entry.get("detailed", "").rstrip()

    if pos or behavior:
        flow_parts = []
        if pos:
            pos_text = "; ".join(pos[:4])
            flow_parts.append(f"ban tỏa ra những phẩm chất nổi bật: {pos_text}")
        if behavior:
            beh_text = "; ".join(beh[:3] for beh in behavior[:3])
            flow_parts.append(f"khuynh hướng tự nhiên: {beh_text}")
        if element_vi and quality_vi:
            flow_parts.append(f"thuộc nhóm {element_vi} {quality_vi}, định hình cách bạn thể hiện năng lượng này")
        if flow_parts:
            intro = "Ở cung này, " + ", ".join(flow_parts) + "."
            extra.append(intro)

    if neg:
        neg_text = "; ".join(neg[:3])
        extra.append(f"Thách thức cần lưu ý: {neg_text}. Nhận diện những điểm này giúp bạn phát triển và đạt được sự cân bằng.")

    if extra:
        enriched = existing + "\n\n" + "\n\n".join(extra)
        entry = dict(entry)
        entry["detailed"] = enriched
    return entry


def _make_fallback_planet_in_sign(planet: str, sign: str) -> Dict[str, Any]:
    p = PLANETS.get(planet)
    s = SIGNS.get(sign)
    p_name = p.name_vi if p else planet
    s_name = s.name_vi if s else sign
    dignity = get_dignity_label(planet, sign)
    tag = f" ({dignity})" if dignity != "neutral" else ""

    sign_data = get_sign_keywords(sign)
    pos = sign_data.get("positive", [])
    neg = sign_data.get("negative", [])
    behavior = sign_data.get("behavior", sign_data.get("core", []))
    short_desc = get_sign_short_description(sign)
    func_text = get_planet_function(planet)
    s_obj = SIGNS.get(sign)
    element_vi = SIGN_ELEMENT_VI.get(sign, "")
    quality_vi = SIGN_QUALITY_VI.get(sign, "")
    element_en = s_obj.element if s_obj else ""

    pos_sample = "; ".join(pos[:4]) if pos else ""
    neg_sample = "; ".join(neg[:3]) if neg else ""
    beh_sample = "; ".join(behavior[:3]) if behavior else ""

    detailed_parts = []

    # Paragraph 1: Opening — planet function + sign context
    if func_text:
        func_short = func_text[:200]
        opening = (
            f"{p_name} — {func_short} "
            f"Khi đặt trong {s_name} ({element_vi} {quality_vi}), "
            f"năng lượng này được thể hiện qua lăng kính của cung {s_name} "
            f"với những đặc tính {element_vi} {quality_vi} riêng có."
        )
    else:
        opening = (
            f"{p_name} ở {s_name}{tag}: "
            f"vị trí thuộc nhóm {element_vi} {quality_vi}, "
            f"mang đến cách thể hiện năng lượng riêng biệt cho {p_name}."
        )
    detailed_parts.append(opening)

    # Paragraph 2: Sign description + element context
    if short_desc:
        element_context = (
            f"Thuộc nguyên tố {element_vi} ({element_en}) và chất lượng {quality_vi}, "
            f"cung {s_name} mang tới cho bạn những đặc điểm: {short_desc}"
        )
        detailed_parts.append(element_context)

    # Paragraph 3: Positive expression + behavioral patterns
    if pos_sample or beh_sample:
        traits_parts = []
        if pos_sample:
            traits_parts.append(
                f"Những phẩm chất nổi bật của bạn bao gồm {pos_sample}. "
                f"Đây là những điểm mạnh giúp bạn phát huy tối đa năng lượng của {p_name}."
            )
        if beh_sample:
            traits_parts.append(
                f"Khuynh hướng tự nhiên: bạn thường {beh_sample}. "
                f"Điều này định hình cách bạn tiếp cận các lĩnh vực mà {p_name} đại diện."
            )
        detailed_parts.append("\n\n".join(traits_parts))

    # Paragraph 4: Challenges and growth
    if neg_sample:
        detailed_parts.append(
            f"Thách thức cần lưu ý: {neg_sample}. "
            f"Những khía cạnh này đòi hỏi bạn ý thức và phát triển để đạt được "
            f"sự cân bằng và trưởng thành trong cách {p_name} thể hiện qua cung {s_name}."
        )
    else:
        detailed_parts.append(
            f"Nhìn chung, {p_name} ở {s_name} mang đến sự kết hợp hài hòa, "
            f"cho phép bạn thể hiện năng lượng này một cách tự nhiên và hiệu quả."
        )

    detailed_text = "\n\n".join(detailed_parts)
    if _ESOTERIC_MODE and is_kb_available():
        detailed_text = enrich_planet_in_sign(planet, sign, detailed_text)

    return {
        "title": f"{p_name} ở {s_name}{tag}",
        "short": f"{p_name} ở {s_name}: {short_desc}" if short_desc else f"{p_name} ở {s_name}: vị trí mang tính khám phá.",
        "detailed": detailed_text,
        "strength": pos_sample or "Khám phá và phát triển",
        "weakness": neg_sample or "Cần thời gian để thấu hiểu",
    }


def _normalize_house_entry(entry, planet, house, lang):
    """Convert string entry to dict format with title/short/detailed.

    Falls back to generated title if dict entry has empty/missing title.
    """
    if isinstance(entry, dict):
        if entry.get("title"):
            return entry
        entry = dict(entry)
        p = PLANETS.get(planet)
        h = HOUSES.get(house)
        p_name = p.name_en if p and lang == "en" else p.name_vi if p else planet
        h_name = h.name_en if h and lang == "en" else h.name_vi if h else f"House {house}"
        entry["title"] = f"{p_name} in the {h_name}" if lang == "en" else f"{p_name} ở {h_name}"
        return entry
    p = PLANETS.get(planet)
    h = HOUSES.get(house)
    p_name = p.name_en if p and lang == "en" else p.name_vi if p else planet
    h_name = h.name_en if h and lang == "en" else h.name_vi if h else f"House {house}"
    title = f"{p_name} in the {h_name}" if lang == "en" else f"{p_name} ở {h_name}"
    return {"title": title, "short": entry[:100] if entry else "", "detailed": entry or ""}


def get_planet_in_house(planet: str, house: int, lang: str = "vi") -> Optional[Dict[str, Any]]:
    data = _load_yaml(lang, "planet_in_house.yaml")
    planet_data = data.get(planet, {})
    entry = planet_data.get(str(house))
    if entry:
        entry = _normalize_house_entry(entry, planet, house, lang)
        if lang == "vi":
            entry = _enrich_house_entry(entry, planet, house)
            entry = _enrich_house_via_kb(planet, house, entry)
        return entry
    if lang == "en":
        baked = _load_baked_yaml("planet_in_house_baked.yaml")
        bentry = (baked.get(planet, {}) or {}).get(str(house))
        if bentry and isinstance(bentry, dict):
            bentry = dict(bentry)
            p = PLANETS.get(planet); h = HOUSES.get(house)
            bentry.setdefault("title", f"{p.name_en if p else planet} in the {h.name_en if h else 'House ' + str(house)}")
            bentry.setdefault("short", bentry.get("title", ""))
            return bentry
        kb = _kb_retrieve_house(planet, house) if _kb_retriever_available() else None
        if kb:
            p = PLANETS.get(planet); h = HOUSES.get(house)
            p_name = p.name_en if p else planet
            h_name = h.name_en if h else f"House {house}"
            return {
                "title": f"{p_name} in the {h_name}",
                "short": f"{p_name} in the {h_name}",
                "detailed": kb,
                "strength": "See description",
                "weakness": "See description",
            }
        return _make_fallback_planet_in_house_en(planet, house)
    return _make_fallback_planet_in_house(planet, house)


def _enrich_house_entry(entry: Dict[str, Any], planet: str, house: int) -> Dict[str, Any]:
    house_data = get_house_keywords(house)
    kw_list = house_data.get("keywords", [])
    h_desc = house_data.get("description", "")
    kw_sample = "; ".join(kw_list[:5]) if kw_list else ""
    extra = []
    if h_desc:
        extra.append(h_desc)
    if kw_sample:
        extra.append(f"Từ khoá: {kw_sample}.")
    func_text = get_planet_function(planet)
    if func_text:
        extra.append(func_text.split(".")[0] + ".")
    existing = entry.get("detailed", "")
    if extra:
        enriched = existing + "\n\n" + "\n\n".join(extra)
        entry = dict(entry)
        entry["detailed"] = enriched
    return entry


def _enrich_house_via_kb(planet: str, house: int, entry: Dict[str, Any]) -> Dict[str, Any]:
    if _ESOTERIC_MODE and is_kb_available():
        enriched = enrich_planet_in_house(planet, house, entry.get("detailed", ""))
        if enriched != entry.get("detailed"):
            entry = dict(entry)
            entry["detailed"] = enriched
    return entry


def _make_fallback_planet_in_sign_en(planet: str, sign: str) -> Dict[str, Any]:
    p = PLANETS.get(planet)
    s = SIGNS.get(sign)
    p_name = p.name_en if p else planet
    s_name = s.name_en if s else sign
    dignity = get_dignity_label(planet, sign)
    tag = f" ({dignity})" if dignity != "neutral" else ""

    sign_data = get_sign_keywords(sign)
    pos = sign_data.get("positive", [])
    neg = sign_data.get("negative", [])
    behavior = sign_data.get("behavior", sign_data.get("core", []))
    short_desc = get_sign_short_description(sign)
    func_text = get_planet_function(planet)
    s_obj = SIGNS.get(sign)
    element_en = s_obj.element if s_obj else ""

    pos_sample = "; ".join(pos[:4]) if pos else ""
    neg_sample = "; ".join(neg[:3]) if neg else ""
    beh_sample = "; ".join(behavior[:3]) if behavior else ""

    detailed_parts = []

    # Paragraph 1: Planet function + sign context
    if func_text:
        func_short = func_text[:200]
        opening = (
            f"{p_name} in {s_name}{tag}: "
            f"{func_short} "
            f"Placed in {s_name} ({element_en}), "
            f"this energy is expressed through the lens of this {element_en} sign."
        )
    else:
        opening = (
            f"{p_name} in {s_name}{tag}: "
            f"this placement belongs to the {element_en} element, "
            f"shaping how {p_name}'s energy expresses itself through you."
        )
    detailed_parts.append(opening)

    # Paragraph 2: Sign description
    if short_desc:
        detailed_parts.append(
            f"As a {s_name} native in this placement, {short_desc}"
        )

    # Paragraph 3: Positive traits and tendencies
    if pos_sample or beh_sample:
        traits_parts = []
        if pos_sample:
            traits_parts.append(
                f"Key strengths include {pos_sample}. "
                f"These qualities help you express {p_name}'s energy in a constructive way."
            )
        if beh_sample:
            traits_parts.append(
                f"Your natural tendencies: you often {beh_sample}. "
                f"This shapes how you approach the areas governed by {p_name}."
            )
        detailed_parts.append("\n\n".join(traits_parts))

    # Paragraph 4: Challenges
    if neg_sample:
        detailed_parts.append(
            f"Challenges to be aware of: {neg_sample}. "
            f"Recognizing these patterns helps you grow and find balance "
            f"in how {p_name} operates through {s_name}."
        )
    else:
        detailed_parts.append(
            f"Overall, {p_name} in {s_name} creates a harmonious blend, "
            f"allowing you to channel this planetary energy naturally and effectively."
        )

    return {
        "title": f"{p_name} in {s_name}{tag}",
        "short": f"{p_name} in {s_name}: {short_desc}" if short_desc else f"{p_name} in {s_name}: an exploratory placement.",
        "detailed": "\n\n".join(detailed_parts),
        "strength": pos_sample or "To be explored",
        "weakness": neg_sample or "Needs time to understand",
    }


def _make_fallback_planet_in_house_en(planet: str, house: int) -> Dict[str, Any]:
    p = PLANETS.get(planet)
    h = HOUSES.get(house)
    p_name = p.name_en if p else planet
    h_name = h.name_en if h else f"House {house}"

    house_data = get_house_keywords(house)
    kw_list = house_data.get("keywords", [])
    h_desc = house_data.get("description", "")
    h_title = house_data.get("title", h_name)

    kw_sample = "; ".join(kw_list[:5]) if kw_list else ""

    detailed = f"{p_name} in the {h_title}:"
    if h_desc:
        detailed += "\n\n" + h_desc
    if kw_sample:
        detailed += "\n\nKeywords: " + kw_sample + "."

    return {
        "title": f"{p_name} in the {h_title}",
        "short": f"{p_name} in the {h_title}" + (": " + h_desc[:100] if h_desc else ""),
        "detailed": detailed,
    }


def _make_fallback_planet_in_house(planet: str, house: int) -> Dict[str, Any]:
    p = PLANETS.get(planet)
    h = HOUSES.get(house)
    p_name = p.name_vi if p else planet
    h_name = h.name_vi if h else f"Nhà {house}"
    
    house_data = get_house_keywords(house)
    kw_list = house_data.get("keywords", [])
    h_desc = house_data.get("description", "")
    h_title = house_data.get("title", h_name)
    
    kw_sample = "; ".join(kw_list[:5]) if kw_list else ""
    
    detailed_parts = [f"{p_name} ở {h_title}:"]
    if h_desc:
        detailed_parts.append(h_desc)
    if kw_sample:
        detailed_parts.append(f"Từ khoá: {kw_sample}.")
    
    func_text = get_planet_function(planet)
    if func_text:
        func_short = func_text.split(".")[0] + "."
        detailed_parts.append(func_short)
    
    detailed_text = "\n\n".join(detailed_parts)
    if _ESOTERIC_MODE and is_kb_available():
        detailed_text = enrich_planet_in_house(planet, house, detailed_text)

    return {
        "title": f"{p_name} ở {h_name}",
        "short": f"{p_name} ở {h_name}: {h_desc[:100]}" if h_desc else f"{p_name} ở {h_name}: {kw_sample[:100]}",
        "detailed": detailed_text,
    }


def get_aspect(planet1: str, planet2: str, aspect_type: str, lang: str = "vi") -> Optional[Dict[str, Any]]:
    data = _load_yaml(lang, "aspects.yaml")
    ordered = sorted([planet1, planet2])
    key = f"{ordered[0]}_{ordered[1]}_{aspect_type}"
    entry = data.get(key)
    if entry:
        if isinstance(entry, str):
            a = ASPECTS.get(aspect_type)
            a_name = a.name_en if a and lang == "en" else a.name_vi if a else aspect_type
            p1 = PLANETS.get(planet1)
            p2 = PLANETS.get(planet2)
            p1_name = p1.name_en if p1 and lang == "en" else p1.name_vi if p1 else planet1
            p2_name = p2.name_en if p2 and lang == "en" else p2.name_vi if p2 else planet2
            return {"title": f"{a_name}: {p1_name} - {p2_name}", "short": entry[:100], "detailed": entry}
        return entry
    if lang == "en":
        baked = _load_baked_yaml("aspects_baked.yaml")
        bentry = (baked.get(aspect_type, {}) or {}).get(f"{planet1}_{planet2}")
        if bentry and isinstance(bentry, dict):
            bentry = dict(bentry)
            a = ASPECTS.get(aspect_type)
            a_name = a.name_en if a else aspect_type
            p1 = PLANETS.get(planet1); p2 = PLANETS.get(planet2)
            bentry.setdefault("title", f"{a_name}: {p1.name_en if p1 else planet1} - {p2.name_en if p2 else planet2}")
            bentry.setdefault("short", bentry.get("title", ""))
            return bentry
        kb = _kb_retrieve_aspect(planet1, planet2, aspect_type) if _kb_retriever_available() else None
        if kb:
            a = ASPECTS.get(aspect_type)
            a_name = a.name_en if a else aspect_type
            p1 = PLANETS.get(planet1); p2 = PLANETS.get(planet2)
            p1_name = p1.name_en if p1 else planet1
            p2_name = p2.name_en if p2 else planet2
            return {
                "title": f"{a_name}: {p1_name} - {p2_name}",
                "short": f"{p1_name} {a_name} {p2_name}",
                "detailed": kb,
                "strength": "See description",
                "weakness": "See description",
            }
        return _make_fallback_aspect_en(planet1, planet2, aspect_type)
    return _make_fallback_aspect(planet1, planet2, aspect_type)


def _make_fallback_aspect(planet1: str, planet2: str, aspect_type: str) -> Dict[str, Any]:
    p1 = PLANETS.get(planet1)
    p2 = PLANETS.get(planet2)
    a = ASPECTS.get(aspect_type)
    p1_name = p1.name_vi if p1 else planet1
    p2_name = p2.name_vi if p2 else planet2
    a_name = a.name_vi if a else aspect_type

    p1_func = get_planet_function(planet1)
    p2_func = get_planet_function(planet2)

    is_harmonious = a.nature in ("harmonious", "neutral") if a else True

    nature_map = {
        "conjunction": ("hòa trộn và kết hợp", "pha trộn hai nguồn năng lượng"),
        "sextile": ("hỗ trợ nhẹ nhàng và mở ra cơ hội", "tạo điều kiện thuận lợi"),
        "square": ("tạo ra căng thẳng và thúc đẩy hành động", "tạo động lực vượt qua thử thách"),
        "trine": ("hài hòa và dễ dàng", "cho phép năng lượng chảy tự nhiên"),
        "opposition": ("tạo ra sự đối lập và bổ sung", "kêu gọi sự cân bằng và nhận thức"),
        "quincunx": ("đòi hỏi sự điều chỉnh và thích nghi", "cần sự tinh chỉnh và linh hoạt"),
        "semisextile": ("tiềm ẩn và chưa rõ ràng", "cần thời gian để bộc lộ"),
        "semisquare": ("gây khó chịu nhẹ và cọ xát", "tạo áp lực nhẹ để điều chỉnh"),
        "sesquiquadrate": ("tích tụ căng thẳng âm ỉ", "đòi hỏi giải pháp sáng tạo"),
        "quintile": ("tài năng và sáng tạo ", "mang năng lực bẩm sinh đặc biệt"),
    }
    default_harmonious = ("hỗ trợ và cộng hưởng tích cực", "mang đến cơ hội phát triển thuận lợi")
    default_challenging = ("tạo ra căng thẳng và thách thức", "đòi hỏi sự điều chỉnh và trưởng thành")
    nature_desc, flow_desc = nature_map.get(aspect_type, default_harmonious if is_harmonious else default_challenging)

    # Planet pair interaction descriptions
    pair_key = "_".join(sorted([planet1, planet2]))
    pair_intro = {
        "sun_moon": f"{p1_name} đại diện cho ý thức, bản ngã và mục đích sống, trong khi {p2_name} đại diện cho cảm xúc, tiềm thức và nhu cầu an toàn",
        "sun_mercury": f"{p1_name} đại diện cho bản ngã và sức sống, trong khi {p2_name} đại diện cho tư duy, giao tiếp và học hỏi",
        "sun_venus": f"{p1_name} đại diện cho bản ngã và mục đích, trong khi {p2_name} đại diện cho tình yêu, cái đẹp và giá trị cá nhân",
        "sun_mars": f"{p1_name} đại diện cho ý chí và mục đích sống, trong khi {p2_name} đại diện cho hành động, xung lực và khát vọng chinh phục",
        "sun_jupiter": f"{p1_name} đại diện cho bản ngã và sự khẳng định, trong khi {p2_name} đại diện cho sự mở rộng, may mắn và triết lý",
        "sun_saturn": f"{p1_name} đại diện cho bản ngã và sự tỏa sáng, trong khi {p2_name} đại diện cho kỷ luật, trách nhiệm và giới hạn",
        "sun_uranus": f"{p1_name} đại diện cho bản ngã và sự ổn định, trong khi {p2_name} đại diện cho sự đột phá, tự do và đổi mới",
        "sun_neptune": f"{p1_name} đại diện cho bản ngã và ranh giới, trong khi {p2_name} đại diện cho sự hòa tan, mơ mộng và tâm linh",
        "sun_pluto": f"{p1_name} đại diện cho bản ngã và sự sống, trong khi {p2_name} đại diện cho biến đổi, quyền lực và tái sinh",
        "moon_mercury": f"{p1_name} đại diện cho cảm xúc và trực giác, trong khi {p2_name} đại diện cho lý trí và tư duy logic",
        "moon_venus": f"{p1_name} đại diện cho nhu cầu cảm xúc, trong khi {p2_name} đại diện cho tình yêu, sự hài hòa và thẩm mỹ",
        "moon_mars": f"{p1_name} đại diện cho cảm xúc và nhu cầu an toàn, trong khi {p2_name} đại diện cho hành động, xung năng và sự quyết đoán",
        "moon_jupiter": f"{p1_name} đại diện cho thế giới nội tâm và cảm xúc, trong khi {p2_name} đại diện cho sự lạc quan, mở rộng và niềm tin",
        "moon_saturn": f"{p1_name} đại diện cho cảm xúc và nhu cầu được che chở, trong khi {p2_name} đại diện cho trách nhiệm, kỷ luật và sự hạn chế",
        "venus_mars": f"{p1_name} đại diện cho tình yêu, hài hòa và giá trị, trong khi {p2_name} đại diện cho đam mê, hành động và chinh phục",
        "venus_jupiter": f"{p1_name} đại diện cho tình yêu và cái đẹp, trong khi {p2_name} đại diện cho sự may mắn, mở rộng và lạc quan",
        "venus_saturn": f"{p1_name} đại diện cho tình yêu và sự gắn kết, trong khi {p2_name} đại diện cho trách nhiệm, kỷ luật và thử thách",
        "mars_jupiter": f"{p1_name} đại diện cho hành động và xung lực, trong khi {p2_name} đại diện cho sự mở rộng, may mắn và lạc quan",
        "mars_saturn": f"{p1_name} đại diện cho hành động và xung năng, trong khi {p2_name} đại diện cho kỷ luật, giới hạn và kiên nhẫn",
        "jupiter_saturn": f"{p1_name} đại diện cho sự mở rộng và lạc quan, trong khi {p2_name} đại diện cho kỷ luật, trách nhiệm và cấu trúc",
        "uranus_neptune": f"{p1_name} đại diện cho sự đột phá và đổi mới, trong khi {p2_name} đại diện cho lý tưởng, mơ mộng và tâm linh",
        "uranus_pluto": f"{p1_name} đại diện cho sự thay đổi mang tính cách mạng, trong khi {p2_name} đại diện cho biến đổi sâu sắc và tái sinh",
        "neptune_pluto": f"{p1_name} đại diện cho sự hòa tan và tâm linh, trong khi {p2_name} đại diện cho quyền lực và biến đổi triệt để",
    }

    if pair_key in pair_intro:
        pair_text = pair_intro[pair_key]
    else:
        pair_text = f"{p1_name} và {p2_name}: hai nguồn năng lượng thiên thể tương tác với nhau"

    # Aspect-type behavioral insight
    aspect_behavior = {
        "conjunction": "Năng lượng của hai hành tinh hòa quyện và khuếch đại lẫn nhau, tạo thành một lực lượng thống nhất mạnh mẽ trong tính cách của bạn.",
        "sextile": "Đây là góc chiếu mang tính cơ hội, khuyến khích bạn tận dụng những tiềm năng từ sự kết hợp này để phát triển bản thân.",
        "square": "Góc chiếu này tạo ra xung đột nội tâm và thách thức từ bên ngoài, thúc đẩy bạn hành động, vượt qua trở ngại và trưởng thành.",
        "trine": "Năng lượng giữa hai hành tinh chảy một cách tự nhiên và hài hòa, mang đến tài năng bẩm sinh và những thuận lợi không cần nỗ lực.",
        "opposition": "Góc chiếu này tạo ra sự căng thẳng giữa hai cực đối lập, mời gọi bạn tìm kiếm sự cân bằng và nhìn nhận từ nhiều góc độ.",
        "quincunx": "Góc chiếu này đòi hỏi sự điều chỉnh liên tục, giúp bạn phát triển tính linh hoạt và khả năng thích ứng với những điều bất ngờ.",
        "semisextile": "Góc chiếu này mang tiềm năng chưa được khai phá, đợi đến thời điểm chín muồi để bộc lộ và phát triển.",
    }
    behavior_text = aspect_behavior.get(aspect_type, "")

    # Build the detailed text
    detailed_parts = [
        f"{p1_name} {a_name} {p2_name}: góc chiếu {a_name} {nature_desc} giữa {p1_name} và {p2_name}.",
        pair_text + ".",
    ]

    if behavior_text:
        detailed_parts.append(behavior_text)

    if p1_func:
        p1_short = p1_func.split(".")[0] + "."
        detailed_parts.append(f"{p1_name}: {p1_short}")
    if p2_func:
        p2_short = p2_func.split(".")[0] + "."
        detailed_parts.append(f"{p2_name}: {p2_short}")

    detailed_parts.append(
        f"Sự kết hợp này {flow_desc}. Tác động cụ thể phụ thuộc vào bối cảnh tổng thể của lá số, "
        f"các góc chiếu khác và sự trưởng thành của bạn."
    )

    return {
        "title": f"{a_name}: {p1_name} - {p2_name}",
        "short": f"{p1_name} {a_name} {p2_name}: {nature_desc}",
        "detailed": "\n\n".join(detailed_parts),
    }


def _make_fallback_aspect_en(planet1: str, planet2: str, aspect_type: str) -> Dict[str, Any]:
    p1 = PLANETS.get(planet1)
    p2 = PLANETS.get(planet2)
    a = ASPECTS.get(aspect_type)
    p1_name = p1.name_en if p1 else planet1
    p2_name = p2.name_en if p2 else planet2
    a_name = a.name_en if a else aspect_type

    p1_func = get_planet_function(planet1)
    p2_func = get_planet_function(planet2)

    is_harmonious = a.nature in ("harmonious", "neutral") if a else True

    nature_map = {
        "conjunction": ("blends and merges", "blending the two energies"),
        "sextile": ("supports gently and opens opportunities", "creates favorable conditions"),
        "square": ("creates tension and drives action", "creates motivation to overcome challenges"),
        "trine": ("harmonizes and flows easily", "allows energy to flow naturally"),
        "opposition": ("creates polarity and complement", "calls for balance and awareness"),
        "quincunx": ("demands adjustment and adaptation", "needs fine-tuning and flexibility"),
        "semisextile": ("is subtle and not yet clear", "needs time to unfold"),
        "semisquare": ("causes mild friction and irritation", "creates gentle pressure to adjust"),
        "sesquiquadrate": ("builds simmering tension", "demands creative solutions"),
        "quintile": ("brings talent and creativity", "carries special innate ability"),
    }
    default_harmonious = ("supports and resonates positively", "brings favorable growth opportunities")
    default_challenging = ("creates tension and challenge", "demands adjustment and maturity")
    nature_desc, flow_desc = nature_map.get(aspect_type, default_harmonious if is_harmonious else default_challenging)

    pair_key = "_".join(sorted([planet1, planet2]))
    pair_intro = {
        "sun_moon": f"{p1_name} represents ego, identity and life purpose, while {p2_name} represents emotions, subconscious and need for security",
        "sun_mercury": f"{p1_name} represents the self and vitality, while {p2_name} represents mind, communication and learning",
        "sun_venus": f"{p1_name} represents identity and purpose, while {p2_name} represents love, beauty and personal values",
        "sun_mars": f"{p1_name} represents willpower and life purpose, while {p2_name} represents action, drive and the urge to conquer",
        "sun_jupiter": f"{p1_name} represents the self and assertion, while {p2_name} represents expansion, luck and philosophy",
        "sun_saturn": f"{p1_name} represents the self and radiance, while {p2_name} represents discipline, responsibility and limits",
        "sun_uranus": f"{p1_name} represents the self and stability, while {p2_name} represents breakthrough, freedom and innovation",
        "sun_neptune": f"{p1_name} represents the self and boundaries, while {p2_name} represents dissolution, dreams and spirituality",
        "sun_pluto": f"{p1_name} represents the self and life, while {p2_name} represents transformation, power and rebirth",
        "moon_mercury": f"{p1_name} represents emotions and intuition, while {p2_name} represents reason and logical thought",
        "moon_venus": f"{p1_name} represents emotional needs, while {p2_name} represents love, harmony and aesthetics",
        "moon_mars": f"{p1_name} represents emotions and need for safety, while {p2_name} represents action, drive and assertiveness",
        "moon_jupiter": f"{p1_name} represents the inner world and feelings, while {p2_name} represents optimism, expansion and faith",
        "moon_saturn": f"{p1_name} represents emotions and need for protection, while {p2_name} represents responsibility, discipline and restriction",
        "venus_mars": f"{p1_name} represents love, harmony and values, while {p2_name} represents passion, action and conquest",
        "venus_jupiter": f"{p1_name} represents love and beauty, while {p2_name} represents luck, expansion and optimism",
        "venus_saturn": f"{p1_name} represents love and bonding, while {p2_name} represents responsibility, discipline and challenge",
        "mars_jupiter": f"{p1_name} represents action and drive, while {p2_name} represents expansion, luck and optimism",
        "mars_saturn": f"{p1_name} represents action and impulse, while {p2_name} represents discipline, limits and patience",
        "jupiter_saturn": f"{p1_name} represents expansion and optimism, while {p2_name} represents discipline, responsibility and structure",
        "uranus_neptune": f"{p1_name} represents breakthrough and innovation, while {p2_name} represents ideals, dreams and spirituality",
        "uranus_pluto": f"{p1_name} represents revolutionary change, while {p2_name} represents deep transformation and rebirth",
        "neptune_pluto": f"{p1_name} represents dissolution and spirituality, while {p2_name} represents power and radical transformation",
    }

    if pair_key in pair_intro:
        pair_text = pair_intro[pair_key]
    else:
        pair_text = f"{p1_name} and {p2_name}: two celestial energies interacting"

    aspect_behavior = {
        "conjunction": "The energies of the two planets blend and amplify each other, forming a powerful unified force in your personality.",
        "sextile": "This is an opportunistic aspect, encouraging you to leverage the potential of this combination for personal growth.",
        "square": "This aspect creates inner conflict and external challenges, pushing you to act, overcome obstacles and mature.",
        "trine": "Energy flows naturally and harmoniously between these two planets, bringing innate talents and effortless advantages.",
        "opposition": "This aspect creates tension between opposite poles, inviting you to find balance and see from multiple perspectives.",
        "quincunx": "This aspect demands constant adjustment, helping you develop flexibility and adaptability to unexpected situations.",
        "semisextile": "This aspect carries hidden potential, waiting for the right time to unfold and develop.",
    }
    behavior_text = aspect_behavior.get(aspect_type, "")

    detailed_parts = [
        f"{p1_name} {a_name} {p2_name}: this {a_name} {nature_desc} between {p1_name} and {p2_name}.",
        pair_text + ".",
    ]

    if behavior_text:
        detailed_parts.append(behavior_text)

    if p1_func:
        p1_short = p1_func.split(".")[0] + "."
        detailed_parts.append(f"{p1_name}: {p1_short}")
    if p2_func:
        p2_short = p2_func.split(".")[0] + "."
        detailed_parts.append(f"{p2_name}: {p2_short}")

    detailed_parts.append(
        f"This combination {flow_desc}. The specific impact depends on the overall chart context, "
        f"other aspects and your personal maturity level."
    )

    return {
        "title": f"{a_name}: {p1_name} - {p2_name}",
        "short": f"{p1_name} {a_name} {p2_name}: {nature_desc}",
        "detailed": "\n\n".join(detailed_parts),
    }


def get_pattern(pattern_type: str, qualifier: str, lang: str = "vi") -> Optional[Dict[str, Any]]:
    data = _load_yaml(lang, "patterns.yaml")
    entry = data.get(pattern_type)
    if entry is None:
        return None
    if isinstance(entry, dict):
        return {"text": entry.get(qualifier, list(entry.values())[0])}
    return {"text": entry}


def get_element_text(key: str, lang: str = "vi") -> Optional[str]:
    data = _load_yaml(lang, "elements.yaml")
    return data.get(key) if data else None


def get_quality_text(key: str, lang: str = "vi") -> Optional[str]:
    """Get quality distribution text (dominant/deficient cardinal/fixed/mutable)."""
    data = _load_yaml(lang, "qualities.yaml")
    return data.get(key) if data else None


def get_house_type_text(key: str, lang: str = "vi") -> Optional[str]:
    """Get house type text (dominant_angular/succedent/cadent, balanced_houses)."""
    data = _load_yaml(lang, "house_types.yaml")
    return data.get(key) if data else None


def get_dignity_text(dignity: str, lang: str = "vi", planet: str = "", sign: str = "") -> Optional[str]:
    data = _load_yaml(lang, "dignities.yaml")
    text = data.get(dignity) if data else None
    if text and planet and sign and lang == "vi":
        text = _enrich_dignity_text(text, planet, sign, dignity)
    return text


def get_house_cusp(sign: str, house: int, lang: str = "vi") -> Optional[Dict[str, Any]]:
    """Get house cusp interpretation for a sign on a house cusp."""
    # Only en has AstroLibrary data; vi falls back to keyword-based
    if lang != "en":
        return None
    data = _load_yaml("en", "house_cusp.yaml")
    sign_data = data.get(sign, {})
    entry = sign_data.get(str(house))
    if entry and isinstance(entry, dict):
        if not entry.get("title"):
            entry = dict(entry)
            s = SIGNS.get(sign)
            h = HOUSES.get(house)
            s_name = s.name_en if s else sign
            h_name = h.name_en if h else f"House {house}"
            entry["title"] = f"{s_name} on Cusp of {h_name}"
        return entry
    return None


def get_combination(
    planet: str,
    sign: str,
    house: int,
    lang: str = "vi",
    chart=None,
) -> Optional[Dict[str, Any]]:
    from astrololo.interpretation.chart_synthesis import (
        is_placeholder_combination,
        make_combination_synthesis,
    )

    data = _load_yaml(lang, "combinations.yaml")
    entry = data.get(f"{planet}_{sign}_{house}")
    if entry and not is_placeholder_combination(entry):
        return entry
    return make_combination_synthesis(planet, sign, house, chart=chart, lang=lang)


def get_fixed_star_conjunction(
    star_name: str, planet_name: str, lang: str = "vi"
) -> Optional[Dict[str, Any]]:
    from astrololo.core.fixed_stars import FIXED_STARS

    star = FIXED_STARS.get(star_name)
    if not star:
        return None
    planet_obj = PLANETS.get(planet_name, {})
    p_name_vi = getattr(planet_obj, "name_vi", planet_name)
    p_name_en = getattr(planet_obj, "name_en", planet_name)
    s_name_vi = star["name_vi"]
    s_name_en = star["name_en"]
    meaning_vi = star.get("meaning_vi", "")
    meaning_en = star.get("meaning_en", "")
    keywords_vi = star.get("keywords_vi", [])
    keywords_en = star.get("keywords_en", [])
    nature = star.get("nature", "neutral")
    mag = star.get("mag", 1.0)

    if nature == "benefic":
        nature_effect_vi = "Đây là một dấu hiệu thuận lợi, mang lại may mắn và bảo vệ."
        nature_effect_en = "This is a favorable indicator, bringing luck and protection."
    elif nature == "malefic":
        nature_effect_vi = "Đây là một dấu hiệu thách thức, đòi hỏi sự thận trọng và sức mạnh nội tâm."
        nature_effect_en = "This is a challenging indicator, requiring caution and inner strength."
    else:
        nature_effect_vi = "Tác động của ngôi sao này phụ thuộc vào cách bạn sử dụng năng lượng của nó."
        nature_effect_en = "The star influence depends on how you channel its energy."

    if lang == "vi":
        title = f"{s_name_vi} hợp {p_name_vi}"
        nature_text = "tốt" if nature == "benefic" else "xấu" if nature == "malefic" else "trung tính"
        detail = f"""Sao cố định {s_name_vi} (sao {nature_text}, cấp sao {mag}) kết hợp với {p_name_vi} trong lá số của bạn.

{s_name_vi}: {meaning_vi}

Khi một ngôi sao cố định mạnh mẽ như {s_name_vi} kết hợp với {p_name_vi}, nó tô màu và khuếch đại năng lượng của hành tinh này. {nature_effect_vi}

Từ khóa liên quan: {', '.join(keywords_vi)}."""
    else:
        title = f"{s_name_en} conjunct {p_name_en}"
        detail = f"""The fixed star {s_name_en} (magnitude {mag}, {nature} nature) conjoins your {p_name_en}.

{s_name_en}: {meaning_en}

When a powerful fixed star like {s_name_en} conjoins {p_name_en}, it colors and amplifies the planet's energy. {nature_effect_en}

Related keywords: {', '.join(keywords_en)}."""

    return {"title": title, "short": "", "detailed": detail}


def get_ascendant_entry(sign: str, lang: str = "en") -> Optional[Dict[str, Any]]:
    """Get ascendant interpretation for a sign. Only EN has templates."""
    data = _load_yaml(lang, "ascendant.yaml")
    entry = data.get(sign)
    if entry and isinstance(entry, dict):
        if not entry.get("title"):
            s = SIGNS.get(sign)
            s_name = s.name_en if s and lang == "en" else s.name_vi if s else sign
            entry = dict(entry)
            entry["title"] = f"Ascendant in {s_name}" if lang == "en" else f"Cung Mọc {s_name}"
        return entry
    return None


def get_mc_entry(sign: str, lang: str = "en") -> Optional[Dict[str, Any]]:
    """Get MC interpretation for a sign. Only EN has templates."""
    data = _load_yaml(lang, "mc.yaml")
    entry = data.get(sign)
    if entry and isinstance(entry, dict):
        if not entry.get("title"):
            s = SIGNS.get(sign)
            s_name = s.name_en if s and lang == "en" else s.name_vi if s else sign
            entry = dict(entry)
            entry["title"] = f"MC in {s_name}" if lang == "en" else f"MC ở {s_name}"
        return entry
    return None


def get_retrograde_text(planet: str, lang: str = "vi", count: int = 1, names: str = "") -> Optional[str]:
    """Get retrograde interpretation for a planet from template."""
    data = _load_yaml(lang, "retrogrades.yaml")
    entry = data.get(planet)
    if entry and isinstance(entry, str):
        return entry.format(count=count, planets=names)
    return None


def clear_cache():
    _cache.clear()


def get_cct_topics_for_section(section: str):
    """Lightweight CCT taxonomy bundle; avoids hard dependency if unused."""
    from astrololo.interpretation.knowledge_cct import mapping_for_section
    return mapping_for_section(section)
