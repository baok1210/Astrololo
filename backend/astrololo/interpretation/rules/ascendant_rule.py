from typing import Optional
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.models.chart import ChartData
from astrololo.core.constants import SIGNS
from astrololo.interpretation.keywords import (
    get_sign_short_description, get_sign_keywords, SIGN_NAME_VI,
)


class AscendantSignRule(InterpretationRule):
    """Interpret the Ascendant (Cung Mọc) sign."""

    def __init__(self):
        super().__init__(priority=5)

    def matches(self, chart: ChartData) -> bool:
        return bool(chart.ascendant_sign)

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[RuleResult]:
        asc_sign = chart.ascendant_sign
        s = SIGNS.get(asc_sign)
        sign_vi = SIGN_NAME_VI.get(asc_sign, asc_sign)
        sign_en = s.name_en if s else asc_sign

        sign_data = get_sign_keywords(asc_sign)
        pos = sign_data.get("positive", [])
        neg = sign_data.get("negative", [])
        behavior = sign_data.get("behavior", sign_data.get("core", []))
        short_desc = get_sign_short_description(asc_sign)
        element = s.element if s else ""
        quality = s.quality if s else ""

        if lang == "vi":
            parts = [
                f"Cung Mọc của bạn là {sign_vi} — cung {element} thuộc nhóm {quality}."
            ]
            if short_desc:
                parts.append(short_desc)
            if behavior:
                parts.append(f"Bạn toát ra năng lượng: {'; '.join(behavior[:4])}.")
            if pos:
                parts.append(f"Điểm mạnh bẩm sinh: {'; '.join(pos[:4])}.")
            if neg:
                parts.append(f"Thách thức tính cách: {'; '.join(neg[:3])}.")
            title = f"Cung Mọc {sign_vi}"
            text = "\n\n".join(parts)
        else:
            parts = [
                f"Your Ascendant is {sign_en} — a {quality} {element} sign."
            ]
            if short_desc:
                parts.append(short_desc)
            if behavior:
                parts.append(f"You project: {'; '.join(behavior[:4])}.")
            if pos:
                parts.append(f"Natural strengths: {'; '.join(pos[:4])}.")
            if neg:
                parts.append(f"Growth areas: {'; '.join(neg[:3])}.")
            title = f"Ascendant in {sign_en}"
            text = "\n\n".join(parts)

        return RuleResult(
            title_vi=title if lang == "vi" else "",
            title_en=title if lang == "en" else "",
            text_vi=text if lang == "vi" else "",
            text_en=text if lang == "en" else "",
            score=8.0,
            priority=self.priority,
            category="synthesis",
            planet="ascendant",
            tags=["ascendant", asc_sign, element, quality],
        )


RuleRegistry.register(AscendantSignRule())
