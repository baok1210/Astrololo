from typing import Optional, List
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.models.chart import ChartData
from astrololo.core.constants import PLANETS, HOUSES
from astrololo.interpretation.template_loader import get_planet_in_house
from astrololo.interpretation.keywords import get_house_keywords, get_planet_function


class PlanetInHouseRule(InterpretationRule):
    def __init__(self):
        super().__init__(priority=35)

    def matches(self, chart: ChartData) -> bool:
        return len(chart.planets) > 0

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[List[RuleResult]]:
        results = []

        for p in chart.planets:
            if p.house < 1 or p.house > 12:
                continue
            h = HOUSES[p.house]
            score = h.weight + p.dignity_score

            entry = get_planet_in_house(p.name, p.house, lang)
            p_name_vi = p.name_vi
            p_name_en = PLANETS[p.name].name_en if p.name in PLANETS else p.name
            h_name_vi = h.name_vi if lang == "vi" else h.name_en
            h_name_en = h.name_en

            if entry and entry.get("detailed"):
                text = entry["detailed"]
                title = entry.get("title", f"{p_name_vi if lang == 'vi' else p_name_en} ở {h_name_vi if lang == 'vi' else h_name_en}")
            else:
                if lang == "vi":
                    house_kw = get_house_keywords(p.house)
                    kw_list = house_kw.get("keywords", [])
                    house_desc = house_kw.get("description", "")
                    p_func = get_planet_function(p.name)
                    parts = [f"{p_name_vi} ở {h.name_vi}:"]
                    if house_desc:
                        parts.append(house_desc)
                    if kw_list:
                        parts.append("Từ khoá: " + "; ".join(kw_list[:4]) + ".")
                    if p_func:
                        parts.append(p_func.split(".")[0] + ".")
                    text = "\n\n".join(parts)
                    title = f"{p_name_vi} ở {h.name_vi}"
                else:
                    text = f"{p_name_en} in {h_name_en}: {h.keywords_en[0] if h.keywords_en else ''}. "
                    title = f"{p_name_en} in {h_name_en}"

            results.append(RuleResult(
                title_vi=title if lang == "vi" else "",
                title_en=title if lang == "en" else "",
                text_vi=text if lang == "vi" else "",
                text_en=text if lang == "en" else "",
                score=score,
                priority=self.priority,
                category="planet_in_house",
                planet=p.name,
                tags=[p.name, str(p.house)],
                metadata={"planet": p.name, "house": p.house, "score": score},
            ))

        return results if results else None


RuleRegistry.register(PlanetInHouseRule())
