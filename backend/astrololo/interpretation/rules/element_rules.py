from typing import Optional
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.models.chart import ChartData
from astrololo.interpretation.template_loader import get_element_text


class ElementRule(InterpretationRule):
    def __init__(self):
        super().__init__(priority=20)

    def matches(self, chart: ChartData) -> bool:
        return chart.element_distribution is not None

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[RuleResult]:
        if not chart.element_distribution:
            return None

        ed = chart.element_distribution
        total = ed.fire + ed.earth + ed.air + ed.water
        if total == 0:
            return None

        elem_map = {"fire": ed.fire, "earth": ed.earth, "air": ed.air, "water": ed.water}
        dominant = max(elem_map, key=elem_map.get)
        deficient = min(elem_map, key=elem_map.get)

        text = ""
        if ed.dominant:
            t = get_element_text(f"dominant_{dominant}", lang)
            if t:
                text += t
        if ed.deficient:
            t = get_element_text(f"deficient_{deficient}", lang)
            if t:
                text += f"\n\n{t}"

        return RuleResult(
            title_vi="Phân Bố Nguyên Tố" if lang == "vi" else "",
            title_en="Element Distribution" if lang == "en" else "",
            text_vi=text if lang == "vi" else "",
            text_en=text if lang == "en" else "",
            score=int(elem_map[dominant] * 3),
            priority=self.priority,
            category="element",
            tags=[dominant, deficient],
            metadata={
                "distribution": elem_map,
                "dominant": dominant,
                "deficient": deficient,
                "total": total,
            },
        )


RuleRegistry.register(ElementRule())
