from typing import Optional, List
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.models.chart import ChartData
from astrololo.interpretation.keywords import (
    get_sign_short_description,
    get_sign_keywords,
    get_house_keywords,
    HOUSE_NAME_VI,
    SIGN_NAME_VI,
    SIGN_NATURAL_RULER,
    get_planet_function,
    SIGN_ELEMENT_VI,
    SIGN_QUALITY_VI,
)
from astrololo.interpretation.template_loader import get_house_cusp as get_house_cusp_template
from astrololo.core.constants import PLANETS


class HouseCuspRule(InterpretationRule):
    """Interpret the sign on each house cusp — combined meaning."""

    def __init__(self):
        super().__init__(priority=32)

    def matches(self, chart: ChartData) -> bool:
        return bool(chart.houses)

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[List[RuleResult]]:
        results = []
        for h in chart.houses:
            sign = h.sign
            sign_name = SIGN_NAME_VI.get(sign, sign)
            house_name = HOUSE_NAME_VI.get(h.house_number, f"Nhà {h.house_number}")

            # Try AstroLibrary template first (en only)
            template_entry = get_house_cusp_template(sign, h.house_number, lang) if lang == "en" else None

            if template_entry:
                results.append(RuleResult(
                    title_vi="",
                    title_en=template_entry.get("title", f"{sign_name} on Cusp of House {h.house_number}"),
                    text_vi="",
                    text_en=template_entry.get("detailed", ""),
                    score=5.0,
                    priority=self.priority,
                    category="house_cusp",
                    tags=[sign, f"house_{h.house_number}"],
                    metadata={"house": h.house_number, "sign": sign, "source": "astrolibrary.org"},
                ))
                continue

            # Fallback: keyword-based generation
            ruler_key = SIGN_NATURAL_RULER.get(sign, "")
            ruler_name = ""
            ruler_func = ""
            if ruler_key:
                p = PLANETS.get(ruler_key)
                ruler_name = p.name_vi if p and lang == "vi" else p.name_en if p else ruler_key
                func = get_planet_function(ruler_key)
                if func:
                    ruler_func = func.split(".")[0] + "."

            sign_data = get_sign_keywords(sign)
            pos_kw = sign_data.get("positive", [])
            core_kw = sign_data.get("core", [])
            short_desc = get_sign_short_description(sign)
            issues = sign_data.get("potential_issues", "")

            house_data = get_house_keywords(h.house_number)
            h_desc = house_data.get("description", "")
            h_kw = house_data.get("keywords", [])

            element_vi = SIGN_ELEMENT_VI.get(sign, "")
            quality_vi = SIGN_QUALITY_VI.get(sign, "")

            if lang == "vi":
                parts = [f"Đỉnh {house_name} là {sign_name} ({element_vi} {quality_vi})."]
                if short_desc:
                    parts.append(short_desc)
                if pos_kw:
                    parts.append("Bạn thể hiện: " + "; ".join(pos_kw[:4]) + ".")
                if core_kw:
                    parts.append("Đặc trưng: " + "; ".join(core_kw[:3]) + ".")
                if h_desc:
                    parts.append(f"Trong lĩnh vực này, {h_desc.lower()}")
                if h_kw:
                    parts.append("Phương diện: " + "; ".join(h_kw[:4]) + ".")
                if ruler_name and ruler_func:
                    parts.append(f"Chủ tinh: {ruler_name}. {ruler_func}")
                if issues:
                    parts.append(f"Lưu ý: {issues}")
                text = "\n\n".join(parts)
            else:
                parts = [f"The cusp of {house_name} is in {sign} ({element_vi} {quality_vi})."]
                if short_desc:
                    parts.append(short_desc)
                if h_desc:
                    parts.append(f"In this area, {h_desc.lower()}")
                if ruler_name:
                    parts.append(f"Ruling planet: {ruler_name}.")
                text = "\n\n".join(parts)

            results.append(RuleResult(
                title_vi=house_name if lang == "vi" else "",
                title_en=house_name if lang == "en" else "",
                text_vi=text if lang == "vi" else "",
                text_en=text if lang == "en" else "",
                score=5.0,
                priority=self.priority,
                category="house_cusp",
                tags=[sign, element_vi, quality_vi, f"house_{h.house_number}"],
                metadata={"house": h.house_number, "sign": sign},
            ))

        return results


RuleRegistry.register(HouseCuspRule())
