"""Unified builder for all celestial bodies in a chart.

Produces a single List[BodyPosition] with correct body_type:
  - "planet" — physical planets (Sun through Pluto), have dignity/element/speed
  - "node"   — lunar nodes (North/South), no dignity
  - "angle"  — ASC, MC, DSC, IC, no dignity/speed

Every BodyPosition uses raw float longitude (0-360). String conversion happens
ONLY at display layer via core/coordinates.py.
"""
from typing import List, Optional, Dict, Any
from astrololo.models.chart import BodyPosition
from astrololo.core.constants import (
    PLANETS, SIGNS, SIGN_ORDER, PLANET_ORDER,
    get_dignity_score, get_dignity_score_full,
    get_element, get_quality,
)
from astrololo.core.ephemeris import (
    calc_planet_position_ut, calc_declination, calc_fixed_star_lon, HAS_SWISSEPH,
)
from astrololo.core.fixed_stars import FIXED_STARS, FIXED_STAR_LIST

_ADDITIONAL_KEYS = ["chiron", "ceres", "pallas", "juno", "vesta", "lilith"]
_ANGLE_NAMES = {k: PLANETS[k].name_vi for k in ("ascendant", "mc", "descendant", "ic")}
_ANGLE_NAMES_EN = {k: PLANETS[k].name_en for k in ("ascendant", "mc", "descendant", "ic")}


