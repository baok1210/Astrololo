"""Dominant Planet ranking rule — separate essential vs accidental dignity."""
from typing import Optional, List
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.interpretation.scoring import ChartScorer
from astrololo.interpretation.keywords import get_planet_function
from astrololo.models.chart import ChartData
from astrololo.core.constants import PLANETS, SIGNS, SIGN_RULERS, get_dignity_label


class DominantPlanetRule(InterpretationRule):
    """Ranks planets by essential dignity first, then accidental (house + aspects)."""

    def __init__(self):
        super().__init__(priority=4)

    def matches(self, chart: ChartData) -> bool:
        return len([b for b in chart.planets if b.body_type == "planet"]) >= 3

    def _body(self, chart, name):
        return next((b for b in chart.planets if b.name == name), None)

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[List[RuleResult]]:
        scorer = ChartScorer(chart)
        base_scores = scorer.get_planet_rankings()

        # Add rulership bonuses
        asc_sign = chart.ascendant_sign or ""
        asc_ruler = SIGN_RULERS.get(asc_sign, "")
        mc_sign = chart.mc_sign or ""
        mc_ruler = SIGN_RULERS.get(mc_sign, "")
        sun_body = self._body(chart, "sun")
        moon_body = self._body(chart, "moon")
        sun_sign = sun_body.sign if sun_body else ""
        moon_sign = moon_body.sign if moon_body else ""
        sun_ruler = SIGN_RULERS.get(sun_sign, "")
        moon_ruler = SIGN_RULERS.get(moon_sign, "")

        enriched = []
        for entry in base_scores:
            pname = entry["planet"]
            extra = 0
            if pname == asc_ruler:
                extra += 3
            if pname == mc_ruler:
                extra += 2
            if pname == sun_ruler:
                extra += 2
            if pname == moon_ruler:
                extra += 1
            entry["rulership_bonus"] = extra
            entry["accidental"] += extra
            entry["total"] += extra
            enriched.append(entry)

        # Primary sort by essential, secondary by accidental
        enriched.sort(key=lambda x: (x["essential"], x["accidental"]), reverse=True)

        physical = [e for e in enriched if self._body(chart, e["planet"]) and
                    self._body(chart, e["planet"]).body_type == "planet"]
        if not physical:
            return None

        top = physical[0]
        pbody = self._body(chart, top["planet"])
        p = PLANETS.get(top["planet"])
        planet_name = p.name_vi if p and lang == "vi" else p.name_en if p else top["planet"]
        sign_name = SIGNS.get(pbody.sign)
        sn = sign_name.name_vi if sign_name and lang == "vi" else sign_name.name_en if sign_name else pbody.sign
        hn = pbody.house
        func = get_planet_function(top["planet"])
        func_short = func.split(".")[0] + "." if func else ""

        # Dignity label for essential
        d_label_str = get_dignity_label(top["planet"], pbody.sign)
        ess = top["essential"]
        acc = top["accidental"]

        if lang == "vi":
            # Check if essential and accidental conflict
            if ess <= 0 and acc >= 5:
                conflict_note = (
                    f"Lưu ý: {planet_name} ở {sn} ở vị trí {d_label_str} về bản chất "
                    f"(Phẩm giá Bẩm sinh: {ess}đ), nhưng có nhiều góc chiếu và vị thế nhà cửa "
                    f"tạo nên sức mạnh tình huống (Phẩm giá Ngẫu nhiên: {acc}đ). "
                    f"Hành tinh này hoạt động mạnh nhưng dễ gây căng thẳng, "
                    f"không phải là điểm tựa vững chắc nhất của lá số."
                )
            elif ess >= 4:
                conflict_note = (
                    f"{planet_name} ở {sn} có Phẩm giá Bẩm sinh rất cao ({d_label_str}, {ess}đ) — "
                    f"đây thực sự là điểm tựa vững chắc của lá số."
                )
            else:
                conflict_note = (
                    f"{planet_name} ở {sn}, Nhà {hn}. "
                    f"Phẩm giá Bẩm sinh: {ess}đ, Phẩm giá Ngẫu nhiên: {acc}đ."
                )

            if top["total"] >= 10:
                closing = "Hành tinh này chi phối toàn bộ lá số và đóng vai trò then chốt trong tính cách của bạn."
            elif top["total"] >= 5:
                closing = "Hành tinh này có ảnh hưởng nổi bật, định hình nhiều khía cạnh trong cuộc sống của bạn."
            else:
                closing = "Hành tinh này góp phần tạo nên sự cân bằng tổng thể của lá số."
        else:
            if ess <= 0 and acc >= 5:
                conflict_note = (
                    f"Note: {planet_name} in {sn} is in {d_label_str} (Essential Dignity: {ess}pt), "
                    f"but many aspects and house position create strong Accidental Dignity ({acc}pt). "
                    f"This planet is active but strained — not your chart's most stable pillar."
                )
            elif ess >= 4:
                conflict_note = (
                    f"{planet_name} in {sn} has very high Essential Dignity ({d_label_str}, {ess}pt) — "
                    f"a truly stable pillar of your chart."
                )
            else:
                conflict_note = (
                    f"{planet_name} in {sn}, House {hn}. "
                    f"Essential Dignity: {ess}pt, Accidental Dignity: {acc}pt."
                )

            if top["total"] >= 10:
                closing = "This planet dominates your chart and plays a key role in your personality."
            elif top["total"] >= 5:
                closing = "This planet has notable influence, shaping many aspects of your life."
            else:
                closing = "This planet contributes to the overall balance of your chart."

        # Build ranking table text
        if lang == "vi":
            ranking_lines = ["Bảng xếp hạng hành tinh (theo Phẩm giá Bẩm sinh):"]
            for i, e in enumerate(physical[:7]):
                b = self._body(chart, e["planet"])
                if not b:
                    continue
                pl = PLANETS.get(e["planet"])
                pn = pl.name_vi if pl else e["planet"]
                sb = SIGNS.get(b.sign)
                sn2 = sb.name_vi if sb else b.sign
                ess2 = e["essential"]
                acc2 = e["accidental"]
                ranking_lines.append(
                    f"{i+1}. {pn} — {sn2}, Nhà {b.house} | Bẩm sinh:{ess2} + Ngẫu nhiên:{acc2}"
                )
        else:
            ranking_lines = ["Planet ranking (by Essential Dignity):"]
            for i, e in enumerate(physical[:7]):
                b = self._body(chart, e["planet"])
                if not b:
                    continue
                pl = PLANETS.get(e["planet"])
                pn = pl.name_en if pl else e["planet"]
                sb = SIGNS.get(b.sign)
                sn2 = sb.name_en if sb else b.sign
                ess2 = e["essential"]
                acc2 = e["accidental"]
                ranking_lines.append(
                    f"{i+1}. {pn} — {sn2}, House {b.house} | Essential:{ess2} + Accidental:{acc2}"
                )

        ranking_text = "\n".join(ranking_lines)

        detail = f"{conflict_note} {func_short} {closing}"
        text = ranking_text + "\n\n" + detail

        return [RuleResult(
            title_vi=f"Hành Tinh Nổi Bật: {planet_name}" if lang == "vi" else "",
            title_en=f"Dominant Planet: {planet_name}" if lang == "en" else "",
            text_vi=text if lang == "vi" else "",
            text_en=text if lang == "en" else "",
            score=float(top["total"]),
            priority=self.priority,
            category="dominant_planet",
            tags=["dominant_planet", top["planet"]],
            metadata={
                "pattern": "dominant_planet",
                "planet": top["planet"],
                "score": top["total"],
                "essential": top["essential"],
                "accidental": top["accidental"],
                "rankings": physical[:7],
            },
        )]


RuleRegistry.register(DominantPlanetRule())
