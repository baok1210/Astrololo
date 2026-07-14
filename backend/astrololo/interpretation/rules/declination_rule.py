from typing import Optional, List
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.models.chart import ChartData
from astrololo.core.constants import PLANETS
from astrololo.interpretation.keywords import get_planet_function


_PARALLEL_ORB = 1.0


class DeclinationRule(InterpretationRule):
    def __init__(self):
        super().__init__(priority=40)

    def matches(self, chart: ChartData) -> bool:
        planets = [p for p in chart.planets if p.body_type == "planet" and p.declination != 0.0]
        return len(planets) >= 2

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[List[RuleResult]]:
        planets = [p for p in chart.planets if p.body_type == "planet" and p.declination != 0.0]
        if len(planets) < 2:
            return None

        results = []
        for i in range(len(planets)):
            for j in range(i + 1, len(planets)):
                p1, p2 = planets[i], planets[j]
                d1, d2 = p1.declination, p2.declination
                diff = abs(d1 - d2)
                if diff > 180:
                    diff = 360 - diff

                if diff <= _PARALLEL_ORB:
                    aspect_type = "parallel"
                elif abs(abs(d1) - abs(d2)) <= _PARALLEL_ORB and d1 * d2 < 0:
                    aspect_type = "contraparallel"
                else:
                    continue

                pl1 = PLANETS.get(p1.name)
                pl2 = PLANETS.get(p2.name)
                n1 = pl1.name_vi if pl1 and lang == "vi" else pl1.name_en if pl1 else p1.name
                n2 = pl2.name_vi if pl2 and lang == "vi" else pl2.name_en if pl2 else p2.name

                f1 = get_planet_function(p1.name) or ""
                f2 = get_planet_function(p2.name) or ""
                f1_short = f1.split(".")[0] + "." if f1 else ""
                f2_short = f2.split(".")[0] + "." if f2 else ""

                stren = (
                    "kết nối này tăng cường và khuếch đại sự tương tác giữa hai nguồn năng lượng"
                    if lang == "vi"
                    else "this connection strengthens and amplifies the interaction between the two energies"
                )
                if aspect_type == "parallel":
                    if lang == "vi":
                        label = "Song Song"
                        nature = (
                            "cùng nằm ở cùng một phía xích vĩ, cho thấy chúng hoạt động "
                            "hài hòa và hỗ trợ lẫn nhau"
                        )
                    else:
                        label = "Parallel"
                        nature = (
                            "share the same declination side, indicating they work "
                            "in harmony and support each other"
                        )
                else:
                    if lang == "vi":
                        label = "Đối Song"
                        nature = (
                            "nằm ở hai phía đối lập của xích vĩ, tạo ra sự căng thẳng "
                            "sáng tạo và bổ sung cho nhau"
                        )
                    else:
                        label = "Contraparallel"
                        nature = (
                            "lie on opposite sides of the declination, creating "
                            "creative tension and complementing each other"
                        )

                if lang == "vi":
                    title = f"{n1} {label} {n2}"
                    parts = [
                        f"{n1} ({p1.declination:.1f}°) và {n2} ({p2.declination:.1f}°) "
                        f"tạo góc {label.lower()}, nghĩa là {nature}.",
                        f"Trong bối cảnh này, {stren}."
                    ]
                    if f1_short:
                        parts.append(f"{n1}: {f1_short}")
                    if f2_short:
                        parts.append(f"{n2}: {f2_short}")
                    text = " ".join(parts)
                else:
                    title = f"{n1} {label} {n2}"
                    parts = [
                        f"{n1} ({p1.declination:.1f}°) and {n2} ({p2.declination:.1f}°) "
                        f"form a {label.lower()} aspect, meaning they {nature}.",
                        f"In this context, {stren}."
                    ]
                    if f1_short:
                        parts.append(f"{n1}: {f1_short}")
                    if f2_short:
                        parts.append(f"{n2}: {f2_short}")
                    text = " ".join(parts)

                results.append(RuleResult(
                    title_vi=title if lang == "vi" else "",
                    title_en=title if lang == "en" else "",
                    text_vi=text if lang == "vi" else "",
                    text_en=text if lang == "en" else "",
                    score=4.0,
                    priority=self.priority,
                    category="aspect",
                    planet=p1.name,
                    aspect=aspect_type,
                    tags=["declination", aspect_type, p1.name, p2.name],
                    metadata={
                        "type": aspect_type,
                        "planet1": p1.name,
                        "planet2": p2.name,
                        "declination1": p1.declination,
                        "declination2": p2.declination,
                        "diff": round(diff, 2),
                    },
                ))

        return results if results else None


RuleRegistry.register(DeclinationRule())