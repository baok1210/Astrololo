from typing import Optional
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.models.chart import ChartData
from astrololo.core.constants import SIGNS
from astrololo.interpretation.keywords import (
    get_sign_short_description, get_sign_keywords, SIGN_NAME_VI,
)


class MCSignRule(InterpretationRule):
    """Interpret the MC (Midheaven / Thiên Đỉnh) sign."""

    def __init__(self):
        super().__init__(priority=6)

    def matches(self, chart: ChartData) -> bool:
        return bool(chart.mc_sign)

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[RuleResult]:
        mc_sign = chart.mc_sign
        s = SIGNS.get(mc_sign)
        sign_vi = SIGN_NAME_VI.get(mc_sign, mc_sign)
        sign_en = s.name_en if s else mc_sign

        sign_data = get_sign_keywords(mc_sign)
        pos = sign_data.get("positive", [])
        neg = sign_data.get("negative", [])
        short_desc = get_sign_short_description(mc_sign)

        if lang == "vi":
            parts = [
                f"Thiên Đỉnh (MC) của bạn ở {sign_vi} — định hướng sự nghiệp và vị thế xã hội."
            ]
            if short_desc:
                parts.append(short_desc)
            if pos:
                parts.append(f"Thế mạnh nghề nghiệp: {'; '.join(pos[:4])}.")
            if neg:
                parts.append(f"Lưu ý trong công danh: {'; '.join(neg[:3])}.")
            title = f"MC ở {sign_vi}"
            text = "\n\n".join(parts)
        else:
            parts = [
                f"Your MC (Midheaven) is in {sign_en} — career and public standing."
            ]
            if short_desc:
                parts.append(short_desc)
            if pos:
                parts.append(f"Career strengths: {'; '.join(pos[:4])}.")
            if neg:
                parts.append(f"Career challenges: {'; '.join(neg[:3])}.")
            title = f"MC in {sign_en}"
            text = "\n\n".join(parts)

        return RuleResult(
            title_vi=title if lang == "vi" else "",
            title_en=title if lang == "en" else "",
            text_vi=text if lang == "vi" else "",
            text_en=text if lang == "en" else "",
            score=7.0,
            priority=self.priority,
            category="synthesis",
            planet="mc",
            tags=["mc", mc_sign],
        )


RuleRegistry.register(MCSignRule())
