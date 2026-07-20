from typing import Optional, List
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.models.chart import ChartData
from astrololo.core.constants import PLANETS, SIGNS, get_dignity_label
from astrololo.interpretation.template_loader import get_planet_in_sign


class PlanetInSignRule(InterpretationRule):
    def __init__(self):
        super().__init__(priority=30)

    def matches(self, chart: ChartData) -> bool:
        return len(chart.planets) > 0

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[List[RuleResult]]:
        results = []
        for p in chart.planets:
            dignity = get_dignity_label(p.name, p.sign)
            entry = get_planet_in_sign(p.name, p.sign, lang)
            if not entry:
                continue

            text = entry.get("detailed", "")
            title = entry.get("title", "")
            if not title:
                p_name = p.name_vi if lang == "vi" else (PLANETS[p.name].name_en if p.name in PLANETS else p.name)
                s_name = p.sign_name_vi if lang == "vi" else SIGNS[p.sign].name_en
                title = f"{p_name} ở {s_name}"
                if dignity != "neutral":
                    title += f" ({dignity})"

            s_name_vi = p.sign_name_vi if lang == "vi" else SIGNS[p.sign].name_en
            ev = [f"{p.name_vi if lang=='vi' else p.name_en} ở {s_name_vi}",
                  f"Nhà {p.house}" if lang == "vi" else f"House {p.house}",
                  f"Độ {p.position_in_sign:.1f}° trong cung" if lang == "vi" else f"{p.position_in_sign:.1f}° into sign"]
            if dignity != "neutral":
                ev.append(f"Dignity: {dignity}")
            if getattr(p, "definition_note", None):
                ev.append(p.definition_note)
            results.append(RuleResult(
                title_vi=title if lang == "vi" else "",
                title_en=title if lang == "en" else "",
                text_vi=text if lang == "vi" else "",
                text_en=text if lang == "en" else "",
                score=p.dignity_score,
                priority=self.priority,
                category="planet_in_sign",
                planet=p.name,
                tags=[p.name, p.sign, dignity],
                evidence=ev,
                metadata={
                    "planet": p.name,
                    "sign": p.sign,
                    "dignity": dignity,
                    "house": p.house,
                    "position": p.position_in_sign,
                },
            ))
        return results if results else None


RuleRegistry.register(PlanetInSignRule())
