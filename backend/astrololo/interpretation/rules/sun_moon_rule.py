"""Standalone Sun/Moon combination section — richer than the synthesis pattern."""
from typing import Optional, List
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.interpretation.keywords import (
    get_sign_short_description, get_sign_keywords,
)
from astrololo.models.chart import ChartData
from astrololo.core.constants import SIGNS

_ELEMENT_VI = {"fire": "Lửa", "earth": "Đất", "air": "Khí", "water": "Nước"}
_ELEMENT_EN = {"fire": "Fire", "earth": "Earth", "air": "Air", "water": "Water"}
_QUALITY_VI = {"cardinal": "Thống Lĩnh", "fixed": "Cố Định", "mutable": "Linh Hoạt"}
_QUALITY_EN = {"cardinal": "Cardinal", "fixed": "Fixed", "mutable": "Mutable"}


class SunMoonRule(InterpretationRule):
    """Interprets the Sun-Moon combination as a dedicated section."""

    def __init__(self):
        super().__init__(priority=3)

    def matches(self, chart: ChartData) -> bool:
        return any(b.name == "sun" for b in chart.planets) and any(
            b.name == "moon" for b in chart.planets
        )

    def _body(self, chart, name):
        return next((b for b in chart.planets if b.name == name), None)

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[List[RuleResult]]:
        sun = self._body(chart, "sun")
        moon = self._body(chart, "moon")
        if not sun or not moon:
            return None

        s_sign = sun.sign
        m_sign = moon.sign
        s_name = SIGNS.get(s_sign)
        m_name = SIGNS.get(m_sign)
        s_label = s_name.name_vi if s_name and lang == "vi" else s_name.name_en if s_name else s_sign
        m_label = m_name.name_vi if m_name and lang == "vi" else m_name.name_en if m_name else m_sign

        s_desc = get_sign_short_description(s_sign) or ""
        m_desc = get_sign_short_description(m_sign) or ""
        s_data = get_sign_keywords(s_sign)
        m_data = get_sign_keywords(m_sign)
        s_core = s_data.get("core", [])
        m_core = m_data.get("core", [])
        s_pos = s_data.get("positive", [])
        m_pos = m_data.get("positive", [])
        s_neg = s_data.get("negative", [])
        m_neg = m_data.get("negative", [])

        # Element and quality analysis
        s_elem = s_name.element if s_name else ""
        m_elem = m_name.element if m_name else ""
        s_qual = s_name.quality if s_name else ""
        m_qual = m_name.quality if m_name else ""
        same_elem = s_elem == m_elem
        elem_harmony = (s_elem, m_elem) in [("fire", "air"), ("air", "fire"), ("earth", "water"), ("water", "earth")]

        if lang == "vi":
            elem_labels = _ELEMENT_VI
            qual_labels = _QUALITY_VI
            if s_sign == m_sign:
                core_short = "thống nhất giữa ý thức và cảm xúc"
                harmony_text = "Mặt Trời và Mặt Trăng cùng cung cho thấy sự hòa hợp sâu sắc giữa lý trí và tình cảm."
                challenge_text = "Thách thức lớn nhất: đôi khi khó phân biệt giữa nhu cầu cá nhân và phản ứng cảm xúc."
            elif same_elem:
                core_short = f"{elem_labels.get(s_elem, s_elem)} thuần nhất"
                harmony_text = f"Cả hai cùng nguyên tố {elem_labels.get(s_elem, s_elem)}: năng lượng {elem_labels.get(s_elem, s_elem)} được khuếch đại."
                challenge_text = "Cần chú ý đến sự thiên lệch quá mức về một phía."
            elif elem_harmony:
                core_short = f"{elem_labels.get(s_elem, s_elem)} + {elem_labels.get(m_elem, m_elem)} bổ trợ"
                harmony_text = f"Nguyên tố {elem_labels.get(s_elem, s_elem)} (Mặt Trời) và {elem_labels.get(m_elem, m_elem)} (Mặt Trăng) bổ sung cho nhau."
                challenge_text = ""
            else:
                core_short = f"{elem_labels.get(s_elem, s_elem)} x {elem_labels.get(m_elem, m_elem)} căng thẳng"
                harmony_text = f"Có sự căng thẳng giữa nguyên tố {elem_labels.get(s_elem, s_elem)} và {elem_labels.get(m_elem, m_elem)}."
                challenge_text = "Đây là động lực để bạn phát triển toàn diện, học cách dung hòa các mặt đối lập."

            # Quality interplay
            if s_qual == m_qual:
                qual_text = f"Cả hai cùng nhóm {qual_labels.get(s_qual, s_qual)}, tăng cường phương thức hành động này."
            else:
                qual_text = f"Chất lượng {qual_labels.get(s_qual, s_qual)} (Mặt Trời) khác {qual_labels.get(m_qual, m_qual)} (Mặt Trăng), tạo sự đa dạng trong cách tiếp cận."

            # Synthesis
            s_kw = "; ".join(s_core[:3]) if s_core else ""
            m_kw = "; ".join(m_core[:3]) if m_core else ""
            s_pk = "; ".join(s_pos[:3]) if s_pos else ""
            m_pk = "; ".join(m_pos[:3]) if m_pos else ""
            s_nk = "; ".join(s_neg[:2]) if s_neg else ""
            m_nk = "; ".join(m_neg[:2]) if m_neg else ""

            sun_part = f"Mặt Trời {s_label} ({elem_labels.get(s_elem, '')} {qual_labels.get(s_qual, '')}): {s_desc}. Từ khóa: {s_kw}. Điểm mạnh: {s_pk}."
            moon_part = f"Mặt Trăng {m_label} ({elem_labels.get(m_elem, '')} {qual_labels.get(m_qual, '')}): {m_desc}. Từ khóa: {m_kw}. Điểm mạnh: {m_pk}."

            challenge_part = ""
            if challenge_text:
                challenge_part = challenge_text
                if s_nk and m_nk:
                    challenge_part += f" Lưu ý: Mặt Trời có thể {s_nk}, Mặt Trăng có thể {m_nk}."

            title = f"Mặt Trời {s_label} — Mặt Trăng {m_label}"
        else:
            if s_sign == m_sign:
                core_short = "unified consciousness and emotions"
                harmony_text = "Sun and Moon in the same sign shows deep harmony between your will and feelings."
                challenge_text = "Main challenge: sometimes hard to separate personal needs from emotional reactions."
            elif same_elem:
                core_short = f"pure {s_elem}"
                harmony_text = f"Both in {s_elem}: the {s_elem} element is amplified."
                challenge_text = "Watch for over-identification with one element."
            elif elem_harmony:
                core_short = f"{s_elem} + {m_elem} complementary"
                harmony_text = f"Sun's {s_elem} and Moon's {m_elem} elements complement each other naturally."
                challenge_text = ""
            else:
                core_short = f"{s_elem} vs {m_elem} tension"
                harmony_text = f"Tension exists between {s_elem} (Sun) and {m_elem} (Moon) elements."
                challenge_text = "This tension drives growth by forcing you to integrate opposites."

            qual_text = f"Both share {s_qual} modality, reinforcing this approach." if s_qual == m_qual else f"Modalities differ ({s_qual} Sun, {m_qual} Moon), adding versatility."

            s_kw = "; ".join(s_core[:3]) if s_core else ""
            m_kw = "; ".join(m_core[:3]) if m_core else ""
            s_pk = "; ".join(s_pos[:3]) if s_pos else ""
            m_pk = "; ".join(m_pos[:3]) if m_pos else ""

            sun_part = f"Sun in {s_label} ({s_elem} {s_qual}): {s_desc}. Keywords: {s_kw}. Strengths: {s_pk}."
            moon_part = f"Moon in {m_label} ({m_elem} {m_qual}): {m_desc}. Keywords: {m_kw}. Strengths: {m_pk}."

            challenge_part = ""
            if challenge_text and s_neg and m_neg:
                s_nk = "; ".join(s_neg[:2])
                m_nk = "; ".join(m_neg[:2])
                challenge_part = challenge_text + f" Note: Sun may show {s_nk}, Moon may show {m_nk}."
            elif challenge_text:
                challenge_part = challenge_text

            title = f"Sun in {s_label} — Moon in {m_label}"

        text = f"Bản chất: {core_short} — {harmony_text} {qual_text}\n\nPhân tích:\n- {sun_part}\n- {moon_part}\n\nTổng kết: Bạn có Mặt Trời {s_label} và Mặt Trăng {m_label}, tạo nên sự kết hợp {'hài hòa' if same_elem or elem_harmony else 'năng động'} giữa ý thức và cảm xúc." if lang == "vi" else f"Nature: {core_short} — {harmony_text} {qual_text}\n\nAnalysis:\n- {sun_part}\n- {moon_part}\n\nSummary: Your Sun in {s_label} and Moon in {m_label} create a {'harmonious' if same_elem or elem_harmony else 'dynamic'} interplay between your conscious will and emotional nature."

        if challenge_part:
            text += f"\n\n{challenge_part}"

        return [RuleResult(
            title_vi=title if lang == "vi" else "",
            title_en=title if lang == "en" else "",
            text_vi=text if lang == "vi" else "",
            text_en=text if lang == "en" else "",
            score=8.0,
            priority=self.priority,
            category="sun_moon",
            tags=["sun_moon", s_sign, m_sign, core_short],
            metadata={"pattern": "sun_moon", "sun_sign": s_sign, "moon_sign": m_sign},
        )]


RuleRegistry.register(SunMoonRule())