def _to_sign(longitude: float) -> str:
    return SIGN_ORDER[int(longitude // 30) % 12]


def _to_sign_vi(longitude: float) -> str:
    return SIGNS[_to_sign(longitude)].name_vi


def _to_sign_en(longitude: float) -> str:
    return SIGNS[_to_sign(longitude)].name_en


def _build_one(jd_ut: float, pk: str, is_daytime: bool = True) -> Optional[BodyPosition]:
    """Build a single BodyPosition for planet/asteroid key pk."""
    if pk not in PLANETS:
        return None
    try:
        lon, lat, dist, speed = calc_planet_position_ut(jd_ut, pk)
    except Exception:
        return None
    sign = _to_sign(lon)
    pos_in_sign = lon % 30
    is_retro = speed < 0
    dignity_info = get_dignity_score_full(pk, sign, pos_in_sign, is_daytime)
    return BodyPosition(
        body_type="planet",
        name=pk,
        name_vi=PLANETS[pk].name_vi,
        name_en=PLANETS[pk].name_en,
        longitude=round(lon, 4),
        latitude=round(lat, 6),
        distance=round(dist, 6),
        speed=round(speed, 6),
        sign=sign,
        sign_name_vi=_to_sign_vi(lon),
        sign_name_en=_to_sign_en(lon),
        position_in_sign=round(pos_in_sign, 4),
        house=0,
        is_retrograde=is_retro,
        element=get_element(sign),
        quality=get_quality(sign),
        dignity_score=get_dignity_score(pk, sign),
        dignity_label=dignity_info["label"],
        minor_dignities=[d for d in dignity_info["dignities"] if d not in ("rulership", "exaltation", "detriment", "fall", "neutral")],
        declination=round(calc_declination(jd_ut, pk), 4) if HAS_SWISSEPH else 0.0,
    )


def build_planets(jd_ut: float, is_daytime: bool = True) -> List[BodyPosition]:
    """Build body_type='planet' entries for Sun through Pluto plus asteroids."""
    bodies = []
    for pk in PLANET_ORDER:
        if pk in _ADDITIONAL_KEYS:
            continue  # handled by build_additional
        bp = _build_one(jd_ut, pk, is_daytime)
        if bp:
            bodies.append(bp)
    return bodies


def _calc_lilith_from_node(jd_ut: float, node_type: str = "mean") -> Optional[BodyPosition]:
    """Calculate Black Moon Lilith as mean apogee = (North Node + 180)°."""
    nk = "true_node" if node_type == "true" else "mean_node"
    try:
        nn_lon, _, _, _ = calc_planet_position_ut(jd_ut, nk)
    except Exception:
        return None
    lon = (nn_lon + 180) % 360
    sign = _to_sign(lon)
    pos_in_sign = lon % 30
    return BodyPosition(
        body_type="planet",
        name="lilith",
        name_vi="Lilith",
        name_en=PLANETS["lilith"].name_en,
        longitude=round(lon, 4),
        latitude=0.0,
        distance=0.0,
        speed=0.0,
        sign=sign,
        sign_name_vi=_to_sign_vi(lon),
        sign_name_en=_to_sign_en(lon),
        position_in_sign=round(pos_in_sign, 4),
        house=0,
        is_retrograde=False,
        element=get_element(sign),
        quality=get_quality(sign),
        dignity_score=0,
        dignity_label="neutral",
        declination=0.0,
    )


def build_additional(jd_ut: float, node_type: str = "mean", is_daytime: bool = True) -> List[BodyPosition]:
    """Build Chiron, asteroids, Lilith (body_type='planet')."""
    bodies = []
    for pk in _ADDITIONAL_KEYS:
        if pk == "lilith":
            bp = _calc_lilith_from_node(jd_ut, node_type)
        else:
            bp = _build_one(jd_ut, pk, is_daytime)
        if bp:
            bodies.append(bp)
    return bodies


def build_nodes(jd_ut: float, node_type: str = "mean") -> List[BodyPosition]:
    """Build body_type='node' entries for North Node and South Node."""
    nk = "true_node" if node_type == "true" else "mean_node"
    try:
        nn_lon, nn_lat, nn_dist, nn_speed = calc_planet_position_ut(jd_ut, nk)
        sn_lon = (nn_lon + 180) % 360
    except Exception:
        nn_lon = 0.0
        sn_lon = 180.0
        nn_speed = 0.0

    nn_retro = nn_speed < -1e-10
    bodies = []
    for node_key, node_lon in [("north_node", nn_lon), ("south_node", sn_lon)]:
        name_vi = "La Hầu" if node_key == "north_node" else "Kế Hầu"
        sign = _to_sign(node_lon)
        pos_in_sign = node_lon % 30
        bodies.append(
            BodyPosition(
                body_type="node",
                name=node_key,
                name_vi=name_vi,
                name_en=PLANETS[node_key].name_en,
                longitude=round(node_lon, 4),
                latitude=0.0,
                distance=0.0,
                speed=round(nn_speed, 6),
                sign=sign,
                sign_name_vi=_to_sign_vi(node_lon),
                sign_name_en=_to_sign_en(node_lon),
                position_in_sign=round(pos_in_sign, 4),
                house=0,
                is_retrograde=nn_retro,
                element="",
                quality="",
                dignity_score=0,
                dignity_label="neutral",
                declination=0.0,
            )
        )
    return bodies


def build_angles(asc: float, mc: float) -> List[BodyPosition]:
    """Build body_type='angle' entries for ASC, MC, DSC, IC."""
    desc = (asc + 180) % 360
    ic = (mc + 180) % 360
    bodies = []
    for key, lon in [("ascendant", asc), ("mc", mc), ("descendant", desc), ("ic", ic)]:
        sign = _to_sign(lon)
        pos_in_sign = lon % 30
        bodies.append(
            BodyPosition(
                body_type="angle",
                name=key,
                name_vi=_ANGLE_NAMES[key],
                name_en=_ANGLE_NAMES_EN[key],
                longitude=round(lon, 4),
                sign=sign,
                sign_name_vi=_to_sign_vi(lon),
                sign_name_en=_to_sign_en(lon),
                position_in_sign=round(pos_in_sign, 4),
                house=0,
                is_retrograde=False,
                element="",
                quality="",
                dignity_score=0,
                dignity_label="neutral",
                declination=0.0,
            )
        )
    return bodies


def build_fixed_stars(jd_ut: float) -> List[Dict[str, Any]]:
    """Build fixed star positions with precession applied.

    Returns list of dicts (not BodyPosition) since fixed stars don't
    participate in houses, aspects, dignity, or element logic.
    """
    stars = []
    for sk in FIXED_STAR_LIST:
        info = FIXED_STARS[sk]
        lon = calc_fixed_star_lon(jd_ut, info["lon_j2000"])
        sign = _to_sign(lon)
        pos_in_sign = lon % 30
        stars.append({
            "name": sk,
            "name_en": info["name_en"],
            "name_vi": info["name_vi"],
            "longitude": round(lon, 4),
            "sign": sign,
            "sign_name_vi": _to_sign_vi(lon),
            "sign_name_en": _to_sign_en(lon),
            "position_in_sign": round(pos_in_sign, 4),
            "magnitude": info["mag"],
            "nature": info["nature"],
            "meaning_en": info["meaning_en"],
            "meaning_vi": info["meaning_vi"],
            "keywords_en": info["keywords_en"],
            "keywords_vi": info["keywords_vi"],
            "orb": info["orb"],
            "constellation": info["constellation"],
        })
    return stars


def build_all_bodies(jd_ut: float, asc: float, mc: float, node_type: str = "mean", is_daytime: bool = True) -> List[BodyPosition]:
    """Build ALL celestial bodies for a chart: planets + asteroids + nodes + angles.

    Returns a flat list of BodyPosition with body_type correctly set.
    The chart's .planets field stores ALL bodies; consumers filter by body_type.
    node_type: 'mean' (default) or 'true'.
    """
    return build_planets(jd_ut, is_daytime) + build_additional(jd_ut, node_type, is_daytime) + build_nodes(jd_ut, node_type) + build_angles(asc, mc)
