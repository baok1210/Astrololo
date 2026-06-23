from typing import Dict
from astrololo.core.constants import PLANETS, SIGNS, HOUSES, ASPECTS


_TRANSLATION_TERMS: Dict[str, Dict[str, str]] = {
    ## Planets
    "sun": {"vi": "Mặt Trời", "en": "Sun"},
    "moon": {"vi": "Mặt Trăng", "en": "Moon"},
    "mercury": {"vi": "Sao Thủy", "en": "Mercury"},
    "venus": {"vi": "Sao Kim", "en": "Venus"},
    "mars": {"vi": "Sao Hỏa", "en": "Mars"},
    "jupiter": {"vi": "Sao Mộc", "en": "Jupiter"},
    "saturn": {"vi": "Sao Thổ", "en": "Saturn"},
    "uranus": {"vi": "Sao Thiên Vương", "en": "Uranus"},
    "neptune": {"vi": "Sao Hải Vương", "en": "Neptune"},
    "pluto": {"vi": "Sao Diêm Vương", "en": "Pluto"},
    ## Signs
    "aries": {"vi": "Bạch Dương", "en": "Aries"},
    "taurus": {"vi": "Kim Ngưu", "en": "Taurus"},
    "gemini": {"vi": "Song Tử", "en": "Gemini"},
    "cancer": {"vi": "Cự Giải", "en": "Cancer"},
    "leo": {"vi": "Sư Tử", "en": "Leo"},
    "virgo": {"vi": "Xử Nữ", "en": "Virgo"},
    "libra": {"vi": "Thiên Bình", "en": "Libra"},
    "scorpio": {"vi": "Bọ Cạp", "en": "Scorpio"},
    "sagittarius": {"vi": "Nhân Mã", "en": "Sagittarius"},
    "capricorn": {"vi": "Ma Kết", "en": "Capricorn"},
    "aquarius": {"vi": "Bảo Bình", "en": "Aquarius"},
    "pisces": {"vi": "Song Ngư", "en": "Pisces"},
    ## Aspects
    "conjunction": {"vi": "Hợp", "en": "Conjunction"},
    "sextile": {"vi": "Lục Hợp", "en": "Sextile"},
    "square": {"vi": "Vuông Góc", "en": "Square"},
    "trine": {"vi": "Tam Hợp", "en": "Trine"},
    "opposition": {"vi": "Đối Xung", "en": "Opposition"},
    "quincunx": {"vi": "Bát Xung", "en": "Quincunx"},
    ## Elements
    "fire": {"vi": "Lửa", "en": "Fire"},
    "earth": {"vi": "Đất", "en": "Earth"},
    "air": {"vi": "Khí", "en": "Air"},
    "water": {"vi": "Nước", "en": "Water"},
    ## Qualities
    "cardinal": {"vi": "Thống Lĩnh", "en": "Cardinal"},
    "fixed": {"vi": "Cố Định", "en": "Fixed"},
    "mutable": {"vi": "Linh Hoạt", "en": "Mutable"},
    ## Common terms
    "ascendant": {"vi": "Cung Mọc", "en": "Ascendant"},
    "midheaven": {"vi": "Thiên Đỉnh", "en": "Midheaven"},
    "retrograde": {"vi": "Nghịch Hành", "en": "Retrograde"},
    "direct": {"vi": "Thuận Hành", "en": "Direct"},
}


class BilingualHelper:
    def __init__(self, lang: str = "vi"):
        self.lang = lang if lang in ("vi", "en") else "vi"

    def t(self, key: str) -> str:
        entry = _TRANSLATION_TERMS.get(key, {})
        return entry.get(self.lang, key)

    def planet(self, key: str) -> str:
        p = PLANETS.get(key)
        return p.name_vi if p and self.lang == "vi" else p.name_en if p else key

    def sign(self, key: str) -> str:
        s = SIGNS.get(key)
        return s.name_vi if s and self.lang == "vi" else s.name_en if s else key

    def house(self, num: int) -> str:
        h = HOUSES.get(num)
        return h.name_vi if h and self.lang == "vi" else h.name_en if h else str(num)

    def aspect(self, key: str) -> str:
        a = ASPECTS.get(key)
        return a.name_vi if a and self.lang == "vi" else a.name_en if a else key

    def element(self, key: str) -> str:
        return self.t(key)

    def quality(self, key: str) -> str:
        return self.t(key)

    def format_dms(self, degree: float) -> str:
        d = int(degree)
        m = int((degree - d) * 60)
        s = round(((degree - d) * 60 - m) * 60)
        return f"{d}°{m:02d}'{s:02d}\""

    def get(self, key: str, default: str = "") -> str:
        return self.t(key) or default
