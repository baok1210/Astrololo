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


# Predictive aspect status helpers

def _aspect_status_summary(aspects, lang):
    if not aspects:
        return {}
    applying = sum(1 for a in aspects if getattr(a, 'applying', False))
    exact = sum(1 for a in aspects if getattr(a, 'exact', False))
    separating = sum(1 for a in aspects if getattr(a, 'separating', False))
    total = len(aspects)
    return {
        'applying': applying,
        'exact': exact,
        'separating': separating,
        'total': total,
    }


def _pack_aspects(aspects, lang):
    out = []
    for a in aspects:
        status = 'unknown'
        if getattr(a, 'exact', False):
            status = 'exact'
        elif getattr(a, 'applying', False):
            status = 'applying'
        elif getattr(a, 'separating', False):
            status = 'separating'
        en_name = a.aspect_type.capitalize()
        out.append({
            'planet1': a.planet1,
            'planet2': a.planet2,
            'aspect_type': a.aspect_type,
            'aspect_name_vi': a.aspect_name_vi,
            'aspect_name_en': en_name,
            'angle': a.angle,
            'orb': a.orb,
            'orb_formatted': a.orb_formatted,
            'exact': bool(a.exact),
            'nature': a.nature,
            'weight': a.weight,
            'applying': bool(a.applying),
            'separating': bool(a.separating),
            'aspect_status': status,
        })
    return out


def create_transits(natal_subject: AstrologicalSubject,
                    transit_year: int, transit_month: int, transit_day: int,
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
    calc = AspectCalculator(
        include_minor_aspects=include_minor_aspects,
        orb_conjunction=orb_conjunction, orb_opposition=orb_opposition,
        orb_square=orb_square, orb_trine=orb_trine, orb_sextile=orb_sextile,
        orb_quincunx=orb_quincunx, orb_semisextile=orb_semisextile,
        orb_semisquare=orb_semisquare, orb_sesquiquadrate=orb_sesquiquadrate,
        orb_quintile=orb_quintile,
    )
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
    from astrololo.analysis.distributions import fill_derived
    fill_derived(transit_chart)
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
        "transit_aspects": _pack_aspects(transit_to_natal, lang),
        "aspect_count": len(transit_to_natal),
        "aspect_status_summary": _aspect_status_summary(transit_to_natal, lang),
        "transit_interpretation": transit_specific,
    }


def create_daily(natal_subject: AstrologicalSubject,
                 house_system: str = "placidus", node_type: str = "mean",
                 lang: str = "vi", esoteric: bool = True,
                 include_minor_aspects: bool = True,
                 orb_conjunction: float = 8, orb_opposition: float = 8,
                 orb_square: float = 8, orb_trine: float = 8, orb_sextile: float = 6,
                 orb_quincunx: float = 3, orb_semisextile: float = 3,
                 orb_semisquare: float = 2, orb_sesquiquadrate: float = 2,
                 orb_quintile: float = 2):
    """Daily horoscope: transit of *today* over the native chart, condensed."""
    from datetime import datetime
    now = datetime.now()
    full = create_transits(
        natal_subject, now.year, now.month, now.day,
        house_system, node_type, lang, esoteric,
        include_minor_aspects=include_minor_aspects,
        orb_conjunction=orb_conjunction, orb_opposition=orb_opposition,
        orb_square=orb_square, orb_trine=orb_trine, orb_sextile=orb_sextile,
        orb_quincunx=orb_quincunx, orb_semisextile=orb_semisextile,
        orb_semisquare=orb_semisquare, orb_sesquiquadrate=orb_sesquiquadrate,
        orb_quintile=orb_quintile,
    )
    # Keep only major-to-moderate aspects for a daily snapshot.
    key = {"conjunction", "opposition", "trine", "square", "sextile"}
    daily_aspects = [a for a in full["transit_aspects"]
                     if a.get("aspect_type") in key and a.get("orb", 9) <= 3.0]
    # Rank by nature (harmonious first) for headline picks.
    daily_aspects.sort(key=lambda a: (a.get("nature") != "harmonious", -a.get("weight", 0)))

    def _label(a):
        p1 = next((p for p in full["natal"]["planets"] if p["name"] == a["planet2"]), None)
        natal_sign = p1["sign_name_vi"] if p1 and lang == "vi" else (p1["sign_name_en"] if p1 else a["planet2"])
        pname = a["planet1"]
        if lang == "vi":
            from astrololo.core.constants import PLANETS as _P
            pname = _P.get(a["planet1"]).name_vi if _P.get(a["planet1"]) else a["planet1"]
        else:
            from astrololo.core.constants import PLANETS as _P
            pname = _P.get(a["planet1"]).name_en if _P.get(a["planet1"]) else a["planet1"]
        return pname, natal_sign

    picks = []
    for a in daily_aspects[:5]:
        pname, natal_sign = _label(a)
        picks.append({
            "transit_planet": a["planet1"],
            "transit_planet_label": pname,
            "aspect": a["aspect_type"],
            "to_natal_planet": a["planet2"],
            "to_natal_sign": natal_sign,
            "orb": a.get("orb"),
            "nature": a.get("nature"),
        })

    if lang == "vi":
        if not picks:
            headline = "Hôm nay các hành tinh di chuyển êm ả — không có góc chiếu mạnh nào chiếu vào lá số của bạn. Đây là ngày để quan sát và nghỉ ngơi."
        else:
            har = sum(1 for p in picks if p["nature"] == "harmonious")
            headline = (f"Hôm nay có {len(picks)} góc chiếu đáng chú ý "
                        f"({har} thuận / {len(picks)-har} nghịch). "
                        f"Nổi bật: {picks[0]['transit_planet_label']} "
                        f"{picks[0]['aspect']} {picks[0]['to_natal_sign']}.")
    else:
        if not picks:
            headline = "Planets move gently today — no strong aspects hit your chart. A good day to observe and rest."
        else:
            har = sum(1 for p in picks if p["nature"] == "harmonious")
            headline = (f"Today brings {len(picks)} notable aspects "
                        f"({har} harmonious / {len(picks)-har} challenging). "
                        f"Highlight: {picks[0]['transit_planet_label']} "
                        f"{picks[0]['aspect']} {picks[0]['to_natal_sign']}.")

    full["daily"] = {
        "date": full["transit_date"],
        "headline": headline,
        "aspect_picks": picks,
    }
    return full

