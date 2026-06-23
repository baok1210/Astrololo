"""Multi-factor synthesis rule — combines multiple chart factors into unified interpretations."""
from typing import Optional, List, Dict
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.interpretation.scoring import ChartScorer
from astrololo.interpretation.template_loader import _load_yaml
from astrololo.interpretation.keywords import (
    get_sign_short_description,
    get_sign_keywords,
    get_house_keywords,
    get_planet_function,
    HOUSE_NAME_VI,
    SIGN_NAME_VI,
)
from astrololo.models.chart import ChartData
from astrololo.core.constants import (
    PLANETS, SIGNS, HOUSES, SIGN_RULERS,
)

_HOUSE_TYPE_LABEL_VI = {1: "nhà góc", 2: "nhà kế", 3: "nhà cuối"}
_HOUSE_TYPE_LABEL_EN = {1: "angular house", 2: "succedent house", 3: "cadent house"}

_QUALITY_NAME_VI = {"cardinal": "Thống Lĩnh", "fixed": "Cố Định", "mutable": "Linh Hoạt"}
_ELEMENT_NAME_VI = {"fire": "Lửa", "earth": "Đất", "air": "Khí", "water": "Nước"}
_HOUSE_TYPE_VI = {"angular": "nhà góc", "succedent": "nhà kế", "cadent": "nhà cuối"}
_HOUSE_TYPE_EN = {"angular": "angular", "succedent": "succedent", "cadent": "cadent"}


