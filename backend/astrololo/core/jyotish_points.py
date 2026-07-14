"""Build Navagraha bodies with sidereal positions, nakshatra, and Jyotish dignities."""
from typing import List, Optional
from astrololo.models.chart import BodyPosition
from astrololo.core.constants import SIGNS, SIGN_ORDER
from astrololo.core.jyotish_constants import (
    NAVAGRAHA, NAVAGRAHA_ORDER, RASHI_NAMES, calc_nakshatra, get_jyotish_dignity,
)
from astrololo.core.ephemeris import (
    calc_planet_position_sidereal, calc_planet_position_ut,
    calc_ayanamsa, calc_declination, HAS_SWISSEPH,
)


def _to_sign(lon: float) -> str:
    return SIGN_ORDER[int(lon // 30) % 12]


def _build_graha(jd_ut: float, graha_key: str, ayanamsa_system: str = "lahiri",
                 is_daytime: bool = True) -> Optional[BodyPosition]:
    graha = NAVAGRAHA.get(graha_key)
    if not graha:
        return None

    western_key = graha.western_key
    if not western_key:
        return None

    sid_lon, lat, dist, speed = calc_planet_position_sidereal(
        jd_ut, western_key, ayanamsa_system
    )
    trop_lon, _, _, _ = calc_planet_position_ut(jd_ut, western_key)

    sid_sign = _to_sign(sid_lon)
    trop_sign = _to_sign(trop_lon)
    pos_in_sign = sid_lon % 30
    is_retro = speed < 0

    nak_idx, nak_info, pada = calc_nakshatra(sid_lon)
    dignity = get_jyotish_dignity(graha_key, sid_sign, pos_in_sign)

    rashi = RASHI_NAMES.get(sid_sign, ("", ""))

    return BodyPosition(
        body_type="planet",
        name=western_key,
        name_vi=graha.name_vi,
        name_en=graha.name_en,
        longitude=round(trop_lon, 4),
        latitude=round(lat, 6),
        distance=round(dist, 6),
        speed=round(speed, 6),
        sign=trop_sign,
        sign_name_vi=SIGNS[trop_sign].name_vi,
        sign_name_en=SIGNS[trop_sign].name_en,
        position_in_sign=round(trop_lon % 30, 4),
        house=0,
        is_retrograde=is_retro,
        element=SIGNS[sid_sign].element,
        quality=SIGNS[sid_sign].quality,
        dignity_score=0,
        dignity_label=dignity,
        declination=round(calc_declination(jd_ut, western_key), 4) if HAS_SWISSEPH else 0.0,
        # Jyotish-specific
        sidereal_longitude=round(sid_lon, 4),
        sidereal_sign=sid_sign,
        sidereal_sign_degree=round(pos_in_sign, 4),
        nakshatra=nak_info.name_sa,
        nakshatra_vi=nak_info.name_vi,
        nakshatra_pada=pada,
        nakshatra_lord=nak_info.ruler,
        graha_name=graha.name_sa,
        graha_name_vi=graha.name_vi,
        tattwa=graha.tattwa,
        guna=graha.guna,
        jyotish_dignity=dignity,
    )


def _build_ketu(jd_ut: float, rahu_body: BodyPosition, ayanamsa_system: str = "lahiri") -> BodyPosition:
    """Ketu = Rahu + 180° (both tropical and sidereal)."""
    graha = NAVAGRAHA["ketu"]

    trop_lon = (rahu_body.longitude + 180) % 360
    sid_lon = (rahu_body.sidereal_longitude + 180) % 360 if rahu_body.sidereal_longitude is not None else 0.0

    trop_sign = _to_sign(trop_lon)
    sid_sign = _to_sign(sid_lon)
    pos_in_sign = sid_lon % 30

    nak_idx, nak_info, pada = calc_nakshatra(sid_lon)
    dignity = get_jyotish_dignity("ketu", sid_sign, pos_in_sign)

    return BodyPosition(
        body_type="node",
        name="south_node",
        name_vi=graha.name_vi,
        name_en=graha.name_en,
        longitude=round(trop_lon, 4),
        latitude=0.0,
        distance=0.0,
        speed=round(rahu_body.speed, 6),
        sign=trop_sign,
        sign_name_vi=SIGNS[trop_sign].name_vi,
        sign_name_en=SIGNS[trop_sign].name_en,
        position_in_sign=round(trop_lon % 30, 4),
        house=0,
        is_retrograde=rahu_body.is_retrograde,
        element="",
        quality="",
        dignity_score=0,
        dignity_label=dignity,
        declination=0.0,
        sidereal_longitude=round(sid_lon, 4),
        sidereal_sign=sid_sign,
        sidereal_sign_degree=round(pos_in_sign, 4),
        nakshatra=nak_info.name_sa,
        nakshatra_vi=nak_info.name_vi,
        nakshatra_pada=pada,
        nakshatra_lord=nak_info.ruler,
        graha_name=graha.name_sa,
        graha_name_vi=graha.name_vi,
        tattwa=graha.tattwa,
        guna=graha.guna,
        jyotish_dignity=dignity,
    )


def build_jyotish_angles(asc_sid: float, mc_sid: float, asc_trop: float, mc_trop: float) -> List[BodyPosition]:
    """Build ASC/MC/DSC/IC with both tropical and sidereal positions."""
    from astrololo.core.constants import PLANETS

    angles = []
    for key, sid_lon, trop_lon in [
        ("ascendant", asc_sid, asc_trop),
        ("mc", mc_sid, mc_trop),
        ("descendant", (asc_sid + 180) % 360, (asc_trop + 180) % 360),
        ("ic", (mc_sid + 180) % 360, (mc_trop + 180) % 360),
    ]:
        trop_sign = _to_sign(trop_lon)
        sid_sign = _to_sign(sid_lon)
        nak_idx, nak_info, pada = calc_nakshatra(sid_lon)
        angles.append(BodyPosition(
            body_type="angle",
            name=key,
            name_vi=PLANETS[key].name_vi,
            name_en=PLANETS[key].name_en,
            longitude=round(trop_lon, 4),
            sign=trop_sign,
            sign_name_vi=SIGNS[trop_sign].name_vi,
            sign_name_en=SIGNS[trop_sign].name_en,
            position_in_sign=round(trop_lon % 30, 4),
            house=0,
            is_retrograde=False,
            element="", quality="",
            dignity_score=0, dignity_label="neutral",
            declination=0.0,
            sidereal_longitude=round(sid_lon, 4),
            sidereal_sign=sid_sign,
            sidereal_sign_degree=round(sid_lon % 30, 4),
            nakshatra=nak_info.name_sa,
            nakshatra_vi=nak_info.name_vi,
            nakshatra_pada=pada,
            nakshatra_lord=nak_info.ruler,
        ))
    return angles


def build_jyotish_bodies(jd_ut: float, asc_trop: float, mc_trop: float,
                         node_type: str = "mean", is_daytime: bool = True,
                         ayanamsa_system: str = "lahiri") -> List[BodyPosition]:
    """Build all Navagraha + angles for a Jyotish chart."""
    ayanamsa = calc_ayanamsa(jd_ut, ayanamsa_system)
    asc_sid = (asc_trop - ayanamsa) % 360
    mc_sid = (mc_trop - ayanamsa) % 360

    bodies: List[BodyPosition] = []
    rahu_body: Optional[BodyPosition] = None

    for graha_key in NAVAGRAHA_ORDER:
        if graha_key == "ketu":
            continue
        if graha_key == "rahu":
            ephem_key = "true_node" if node_type == "true" else "mean_node"
            graha = NAVAGRAHA["rahu"]
            sid_lon, lat, dist, speed = calc_planet_position_sidereal(jd_ut, ephem_key, ayanamsa_system)
            trop_lon, _, _, _ = calc_planet_position_ut(jd_ut, ephem_key)

            sid_sign = _to_sign(sid_lon)
            trop_sign = _to_sign(trop_lon)
            pos_in_sign = sid_lon % 30
            nak_idx, nak_info, pada = calc_nakshatra(sid_lon)
            dignity = get_jyotish_dignity("rahu", sid_sign, pos_in_sign)

            bp = BodyPosition(
                body_type="node",
                name="north_node",
                name_vi=graha.name_vi,
                name_en=graha.name_en,
                longitude=round(trop_lon, 4),
                latitude=0.0, distance=0.0,
                speed=round(speed, 6),
                sign=trop_sign,
                sign_name_vi=SIGNS[trop_sign].name_vi,
                sign_name_en=SIGNS[trop_sign].name_en,
                position_in_sign=round(trop_lon % 30, 4),
                house=0,
                is_retrograde=speed < 0,
                element="", quality="",
                dignity_score=0, dignity_label=dignity,
                declination=0.0,
                sidereal_longitude=round(sid_lon, 4),
                sidereal_sign=sid_sign,
                sidereal_sign_degree=round(pos_in_sign, 4),
                nakshatra=nak_info.name_sa,
                nakshatra_vi=nak_info.name_vi,
                nakshatra_pada=pada,
                nakshatra_lord=nak_info.ruler,
                graha_name=graha.name_sa,
                graha_name_vi=graha.name_vi,
                tattwa=graha.tattwa,
                guna=graha.guna,
                jyotish_dignity=dignity,
            )
            rahu_body = bp
            bodies.append(bp)
            continue

        bp = _build_graha(jd_ut, graha_key, ayanamsa_system, is_daytime)
        if bp:
            bodies.append(bp)

    if rahu_body:
        bodies.append(_build_ketu(jd_ut, rahu_body, ayanamsa_system))

    bodies.extend(build_jyotish_angles(asc_sid, mc_sid, asc_trop, mc_trop))

    return bodies
