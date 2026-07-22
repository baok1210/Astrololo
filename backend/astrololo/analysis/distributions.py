"""Shared post-processing for transit/progression/solar-return charts."""
from typing import List, Dict, Optional

from astrololo.models.chart import (
    ChartData, BodyPosition,
    ElementDistribution, QualityDistribution, DispositorResult,
)
from astrololo.core.constants import PLANETS, SIGNS, SIGN_RULERS, SIGN_MODERN_RULERS


def fill_derived(chart: ChartData) -> None:
    physical: List[BodyPosition] = [p for p in (chart.planets or []) if p.body_type == "planet"]

    fire = earth = air = water = 0
    for p in physical:
        element = p.element or (PLANETS.get(p.name) or {}).element or ""
        if element == "fire":
            fire += 1
        elif element == "earth":
            earth += 1
        elif element == "air":
            air += 1
        elif element == "water":
            water += 1
    elem_counts = {"fire": fire, "earth": earth, "air": air, "water": water}
    dom_elem = max(elem_counts, key=elem_counts.get) if max(elem_counts.values()) > 0 else None
    def_elem = min(elem_counts, key=elem_counts.get) if max(elem_counts.values()) > 0 else None
    chart.element_distribution = ElementDistribution(
        fire=fire, earth=earth, air=air, water=water,
        dominant=dom_elem, deficient=def_elem,
    )

    cardinal = fixed = mutable = 0
    for p in physical:
        quality = p.quality or (PLANETS.get(p.name) or {}).quality or ""
        if quality == "cardinal":
            cardinal += 1
        elif quality == "fixed":
            fixed += 1
        elif quality == "mutable":
            mutable += 1
    chart.quality_distribution = QualityDistribution(
        cardinal=cardinal, fixed=fixed, mutable=mutable,
        dominant=max({"cardinal": cardinal, "fixed": fixed, "mutable": mutable},
                     key=lambda k: {"cardinal": cardinal, "fixed": fixed, "mutable": mutable}[k])
        if max(cardinal, fixed, mutable) > 0 else None,
    )

    chain: Dict[str, str] = {p.name: SIGN_RULERS.get(p.sign, "") for p in physical}
    planet_signs: Dict[str, str] = {p.name: p.sign for p in physical}
    final_dispositors = [
        pn for pn, r in chain.items()
        if r == pn or SIGN_MODERN_RULERS.get(planet_signs[pn]) == pn
    ]
    chart.dispositor = DispositorResult(
        chain=chain,
        final_dispositor=final_dispositors[0] if final_dispositors else None,
        final_dispositors=final_dispositors,
        mutual_receptions=[
            (p1, p2) for p1 in chain for p2 in chain
            if p1 < p2 and chain[p1] == p2 and chain[p2] == p1
        ],
    )

    try:
        from astrololo.scoring.dignity import chart_dignity_scores
        chart.dignity_scores = chart_dignity_scores(chart)
    except Exception:
        chart.dignity_scores = {}

    try:
        from astrololo.scoring.dominant import chart_dominant_scores
        chart.dominant_scores = chart_dominant_scores(chart)
    except Exception:
        chart.dominant_scores = {}
