from typing import Optional
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.models.chart import ChartData
from astrololo.interpretation.template_loader import _load_yaml


class MoonPhaseRule(InterpretationRule):
    """Interpret the Moon phase at birth."""

    def __init__(self):
        super().__init__(priority=8)

    def matches(self, chart: ChartData) -> bool:
        return bool(chart.moon_phase) and chart.moon_phase != "Unknown"

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[RuleResult]:
        phase = chart.moon_phase
        if not phase or phase == "Unknown":
            return None

        data = _load_yaml(lang, "moon_phase.yaml")
        text = data.get(phase, "") if data else ""

        if lang == "vi":
            title = f"Tuần Trăng: {phase}"
        else:
            title = f"Moon Phase: {phase}"

        return RuleResult(
            title_vi=title if lang == "vi" else "",
            title_en=title if lang == "en" else "",
            text_vi=text if lang == "vi" else "",
            text_en=text if lang == "en" else "",
            score=8.0,
            priority=self.priority,
            category="synthesis",
            planet="moon",
            tags=["moon_phase", phase.lower().replace(" ", "_")],
            metadata={"moon_phase": phase},
        )


RuleRegistry.register(MoonPhaseRule())
