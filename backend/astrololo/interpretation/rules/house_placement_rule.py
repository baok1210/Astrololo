from typing import Optional, List
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.models.chart import ChartData
from astrololo.core.constants import (
    SIGN_ORDER, PLANETS, ANGULAR_HOUSES,
    SUCCEDENT_HOUSES,
)
from astrololo.interpretation.keywords import (
    SIGN_NAME_VI, HOUSE_NAME_VI, SIGN_ELEMENT_VI, SIGN_QUALITY_VI,
    SIGN_NATURAL_RULER, get_sign_short_description, get_sign_keywords,
    get_house_keywords, get_planet_function,
)
from astrololo.interpretation.template_loader import get_planet_in_house


def _format_dms(deg: float) -> str:
    d = int(deg)
    m = int(abs(deg - d) * 60)
    return f"{d}\u00b0{m:02d}'"


ANGLE_LABELS = {1: "AC", 4: "IC", 7: "DC", 10: "MC"}
HOUSE_TYPE_VI = {1: "G\u00f3c", 2: "K\u1ebf", 3: "M\u1ee5c"}


class HousePlacementRule(InterpretationRule):
    """House System Placement Table — cusp + planets + meaning per house."""

    def __init__(self):
        super().__init__(priority=18)

    def matches(self, chart: ChartData) -> bool:
        return bool(chart.houses) and len(chart.planets) > 0

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[List[RuleResult]]:
        results = []

        for h in chart.houses:
            hn = h.house_number
            sign = h.sign
            sign_vi = SIGN_NAME_VI.get(sign, sign)
            sign_idx = SIGN_ORDER.index(sign) if sign in SIGN_ORDER else 0
            cusp_pos = h.cusp_degree - sign_idx * 30
            cusp_dms = _format_dms(cusp_pos)

            angle_label = ANGLE_LABELS.get(hn, "")
            element_vi = SIGN_ELEMENT_VI.get(sign, "")
            quality_vi = SIGN_QUALITY_VI.get(sign, "")
            house_type_num = 1 if hn in ANGULAR_HOUSES else 2 if hn in SUCCEDENT_HOUSES else 3
            house_type_vi = HOUSE_TYPE_VI[house_type_num]

            if angle_label:
                title_vi = f"Nh\xe0 {hn}: {cusp_dms} {sign_vi} ({angle_label})"
            else:
                title_vi = f"Nh\xe0 {hn}: {cusp_dms} {sign_vi}"

            planets_in_house = [
                p for p in chart.planets
                if p.house == hn and p.body_type in ("planet", "node")
            ]
            is_empty = len(planets_in_house) == 0

            text_vi = self._build_text(
                hn, sign, sign_vi, element_vi, quality_vi,
                house_type_vi, angle_label, planets_in_house,
                is_empty, lang,
            )

            planet_list = []
            for p in planets_in_house:
                p_sign_idx = SIGN_ORDER.index(p.sign) if p.sign in SIGN_ORDER else 0
                p_pos = p.longitude - p_sign_idx * 30
                p_dms = _format_dms(p_pos)
                planet_list.append({
                    "name": p.name,
                    "name_vi": p.name_vi,
                    "position_dms": p_dms,
                    "position_in_sign": round(p_pos, 2),
                    "sign_vi": p.sign_name_vi,
                    "sign": p.sign,
                    "is_retrograde": p.is_retrograde,
                    "dignity_label": p.dignity_label,
                    "dignity_score": p.dignity_score,
                    "body_type": p.body_type,
                })

            results.append(RuleResult(
                title_vi=title_vi,
                title_en=title_vi,
                text_vi=text_vi,
                text_en=text_vi,
                score=5.0,
                priority=self.priority,
                category="house_placement",
                tags=[
                    sign, element_vi, quality_vi,
                    f"house_{hn}", house_type_vi,
                ],
                metadata={
                    "house": hn,
                    "cusp_degree_dms": cusp_dms,
                    "cusp_sign_vi": sign_vi,
                    "cusp_sign": sign,
                    "element_vi": element_vi,
                    "quality_vi": quality_vi,
                    "angle_label": angle_label,
                    "house_type_vi": house_type_vi,
                    "house_type_num": house_type_num,
                    "planets": planet_list,
                    "is_empty": is_empty,
                },
            ))

        return results

    def _build_text(
        self, hn: int, sign: str, sign_vi: str,
        element_vi: str, quality_vi: str,
        house_type_vi: str, angle_label: str,
        planets_in_house: list, is_empty: bool,
        lang: str,
    ) -> str:
        parts = []

        house_name = HOUSE_NAME_VI.get(hn, f"Nh\xe0 {hn}")
        ruler_key = SIGN_NATURAL_RULER.get(sign, "")
        ruler_name = ""
        if ruler_key:
            p = PLANETS.get(ruler_key)
            ruler_name = p.name_vi if p else ruler_key
        ruler_func = get_planet_function(ruler_key)

        sign_short = get_sign_short_description(sign)
        sign_data = get_sign_keywords(sign)
        pos_kw = sign_data.get("positive", [])
        core_kw = sign_data.get("core", [])

        house_data = get_house_keywords(hn)
        h_desc = house_data.get("description", "")
        h_kw = house_data.get("keywords", [])

        # House cusp meaning
        cusp_parts = []
        if angle_label:
            cusp_parts.append(
                f"\u0110\u1ec9nh {house_name} l\xe0 {sign_vi} ({element_vi} {quality_vi}) — {house_type_vi}."
            )
        else:
            cusp_parts.append(
                f"\u0110\u1ec9nh {house_name} l\xe0 {sign_vi} ({element_vi} {quality_vi}) — {house_type_vi}."
            )
        if sign_short:
            cusp_parts.append(sign_short)
        if pos_kw:
            cusp_parts.append("B\u1ea1n th\u1ec3 hi\u1ec7n: " + "; ".join(pos_kw[:4]) + ".")
        if core_kw:
            cusp_parts.append("\u0110\u1eb7c tr\u01b0ng: " + "; ".join(core_kw[:3]) + ".")
        if h_desc:
            cusp_parts.append(f"Trong l\u0129nh v\u1ef1c n\xe0y, {h_desc.lower()}")
        if h_kw:
            cusp_parts.append("Ph\u01b0\u01a1ng di\u1ec7n: " + "; ".join(h_kw[:4]) + ".")
        if ruler_name:
            ruler_line = f"Ch\u1ee7 tinh: {ruler_name}."
            if ruler_func:
                ruler_line += f" {ruler_func.split('.')[0]}."
            cusp_parts.append(ruler_line)

        parts.append("\n\n".join(cusp_parts))

        # Planets in this house
        if is_empty:
            parts.append("Kh\u00f4ng c\xf3 h\xe0nh tinh n\xe0o t\u1ecda l\u1ea1c \u1edf nh\xe0 n\xe0y.")
        else:
            for p in planets_in_house:
                p_sign_idx = SIGN_ORDER.index(p.sign) if p.sign in SIGN_ORDER else 0
                p_pos = p.longitude - p_sign_idx * 30
                p_dms = _format_dms(p_pos)
                retro = " (Ngh\u1ecbch h\xe0nh)" if p.is_retrograde else ""

                entry = get_planet_in_house(p.name, hn, lang)
                p_func = get_planet_function(p.name)

                if entry and entry.get("detailed"):
                    p_text = entry["detailed"]
                else:
                    p_text_parts = []
                    if lang == "vi":
                        if p_func:
                            p_text_parts.append(p_func.split(".")[0] + ".")
                        hk = get_house_keywords(hn)
                        kw = hk.get("keywords", [])
                        if kw:
                            p_text_parts.append("T\u1eeb kho\xe1: " + "; ".join(kw[:4]) + ".")
                    p_text = "\n\n".join(p_text_parts) if p_text_parts else ""

                if p_text:
                    parts.append(
                        f"{p.name_vi} ({p_dms} {p.sign_name_vi}){retro} \u1edf {house_name}:\n{p_text}"
                    )
                else:
                    parts.append(
                        f"{p.name_vi} ({p_dms} {p.sign_name_vi}){retro} \u1edf {house_name}."
                    )

        return "\n\n".join(parts)


RuleRegistry.register(HousePlacementRule())
