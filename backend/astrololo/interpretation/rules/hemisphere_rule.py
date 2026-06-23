from typing import Optional
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.models.chart import ChartData
from astrololo.interpretation.template_loader import _load_yaml


class HemisphereRule(InterpretationRule):
    """Interpret hemisphere emphasis (North/South, East/West)."""

    def __init__(self):
        super().__init__(priority=23)

    def matches(self, chart: ChartData) -> bool:
        planets = [p for p in chart.planets if p.body_type == "planet" and p.house > 0]
        return len(planets) >= 3

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[RuleResult]:
        planets = [p for p in chart.planets if p.body_type == "planet" and p.house > 0]
        total = len(planets)
        if total < 3:
            return None

        north = sum(1 for p in planets if p.house <= 6)
        south = total - north

        east = sum(1 for p in planets if p.house in (1, 2, 3, 10, 11, 12))
        west = total - east

        threshold = int(total * 0.6) + 1

        data = _load_yaml(lang, "hemispheres.yaml")

        lines = []

        if north >= threshold:
            key = "Northern"
        elif south >= threshold:
            key = "Southern"
        else:
            key = "Balanced"

        templ = data.get(key, "") if data else ""
        templ = templ.format(count=max(north, south), total=total,
                             count_north=north, count_south=south,
                             count_east=east, count_west=west)
        if templ:
            lines.append(templ)

        if east >= threshold:
            key2 = "Eastern"
        elif west >= threshold:
            key2 = "Western"
        else:
            key2 = "Balanced"

        templ2 = data.get(key2, "") if data else ""
        templ2 = templ2.format(count=max(east, west), total=total,
                               count_north=north, count_south=south,
                               count_east=east, count_west=west)
        if templ2:
            lines.append(templ2)

        if lang == "vi":
            title = "Phân Bố Bán Cầu"
        else:
            title = "Hemisphere Distribution"

        return RuleResult(
            title_vi=title if lang == "vi" else "",
            title_en=title if lang == "en" else "",
            text_vi="\n\n".join(lines) if lang == "vi" else "",
            text_en="\n\n".join(lines) if lang == "en" else "",
            score=5.0,
            priority=self.priority,
            category="quality",
            tags=["hemisphere", key.lower()],
            metadata={
                "north": north, "south": south,
                "east": east, "west": west, "total": total,
            },
        )


RuleRegistry.register(HemisphereRule())
