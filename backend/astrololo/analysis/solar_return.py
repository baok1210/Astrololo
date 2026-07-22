"""Solar Return chart calculation."""
from astrololo.models.chart import ChartData, HouseData
from astrololo.models.subject import AstrologicalSubject
from astrololo.core.ephemeris import (
    calc_julian_day, calc_house_cusps_ut, calc_planet_position_ut,
    is_daytime,
)
from astrololo.core.constants import SIGNS, SIGN_ORDER
from astrololo.core.aspects import AspectCalculator
from astrololo.core.points import build_all_bodies
from astrololo.analysis.natal import create_natal_chart
from astrololo.core.validation import validate_chart
from astrololo.analysis.transit import _pack_aspects, _aspect_status_summary


def _find_solar_return_jd(natal_sun_lon: float, birth_jd: float) -> float:
    """Find the exact JD when transiting Sun crosses the natal Sun longitude.

    Uses binary search around the birthday ± 5 days.
    """
    from astrololo.core.ephemeris import HAS_SWISSEPH

    if HAS_SWISSEPH:
        import swisseph as swe
        try:
            return swe.solcross_ut(natal_sun_lon, birth_jd)
        except Exception:
            pass

    low = birth_jd - 5
    high = birth_jd + 5

    for _ in range(50):
        mid = (low + high) / 2
        sun_lon, _, _, _ = calc_planet_position_ut(mid, "sun")
        diff = (sun_lon - natal_sun_lon) % 360
        if diff < 180:
            high = mid
        else:
            low = mid
        if high - low < 1e-6:
            return mid
    return (low + high) / 2


def create_solar_return(natal_subject: AstrologicalSubject,
                        target_year: int,
                        house_system: str = "placidus", node_type: str = "mean", lang: str = "vi",
                        esoteric: bool = True,
                        include_minor_aspects: bool = True,
                        orb_conjunction: float = 8, orb_opposition: float = 8,
                        orb_square: float = 8, orb_trine: float = 8, orb_sextile: float = 6,
                        orb_quincunx: float = 3, orb_semisextile: float = 3,
                        orb_semisquare: float = 2, orb_sesquiquadrate: float = 2,
                        orb_quintile: float = 2):
    natal = create_natal_chart(natal_subject, house_system, node_type, lang, esoteric,
        include_minor_aspects=include_minor_aspects,
        orb_conjunction=orb_conjunction, orb_opposition=orb_opposition,
        orb_square=orb_square, orb_trine=orb_trine, orb_sextile=orb_sextile,
        orb_quincunx=orb_quincunx, orb_semisextile=orb_semisextile,
        orb_semisquare=orb_semisquare, orb_sesquiquadrate=orb_sesquiquadrate,
        orb_quintile=orb_quintile,
    )

    # Find natal Sun longitude
    natal_sun = next((p for p in natal.planets if p.name == "sun"), None)
    if not natal_sun:
        return {"error": "No Sun found in natal chart"}

    natal_sun_lon = natal_sun.longitude
    birth_jd = natal_subject.julian_day_ut or \
               calc_julian_day(natal_subject.year, natal_subject.month, natal_subject.day,
                               natal_subject.hour, natal_subject.minute)

    # Find solar return moment
    sr_jd = _find_solar_return_jd(natal_sun_lon, birth_jd)

    # Houses at SR moment at birth location
    from astrololo.analysis.natal import _HOUSE_SYSTEM_CODES
    hsys_code = _HOUSE_SYSTEM_CODES.get(house_system, "P")
    cusps_raw, ascmc_raw = calc_house_cusps_ut(
        sr_jd, natal_subject.latitude, natal_subject.longitude, hsys_code,
    )
    house_cusps_deg = [c % 360 for c in cusps_raw[:12]]
    ascendant = float(ascmc_raw[0])
    mc = float(ascmc_raw[1])

    hous = []
    for i in range(12):
        sign = SIGN_ORDER[int(house_cusps_deg[i] // 30) % 12]
        hn = i + 1
        hous.append(HouseData(
            house_number=hn, cusp_degree=round(house_cusps_deg[i], 4),
            sign=sign, sign_name_vi=SIGNS[sign].name_vi,
            is_angular=hn in (1, 4, 7, 10),
            is_succedent=hn in (2, 5, 8, 11),
            is_cadent=hn in (3, 6, 9, 12),
        ))

    sr_daytime = is_daytime(sr_jd, natal_subject.latitude, natal_subject.longitude)
    sr_planets = build_all_bodies(sr_jd, ascendant, mc, node_type, is_daytime=sr_daytime)

    # Assign houses
    for bp in sr_planets:
        lon = bp.longitude
        for i, cusp in enumerate(house_cusps_deg):
            next_cusp = house_cusps_deg[(i + 1) % 12] if i < 11 else house_cusps_deg[0] + 360
            this_cusp = cusp
            if lon < this_cusp:
                lon += 360
            if this_cusp <= lon < next_cusp:
                bp.house = i + 1
                break

    # Aspects within SR chart
    calc = AspectCalculator(
        include_minor_aspects=include_minor_aspects,
        orb_conjunction=orb_conjunction, orb_opposition=orb_opposition,
        orb_square=orb_square, orb_trine=orb_trine, orb_sextile=orb_sextile,
        orb_quincunx=orb_quincunx, orb_semisextile=orb_semisextile,
        orb_semisquare=orb_semisquare, orb_sesquiquadrate=orb_sesquiquadrate,
        orb_quintile=orb_quintile,
    )
    sr_aspects = calc.calculate(sr_planets)

    # SR to natal aspects (transit-style)
    sr_to_natal = []
    for sp in sr_planets:
        for np in natal.planets:
            aspect = calc._calc_aspect(sp, np)
            if aspect:
                sr_to_natal.append(aspect)

    sr_chart = ChartData(
        subject_name=f"{natal_subject.name} — Solar Return {target_year}",
        chart_type="solar_return",
        datetime_utc=None,
        julian_day=sr_jd,
        house_system=house_system,
        node_type=node_type,
        houses=hous,
        planets=sr_planets,
        aspects=sr_aspects,
        ascendant=round(ascendant, 4),
        ascendant_sign=SIGN_ORDER[int(ascendant // 30) % 12],
        mc=round(mc, 4),
        mc_sign=SIGN_ORDER[int(mc // 30) % 12],
        is_daytime=sr_daytime,
    )

    from astrololo.interpretation.engine import InterpretationEngine
    engine = InterpretationEngine(lang=lang, esoteric=esoteric)
    sr_interp = engine.interpret(sr_chart)
    sr_chart.interpretation = sr_interp.model_dump()
    sr_chart.validation = validate_chart(sr_chart)

    return {
        "natal": natal.model_dump(),
        "solar_return": sr_chart.model_dump(),
        "target_year": target_year,
        "solar_return_planets": [
            {
                "name": p.name, "name_vi": p.name_vi, "name_en": p.name_en,
                "longitude": p.longitude, "sign": p.sign,
                "sign_name_vi": p.sign_name_vi, "sign_name_en": p.sign_name_en,
                "position_in_sign": p.position_in_sign, "house": p.house,
                "speed": p.speed, "is_retrograde": p.is_retrograde,
            }
            for p in sr_planets
        ],
        "sr_to_natal_aspects": _pack_aspects(sr_to_natal, lang),
        "aspect_count": len(sr_to_natal),
        "aspect_status_summary": _aspect_status_summary(sr_to_natal, lang),
    }