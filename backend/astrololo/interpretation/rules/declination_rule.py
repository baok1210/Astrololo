from typing import Optional, List
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.models.chart import ChartData
from astrololo.core.constants import PLANETS


_PARALLEL_ORB = 1.0


class DeclinationRule(InterpretationRule):
    """Detect parallel (same declination) and contraparallel (opposite declination) aspects."""

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

                if lang == "vi":
                    label = "Song Song" if aspect_type == "parallel" else "Đối Song"
                    title = f"{n1} {label} {n2}"
                    text = (f"{n1} ({p1.declination:.1f}°) và {n2} ({p2.declination:.1f}°) "
                            f"tạo góc {label.lower()}, nghĩa là chúng có cùng cường độ xích vĩ. "
                            f"Điều này tăng cường sự kết nối năng lượng giữa hai hành tinh.")
                else:
                    label = "Parallel" if aspect_type == "parallel" else "Contraparallel"
                    title = f"{n1} {label} {n2}"
                    text = (f"{n1} ({p1.declination:.1f}°) and {n2} ({p2.declination:.1f}°) "
                            f"form a {label.lower()} aspect, sharing the same declination magnitude. "
                            f"This strengthens the energetic connection between the two planets.")

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
