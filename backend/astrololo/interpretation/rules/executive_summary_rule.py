"""Executive Summary — the personalised chart narrative that competitors lack.

Astro-Seek / Cafe Astrology / Astro.com dump generic per-factor text the
user must mentally stitch together. This rule writes ONE coherent overview
that links Sun + Moon + Rising + Dominant planet + key aspect + top life-area
into a single reading written as if for this person alone.
"""
from typing import Optional, List
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.interpretation.scoring import ChartScorer
from astrololo.core.constants import PLANETS, SIGNS, SIGN_RULERS
from astrololo.models.chart import ChartData

_SIGNS_ORDER = ["aries","taurus","gemini","cancer","leo","virgo","libra","scorpio","sagittarius","capricorn","aquarius","pisces"]
_SIGN_VI = {
    "aries":"Bạch Dương","taurus":"Kim Ngưu","gemini":"Song Tử","cancer":"Cự Giải","leo":"Sư Tử","virgo":"Xử Nữ",
    "libra":"Thiên Bình","scorpio":"Bọ Cạp","sagittarius":"Nhân Mã","capricorn":"Ma Kết","aquarius":"Bảo Bình","pisces":"Song Ngư",
}
_SIGN_EN = {
    "aries":"Aries","taurus":"Taurus","gemini":"Gemini","cancer":"Cancer","leo":"Leo","virgo":"Virgo",
    "libra":"Libra","scorpio":"Scorpio","sagittarius":"Sagittarius","capricorn":"Capricorn","aquarius":"Aquarius","pisces":"Pisces",
}
_ELEM_VI = {"fire":"Lửa","earth":"Đất","air":"Khí","water":"Nước"}
_QUAL_VI = {"cardinal":"Thống Lĩnh","fixed":"Cố Định","mutable":"Linh Hoạt"}


