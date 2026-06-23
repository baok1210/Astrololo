from astrololo.models.subject import AstrologicalSubject
from astrololo.analysis.natal import create_natal_chart
from astrololo.core.aspects import AspectCalculator
from astrololo.core.constants import PLANETS


def create_synastry(person1: AstrologicalSubject, person2: AstrologicalSubject,
                    house_system: str = "placidus", node_type: str = "mean", lang: str = "vi",
                    esoteric: bool = True):
    chart1 = create_natal_chart(person1, house_system, node_type, lang, esoteric)
    chart2 = create_natal_chart(person2, house_system, node_type, lang, esoteric)

    # Run interpretation on both charts
    from astrololo.interpretation.engine import InterpretationEngine
    engine = InterpretationEngine(lang=lang, esoteric=esoteric)
    interp1 = engine.interpret(chart1)
    interp2 = engine.interpret(chart2)
    chart1.interpretation = interp1.model_dump()
    chart2.interpretation = interp2.model_dump()

    calc = AspectCalculator()
    cross_aspects = calc.calculate_dual(chart1.planets, chart2.planets)

    harmonious = sum(1 for a in cross_aspects if a.nature == "harmonious")
    challenging = sum(1 for a in cross_aspects if a.nature == "challenging")
    total = len(cross_aspects)

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
        "cross_interpretation": cross_items,
        "summary": {
            "vi": summary_vi,
            "en": summary_en,
        },
    }
