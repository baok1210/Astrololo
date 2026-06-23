"""Midpoint calculation for all planet pairs and key angle-planet combinations."""
from typing import List
from astrololo.models.chart import BodyPosition, MidpointData
from astrololo.core.constants import SIGN_ORDER, SIGNS


def _to_sign(longitude: float) -> str:
    return SIGN_ORDER[int(longitude // 30) % 12]


def _to_sign_vi(longitude: float) -> str:
    return SIGNS[_to_sign(longitude)].name_vi


def calc_midpoint(lon1: float, lon2: float) -> float:
    """Calculate the shortest-arc midpoint between two longitudes (0-360)."""
    diff = (lon2 - lon1 + 360) % 360
    if diff <= 180:
        return ((lon1 + lon2) / 2) % 360
    return ((lon1 + lon2) / 2 + 180) % 360


def calc_midpoints(bodies: List[BodyPosition]) -> List[MidpointData]:
    """Calculate midpoints for all unique pairs of planets/nodes/angles."""
    midpoints = []
    n = len(bodies)
    for i in range(n):
        for j in range(i + 1, n):
            b1, b2 = bodies[i], bodies[j]
            mp = calc_midpoint(b1.longitude, b2.longitude)
            sign = _to_sign(mp)
            midpoints.append(MidpointData(
                body1=b1.name,
                body2=b2.name,
                midpoint=round(mp, 4),
                sign=sign,
                sign_vi=_to_sign_vi(mp),
                position_in_sign=round(mp % 30, 4),
            ))
    return midpoints
