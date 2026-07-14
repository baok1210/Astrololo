"""Jyotish (Vedic) natal chart creation — sidereal positions, Navagraha, Dasha."""
from typing import List, Tuple

from astrololo.models.chart import (
    ChartData, HouseData, TattwaDistribution, GunaDistribution,
    DispositorResult,
)
from astrololo.models.subject import AstrologicalSubject
from astrololo.core.ephemeris import (
    calc_julian_day, calc_house_cusps_ut, is_daytime,
    calc_moon_phase, calc_delta_t, calc_ayanamsa,
)
from astrololo.core.constants import SIGNS, SIGN_ORDER, HOUSES
from astrololo.core.aspects import AspectCalculator
from astrololo.core.jyotish_points import build_jyotish_bodies
from astrololo.core.jyotish_constants import (
    NAVAGRAHA, JYOTISH_SIGN_RULERS, VARA_RULERS,
)
from astrololo.core.dasha import calc_vimshottari_dasha


def _calc_houses_sidereal(
    jd_ut: float, lat: float, lng: float, ayanamsa_deg: float,
    system: str = "whole_sign",
) -> Tuple[List[dict], List[float]]:
    """Calculate house cusps using sidereal ascendant.

    Default Whole Sign for Jyotish.
    """
    hsys_map = {"whole_sign": "W", "equal": "E", "placidus": "P", "koch": "K"}
    hsys = hsys_map.get(system, "W")

    cusps_raw, ascmc_raw = calc_house_cusps_ut(jd_ut, lat, lng, hsys)
    asc_trop = cusps_raw[0] if cusps_raw else 0
    asc_sid = (asc_trop - ayanamsa_deg) % 360

    if system == "whole_sign":
        asc_sign_idx = int(asc_sid // 30)
        cusps_sid = [(asc_sign_idx * 30 + i * 30) % 360 for i in range(12)]
    else:
        cusps_sid = [(c - ayanamsa_deg) % 360 for c in cusps_raw[:12]]

    houses = []
    for i in range(12):
        cusp = cusps_sid[i] if i < len(cusps_sid) else (i * 30.0)
        sign_key = SIGN_ORDER[int(cusp // 30) % 12]
        h = HOUSES.get(i + 1, HOUSES[1])
        houses.append({
            "house_number": i + 1,
            "cusp_degree": round(cusp, 4),
            "sign": sign_key,
            "sign_name_vi": SIGNS[sign_key].name_vi,
            "is_angular": h.type_ == "angular",
            "is_succedent": h.type_ == "succedent",
            "is_cadent": h.type_ == "cadent",
        })

    cusp_degrees = [h["cusp_degree"] for h in houses]
    return houses, cusp_degrees


def create_jyotish_chart(
    subject: AstrologicalSubject,
    house_system: str = "whole_sign",
    node_type: str = "mean",
    lang: str = "vi",
    ayanamsa_system: str = "lahiri",
    include_minor_aspects: bool = True,
    orb_conjunction: float = 8, orb_opposition: float = 8,
    orb_square: float = 8, orb_trine: float = 8, orb_sextile: float = 6,
    orb_quincunx: float = 3, orb_semisextile: float = 3,
    orb_semisquare: float = 2, orb_sesquiquadrate: float = 2,
    orb_quintile: float = 2,
) -> ChartData:
    """Create a Vedic/Jyotish natal chart with sidereal positions."""

    utc_dt = subject.birth_datetime_utc
    jd_ut = calc_julian_day(
        utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour, utc_dt.minute
    )
    subject.julian_day_ut = jd_ut

    try:
        delta = calc_delta_t(utc_dt.year, utc_dt.month)
        subject.delta_t = delta
        subject.julian_day_tt = jd_ut + delta / 86400.0
    except Exception:
        pass

    ayanamsa_deg = calc_ayanamsa(jd_ut, ayanamsa_system)

    # Tropical cusps first (for ascendant/MC reference)
    cusps_trop, ascmc_trop = calc_house_cusps_ut(
        jd_ut, subject.latitude, subject.longitude, "P"
    )
    asc_trop = cusps_trop[0] if cusps_trop else 0
    mc_trop = ascmc_trop[1] if len(ascmc_trop) > 1 else (asc_trop + 90) % 360

    asc_sid = (asc_trop - ayanamsa_deg) % 360
    mc_sid = (mc_trop - ayanamsa_deg) % 360
    asc_sign = SIGN_ORDER[int(asc_sid // 30) % 12]
    mc_sign = SIGN_ORDER[int(mc_sid // 30) % 12]

    day_time = is_daytime(jd_ut, subject.latitude, subject.longitude)

    # Sidereal houses
    houses_raw, house_cusps_deg = _calc_houses_sidereal(
        jd_ut, subject.latitude, subject.longitude, ayanamsa_deg, house_system
    )

    # Build Navagraha
    all_bodies = build_jyotish_bodies(
        jd_ut, asc_trop, mc_trop, node_type, day_time, ayanamsa_system
    )

    # Assign sidereal houses
    for bp in all_bodies:
        sid_lon = bp.sidereal_longitude if bp.sidereal_longitude is not None else 0
        bp.house = _find_house(sid_lon, house_cusps_deg)

    house_list = [HouseData(**h) for h in houses_raw]

    # Aspects
    aspect_calc = AspectCalculator(
        include_minor_aspects=include_minor_aspects,
        orb_conjunction=orb_conjunction, orb_opposition=orb_opposition,
        orb_square=orb_square, orb_trine=orb_trine, orb_sextile=orb_sextile,
        orb_quincunx=orb_quincunx, orb_semisextile=orb_semisextile,
        orb_semisquare=orb_semisquare, orb_sesquiquadrate=orb_sesquiquadrate,
        orb_quintile=orb_quintile,
    )
    aspects = aspect_calc.calculate(all_bodies)

    moon_phase = calc_moon_phase(jd_ut)

    # Tattwa distribution
    tattwa_counts = {"agni": 0, "jala": 0, "prithvi": 0, "vayu": 0, "akash": 0}
    guna_counts = {"sattwa": 0, "rajas": 0, "tamas": 0}
    for bp in all_bodies:
        if bp.body_type == "planet" and bp.tattwa:
            tattwa_counts[bp.tattwa] = tattwa_counts.get(bp.tattwa, 0) + 1
        if bp.body_type in ("planet", "node") and bp.guna:
            guna_counts[bp.guna] = guna_counts.get(bp.guna, 0) + 1

    dom_tattwa = max(tattwa_counts, key=tattwa_counts.get) if any(tattwa_counts.values()) else None
    dom_guna = max(guna_counts, key=guna_counts.get) if any(guna_counts.values()) else None

    # Dispositor chain (Jyotish rulers)
    physical = [b for b in all_bodies if b.body_type == "planet" and b.sidereal_sign]
    chain = {}
    for p in physical:
        ruler_graha = JYOTISH_SIGN_RULERS.get(p.sidereal_sign, "")
        g = NAVAGRAHA.get(ruler_graha)
        chain[p.name] = g.western_key if g else ""

    final_dispositors = [pn for pn, r in chain.items() if r == pn]

    # Vimshottari Dasha
    moon_bp = next((b for b in all_bodies if b.name == "moon" and b.body_type == "planet"), None)
    dasha_data = None
    if moon_bp and moon_bp.sidereal_longitude is not None:
        dasha_data = calc_vimshottari_dasha(
            moon_bp.sidereal_longitude, subject.birth_datetime_utc
        )

    # Vara
    weekday = subject.birth_datetime.weekday()
    vara = VARA_RULERS.get(weekday)

    chart = ChartData(
        subject_name=subject.name,
        chart_type="natal",
        datetime_utc=subject.birth_datetime_utc,
        julian_day=jd_ut,
        house_system=house_system,
        node_type=node_type,
        houses=house_list,
        planets=all_bodies,
        aspects=aspects,
        ascendant=round(asc_sid, 4),
        ascendant_sign=asc_sign,
        mc=round(mc_sid, 4),
        mc_sign=mc_sign,
        dispositor=DispositorResult(
            chain=chain,
            final_dispositor=final_dispositors[0] if final_dispositors else None,
            final_dispositors=final_dispositors,
            mutual_receptions=[],
        ),
        is_daytime=day_time,
        moon_phase=moon_phase["phase"],
        zodiac_type="sidereal",
        ayanamsa=ayanamsa_system,
        ayanamsa_degrees=round(ayanamsa_deg, 6),
        dasha=dasha_data,
        vara=vara,
        tattwa_distribution=TattwaDistribution(
            **tattwa_counts, dominant=dom_tattwa,
        ),
        guna_distribution=GunaDistribution(
            **guna_counts, dominant=dom_guna,
        ),
    )

    return chart


def _find_house(longitude: float, cusps: List[float]) -> int:
    """Find which house a sidereal longitude falls in."""
    lon = longitude % 360
    for i in range(12):
        start = cusps[i] % 360
        end = cusps[(i + 1) % 12] % 360
        if start <= end:
            if start <= lon < end:
                return i + 1
        else:
            if lon >= start or lon < end:
                return i + 1
    return 1
