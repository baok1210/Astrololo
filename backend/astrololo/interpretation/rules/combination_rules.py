from typing import Optional, List
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.models.chart import ChartData
from astrololo.interpretation.template_loader import get_combination


class CombinationRule(InterpretationRule):
    def __init__(self):
        super().__init__(priority=5)

    def matches(self, chart: ChartData) -> bool:
        return len(chart.planets) > 0

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[List[RuleResult]]:
        results = []

        for p in chart.planets:
            entry = get_combination(p.name, p.sign, p.house, lang, chart=chart)
            if entry:
                score = p.dignity_score * 1.5
                results.append(RuleResult(
                    title_vi=entry.get("title", f"{p.name_vi} {p.sign_name_vi} - Nhà {p.house}") if lang == "vi" else "",
                    title_en=entry.get("title_en", f"{p.name} {p.sign} - House {p.house}") if lang == "en" else "",
                    text_vi=entry.get("text", entry.get("vi", "")) if lang == "vi" else "",
                    text_en=entry.get("text_en", entry.get("en", "")) if lang == "en" else "",
                    score=score,
                    priority=self.priority,
                    category="combination",
                    planet=p.name,
                    tags=[p.name, p.sign, str(p.house)],
                    metadata={"planet": p.name, "sign": p.sign, "house": p.house},
                ))

        return results if results else None


RuleRegistry.register(CombinationRule())
