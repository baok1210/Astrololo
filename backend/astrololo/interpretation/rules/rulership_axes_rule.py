"""P2 + P3 + Internal-Conflict — connect houses into one logic chain.

P2 RULERSHIP LINKS (cấp 1):
  For every house, find its cusp sign's ruling planet, then where THAT planet
  sits -> "House N is driven through House M". Builds the cross-life narrative
  the user asked for (e.g. "Chủ nhà 2 nằm nhà 3 -> thu nhập từ giao tiếp").

P3 AXES (trục đối xứng) — always analysed as PAIRS, not alone:
  1-7 (Bản thân - Đối tác), 2-8 (Giá trị - Chung đụng), 4-10 (Gia đình - Sự nghiệp).
  Reports the balance / tension between the two ends.

INTERNAL CONFLICT (xung đột nội tâm):
  Hard aspects (square/opposition) between Sun or Mars (outer drive / action)
  and Moon (inner safety) -> the gap between how you act and what you need.
"""
from typing import Optional, List
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.models.chart import ChartData
from astrololo.interpretation.keywords import (
    HOUSE_NAME_VI, SIGN_NATURAL_RULER, HOUSE_NATURAL_RULER, SIGN_NAME_VI,
)
from astrololo.interpretation.rules.functional_compose import (
    PLANET_FUNC_VI, PLANET_FUNC_EN,
)


def _planet_house(chart: ChartData, name: str) -> Optional[int]:
    b = next((p for p in chart.planets if p.name == name), None)
    return b.house if b else None


def _planet_sign(chart: ChartData, name: str) -> Optional[str]:
    b = next((p for p in chart.planets if p.name == name), None)
    return b.sign if b else None


def _has_aspect(chart: ChartData, a: str, b: str, kinds) -> Optional[str]:
    for asp in chart.aspects:
        if ((asp.planet1 == a and asp.planet2 == b) or
            (asp.planet1 == b and asp.planet2 == a)) and asp.aspect_type in kinds:
            return asp.aspect_type
    return None