class ExecutiveSummaryRule(InterpretationRule):
    """One coherent, personalised overview of the whole chart."""

    def __init__(self):
        super().__init__(priority=1)

    def matches(self, chart: ChartData) -> bool:
        return bool(chart.planets)

    # helpers -------------------------------------------------------------
    def _body(self, chart, name):
        return next((b for b in chart.planets if b.name == name), None)

    def _pname(self, p, lang):
        pl = PLANETS.get(p.name)
        return pl.name_vi if pl and lang == "vi" else pl.name_en if pl else p.name

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[List[RuleResult]]:
        sun = self._body(chart, "sun")
        moon = self._body(chart, "moon")
        if not sun or not moon:
            return None

        asc_sign = chart.ascendant_sign
        asc_name = _SIGN_VI.get(asc_sign, asc_sign) if lang == "vi" else _SIGN_EN.get(asc_sign, asc_sign)
        sun_name = _SIGN_VI.get(sun.sign, sun.sign) if lang == "vi" else _SIGN_EN.get(sun.sign, sun.sign)
        moon_name = _SIGN_VI.get(moon.sign, moon.sign) if lang == "vi" else _SIGN_EN.get(moon.sign, moon.sign)

        # dominant planet
        scorer = ChartScorer(chart)
        rankings = scorer.get_planet_rankings()
        dom = rankings[0] if rankings else None
        dom_body = self._body(chart, dom["planet"]) if dom else None
        dom_name = self._pname(dom_body, lang) if dom_body else ""

        # key aspect: tightest major aspect involving sun/moon/asc-ruler
        key = None
        focal = {sun.name, moon.name}
        major = {"conjunction","sextile","square","trine","opposition"}
        tight = sorted(
            [a for a in chart.aspects if a.aspect_type in major],
            key=lambda a: a.orb,
        )
        for a in tight:
            if a.planet1 in focal or a.planet2 in focal:
                key = a
                break
        if not key and tight:
            key = tight[0]

        # top life area
        try:
            from astrololo.analysis.life_areas import calculate_life_areas
            areas = calculate_life_areas(chart)
            top_area = max(areas, key=lambda x: x["score"]) if areas else None
            low_area = min(areas, key=lambda x: x["score"]) if areas else None
        except Exception:
            top_area = low_area = None

        if lang == "vi":
            text = self._vi(sun_name, moon_name, asc_name, dom_name, key, top_area, low_area)
        else:
            text = self._en(sun_name, moon_name, asc_name, dom_name, key, top_area, low_area)

        ev = [f"Mặt Trời: {sun_name}", f"Mặt Trăng: {moon_name}", f"Cung Mọc: {asc_name}"]
        if dom_name:
            ev.append(f"Hành tinh nổi bật: {dom_name}")
        if key:
            ev.append(f"Góc khóa: {key.aspect_name_vi} {key.planet1}-{key.planet2}")

        return [RuleResult(
            title_vi="Tổng Quan Lá Số Cá Nhân Hóa" if lang == "vi" else "Personalised Chart Overview",
            title_en="Personalised Chart Overview" if lang == "en" else "",
            text_vi=text if lang == "vi" else "",
            text_en=text if lang == "en" else "",
            score=10.0,
            priority=self.priority,
            category="executive_summary",
            tags=["overview", sun.sign, moon.sign, asc_sign],
            evidence=ev,
            metadata={"sun_sign": sun.sign, "moon_sign": moon.sign, "asc_sign": asc_sign,
                      "dominant": dom["planet"] if dom else None},
        )]

    # language builders ---------------------------------------------------
    def _vi(self, sun, moon, asc, dom, key, top, low):
        s = f"Bản đồ sao của bạn là một cá thể duy nhất: Mặt Trời tại {sun} cho thấy cách bạn bộc lộ ý chí và bản sắc cốt lõi, "
        s += f"trong khi Mặt Trăng tại {moon} định hình đời sống cảm xúc và phản ứng vô thức của bạn. "
        s += f"Sự kết hợp này tạo nên nền tảng tính cách: lý trí hướng về {sun}, cảm xúc neo vào {moon}. "
        s += f"Với Cung Mọc {asc}, bạn trình diện bản thân với thế giới qua lăng kính {asc} — "
        s += "đây là 'mặt nạ' đầu tiên người khác thấy, dù bên trong bạn là sự pha trộn của cả ba."
        if dom:
            s += f"\n\nHành tinh chi phối mạnh nhất lá số là {dom}. Năng lượng của {dom} thấm vào nhiều lĩnh vực, "
            s += "biến nó thành động cơ chủ đạo định hình cách bạn hành động và thu hút cơ hội."
        if key:
            s += f"\n\nGóc chiếu then chốt là {key.aspect_name_vi} giữa {key.planet1} và {key.planet2} (orb {key.orb:.1f}°). "
            s += "Đây là 'chốt' cấu trúc — nó khuếch đại hoặc thử thách luồng năng lượng chính, "
            "và là điểm bạn dễ nhận thấy nhất khi nhìn lại cuộc đời mình."
        if top and low:
            s += f"\n\nVề 14 khía cạnh cuộc sống, điểm sáng nhất của bạn nằm ở {top['title_vi']} ({top['score']}/100), "
            s += f"trong khi {low['title_vi']} ({low['score']}/100) là lĩnh vực cần đầu tư nhiều năng lượng hơn. "
            s += "Sự chênh lệch này không phải điểm yếu — nó chỉ ra nơi bạn đã thuần thục và nơi còn dư địa phát triển."
        s += "\n\nTóm lại: bạn không phải là 'Mặt Trời " + sun + " điển hình' trong sách, "
        s += f"mà là sự giao thoa cụ thể của {sun} + {moon} + {asc} cùng các góc chiếu riêng — "
        s += "một tổng thể chỉ đúng với một mình bạn."
        return s

    def _en(self, sun, moon, asc, dom, key, top, low):
        s = f"Your birth chart is a unique individual: the Sun in {sun} shows how you express will and core identity, "
        s += f"while the Moon in {moon} shapes your emotional life and unconscious reactions. "
        s += f"Together they form your personality foundation: intellect leans {sun}, feelings root in {moon}. "
        s += f"With {asc} Rising, you present yourself to the world through the {asc} lens — "
        s += "the first mask others see, even as the inner mix is all three."
        if dom:
            s += f"\n\nThe most influential planet is {dom}. Its energy permeates many areas, "
            s += "becoming the main drive shaping how you act and attract opportunity."
        if key:
            s += f"\n\nThe pivotal aspect is the {key.aspect_name_vi} between {key.planet1} and {key.planet2} (orb {key.orb:.1f}°). "
            s += "This is the structural 'key' — it amplifies or challenges the main current, "
            "and is the pattern you notice most when looking back on your life."
        if top and low:
            s += f"\n\nAcross 14 life areas, your brightest score is {top['title_en']} ({top['score']}/100), "
            s += f"while {low['title_en']} ({low['score']}/100) needs more investment. "
            s += "The gap is not a weakness — it shows where you are fluent and where there is room to grow."
        s += "\n\nIn short: you are not the 'typical " + sun + " Sun' from a book, "
        s += f"but the specific intersection of {sun} + {moon} + {asc} with your own aspects — "
        s += "a whole that is true only for you."
        return s


RuleRegistry.register(ExecutiveSummaryRule())
