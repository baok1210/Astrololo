"""P5 + P6 — Karmic & Psychological deep-mining (the Logic Matrix).

Builds the cross-linking matrix the user asked for:
  Ruler -> House position -> Axis pair -> Sensitive points (Chiron/Vertex)
  -> Functional keywords -> "structure shows you use script A to resolve
     pain B on axis C" (not flat "you are like this").

Covers:
  P5  - Vertex (duyên phận) computed into chart; Chiron+Vertex co-position =
        "bài học không thể bỏ qua". Node grading: South=mature/accumulated,
        North=nascent/learned.
  P6  - Script vs Core: ASC ruler / ASC sign vs Sun-Moon core -> "lớp phủ"
        when the persona sign differs from the core. Axis imbalance (density)
        e.g. 5-11, 1-7, 2-8 -> warn when one side overloaded, other afflicted.
  Functional keywords reused from functional_compose (Saturn@7 -> "khó gần gũi").
"""
from typing import Optional, List
from collections import Counter
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.models.chart import ChartData
from astrololo.interpretation.keywords import (
    HOUSE_NAME_VI, SIGN_NATURAL_RULER, SIGN_NAME_VI,
)
from astrololo.interpretation.rules.functional_compose import (
    PLANET_FUNC_VI, PLANET_FUNC_EN,
)


def _p(chart, name):
    return next((b for b in chart.planets if b.name == name), None)


def _planet_house(chart, name):
    b = _p(chart, name)
    return b.house if b else None


def _sign_of(chart, name):
    b = _p(chart, name)
    return b.sign if b else None


