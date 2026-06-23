from typing import Optional
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.models.chart import ChartData
from astrololo.core.constants import SIGN_RULERS, SIGN_MODERN_RULERS, PLANETS


class DispositorRule(InterpretationRule):
    def __init__(self):
        super().__init__(priority=5)

    def matches(self, chart: ChartData) -> bool:
        return len(chart.planets) > 0

    def _resolve_chain(self, chain: dict, mutual_pairs: list) -> dict:
        """Walk each planet's chain until hitting a terminal (final or mutual pair)."""
        terminal = {}
        for p_name in chain:
            visited = set()
            current = p_name
            while current in chain and current not in visited:
                visited.add(current)
                ruler = chain[current]["ruled_by"]
                if (
                    ruler == current
                    or SIGN_MODERN_RULERS.get(chain[current]["in_sign"]) == current
                ):
                    terminal[p_name] = ("final", current)
                    break
                mr = [pair for pair in mutual_pairs if current in pair]
                if mr:
                    terminal[p_name] = ("mutual", tuple(mr[0]))
                    break
                if ruler not in chain:
                    terminal[p_name] = ("unknown", ruler)
                    break
                current = ruler
            else:
                terminal[p_name] = ("loop", current)
        return terminal

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[RuleResult]:
        chain = {}
        for p in chart.planets:
            ruler = SIGN_RULERS.get(p.sign, "")
            chain[p.name] = {"in_sign": p.sign, "ruled_by": ruler}

        final = [
            p_name
            for p_name, info in chain.items()
            if info["ruled_by"] == p_name
            or SIGN_MODERN_RULERS.get(info["in_sign"]) == p_name
        ]

        mutual_pairs = []
        for p1 in chain:
            for p2 in chain:
                if p1 < p2:
                    if chain[p1]["ruled_by"] == p2 and chain[p2]["ruled_by"] == p1:
                        mutual_pairs.append((p1, p2))

        if not final and not mutual_pairs:
            return None

        terminal = self._resolve_chain(chain, mutual_pairs)

        parts = []

        if final:
            for f in final:
                p = next(p for p in chart.planets if p.name == f)
                planets_here = [
                    pn
                    for pn, (t, _) in terminal.items()
                    if t == "final" and _ == f and pn != f
                ]
                if lang == "vi":
                    line = (
                        f"{p.name_vi} là chủ tinh tối cao (Final Dispositor) của lá số."
                    )
                    if planets_here:
                        names_vi = [
                            next(p2.name_vi for p2 in chart.planets if p2.name == pn)
                            for pn in planets_here
                        ]
                        line += (
                            f" Năng lượng của {', '.join(names_vi)} đổ về {p.name_vi}."
                        )
                    line += f" Tính chất {p.name_vi} - {', '.join(PLANETS[f].keywords_vi)} - ảnh hưởng xuyên suốt."
                    parts.append(line)
                else:
                    line = f"{PLANETS[f].name_en} is a Final Dispositor."
                    if planets_here:
                        names_en = [PLANETS[pn].name_en for pn in planets_here]
                        line += f" Energy from {', '.join(names_en)} flows here."
                    parts.append(line)

        if mutual_pairs:
            for p1, p2 in mutual_pairs:
                pp1 = next(p for p in chart.planets if p.name == p1)
                pp2 = next(p for p in chart.planets if p.name == p2)
                planets_here = [
                    pn
                    for pn, (t, _) in terminal.items()
                    if t == "mutual"
                    and _ == tuple(sorted([p1, p2]))
                    and pn not in (p1, p2)
                ]
                if lang == "vi":
                    line = f"Vòng lặp tương hỗ (Mutual Reception Loop) giữa {pp1.name_vi} và {pp2.name_vi}: hai hành tinh nằm trong cung của nhau tạo thành một hệ thống chủ quản khép kín."
                    if planets_here:
                        names_vi = [
                            next(p3.name_vi for p3 in chart.planets if p3.name == pn)
                            for pn in planets_here
                        ]
                        line += f" Năng lượng của {', '.join(names_vi)} đổ vào vòng lặp này."
                    parts.append(line)
                else:
                    line = f"Mutual Reception Loop between {PLANETS[p1].name_en} and {PLANETS[p2].name_en}: they form a closed rulership system."
                    if planets_here:
                        names_en = [PLANETS[pn].name_en for pn in planets_here]
                        line += (
                            f" Energy from {', '.join(names_en)} flows into this loop."
                        )
                    parts.append(line)

        text = "\n\n".join(parts)
        score = len(final) * 5 + len(mutual_pairs) * 5

        return RuleResult(
            title_vi="Chuỗi Chủ Tinh (Dispositor Chain)" if lang == "vi" else "",
            title_en="Dispositor Chain" if lang == "en" else "",
            text_vi=text if lang == "vi" else "",
            text_en=text if lang == "en" else "",
            score=score,
            priority=self.priority,
            category="dispositor",
            tags=final + [f"{a}-{b}" for a, b in mutual_pairs],
            metadata={"final_dispositors": final, "mutual_receptions": mutual_pairs},
        )


RuleRegistry.register(DispositorRule())
