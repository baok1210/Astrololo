"""Jyotish (Vedic astrology) constants — Navagraha, Nakshatra, Dasha, dignities.

Separate from Western constants to keep the two systems clean.
Data sourced from BPHS (Brihat Parashara Hora Shastra) and Navagraha study materials.
"""
from typing import NamedTuple, List, Dict, Tuple


# ---------------------------------------------------------------------------
# Graha (Planet) definitions
# ---------------------------------------------------------------------------

class GrahaInfo(NamedTuple):
    name_sa: str        # Sanskrit
    name_vi: str        # Vietnamese
    name_en: str        # English
    western_key: str    # key in ephemeris._PLANET_CODES / constants.PLANETS
    symbol: str
    tattwa: str         # Agni/Jala/Prithvi/Vayu/Akash
    guna: str           # Sattwa/Rajas/Tamas
    nature: str         # shubha (benefic) / papa (malefic) / neutral
    own_signs: List[str]
    moolatrikona_sign: str
    moolatrikona_range: Tuple[float, float]  # degree range within sign
    exaltation_sign: str
    exaltation_degree: float
    debilitation_sign: str
    debilitation_degree: float
    vara_day: str       # weekday ruled ("" for Rahu/Ketu)
    friends: List[str]
    enemies: List[str]


NAVAGRAHA: Dict[str, GrahaInfo] = {
    "surya": GrahaInfo(
        "Surya", "Mặt Trời", "Sun", "sun", "☉",
        "agni", "sattwa", "papa",
        ["leo"], "leo", (0, 20),
        "aries", 10.0, "libra", 10.0,
        "sunday",
        ["moon", "mars", "jupiter"], ["venus", "saturn"],
    ),
    "chandra": GrahaInfo(
        "Chandra", "Mặt Trăng", "Moon", "moon", "☽",
        "jala", "sattwa", "shubha",
        ["cancer"], "taurus", (4, 20),
        "taurus", 3.0, "scorpio", 3.0,
        "monday",
        ["sun", "mercury"], [],
    ),
    "mangala": GrahaInfo(
        "Mangala", "Hỏa Tinh", "Mars", "mars", "♂",
        "agni", "tamas", "papa",
        ["aries", "scorpio"], "aries", (0, 12),
        "capricorn", 28.0, "cancer", 28.0,
        "tuesday",
        ["sun", "moon", "jupiter"], ["mercury"],
    ),
    "budha": GrahaInfo(
        "Budha", "Thủy Tinh", "Mercury", "mercury", "☿",
        "prithvi", "rajas", "neutral",
        ["gemini", "virgo"], "virgo", (16, 20),
        "virgo", 15.0, "pisces", 15.0,
        "wednesday",
        ["sun", "venus"], ["moon"],
    ),
    "guru": GrahaInfo(
        "Guru", "Mộc Tinh", "Jupiter", "jupiter", "♃",
        "akash", "sattwa", "shubha",
        ["sagittarius", "pisces"], "sagittarius", (0, 10),
        "cancer", 5.0, "capricorn", 5.0,
        "thursday",
        ["sun", "moon", "mars"], ["mercury", "venus"],
    ),
    "shukra": GrahaInfo(
        "Shukra", "Kim Tinh", "Venus", "venus", "♀",
        "jala", "rajas", "shubha",
        ["taurus", "libra"], "libra", (0, 15),
        "pisces", 27.0, "virgo", 27.0,
        "friday",
        ["mercury", "saturn"], ["sun", "moon"],
    ),
    "shani": GrahaInfo(
        "Shani", "Thổ Tinh", "Saturn", "saturn", "♄",
        "vayu", "tamas", "papa",
        ["capricorn", "aquarius"], "aquarius", (0, 20),
        "libra", 20.0, "aries", 20.0,
        "saturday",
        ["mercury", "venus"], ["sun", "moon", "mars"],
    ),
    "rahu": GrahaInfo(
        "Rahu", "La Hầu", "Rahu", "mean_node", "☊",
        "vayu", "tamas", "papa",
        [], "", (0, 0),
        "taurus", 20.0, "scorpio", 20.0,
        "",
        ["venus", "saturn"], ["sun", "moon", "mars"],
    ),
    "ketu": GrahaInfo(
        "Ketu", "Kế Đô", "Ketu", "", "☋",
        "agni", "tamas", "papa",
        [], "", (0, 0),
        "scorpio", 20.0, "taurus", 20.0,
        "",
        ["mars", "venus", "saturn"], ["sun", "moon"],
    ),
}