class KarmicPsychRule(InterpretationRule):
    def __init__(self):
        super().__init__(priority=7)  # after pattern_release(9)? place mid; before combination

    def matches(self, chart: ChartData) -> bool:
        return len([p for p in chart.planets if p.body_type == "planet"]) >= 3

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[RuleResult]:
        out: List[RuleResult] = []
        func = PLANET_FUNC_VI if lang == "vi" else PLANET_FUNC_EN
        hname = lambda n: HOUSE_NAME_VI[n] if lang == "vi" else f"House {n}"
        S = lambda vi, en: vi if lang == "vi" else en

        # ── P5: Vertex + Chiron karmic ──
        vtx = chart.vertex
        if vtx:
            vh = vtx["house"]
            chiron = _p(chart, "chiron")
            co = chiron and chiron.house == vh
            if lang == "vi":
                line = (f"Vertex (điểm duyên phận) nằm {SIGN_NAME_VI.get(vtx['sign'], vtx['sign'])} "
                        f"ở {hname(vh)} — những gặp gỡ mang tính 'không né được' thường mở ra qua "
                        f"lĩnh vực {hname(vh).lower()}.")
                if co:
                    line += (f" Chiron (vết thương) CÙNG nằm {hname(vh)} → đây là 'bài học không thể "
                             f"bỏ qua': nỗi đau cốt lõi và duyên phận giao nhau tại đây.")
            else:
                line = (f"Vertex is {vtx['sign']} in {hname(vh)} — fated encounters open through the "
                        f"{hname(vh).lower()} area.")
                if co:
                    line += (f" Chiron (the wound) is ALSO in {hname(vh)} → a 'lesson you cannot skip': "
                             f"core wound and fate meet here.")
            out.append(self._mk("vertex_karmic", line, ["vertex", "chiron"], chart, lang))

        # ── Node grading: South=mature, North=nascent ──
        sn = _p(chart, "south_node"); nn = _p(chart, "north_node")
        if sn and nn:
            if lang == "vi":
                line = (f"La Hầu (Bắc Node) ở {SIGN_NAME_VI.get(nn.sign, nn.sign)} — năng lượng 'Thai', "
                        f"bỡ ngỡ, là nơi bạn CẦN học. Kế Đô (Nam Node) ở "
                        f"{SIGN_NAME_VI.get(sn.sign, sn.sign)} — năng lượng tích lũy, thuần thục nhất, "
                        f"là 'vốn cũ' bạn mang theo. Nhiệm vụ: rời vùng an toàn Kế Đô để trưởng thành "
                        f"về phía La Hầu.")
            else:
                line = (f"North Node in {nn.sign} — 'embryo' energy, unlearned, where you must GROW. "
                        f"South Node in {sn.sign} — accumulated, most mastered energy, your 'old capital'. "
                        f"Task: leave the South Node comfort to mature toward the North Node.")
            out.append(self._mk("node_grading", line, ["north_node", "south_node"], chart, lang))

        # ── P6: Script vs Core (persona vs essence) ──
        asc_sign = chart.ascendant_sign
        asc_ruler = SIGN_NATURAL_RULER.get(asc_sign)
        sun_sign = _sign_of(chart, "sun"); moon_sign = _sign_of(chart, "moon")
        if asc_sign and sun_sign:
            if asc_sign != sun_sign and asc_sign != moon_sign:
                if lang == "vi":
                    line = (f"Lớp phủ (kịch bản): Mọc {SIGN_NAME_VI.get(asc_sign, asc_sign)} "
                            f"(chủ {SIGN_NAME_VI.get(asc_ruler, asc_ruler) if asc_ruler else '?'}) là mặt nạ "
                            f"bạn trình diện; trong khi cốt lõi là Mặt Trời {SIGN_NAME_VI.get(sun_sign, sun_sign)}"
                            f"{(' / Mặt Trăng ' + SIGN_NAME_VI.get(moon_sign, moon_sign)) if moon_sign else ''}. "
                            f"Cấu trúc này cho thấy bạn dùng kịch bản {SIGN_NAME_VI.get(asc_sign, asc_sign)} "
                            f"để che giấu hoặc xử lý bản chất sâu hơn — 'bên ngoài X, bên trong Y'.")
                else:
                    line = (f"Persona script: Ascendant {asc_sign} (ruler {asc_ruler}) is the mask you "
                            f"present; core is Sun {sun_sign}{(' / Moon ' + moon_sign) if moon_sign else ''}. "
                            f"This structure shows you run the {asc_sign} script to handle a deeper nature "
                            f"— 'outside X, inside Y'.")
                out.append(self._mk("script_core", line, ["sun", "moon", "ascendant"], chart, lang))

        # ── Axis imbalance (density) ──
        from astrololo.core.constants import SIGNS
        density = Counter(p.house for p in chart.planets if p.body_type == "planet")
        axis_pairs = [(1, 7), (2, 8), (4, 10), (5, 11)]
        axis_names = {(1, 7): ("Bản thân", "Đối tác"), (2, 8): ("Giá trị", "Chung đụng"),
                      (4, 10): ("Gia đình", "Sự nghiệp"), (5, 11): ("Đam mê", "Hội nhóm")}
        for a, b in axis_pairs:
            da, db = density.get(a, 0), density.get(b, 0)
            if da == 0 and db == 0:
                continue
            diff = abs(da - db)
            if diff >= 2 or (da == 0 or db == 0) and (da + db) >= 2:
                va, vb = axis_names[(a, b)]
                if lang == "vi":
                    heavy = a if da > db else b
                    light = b if da > db else a
                    line = (f"Lệch trục {a}-{b} ({va} – {vb}): {hname(heavy)} có {max(da,db)} hành tinh "
                            f"trong khi {hname(light)} chỉ {min(da,db)}. Năng lượng dồn về {hname(heavy).lower()} "
                            f"khiến trải nghiệm {va.lower() if da>db else vb.lower()} bị quá tải, "
                            f"còn {vb.lower() if da>db else va.lower()} thiếu đất diễn — cần cân bằng có ý thức.")
                else:
                    heavy = a if da > db else b
                    light = b if da > db else a
                    line = (f"Axis tilt {a}-{b} ({va}–{vb}): {hname(heavy)} holds {max(da,db)} planets vs "
                            f"{min(da,db)} in {hname(light)}. Energy over-fills {hname(heavy).lower()}, "
                            f"starving {hname(light).lower()} — conscious rebalancing needed.")
                out.append(self._mk(f"axis_tilt_{a}_{b}", line, [a, b], chart, lang))

        # ── Social-outcome ruler link (10 -> 7 targeted) ──
        h10 = chart.houses[9]
        r10 = SIGN_NATURAL_RULER.get(h10.sign)
        if r10:
            rh = _planet_house(chart, r10)
            if rh == 7:
                if lang == "vi":
                    line = (f"Chủ Nhà 10 (Sự nghiệp) là {SIGN_NAME_VI.get(r10, r10)} nằm ở Nhà 7 (Đối tác) "
                            f"→ sự nghiệp chịu ảnh hưởng lớn từ đối tác; hoặc hôn nhân có yếu tố "
                            f"'môn đăng hộ đối', gắn danh tiếng với người đi cùng.")
                else:
                    line = (f"Ruler of House 10 (career) is {r10} in House 7 (partner) → career is strongly "
                            f"shaped by the partner; or marriage carries 'status match', tying reputation "
                            f"to who stands beside you.")
                out.append(self._mk("social_10_7", line, [r10, 10, 7], chart, lang))

        # ── Functional keyword: Saturn @ 7 (hard relation) ──
        sat_h = _planet_house(chart, "saturn")
        if sat_h == 7:
            if lang == "vi":
                line = (f"Thổ tinh ở Nhà 7: ghép từ khóa → '{func.get('saturn','')}' trong quan hệ' → "
                        f"khó khăn / xa cách có giới hạn khi gần gũi; cần thời gian để mở lòng.")
            else:
                line = (f"Saturn in House 7: keyword blend → '{func.get('saturn','')} in relationship' → "
                        f"difficulty / bounded distance in intimacy; needs time to open.")
            out.append(self._mk("saturn_7", line, ["saturn", 7], chart, lang))

        if not out:
            return None
        if len(out) == 1:
            return out[0]
        title = S("Ma Trận Nghiệp Quả & Tâm Lý", "Karmic & Psychological Matrix")
        return RuleResult(
            title_vi=title if lang == "vi" else "",
            title_en=title if lang == "en" else "",
            text_vi="\n\n".join(r.text_vi for r in out) if lang == "vi" else "",
            text_en="\n\n".join(r.text_en for r in out) if lang == "en" else "",
            score=sum(r.score for r in out),
            priority=self.priority,
            category="karmic_psych",
            tags=[t for r in out for t in r.tags],
            metadata={"blocks": [r.metadata for r in out]},
        )

    def _mk(self, pat, line, planets, chart, lang):
        return RuleResult(
            title_vi="" if lang == "vi" else "",
            title_en="" if lang == "en" else "",
            text_vi=line if lang == "vi" else "",
            text_en=line if lang == "en" else "",
            score=9.0,
            priority=self.priority,
            category="karmic_psych",
            tags=[pat] + [str(p) for p in planets],
            metadata={"pattern_type": pat, "planets": planets},
        )


RuleRegistry.register(KarmicPsychRule())
