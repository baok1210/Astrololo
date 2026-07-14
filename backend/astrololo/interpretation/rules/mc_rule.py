from typing import Optional
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.models.chart import ChartData
from astrololo.core.constants import SIGNS
from astrololo.interpretation.keywords import (
    get_sign_short_description, get_sign_keywords, SIGN_NAME_VI,
)
from astrololo.interpretation.template_loader import get_mc_entry


class MCSignRule(InterpretationRule):
    def __init__(self):
        super().__init__(priority=6)

    def matches(self, chart: ChartData) -> bool:
        return bool(chart.mc_sign)

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[RuleResult]:
        mc_sign = chart.mc_sign

        if lang == "en":
            entry = get_mc_entry(mc_sign, "en")
            if entry:
                s = SIGNS.get(mc_sign)
                sign_en = s.name_en if s else mc_sign
                return RuleResult(
                    title_vi="",
                    title_en=entry.get("title", f"MC in {sign_en}"),
                    text_vi="",
                    text_en=entry.get("detailed", entry.get("short", "")),
                    score=7.0,
                    priority=self.priority,
                    category="synthesis",
                    planet="mc",
                    tags=["mc", mc_sign],
                )

        s = SIGNS.get(mc_sign)
        sign_vi = SIGN_NAME_VI.get(mc_sign, mc_sign)
        sign_data = get_sign_keywords(mc_sign)
        pos = sign_data.get("positive", [])
        neg = sign_data.get("negative", [])
        short_desc = get_sign_short_description(mc_sign)

        if lang == "vi":
            parts = [
                f"Thiên Đỉnh (MC) của bạn ở {sign_vi} — "
                f"điểm cao nhất trên bầu trời lá số, đại diện cho "
                f"sự nghiệp, vị thế xã hội và đóng góp của bạn cho thế giới."
            ]
            if short_desc:
                parts.append(
                    f"Cung {sign_vi} ảnh hưởng đến con đường sự nghiệp: {short_desc}"
                )
            if pos:
                parts.append(
                    f"Thế mạnh nghề nghiệp: {'; '.join(pos[:4])}. "
                    f"Đây là những phẩm chất bạn cần phát huy để đạt được thành công "
                    f"và được công nhận trong sự nghiệp."
                )
            if neg:
                parts.append(
                    f"Lưu ý trong công danh: {'; '.join(neg[:3])}. "
                    f"Nhận diện những thách thức này giúp bạn vượt qua các trở ngại "
                    f"trên con đường sự nghiệp."
                )
            title = f"MC ở {sign_vi}"
            text = "\n\n".join(parts)
        else:
            sign_en = s.name_en if s else mc_sign
            parts = [
                f"Your MC (Midheaven) is in {sign_en} — "
                f"the highest point in the chart, representing "
                f"career, public standing, and your contribution to the world."
            ]
            if short_desc:
                parts.append(
                    f"{sign_en} influences your career path: {short_desc}"
                )
            if pos:
                parts.append(
                    f"Career strengths: {'; '.join(pos[:4])}. "
                    f"These qualities help you find success and recognition."
                )
            if neg:
                parts.append(
                    f"Career challenges: {'; '.join(neg[:3])}. "
                    f"Being aware of these helps you navigate obstacles in your professional path."
                )
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