NAVAGRAHA_ORDER = ["surya", "chandra", "mangala", "budha", "guru", "shukra", "shani", "rahu", "ketu"]

WESTERN_TO_GRAHA: Dict[str, str] = {
    "sun": "surya", "moon": "chandra", "mars": "mangala",
    "mercury": "budha", "jupiter": "guru", "venus": "shukra",
    "saturn": "shani", "mean_node": "rahu", "true_node": "rahu",
    "north_node": "rahu", "south_node": "ketu",
}

GRAHA_TO_WESTERN: Dict[str, str] = {
    "surya": "sun", "chandra": "moon", "mangala": "mars",
    "budha": "mercury", "guru": "jupiter", "shukra": "venus",
    "shani": "saturn", "rahu": "mean_node", "ketu": "",
}


# ---------------------------------------------------------------------------
# Jyotish sign rulers (traditional only — no Uranus/Neptune/Pluto)
# ---------------------------------------------------------------------------

JYOTISH_SIGN_RULERS: Dict[str, str] = {
    "aries": "mangala", "taurus": "shukra", "gemini": "budha",
    "cancer": "chandra", "leo": "surya", "virgo": "budha",
    "libra": "shukra", "scorpio": "mangala", "sagittarius": "guru",
    "capricorn": "shani", "aquarius": "shani", "pisces": "guru",
}


# ---------------------------------------------------------------------------
# Rashi (Sign) names in Sanskrit/Vietnamese
# ---------------------------------------------------------------------------

RASHI_NAMES: Dict[str, Tuple[str, str]] = {
    "aries": ("Mesha", "Dương Cưu"),
    "taurus": ("Vrishabha", "Kim Ngưu"),
    "gemini": ("Mithuna", "Song Tử"),
    "cancer": ("Karka", "Cự Giải"),
    "leo": ("Simha", "Sư Tử"),
    "virgo": ("Kanya", "Xử Nữ"),
    "libra": ("Tula", "Thiên Bình"),
    "scorpio": ("Vrishchika", "Thần Nông"),
    "sagittarius": ("Dhanu", "Nhân Mã"),
    "capricorn": ("Makara", "Ma Kết"),
    "aquarius": ("Kumbha", "Bảo Bình"),
    "pisces": ("Meena", "Song Ngư"),
}


# ---------------------------------------------------------------------------
# 27 Nakshatras
# ---------------------------------------------------------------------------

class NakshatraInfo(NamedTuple):
    number: int         # 1-27
    name_sa: str        # Sanskrit
    name_vi: str        # Vietnamese
    ruler: str          # graha key (for Vimshottari Dasha)
    deity: str          # presiding deity
    symbol: str
    gana: str           # Deva / Manushya / Rakshasa
    quality: str        # Dhruva/Chara/Tikshna/Mridu/Ugra/Mishra


NAKSHATRA_SPAN = 360.0 / 27  # 13°20' = 13.3333...°
PADA_SPAN = NAKSHATRA_SPAN / 4  # 3°20' = 3.3333...°

