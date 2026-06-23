from astrololo.models.chart import ChartData, HouseData
from astrololo.models.subject import AstrologicalSubject
from astrololo.core.ephemeris import (
    calc_julian_day, calc_house_cusps_ut,
)
from astrololo.core.constants import (
    SIGNS, SIGN_ORDER,
    HOUSES,
)
from astrololo.core.aspects import AspectCalculator
from astrololo.core.points import build_all_bodies
from astrololo.analysis.natal import create_natal_chart
from astrololo.core.validation import validate_chart


def create_transits(natal_subject: AstrologicalSubject,
                    transit_year: int, transit_month: int, transit_day: int,
                    house_system: str = "placidus", node_type: str = "mean", lang: str = "vi",
                    esoteric: bool = True):
    natal = create_natal_chart(natal_subject, house_system, node_type, lang, esoteric)

    transit_jd = calc_julian_day(transit_year, transit_month, transit_day, 12, 0)
    transit_date = f"{transit_year}-{transit_month:02d}-{transit_day:02d}"

    # Houses for transit time
    from astrololo.analysis.natal import _HOUSE_SYSTEM_CODES
    hsys_code = _HOUSE_SYSTEM_CODES.get(house_system, "P")
    cusps_raw, ascmc_raw = calc_house_cusps_ut(transit_jd, natal_subject.latitude, natal_subject.longitude, hsys_code)
    house_cusps_deg = [cusps_raw[i] if cusps_raw[i] != 0 else cusps_raw[i - 1] + 30 if i > 0 else 0.0 for i in range(12)]
    ascendant = float(ascmc_raw[0])
    mc = float(ascmc_raw[1])

    hous = []
    for i in range(12):
        sign = SIGN_ORDER[int(house_cusps_deg[i] // 30) % 12]
        hn = i + 1
        hid = f"house_{hn}"
        ht = HOUSES.get(hid)
        hous.append(HouseData(
            house_number=hn,
            cusp_degree=round(house_cusps_deg[i], 4),
            sign=sign,
            sign_name_vi=SIGNS[sign].name_vi,
            is_angular=hn in (1, 4, 7, 10) if ht else False,
            is_succedent=hn in (2, 5, 8, 11) if ht else False,
            is_cadent=hn in (3, 6, 9, 12) if ht else False,
        ))

    # Transit bodies
    from astrololo.core.ephemeris import is_daytime as calc_daytime
    t_is_daytime = calc_daytime(transit_jd, natal_subject.latitude, natal_subject.longitude)
    transit_planets = build_all_bodies(transit_jd, ascendant, mc, node_type, is_daytime=t_is_daytime)

    # Assign houses to transit planets
    for bp in transit_planets:
        lon = bp.longitude
        for i, cusp in enumerate(house_cusps_deg):
            next_cusp = house_cusps_deg[(i + 1) % 12] if i < 11 else house_cusps_deg[0] + 360
            this_cusp = cusp
            if lon < this_cusp:
                lon += 360
            if this_cusp <= lon < next_cusp:
                bp.house = i + 1
                break

    # Aspects: transit planets to natal planets
    calc = AspectCalculator()
    transit_to_natal = []
    for tp in transit_planets:
        for np in natal.planets:
            aspect = calc._calc_aspect(tp, np)
            if aspect:
                transit_to_natal.append(aspect)

    # Interpretation for transit
    transit_chart = ChartData(
        subject_name=f"{natal_subject.name} — Transit {transit_date}",
        chart_type="transit",
        datetime_utc=natal_subject.birth_datetime_utc,
        julian_day=transit_jd,
        house_system=house_system,
        node_type=node_type,
        houses=hous,
        planets=transit_planets,
        aspects=transit_to_natal,
        ascendant=round(ascendant, 4),
        ascendant_sign=SIGN_ORDER[int(ascendant // 30) % 12],
        mc=round(mc, 4),
        mc_sign=SIGN_ORDER[int(mc // 30) % 12],
        is_daytime=t_is_daytime,
    )

    # Run interpretation on transit chart
    from astrololo.interpretation.engine import InterpretationEngine
    engine = InterpretationEngine(lang=lang, esoteric=esoteric)
    transit_interp = engine.interpret(transit_chart)
    transit_chart.interpretation = transit_interp.model_dump()

    # Generate transit-specific interpretation
    try:
        from astrololo.analysis.transit_interpretation import interpret_transit
        transit_specific = interpret_transit(natal, transit_chart, lang)
    except Exception:
        transit_specific = {"overview": "", "sections": [], "per_planet": []}

    # Validate transit chart
    transit_chart.validation = validate_chart(transit_chart)

    return {
        "natal": natal.model_dump(),
        "transit": transit_chart.model_dump(),
        "transit_date": transit_date,
        "transit_planets": [
            {
                "name": p.name,
                "name_vi": p.name_vi,
                "name_en": p.name_en,
                "longitude": p.longitude,
                "sign": p.sign,
                "sign_name_vi": p.sign_name_vi,
                "sign_name_en": p.sign_name_en,
                "position_in_sign": p.position_in_sign,
                "house": p.house,
                "speed": p.speed,
                "is_retrograde": p.is_retrograde,
            }
            for p in transit_planets
        ],
        "transit_aspects": [a.model_dump() for a in transit_to_natal],
        "aspect_count": len(transit_to_natal),
        "transit_interpretation": transit_specific,
    }
