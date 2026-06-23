from typing import Optional, List
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.models.chart import ChartData
from astrololo.core.constants import get_dignity_label, PLANETS, SIGNS
from astrololo.interpretation.template_loader import get_dignity_text


class DignityRule(InterpretationRule):
    def __init__(self):
        super().__init__(priority=25)

    def _minor_dignity_text(self, p, lang: str) -> str:
        """Build supplementary text for minor dignities."""
        parts = []
        for md in p.minor_dignities:
            tmpl = get_dignity_text(md, lang, p.name, p.sign)
            if not tmpl:
                continue
            if lang == "vi":
                parts.append(tmpl.format(planet=p.name_vi, sign=p.sign_name_vi))
            else:
                parts.append(tmpl.format(planet=PLANETS[p.name].name_en, sign=SIGNS[p.sign].name_en))
        return "\n\n".join(parts)

    def matches(self, chart: ChartData) -> bool:
        return len(chart.planets) > 0

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[List[RuleResult]]:
        results = []
        for p in chart.planets:
            dignity = get_dignity_label(p.name, p.sign)
            if dignity == "neutral" and not p.minor_dignities:
                continue

            parts = []
            # Primary dignity text
            if dignity != "neutral":
                template = get_dignity_text(dignity, lang, p.name, p.sign)
                if template:
                    if lang == "vi":
                        parts.append(template.format(planet=p.name_vi, sign=p.sign_name_vi))
                    else:
                        parts.append(template.format(planet=PLANETS[p.name].name_en, sign=SIGNS[p.sign].name_en))

            # Minor dignity text
            minor_text = self._minor_dignity_text(p, lang)
            if minor_text:
                parts.append(minor_text)

            if not parts:
                continue

            text = "\n\n".join(parts)
            total_score = p.dignity_score + sum(
                3 if d == "triplicity" else 2 if d == "term" else 1 for d in p.minor_dignities
            )

            results.append(RuleResult(
                title_vi=f"{p.name_vi}: {dignity}" if lang == "vi" else "",
                title_en=f"{PLANETS[p.name].name_en}: {dignity}" if lang == "en" else "",
                text_vi=text if lang == "vi" else "",
                text_en=text if lang == "en" else "",
                score=total_score,
                priority=self.priority,
                category="dignity",
                planet=p.name,
                tags=[p.name, dignity] + p.minor_dignities,
                metadata={"dignity": dignity, "score": total_score, "minor_dignities": p.minor_dignities},
            ))

        return results if results else None


RuleRegistry.register(DignityRule())
