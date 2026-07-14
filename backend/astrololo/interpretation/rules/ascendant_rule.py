from typing import Optional
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.models.chart import ChartData
from astrololo.core.constants import SIGNS
from astrololo.interpretation.keywords import (
    get_sign_short_description, get_sign_keywords, SIGN_NAME_VI,
)
from astrololo.interpretation.template_loader import get_ascendant_entry


class AscendantSignRule(InterpretationRule):
    def __init__(self):
        super().__init__(priority=5)

    def matches(self, chart: ChartData) -> bool:
        return bool(chart.ascendant_sign)

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[RuleResult]:
        asc_sign = chart.ascendant_sign

        if lang == "en":
            entry = get_ascendant_entry(asc_sign, "en")
            if entry:
                s = SIGNS.get(asc_sign)
                sign_en = s.name_en if s else asc_sign
                return RuleResult(
                    title_vi="",
                    title_en=entry.get("title", f"Ascendant in {sign_en}"),
                    text_vi="",
                    text_en=entry.get("detailed", entry.get("short", "")),
                    score=8.0,
                    priority=self.priority,
                    category="synthesis",
                    planet="ascendant",
                    tags=["ascendant", asc_sign],
                )

        s = SIGNS.get(asc_sign)
        sign_vi = SIGN_NAME_VI.get(asc_sign, asc_sign)
        sign_data = get_sign_keywords(asc_sign)
        pos = sign_data.get("positive", [])
        neg = sign_data.get("negative", [])
        behavior = sign_data.get("behavior", sign_data.get("core", []))
        short_desc = get_sign_short_description(asc_sign)
        element = s.element if s else ""
        quality = s.quality if s else ""

        if lang == "vi":
            parts = [
                f"Cung Mọc (Ascendant) của bạn là {sign_vi} — "
                f"một cung {element} thuộc nhóm {quality}. "
                f"Đây là 'chiếc mặt nạ' bạn đeo khi ra ngoài xã hội, "
                f"ấn tượng đầu tiên bạn để lại cho người khác."
            ]
            if short_desc:
                parts.append(short_desc)
            if behavior:
                parts.append(
                    f"Năng lượng bạn toát ra: {'; '.join(behavior[:4])}. "
                    f"Đây là cách người khác thường nhìn nhận về bạn ban đầu."
                )
            if pos:
                parts.append(
                    f"Điểm mạnh bẩm sinh của Cung Mọc này: {'; '.join(pos[:4])}. "
                    f"Đây là những phẩm chất tự nhiên giúp bạn gây ấn tượng tốt và "
                    f"tạo thiện cảm với người đối diện."
                )
            if neg:
                parts.append(
                    f"Thách thức tính cách cần cân bằng: {'; '.join(neg[:3])}. "
                    f"Nhận diện những điểm này giúp bạn điều chỉnh lối thể hiện bản thân "
                    f"để trở nên hài hòa và hiệu quả hơn trong giao tiếp."
                )
            parts.append(
                f"Cung Mọc {sign_vi} là cửa ngõ đầu tiên giữa bạn và thế giới — "
                f"khi bạn ý thức và phát triển năng lượng này, bạn sẽ tự nhiên thu hút "
                f"những con người và cơ hội phù hợp với con đường phát triển của mình."
            )
            title = f"Cung Mọc {sign_vi}"
            text = "\n\n".join(parts)
        else:
            sign_en = s.name_en if s else asc_sign
            parts = [
                f"Your Ascendant is {sign_en} — a {quality} {element} sign. "
                f"This is the 'mask' you wear when you step out into the world, "
                f"the first impression you leave on others."
            ]
            if short_desc:
                parts.append(short_desc)
            if behavior:
                parts.append(
                    f"You project: {'; '.join(behavior[:4])}. "
                    f"This is how people typically perceive you at first."
                )
            if pos:
                parts.append(
                    f"Natural strengths: {'; '.join(pos[:4])}. "
                    f"These qualities help you make a positive impression."
                )
            if neg:
                parts.append(
                    f"Growth areas: {'; '.join(neg[:3])}. "
                    f"Being aware of these helps you adjust how you present yourself."
                )
            parts.append(
                f"Your {sign_en} Ascendant is the gateway between you and the world — "
                f"when you consciously develop this energy, you naturally attract "
                f"the right people and opportunities on your path."
            )
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