NAKSHATRAS: List[NakshatraInfo] = [
    NakshatraInfo(1, "Ashwini", "Mã Tinh", "ketu", "Ashwini Kumaras", "Đầu ngựa", "Deva", "Chara"),
    NakshatraInfo(2, "Bharani", "Vị Tinh", "shukra", "Yama", "Yoni", "Manushya", "Ugra"),
    NakshatraInfo(3, "Krittika", "Mão Tinh", "surya", "Agni", "Dao cạo", "Rakshasa", "Mishra"),
    NakshatraInfo(4, "Rohini", "Tất Tinh", "chandra", "Brahma", "Xe bò", "Manushya", "Dhruva"),
    NakshatraInfo(5, "Mrigashira", "Sâm Tinh", "mangala", "Soma", "Đầu nai", "Deva", "Mridu"),
    NakshatraInfo(6, "Ardra", "Tỉnh Tinh", "rahu", "Rudra", "Giọt nước mắt", "Manushya", "Tikshna"),
    NakshatraInfo(7, "Punarvasu", "Quỷ Tinh", "guru", "Aditi", "Cung tên", "Deva", "Chara"),
    NakshatraInfo(8, "Pushya", "Liễu Tinh", "shani", "Brihaspati", "Bông hoa", "Deva", "Dhruva"),
    NakshatraInfo(9, "Ashlesha", "Tinh Tinh", "budha", "Sarpa", "Rắn", "Rakshasa", "Tikshna"),
    NakshatraInfo(10, "Magha", "Trương Tinh", "ketu", "Pitris", "Ngai vàng", "Rakshasa", "Ugra"),
    NakshatraInfo(11, "Purva Phalguni", "Dực Tinh", "shukra", "Bhaga", "Giường", "Manushya", "Ugra"),
    NakshatraInfo(12, "Uttara Phalguni", "Chẩn Tinh", "surya", "Aryaman", "Giường", "Manushya", "Dhruva"),
    NakshatraInfo(13, "Hasta", "Giác Tinh", "chandra", "Savitar", "Bàn tay", "Deva", "Chara"),
    NakshatraInfo(14, "Chitra", "Cang Tinh", "mangala", "Tvashtar", "Ngọc trai", "Rakshasa", "Mridu"),
    NakshatraInfo(15, "Swati", "Đê Tinh", "rahu", "Vayu", "San hô", "Deva", "Chara"),
    NakshatraInfo(16, "Vishakha", "Phòng Tinh", "guru", "Indragni", "Cổng vòm", "Rakshasa", "Mishra"),
    NakshatraInfo(17, "Anuradha", "Tâm Tinh", "shani", "Mitra", "Hoa sen", "Deva", "Mridu"),
    NakshatraInfo(18, "Jyeshtha", "Vĩ Tinh", "budha", "Indra", "Bùa hộ mệnh", "Rakshasa", "Tikshna"),
    NakshatraInfo(19, "Moola", "Cơ Tinh", "ketu", "Nirriti", "Rễ cây", "Rakshasa", "Tikshna"),
    NakshatraInfo(20, "Purva Ashadha", "Đẩu Tinh", "shukra", "Apas", "Quạt", "Manushya", "Ugra"),
    NakshatraInfo(21, "Uttara Ashadha", "Ngưu Tinh", "surya", "Vishvedevas", "Ngà voi", "Manushya", "Dhruva"),
    NakshatraInfo(22, "Shravana", "Nữ Tinh", "chandra", "Vishnu", "Đôi tai", "Deva", "Chara"),
    NakshatraInfo(23, "Dhanishta", "Hư Tinh", "mangala", "Vasus", "Trống", "Rakshasa", "Chara"),
    NakshatraInfo(24, "Shatabhisha", "Nguy Tinh", "rahu", "Varuna", "Vòng tròn", "Rakshasa", "Chara"),
    NakshatraInfo(25, "Purva Bhadrapada", "Thất Tinh", "guru", "Aja Ekapada", "Kiếm", "Manushya", "Ugra"),
    NakshatraInfo(26, "Uttara Bhadrapada", "Bích Tinh", "shani", "Ahir Budhnya", "Rắn đôi", "Manushya", "Dhruva"),
    NakshatraInfo(27, "Revati", "Khuê Tinh", "budha", "Pushan", "Cá", "Deva", "Mridu"),
]


