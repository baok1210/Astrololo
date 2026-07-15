"""Moon-in-sign deep prose rule (fills A2 gap from the reference report).

Reuses the planet_in_sign corpus for the Moon specifically, producing a
long-form VI/EN interpretation like the MystechX "Mặt Trăng" section.
"""
from typing import Optional, List
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.models.chart import ChartData
from astrololo.interpretation.template_loader import (
    get_planet_in_sign,
)
import logging

logger = logging.getLogger(__name__)


class MoonSignRule(InterpretationRule):
    def __init__(self):
        super().__init__(priority=4)  # near ascendant/mc, top of synthesis

    def matches(self, chart: ChartData) -> bool:
        return any(p.name == "moon" for p in chart.planets)

    def interpret(self, chart: ChartData, lang: str = "vi", **kwargs) -> List[RuleResult]:
        moon = next((p for p in chart.planets if p.name == "moon"), None)
        if not moon:
            return []
        entry = get_planet_in_sign(moon.name, moon.sign, lang=lang)
        if not entry:
            return []
        title_vi = "Mặt Trăng — Cảm Xúc & Nội Tâm"
        title_en = "Moon — Emotions & Inner World"
        text = entry.get("text") or entry.get("short") or ""
        if not text:
            return []
        return [RuleResult(
            title_vi=title_vi,
            title_en=title_en,
            text_vi=text if lang == "vi" else "",
            text_en=text if lang == "en" else "",
            score=self.priority,
            tags=["moon", "planet_in_sign"],
            category="moon_sign",
            metadata={"sign": moon.sign},
        )]

RuleRegistry.register(MoonSignRule())
