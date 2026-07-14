from typing import Dict, Any, List
from astrololo.models.chart import ChartData, PlanetPosition
from astrololo.core.constants import (
    get_dignity_score,
    HOUSES,
    MINOR_DIGNITY_SCORES,
    PLANET_ORDER,
)

# Body-class weight: classical planets dominate a chart far more than outer
# planets / asteroids. Without this, Pluto/Juno/Vesta rack up aspect+house points
# and wrongly outrank the Sun/Moon in "dominant planet" + chart strength.
# classical (Sun..Pluto) = 1.0, minor asteroids (chiron/ceres/pallas/juno/vesta)
# and lilith = 0.5 (informational, not chart-ruling).
_BODY_WEIGHT = {
    "sun": 1.0, "moon": 1.0, "mercury": 1.0, "venus": 1.0, "mars": 1.0,
    "jupiter": 1.0, "saturn": 1.0, "uranus": 0.8, "neptune": 0.8, "pluto": 0.8,
    "chiron": 0.5, "ceres": 0.5, "pallas": 0.5, "juno": 0.5, "vesta": 0.5,
    "lilith": 0.5,
}


def body_weight(name: str) -> float:
    return _BODY_WEIGHT.get(name, 1.0 if name in PLANET_ORDER else 0.5)


class ChartScorer:
    def __init__(self, chart: ChartData):
        self.chart = chart

    def score_planet(self, planet: PlanetPosition) -> Dict[str, Any]:
        dignity = get_dignity_score(planet.name, planet.sign)
        house_weight = (
            HOUSES.get(planet.house, HOUSES[1]).weight if planet.house >= 1 else 0
        )
        bw = body_weight(planet.name)

        aspect_score = 0
        for a in self.chart.aspects:
            if a.planet1 == planet.name or a.planet2 == planet.name:
                aspect_score += a.weight

        # Essential dignity: planet-in-sign quality + minor dignities (triplicity, term, face)
        minor_bonus = sum(MINOR_DIGNITY_SCORES.get(d, 0) for d in planet.minor_dignities)
        essential = dignity + minor_bonus
        # Accidental dignity: house + aspects + rulership bonuses, scaled by body class
        # so asteroids/Pluto don't outrank the luminaries purely via aspect counts.
        accidental = (house_weight + aspect_score) * bw

        total = essential + accidental

        return {
            "planet": planet.name,
            "dignity": dignity,
            "house_weight": house_weight,
            "aspect_score": aspect_score,
            "essential": essential,
            "accidental": accidental,
            "total": total,
            "label": "very_strong"
            if total >= 10
            else "strong"
            if total >= 5
            else "neutral"
            if total >= 0
            else "weak"
            if total >= -5
            else "very_weak",
        }

    def score_planet_essential(self, planet: PlanetPosition) -> float:
        """Pure essential dignity score (planet by sign, no aspects/house)."""
        return float(get_dignity_score(planet.name, planet.sign))

    def score_planet_accidental(self, planet: PlanetPosition) -> float:
        """Accidental dignity from house placement and rulership bonuses."""
        return float(
            HOUSES.get(planet.house, HOUSES[1]).weight if planet.house >= 1 else 0
        )

    def score_chart(self) -> Dict[str, Any]:
        total = 0
        planet_scores = []

        for p in self.chart.planets:
            ps = self.score_planet(p)
            planet_scores.append(ps)
            total += ps["total"]

        pattern_score = sum(ap.score for ap in self.chart.aspect_patterns)
        total += pattern_score

        element_score = self._score_elements()
        total += element_score

        quality_score = self._score_quality()
        total += quality_score

        dispositor_score = self._score_dispositor()
        total += dispositor_score

        return {
            "total": total,
            "planet_scores": planet_scores,
            "pattern_score": pattern_score,
            "element_score": element_score,
            "quality_score": quality_score,
            "dispositor_score": dispositor_score,
            "strength": "exceptional"
            if total >= 50
            else "strong"
            if total >= 25
            else "moderate"
            if total >= 10
            else "challenging"
            if total >= 0
            else "difficult",
        }

    def _score_elements(self) -> int:
        if not self.chart.element_distribution:
            return 0
        ed = self.chart.element_distribution
        counts = {"fire": ed.fire, "earth": ed.earth, "air": ed.air, "water": ed.water}
        dominant = max(counts, key=counts.get)
        return 10 if counts[dominant] >= len([p for p in self.chart.planets if p.body_type == "planet"]) * 0.4 else 0

    def _score_quality(self) -> int:
        if not self.chart.quality_distribution:
            return 0
        qd = self.chart.quality_distribution
        counts = {"cardinal": qd.cardinal, "fixed": qd.fixed, "mutable": qd.mutable}
        dominant = max(counts, key=counts.get)
        return 10 if counts[dominant] >= len([p for p in self.chart.planets if p.body_type == "planet"]) * 0.4 else 0

    def _score_dispositor(self) -> int:
        if not self.chart.dispositor:
            return 0
        score = 0
        if self.chart.dispositor.final_dispositors:
            score += len(self.chart.dispositor.final_dispositors) * 5
        elif self.chart.dispositor.final_dispositor:
            score += 5
        if self.chart.dispositor.mutual_receptions:
            score += len(self.chart.dispositor.mutual_receptions) * 5
        return score

    def get_planet_rankings(self) -> List[Dict[str, Any]]:
        scores = [self.score_planet(p) for p in self.chart.planets]
        scores.sort(key=lambda x: x["total"], reverse=True)
        return scores

    def get_planet_rankings_by_essential(self) -> List[Dict[str, Any]]:
        """Rank planets by essential dignity (ignoring aspects/house)."""
        scores = [self.score_planet(p) for p in self.chart.planets]
        scores.sort(key=lambda x: x["essential"], reverse=True)
        return scores
