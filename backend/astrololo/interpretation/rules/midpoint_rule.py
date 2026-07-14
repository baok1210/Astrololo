from typing import Optional, List
from astrololo.models.chart import ChartData
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.core.constants import SIGNS
from astrololo.interpretation.keywords import get_sign_keywords


_KEY_MIDPOINTS = {
    ("sun", "moon"): ("Sun/Moon", "bản ngã/cảm xúc — ý thức/tiềm thức", "ego/emotion — conscious/subconscious"),
    ("ascendant", "mc"): ("ASC/MC", "bản thân/sự nghiệp — cách bạn xuất hiện/vị thế xã hội", "self/career — how you appear/social standing"),
    ("sun", "ascendant"): ("Sun/ASC", "bản ngã/bản thân — căn tính/lối thể hiện", "ego/self — identity/outward expression"),
    ("moon", "ascendant"): ("Moon/ASC", "cảm xúc/bản thân — nhu cầu tình cảm/cách thể hiện", "emotion/self — emotional needs/outward style"),
    ("sun", "mc"): ("Sun/MC", "bản ngã/sự nghiệp — căn tính/con đường công danh", "ego/career — identity/public path"),
    ("moon", "mc"): ("Moon/MC", "cảm xúc/sự nghiệp — nhu cầu tình cảm/khát vọng xã hội", "emotion/career — emotional needs/public ambition"),
    ("venus", "mars"): ("Venus/Mars", "tình yêu/đam mê — hài hòa/xung lực", "love/passion — harmony/drive"),
    ("sun", "saturn"): ("Sun/Saturn", "bản ngã/trách nhiệm — thành tựu/thử thách", "ego/responsibility — achievement/challenge"),
    ("moon", "saturn"): ("Moon/Saturn", "cảm xúc/kỷ luật — an toàn/trách nhiệm", "emotion/discipline — security/duty"),
}


class MidpointRule(InterpretationRule):
    priority = 12

    def __init__(self):
        super().__init__(priority=12)

    def matches(self, chart: ChartData) -> bool:
        return len(chart.midpoints) > 0

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[List[RuleResult]]:
        if not chart.midpoints:
            return None

        items = []
        seen = set()
        for mp in chart.midpoints:
            k1 = (mp.body1, mp.body2)
            k2 = (mp.body2, mp.body1)
            match = _KEY_MIDPOINTS.get(k1) or _KEY_MIDPOINTS.get(k2)
            if match and match[0] not in seen:
                seen.add(match[0])
                label, desc_vi, desc_en = match
                sign_key = mp.sign
                s = SIGNS.get(sign_key)
                sign_vi = s.name_vi if s else sign_key
                sign_en = s.name_en if s else sign_key
                sign_data = get_sign_keywords(sign_key) or {}
                core_kw = sign_data.get("core", [])
                core_sample = "; ".join(core_kw[:3]) if core_kw else ""

                if lang == "vi":
                    title = f"Trung Điểm {label}"
                    text = (
                        f"{mp.body1}/{mp.body2} tại {mp.position_in_sign:.2f}° {sign_vi}. "
                        f"Trung điểm này đại diện cho sự kết hợp giữa {desc_vi}. "
                    )
                    if core_sample:
                        text += (
                            f"Nằm ở cung {sign_vi}, trung điểm này mang màu sắc của "
                            f"sự {core_sample}."
                        )
                    text += (
                        " Đây là điểm nhạy cảm trong lá số — khi có hành tinh quá cảnh "
                        "kích hoạt điểm này, bạn sẽ cảm nhận rõ rệt sự kiện liên quan "
                        "đến chủ đề này."
                    )
                else:
                    title = f"Midpoint {label}"
                    text = (
                        f"{mp.body1}/{mp.body2} at {mp.position_in_sign:.2f}° {sign_en}. "
                        f"This midpoint represents the blend of {desc_en}. "
                    )
                    if core_sample:
                        text += (
                            f"Falling in {sign_en}, this midpoint is colored by "
                            f"{core_sample}."
                        )
                    text += (
                        " This is a sensitive point — when transiting planets activate it, "
                        "you will feel events related to this theme strongly."
                    )

                items.append(RuleResult(
                    title_vi=title if lang == "vi" else "",
                    title_en=title if lang == "en" else "",
                    text_vi=text if lang == "vi" else "",
                    text_en=text if lang == "en" else "",
                    score=50,
                    priority=12,
                    category="midpoints",
                    tags=["midpoint", label],
                    metadata={"body1": mp.body1, "body2": mp.body2,
                              "midpoint": mp.midpoint, "sign": mp.sign,
                              "position_in_sign": mp.position_in_sign},
                ))
        return items if items else None


RuleRegistry.register(MidpointRule())