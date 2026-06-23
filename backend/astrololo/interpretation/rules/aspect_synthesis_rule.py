"""Cross-aspect synthesis — for each planet, combine all its aspects into one narrative."""
from typing import Optional, List, Dict, Any
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.models.chart import ChartData
from astrololo.core.constants import PLANETS


def _aspect_synthesis_for_planet(
    chart: ChartData, planet_name: str, lang: str = "vi"
) -> Dict[str, Any]:
    """Generate a synthesis of all aspects for one planet."""
    p = PLANETS.get(planet_name)
    pbody = next((b for b in chart.planets if b.name == planet_name), None)
    if not pbody:
        return {}

    p_name = p.name_vi if p and lang == "vi" else p.name_en if p else planet_name

    aspects_n = [a for a in chart.aspects if a.planet1 == planet_name or a.planet2 == planet_name]
    if len(aspects_n) < 2:
        return {}

    harmonious = []
    challenging = []
    for a in aspects_n:
        if a.nature == "harmonious":
            harmonious.append(a)
        else:
            challenging.append(a)

    h_count = len(harmonious)
    c_count = len(challenging)

    # Build detailed text
    lines = []
    if lang == "vi":
        lines.append(f"{p_name} có {len(aspects_n)} góc chiếu chính:")
    else:
        lines.append(f"{p_name} has {len(aspects_n)} major aspects:")

    for a in aspects_n[:6]:
        other = a.planet2 if a.planet1 == planet_name else a.planet1
        ob = next((b for b in chart.planets if b.name == other), None)
        if not ob:
            continue
        a_name = a.aspect_name_vi if lang == "vi" else a.aspect_type.replace("_", " ").title()
        o_name = PLANETS[other].name_vi if lang == "vi" and PLANETS.get(other) else (
            PLANETS[other].name_en if PLANETS.get(other) else other
        )
        lines.append(f"  • {a_name} {o_name} (orb {a.orb:.1f}°)")

    if lang == "vi":
        if h_count > c_count:
            balance = (
                f"Nhìn chung, các góc chiếu tích cực chiếm ưu thế ({h_count}/{len(aspects_n)}), "
                f"cho thấy {p_name} hoạt động hiệu quả và gặp nhiều thuận lợi."
            )
        elif c_count > h_count:
            balance = (
                f"Các góc chiếu thách thức chiếm ưu thế ({c_count}/{len(aspects_n)}), "
                f"cho thấy {p_name} là một điểm cần nỗ lực và trưởng thành trong lá số."
            )
        else:
            balance = (
                f"Cân bằng giữa góc thuận và góc khó ({h_count}/{c_count}), "
                f"cho thấy {p_name} vừa có thuận lợi vừa có thách thức."
            )
        lines.append("")
        lines.append(balance)
        lines.append("")
        lines.append(
            f"Để hiểu đầy đủ {p_name}, cần xem xét tất cả góc chiếu này trong bối cảnh "
            f"tổng thể — không chỉ từng góc riêng lẻ."
        )
    else:
        if h_count > c_count:
            balance = (
                f"Overall, harmonious aspects dominate ({h_count}/{len(aspects_n)}), "
                f"indicating {p_name} functions effectively with many advantages."
            )
        elif c_count > h_count:
            balance = (
                f"Challenging aspects dominate ({c_count}/{len(aspects_n)}), "
                f"indicating {p_name} is an area requiring effort and growth."
            )
        else:
            balance = (
                f"Balanced between easy and hard aspects ({h_count}/{c_count}), "
                f"indicating both advantages and challenges for {p_name}."
            )
        lines.append("")
        lines.append(balance)
        lines.append("")
        lines.append(
            f"To fully understand {p_name}, consider all these aspects together "
            f"in the overall chart context — not each in isolation."
        )

    text = "\n".join(lines)

    if lang == "vi":
        title = f"Tổng hợp góc chiếu: {p_name}"
    else:
        title = f"Aspect synthesis: {p_name}"

    return {"title": title, "text": text}


class AspectSynthesisRule(InterpretationRule):
    def __init__(self):
        super().__init__(priority=30)

    def matches(self, chart: ChartData) -> bool:
        return len(chart.planets) > 0 and len(chart.aspects) > 0

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[List[RuleResult]]:
        results = []
        physical = [p for p in chart.planets if p.body_type == "planet"]
        for p in physical:
            syn = _aspect_synthesis_for_planet(chart, p.name, lang)
            if not syn:
                continue
            results.append(RuleResult(
                title_vi=syn.get("title", ""),
                title_en=syn.get("title", ""),
                text_vi=syn.get("text", ""),
                text_en=syn.get("text", ""),
                score=len([a for a in chart.aspects if a.planet1 == p.name or a.planet2 == p.name]),
                priority=self.priority,
                category="aspect_synthesis",
                planet=p.name,
                tags=[p.name, "synthesis"],
            ))
        return results if results else None
