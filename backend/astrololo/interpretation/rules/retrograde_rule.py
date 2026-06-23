from typing import Optional, List
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.models.chart import ChartData
from astrololo.core.constants import PLANETS


class RetrogradeRule(InterpretationRule):
    """Interpret retrograde planets."""

    def __init__(self):
        super().__init__(priority=20)

    def matches(self, chart: ChartData) -> bool:
        return any(p.is_retrograde for p in chart.planets if p.body_type == "planet")

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[List[RuleResult]]:
        retros = [p for p in chart.planets if p.is_retrograde and p.body_type == "planet"]
        if not retros:
            return None

        ret_tags = [p.name for p in retros]
        names = []
        for p in retros:
            pl = PLANETS.get(p.name)
            n = pl.name_vi if pl and lang == "vi" else pl.name_en if pl else p.name
            names.append(n)

        results = []
        for p in retros:
            pl = PLANETS.get(p.name)
            n = pl.name_vi if pl and lang == "vi" else pl.name_en if pl else p.name
            if lang == "vi":
                title = f"{n} Nghịch Hành"
                text = f"{n} nghịch hành trong lá số của bạn."
            else:
                title = f"{n} Retrograde"
                text = f"{n} is retrograde in your chart."
            results.append(RuleResult(
                title_vi=title if lang == "vi" else "",
                title_en=title if lang == "en" else "",
                text_vi=text if lang == "vi" else "",
                text_en=text if lang == "en" else "",
                score=6.0,
                priority=self.priority,
                category="retrograde",
                planet=p.name,
                tags=["retrograde", p.name],
                metadata={"retrograde_planets": ret_tags},
            ))
        return results


RuleRegistry.register(RetrogradeRule())
