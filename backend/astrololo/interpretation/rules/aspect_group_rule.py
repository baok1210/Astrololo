"""Aspect grouping rule (C20-C22 of the reference report).

Splits the chart's aspects into three interpretable groups:
- prominent: tight-orb or angular (ASC/MC) aspects — "góc hợp ảnh hưởng nổi bật"
- harmonious: trine/sextile — "góc hợp hài hòa"
- challenging: square/opposition/quincunx — "góc hợp thử thách"
"""
from typing import List
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.models.chart import ChartData
import logging

logger = logging.getLogger(__name__)

_ANGULAR = {"ascendant", "mc", "asc", "mc_", "rising"}


def _is_prominent(a) -> bool:
    orb = abs(getattr(a, "orb", 0.0))
    p1, p2 = a.planet1, a.planet2
    angular = any(k in p1.lower() or k in p2.lower() for k in _ANGULAR)
    return orb <= 2.0 or angular


class AspectGroupRule(InterpretationRule):
    def __init__(self):
        super().__init__(priority=22)

    def matches(self, chart: ChartData) -> bool:
        return bool(chart.aspects)

    def interpret(self, chart: ChartData, lang: str = "vi", **kwargs) -> List[RuleResult]:
        prominent, harm, chall = [], [], []
        for a in chart.aspects:
            nature = getattr(a, "nature", "neutral")
            label = f"{a.planet1} {a.aspect_name_vi or a.aspect_type} {a.planet2}"
            if _is_prominent(a):
                prominent.append(label)
            if nature == "harmonious":
                harm.append(label)
            elif nature == "challenging":
                chall.append(label)

        def mk(cat, title_vi, title_en, items):
            text = ("\n".join(f"• {x}" for x in items)) if items else (
                "Không có góc hợp loại này nổi bật trong bản đồ." if lang == "vi"
                else "No prominent aspects of this type in the chart.")
            return RuleResult(
                title_vi=title_vi, title_en=title_en,
                text_vi=text if lang == "vi" else "",
                text_en=text if lang == "en" else "",
                score=self.priority, tags=["aspect_group", cat], category="aspect_group",
                metadata={"count": len(items)},
            )

        return [
            mk("prominent", "Góc Hợp Ảnh Hưởng Nổi Bật", "Prominent Aspects", prominent),
            mk("harmonious", "Góc Hợp Hài Hòa", "Harmonious Aspects", harm),
            mk("challenging", "Góc Hợp Thử Thách", "Challenging Aspects", chall),
        ]

RuleRegistry.register(AspectGroupRule())
