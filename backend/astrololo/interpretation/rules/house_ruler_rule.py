from typing import Optional, List
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.models.chart import ChartData
from astrololo.core.constants import PLANETS, SIGNS, HOUSES


_SIGN_RULERS = {
    "aries": "mars", "taurus": "venus", "gemini": "mercury", "cancer": "moon",
    "leo": "sun", "virgo": "mercury", "libra": "venus", "scorpio": "pluto",
    "sagittarius": "jupiter", "capricorn": "saturn", "aquarius": "uranus", "pisces": "neptune",
}


class HouseRulerRule(InterpretationRule):
    """Interpret house rulers - which planet rules each house and where it sits."""

    def __init__(self):
        super().__init__(priority=30)

    def matches(self, chart: ChartData) -> bool:
        return len(chart.houses) > 0

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[List[RuleResult]]:
        planets_by_name = {p.name: p for p in chart.planets}
        results = []

        for house in chart.houses:
            sign = house.sign
            ruler_name = _SIGN_RULERS.get(sign)
            if not ruler_name:
                continue

            ruler_pos = planets_by_name.get(ruler_name)
            if not ruler_pos:
                continue

            s = SIGNS.get(sign)
            h = HOUSES.get(house.house_number)
            ruler_pl = PLANETS.get(ruler_name)
            ruler_house_num = ruler_pos.house

            if lang == "vi":
                sign_vi = s.name_vi if s else sign
                house_vi = h.name_vi if h else f"Nhà {house.house_number}"
                ruler_vi = ruler_pl.name_vi if ruler_pl else ruler_name
                ruler_house_vi = HOUSES.get(ruler_house_num).name_vi if HOUSES.get(ruler_house_num) else f"Nhà {ruler_house_num}"
                title = f"Chủ Nhà {house.house_number} ({house_vi} — {sign_vi})"
                text = (f"Hành tinh chủ của Nhà {house.house_number} ({house_vi}, cung {sign_vi}) là {ruler_vi}. "
                        f"{ruler_vi} tọa lạc tại Nhà {ruler_house_num} ({ruler_house_vi}). "
                        f"Những vấn đề của {house_vi} được thể hiện qua năng lượng của {ruler_house_vi}.")
            else:
                sign_en = s.name_en if s else sign
                house_en = h.name_en if h else f"House {house.house_number}"
                ruler_en = ruler_pl.name_en if ruler_pl else ruler_name
                ruler_house_en = HOUSES.get(ruler_house_num).name_en if HOUSES.get(ruler_house_num) else f"House {ruler_house_num}"
                title = f"Ruler of House {house.house_number} ({house_en} — {sign_en})"
                text = (f"The ruler of House {house.house_number} ({house_en}, sign {sign_en}) is {ruler_en}. "
                        f"{ruler_en} is placed in House {ruler_house_num} ({ruler_house_en}). "
                        f"Matters of {house_en} are expressed through the energy of {ruler_house_en}.")

            results.append(RuleResult(
                title_vi=title if lang == "vi" else "",
                title_en=title if lang == "en" else "",
                text_vi=text if lang == "vi" else "",
                text_en=text if lang == "en" else "",
                score=4.0,
                priority=self.priority,
                category="house_placement",
                planet=ruler_name,
                tags=["house_ruler", sign, ruler_name],
                metadata={
                    "house": house.house_number,
                    "sign": sign,
                    "ruler": ruler_name,
                    "ruler_house": ruler_house_num,
                },
            ))

        return results if results else None


RuleRegistry.register(HouseRulerRule())
