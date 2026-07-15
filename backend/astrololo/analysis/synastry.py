from astrololo.models.subject import AstrologicalSubject
from astrololo.models.chart import ChartData
from astrololo.analysis.natal import create_natal_chart
from astrololo.core.aspects import AspectCalculator
from astrololo.core.constants import PLANETS, SIGNS, SIGN_ORDER
from astrololo.core.houses import find_house
from typing import List


def _calc_midpoint_lon(lon1: float, lon2: float) -> float:
    """Calculate the shortest-arc midpoint between two longitudes."""
    diff = (lon2 - lon1) % 360
    if diff > 180:
        diff -= 360
    return (lon1 + diff / 2) % 360


def _calc_house_overlays(chart1: ChartData, chart2: ChartData) -> List[dict]:
    """Calculate which house of chart2 each planet of chart1 falls in."""
    house_cusps2 = [h.cusp_degree for h in chart2.houses]
    overlays = []
    for p in chart1.planets:
        if p.body_type != "planet":
            continue
        overlay_house = find_house(p.longitude, house_cusps2)
        from astrololo.interpretation.template_loader import get_planet_in_house
        entry = get_planet_in_house(p.name, overlay_house, "vi")
        entry_en = get_planet_in_house(p.name, overlay_house, "en")
        overlays.append({
            "planet": p.name,
            "planet_name_vi": p.name_vi,
            "planet_name_en": p.name_en,
            "overlay_house": overlay_house,
            "interpretation_vi": entry.get("detailed", entry.get("short", "")) if entry else "",
            "interpretation_en": entry_en.get("detailed", entry_en.get("short", "")) if entry_en else "",
        })
    return overlays


