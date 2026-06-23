from typing import Optional, List
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.models.chart import ChartData
from astrololo.core.constants import get_dignity_score
from astrololo.interpretation.template_loader import get_aspect
from astrololo.interpretation.chart_synthesis import enrich_aspect_with_chart


class AspectRule(InterpretationRule):
    def __init__(self):
        super().__init__(priority=40)

    def matches(self, chart: ChartData) -> bool:
        return len(chart.aspects) > 0

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[List[RuleResult]]:
        results = []
        for a in chart.aspects:
            entry = get_aspect(a.planet1, a.planet2, a.aspect_type, lang)
            base_text = entry.get("detailed", "") if entry else ""
            text = enrich_aspect_with_chart(chart, a, base_text, lang)
            title = entry.get("title", "") if entry else ""

            if not title:
                if lang == "vi":
                    title = f"{a.aspect_name_vi}: {a.planet1} - {a.planet2}"
                else:
                    title = f"{a.aspect_type}: {a.planet1} - {a.planet2}"

            score = a.weight + get_dignity_score(a.planet1, "") * 0.5

            results.append(RuleResult(
                title_vi=title if lang == "vi" else "",
                title_en=title if lang == "en" else "",
                text_vi=text if lang == "vi" else "",
                text_en=text if lang == "en" else "",
                score=score,
                priority=self.priority,
                category="aspect",
                aspect=a.aspect_type,
                tags=[a.planet1, a.planet2, a.aspect_type],
                metadata={
                    "planet1": a.planet1,
                    "planet2": a.planet2,
                    "aspect_type": a.aspect_type,
                    "angle": a.angle,
                    "orb": a.orb,
                },
            ))
        return results if results else None


RuleRegistry.register(AspectRule())
