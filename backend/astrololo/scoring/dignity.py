"""Dignity scoring — essential + accidental.

Spec 010 §2.1. Reuses existing essential-dignity engine in constants.py.
"""
from typing import Optional, Dict
from astrololo.core.constants import (
    get_dignity_score_full,
    PLANETS,
    ANGULAR_HOUSES,
    SUCCEDENT_HOUSES,
    CADENT_HOUSES,
    SIGNS,
)


def _house_type(house: int) -> str:
    if house in ANGULAR_HOUSES:
        return "angular"
    if house in SUCCEDENT_HOUSES:
        return "succedent"
    if house in CADENT_HOUSES:
        return "cadent"
    return ""


def calc_essential(planet_name: str, sign: str, degree: float = 0.0, is_daytime: bool = True) -> int:
    info = get_dignity_score_full(planet_name, sign, degree=degree, is_daytime=is_daytime)
    return int(info.get("score", 0))


def calc_accidental(planet_name: str, house: int, is_retrograde: bool, longitude: float = 0.0, sun_longitude: float = 0.0) -> int:
    score = 0
    htype = _house_type(house)
    if htype == "angular":
        score += 5
    elif htype == "succedent":
        score += 3
    elif htype == "cadent":
        score += 1

    if is_retrograde:
        score -= 5

    # Combustion: within 15° of Sun (excluding cazimi ±17')
    if sun_longitude and longitude:
        from astrololo.core.aspects import angular_distance
        dist = angular_distance(longitude, sun_longitude)
        if dist <= 17/60:          # cazimi
            score += 5
        elif dist <= 15:          # combustion
            score -= 5
    return score


def chart_dignity_scores(chart) -> Dict[str, int]:
    sun = next((p for p in chart.planets if p.name == "sun"), None)
    sun_lon = sun.longitude if sun else 0.0
    out: Dict[str, int] = {}
    for p in chart.planets:
        if p.body_type != "planet":
            continue
        ess = calc_essential(p.name, p.sign, degree=p.position_in_sign, is_daytime=getattr(chart, "is_daytime", True))
        acc = calc_accidental(p.name, p.house, p.is_retrograde, p.longitude, sun_lon)
        out[p.name] = ess + acc
    return out
