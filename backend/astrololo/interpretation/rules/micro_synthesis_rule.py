"""Micro-synthesis — runs the 5-step interpretive workflow on real chart data.

Competitor auto-reports dump the five micro-steps (planet-in-house, planet
interactions, corrections, house-cusp energy, planet+sign+house blend) as
separate raw lists. This rule demonstrates the *workflow*: it picks the
chart's strongest planet and its tightest challenging aspect, then walks
steps 1->5 so the reader sees HOW the interpretation is derived — not just
the ingredients.
"""
from typing import Optional, List
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.interpretation.scoring import ChartScorer
from astrololo.interpretation.template_loader import get_planet_in_sign, get_planet_in_house
from astrololo.core.constants import PLANETS, SIGNS, HOUSES, SIGN_RULERS
from astrololo.models.chart import ChartData

_SIGN_VI = {
    "aries":"Bạch Dương","taurus":"Kim Ngưu","gemini":"Song Tử","cancer":"Cự Giải","leo":"Sư Tử","virgo":"Xử Nữ",
    "libra":"Thiên Bình","scorpio":"Bọ Cạp","sagittarius":"Nhân Mã","capricorn":"Ma Kết","aquarius":"Bảo Bình","pisces":"Song Ngư",
}
_HOUSE_VI = {1:"Góc 1 (Bản thân)",2:"Tài chính",3:"Giao tiếp",4:"Gia đình",5:"Sáng tạo",6:"Sức khỏe",
             7:"Quan hệ",8:"Tài chính sâu",9:"Tri thức",10:"Sự nghiệp",11:"Cộng đồng",12:"Tiềm thức"}


class MicroSynthesisRule(InterpretationRule):
    """Demonstrates the 5-step micro workflow on the chart's key planet."""

    def __init__(self):
        super().__init__(priority=4)

    def matches(self, chart: ChartData) -> bool:
        return bool(chart.planets) and bool(chart.aspects)

    def _body(self, chart, name):
        return next((b for b in chart.planets if b.name == name), None)

    def _pname(self, p, lang):
        pl = PLANETS.get(p.name)
        return pl.name_vi if pl and lang == "vi" else pl.name_en if pl else p.name

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[List[RuleResult]]:
        # pick the dominant planet
        scorer = ChartScorer(chart)
        rankings = scorer.get_planet_rankings()
        dom = rankings[0] if rankings else None
        pbody = self._body(chart, dom["planet"]) if dom else None
        if not pbody:
            return None

        pname = pbody.name
        p_vi = self._pname(pbody, "vi")
        p_en = self._pname(pbody, "en")
        sign_vi = _SIGN_VI.get(pbody.sign, pbody.sign)
        sign_en = SIGNS[pbody.sign].name_en
        house = pbody.house
        house_vi = _HOUSE_VI.get(house, f"Nhà {house}")
        house_en = f"House {house}"

        # step 2: interactions of this planet
        related = [a for a in chart.aspects if a.planet1 == pname or a.planet2 == pname]
        related.sort(key=lambda a: a.orb)
        key = related[0] if related else None
        key_txt = ""
        if key:
            other = key.planet2 if key.planet1 == pname else key.planet1
            ob = self._body(chart, other)
            o_vi = self._pname(ob, "vi") if ob else other
            o_en = self._pname(ob, "en") if ob else other
            key_txt = (f"{p_vi} {key.aspect_name_vi} {o_vi} (orb {key.orb:.1f}°)"
                       if lang == "vi" else
                       f"{p_en} {key.aspect_name_vi} {o_en} (orb {key.orb:.1f}°)")

        # step 3: retrograde? (BodyPosition stores the flag as is_retrograde)
        retro = getattr(pbody, "is_retrograde", False)
        retro_txt = ("đang đi lùi (retrograde)" if lang == "vi" else "is retrograde") if retro else (
            "không retrograde" if lang == "vi" else "is direct")

        # step 4: house cusp energy
        cusp_sign_idx = None
        if chart.houses and 0 < house <= len(chart.houses):
            cusp_sign_idx = chart.houses[house - 1].sign if hasattr(chart.houses[house - 1], "sign") else None
        cusp_vi = _SIGN_VI.get(cusp_sign_idx, "không xác định") if cusp_sign_idx is not None else "không xác định"
        cusp_en = SIGNS[cusp_sign_idx].name_en if cusp_sign_idx is not None else "unknown"

        # step 5: blend
        blend = get_planet_in_sign(pname, SIGNS[pbody.sign].name_en.lower(), lang) or {}
        blend_txt = (blend.get("short") or blend.get("detailed") or "")[:160]

        if lang == "vi":
            title = f"Quy Trình Luận Giải Vi Mô: {p_vi}"
            steps = (
                f"1) Phân bổ: {p_vi} nằm tại {sign_vi}, Nhà {house} ({house_vi}).\n"
                f"2) Tương tác: {key_txt if key_txt else 'hành tinh này ít góc chiếu nổi bật'}.\n"
                f"3) Đã chỉnh sửa: {p_vi} {retro_txt}.\n"
                f"4) Năng lượng hoàng đạo của nhà: Nhà {house} có đỉnh cung {cusp_vi}, "
                f"tạo nền tảng năng lượng riêng cho vị trí này.\n"
                f"5) Kết hợp: {p_vi} mang năng lượng {sign_vi} ("
                f"{blend_txt[:80]}...) hòa vào lĩnh vực {house_vi}. "
                f"Tức là cách {p_vi} bộc lộ không chỉ do bản thân nó, mà do sự pha trộn "
                f"giữa tính chất cung {sign_vi} và môi trường nhà {house}."
            )
            closing = (f"Quy trình này lặp lại cho mọi hành tinh — đây là một ví dụ điển hình với {p_vi}, "
                       f"hành tinh chi phối nhất lá số.")
        else:
            title = f"Micro-Interpretation Workflow: {p_en}"
            steps = (
                f"1) Placement: {p_en} is in {sign_en}, House {house} ({house_en}).\n"
                f"2) Interaction: {key_txt if key_txt else 'few prominent aspects'}.\n"
                f"3) Correction: {p_en} {retro_txt}.\n"
                f"4) House cusp energy: House {house} has cusp in {cusp_en}, giving this placement its base tone.\n"
                f"5) Blend: {p_en} carries {sign_en} energy merged into the {house_en} sphere — "
                f"how it expresses comes from the mix of sign nature and house environment."
            )
            closing = (f"This workflow repeats for every planet; this is the canonical example using {p_en}, "
                       f"the chart's dominant planet.")

        text = steps + "\n\n" + closing
        ev = [f"{p_vi}: {sign_vi} / Nhà {house}",
              f"Góc: {key_txt}" if key_txt else f"{p_vi}: ít góc nổi bật",
              f"{p_vi} {retro_txt}"]

        return [RuleResult(
            title_vi=title if lang == "vi" else "",
            title_en=title if lang == "en" else "",
            text_vi=text if lang == "vi" else "",
            text_en=text if lang == "en" else "",
            score=7.0,
            priority=self.priority,
            category="micro_synthesis",
            tags=["micro", pname],
            evidence=ev,
            metadata={"planet": pname, "sign": pbody.sign, "house": house,
                      "retrograde": retro, "key_aspect": key_txt},
        )]


RuleRegistry.register(MicroSynthesisRule())
