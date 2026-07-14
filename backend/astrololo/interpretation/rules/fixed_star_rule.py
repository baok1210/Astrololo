from typing import Optional, List
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.models.chart import ChartData
from astrololo.interpretation.template_loader import get_fixed_star_conjunction


class FixedStarRule(InterpretationRule):
    def __init__(self):
        super().__init__(priority=28)

    def matches(self, chart: ChartData) -> bool:
        return len(chart.fixed_stars) > 0 and len(chart.planets) > 0

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[List[RuleResult]]:
        results = []
        for star in chart.fixed_stars:
            star_lon = star["longitude"]
            star_orb = star.get("orb", 2.0)
            for p in chart.planets:
                if p.body_type == "fixed_star":
                    continue
                diff = abs(p.longitude - star_lon)
                if diff > 180:
                    diff = 360 - diff
                if diff <= star_orb:
                    entry = get_fixed_star_conjunction(star["name"], p.name, lang)
                    if entry:
                        text = entry.get("detailed", "")
                        title = entry.get("title", "")
                        if not title:
                            if lang == "vi":
                                title = f"{star['name_vi']} ({star['sign']}) hợp {p.name_vi}"
                            else:
                                title = f"{star['name_en']} ({star['sign']}) conjunct {p.name_en}"
                        results.append(RuleResult(
                            title_vi=title if lang == "vi" else "",
                            title_en=title if lang == "en" else "",
                            text_vi=text if lang == "vi" else "",
                            text_en=text if lang == "en" else "",
                            score=1,
                            priority=self.priority,
                            category="fixed_stars",
                            planet=p.name,
                            tags=[star["name"], p.name, "conjunction"],
                            metadata={
                                "star": star["name"],
                                "star_name_vi": star["name_vi"],
                                "star_name_en": star["name_en"],
                                "planet": p.name,
                                "orb": round(diff, 2),
                                "sign": star["sign"],
                                "magnitude": star["magnitude"],
                                "nature": star.get("nature", "neutral"),
                            },
                        ))
            if not results:
                pass
        if not results:
            for star in chart.fixed_stars[:5]:
                if lang == "vi":
                    title = f"{star['name_vi']} ({star['sign']})"
                    meaning = star.get("meaning_vi", "")
                else:
                    title = f"{star['name_en']} ({star['sign']})"
                    meaning = star.get("meaning_en", "")
                results.append(RuleResult(
                    title_vi=title if lang == "vi" else "",
                    title_en=title if lang == "en" else "",
                    text_vi=meaning if lang == "vi" else "",
                    text_en=meaning if lang == "en" else "",
                    score=0,
                    priority=self.priority,
                    category="fixed_stars",
                    tags=[star["name"]],
                    metadata={
                        "star": star["name"],
                        "star_name_vi": star["name_vi"],
                        "star_name_en": star["name_en"],
                        "sign": star["sign"],
                        "magnitude": star["magnitude"],
                        "nature": star.get("nature", "neutral"),
                    },
                ))
        return results if results else None


RuleRegistry.register(FixedStarRule())
