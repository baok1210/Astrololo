"""Cross-Cutting Synthesis — infers links ACROSS chart factors that
descriptive rules miss: sign reinforcement (2+ key points share a sign),
worldly mapping of house cusps, planet→house governance (a planet's action
is filtered by the house it occupies), and contrarian nuance (popular
misconception vs reality per sign).

This is the "human astrologer abduction" layer: it weaves facts into a
narrative with judgment, not just a list of positions.
"""
from typing import Optional, List, Dict, Tuple
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.interpretation.keywords import (
    get_sign_keywords,
    get_house_keywords,
    get_planet_function,
    HOUSE_NAME_VI,
    SIGN_NATURAL_RULER,
    SIGN_NAME_VI,
)
from astrololo.interpretation.rules.house_synthesis_data import (
    HOUSE_BASE_VI, HOUSE_BASE_EN, PLANET_TONE_VI, PLANET_TONE_EN,
)
from astrololo.models.chart import ChartData
from astrololo.core.constants import PLANETS, SIGNS

_ANGULAR = {1, 4, 7, 10}

# Popular misconception vs reality per sign (contrarian nuance layer).
_SIGN_NUANCE_VI = {
    "aries": ("Bạch Dương thường bị hiểu là hung hăng, ích kỷ, chỉ biết tới mình.",
              "Thực ra Bạch Dương là tiên phong dám làm, hành động vì lý tưởng hơn là tư lợi — sự bốc đồng che giấu một ý chí kiến tạo."),
    "taurus": ("Kim Ngưu bị hiểu là lười, bám víu vật chất, chỉ thích ăn ngủ.",
               "Thực ra Kim Ngưu xây dựng giá trị bền vững — sự chậm rãi là sự kiên định, không phải trì trệ."),
    "gemini": ("Song Tử bị hiểu là hai mặt, không đáng tin, hời hợt.",
               "Thực ra Song Tử là trí tò mò đa chiều — họ kết nối các ý tưởng, không phải lừa dối; 'hai mặt' là khả năng nhìn nhiều góc."),
    "cancer": ("Cự Giải bị hiểu là yếu đuối, chỉ biết bám lấy người khác.",
               "Thực ra Cự Giải có sức mạnh bảo vệ thầm lặng — họ là nền móng cảm xúc vững chắc của người khác."),
    "leo": ("Sư Tử bị hiểu là khao khát được thờ phụng, kiêu ngạo, thích chú ý.",
            "Thực ra Sư Tử lãnh đạo bằng sự hào phóng — họ muốn tỏa sáng để nâng người khác lên, không chỉ cho mình."),
    "virgo": ("Xử Nữ bị hiểu là hay phê phán, kén cá chọn canh, bệnh lý hoàn hảo.",
              "Thực ra Xử Nữ phục vụ bằng sự tỉ mỉ — sự cầu toàn là cách họ chăm sóc thế giới."),
    "libra": ("Thiên Bình bị hiểu là do dự, nịnh hót, không có chính kiến.",
              "Thực ra Thiên Bình tìm sự công bằng thực sự — sự lưỡng lự là vì họ cân nhắc mọi phía trước khi quyết."),
    "scorpio": ("Bọ Cạp thường bị hiểu là về tình dục mãnh liệt, ghen tuông, chiếm hữu.",
                "Thực ra Bọ Cạp khao khát chiều sâu — sâu sắc về tâm hồn và trí tuệ. 'Sâu' ở đây là nội tâm/tri thức, không phải chỉ cảm xúc hay dục vọng bề mặt."),
    "sagittarius": ("Nhân Mã bị hiểu là vô trách nhiệm, bỏ trốn, chỉ thích chơi.",
                    "Thực ra Nhân Mã là kẻ truy cầu ý nghĩa — họ rời đi để mở rộng chân trời, không phải để trốn tránh."),
    "capricorn": ("Ma Kết bị hiểu là lạnh lùng, tham vọng tiền bạc, vô cảm.",
                  "Thực ra Ma Kết xây dựng di sản qua kỷ luật — sự nghiêm khắc là sự tôn trọng thành tựu dài hạn."),
    "aquarius": ("Bảo Bình bị hiểu là lập dị, vô cảm, xa cách cảm xúc.",
                "Thực ra Bảo Bình hành động vì tập thể — sự độc lập là để mang lại sự tiến bộ chung, không phải để cô lập."),
    "pisces": ("Song Ngư bị hiểu là yếu đuối, mơ mộng hão huyền, dễ bị lợi dụng.",
               "Thực ra Song Ngư có trực giác thấu thị sâu sắc — sự nhường nhịn là sức mạnh tha thứ, không phải yếu đuối."),
}
_SIGN_NUANCE_EN = {
    "aries": ("Aries is often read as aggressive and selfish.",
              "In truth Aries is a pioneering builder — impulsiveness masks a creative will."),
    "taurus": ("Taurus is read as lazy and materially attached.",
               "In truth Taurus builds durable value — slowness is steadiness, not stagnation."),
    "gemini": ("Gemini is read as two-faced and shallow.",
               "In truth Gemini is multi-perspective curiosity — they connect ideas, not deceive."),
    "cancer": ("Cancer is read as weak and clingy.",
               "In truth Cancer is silent protective strength — the emotional bedrock of others."),
    "leo": ("Leo is read as attention-seeking and arrogant.",
            "In truth Leo leads through generosity — they shine to lift others."),
    "virgo": ("Virgo is read as judgemental and perfectionist.",
              "In truth Virgo serves through precision — exacting care for the world."),
    "libra": ("Libra is read as indecisive and people-pleasing.",
              "In truth Libra seeks real fairness — hesitation weighs every side first."),
    "scorpio": ("Scorpio is read as sexual intensity and possessiveness.",
                "In truth Scorpio craves depth — of soul and intellect. 'Deep' means inner/mental, not just surface passion."),
    "sagittarius": ("Sagittarius is read as irresponsible and flighty.",
                    "In truth Sagittarius pursues meaning — they leave to expand horizons, not to flee."),
    "capricorn": ("Capricorn is read as cold and money-hungry.",
                  "In truth Capricorn builds legacy through discipline."),
    "aquarius": ("Aquarius is read as detached and eccentric.",
                "In truth Aquarius acts for the collective — independence serves progress."),
    "pisces": ("Pisces is read as weak and deluded.",
               "In truth Pisces holds deep intuitive sight — surrender is forgiving strength."),
}

