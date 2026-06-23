"""Transit-specific interpretation engine — generates per-planet transit text."""
from typing import List, Dict, Any
from astrololo.models.chart import ChartData
from astrololo.core.constants import PLANETS, SIGNS, HOUSES
from astrololo.interpretation.keywords import get_planet_function, get_house_keywords, get_sign_keywords

_FAST_PLANETS = ["moon", "sun", "mercury", "venus", "mars"]
_SLOW_PLANETS = ["jupiter", "saturn", "uranus", "neptune", "pluto"]


def _find_natal_house(longitude: float, natal_houses: List[Any]) -> int:
    for i in range(12):
        cusp = natal_houses[i].cusp_degree
        next_cusp = natal_houses[(i + 1) % 12].cusp_degree
        if i == 11:
            next_cusp += 360
        lon = longitude
        if lon < cusp:
            lon += 360
        if cusp <= lon < next_cusp:
            return i + 1
    return 1


def _planet_name(planet_key: str, lang: str) -> str:
    p = PLANETS.get(planet_key)
    return p.name_vi if p and lang == "vi" else p.name_en if p else planet_key


def _sign_name(sign_key: str, lang: str) -> str:
    s = SIGNS.get(sign_key)
    return s.name_vi if s and lang == "vi" else s.name_en if s else sign_key


def _house_name(house_num: int, lang: str) -> str:
    h = HOUSES.get(house_num)
    return h.name_vi if h and lang == "vi" else h.name_en if h else f"House {house_num}"


def _nature_label(nature: str, lang: str) -> str:
    if lang == "vi":
        return {"harmonious": "hài hòa", "challenging": "thách thức", "neutral": "trung tính"}.get(nature, nature)
    return nature


def _make_transit_planet_text(
    tp: Any, natal_house: int, aspects: List[Any], lang: str
) -> Dict[str, Any]:
    p_key = tp.name
    pn = _planet_name(p_key, lang)
    sn = _sign_name(tp.sign, lang)
    hn = _house_name(natal_house, lang)

    func = get_planet_function(p_key)
    func_short = func.split(".")[0] + "." if func else ""

    is_fast = p_key in _FAST_PLANETS
    is_slow = p_key in _SLOW_PLANETS

    # Sign interpretation
    sign_data = get_sign_keywords(tp.sign)
    pos_kw = sign_data.get("positive", [])
    beh_kw = sign_data.get("behavior", sign_data.get("core", []))
    pos_sample = "; ".join(pos_kw[:3]) if pos_kw else ""
    beh_sample = "; ".join(beh_kw[:2]) if beh_kw else ""

    if lang == "vi":
        speed_desc = "di chuyển nhanh" if is_fast else "di chuyển chậm" if is_slow else ""
        period = "vài ngày" if p_key == "moon" else "vài tuần" if is_fast else "vài tháng" if p_key in ("mercury", "venus", "mars") else "khoảng 1 năm" if p_key == "jupiter" else "2-3 năm" if p_key == "saturn" else "nhiều năm"

        sign_part = f"{pn} đang quá cảnh qua cung {sn}. {func_short} Đây là hành tinh {speed_desc}, ảnh hưởng kéo dài {period}."
        if pos_sample:
            sign_part += f" Trong cung {sn}, năng lượng này thể hiện qua: {pos_sample}."
        if beh_sample:
            sign_part += f" Xu hướng: {beh_sample}."

        house_part = f"{pn} đang ảnh hưởng đến Nhà {natal_house} ({hn}) trong lá số gốc của bạn."
        hk = get_house_keywords(natal_house)
        h_desc = hk.get("description", "")
        h_kw = hk.get("keywords", [])
        if h_desc:
            house_part += f" {h_desc}."
        if h_kw:
            house_part += f" Lĩnh vực: {'; '.join(h_kw[:3])}."

        retro_text = f" {pn} đang nghịch hành, bạn có thể cảm nhận năng lượng này một cách nội tâm hơn." if tp.is_retrograde else ""
    else:
        speed_desc = "fast-moving" if is_fast else "slow-moving" if is_slow else ""
        period = "a few days" if p_key == "moon" else "a few weeks" if is_fast else "a few months" if p_key in ("mercury", "venus", "mars") else "about 1 year" if p_key == "jupiter" else "2-3 years" if p_key == "saturn" else "many years"

        sign_part = f"Transit {pn} is moving through {sn}. {func_short} This is a {speed_desc} planet, with influence lasting {period}."
        if pos_sample:
            sign_part += f" In {sn}, this energy expresses through: {pos_sample}."
        if beh_sample:
            sign_part += f" Tendencies: {beh_sample}."

        house_part = f"{pn} is currently transiting your {natal_house} house ({hn})."
        hk = get_house_keywords(natal_house)
        h_desc = hk.get("description", "")
        h_kw = hk.get("keywords", [])
        if h_desc:
            house_part += f" {h_desc}."
        if h_kw:
            house_part += f" Areas: {'; '.join(h_kw[:3])}."

        retro_text = f" {pn} is retrograde, so you may feel this energy more inwardly." if tp.is_retrograde else ""

    # Aspect text
    aspect_lines = []
    for a in aspects:
        other_p = a.planet2 if a.planet1 == p_key else a.planet1
        other_n = _planet_name(other_p, lang)
        a_type = a.aspect_type
        a_nature = _nature_label(a.nature, lang)
        a_name = a.aspect_name_vi if lang == "vi" else a_type.capitalize()

        if lang == "vi":
            if a.nature == "harmonious":
                line = f"  Góc {a_name} với {other_n} ({a_nature}): thuận lợi, hỗ trợ cho {pn} quá cảnh."
            elif a.nature == "challenging":
                line = f"  Góc {a_name} với {other_n} ({a_nature}): tạo áp lực, thúc đẩy bạn điều chỉnh."
            else:
                line = f"  Góc {a_name} với {other_n}: tương tác trung tính, tùy bối cảnh."
        else:
            if a.nature == "harmonious":
                line = f"  {a_name} to natal {other_n} ({a_nature}): supportive, easy flow."
            elif a.nature == "challenging":
                line = f"  {a_name} to natal {other_n} ({a_nature}): pressure, calls for adjustment."
            else:
                line = f"  {a_name} to natal {other_n}: neutral interaction, depends on context."
        aspect_lines.append(line)

    # Build final text
    parts = [sign_part + retro_text, house_part]
    if aspect_lines:
        if lang == "vi":
            parts.append("Các góc chiếu với lá số gốc:")
        else:
            parts.append("Aspects to your natal chart:")
        parts.extend(aspect_lines)

    return {
        "planet": p_key,
        "planet_name_vi": _planet_name(p_key, "vi"),
        "planet_name_en": _planet_name(p_key, "en"),
        "sign": tp.sign,
        "natal_house": natal_house,
        "is_retrograde": tp.is_retrograde,
        "text_vi": "\n\n".join(parts) if lang == "vi" else "",
        "text_en": "\n\n".join(parts) if lang == "en" else "",
    }


