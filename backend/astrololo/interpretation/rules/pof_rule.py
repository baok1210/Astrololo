from typing import Optional
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.models.chart import ChartData
from astrololo.core.constants import SIGNS
from astrololo.interpretation.keywords import (
    get_sign_short_description, get_sign_keywords, SIGN_NAME_VI, HOUSE_NAME_VI, get_house_keywords,
)


class PartOfFortuneRule(InterpretationRule):
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
        s = SIGNS.get(sign)
        element = s.element if s else ""
        quality = s.quality if s else ""
        sign_data = get_sign_keywords(sign)
        pos_kw = sign_data.get("positive", [])
        short_desc = get_sign_short_description(sign)
        h_data = get_house_keywords(house)
        h_desc = h_data.get("description", "")
        h_kw = h_data.get("keywords", [])
        h_title = h_data.get("title", house_vi)

        if lang == "vi":
            title = f"Phần Tài Lộc ở {sign_vi} - Nhà {house}"
            parts = [
                f"Phần Tài Lộc (Part of Fortune) của bạn nằm ở {sign_vi}, Nhà {house} ({h_title}). "
                f"Đây là điểm 'kho báu' trong lá số — nơi năng lượng chảy tự nhiên và dễ dàng nhất, "
                f"mang đến may mắn, niềm vui và sự thịnh vượng khi bạn sống đúng với bản chất của mình."
            ]
            if short_desc:
                parts.append(
                    f"Cung {sign_vi} thuộc nhóm {element} ({quality}): {short_desc}"
                )
            if pos_kw:
                parts.append(
                    f"Con đường dẫn đến may mắn của bạn: {'; '.join(pos_kw[:5])}. "
                    f"Đây là những phẩm chất bạn cần phát huy để thu hút năng lượng tích cực "
                    f"và cơ hội vào cuộc sống."
                )
            if h_desc:
                parts.append(
                    f"Lĩnh vực Nhà {house} ({h_title}): {h_desc}"
                )
            if h_kw:
                parts.append(
                    f"Từ khoá cho lĩnh vực này: {'; '.join(h_kw[:5])}. "
                    f"Đây là nơi bạn có thể tìm thấy sự viên mãn và thành công tự nhiên nhất."
                )
            parts.append(
                f"Lời khuyên: Khi cảm thấy lạc lối hoặc mất phương hướng, hãy nhìn vào "
                f"Phần Tài Lộc của bạn. Sống theo năng lượng của cung {sign_vi} và "
                f"tập trung vào lĩnh vực nhà {house} — đó là con đường dẫn đến hạnh phúc "
                f"và thịnh vượng đích thực của bạn."
            )
            text = "\n\n".join(parts)
        else:
            s_en = s.name_en if s else sign
            title = f"Part of Fortune in {s_en} - House {house}"
            parts = [
                f"Your Part of Fortune is in {s_en}, House {house} ({h_title}). "
                f"This is the 'treasure map' point in your chart — where energy flows naturally, "
                f"bringing luck, joy, and abundance when you live in alignment with your true nature."
            ]
            if short_desc:
                parts.append(f"The {quality} {element} sign {s_en}: {short_desc}")
            if pos_kw:
                parts.append(
                    f"Your path to fortune: {'; '.join(pos_kw[:5])}. "
                    f"These are qualities to cultivate to attract positive energy and opportunities."
                )
            if h_desc:
                parts.append(f"House {house} ({h_title}): {h_desc}")
            if h_kw:
                parts.append(
                    f"Keywords for this life area: {'; '.join(h_kw[:5])}. "
                    f"This is where you naturally find fulfillment and success."
                )
            parts.append(
                f"Guidance: When feeling lost, look to your Part of Fortune. "
                f"Live the energy of {s_en} and focus on the themes of House {house} — "
                f"that is your path to genuine happiness and prosperity."
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
                "position_in_sign": pof.get("position_in_sign"),
            },
        )


RuleRegistry.register(PartOfFortuneRule())