# Notable house → governance flavor (a planet here has its action filtered by this).
_HOUSE_GOVERN_VI = {
    1: "thể hiện trực tiếp qua cá tính/bản thân — bạn hành động như chính bạn, khó che giấu",
    4: "gắn với nền tảng gia đình/cội nguồn — hành động bị chi phối bởi cảm giác an toàn và quá khứ",
    7: "bị chi phối bởi đối tác — mọi hành động đi qua thỏa thuận và quan hệ một-một",
    10: "bị lọc qua lăng kính danh tiếng — bạn có tiêu chuẩn riêng, không làm bừa, cân nhắc kỹ vì ảnh hưởng đến uy tín",
}
_HOUSE_GOVERN_EN = {
    1: "expresses directly through identity — you act as yourself, hard to hide",
    4: "tied to family/roots — action is shaped by security and the past",
    7: "governed by the partner — action flows through agreement and one-to-one relations",
    10: "filtered through reputation — you hold standards, never act carelessly, weigh impact on status",
}


class CrossSynthesisRule(InterpretationRule):
    def __init__(self):
        super().__init__(priority=3)  # right after micro_synthesis (4)

    def matches(self, chart: ChartData) -> bool:
        return bool(chart.planets) and bool(chart.houses)

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[List[RuleResult]]:
        results: List[RuleResult] = []
        amp = self._sign_repetition(chart, lang)
        results += amp
        results += self._house_worldly(chart, lang)
        gov = self._governance(chart, lang)
        results += gov
        results += self._contrarian(chart, lang)
        tensions = self._tension(chart, lang)
        results += tensions
        # capstone: weave everything into one through-line narrative
        theme = self._life_theme(chart, lang, amp, gov, tensions)
        if theme:
            results.insert(0, theme)  # put the synthesis at the top of the section
        return results if results else None

    # ─── helpers ──────────────────────────────────────────────────────────
    def _body(self, chart, name):
        return next((b for b in chart.planets if b.name == name), None)

    def _pname(self, name, lang):
        p = PLANETS.get(name)
        return p.name_vi if p and lang == "vi" else p.name_en if p else name

    def _sname(self, sign, lang):
        return SIGN_NAME_VI.get(sign, sign) if lang == "vi" else sign.title()

    def _hname(self, h, lang):
        base = HOUSE_NAME_VI.get(h, f"Nhà {h}") if lang == "vi" else f"House {h}"
        return base

    def _element_counts(self, chart) -> Dict[str, int]:
        counts = {"fire": 0, "earth": 0, "air": 0, "water": 0}
        for b in chart.planets:
            if b.body_type != "planet":
                continue
            sig = SIGNS.get(b.sign)
            if sig:
                counts[sig.element] = counts.get(sig.element, 0) + 1
        return counts

    # ─── 1. Sign repetition: 2+ key points share a sign → theme amplified ──
    def _sign_repetition(self, chart, lang) -> List[RuleResult]:
        points = []
        if chart.ascendant_sign:
            points.append(("ascendant", chart.ascendant_sign, "Cung Mọc" if lang == "vi" else "Ascendant"))
        if chart.mc_sign:
            points.append(("mc", chart.mc_sign, "Thiên Đỉnh" if lang == "vi" else "Midheaven"))
        sun = self._body(chart, "sun")
        moon = self._body(chart, "moon")
        if sun:
            points.append(("sun", sun.sign, "Mặt Trời" if lang == "vi" else "Sun"))
        if moon:
            points.append(("moon", moon.sign, "Mặt Trăng" if lang == "vi" else "Moon"))

        groups: Dict[str, List[str]] = {}
        for _, sign, label in points:
            groups.setdefault(sign, []).append(label)
        out = []
        for sign, labels in groups.items():
            if len(labels) < 2:
                continue
            sname = self._sname(sign, lang)
            if lang == "vi":
                lead = f"{' và '.join(labels)} cùng cung {sname}"
                text = (f"{lead} → chủ đề của cung {sname} bị khuếch đại gấp bội. "
                        f"Một người có Mặt Trời (lẽ sống) và Cung Mọc (mặt nạ xã hội) cùng một cung "
                        f"thì không chỉ 'thể hiện' năng lượng đó ở bề mặt — họ SỐNG nó ở cốt lõi. "
                        f"Các đặc trưng của {sname} trở thành bản sắc cố định, khó pha trộn với cung khác, "
                        f"và thường bị người ngoài hiểu lầm vì quá tập trung vào một chiều sâu duy nhất.")
                title = f"Khuếch Đại Cung: {sname} ({' + '.join(labels)})"
            else:
                lead = f"{' and '.join(labels)} are both in {sname}"
                text = (f"{lead} → the {sname} theme is amplified. When Sun (life purpose) and "
                        f"Ascendant (social mask) share a sign, you don't just 'show' that energy — "
                        f"you live it at the core. Its traits become a fixed identity.")
                title = f"Sign Amplification: {sname} ({' + '.join(labels)})"
            out.append(RuleResult(
                title_vi=title if lang == "vi" else "",
                title_en=title if lang == "en" else "",
                text_vi=text if lang == "vi" else "",
                text_en=text if lang == "en" else "",
                score=9.0,
                priority=self.priority,
                category="cross_synthesis",
                tags=["sign_amplification", sign] + [l for l in labels],
                metadata={"pattern": "sign_amplification", "sign": sign, "points": labels},
            ))
        return out

    # ─── 2. House synthesis: multi-variable (base + occupants + ruler + asp) ──
    def _house_worldly(self, chart, lang) -> List[RuleResult]:
        out = []
        base = HOUSE_BASE_VI if lang == "vi" else HOUSE_BASE_EN
        tone = PLANET_TONE_VI if lang == "vi" else PLANET_TONE_EN
        for h in chart.houses:
            n = h.house_number
            sign = h.sign
            sname = self._sname(sign, lang)
            hname = self._hname(n, lang)
            parts: List[str] = []

            # LAYER 1 — BASE (cusp sign flavor)
            btext = base.get(n, {}).get(sign, "")
            if lang == "vi":
                parts.append(f"[Nền] Đỉnh {hname} là {sname}: {btext}")
            else:
                parts.append(f"[Base] Cusp of {hname} is {sname}: {btext}")

            # LAYER 2 — OCCUPANTS (planets actually in the house; highest weight)
            occ = [b for b in chart.planets if getattr(b, "house", None) == n]
            if occ:
                for b in occ:
                    pname = self._pname(b.name, lang)
                    t = tone.get(b.name, "")
                    if lang == "vi":
                        parts.append(f"[Vì có {pname} ở nhà {n}] năng lượng {t} được đưa thẳng vào lĩnh vực này — đây là ảnh hưởng mạnh nhất tới cách bạn trải nghiệm {hname.lower()}.")
                    else:
                        parts.append(f"[Because {pname} is in house {n}] the {t} energy is brought directly into this area — the strongest influence on how you experience {hname.lower()}.")
            else:
                if lang == "vi":
                    parts.append(f"[Nhà trống] không hành tinh nào tọa thủ — năng lượng {sname} ở đỉnh là chủ đạo, ít bị pha trộn.")
                else:
                    parts.append(f"[Empty house] no planet sits here — the cusp {sname} energy leads, little mixed in.")

            # LAYER 3 — RULER (ruler of cusp sign + which house it occupies)
            ruler = SIGN_NATURAL_RULER.get(sign)
            if ruler:
                rbody = next((b for b in chart.planets if b.name == ruler), None)
                rhouse = rbody.house if rbody else None
                rname = self._pname(ruler, lang)
                if rhouse:
                    rhname = self._hname(rhouse, lang)
                    if lang == "vi":
                        parts.append(f"[Chủ nhà {n} là {rname}] nằm ở {rhname} → năng lượng của {hname.lower()} được dẫn dắt qua lĩnh vực {rhname.lower()}.")
                    else:
                        parts.append(f"[Ruler of house {n} is {rname}] placed in {rhname} → the house {n} energy is driven through the {rhname.lower()} area.")
                else:
                    if lang == "vi":
                        parts.append(f"[Chủ nhà {n} là {rname}] không nằm trong nhà nào được tính.")
                    else:
                        parts.append(f"[Ruler of house {n} is {rname}] not placed in a computed house.")

            # LAYER 4 — ASPECTS (harmony/dissonance among occupants + ruler)
            asp_note = self._house_aspect_note(chart, occ, ruler, hname, lang)
            if asp_note:
                parts.append(asp_note)

            text = "\n".join(parts)
            if lang == "vi":
                title = f"Nhà {n} — Tổng Hợp Đa Biến Số"
            else:
                title = f"House {n} — Multi-Variable Synthesis"
            out.append(RuleResult(
                title_vi=title if lang == "vi" else "",
                title_en=title if lang == "en" else "",
                text_vi=text if lang == "vi" else "",
                text_en=text if lang == "en" else "",
                score=6.0,
                priority=self.priority,
                category="cross_synthesis",
                tags=["house_worldly", f"house_{n}", sign],
                metadata={"pattern": "house_worldly", "house": n, "cusp": sign,
                           "occupants": [b.name for b in occ], "ruler": ruler},
            ))
        return out

    def _house_aspect_note(self, chart, occ, ruler, hname, lang) -> Optional[str]:
        # aspects involving any occupant or the ruler planet
        watch = {b.name for b in occ}
        if ruler:
            watch.add(ruler)
        if not watch:
            return None
        harm = 0
        dis = 0
        names = set()
        for a in chart.aspects:
            p1, p2 = a.planet1, a.planet2
            if p1 in watch and p2 in watch:
                names.add(p1); names.add(p2)
                if a.nature == "harmonious":
                    harm += 1
                elif a.nature == "challenging":
                    dis += 1
        if harm == 0 and dis == 0:
            return None
        pn = ", ".join(self._pname(x, lang) for x in sorted(names))
        if lang == "vi":
            if harm and not dis:
                return f"[Góc chiếu] {pn} tạo góc thuận → các yếu tố trong {hname.lower()} hòa hợp, dễ bộc lộ."
            if dis and not harm:
                return f"[Góc chiếu] {pn} tạo góc thử thách → {hname.lower()} có xung đột/nội tâm cần hóa giải."
            return f"[Góc chiếu] {pn} vừa có góc thuận ({harm}) vừa góc thử thách ({dis}) → {hname.lower()} vừa linh hoạt vừa có mâu thuẫn cần cân bằng."
        if harm and not dis:
            return f"[Aspects] {pn} form harmonious aspects → the factors in {hname.lower()} flow easily."
        if dis and not harm:
            return f"[Aspects] {pn} form challenging aspects → {hname.lower()} carries tension to resolve."
        return f"[Aspects] {pn} mix harmonious ({harm}) and challenging ({dis}) → {hname.lower()} is both fluid and conflicted, needing balance."

    # ─── 3. Planet governance: planet in angular house filters its action ─
    def _governance(self, chart, lang) -> List[RuleResult]:
        out = []
        for b in chart.planets:
            if b.body_type != "planet":
                continue
            if b.house not in _ANGULAR:
                continue
            flavor = (_HOUSE_GOVERN_VI if lang == "vi" else _HOUSE_GOVERN_EN).get(b.house)
            if not flavor:
                continue
            pname = self._pname(b.name, lang)
            func = get_planet_function(b.name)
            func_short = (func.split(".")[0] + ".") if func else ""
            sname = self._sname(b.sign, lang)
            hname = self._hname(b.house, lang)
            if lang == "vi":
                text = (f"{pname} (chức năng: {func_short}) nằm tại {hname} (đỉnh {sname}). "
                        f"Vì ở nhà góc, hành động của {pname} {flavor}. "
                        f"Điều này nghĩa là cách {pname} bộc lộ không tự do thuần túy — "
                        f"nó luôn bị 'kiểm duyệt' bởi lăng kính của {hname.lower()}.")
                title = f"Quản Trị Hành Tinh: {pname} @ {hname}"
            else:
                text = (f"{pname} (function: {func_short}) is in {hname} (cusp {sname}). "
                        f"Being in an angular house, {pname}'s action {flavor}. "
                        f"This means {pname} never acts purely freely — it is vetted by the {hname} lens.")
                title = f"Planet Governance: {pname} @ {hname}"
            out.append(RuleResult(
                title_vi=title if lang == "vi" else "",
                title_en=title if lang == "en" else "",
                text_vi=text if lang == "vi" else "",
                text_en=text if lang == "en" else "",
                score=5.0,
                priority=self.priority,
                category="cross_synthesis",
                tags=["planet_governance", b.name, f"house_{b.house}"],
                metadata={"pattern": "planet_governance", "planet": b.name, "house": b.house},
            ))
        return out

    # ─── 4. Contrarian nuance: misconception vs reality per key sign ───────
    def _contrarian(self, chart, lang) -> List[RuleResult]:
        signs = []
        if chart.ascendant_sign:
            signs.append(chart.ascendant_sign)
        sun = self._body(chart, "sun")
        moon = self._body(chart, "moon")
        if sun:
            signs.append(sun.sign)
        if moon:
            signs.append(moon.sign)
        table = _SIGN_NUANCE_VI if lang == "vi" else _SIGN_NUANCE_EN
        lines = []
        for s in dict.fromkeys(signs):  # dedupe, keep order
            if s in table:
                mis, real = table[s]
                sname = self._sname(s, lang)
                if lang == "vi":
                    lines.append(f"• {sname}: Hiểu lầm — {mis} / Thực tế — {real}")
                else:
                    lines.append(f"• {sname}: Misconception — {mis} / Reality — {real}")
        if not lines:
            return []
        if lang == "vi":
            text = ("Chiêm tinh sách vở thường mô tả mỗi cung một chiều. Dưới đây là lớp 'thực tế' "
                    "mà người ngoài dễ hiểu sai với lá số của bạn:\n\n" + "\n".join(lines))
            title = "Lớp Thực Tế Của Các Cung (Misconception vs Reality)"
        else:
            text = ("Textbook astrology describes each sign one-dimensionally. Here is the 'reality' "
                    "layer often misread in your chart:\n\n" + "\n".join(lines))
            title = "Sign Reality Layer (Misconception vs Reality)"
        return [RuleResult(
            title_vi=title if lang == "vi" else "",
            title_en=title if lang == "en" else "",
            text_vi=text if lang == "vi" else "",
            text_en=text if lang == "en" else "",
            score=6.0,
            priority=self.priority,
            category="cross_synthesis",
            tags=["contrarian_nuance"] + signs,
            metadata={"pattern": "contrarian_nuance", "signs": signs},
        )]


    # ─── 5. Tension: where two chart factors pull in opposite directions ──
    def _tension(self, chart, lang) -> List[RuleResult]:
        out = []
        sun = self._body(chart, "sun")
        moon = self._body(chart, "moon")
        asc = self._body(chart, "ascendant")

        # 5a. Sun vs Moon sign mismatch → inner (Sun) vs outer/emotional (Moon) pull
        if sun and moon and sun.sign != moon.sign:
            sun_s = self._sname(sun.sign, lang)
            moon_s = self._sname(moon.sign, lang)
            if lang == "vi":
                text = (f"Mặt Trời ở {sun_s} (bạn LÀ ai) khác với Mặt Trăng ở {moon_s} (bạn CẢM thế nào). "
                        f"Đây là căng thẳng cốt lõi: bên ngoài bạn phản ứng theo kiểu {moon_s}, "
                        f"nhưng cái tôi thật lại vận hành theo {sun_s}. Người khác dễ hiểu lầm bạn "
                        f"vì lớp cảm xúc ({moon_s}) che khuất lẽ sống ({sun_s}).")
                title = f"Căng Thẳng: Mặt Trời {sun_s} ⇄ Mặt Trăng {moon_s}"
            else:
                text = (f"Sun in {sun_s} (who you are) differs from Moon in {moon_s} (how you feel). "
                        f"Core tension: your emotional reflex is {moon_s}, but your true self runs on {sun_s}. "
                        f"Others misread you because the {moon_s} layer hides the {sun_s} core.")
                title = f"Tension: Sun {sun_s} ⇄ Moon {moon_s}"
            out.append(RuleResult(
                title_vi=title if lang == "vi" else "",
                title_en=title if lang == "en" else "",
                text_vi=text if lang == "vi" else "",
                text_en=text if lang == "en" else "",
                score=7.0, priority=self.priority, category="cross_synthesis",
                tags=["tension", "sun_moon", sun.sign, moon.sign],
                metadata={"pattern": "tension", "type": "sun_moon", "sun": sun.sign, "moon": moon.sign},
            ))

        # 5b. Ascendant (mask) vs Sun (core) mismatch → how you're seen vs who you are
        if asc and sun and asc.sign != sun.sign:
            asc_s = self._sname(asc.sign, lang)
            sun_s = self._sname(sun.sign, lang)
            if lang == "vi":
                text = (f"Cung Mọc {asc_s} (mặt nạ xã hội) khác Mặt Trời {sun_s} (cốt lõi). "
                        f"Bạn bị người lạ 'đọc' là kiểu {asc_s}, nhưng bản chất là {sun_s}. "
                        f"Nếu hai năng lượng này trái ngược, bạn hay bị bảo 'lúc đầu tưởng cậu như vậy "
                        f"mà hóa ra khác' — đó là khoảng cách giữa ấn tượng đầu và con người thật.")
                title = f"Căng Thẳng: Mọc {asc_s} ⇄ Mặt Trời {sun_s}"
            else:
                text = (f"Ascendant {asc_s} (social mask) differs from Sun {sun_s} (core). "
                        f"Strangers read you as {asc_s}, but your essence is {sun_s} — sometimes a "
                        f"'first impression vs real self' gap.")
                title = f"Tension: Asc {asc_s} ⇄ Sun {sun_s}"
            out.append(RuleResult(
                title_vi=title if lang == "vi" else "",
                title_en=title if lang == "en" else "",
                text_vi=text if lang == "vi" else "",
                text_en=text if lang == "en" else "",
                score=6.0, priority=self.priority, category="cross_synthesis",
                tags=["tension", "asc_sun", asc.sign, sun.sign],
                metadata={"pattern": "tension", "type": "asc_sun", "asc": asc.sign, "sun": sun.sign},
            ))

        # 5c. Element imbalance → one mode dominates, its opposite is starved
        counts = self._element_counts(chart)
        if counts:
            hi = max(counts, key=counts.get)
            lo = min(counts, key=counts.get)
            if counts[hi] >= 4 and counts[lo] == 0:
                elem_vi = {"fire": "Hỏa", "earth": "Thổ", "air": "Khí", "water": "Thủy"}
                opposite = {"fire": "water", "water": "fire", "earth": "air", "air": "earth"}[hi]
                if lang == "vi":
                    text = (f"Lá số lệch hẳn về nguyên tố {elem_vi[hi]} ({counts[hi]} hành tinh), "
                            f"trong khi {elem_vi[lo]} = 0. Điểm mạnh: bạn rất {elem_vi[hi].lower()} "
                            f"(hành động/tư duy theo mode đó). Điểm yếu: thiếu {elem_vi[opposite].lower()} "
                            f"— dễ thiếu sự cân bằng mà nguyên tố đối lập mang lại "
                            f"(vd thiếu Thủy = khó chạm cảm xúc; thiếu Khí = khó khách quan).")
                    title = f"Căng Thẳng Nguyên Tố: {elem_vi[hi]} áp đảo / {elem_vi[lo]} = 0"
                else:
                    text = (f"Chart skews hard to {hi} ({counts[hi]} planets), {lo} = 0. "
                            f"Strength: strong {hi} mode. Blind spot: starved {opposite} — "
                            f"the balance that opposite element gives is missing.")
                    title = f"Element Tension: {hi} dominant / {lo} = 0"
                out.append(RuleResult(
                    title_vi=title if lang == "vi" else "",
                    title_en=title if lang == "en" else "",
                    text_vi=text if lang == "vi" else "",
                    text_en=text if lang == "en" else "",
                    score=6.0, priority=self.priority, category="cross_synthesis",
                    tags=["tension", "element", hi, lo],
                    metadata={"pattern": "tension", "type": "element", "high": hi, "low": lo},
                ))
        return out

    # ─── 6. Life-theme synthesis: one through-line narrative (capstone) ────
    def _life_theme(self, chart, lang, amp, gov, tensions) -> Optional[RuleResult]:
        bits = []
        # strongest amplification
        if amp:
            a = amp[0]
            sign = a.metadata.get("sign")
            pts = ", ".join(a.metadata.get("points", []))
            if lang == "vi":
                bits.append(f"chủ đạo {self._sname(sign, 'vi')} (do {pts} cùng cung)")
            else:
                bits.append(f"a {self._sname(sign, 'en')} through-line (from {pts} shared)")
        # career/public governance if any
        pub = next((g for g in gov if g.metadata.get("house") == 10), None)
        if pub:
            p = pub.metadata.get("planet")
            if lang == "vi":
                bits.append(f"{self._pname(p, 'vi')} nơi công chúng bị 'kiểm duyệt' danh tiếng")
            else:
                bits.append(f"{self._pname(p, 'en')} publicly vetted by reputation")
        # top tension
        if tensions:
            t = tensions[0]
            if lang == "vi":
                bits.append("căng thẳng nội tại cần hòa giải")
            else:
                bits.append("an inner tension to reconcile")
        if not bits:
            return None
        if lang == "vi":
            text = ("Gom lại, lá số này không phải danh sách rời rạc mà là MỘT mạch sống: " + \
                    "; ".join(bits) + ". " + \
                    "Sự khác biệt giữa các lớp (mặt nạ, cảm xúc, cốt lõi, danh tiếng) là nơi "
                    "bạn trưởng thành — không phải lỗi, mà là lực kéo tạo nên cá tính sâu.")
            title = "Mạch Sống Xuyên Suốt (Life-Theme Synthesis)"
        else:
            text = ("Taken together, this chart is not a scattered list but ONE through-line: " + \
                    "; ".join(bits) + ". " + \
                    "The gaps between layers (mask, emotion, core, public) are where you grow — "
                    "not flaws, but the tension that makes a real personality.")
            title = "Life-Theme Synthesis"
        return RuleResult(
            title_vi=title if lang == "vi" else "",
            title_en=title if lang == "en" else "",
            text_vi=text if lang == "vi" else "",
            text_en=text if lang == "en" else "",
            score=10.0, priority=self.priority, category="cross_synthesis",
            tags=["life_theme"],
            metadata={"pattern": "life_theme"},
        )


RuleRegistry.register(CrossSynthesisRule())
