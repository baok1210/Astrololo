from typing import List, Tuple

from astrololo.models.chart import (
    ChartData,
    HouseData,
    ElementDistribution,
    QualityDistribution,
    DispositorResult,
)
from astrololo.models.subject import AstrologicalSubject
from astrololo.core.ephemeris import (
    calc_julian_day,
    calc_house_cusps_ut,
    is_daytime,
    calc_moon_phase,
    calc_delta_t,
)
from astrololo.core.constants import (
    SIGNS,
    HOUSES,
    SIGN_ORDER,
)
from astrololo.core.aspects import AspectCalculator
from astrololo.core.points import build_all_bodies, build_fixed_stars
from astrololo.analysis.midpoints import calc_midpoints


_HOUSE_SYSTEM_CODES = {
    "placidus": "P",
    "koch": "K",
    "equal": "E",
    "whole_sign": "W",
    "regiomontanus": "R",
    "campanus": "C",
    "porphyry": "O",
}


def _calc_houses(
    jd_ut: float, lat: float, lng: float, system: str
) -> Tuple[List[dict], List[float], List[float]]:
    hsys = _HOUSE_SYSTEM_CODES.get(system, "P")
    cusps_raw, ascmc_raw = calc_house_cusps_ut(jd_ut, lat, lng, hsys)
    houses = []
    for i in range(12):
        cusp = cusps_raw[i] if i < len(cusps_raw) else (i * 30.0)
        sign_key = SIGN_ORDER[int(cusp // 30) % 12]
        h = HOUSES.get(i + 1, HOUSES[1])
        houses.append(
            {
                "house_number": i + 1,
                "cusp_degree": round(cusp, 4),
                "sign": sign_key,
                "sign_name_vi": SIGNS[sign_key].name_vi,
                "is_angular": h.type_ == "angular",
                "is_succedent": h.type_ == "succedent",
                "is_cadent": h.type_ == "cadent",
            }
        )
    cusp_degrees = [h["cusp_degree"] for h in houses]
    return houses, cusp_degrees, list(ascmc_raw)


def create_natal_chart(
    subject: AstrologicalSubject, house_system: str = "placidus", node_type: str = "mean", lang: str = "vi",
    esoteric: bool = True,
    include_minor_aspects: bool = True,
    orb_conjunction: float = 8, orb_opposition: float = 8,
    orb_square: float = 8, orb_trine: float = 8, orb_sextile: float = 6,
    orb_quincunx: float = 3, orb_semisextile: float = 3,
    orb_semisquare: float = 2, orb_sesquiquadrate: float = 2,
    orb_quintile: float = 2,
) -> ChartData:
    utc_dt = subject.birth_datetime_utc
    jd_ut = calc_julian_day(
        utc_dt.year, utc_dt.month, utc_dt.day, utc_dt.hour, utc_dt.minute
    )
    subject.julian_day_ut = jd_ut

    jd_tt = jd_ut
    try:
        delta = calc_delta_t(utc_dt.year, utc_dt.month)
        subject.delta_t = delta
        jd_tt = jd_ut + delta / 86400.0
        subject.julian_day_tt = jd_tt
    except Exception:
        pass

    houses_raw, house_cusps_deg, ascmc_raw = _calc_houses(
        jd_ut, subject.latitude, subject.longitude, house_system
    )
    ascendant = house_cusps_deg[0] if house_cusps_deg else 0
    mc = ascmc_raw[1] if len(ascmc_raw) > 1 else (
        house_cusps_deg[9] if len(house_cusps_deg) > 9 else (ascendant + 90) % 360
    )
    asc_sign = SIGN_ORDER[int(ascendant // 30) % 12]
    mc_sign = SIGN_ORDER[int(mc // 30) % 12]

    # ------------------------------------------------------------------ #
    # Check daytime/nighttime for triplicity rulers
    # ------------------------------------------------------------------ #
    day_time = is_daytime(jd_ut, subject.latitude, subject.longitude)

    # ------------------------------------------------------------------ #
    # Build ALL celestial bodies using points.py (planets + nodes + angles)
    # ------------------------------------------------------------------ #
    all_bodies = build_all_bodies(jd_ut, ascendant, mc, node_type, is_daytime=day_time)

    # Assign houses + cusp proximity to every body
    planets_dict = [p.model_dump() for p in all_bodies]
    from astrololo.core.houses import assign_planets_to_houses

    planets_dict = assign_planets_to_houses(planets_dict, house_cusps_deg)
    for i, p in enumerate(all_bodies):
        p.house = planets_dict[i].get("house", 0)
        p.cusp_proximity = planets_dict[i].get("cusp_proximity")

    # Physical planets only (for element/quality/dispositor)
    physical = [b for b in all_bodies if b.body_type == "planet"]

    house_list = [HouseData(**h) for h in houses_raw]

    # Aspect calculation uses ALL bodies (planets + nodes + angles)
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

    # Weighted element distribution (Big 3 weighted highest, outer planets lowest)
    ELEM_WEIGHTS = {"sun": 4, "moon": 4, "mercury": 3, "venus": 3, "mars": 3,
                    "jupiter": 2, "saturn": 2,
                    "uranus": 1, "neptune": 1, "pluto": 1,
                    "chiron": 0.5, "ceres": 0.5, "pallas": 0.5, "juno": 0.5, "vesta": 0.5, "lilith": 0.5}
    fire = sum(ELEM_WEIGHTS.get(p.name, 1) for p in physical if p.element == "fire")
    earth = sum(ELEM_WEIGHTS.get(p.name, 1) for p in physical if p.element == "earth")
    air = sum(ELEM_WEIGHTS.get(p.name, 1) for p in physical if p.element == "air")
    water = sum(ELEM_WEIGHTS.get(p.name, 1) for p in physical if p.element == "water")
    # Include Ascendant and MC signs (weighted at 4 each)
    asc_sign_obj = SIGNS.get(asc_sign)
    mc_sign_obj = SIGNS.get(mc_sign)
    if asc_sign_obj:
        asc_elem = asc_sign_obj.element
        if asc_elem == "fire":
            fire += 4
        elif asc_elem == "earth":
            earth += 4
        elif asc_elem == "air":
            air += 4
        elif asc_elem == "water":
            water += 4
    if mc_sign_obj:
        mc_elem = mc_sign_obj.element
        if mc_elem == "fire":
            fire += 4
        elif mc_elem == "earth":
            earth += 4
        elif mc_elem == "air":
            air += 4
        elif mc_elem == "water":
            water += 4
    elem_counts = {"fire": fire, "earth": earth, "air": air, "water": water}
    max_count = max(elem_counts.values())
    dom_elem = max(elem_counts, key=elem_counts.get) if max_count > 0 else None
    def_elem = min(elem_counts, key=elem_counts.get) if max_count > 0 else None

    # Weighted quality distribution
    cardinal = sum(ELEM_WEIGHTS.get(p.name, 1) for p in physical if p.quality == "cardinal")
    fixed = sum(ELEM_WEIGHTS.get(p.name, 1) for p in physical if p.quality == "fixed")
    mutable = sum(ELEM_WEIGHTS.get(p.name, 1) for p in physical if p.quality == "mutable")
    # Include Ascendant and MC signs (weighted at 4 each)
    if asc_sign_obj:
        asc_qual = asc_sign_obj.quality
        if asc_qual == "cardinal":
            cardinal += 4
        elif asc_qual == "fixed":
            fixed += 4
        elif asc_qual == "mutable":
            mutable += 4
    if mc_sign_obj:
        mc_qual = mc_sign_obj.quality
        if mc_qual == "cardinal":
            cardinal += 4
        elif mc_qual == "fixed":
            fixed += 4
        elif mc_qual == "mutable":
            mutable += 4

    # Dispositor chain (physical planets only)
    from astrololo.core.constants import SIGN_RULERS, SIGN_MODERN_RULERS

    chain = {p.name: SIGN_RULERS.get(p.sign, "") for p in physical}
    planet_signs = {p.name: p.sign for p in physical}
    final_dispositors = [
        pn for pn, r in chain.items()
        if r == pn or SIGN_MODERN_RULERS.get(planet_signs[pn]) == pn
    ]
    mutual_receptions = [
        (p1, p2) for p1 in chain for p2 in chain
        if p1 < p2 and chain[p1] == p2 and chain[p2] == p1
    ]

    midpoints = calc_midpoints(all_bodies)

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
        midpoints=midpoints,
        ascendant=round(ascendant, 4),
        ascendant_sign=asc_sign,
        mc=round(mc, 4),
        mc_sign=mc_sign,
        element_distribution=ElementDistribution(
            fire=fire, earth=earth, air=air, water=water,
            dominant=dom_elem, deficient=def_elem,
        ),
        quality_distribution=QualityDistribution(
            cardinal=cardinal, fixed=fixed, mutable=mutable,
            dominant=max(
                {"cardinal": cardinal, "fixed": fixed, "mutable": mutable},
                key=lambda k: {"cardinal": cardinal, "fixed": fixed, "mutable": mutable}[k],
            ) if max(cardinal, fixed, mutable) > 0 else None,
        ),
        dispositor=DispositorResult(
            chain=chain,
            final_dispositor=final_dispositors[0] if final_dispositors else None,
            final_dispositors=final_dispositors,
            mutual_receptions=mutual_receptions,
        ),
        is_daytime=day_time,
        moon_phase=moon_phase["phase"],
    )

    # Fixed Stars
    chart.fixed_stars = build_fixed_stars(jd_ut)

    # Part of Fortune
    sun_bp = next((p for p in all_bodies if p.name == "sun" and p.body_type == "planet"), None)
    moon_bp = next((p for p in all_bodies if p.name == "moon" and p.body_type == "planet"), None)
    if sun_bp and moon_bp:
        if day_time:
            pof_lon = (ascendant + moon_bp.longitude - sun_bp.longitude) % 360
        else:
            pof_lon = (ascendant + sun_bp.longitude - moon_bp.longitude) % 360
        pof_sign = SIGN_ORDER[int(pof_lon // 30) % 12]
        pof_house = 1
        for i, cusp in enumerate(house_cusps_deg):
            next_cusp = house_cusps_deg[(i + 1) % 12] if i < 11 else house_cusps_deg[0] + 360
            this_cusp = cusp
            if pof_lon < this_cusp:
                pof_lon += 360
            if this_cusp <= pof_lon < next_cusp:
                pof_house = i + 1
                break
        pof_pos_in_sign = pof_lon % 30
        chart.part_of_fortune = {
            "longitude": round(pof_lon, 4),
            "sign": pof_sign,
            "sign_vi": SIGNS[pof_sign].name_vi,
            "house": pof_house,
            "position_in_sign": round(pof_pos_in_sign, 4),
        }

    # Vertex (điểm duyên phận / "không né được") — ascmc_raw[3] from houses_ex
    if len(ascmc_raw) > 3:
        vertex_lon = float(ascmc_raw[3]) % 360
        vertex_sign = SIGN_ORDER[int(vertex_lon // 30) % 12]
        vertex_house = 1
        for i, cusp in enumerate(house_cusps_deg):
            nxt = house_cusps_deg[(i + 1) % 12] if i < 11 else house_cusps_deg[0] + 360
            this = cusp
            if vertex_lon < this:
                vertex_lon += 360
            if this <= vertex_lon < nxt:
                vertex_house = i + 1
                break
        chart.vertex = {
            "longitude": round(float(ascmc_raw[3]) % 360, 4),
            "sign": vertex_sign,
            "sign_vi": SIGNS[vertex_sign].name_vi,
            "house": vertex_house,
            "position_in_sign": round(float(ascmc_raw[3]) % 30, 4),
        }

    # Dignity scores (essential + accidental)
    from astrololo.scoring.dignity import chart_dignity_scores
    chart.dignity_scores = chart_dignity_scores(chart)

    # Dominant scores
    from astrololo.scoring.dominant import chart_dominant_scores
    chart.dominant_scores = chart_dominant_scores(chart)

    from astrololo.interpretation.engine import InterpretationEngine
    from astrololo.core.validation import validate_chart

    engine = InterpretationEngine(lang=lang, esoteric=esoteric)
    interpretation = engine.interpret(chart)
    chart.interpretation = interpretation.model_dump()

    chart.validation = validate_chart(chart)

    return chart
