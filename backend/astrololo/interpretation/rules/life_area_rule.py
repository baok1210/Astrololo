"""Life-area report rule: emits the 14 scored life areas (tra-cuu-ban-do-sao-1).

Reads scores from analysis.life_areas and produces one section per the
MystechX structure (B6-B19). Prose is assembled from the planet-in-house
corpus for the area's seed planet, plus the computed score + label.
"""
from typing import Optional, List
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.models.chart import ChartData
from astrololo.analysis.life_areas import calculate_life_areas
from astrololo.interpretation.template_loader import (
    get_planet_in_house,
)
import logging

logger = logging.getLogger(__name__)


class LifeAreaRule(InterpretationRule):
    def __init__(self):
        super().__init__(priority=25)  # after core placements, before encyclopedia

    def matches(self, chart: ChartData) -> bool:
        return bool(chart.planets)

    def interpret(self, chart: ChartData, lang: str = "vi", **kwargs) -> List[RuleResult]:
        areas = calculate_life_areas(chart)
        results: List[RuleResult] = []
        for a in areas:
            # prose from corpus: seed planet placed in the area's first house
            prose = ""
            seed = a.get("key")
            # map area->seed planet for corpus lookup
            from astrololo.analysis.life_areas import _AREAS
            seed_planet = next((s for s in _AREAS[seed]["seed"] if s not in ("ascendant", "mc", "ic", "descendant")), None)
            house = _AREAS[seed]["houses"][0]
            if seed_planet:
                raw = get_planet_in_house(seed_planet, house, lang=lang)
                if raw and len(raw) > 120:
                    prose = raw[:600]
            if not prose:
                prose = (f"Lĩnh vực {a['title_vi']} được hình thành từ các hành tinh "
                         f"tác động vào nhà {_AREAS[seed]['houses'][0]} của bản đồ.")
            title = f"{a['title_vi']} — {a['score']}/100 ({a['label_vi']})" if lang == "vi" \
                else f"{a['title_en']} — {a['score']}/100 ({a['label_en']})"
            text = prose
            results.append(RuleResult(
                title_vi=title if lang == "vi" else "",
                title_en=title if lang == "en" else "",
                text_vi=text if lang == "vi" else "",
                text_en=text if lang == "en" else "",
                score=self.priority,
                tags=["life_area", seed],
                category="life_area",
                metadata={"score": a["score"], "label_vi": a["label_vi"], "label_en": a["label_en"]},
            ))
        return results

RuleRegistry.register(LifeAreaRule())
