"""Dominant planet weighted scoring.

Spec 010 §3: Dominant Planet Algorithm.
Weights: essential=0.5, accidental=0.3, aspect_density=0.3.
Body class weights: classical=1.0, outer=0.85, asteroids/lilith=0.5.
"""
from typing import Dict
from astrololo.scoring.dignity import calc_essential, calc_accidental
from astrololo.core.constants import PLANETS


_BODY_CLASS_WEIGHT = {
    "sun": 1.0, "moon": 1.0,
    "mercury": 1.0, "venus": 1.0, "mars": 1.0,
    "jupiter": 1.0, "saturn": 1.0,
    "uranus": 0.85, "neptune": 0.85, "pluto": 0.85,
    "north_node": 0.85, "south_node": 0.85,
    "chiron": 0.5, "ceres": 0.5, "pallas": 0.5,
    "juno": 0.5, "vesta": 0.5, "lilith": 0.5,
}


def _body_weight(name: str) -> float:
    return _BODY_CLASS_WEIGHT.get(name, 1.0)


def calc_dominant_score(
    planet_name: str,
    essential: int,
    accidental: int,
    aspect_density: float,
) -> float:
    raw = (0.5 * essential) + (0.3 * accidental) + (0.3 * aspect_density * 10)
    return round(raw * _body_weight(planet_name), 2)


def chart_dominant_scores(chart) -> Dict[str, float]:
    if not hasattr(chart, "dignity_scores") or not chart.dignity_scores:
        return {}

    sun = next((p for p in chart.planets if p.body_type == "planet" and p.name == "sun"), None)
    sun_lon = sun.longitude if sun else 0.0
    total_planets = len([p for p in chart.planets if p.body_type == "planet"])

    aspect_counts: Dict[str, int] = {}
    for a in chart.aspects:
        aspect_counts[a.planet1] = aspect_counts.get(a.planet1, 0) + 1
        aspect_counts[a.planet2] = aspect_counts.get(a.planet2, 0) + 1

    out: Dict[str, float] = {}
    for p in chart.planets:
        if p.body_type != "planet":
            continue
        ess = calc_essential(p.name, p.sign, degree=p.position_in_sign, is_daytime=getattr(chart, "is_daytime", True))
        acc = calc_accidental(p.name, p.house, p.is_retrograde, p.longitude, sun_lon)
        aspect_density = aspect_counts.get(p.name, 0) / max(total_planets - 1, 1)
        out[p.name] = calc_dominant_score(p.name, ess, acc, aspect_density)
    return out
