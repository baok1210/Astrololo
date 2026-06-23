from typing import Optional
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.models.chart import ChartData
from astrololo.core.constants import get_dignity_label, PLANETS, SIGNS
from astrololo.interpretation.template_loader import get_dignity_text


class DignityRule(InterpretationRule):
    def __init__(self):
        super().__init__(priority=25)

    def matches(self, chart: ChartData) -> bool:
        return len(chart.planets) > 0

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[RuleResult]:
        results = []
        for p in chart.planets:
            dignity = get_dignity_label(p.name, p.sign)
            if dignity == "neutral":
                continue

            template = get_dignity_text(dignity, lang, p.name, p.sign)
            if not template:
                continue

            if lang == "vi":
                text = template.format(planet=p.name_vi, sign=p.sign_name_vi)
            else:
                text = template.format(planet=PLANETS[p.name].name_en, sign=SIGNS[p.sign].name_en)

            results.append(RuleResult(
                title_vi=f"{p.name_vi}: {dignity}" if lang == "vi" else "",
                title_en=f"{PLANETS[p.name].name_en}: {dignity}" if lang == "en" else "",
                text_vi=text if lang == "vi" else "",
                text_en=text if lang == "en" else "",
                score=p.dignity_score,
                priority=self.priority,
                category="dignity",
                planet=p.name,
                tags=[p.name, dignity],
                metadata={"dignity": dignity, "score": p.dignity_score},
            ))

        return results if results else None


RuleRegistry.register(DignityRule())
