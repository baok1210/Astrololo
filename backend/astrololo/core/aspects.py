from typing import List, Optional, Dict
from astrololo.core.constants import (
    ASPECTS, angular_distance, MAJOR_ASPECTS,
)
from astrololo.models.chart import AspectData, BodyPosition
from astrololo.core.coordinates import decimal_to_rounded_dms, dms_to_display_string


def _format_orb(orb_deg: float) -> str:
    """Convert decimal degree orb to degrees and arc-minutes string."""
    d, m = decimal_to_rounded_dms(orb_deg)
    return dms_to_display_string(d, m)


class AspectCalculator:
    def __init__(self, orb_conjunction: float = 8, orb_opposition: float = 8,
                 orb_square: float = 8, orb_trine: float = 8, orb_sextile: float = 6,
                 orb_quincunx: float = 3, orb_semisextile: float = 3,
                 orb_semisquare: float = 2, orb_sesquiquadrate: float = 2,
                 orb_quintile: float = 2,
                 include_minor_aspects: bool = True):
        self.orbs = {
            "conjunction": orb_conjunction,
            "opposition": orb_opposition,
            "square": orb_square,
            "trine": orb_trine,
            "sextile": orb_sextile,
            "quincunx": orb_quincunx,
            "semisextile": orb_semisextile,
            "semisquare": orb_semisquare,
            "sesquiquadrate": orb_sesquiquadrate,
            "quintile": orb_quintile,
        }
        if include_minor_aspects:
            self.aspect_list = ["conjunction", "opposition", "square", "trine", "sextile", "quincunx", "semisextile", "semisquare", "sesquiquadrate", "quintile"]
        else:
            self.aspect_list = list(MAJOR_ASPECTS)

    def calculate(self, planets: List[BodyPosition]) -> List[AspectData]:
        aspects = []
        for i, p1 in enumerate(planets):
            for j, p2 in enumerate(planets):
                if i >= j:
                    continue
                aspect = self._calc_aspect(p1, p2)
                if aspect:
                    aspects.append(aspect)
        return aspects

    def calculate_dual(self, planets1: List[BodyPosition], planets2: List[BodyPosition]) -> List[AspectData]:
        aspects = []
        for p1 in planets1:
            for p2 in planets2:
                aspect = self._calc_aspect(p1, p2)
                if aspect:
                    aspects.append(aspect)
        return aspects

    def _calc_aspect(self, p1: BodyPosition, p2: BodyPosition) -> Optional[AspectData]:
        angle = angular_distance(p1.longitude, p2.longitude)

        # Compute if angular distance is decreasing (applying) or increasing (separating)
        dt = 0.01  # ~15 minutes ahead
        p1_future = (p1.longitude + p1.speed * dt) % 360
        p2_future = (p2.longitude + p2.speed * dt) % 360
        future_angle = angular_distance(p1_future, p2_future)
        applies = future_angle < angle - 1e-8

        for aspect_key in self.aspect_list:
            asp = ASPECTS.get(aspect_key)
            if not asp:
                continue
            max_orb = self.orbs.get(aspect_key, asp.orb)
            if p1.name in ("sun", "moon") or p2.name in ("sun", "moon"):
                max_orb += 1

            diff = abs(angle - asp.angle)
            if diff <= max_orb:
                weight = asp.weight
                if diff <= max_orb * 0.3:
                    weight += 1

                return AspectData(
                    planet1=p1.name,
                    planet2=p2.name,
                    aspect_type=aspect_key,
                    aspect_name_vi=asp.name_vi,
                    angle=round(angle, 2),
                    orb=round(diff, 2),
                    orb_formatted=_format_orb(diff),
                    exact=diff < 0.5,
                    nature=asp.nature,
                    weight=weight,
                    applying=applies,
                    separating=not applies,
                )
        return None
