"""P1 — Configuration Release-Point analysis.

Reuses the geometry detectors in pattern_rules.py (Kite, T-Square, Grand Trine)
and adds the MISSING expert layer the user asked for: the apex planet is the
"pressure-release valve". For a Kite, the 4th (opposing) planet is the outlet
that resolves the tension of the base Grand Trine. For a T-Square, the apex
(planet squaring the opposition) is where you act to relieve the opposition.

Also extends Stellium detection to HOUSE concentration (not just sign), since a
pile-up of planets in one house is a real, separate emphasis.

Outputs RuleResults under category "pattern_release".
"""
from typing import Optional, List
from collections import Counter
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.models.chart import ChartData
from astrololo.interpretation.rules.pattern_rules import (
    _detect_kite, _detect_tsquare, _detect_grand_trine, _detect_stellium,
)
from astrololo.interpretation.rules.functional_compose import (
    PLANET_FUNC_VI, PLANET_FUNC_EN,
)
from astrololo.interpretation.keywords import HOUSE_NAME_VI, SIGN_NAME_VI


def _planet_house(chart: ChartData, name: str) -> Optional[int]:
    b = next((p for p in chart.planets if p.name == name), None)
    return b.house if b else None


def _house_stellium(chart: ChartData):
    counts = Counter(p.house for p in chart.planets if p.body_type == "planet")
    for h, n in counts.items():
        if n >= 3:
            names = [p.name for p in chart.planets if p.body_type == "planet" and p.house == h]
            return h, names
    return None


class ReleasePointRule(InterpretationRule):
    def __init__(self):
        super().__init__(priority=9)  # near pattern rule (10), before combination

    def matches(self, chart: ChartData) -> bool:
        return len([p for p in chart.planets if p.body_type == "planet"]) >= 3

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[RuleResult]:
        out: List[RuleResult] = []
        func = PLANET_FUNC_VI if lang == "vi" else PLANET_FUNC_EN
        hname = lambda n: HOUSE_NAME_VI[n] if lang == "vi" else f"House {n}"

        # ── Kite: the 4th (opposing) planet is the release outlet ──
        kite = _detect_kite(chart.planets, chart.aspects)
        if kite:
            _, el, names = kite
            base = names[:3]
            apex = names[3] if len(names) > 3 else None
            if apex:
                ah = _planet_house(chart, apex)
                if lang == "vi":
                    line = (f"Cánh Diều (Grand Trine {el} + {apex} đối đỉnh): nền tảng {el} rất thuận "
                            f"nhưng dễ 'ngủ quên' vì quá êm. Điểm giải phóng là {apex} "
                            f"({func.get(apex,'')})")
                    if ah:
                        line += f" ở {hname(ah)} — đây là van xả: bạn bộc lộ năng lượng {el} ra thực tế qua lĩnh vực {hname(ah).lower()}."
                    else:
                        line += " — đây là van xả giúp bạn bộc lộ năng lượng đó ra thực tế."
                else:
                    line = (f"Kite (Grand Trine {el} + {apex} in opposition): the {el} base flows easily "
                            f"but can stall. The release point is {apex} ({func.get(apex,'')})")
                    if ah:
                        line += f" in {hname(ah)} — the valve: you express that {el} energy concretely through the {hname(ah).lower()} area."
                    else:
                        line += " — the valve that brings that energy into real life."
                out.append(self._mk("kite_release", line, [apex] + base, chart, lang))

        # ── T-Square: the apex (squaring planet) is where you act to relieve ──
        ts = _detect_tsquare(chart.planets, chart.aspects)
        if ts:
            _, quality, names = ts
            # apex = the one NOT in the opposition pair (last in names list from detector)
            apex = names[-1]
            opp = names[:2]
            ah = _planet_house(chart, apex)
            if lang == "vi":
                line = (f"T-Square ({quality}): {opp[0]} đối đỉnh {opp[1]} tạo áp lực kéo hai chiều, "
                        f"và {apex} ({func.get(apex,'')}) vuông góc cả hai — đây là điểm thắt.")
                if ah:
                    line += f" Nằm ở {hname(ah)}, {apex} là nơi bạn HÀNH ĐỘNG để giải tỏa: chuyển áp lực thành kết quả qua {hname(ah).lower()}."
                else:
                    line += " Đây là nơi bạn hành động để giải tỏa áp lực."
            else:
                line = (f"T-Square ({quality}): {opp[0]} opposes {opp[1]} (two-way pull), and {apex} "
                        f"({func.get(apex,'')}) squares both — the pinch point.")
                if ah:
                    line += f" In {hname(ah)}, {apex} is where you ACT to release: turn the pressure into output via the {hname(ah).lower()} area."
                else:
                    line += " This is where you act to release the pressure."
            out.append(self._mk("tsquare_release", line, names, chart, lang))

        # ── House stellium (extension beyond sign-based) ──
        hs = _house_stellium(chart)
        if hs:
            h, names = hs
            if lang == "vi":
                line = (f"Tập trung hành tinh tại {hname(h)}: {', '.join(names)} cùng nằm một nhà. "
                        f"Năng lượng đời bạn dồn mạnh vào lĩnh vực {hname(h).lower()} — vừa là thế mạnh "
                        f"tập trung, vừa dễ bỏ ngỏ các nhà khác.")
            else:
                line = (f"Planetary pile-up in {hname(h)}: {', '.join(names)} share one house. "
                        f"Your energy concentrates hard on the {hname(h).lower()} area — both a focused "
                        f"strength and a risk of neglecting other houses.")
            out.append(self._mk("house_stellium", line, names, chart, lang))

        if not out:
            return None
        if len(out) == 1:
            return out[0]
        # combine
        idx = 0 if lang == "vi" else 1
        title = ("Điểm Giải Phóng Cấu Trúc" if lang == "vi" else "Configuration Release Points")
        return RuleResult(
            title_vi=title if lang == "vi" else "",
            title_en=title if lang == "en" else "",
            text_vi="\n\n".join(r.text_vi for r in out) if lang == "vi" else "",
            text_en="\n\n".join(r.text_en for r in out) if lang == "en" else "",
            score=sum(r.score for r in out),
            priority=self.priority,
            category="pattern_release",
            tags=[t for r in out for t in r.tags],
            metadata={"releases": [r.metadata for r in out]},
        )

    def _mk(self, pat, line, planets, chart, lang):
        return RuleResult(
            title_vi="" if lang == "vi" else "",
            title_en="" if lang == "en" else "",
            text_vi=line if lang == "vi" else "",
            text_en=line if lang == "en" else "",
            score=12.0,
            priority=self.priority,
            category="pattern_release",
            tags=[pat] + planets,
            metadata={"pattern_type": pat, "planets": planets},
        )


RuleRegistry.register(ReleasePointRule())
