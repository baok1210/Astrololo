"""Strengths & Weaknesses summary rule — synthesizes chart factors into categorized lists."""
from typing import Optional, List
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.models.chart import ChartData
from astrololo.core.constants import PLANETS, SIGNS


class StrengthWeaknessRule(InterpretationRule):
    """Summarizes chart strengths (dignities, angular houses, harmonious aspects)
    and weaknesses (detriments, challenging aspects, retrograde)."""

    def __init__(self):
        super().__init__(priority=3)

    def matches(self, chart: ChartData) -> bool:
        return len(chart.planets) >= 3

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[List[RuleResult]]:
        strengths = []
        weaknesses = []

        planets_data = [p for p in chart.planets if p.body_type == "planet"]

        # 1. Essential dignity scan
        for p in planets_data:
            pl = PLANETS.get(p.name)
            if not pl:
                continue
            sign = p.sign

            if sign in pl.ruler_of:
                strengths.append((p.name, "rulership", lang))
            if pl.exaltation and sign == pl.exaltation:
                strengths.append((p.name, "exaltation", lang))

            if sign in pl.detriment:
                weaknesses.append((p.name, "detriment", lang))
            if pl.fall and sign == pl.fall:
                weaknesses.append((p.name, "fall", lang))

        # 2. House strength/weakness
        angular = {1, 4, 7, 10}
        cadent = {3, 6, 9, 12}
        for p in planets_data:
            if p.house in angular and p.name not in ("chiron", "ceres", "pallas", "juno", "vesta", "lilith"):
                strengths.append((p.name, "angular_house", lang, p.house))
            if p.house in cadent and p.name not in ("chiron", "ceres", "pallas", "juno", "vesta", "lilith"):
                weaknesses.append((p.name, "cadent_house", lang, p.house))

        # 3. Retrograde
        for p in planets_data:
            if p.is_retrograde and p.body_type == "planet":
                weaknesses.append((p.name, "retrograde", lang))

        # 4. Aspect analysis
        harmonious_count = {p.name: 0 for p in planets_data}
        challenging_count = {p.name: 0 for p in planets_data}
        for asp in chart.aspects:
            if asp.nature == "harmonious":
                harmonious_count[asp.planet1] = harmonious_count.get(asp.planet1, 0) + 1
                harmonious_count[asp.planet2] = harmonious_count.get(asp.planet2, 0) + 1
            elif asp.nature == "challenging":
                challenging_count[asp.planet1] = challenging_count.get(asp.planet1, 0) + 1
                challenging_count[asp.planet2] = challenging_count.get(asp.planet2, 0) + 1

        for p in planets_data:
            hn = harmonious_count.get(p.name, 0)
            cn = challenging_count.get(p.name, 0)
            if hn >= 3 and hn > cn * 1.5:
                strengths.append((p.name, "harmonious_aspects", lang, hn))
            if cn >= 3 and cn > hn * 1.5:
                weaknesses.append((p.name, "challenging_aspects", lang, cn))

        # 5. Element imbalance
        if chart.element_distribution:
            ed = chart.element_distribution
            total = ed.fire + ed.earth + ed.air + ed.water
            if total > 0:
                max_elem = max([(ed.fire, "fire"), (ed.earth, "earth"), (ed.air, "air"), (ed.water, "water")],
                               key=lambda x: x[0])
                min_elem = min([(ed.fire, "fire"), (ed.earth, "earth"), (ed.air, "air"), (ed.water, "water")],
                               key=lambda x: x[0])
                if max_elem[0] / total >= 0.5:
                    strengths.append(("element", max_elem[1], lang, round(max_elem[0] / total * 100)))
                if min_elem[0] / total <= 0.1 and min_elem[0] < total * 0.15:
                    weaknesses.append(("element", min_elem[1], lang, round(min_elem[0] / total * 100)))

        # 6. Overall aspect balance
        total_harmonious = sum(1 for a in chart.aspects if a.nature == "harmonious")
        total_challenging = sum(1 for a in chart.aspects if a.nature == "challenging")
        total_aspects = len(chart.aspects)
        if total_aspects >= 10:
            if total_harmonious >= total_challenging * 2:
                strengths.append(("chart", "overall_harmonious", lang, total_harmonious, total_challenging))
            elif total_challenging >= total_harmonious * 2:
                weaknesses.append(("chart", "overall_challenging", lang, total_challenging, total_harmonious))

        # Build bilingual output
        def _planet_name(name, lang):
            p = PLANETS.get(name)
            return p.name_vi if p and lang == "vi" else p.name_en if p else name

        def _sign_name(sign, lang):
            s = SIGNS.get(sign)
            return s.name_vi if s and lang == "vi" else s.name_en if s else sign

        def _elem_name(elem, lang):
            names = {"fire": ("Lửa", "Fire"), "earth": ("Đất", "Earth"), "air": ("Khí", "Air"), "water": ("Nước", "Water")}
            return names.get(elem, (elem, elem))[0 if lang == "vi" else 1]

        if lang == "vi":
            strength_lines = []
            for s in strengths:
                if s[1] == "rulership":
                    strength_lines.append(f"• {_planet_name(s[0], 'vi')} ở cung chủ tinh — vị trí mạnh nhất về bản chất")
                elif s[1] == "exaltation":
                    strength_lines.append(f"• {_planet_name(s[0], 'vi')} ở cung phò trợ (exaltation) — sức mạnh đặc biệt")
                elif s[1] == "angular_house":
                    strength_lines.append(f"• {_planet_name(s[0], 'vi')} ở Nhà {s[3]} (góc) — tầm nhìn và tác động rộng")
                elif s[1] == "harmonious_aspects":
                    strength_lines.append(f"• {_planet_name(s[0], 'vi')} có {s[3]} góc chiếu thuận lợi — năng lượng hài hòa")
                elif s[1] == "element" and s[0] == "element":
                    strength_lines.append(f"• Nguyên tố {_elem_name(s[2], 'vi')} chiếm ưu thế ({s[3]}%) — thế mạnh năng lượng")
                elif s[1] == "overall_harmonious":
                    strength_lines.append(f"• Lá số có nhiều góc chiếu thuận lợi ({s[3]} thuận, {s[4]} thách thức) — tổng thể hài hòa")

            weakness_lines = []
            for w in weaknesses:
                if w[1] == "detriment":
                    weakness_lines.append(f"• {_planet_name(w[0], 'vi')} ở cung đối địch (detriment) — yếu về bản chất")
                elif w[1] == "fall":
                    weakness_lines.append(f"• {_planet_name(w[0], 'vi')} ở cung suy yếu (fall) — khó phát huy sức mạnh")
                elif w[1] == "cadent_house":
                    weakness_lines.append(f"• {_planet_name(w[0], 'vi')} ở Nhà {w[3]} (yếu) — tầm ảnh hưởng hạn chế")
                elif w[1] == "retrograde":
                    weakness_lines.append(f"• {_planet_name(w[0], 'vi')} nghịch hành — năng lượng hướng nội, cần điều chỉnh")
                elif w[1] == "challenging_aspects":
                    weakness_lines.append(f"• {_planet_name(w[0], 'vi')} có {w[3]} góc chiếu thách thức — dễ gây căng thẳng")
                elif w[1] == "element" and w[0] == "element":
                    weakness_lines.append(f"• Nguyên tố {_elem_name(w[2], 'vi')} yếu ({w[3]}%) — cần bổ sung năng lượng")
                elif w[1] == "overall_challenging":
                    weakness_lines.append(f"• Lá số có nhiều góc chiếu thách thức ({w[3]} thách thức, {w[4]} thuận) — đòi hỏi nỗ lực")

            if not strength_lines:
                strength_lines.append("• Không có điểm mạnh nổi bật — lá số cần phát triển qua nỗ lực cá nhân.")
            if not weakness_lines:
                weakness_lines.append("• Không có điểm yếu đáng kể — các hành tinh ở vị trí tương đối ổn định.")

            text = "=== ĐIỂM MẠNH ===\n" + "\n".join(strength_lines) + "\n\n=== ĐIỂM YẾU ===\n" + "\n".join(weakness_lines)
        else:
            strength_lines = []
            for s in strengths:
                if s[1] == "rulership":
                    strength_lines.append(f"• {_planet_name(s[0], 'en')} in its ruling sign — maximum essential dignity")
                elif s[1] == "exaltation":
                    strength_lines.append(f"• {_planet_name(s[0], 'en')} in exaltation — exceptional strength")
                elif s[1] == "angular_house":
                    strength_lines.append(f"• {_planet_name(s[0], 'en')} in House {s[3]} (angular) — wide visibility and impact")
                elif s[1] == "harmonious_aspects":
                    strength_lines.append(f"• {_planet_name(s[0], 'en')} has {s[3]} harmonious aspects — easy-flowing energy")
                elif s[1] == "element" and s[0] == "element":
                    strength_lines.append(f"• {_elem_name(s[2], 'en')} element dominates ({s[3]}%) — energetic strength")
                elif s[1] == "overall_harmonious":
                    strength_lines.append(f"• Chart has many harmonious aspects ({s[3]} harmonious, {s[4]} challenging) — overall ease")

            weakness_lines = []
            for w in weaknesses:
                if w[1] == "detriment":
                    weakness_lines.append(f"• {_planet_name(w[0], 'en')} in detriment — weak essential nature")
                elif w[1] == "fall":
                    weakness_lines.append(f"• {_planet_name(w[0], 'en')} in fall — difficulty expressing strength")
                elif w[1] == "cadent_house":
                    weakness_lines.append(f"• {_planet_name(w[0], 'en')} in House {w[3]} (cadent) — limited influence")
                elif w[1] == "retrograde":
                    weakness_lines.append(f"• {_planet_name(w[0], 'en')} retrograde — internalized energy, needs adjustment")
                elif w[1] == "challenging_aspects":
                    weakness_lines.append(f"• {_planet_name(w[0], 'en')} has {w[3]} challenging aspects — potential tension")
                elif w[1] == "element" and w[0] == "element":
                    weakness_lines.append(f"• {_elem_name(w[2], 'en')} element is weak ({w[3]}%) — needs cultivation")
                elif w[1] == "overall_challenging":
                    weakness_lines.append(f"• Chart has many challenging aspects ({w[3]} challenging, {w[4]} harmonious) — requires effort")

            if not strength_lines:
                strength_lines.append("• No outstanding strengths — the chart relies on personal effort.")
            if not weakness_lines:
                weakness_lines.append("• No significant weaknesses — planets are in relatively stable positions.")

            text = "=== STRENGTHS ===\n" + "\n".join(strength_lines) + "\n\n=== WEAKNESSES ===\n" + "\n".join(weakness_lines)

        return [RuleResult(
            title_vi="Điểm Mạnh & Điểm Yếu" if lang == "vi" else "",
            title_en="Strengths & Weaknesses" if lang == "en" else "",
            text_vi=text if lang == "vi" else "",
            text_en=text if lang == "en" else "",
            score=float(total_harmonious - total_challenging),
            priority=self.priority,
            category="strength_weakness",
            tags=["strength_weakness"],
            metadata={
                "strength_count": len(strengths),
                "weakness_count": len(weaknesses),
                "strengths": [{"type": s[1], "planet": s[0]} for s in strengths],
                "weaknesses": [{"type": w[1], "planet": w[0]} for w in weaknesses],
            },
        )]


RuleRegistry.register(StrengthWeaknessRule())