def _build_composite_chart(chart1: ChartData, chart2: ChartData, lang: str) -> ChartData:
    """Build a composite chart from midpoints of two natal charts."""
    from astrololo.models.chart import ElementDistribution, QualityDistribution, DispositorResult

    p1_map = {p.name: p for p in chart1.planets}
    p2_map = {p.name: p for p in chart2.planets}

    comp_planets = []
    for name, p1 in p1_map.items():
        p2 = p2_map.get(name)
        if not p2:
            continue
        comp_lon = _calc_midpoint_lon(p1.longitude, p2.longitude)
        comp_sign = SIGN_ORDER[int(comp_lon // 30) % 12]
        comp_pos = comp_lon % 30
        s_obj = SIGNS.get(comp_sign)
        from astrololo.models.chart import BodyPosition
        comp_planets.append(BodyPosition(
            name=name, name_vi=p1.name_vi, name_en=p1.name_en,
            longitude=round(comp_lon, 4), sign=comp_sign,
            sign_name_vi=s_obj.name_vi if s_obj else "", sign_name_en=s_obj.name_en if s_obj else "",
            position_in_sign=round(comp_pos, 4), house=0, body_type=p1.body_type,
            element=s_obj.element if s_obj else "", quality=s_obj.quality if s_obj else "",
            speed=(p1.speed + p2.speed) / 2, is_retrograde=False,
            polarity=s_obj.polarity if s_obj else "",
            dignity_score=0, dignity_label="", jyotish_dignity="",
        ))

    # Composite angles
    comp_asc = _calc_midpoint_lon(chart1.ascendant or 0, chart2.ascendant or 0)
    comp_mc = _calc_midpoint_lon(chart1.mc or 0, chart2.mc or 0)
    comp_asc_sign = SIGN_ORDER[int(comp_asc // 30) % 12]
    comp_mc_sign = SIGN_ORDER[int(comp_mc // 30) % 12]

    # Aspect calculation for composite
    calc = AspectCalculator()
    comp_aspects = calc.calculate(comp_planets)

    comp_chart = ChartData(
        subject_name=f"{chart1.subject_name} + {chart2.subject_name}",
        chart_type="composite",
        datetime_utc=None,
        julian_day=0,
        house_system=chart1.house_system,
        node_type=chart1.node_type,
        houses=chart1.houses,
        planets=comp_planets,
        aspects=comp_aspects,
        ascendant=round(comp_asc, 4),
        ascendant_sign=comp_asc_sign,
        mc=round(comp_mc, 4),
        mc_sign=comp_mc_sign,
        is_daytime=chart1.is_daytime,
        element_distribution=ElementDistribution(),
        quality_distribution=QualityDistribution(),
        dispositor=DispositorResult(),
    )

    # Run interpretation
    from astrololo.interpretation.engine import InterpretationEngine
    engine = InterpretationEngine(lang=lang, esoteric=False)
    interp = engine.interpret(comp_chart)
    comp_chart.interpretation = interp.model_dump()

    return comp_chart


def create_synastry(person1: AstrologicalSubject, person2: AstrologicalSubject,
                    house_system: str = "placidus", node_type: str = "mean", lang: str = "vi",
                    esoteric: bool = True,
                    include_minor_aspects: bool = True,
                    orb_conjunction: float = 8, orb_opposition: float = 8,
                    orb_square: float = 8, orb_trine: float = 8, orb_sextile: float = 6,
                    orb_quincunx: float = 3, orb_semisextile: float = 3,
                    orb_semisquare: float = 2, orb_sesquiquadrate: float = 2,
                    orb_quintile: float = 2):
    chart1 = create_natal_chart(person1, house_system, node_type, lang, esoteric,
        include_minor_aspects=include_minor_aspects,
        orb_conjunction=orb_conjunction, orb_opposition=orb_opposition,
        orb_square=orb_square, orb_trine=orb_trine, orb_sextile=orb_sextile,
        orb_quincunx=orb_quincunx, orb_semisextile=orb_semisextile,
        orb_semisquare=orb_semisquare, orb_sesquiquadrate=orb_sesquiquadrate,
        orb_quintile=orb_quintile,
    )
    chart2 = create_natal_chart(person2, house_system, node_type, lang, esoteric,
        include_minor_aspects=include_minor_aspects,
        orb_conjunction=orb_conjunction, orb_opposition=orb_opposition,
        orb_square=orb_square, orb_trine=orb_trine, orb_sextile=orb_sextile,
        orb_quincunx=orb_quincunx, orb_semisextile=orb_semisextile,
        orb_semisquare=orb_semisquare, orb_sesquiquadrate=orb_sesquiquadrate,
        orb_quintile=orb_quintile,
    )

    # Run interpretation on both charts
    from astrololo.interpretation.engine import InterpretationEngine
    engine = InterpretationEngine(lang=lang, esoteric=esoteric)
    interp1 = engine.interpret(chart1)
    interp2 = engine.interpret(chart2)
    chart1.interpretation = interp1.model_dump()
    chart2.interpretation = interp2.model_dump()

    calc = AspectCalculator(
        include_minor_aspects=include_minor_aspects,
        orb_conjunction=orb_conjunction, orb_opposition=orb_opposition,
        orb_square=orb_square, orb_trine=orb_trine, orb_sextile=orb_sextile,
        orb_quincunx=orb_quincunx, orb_semisextile=orb_semisextile,
        orb_semisquare=orb_semisquare, orb_sesquiquadrate=orb_sesquiquadrate,
        orb_quintile=orb_quintile,
    )
    cross_aspects = calc.calculate_dual(chart1.planets, chart2.planets)

    harmonious = sum(1 for a in cross_aspects if a.nature == "harmonious")
    challenging = sum(1 for a in cross_aspects if a.nature == "challenging")
    total = len(cross_aspects)

    # ---- Compatibility score (0-100) ----
    # Weighted cross-aspect tally (harmonious +, challenging -), then bonus for
    # relationship-defining pairs (Sun-Moon, Venus-Mars, ASC/MC contacts).
    _KEY_PAIRS = {
        ("sun", "moon"): 8, ("moon", "sun"): 8,
        ("venus", "mars"): 6, ("mars", "venus"): 6,
        ("venus", "venus"): 4, ("mars", "mars"): 4,
        ("sun", "venus"): 4, ("venus", "sun"): 4,
        ("sun", "mars"): 4, ("mars", "sun"): 4,
        ("ascendant", "sun"): 5, ("sun", "ascendant"): 5,
        ("ascendant", "moon"): 5, ("moon", "ascendant"): 5,
        ("ascendant", "venus"): 4, ("venus", "ascendant"): 4,
        ("mc", "sun"): 3, ("sun", "mc"): 3,
    }
    _ASP_W = {"conjunction": 3.0, "trine": 2.0, "sextile": 1.5,
              "opposition": -1.5, "square": -2.0, "quincunx": -0.5,
              "semisquare": -0.5, "sesquiquadrate": -0.5,
              "semisextile": 0.5, "quintile": 1.0}
    score_raw = sum(_ASP_W.get(a.aspect_type, 0.0) for a in cross_aspects)
    for a in cross_aspects:
        pair = _KEY_PAIRS.get((a.planet1, a.planet2))
        if pair:
            score_raw += pair * (1.0 if a.nature == "harmonious" else 0.5 if a.aspect_type in ("conjunction", "trine", "sextile") else -0.3)
    # Normalize via ratio of harmonious vs challenging so the score doesn't
    # saturate at 100 for charts with many aspects (which always net positive).
    denom = (harmonious + challenging) or 1
    ratio = (harmonious - challenging) / denom
    compatibility = max(0, min(100, int(round(50 + 50 * ratio))))
    compat_label = (
        "Rất hợp" if compatibility >= 75 else
        "Khá hợp" if compatibility >= 55 else
        "Trung bình" if compatibility >= 40 else
        "Cần nỗ lực" if compatibility >= 25 else "Nhiều thách thức"
    ) if total > 0 else "Chưa đủ dữ liệu"

    # Generate interpreted cross-aspect sections
    from astrololo.interpretation.template_loader import get_aspect
    cross_items = []
    for a in cross_aspects[:20]:
        entry = get_aspect(a.planet1, a.planet2, a.aspect_type, lang)
        if entry:
            p1_name = PLANETS.get(a.planet1)
            p2_name = PLANETS.get(a.planet2)
            p1_label = p1_name.name_vi if p1_name and lang == "vi" else (p1_name.name_en if p1_name else a.planet1)
            p2_label = p2_name.name_vi if p2_name and lang == "vi" else (p2_name.name_en if p2_name else a.planet2)
            title = entry.get("title", f"{p1_label} - {p2_label}")
            text = entry.get("detailed", entry.get("short", ""))
            cross_items.append({
                "title": title,
                "text": text,
                "score": a.weight,
                "tags": ["synastry", a.aspect_type, a.planet1, a.planet2],
                "metadata": {
                    "planet1": a.planet1, "planet2": a.planet2,
                    "aspect_type": a.aspect_type, "angle": a.angle, "orb": a.orb,
                    "nature": a.nature,
                },
            })

    # House overlays: P1 planets in P2 houses (and vice versa)
    overlays_1in2 = _calc_house_overlays(chart1, chart2)
    overlays_2in1 = _calc_house_overlays(chart2, chart1)

    # Composite chart
    try:
        comp_chart = _build_composite_chart(chart1, chart2, lang)
        composite = comp_chart.model_dump()
    except Exception:
        composite = None

    # KB-sourced synastry overview (EN) from the love_compatibility corpus
    compatibility_text = None
    if lang == "en":
        from astrololo.interpretation.knowledge_retriever import retrieve_compatibility
        def _sign_of(chart, body):
            for pl in chart.planets:
                if getattr(pl, "name", "") == body:
                    return getattr(pl, "sign", "")
            return ""
        p1sig = _sign_of(chart1, "sun")
        p2sig = _sign_of(chart2, "sun")
        compatibility_text = retrieve_compatibility(p1sig, p2sig)

    # Generate a simple synastry summary interpretation
    if total > 0:
        if harmonious > challenging * 1.5:
            summary_vi = f"Mối quan hệ có nhiều góc chiếu thuận lợi ({harmonious}/{total}), cho thấy sự hòa hợp tự nhiên giữa hai người."
            summary_en = f"This relationship has many harmonious aspects ({harmonious}/{total}), indicating natural compatibility."
        elif challenging > harmonious * 1.5:
            summary_vi = f"Mối quan hệ có nhiều góc chiếu thách thức ({challenging}/{total}), đòi hỏi sự nỗ lực và thấu hiểu từ cả hai."
            summary_en = f"This relationship has many challenging aspects ({challenging}/{total}), requiring effort and understanding."
        else:
            summary_vi = f"Mối quan hệ cân bằng giữa góc chiếu thuận ({harmonious}) và thách thức ({challenging}), tạo nên sự năng động."
            summary_en = f"This relationship balances harmonious ({harmonious}) and challenging ({challenging}) aspects, creating dynamic energy."
    else:
        summary_vi = "Không có góc chiếu chính nào giữa hai lá số."
        summary_en = "No major aspects between the two charts."

    return {
        "person1": chart1.model_dump(),
        "person2": chart2.model_dump(),
        "cross_aspects": [a.model_dump() for a in cross_aspects],
        "cross_aspect_count": total,
        "harmonious_aspects": harmonious,
        "challenging_aspects": challenging,
        "compatibility_score": compatibility,
        "compatibility_label": compat_label,
        "cross_interpretation": cross_items,
        "house_overlays": {
            "p1_in_p2": overlays_1in2,
            "p2_in_p1": overlays_2in1,
        },
        "composite": composite,
        "compatibility_text": compatibility_text,
        "summary": {
            "vi": summary_vi,
            "en": summary_en,
        },
    }