class RulershipAxesRule(InterpretationRule):
    def __init__(self):
        super().__init__(priority=4)  # after micro/cross synthesis, before pattern

    def matches(self, chart: ChartData) -> bool:
        return len([p for p in chart.planets if p.body_type == "planet"]) >= 3

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[RuleResult]:
        out: List[RuleResult] = []
        func = PLANET_FUNC_VI if lang == "vi" else PLANET_FUNC_EN
        hname = lambda n: HOUSE_NAME_VI[n] if lang == "vi" else f"House {n}"

        # ── P2: ruler linkage for all 12 houses ──
        links = []
        for n in range(1, 13):
            h = chart.houses[n - 1]
            ruler = SIGN_NATURAL_RULER.get(h.sign)
            if not ruler:
                continue
            rh = _planet_house(chart, ruler)
            if rh is None or rh == n:
                continue
            links.append((n, ruler, rh))
        if links:
            if lang == "vi":
                lines = [f"• Chủ {hname(n)} ({SIGN_NAME_VI[chart.houses[n-1].sign]}) là "
                         f"{SIGN_NAME_VI.get(ruler, ruler)} nằm ở {hname(rh)} — "
                         f"{hname(n).lower()} được dẫn dắt qua {hname(rh).lower()}."
                         for n, ruler, rh in links]
                text = ("Liên kết chủ tinh (logic chuỗi giữa các nhà):\n" + "\n".join(lines) +
                        "\n\n→ Đọc một nhà không thể tách rời: năng lượng của nhà này chảy sang "
                        "lĩnh vực khác qua chủ tinh của nó.")
            else:
                lines = [f"• Ruler of {hname(n)} ({chart.houses[n-1].sign}) is "
                         f"{ruler} placed in {hname(rh)} — {hname(n)} is driven through "
                         f"the {hname(rh).lower()} area." for n, ruler, rh in links]
                text = ("Rulership links (chain logic between houses):\n" + "\n".join(lines) +
                        "\n\n→ No house is read alone: its energy flows to another area via its ruler.")
            out.append(self._mk("rulership_links", text, [r for _, r, _ in links], chart, lang))

        # ── P3: paired axes ──
        axis_defs = [(1, 7, "Bản thân", "Đối tác", "self", "partner"),
                     (2, 8, "Giá trị cá nhân", "Chung đụng", "personal value", "shared resources"),
                     (4, 10, "Gia đình", "Sự nghiệp", "family", "career")]
        for a, b, va, vb, ea, eb in axis_defs:
            ha, hb = chart.houses[a - 1], chart.houses[b - 1]
            ra, rb = SIGN_NATURAL_RULER.get(ha.sign), SIGN_NATURAL_RULER.get(hb.sign)
            if lang == "vi":
                text = (f"Trục {a}-{b} ({va} – {vb}): đỉnh {va} là {SIGN_NAME_VI[ha.sign]}, "
                        f"đỉnh {vb} là {SIGN_NAME_VI[hb.sign]}. Cần cân bằng giữa {va.lower()} "
                        f"và {vb.lower()} — áp lực một đầu thường giải qua đầu kia.")
            else:
                text = (f"Axis {a}-{b} ({ea} – {eb}): {ea} cusp {ha.sign}, {eb} cusp {hb.sign}. "
                        f"Balance {ea} and {eb} — pressure at one end is often resolved through the other.")
            out.append(self._mk(f"axis_{a}_{b}", text, [a, b], chart, lang))

        # ── Internal conflict: Sun/Mars vs Moon hard aspects ──
        moon = _planet_sign(chart, "moon")
        conflicts = []
        for drive in ("sun", "mars"):
            asp = _has_aspect(chart, drive, "moon", ("square", "opposition"))
            if asp:
                conflicts.append((drive, asp))
        if conflicts:
            if lang == "vi":
                parts = []
                for drive, asp in conflicts:
                    dname = "Mặt Trời" if drive == "sun" else "Sao Hỏa"
                    aname = "Vuông Góc" if asp == "square" else "Đối Xung"
                    parts.append(f"{dname} {aname} Mặt Trăng")
                text = ("Xung đột nội tâm: " + ", ".join(parts) +
                        " — lý tưởng / động lực bên ngoài (bạn làm gì) kéo ngược với vùng an toàn "
                        "nội tâm (Mặt Trăng). Bạn dễ căng thẳng giữa 'nên hành động' và 'cần được che chở'.")
            else:
                parts = []
                for drive, asp in conflicts:
                    dname = "Sun" if drive == "sun" else "Mars"
                    parts.append(f"{dname} {asp} Moon")
                text = ("Internal conflict: " + ", ".join(parts) +
                        " — outer drive/action pulls against the inner-safety need (Moon). Tension "
                        "between 'should act' and 'needs to be held'.")
            out.append(self._mk("internal_conflict", text,
                                 [d for d, _ in conflicts] + ["moon"], chart, lang))

        if not out:
            return None
        if len(out) == 1:
            return out[0]
        idx = 0 if lang == "vi" else 1
        title = ("Logic Chuỗi & Trục Đối Xứng" if lang == "vi" else "Chain Logic & Axes")
        return RuleResult(
            title_vi=title if lang == "vi" else "",
            title_en=title if lang == "en" else "",
            text_vi="\n\n".join(r.text_vi for r in out) if lang == "vi" else "",
            text_en="\n\n".join(r.text_en for r in out) if lang == "en" else "",
            score=sum(r.score for r in out),
            priority=self.priority,
            category="rulership_axes",
            tags=[t for r in out for t in r.tags],
            metadata={"blocks": [r.metadata for r in out]},
        )

    def _mk(self, pat, line, planets, chart, lang):
        return RuleResult(
            title_vi="" if lang == "vi" else "",
            title_en="" if lang == "en" else "",
            text_vi=line if lang == "vi" else "",
            text_en=line if lang == "en" else "",
            score=8.0,
            priority=self.priority,
            category="rulership_axes",
            tags=[pat] + [str(p) for p in planets],
            metadata={"pattern_type": pat, "planets": planets},
        )


RuleRegistry.register(RulershipAxesRule())