def interpret_transit(natal: ChartData, transit: ChartData, lang: str = "vi") -> Dict[str, Any]:
    """Generate transit-specific interpretation sections."""
    transit_planets = transit.planets
    transit_aspects = transit.aspects

    per_planet: List[Dict[str, Any]] = []
    for tp in transit_planets:
        if tp.body_type != "planet":
            continue
        natal_house = _find_natal_house(tp.longitude, natal.houses)
        aspects_to_natal = [
            a for a in transit_aspects
            if (a.planet1 == tp.name or a.planet2 == tp.name)
        ]
        aspects_to_natal.sort(key=lambda a: -abs(a.weight))
        top_aspects = aspects_to_natal[:5]

        entry = _make_transit_planet_text(tp, natal_house, top_aspects, lang)
        per_planet.append(entry)

    # Count harmonious/challenging
    total_harm = sum(1 for a in transit_aspects if a.nature == "harmonious")
    total_chall = sum(1 for a in transit_aspects if a.nature == "challenging")

    # Overview text
    active_fast = [p for p in per_planet if p["planet"] in _FAST_PLANETS]
    active_slow = [p for p in per_planet if p["planet"] in _SLOW_PLANETS]

    if lang == "vi":
        overview = (
            f"Tổng quan quá cảnh: {len(active_slow)} hành tinh chậm và {len(active_fast)} hành tinh nhanh "
            f"đang tạo ảnh hưởng lên lá số của bạn. "
            f"Có {total_harm} góc chiếu hài hòa và {total_chall} góc chiếu thách thức."
        )
        title = f"Diễn Giải Quá Cảnh — {transit.subject_name.replace(' — Transit ', ' ngày ')}"
    else:
        overview = (
            f"Transit overview: {len(active_slow)} slow planets and {len(active_fast)} fast planets "
            f"are currently affecting your chart. "
            f"There are {total_harm} harmonious and {total_chall} challenging aspects."
        )
        title = f"Transit Interpretation — {transit.subject_name}"

    # Build sections
    sections = []
    if per_planet:
        items = []
        for entry in per_planet:
            items.append({
                "title": entry["planet_name_vi"] if lang == "vi" else entry["planet_name_en"],
                "text": entry["text_vi"] if lang == "vi" else entry["text_en"],
                "score": 0.0,
                "tags": ["transit", entry["planet"], entry["sign"]],
                "metadata": {
                    "planet": entry["planet"],
                    "sign": entry["sign"],
                    "natal_house": entry["natal_house"],
                    "is_retrograde": entry["is_retrograde"],
                },
            })
        sections.append({
            "category": "transit",
            "title": title,
            "items": items,
        })

    return {
        "overview": overview,
        "sections": sections,
        "per_planet": per_planet,
    }