class SynthesisRule(InterpretationRule):
    """Detects cross-factor patterns and generates unified interpretations."""

    def __init__(self):
        super().__init__(priority=2)

    def matches(self, chart: ChartData) -> bool:
        return bool(chart.planets) and bool(chart.houses)

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[List[RuleResult]]:
        results = []
        tpl = _load_yaml(lang, "synthesis.yaml")

        self._make_asc_ruler(chart, lang, tpl, results)
        self._make_sun_moon(chart, lang, tpl, results)
        self._make_dominant_planet(chart, lang, tpl, results)
        self._make_conjunction_cluster(chart, lang, tpl, results)
        self._make_element_quality_house(chart, lang, tpl, results)

        return results if results else None

    def _body(self, chart, name):
        return next((b for b in chart.planets if b.name == name), None)

    def _planet_name(self, p, lang):
        pl = PLANETS.get(p.name)
        return pl.name_vi if pl and lang == "vi" else pl.name_en if pl else p.name

    # ─── Pattern 1: ASC Ruler Analysis ────────────────────────────────────

    def _make_asc_ruler(self, chart, lang, tpl, results):
        asc_sign = chart.ascendant_sign
        if not asc_sign:
            return
        ruler_key = SIGN_RULERS.get(asc_sign, "")
        if not ruler_key:
            return

        ruler_body = self._body(chart, ruler_key)
        if not ruler_body:
            return

        asc_name = SIGN_NAME_VI.get(asc_sign, asc_sign)
        ruler_name = self._planet_name(ruler_body, lang)
        ruler_sign = SIGN_NAME_VI.get(ruler_body.sign, ruler_body.sign)
        rh = ruler_body.house
        ht = HOUSES.get(rh)
        ht_label = _HOUSE_TYPE_VI.get(ht.type_, "") if ht and lang == "vi" else _HOUSE_TYPE_EN.get(ht.type_, "")
        house_label = HOUSE_NAME_VI.get(rh, f"Nhà {rh}") if lang == "vi" else f"House {rh}"

        # Ruler description
        func = get_planet_function(ruler_key)
        ruler_short = func.split(".")[0] + "." if func else ""
        if lang == "vi":
            ruler_short = func.split(".")[0] + "." if func else ""

        # Sign keywords for ASC
        asc_data = get_sign_keywords(asc_sign)
        pos_kw = asc_data.get("positive", [])[:3]
        core_kw = asc_data.get("core", [])[:2]
        kw_list = pos_kw + core_kw
        sign_kw = "; ".join(kw_list[:4]) if kw_list else ""
        if lang == "vi":
            sign_kw = "; ".join(kw_list[:4]) if kw_list else ""

        # House keywords
        h_data = get_house_keywords(rh)
        h_kw_list = h_data.get("keywords", [])[:4]
        h_kw = "; ".join(h_kw_list) if h_kw_list else ""

        # Get template key based on house type
        type_key_map = {"angular": "asc_ruler_angular", "succedent": "asc_ruler_succedent", "cadent": "asc_ruler_cadent"}
        tpl_key = type_key_map.get(ht.type_, "asc_ruler_cadent")

        if lang == "vi":
            title = f"Cung Mọc {asc_name} — Chủ Tinh {ruler_name} tại {house_label}"
        else:
            title = f"Ascendant {asc_name} — Ruler {ruler_name} in {house_label}"

        raw = tpl.get(tpl_key, "")
        if not raw:
            return

        text = raw.format(
            asc_sign=asc_name,
            ruler_name=ruler_name,
            ruler_sign=ruler_sign,
            ruler_house=rh,
            ruler_house_ordinal=self._ordinal(rh, lang),
            house_type_text=ht_label,
            ruler_short_desc=ruler_short,
            sign_kw=sign_kw,
            house_kw=h_kw,
        )

        results.append(RuleResult(
            title_vi=title if lang == "vi" else "",
            title_en=title if lang == "en" else "",
            text_vi=text if lang == "vi" else "",
            text_en=text if lang == "en" else "",
            score=8.0,
            priority=self.priority,
            category="synthesis",
            tags=["asc_ruler", asc_sign, ruler_key, f"house_{rh}"],
            metadata={"pattern": "asc_ruler", "asc_sign": asc_sign, "ruler": ruler_key, "ruler_house": rh},
        ))

    # ─── Pattern 2: Sun-Moon Synthesis ────────────────────────────────────

    def _make_sun_moon(self, chart, lang, tpl, results):
        sun = self._body(chart, "sun")
        moon = self._body(chart, "moon")
        if not sun or not moon:
            return

        s_sign = sun.sign
        m_sign = moon.sign
        s_name = SIGN_NAME_VI.get(s_sign, s_sign)
        m_name = SIGN_NAME_VI.get(m_sign, m_sign)
        s_short = get_sign_short_description(s_sign)
        m_short = get_sign_short_description(m_sign)

        s_data = get_sign_keywords(s_sign)
        m_data = get_sign_keywords(m_sign)
        s_core = "; ".join(s_data.get("core", [])[:2])
        m_core = "; ".join(m_data.get("core", [])[:2])

        # Determine compatibility
        s_elem = SIGNS.get(s_sign)
        m_elem = SIGNS.get(m_sign)
        same_elem = s_elem and m_elem and s_elem.element == m_elem.element
        elem_harmony = s_elem and m_elem and (
            (s_elem.element, m_elem.element) in [("fire", "air"), ("air", "fire"),
             ("earth", "water"), ("water", "earth")]
        )

        if lang == "vi":
            if s_sign == m_sign:
                synthesis_text = "tạo nên sự thống nhất hiếm có giữa ý thức và cảm xúc"
                closing = "Bạn là người nhất quán, biết mình muốn gì và cảm thấy thế nào."
            elif same_elem:
                synthesis_text = f"tăng cường năng lượng {_ELEMENT_NAME_VI.get(s_elem.element, '')}: cả lý trí và tình cảm đều hướng về cùng một hướng"
                closing = "Sự hòa hợp giữa ý chí và cảm xúc giúp bạn kiên định và tập trung."
            elif elem_harmony:
                synthesis_text = "bổ sung cho nhau: lý trí và cảm xúc hỗ trợ lẫn một cách hài hòa"
                closing = "Bạn có khả năng cân bằng giữa hành động và cảm xúc."
            else:
                synthesis_text = "tạo ra sự căng thẳng sáng tạo giữa ý thức và cảm xúc"
                closing = "Thách thức giúp bạn phát triển toàn diện hơn."
        else:
            synthesis_text = "creates a unique dynamic between your conscious and emotional selves"
            closing = ""

        raw = tpl.get("sun_moon_synthesis", "")
        if not raw:
            return

        text = raw.format(
            sun_sign=s_name, moon_sign=m_name,
            sun_short_desc=s_short, moon_short_desc=m_short,
            sun_core=s_core, moon_core=m_core,
            synthesis_text=synthesis_text, closing=closing,
        )

        results.append(RuleResult(
            title_vi=f"Mặt Trời {s_name} — Mặt Trăng {m_name}" if lang == "vi" else "",
            title_en=f"Sun in {s_name} — Moon in {m_name}" if lang == "en" else "",
            text_vi=text if lang == "vi" else "",
            text_en=text if lang == "en" else "",
            score=7.0,
            priority=self.priority,
            category="synthesis",
            tags=["sun_moon", s_sign, m_sign],
            metadata={"pattern": "sun_moon", "sun_sign": s_sign, "moon_sign": m_sign},
        ))

    # ─── Pattern 3: Dominant Planet ──────────────────────────────────────

    def _make_dominant_planet(self, chart, lang, tpl, results):
        scorer = ChartScorer(chart)
        rankings = scorer.get_planet_rankings()
        if not rankings:
            return

        top = rankings[0]
        pname = top["planet"]
        pbody = self._body(chart, pname)
        if not pbody or pbody.body_type != "planet":
            return

        sign_name = SIGN_NAME_VI.get(pbody.sign, pbody.sign)
        house_label = HOUSE_NAME_VI.get(pbody.house, f"Nhà {pbody.house}")
        dignity_label = top.get("label", "neutral")

        # Count aspects
        harm = sum(1 for a in chart.aspects
                    if (a.planet1 == pname or a.planet2 == pname) and a.nature == "harmonious")
        chall = sum(1 for a in chart.aspects
                     if (a.planet1 == pname or a.planet2 == pname) and a.nature == "challenging")
        total_aspects = harm + chall

        p = PLANETS.get(pname)
        planet_name = p.name_vi if p and lang == "vi" else p.name_en if p else pname
        func = get_planet_function(pname)
        planet_short = func.split(".")[0] + "." if func else ""

        dignity_text = {"very_strong": "rất mạnh", "strong": "mạnh", "neutral": "trung bình",
                        "weak": "yếu", "very_weak": "rất yếu"}
        dt = dignity_text.get(dignity_label, dignity_label) if lang == "vi" else dignity_label

        if lang == "vi":
            if top["total"] >= 8:
                closing = "Đây là hành tinh chủ chốt chi phối toàn bộ lá số của bạn."
            else:
                closing = "Hành tinh này đóng vai trò quan trọng trong cấu trúc lá số của bạn."
        else:
            closing = "This planet plays a key role in your chart."

        raw = tpl.get("dominant_planet", "")
        if not raw:
            return

        text = raw.format(
            planet_name=planet_name,
            sign_name=sign_name,
            house=top.get("house", top.get("planet", "")),
            house_label=house_label,
            dignity_label=dignity_label,
            dignity_text=dt,
            aspect_count=total_aspects,
            harmonious_count=harm,
            challenging_count=chall,
            planet_short_desc=planet_short,
            planet_closing=closing,
        )

        results.append(RuleResult(
            title_vi=f"Hành Tinh Nổi Bật: {planet_name}" if lang == "vi" else "",
            title_en=f"Dominant Planet: {planet_name}" if lang == "en" else "",
            text_vi=text if lang == "vi" else "",
            text_en=text if lang == "en" else "",
            score=float(top["total"]),
            priority=self.priority,
            category="synthesis",
            tags=["dominant_planet", pname],
            metadata={"pattern": "dominant_planet", "planet": pname, "score": top["total"]},
        ))

    # ─── Pattern 4: Conjunction Cluster (Stellium) ────────────────────────

    def _make_conjunction_cluster(self, chart, lang, tpl, results):
        # Find 3+ planets in same sign
        sign_groups: Dict[str, list] = {}
        for b in chart.planets:
            if b.body_type != "planet":
                continue
            sign_groups.setdefault(b.sign, []).append(b)

        best_sign = None
        best_planets = []
        for sign, planets in sign_groups.items():
            if len(planets) >= 3 and len(planets) > len(best_planets):
                best_sign = sign
                best_planets = planets

        if not best_sign or len(best_planets) < 3:
            return

        # Also check house clusters
        house_groups: Dict[int, list] = {}
        for b in chart.planets:
            if b.body_type != "planet":
                continue
            house_groups.setdefault(b.house, []).append(b)

        best_house = None
        best_house_planets = []
        for hn, planets in house_groups.items():
            if len(planets) >= 3 and len(planets) > len(best_house_planets):
                best_house = hn
                best_house_planets = planets

        # Choose the most impressive cluster
        use_sign = len(best_planets) >= (len(best_house_planets) if best_house_planets else 0)

        if use_sign:
            cluster_sign = best_sign
            cluster_planets = best_planets
            cluster_sign_name = SIGN_NAME_VI.get(cluster_sign, cluster_sign)
            sign_data = get_sign_keywords(cluster_sign)
            theme = "; ".join(sign_data.get("core", [])[:2])
            strengths = "; ".join(sign_data.get("positive", [])[:3])
            challenges = "; ".join(sign_data.get("negative", [])[:3])

            names = [self._planet_name(p, lang) for p in cluster_planets]
            planets_str = ", ".join(names)

            if lang == "vi":
                location = f"cung {cluster_sign_name}"
                theme_desc = f"Những hành tinh này cùng mang năng lượng {cluster_sign_name}: {theme}"
                strengths_text = strengths or "sự tập trung năng lượng"
                challenges_text = challenges or "cần cân bằng giữa các hành tinh"
            else:
                location = f"sign {cluster_sign_name}"
                theme_desc = f"These planets share the {cluster_sign_name} energy: {theme}"
                strengths_text = strengths or "focused energy"
                challenges_text = challenges or "need for balance"
        else:
            cluster_planets = best_house_planets
            hn = best_house
            cluster_sign_name = ""

            names_list = []
            for p in cluster_planets:
                n = self._planet_name(p, lang)
                names_list.append(f"{n} ({SIGN_NAME_VI.get(p.sign, p.sign)})")
            planets_str = ", ".join(names_list)

            house_label = HOUSE_NAME_VI.get(hn, f"Nhà {hn}") if lang == "vi" else f"House {hn}"
            h_data = get_house_keywords(hn)
            theme_kw = "; ".join(h_data.get("keywords", [])[:3]) if h_data else ""

            if lang == "vi":
                location = f"Nhà {hn} ({house_label})"
                theme_desc = f"Năng lượng dồn vào lĩnh vực {house_label}: {theme_kw}"
                strengths_text = f"khả năng tập trung cao độ vào {house_label}"
                challenges_text = "cần mở rộng ra các lĩnh vực khác"
            else:
                location = f"House {hn} ({house_label})"
                theme_desc = f"Energy concentrated in {house_label}: {theme_kw}"
                strengths_text = f"ability to intensely focus on {house_label}"
                challenges_text = "need to branch out into other areas"

        raw = tpl.get("conjunction_cluster", "")
        if not raw:
            return

        text = raw.format(
            location=location,
            planets_list=planets_str,
            theme_desc=theme_desc,
            strengths=strengths_text,
            challenges=challenges_text,
        )

        results.append(RuleResult(
            title_vi="Cụm Hội Tụ (Stellium)" if lang == "vi" else "",
            title_en="Conjunction Cluster (Stellium)" if lang == "en" else "",
            text_vi=text if lang == "vi" else "",
            text_en=text if lang == "en" else "",
            score=float(len(cluster_planets) * 2),
            priority=self.priority,
            category="synthesis",
            tags=["conjunction_cluster", "stellium"],
            metadata={"pattern": "conjunction_cluster", "planets": [p.name for p in cluster_planets], "location": best_sign or f"house_{best_house}"},
        ))

    # ─── Pattern 5: Element + Quality + House Type Synthesis ──────────────

    def _make_element_quality_house(self, chart, lang, tpl, results):
        ed = chart.element_distribution
        qd = chart.quality_distribution
        if not ed or not qd:
            return

        total_planets = len([p for p in chart.planets if p.body_type == "planet"])
        if total_planets == 0:
            return

        # Element analysis
        elem_map = {"fire": ed.fire, "earth": ed.earth, "air": ed.air, "water": ed.water}
        dom_elem = max(elem_map, key=elem_map.get)
        elem_pct = int(elem_map[dom_elem] / total_planets * 100)

        # Quality analysis
        qual_map = {"cardinal": qd.cardinal, "fixed": qd.fixed, "mutable": qd.mutable}
        dom_qual = max(qual_map, key=qual_map.get)
        qual_pct = int(qual_map[dom_qual] / total_planets * 100)

        # House type analysis
        type_counts = {"angular": 0, "succedent": 0, "cadent": 0}
        for b in chart.planets:
            if b.body_type != "planet":
                continue
            h = HOUSES.get(b.house)
            if h:
                type_counts[h.type_] += 1
        dom_type = max(type_counts, key=type_counts.get)
        house_pct = int(type_counts[dom_type] / total_planets * 100) if total_planets else 0

        if lang == "vi":
            en = _ELEMENT_NAME_VI
            qn = _QUALITY_NAME_VI
            hn = _HOUSE_TYPE_VI
            element_desc = f"nguyên tố {en[dom_elem]}"
            quality_desc = f"nhóm {qn[dom_qual]}"
            house_type_desc = f"{hn[dom_type]}"

            # Closing texts
            elem_closings = {
                "fire": "Bạn có động lực và nhiệt huyết mạnh mẽ, hãy cân bằng với sự kiên nhẫn.",
                "earth": "Bạn thực tế và đáng tin cậy, hãy mở lòng với những ý tưởng mới.",
                "air": "Bạn thông minh và giao tiếp giỏi, hãy kết nối với cảm xúc nhiều hơn.",
                "water": "Bạn nhạy cảm và trực giác tốt, hãy bảo vệ ranh giới cảm xúc của mình.",
            }
            qual_closings = {
                "cardinal": "Bạn có khả năng khởi xướng và lãnh đạo tự nhiên.",
                "fixed": "Sự kiên định và bền bỉ là điểm mạnh lớn nhất của bạn.",
                "mutable": "Khả năng thích nghi và linh hoạt giúp bạn vượt qua mọi thử thách.",
            }
            house_closings = {
                "angular": "Bạn có tác động mạnh đến môi trường xung quanh.",
                "succedent": "Bạn xây dựng giá trị bền vững qua thời gian.",
                "cadent": "Trí tuệ và khả năng phân tích là vũ khí mạnh nhất của bạn.",
            }
            combined_closings = {
                ("fire", "cardinal"): "Bạn là người tiên phong, dám nghĩ dám làm.",
                ("fire", "fixed"): "Bạn có nhiệt huyết và ý chí sắt đá.",
                ("fire", "mutable"): "Sáng tạo và linh hoạt là thế mạnh của bạn.",
                ("earth", "cardinal"): "Bạn xây dựng sự nghiệp vững chắc từ thực tế.",
                ("earth", "fixed"): "Bạn đáng tin cậy và không gì lay chuyển nổi.",
                ("earth", "mutable"): "Bạn áp dụng kiến thức vào thực tiễn hiệu quả.",
                ("air", "cardinal"): "Bạn dẫn dắt bằng trí tuệ và tầm nhìn.",
                ("air", "fixed"): "Bạn có tư duy độc lập và không dễ bị ảnh hưởng.",
                ("air", "mutable"): "Bạn giao tiếp linh hoạt và kết nối mọi người.",
                ("water", "cardinal"): "Trực giác dẫn dắt hành động của bạn.",
                ("water", "fixed"): "Cảm xúc của bạn sâu sắc và mãnh liệt.",
                ("water", "mutable"): "Bạn thấu hiểu cảm xúc và dễ thích nghi.",
            }
        else:
            element_desc = dom_elem
            quality_desc = dom_qual
            house_type_desc = dom_type
            elem_closings = {}
            qual_closings = {}
            house_closings = {}
            combined_closings = {}

        raw = tpl.get("element_quality_house", "")
        if not raw:
            return

        text = raw.format(
            element_desc=element_desc, elem_pct=elem_pct,
            quality_desc=quality_desc, qual_pct=qual_pct,
            house_type_desc=house_type_desc, house_pct=house_pct,
            element_closing=elem_closings.get(dom_elem, "") if lang == "vi" else "",
            quality_closing=qual_closings.get(dom_qual, "") if lang == "vi" else "",
            house_closing=house_closings.get(dom_type, "") if lang == "vi" else "",
            combined_closing=combined_closings.get((dom_elem, dom_qual), "") if lang == "vi" else "",
        )

        results.append(RuleResult(
            title_vi="Tổng Hợp Năng Lượng" if lang == "vi" else "",
            title_en="Energy Synthesis" if lang == "en" else "",
            text_vi=text if lang == "vi" else "",
            text_en=text if lang == "en" else "",
            score=float(elem_pct + qual_pct + house_pct) / 3,
            priority=self.priority,
            category="synthesis",
            tags=["element_quality_house", dom_elem, dom_qual, dom_type],
            metadata={"pattern": "element_quality_house", "element": dom_elem, "quality": dom_qual, "house_type": dom_type},
        ))

    @staticmethod
    def _ordinal(n: int, lang: str) -> str:
        if lang == "vi":
            return {1: "Nhất", 2: "Nhị", 3: "Tam", 4: "Tứ", 5: "Ngũ", 6: "Lục",
                    7: "Thất", 8: "Bát", 9: "Cửu", 10: "Thập", 11: "Thập Nhất", 12: "Thập Nhị"}.get(n, str(n))
        return {1: "First", 2: "Second", 3: "Third", 4: "Fourth", 5: "Fifth", 6: "Sixth",
                7: "Seventh", 8: "Eighth", 9: "Ninth", 10: "Tenth", 11: "Eleventh", 12: "Twelfth"}.get(n, str(n))


RuleRegistry.register(SynthesisRule())
