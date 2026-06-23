"""AI-powered per-planet synthesis — combines planet+sign+house keywords into natural narrative."""
import logging
from typing import List, Dict, Any
from astrololo.interpretation.ai_provider import ai_complete
from astrololo.interpretation.keywords import (
    get_planet_function, get_sign_keywords, get_house_keywords,
)
from astrololo.models.chart import ChartData
from astrololo.core.constants import PLANETS, SIGNS, HOUSES

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_VI = (
    "Bạn là chuyên gia chiêm tinh. Dựa trên từ khóa được cung cấp, "
    "hãy viết 1-2 câu tổng hợp ý nghĩa của hành tinh trong cung và nhà. "
    "Viết tự nhiên, trôi chảy, mang tính luận giải thực tế. "
    "KHÔNG liệt kê từ khóa. KHÔNG thêm giải thích."
)

SYSTEM_PROMPT_EN = (
    "You are an expert astrologer. Based on the keywords provided, "
    "write 1-2 sentences synthesizing the meaning of the planet in sign and house. "
    "Write naturally, conversationally, with practical interpretation. "
    "DO NOT list keywords. DO NOT add explanations."
)


def synthesize_planet(
    planet_name: str,
    sign: str,
    house: int,
    lang: str = "vi",
) -> str:
    """Generate a synthesized paragraph for one planet in sign+house via LLM."""
    p = PLANETS.get(planet_name)
    s = SIGNS.get(sign)
    h = HOUSES.get(house)

    p_name = p.name_vi if p and lang == "vi" else p.name_en if p else planet_name
    s_name = s.name_vi if s and lang == "vi" else s.name_en if s else sign
    h_name = h.name_vi if h and lang == "vi" else h.name_en if h else f"House {house}"

    func = get_planet_function(planet_name) or ""
    sign_data = get_sign_keywords(sign) or {}
    house_data = get_house_keywords(house) or {}

    pos_kw = "; ".join(sign_data.get("positive", [])[:5])
    neg_kw = "; ".join(sign_data.get("negative", [])[:3])
    core_kw = "; ".join(sign_data.get("core", [])[:3])
    h_desc = house_data.get("description", "")
    h_kw = "; ".join(house_data.get("keywords", [])[:5])

    if lang == "vi":
        prompt = (
            f"Hành tinh: {p_name}\n"
            f"Cung: {s_name}\n"
            f"Nhà: {h_name}\n"
            f"Chức năng: {func[:200]}\n"
            f"Từ khóa tích cực: {pos_kw}\n"
            f"Từ khóa tiêu cực: {neg_kw}\n"
            f"Từ khóa cốt lõi: {core_kw}\n"
            f"Mô tả nhà: {h_desc[:200]}\n"
            f"Từ khóa nhà: {h_kw}\n\n"
            f"Viết 1-2 câu tổng hợp ý nghĩa của {p_name} ở {s_name} tại Nhà {house}."
        )
        sp = SYSTEM_PROMPT_VI
    else:
        prompt = (
            f"Planet: {p_name}\n"
            f"Sign: {s_name}\n"
            f"House: {h_name}\n"
            f"Function: {func[:200]}\n"
            f"Positive keywords: {pos_kw}\n"
            f"Negative keywords: {neg_kw}\n"
            f"Core keywords: {core_kw}\n"
            f"House description: {h_desc[:200]}\n"
            f"House keywords: {h_kw}\n\n"
            f"Write 1-2 sentences synthesizing {p_name} in {s_name} in {h_name}."
        )
        sp = SYSTEM_PROMPT_EN

    r = ai_complete([{"role": "user", "content": prompt}], system_prompt=sp)
    if r.success and r.text.strip():
        logger.info(f"AI synthesis OK: {planet_name} ({len(r.text)} chars)")
        return r.text.strip()
    logger.warning(f"AI synthesis FAILED for {planet_name}: {r.error}")
    return ""


def synthesize_all_planets(
    chart: ChartData,
    lang: str = "vi",
    max_planets: int = 10,
) -> List[Dict[str, Any]]:
    """Generate AI synthesis for each physical planet in the chart."""
    physical = [p for p in chart.planets if p.body_type == "planet"]
    results = []

    for p in physical[:max_planets]:
        text = synthesize_planet(p.name, p.sign, p.house or 1, lang)
        if text:
            pl = PLANETS.get(p.name)
            pn = pl.name_vi if pl and lang == "vi" else pl.name_en if pl else p.name
            results.append({
                "planet": p.name,
                "planet_name": pn,
                "text": text,
            })

    return results
