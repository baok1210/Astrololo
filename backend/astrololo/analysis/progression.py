"""Secondary Progressions (day-for-a-year method)."""
from datetime import timedelta

from astrololo.models.chart import ChartData, HouseData
from astrololo.models.subject import AstrologicalSubject
from astrololo.core.ephemeris import (
    calc_julian_day, calc_house_cusps_ut, is_daytime,
)
from astrololo.core.constants import SIGNS, SIGN_ORDER
from astrololo.core.aspects import AspectCalculator
from astrololo.core.points import build_all_bodies
from astrololo.analysis.natal import create_natal_chart
from astrololo.core.validation import validate_chart
from astrololo.analysis.transit import _aspect_status_summary, _pack_aspects


def create_progressions(natal_subject: AstrologicalSubject,
                        age_years: float,
                        house_system: str = "placidus", node_type: str = "mean", lang: str = "vi",
                        esoteric: bool = True,
                        include_minor_aspects: bool = True,
                        orb_conjunction: float = 8, orb_opposition: float = 8,
                        orb_square: float = 8, orb_trine: float = 8, orb_sextile: float = 6,
                        orb_quincunx: float = 3, orb_semisextile: float = 3,
                        orb_semisquare: float = 2, orb_sesquiquadrate: float = 2,
                        orb_quintile: float = 2):
    """Calculate secondary progressions using day-for-a-year method.

    For each year of life, one day after birth is advanced.
    The progressed chart shows the planetary positions at that advanced date,
    computed at the birth location.
    """
    natal = create_natal_chart(natal_subject, house_system, node_type, lang, esoteric,
        include_minor_aspects=include_minor_aspects,
        orb_conjunction=orb_conjunction, orb_opposition=orb_opposition,
        orb_square=orb_square, orb_trine=orb_trine, orb_sextile=orb_sextile,
        orb_quincunx=orb_quincunx, orb_semisextile=orb_semisextile,
        orb_semisquare=orb_semisquare, orb_sesquiquadrate=orb_sesquiquadrate,
        orb_quintile=orb_quintile,
    )

    # Day-for-a-year: progressed date = birth date + age_in_days
    age_days = int(age_years * 365.25)
    progressed_utc = natal_subject.birth_datetime_utc + timedelta(days=age_days)

    prog_jd = calc_julian_day(
        progressed_utc.year, progressed_utc.month,
        progressed_utc.day, progressed_utc.hour, progressed_utc.minute,
    )

    # Houses at progressed date at birth location
    from astrololo.analysis.natal import _HOUSE_SYSTEM_CODES
    hsys_code = _HOUSE_SYSTEM_CODES.get(house_system, "P")
    cusps_raw, ascmc_raw = calc_house_cusps_ut(
        prog_jd, natal_subject.latitude, natal_subject.longitude, hsys_code,
    )
    house_cusps_deg = [c % 360 for c in cusps_raw[:12]]
    ascendant = float(ascmc_raw[0])
    mc = float(ascmc_raw[1])

    hous = []
    for i in range(12):
        sign = SIGN_ORDER[int(house_cusps_deg[i] // 30) % 12]
        hn = i + 1
        hous.append(HouseData(
            house_number=hn,
            cusp_degree=round(house_cusps_deg[i], 4),
            sign=sign,
            sign_name_vi=SIGNS[sign].name_vi,
            is_angular=hn in (1, 4, 7, 10),
            is_succedent=hn in (2, 5, 8, 11),
            is_cadent=hn in (3, 6, 9, 12),
        ))

    # Progressed bodies
    prog_daytime = is_daytime(prog_jd, natal_subject.latitude, natal_subject.longitude)
    prog_planets = build_all_bodies(prog_jd, ascendant, mc, node_type, is_daytime=prog_daytime)

    # Assign houses
    for bp in prog_planets:
        lon = bp.longitude
        for i, cusp in enumerate(house_cusps_deg):
            next_cusp = house_cusps_deg[(i + 1) % 12] if i < 11 else house_cusps_deg[0] + 360
            this_cusp = cusp
            if lon < this_cusp:
                lon += 360
            if this_cusp <= lon < next_cusp:
                bp.house = i + 1
                break

    # Aspects: progressed planets to natal planets
    calc = AspectCalculator(
        include_minor_aspects=include_minor_aspects,
        orb_conjunction=orb_conjunction, orb_opposition=orb_opposition,
        orb_square=orb_square, orb_trine=orb_trine, orb_sextile=orb_sextile,
        orb_quincunx=orb_quincunx, orb_semisextile=orb_semisextile,
        orb_semisquare=orb_semisquare, orb_sesquiquadrate=orb_sesquiquadrate,
        orb_quintile=orb_quintile,
    )
    prog_to_natal = []
    for pp in prog_planets:
        for np in natal.planets:
            aspect = calc._calc_aspect(pp, np)
            if aspect:
                prog_to_natal.append(aspect)

    progressed_date_str = f"{progressed_utc.year}-{progressed_utc.month:02d}-{progressed_utc.day:02d}"

    prog_chart = ChartData(
        subject_name=f"{natal_subject.name} — Progressed Age {age_years}",
        chart_type="progression",
        datetime_utc=progressed_utc,
        julian_day=prog_jd,
        house_system=house_system,
        node_type=node_type,
        houses=hous,
        planets=prog_planets,
        aspects=prog_to_natal,
        ascendant=round(ascendant, 4),
        ascendant_sign=SIGN_ORDER[int(ascendant // 30) % 12],
        mc=round(mc, 4),
        mc_sign=SIGN_ORDER[int(mc // 30) % 12],
        is_daytime=prog_daytime,
    )

    # Run interpretation
    from astrololo.interpretation.engine import InterpretationEngine
    engine = InterpretationEngine(lang=lang, esoteric=esoteric)
    prog_interp = engine.interpret(prog_chart)
    prog_chart.interpretation = prog_interp.model_dump()

    # Validate
    prog_chart.validation = validate_chart(prog_chart)

    return {
        "natal": natal.model_dump(),
        "progression": prog_chart.model_dump(),
        "age": age_years,
        "progressed_date": progressed_date_str,
        "progressed_planets": [
            {
                "name": p.name, "name_vi": p.name_vi, "name_en": p.name_en,
                "longitude": p.longitude, "sign": p.sign,
                "sign_name_vi": p.sign_name_vi, "sign_name_en": p.sign_name_en,
                "position_in_sign": p.position_in_sign, "house": p.house,
                "speed": p.speed, "is_retrograde": p.is_retrograde,
            }
            for p in prog_planets
        ],
        "progressed_aspects": _pack_aspects(prog_to_natal, lang),
        "aspect_count": len(prog_to_natal),
        "aspect_status_summary": _aspect_status_summary(prog_to_natal, lang),
    }