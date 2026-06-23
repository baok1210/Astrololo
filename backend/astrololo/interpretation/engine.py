from typing import List, Dict, Any, Optional
from astrololo.models.chart import ChartData, InterpretationResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.interpretation.rules.base import RuleResult
from astrololo.interpretation.scoring import ChartScorer
from astrololo.interpretation.bilingual import BilingualHelper
from astrololo.core.constants import ELEMENT_SIGNS
from astrololo.interpretation.template_loader import set_esoteric_mode


class InterpretationEngine:
    def __init__(self, lang: str = "vi", esoteric: bool = True):
        self.lang = lang
        self.esoteric = esoteric
        self.bh = BilingualHelper(lang)

    def interpret(self, chart: ChartData) -> InterpretationResult:
        set_esoteric_mode(self.esoteric)
        rules = RuleRegistry.get_rules()
        scorer = ChartScorer(chart)

        self._enrich_chart(chart)

        all_results: List[RuleResult] = []
        for rule in rules:
            if rule.matches(chart):
                result = rule.interpret(chart, self.lang)
                if isinstance(result, list):
                    all_results.extend(r for r in result if r)
                elif result:
                    all_results.append(result)

        all_results.sort(key=lambda r: (r.priority, r.score), reverse=True)

        sections: List[Dict[str, Any]] = []
        categorized: Dict[str, List[RuleResult]] = {}
        for r in all_results:
            cat = r.category
            if cat not in categorized:
                categorized[cat] = []
            limit = 50 if cat == "aspect" else 20 if cat in ("planet_in_sign", "planet_in_house", "house_cusp") else 12 if cat == "house_placement" else 10 if cat in ("synthesis", "part_of_fortune", "aspect_synthesis") else 5
            if len(categorized[cat]) < limit:
                categorized[cat].append(r)

        section_order = [
            "synthesis",
            "sun_moon",
            "dominant_planet",
            "part_of_fortune",
            "dispositor",
            "pattern",
            "combination",
            "house_placement",
            "house_distribution",
            "dignity",
            "element",
            "quality",
            "planet_in_sign",
            "planet_in_house",
            "house_cusp",
            "aspect",
            "aspect_synthesis",
            "midpoints",
        ]

        for cat in section_order:
            if cat in categorized:
                section = self._make_section(cat, categorized[cat])
                if section:
                    sections.append(section)

        overall = self._generate_overview(chart, all_results, scorer)

        return InterpretationResult(
            chart_summary=self._make_chart_summary(chart),
            planet_interpretations=[
                r.metadata
                for r in all_results
                if r.category in ("planet_in_sign", "dignity")
            ],
            aspect_interpretations=[
                r.metadata for r in all_results if r.category == "aspect"
            ],
            pattern_interpretations=[
                r.metadata for r in all_results if r.category == "pattern"
            ],
            element_interpretations=[
                r.metadata for r in all_results if r.category == "element"
            ],
            dispositor_interpretation=self._make_dispositor_text(
                categorized.get("dispositor", [])
            ),
            overall_interpretation=overall,
            sections=sections,
        )

    def _make_section(
        self, category: str, results: List[RuleResult]
    ) -> Optional[Dict[str, Any]]:
        if not results:
            return None
        category_titles = {
            "synthesis": ("Tổng Hợp Đa Yếu Tố", "Multi-Factor Synthesis"),
            "sun_moon": ("Kết Hợp Mặt Trời - Mặt Trăng", "Sun-Moon Combination"),
            "dominant_planet": ("Hành Tinh Nổi Bật", "Dominant Planets"),
            "part_of_fortune": ("Phần Tài Lộc", "Part of Fortune"),
            "dispositor": ("Chuỗi Chủ Tinh", "Dispositor Chain"),
            "pattern": ("Cấu Hình Đặc Biệt", "Aspect Patterns"),
            "combination": ("Kết Hợp Sao-Cung-Nhà", "Planet-Sign-House Combinations"),
            "house_placement": ("Bảng Vị Trí & Ý Nghĩa Nhà", "House System Placement Table"),
            "house_distribution": ("Phân Bố Hành Tinh Theo Nhà", "Planet Distribution by House"),
            "dignity": ("Sức Mạnh Hành Tinh", "Planetary Dignities"),
            "element": ("Cân Bằng Nguyên Tố", "Element Balance"),
            "quality": ("Phân Bố Năng Lượng Hoàng Đạo", "Zodiacal Energy Distribution"),
            "planet_in_sign": ("Hành Tinh Trong Cung", "Planets in Signs"),
            "planet_in_house": ("Hành Tinh Trong Nhà", "Planets in Houses"),
            "house_cusp": ("Ý Nghĩa Đỉnh Nhà", "House Cusp Meanings"),
            "aspect": ("Các Góc Chiếu", "Aspects"),
            "aspect_synthesis": ("Tổng Hợp Góc Chiếu Theo Hành Tinh", "Per-Planet Aspect Synthesis"),
            "midpoints": ("Trung Điểm", "Midpoints"),
        }
        idx = 0 if self.lang == "vi" else 1
        title = category_titles.get(category, ("", ""))
        section_title = title[idx] if isinstance(title, tuple) else title

        items = []
        for r in results:
            text = r.text_vi if self.lang == "vi" else r.text_en
            item = {
                "title": r.title_vi if self.lang == "vi" else r.title_en,
                "text": text,
                "score": r.score,
                "tags": r.tags,
            }
            if r.metadata:
                item["metadata"] = r.metadata
            items.append(item)

        return {
            "category": category,
            "title": section_title,
            "items": items,
        }

    def _make_chart_summary(self, chart: ChartData) -> Dict[str, Any]:
        asc_sign = chart.ascendant_sign
        return {
            "name": chart.subject_name,
            "type": chart.chart_type,
            "ascendant": f"{chart.ascendant:.2f}°",
            "ascendant_sign": self.bh.sign(asc_sign) if asc_sign else "",
            "mc": f"{chart.mc:.2f}°",
            "mc_sign": self.bh.sign(chart.mc_sign) if chart.mc_sign else "",
            "house_system": chart.house_system,
            "is_daytime": chart.is_daytime,
            "planet_count": len(chart.planets),
            "aspect_count": len(chart.aspects),
        }

    def _make_dispositor_text(self, results: List[RuleResult]) -> Optional[str]:
        if not results:
            return None
        r = results[0]
        return r.text_vi if self.lang == "vi" else r.text_en

    def _generate_overview(
        self, chart: ChartData, results: List[RuleResult], scorer: ChartScorer
    ) -> str:
        score_info = scorer.score_chart()
        parts = []

        # Paragraph 1: Ascendant + MC
        if chart.ascendant_sign:
            asc_name = self.bh.sign(chart.ascendant_sign)
            if self.lang == "vi":
                asc_line = f"Cung Mọc (Ascendant) của bạn là {asc_name} — 'chiếc mặt nạ' bạn thể hiện ra thế giới bên ngoài, ấn tượng đầu tiên bạn để lại cho người khác."
            else:
                asc_line = f"Your Ascendant is {asc_name} — the 'mask' you show to the world, the first impression you leave on others."
            if chart.mc_sign:
                mc_name = self.bh.sign(chart.mc_sign)
                if self.lang == "vi":
                    asc_line += f" Thiên Đỉnh (MC) của bạn ở {mc_name}, định hướng sự nghiệp và vị thế xã hội của bạn."
                else:
                    asc_line += f" Your Midheaven (MC) is in {mc_name}, pointing toward your career path and public standing."
            parts.append(asc_line)

        # Paragraph 2: Element distribution
        if chart.element_distribution:
            ed = chart.element_distribution
            if ed.dominant:
                elem_name = self.bh.element(ed.dominant)
                if self.lang == "vi":
                    total = ed.fire + ed.earth + ed.air + ed.water
                    pcts = {k: round(v/total*100) for k, v in {"fire": ed.fire, "earth": ed.earth, "air": ed.air, "water": ed.water}.items() if total > 0}
                    elem_parts = [f"{self.bh.element(k)} {pct}%" for k, pct in sorted(pcts.items(), key=lambda x: -x[1]) if pct > 0]
                    line = f"Lá số của bạn nghiêng về nguyên tố {elem_name} ({elem_parts[0]} trong tổng thể). "
                    line += f"Phân bố: {', '.join(elem_parts)}."
                    if ed.deficient and ed.deficient != ed.dominant:
                        def_name = self.bh.element(ed.deficient)
                        line += f" Nguyên tố {def_name} yếu hơn, có thể bạn cần bổ sung năng lượng này qua các mối quan hệ hoặc sở thích."
                    parts.append(line)
                else:
                    total = ed.fire + ed.earth + ed.air + ed.water
                    elem_parts = [f"{k} {round(v/total*100)}%" for k, v in {"fire": ed.fire, "earth": ed.earth, "air": ed.air, "water": ed.water}.items() if total > 0 and v > 0]
                    line = f"The {elem_name} element dominates your chart ({elem_parts[0]} overall). "
                    line += f"Distribution: {', '.join(elem_parts)}."
                    if ed.deficient and ed.deficient != ed.dominant:
                        line += f" The {self.bh.element(ed.deficient)} element is less present, which you may need to cultivate through relationships or activities."
                    parts.append(line)

        # Paragraph 3: Quality distribution
        if chart.quality_distribution:
            qd = chart.quality_distribution
            if qd.dominant:
                qual_name = self.bh.quality(qd.dominant)
                if self.lang == "vi":
                    line = f"Về chất lượng, nhóm {qual_name} chiếm ưu thế trong lá số của bạn. "
                    if qd.dominant == "cardinal":
                        line += "Điều này cho thấy bạn có xu hướng chủ động, khởi xướng và dẫn dắt."
                    elif qd.dominant == "fixed":
                        line += "Điều này cho thấy bạn có sự kiên định, bền bỉ và tập trung."
                    elif qd.dominant == "mutable":
                        line += "Điều này cho thấy bạn linh hoạt, dễ thích nghi và đa năng."
                    parts.append(line)
                else:
                    line = f"In terms of modality, {qual_name} qualities are strongest in your chart. "
                    if qd.dominant == "cardinal":
                        line += "This suggests you are proactive, initiating, and leadership-oriented."
                    elif qd.dominant == "fixed":
                        line += "This suggests you are determined, persistent, and focused."
                    elif qd.dominant == "mutable":
                        line += "This suggests you are adaptable, flexible, and versatile."
                    parts.append(line)

        # Paragraph 4: Chart strength + day/night + major themes
        strength = score_info.get("strength", "moderate")
        strength_map = {
            "exceptional": ("Lá số của bạn có sức mạnh đặc biệt, với nhiều yếu tố hỗ trợ lẫn nhau.",
                           "Your chart has exceptional strength, with many supportive factors working together."),
            "strong": ("Lá số của bạn khá mạnh với sự cân bằng tốt giữa các yếu tố.",
                      "Your chart is quite strong with good balance between different factors."),
            "moderate": ("Lá số của bạn có sự kết hợp hài hòa giữa thách thức và cơ hội.",
                        "Your chart shows a harmonious mix of challenges and opportunities."),
            "challenging": ("Lá số của bạn có nhiều thách thức, nhưng đó là động lực để trưởng thành.",
                          "Your chart has many challenges, but these are drivers for growth."),
            "difficult": ("Lá số của bạn có nhiều góc cạnh khó khăn, đòi hỏi nỗ lực vượt qua.",
                         "Your chart has many difficult aspects, requiring effort to overcome."),
        }
        s_vi, s_en = strength_map.get(strength, strength_map["moderate"])

        # Count retrogrades
        retro_count = sum(1 for p in chart.planets if p.is_retrograde)
        if self.lang == "vi":
            strength_text = s_vi
            if chart.is_daytime:
                strength_text += " Đây là lá số ban ngày, các hành tinh xã hội và Mặt Trời có lợi thế hơn."
            else:
                strength_text += " Đây là lá số ban đêm, Mặt Trăng và các hành tinh nội tâm có lợi thế hơn."
            if retro_count > 0:
                strength_text += f" Có {retro_count} hành tinh nghịch hành, cho thấy những lĩnh vực bạn cần nhìn lại và điều chỉnh."
        else:
            strength_text = s_en
            if chart.is_daytime:
                strength_text += " This is a day chart, giving advantage to social planets and the Sun."
            else:
                strength_text += " This is a night chart, giving advantage to the Moon and inner planets."
            if retro_count > 0:
                strength_text += f" {retro_count} planets are retrograde, indicating areas where you need to review and adjust."
        parts.append(strength_text)

        # Paragraph 5: Dispositor chain (if interesting)
        if chart.dispositor and chart.dispositor.final_dispositors:
            finals = chart.dispositor.final_dispositors
            frs = chart.dispositor.mutual_receptions
            planet_names = {p.name: p.name_vi for p in chart.planets}
            if self.lang == "vi":
                f_vi = [planet_names.get(f, f) for f in finals]
                if len(finals) == 1:
                    parts.append(f"Chuỗi chủ tinh hội tụ về {f_vi[0]}, đây là hành tinh chủ đạo chi phối toàn bộ lá số của bạn.")
                else:
                    parts.append(f"Có {len(finals)} hành tinh chủ đạo cuối cùng: {', '.join(f_vi)}, cùng nhau chi phối lá số của bạn.")
                if frs:
                    parts.append("Ngoài ra, có hiện tượng tương nhận giữa các chủ tinh, tạo sự hỗ trợ qua lại mạnh mẽ.")
            else:
                if len(finals) == 1:
                    parts.append(f"The dispositor chain culminates in {finals[0]}, the dominant planet governing your entire chart.")
                else:
                    parts.append(f"There are {len(finals)} final dispositors: {', '.join(finals)}, co-governing your chart.")
                if frs:
                    parts.append("Mutual receptions exist between rulers, creating strong mutual support.")

        return "\n\n".join(p for p in parts if p)

    def _enrich_chart(self, chart: ChartData):
        if chart.element_distribution is None:
            fire = earth = air = water = 0
            for p in chart.planets:
                sign = p.sign
                if sign in ELEMENT_SIGNS["fire"]:
                    fire += 1
                elif sign in ELEMENT_SIGNS["earth"]:
                    earth += 1
                elif sign in ELEMENT_SIGNS["air"]:
                    air += 1
                elif sign in ELEMENT_SIGNS["water"]:
                    water += 1

            elem_counts = {"fire": fire, "earth": earth, "air": air, "water": water}
            dominant = max(elem_counts, key=elem_counts.get)
            deficient = min(elem_counts, key=elem_counts.get)

            from astrololo.models.chart import ElementDistribution

            chart.element_distribution = ElementDistribution(
                fire=fire,
                earth=earth,
                air=air,
                water=water,
                dominant=dominant if max(elem_counts.values()) > 0 else None,
                deficient=deficient if max(elem_counts.values()) > 0 else None,
            )

        if chart.dispositor is None:
            from astrololo.models.chart import DispositorResult
            from astrololo.core.constants import SIGN_RULERS, SIGN_MODERN_RULERS

            chain = {}
            for p in chart.planets:
                ruler = SIGN_RULERS.get(p.sign, "")
                chain[p.name] = ruler

            final = [
                p_name
                for p_name, r in chain.items()
                if r == p_name
                or SIGN_MODERN_RULERS.get(
                    next(p2.sign for p2 in chart.planets if p2.name == p_name)
                )
                == p_name
            ]
            mutual = []
            for p1 in chain:
                for p2 in chain:
                    if p1 < p2 and chain[p1] == p2 and chain[p2] == p1:
                        mutual.append((p1, p2))

            chart.dispositor = DispositorResult(
                chain=chain,
                final_dispositor=final[0] if final else None,
                final_dispositors=final,
                mutual_receptions=mutual,
            )