# ---------------------------------------------------------------------------
# Vimshottari Dasha
# ---------------------------------------------------------------------------

DASHA_YEARS: Dict[str, float] = {
    "ketu": 7, "shukra": 20, "surya": 6, "chandra": 10,
    "mangala": 7, "rahu": 18, "guru": 16, "shani": 19, "budha": 17,
}

DASHA_SEQUENCE: List[str] = [
    "ketu", "shukra", "surya", "chandra", "mangala",
    "rahu", "guru", "shani", "budha",
]

TOTAL_DASHA_YEARS = 120.0


# ---------------------------------------------------------------------------
# Vara (day rulers)
# ---------------------------------------------------------------------------

VARA_RULERS: Dict[int, str] = {
    6: "surya",     # Sunday (Python weekday: 6)
    0: "chandra",   # Monday
    1: "mangala",   # Tuesday
    2: "budha",     # Wednesday
    3: "guru",      # Thursday
    4: "shukra",    # Friday
    5: "shani",     # Saturday
}

VARA_NAMES_VI: Dict[str, str] = {
    "surya": "Chủ Nhật", "chandra": "Thứ Hai", "mangala": "Thứ Ba",
    "budha": "Thứ Tư", "guru": "Thứ Năm", "shukra": "Thứ Sáu",
    "shani": "Thứ Bảy",
}


# ---------------------------------------------------------------------------
# Tattwa & Guna names
# ---------------------------------------------------------------------------

TATTWA_NAMES_VI: Dict[str, str] = {
    "agni": "Lửa (Agni)", "jala": "Nước (Jala)", "prithvi": "Đất (Prithvi)",
    "vayu": "Gió (Vayu)", "akash": "Không gian (Akash)",
}

GUNA_NAMES_VI: Dict[str, str] = {
    "sattwa": "Sattwa (Thuần khiết)", "rajas": "Rajas (Hoạt động)",
    "tamas": "Tamas (Trì trệ)",
}


# ---------------------------------------------------------------------------
# Dignity helpers
# ---------------------------------------------------------------------------

def get_jyotish_dignity(graha_key: str, sign: str, degree_in_sign: float = 15.0) -> str:
    """Return Jyotish dignity: uchcha/neecha/moolatrikona/swakshetra/neutral."""
    graha = NAVAGRAHA.get(graha_key)
    if not graha:
        return "neutral"

    if sign == graha.exaltation_sign:
        return "uchcha"  # exalted

    if sign == graha.debilitation_sign:
        return "neecha"  # debilitated

    if sign == graha.moolatrikona_sign:
        lo, hi = graha.moolatrikona_range
        if lo <= degree_in_sign <= hi:
            return "moolatrikona"
        if sign in graha.own_signs:
            return "swakshetra"

    if sign in graha.own_signs:
        return "swakshetra"  # own sign

    return "neutral"


DIGNITY_NAMES_VI: Dict[str, str] = {
    "uchcha": "Vượng (Exalted)",
    "neecha": "Suy (Debilitated)",
    "moolatrikona": "Moolatrikona",
    "swakshetra": "Tự quản (Own Sign)",
    "neutral": "Trung tính",
}

DIGNITY_SCORES: Dict[str, int] = {
    "uchcha": 5,
    "moolatrikona": 4,
    "swakshetra": 3,
    "neutral": 0,
    "neecha": -5,
}


def calc_nakshatra(sidereal_lon: float) -> Tuple[int, NakshatraInfo, int]:
    """Calculate nakshatra index (0-26), info, and pada (1-4) from sidereal longitude."""
    lon = sidereal_lon % 360
    nak_idx = int(lon / NAKSHATRA_SPAN) % 27
    pos_in_nak = lon - nak_idx * NAKSHATRA_SPAN
    pada = int(pos_in_nak / PADA_SPAN) + 1
    pada = min(pada, 4)
    return nak_idx, NAKSHATRAS[nak_idx], pada
