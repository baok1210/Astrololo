from typing import Optional
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.models.chart import ChartData
from astrololo.core.constants import SIGNS
from astrololo.interpretation.keywords import (
    get_sign_short_description, get_sign_keywords, SIGN_NAME_VI, HOUSE_NAME_VI,
)


class PartOfFortuneRule(InterpretationRule):
    """Interpret the Part of Fortune (Phần Tài Lộc)."""

    def __init__(self):
        super().__init__(priority=8)

    def matches(self, chart: ChartData) -> bool:
        return chart.part_of_fortune is not None

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[RuleResult]:
        pof = chart.part_of_fortune
        if not pof:
            return None

        sign = pof["sign"]
        sign_vi = pof.get("sign_vi", SIGN_NAME_VI.get(sign, sign))
        house = pof.get("house", 1)
        house_vi = HOUSE_NAME_VI.get(house, f"Nh\xe0 {house}")
        pos = pof.get("position_in_sign", 0)

        sign_data = get_sign_keywords(sign)
        pos_kw = sign_data.get("positive", [])
        short_desc = get_sign_short_description(sign)
        s = SIGNS.get(sign)
        element = s.element if s else ""

        if lang == "vi":
            title = f"Phần Tài Lộc ở {sign_vi} - Nhà {house}"
            parts = [
                f"Phần Tài Lộc (Part of Fortune) của bạn nằm ở {sign_vi}, Nhà {house} ({house_vi})."
            ]
            if short_desc:
                parts.append(f"Cung {sign_vi} ({element}): {short_desc}")
            if pos_kw:
                parts.append(f"Con đường may mắn: {'; '.join(pos_kw[:4])}.")
            parts.append(
                f"Lĩnh vực nhà {house} ({house_vi}) là nơi bạn dễ tìm thấy "
                f"niềm vui, sự thịnh vượng và dòng chảy tự nhiên nhất."
            )
            text = "\n\n".join(parts)
        else:
            s_en = s.name_en if s else sign
            title = f"Part of Fortune in {s_en} - House {house}"
            parts = [
                f"Your Part of Fortune is in {s_en}, House {house} ({house_vi})."
            ]
            if short_desc:
                parts.append(short_desc)
            if pos_kw:
                parts.append(f"Path of fortune: {'; '.join(pos_kw[:4])}.")
            parts.append(
                f"House {house} ({house_vi}) is where you naturally find "
                f"joy, abundance, and effortless flow."
            )
            text = "\n\n".join(parts)

        return RuleResult(
            title_vi=title if lang == "vi" else "",
            title_en=title if lang == "en" else "",
            text_vi=text if lang == "vi" else "",
            text_en=text if lang == "en" else "",
            score=6.0,
            priority=self.priority,
            category="part_of_fortune",
            tags=["part_of_fortune", sign, str(house)],
            metadata={
                "longitude": pof.get("longitude"),
                "sign": sign,
                "sign_vi": sign_vi,
                "house": house,
                "position_in_sign": pos,
            },
        )


RuleRegistry.register(PartOfFortuneRule())
