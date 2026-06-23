from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class Planet:
    key: str
    name_vi: str
    name_en: str
    symbol: str
    ruler_of: List[str]
    exaltation: Optional[str]
    fall: Optional[str]
    detriment: List[str]
    keywords_vi: List[str]
    keywords_en: List[str]
    natura: str  # benefic / malefic / neutral
    is_social: bool = False
    is_transpersonal: bool = False
    speed_daily: float = 1.0  # degrees per day approx


@dataclass(frozen=True)
class Sign:
    key: str
    name_vi: str
    name_en: str
    symbol: str
    element: str  # fire / earth / air / water
    quality: str  # cardinal / fixed / mutable
    polarity: str  # positive / negative
    ruler: str
    exaltation_planet: Optional[str]
    fall_planet: Optional[str]
    detriment_planet: Optional[str]
    keywords_vi: List[str]
    keywords_en: List[str]
    house_theme_vi: str
    house_theme_en: str
    degree_range: tuple = (0, 30)


@dataclass(frozen=True)
class Aspect:
    key: str
    name_vi: str
    name_en: str
    symbol: str
    angle: float
    orb: float
    weight: int
    nature: str  # harmonious / challenging / neutral


@dataclass(frozen=True)
class House:
    number: int
    name_vi: str
    name_en: str
    type_: str  # angular / succedent / cadent
    weight: int
    keywords_vi: List[str]
    keywords_en: List[str]
    natural_sign: str  # natural zodiac correspondence


PLANETS: Dict[str, Planet] = {
    "sun": Planet(
        key="sun",
        name_vi="Mặt Trời",
        name_en="Sun",
        symbol="☉",
        ruler_of=["leo"],
        exaltation="aries",
        fall="libra",
        detriment=["aquarius"],
        keywords_vi=["bản ngã", "ý thức", "cá tính", "sức sống", "mục đích"],
        keywords_en=["ego", "identity", "vitality", "life purpose", "self-expression"],
        natura="neutral",
        speed_daily=0.9856,
    ),
    "moon": Planet(
        key="moon",
        name_vi="Mặt Trăng",
        name_en="Moon",
        symbol="☽",
        ruler_of=["cancer"],
        exaltation="taurus",
        fall="scorpio",
        detriment=["capricorn"],
        keywords_vi=["cảm xúc", "tiềm thức", "bản năng", "thói quen", "nhu cầu"],
        keywords_en=["emotions", "subconscious", "instincts", "habits", "needs"],
        natura="benefic",
        speed_daily=13.176,
    ),
    "mercury": Planet(
        key="mercury",
        name_vi="Sao Thủy",
        name_en="Mercury",
        symbol="☿",
        ruler_of=["gemini", "virgo"],
        exaltation="virgo",
        fall="pisces",
        detriment=["sagittarius", "pisces"],
        keywords_vi=["tư duy", "giao tiếp", "học hỏi", "lý trí", "ngôn ngữ"],
        keywords_en=["mind", "communication", "learning", "intellect", "language"],
        natura="neutral",
        speed_daily=1.383,
    ),
    "venus": Planet(
        key="venus",
        name_vi="Sao Kim",
        name_en="Venus",
        symbol="♀",
        ruler_of=["taurus", "libra"],
        exaltation="pisces",
        fall="virgo",
        detriment=["aries", "scorpio"],
        keywords_vi=["tình yêu", "sắc đẹp", "giá trị", "hài hòa", "hưởng thụ"],
        keywords_en=["love", "beauty", "values", "harmony", "pleasure"],
        natura="benefic",
        speed_daily=1.2,
    ),
    "mars": Planet(
        key="mars",
        name_vi="Sao Hỏa",
        name_en="Mars",
        symbol="♂",
        ruler_of=["aries", "scorpio"],
        exaltation="capricorn",
        fall="cancer",
        detriment=["taurus", "libra"],
        keywords_vi=["hành động", "năng lượng", "tham vọng", "xung đột", "đam mê"],
        keywords_en=["action", "energy", "ambition", "conflict", "passion"],
        natura="malefic",
        speed_daily=0.524,
    ),
    "jupiter": Planet(
        key="jupiter",
        name_vi="Sao Mộc",
        name_en="Jupiter",
        symbol="♃",
        ruler_of=["sagittarius", "pisces"],
        exaltation="cancer",
        fall="capricorn",
        detriment=["gemini", "virgo"],
        keywords_vi=["may mắn", "mở rộng", "triết lý", "dư dả", "lạc quan"],
        keywords_en=["luck", "expansion", "philosophy", "abundance", "optimism"],
        natura="benefic",
        is_social=True,
        speed_daily=0.083,
    ),
    "saturn": Planet(
        key="saturn",
        name_vi="Sao Thổ",
        name_en="Saturn",
        symbol="♄",
        ruler_of=["capricorn", "aquarius"],
        exaltation="libra",
        fall="aries",
        detriment=["cancer", "leo"],
        keywords_vi=["kỷ luật", "trách nhiệm", "bài học", "kiềm chế", "cấu trúc"],
        keywords_en=[
            "discipline",
            "responsibility",
            "lessons",
            "restriction",
            "structure",
        ],
        natura="malefic",
        is_social=True,
        speed_daily=0.033,
    ),
    "uranus": Planet(
        key="uranus",
        name_vi="Sao Thiên Vương",
        name_en="Uranus",
        symbol="♅",
        ruler_of=["aquarius"],
        exaltation="scorpio",
        fall="taurus",
        detriment=["leo"],
        keywords_vi=["đột phá", "cách mạng", "sáng tạo", "tự do", "khác biệt"],
        keywords_en=["innovation", "revolution", "originality", "freedom", "change"],
        natura="neutral",
        is_transpersonal=True,
        speed_daily=0.012,
    ),
    "neptune": Planet(
        key="neptune",
        name_vi="Sao Hải Vương",
        name_en="Neptune",
        symbol="♆",
        ruler_of=["pisces"],
        exaltation="cancer",
        fall="capricorn",
        detriment=["virgo"],
        keywords_vi=["mơ mộng", "tâm linh", "trực giác", "ảo ảnh", "nghệ thuật"],
        keywords_en=["dreams", "spirituality", "intuition", "illusion", "art"],
        natura="neutral",
        is_transpersonal=True,
        speed_daily=0.006,
    ),
    "pluto": Planet(
        key="pluto",
        name_vi="Sao Diêm Vương",
        name_en="Pluto",
        symbol="♇",
        ruler_of=["scorpio"],
        exaltation=None,
        fall=None,
        detriment=["taurus"],
        keywords_vi=["chuyển hóa", "quyền lực", "tái sinh", "bí ẩn", "kiểm soát"],
        keywords_en=["transformation", "power", "rebirth", "mystery", "control"],
        natura="neutral",
        is_transpersonal=True,
        speed_daily=0.002,
    ),
    "north_node": Planet(
        key="north_node",
        name_vi="La Hầu",
        name_en="North Node",
        symbol="☊",
        ruler_of=[],
        exaltation=None,
        fall=None,
        detriment=[],
        keywords_vi=["nghiệp quả", "định mệnh", "phát triển"],
        keywords_en=["karma", "destiny", "growth"],
        natura="neutral",
        speed_daily=0.0,
    ),
    "south_node": Planet(
        key="south_node",
        name_vi="Kế Hầu",
        name_en="South Node",
        symbol="☋",
        ruler_of=[],
        exaltation=None,
        fall=None,
        detriment=[],
        keywords_vi=["nghiệp quá khứ", "thói quen", "bài học cũ"],
        keywords_en=["past karma", "habits", "past lessons"],
        natura="neutral",
        speed_daily=0.0,
    ),
    "ascendant": Planet(
        key="ascendant",
        name_vi="Cung Mọc",
        name_en="Ascendant",
        symbol="AS",
        ruler_of=[],
        exaltation=None,
        fall=None,
        detriment=[],
        keywords_vi=["bản thân", "ngoại hình", "cá tính", "khởi đầu"],
        keywords_en=["self", "appearance", "personality", "beginnings"],
        natura="neutral",
        speed_daily=0.0,
    ),
    "mc": Planet(
        key="mc",
        name_vi="Thiên Đỉnh",
        name_en="MC",
        symbol="MC",
        ruler_of=[],
        exaltation=None,
        fall=None,
        detriment=[],
        keywords_vi=["sự nghiệp", "danh vọng", "địa vị", "mục tiêu"],
        keywords_en=["career", "reputation", "status", "goals"],
        natura="neutral",
        speed_daily=0.0,
    ),
    "descendant": Planet(
        key="descendant",
        name_vi="Cung Lặn",
        name_en="Descendant",
        symbol="DS",
        ruler_of=[],
        exaltation=None,
        fall=None,
        detriment=[],
        keywords_vi=["hôn nhân", "đối tác", "quan hệ", "hợp đồng"],
        keywords_en=["marriage", "partnerships", "relationships", "contracts"],
        natura="neutral",
        speed_daily=0.0,
    ),
    "ic": Planet(
        key="ic",
        name_vi="Thiên Đế",
        name_en="IC",
        symbol="IC",
        ruler_of=[],
        exaltation=None,
        fall=None,
        detriment=[],
        keywords_vi=["gia đình", "cội nguồn", "nhà cửa", "cảm xúc nền tảng"],
        keywords_en=["family", "home", "roots", "emotional foundation"],
        natura="neutral",
        speed_daily=0.0,
    ),
    "chiron": Planet(
        key="chiron",
        name_vi="Chiron",
        name_en="Chiron",
        symbol="⚷",
        ruler_of=[],
        exaltation=None,
        fall=None,
        detriment=[],
        keywords_vi=["vết thương", "chữa lành", "khai sáng", "dạy dỗ", "bản ngã cao"],
        keywords_en=["wound", "healing", "wisdom", "teaching", "higher self"],
        natura="neutral",
        speed_daily=0.003,
    ),
    "ceres": Planet(
        key="ceres",
        name_vi="Ceres",
        name_en="Ceres",
        symbol="⚳",
        ruler_of=[],
        exaltation=None,
        fall=None,
        detriment=[],
        keywords_vi=["mẹ", "mùa màng", "dinh dưỡng", "chu kỳ", "truyền thống"],
        keywords_en=["motherhood", "harvest", "nurturing", "cycles", "tradition"],
        natura="neutral",
        speed_daily=0.004,
    ),
    "pallas": Planet(
        key="pallas",
        name_vi="Pallas",
        name_en="Pallas",
        symbol="⚴",
        ruler_of=[],
        exaltation=None,
        fall=None,
        detriment=[],
        keywords_vi=["trí tuệ", "chiến lược", "sáng tạo", "công bằng", "khéo léo"],
        keywords_en=["wisdom", "strategy", "creativity", "justice", "craftsmanship"],
        natura="neutral",
        speed_daily=0.004,
    ),
    "juno": Planet(
        key="juno",
        name_vi="Juno",
        name_en="Juno",
        symbol="⚵",
        ruler_of=[],
        exaltation=None,
        fall=None,
        detriment=[],
        keywords_vi=["hôn nhân", "cam kết", "đối tác", "lòng chung thủy", "bình đẳng"],
        keywords_en=["marriage", "commitment", "partnership", "fidelity", "equality"],
        natura="neutral",
        speed_daily=0.003,
    ),
    "vesta": Planet(
        key="vesta",
        name_vi="Vesta",
        name_en="Vesta",
        symbol="⚶",
        ruler_of=[],
        exaltation=None,
        fall=None,
        detriment=[],
        keywords_vi=["cống hiến", "tập trung", "hy sinh", "nhiệt tâm", "tinh khiết"],
        keywords_en=["dedication", "focus", "sacrifice", "devotion", "purity"],
        natura="neutral",
        speed_daily=0.003,
    ),
    "lilith": Planet(
        key="lilith",
        name_vi="Lilith",
        name_en="Black Moon Lilith",
        symbol="⚸",
        ruler_of=[],
        exaltation=None,
        fall=None,
        detriment=[],
        keywords_vi=["bóng tối", "nữ quyền", "tự do", "bản năng gốc", "bị kìm nén"],
        keywords_en=["shadow", "feminine power", "freedom", "raw instinct", "repressed"],
        natura="neutral",
        speed_daily=0.003,
    ),
}


SIGNS: Dict[str, Sign] = {
    "aries": Sign(
        key="aries",
        name_vi="Bạch Dương",
        name_en="Aries",
        symbol="♈",
        element="fire",
        quality="cardinal",
        polarity="positive",
        ruler="mars",
        exaltation_planet="sun",
        fall_planet="saturn",
        detriment_planet="venus",
        keywords_vi=["tiên phong", "dũng cảm", "bốc đồng", "cạnh tranh", "năng động"],
        keywords_en=[
            "pioneering",
            "courageous",
            "impulsive",
            "competitive",
            "energetic",
        ],
        house_theme_vi="bản thân, khởi đầu",
        house_theme_en="self, beginnings",
    ),
    "taurus": Sign(
        key="taurus",
        name_vi="Kim Ngưu",
        name_en="Taurus",
        symbol="♉",
        element="earth",
        quality="fixed",
        polarity="negative",
        ruler="venus",
        exaltation_planet="moon",
        fall_planet="uranus",
        detriment_planet="mars",
        keywords_vi=["kiên định", "thực tế", "kiên nhẫn", "hưởng thụ", "đáng tin"],
        keywords_en=["stable", "practical", "patient", "sensual", "reliable"],
        house_theme_vi="tài chính, giá trị",
        house_theme_en="finances, values",
    ),
    "gemini": Sign(
        key="gemini",
        name_vi="Song Tử",
        name_en="Gemini",
        symbol="♊",
        element="air",
        quality="mutable",
        polarity="positive",
        ruler="mercury",
        exaltation_planet=None,
        fall_planet=None,
        detriment_planet="jupiter",
        keywords_vi=["linh hoạt", "tò mò", "giao tiếp", "thích nghi", "đa năng"],
        keywords_en=["versatile", "curious", "communicative", "adaptable", "witty"],
        house_theme_vi="giao tiếp, học tập",
        house_theme_en="communication, learning",
    ),
    "cancer": Sign(
        key="cancer",
        name_vi="Cự Giải",
        name_en="Cancer",
        symbol="♋",
        element="water",
        quality="cardinal",
        polarity="negative",
        ruler="moon",
        exaltation_planet="jupiter",
        fall_planet="mars",
        detriment_planet="saturn",
        keywords_vi=["nhạy cảm", "nuôi dưỡng", "gia đình", "bảo vệ", "trực giác"],
        keywords_en=["sensitive", "nurturing", "family", "protective", "intuitive"],
        house_theme_vi="gia đình, cảm xúc",
        house_theme_en="family, emotions",
    ),
    "leo": Sign(
        key="leo",
        name_vi="Sư Tử",
        name_en="Leo",
        symbol="♌",
        element="fire",
        quality="fixed",
        polarity="positive",
        ruler="sun",
        exaltation_planet=None,
        fall_planet=None,
        detriment_planet="saturn",
        keywords_vi=["tỏa sáng", "hào phóng", "sáng tạo", "tự tin", "lãnh đạo"],
        keywords_en=["dramatic", "generous", "creative", "confident", "leadership"],
        house_theme_vi="sáng tạo, giải trí",
        house_theme_en="creativity, entertainment",
    ),
    "virgo": Sign(
        key="virgo",
        name_vi="Xử Nữ",
        name_en="Virgo",
        symbol="♍",
        element="earth",
        quality="mutable",
        polarity="negative",
        ruler="mercury",
        exaltation_planet="mercury",
        fall_planet="venus",
        detriment_planet="jupiter",
        keywords_vi=["phân tích", "tỉ mỉ", "khiêm tốn", "cầu toàn", "phục vụ"],
        keywords_en=["analytical", "meticulous", "humble", "perfectionist", "service"],
        house_theme_vi="công việc, sức khỏe",
        house_theme_en="work, health",
    ),
    "libra": Sign(
        key="libra",
        name_vi="Thiên Bình",
        name_en="Libra",
        symbol="♎",
        element="air",
        quality="cardinal",
        polarity="positive",
        ruler="venus",
        exaltation_planet="saturn",
        fall_planet="sun",
        detriment_planet="mars",
        keywords_vi=["cân bằng", "công bằng", "ngoại giao", "hợp tác", "thẩm mỹ"],
        keywords_en=["balanced", "fair", "diplomatic", "cooperative", "aesthetic"],
        house_theme_vi="hôn nhân, đối tác",
        house_theme_en="marriage, partnerships",
    ),
    "scorpio": Sign(
        key="scorpio",
        name_vi="Bọ Cạp",
        name_en="Scorpio",
        symbol="♏",
        element="water",
        quality="fixed",
        polarity="negative",
        ruler="mars",
        exaltation_planet="uranus",
        fall_planet="moon",
        detriment_planet="venus",
        keywords_vi=["sâu sắc", "mãnh liệt", "bí ẩn", "kiên định", "chuyển hóa"],
        keywords_en=[
            "intense",
            "passionate",
            "secretive",
            "determined",
            "transformative",
        ],
        house_theme_vi="chuyển hóa, tài chính chung",
        house_theme_en="transformation, joint finances",
    ),
    "sagittarius": Sign(
        key="sagittarius",
        name_vi="Nhân Mã",
        name_en="Sagittarius",
        symbol="♐",
        element="fire",
        quality="mutable",
        polarity="positive",
        ruler="jupiter",
        exaltation_planet=None,
        fall_planet=None,
        detriment_planet="mercury",
        keywords_vi=["tự do", "phiêu lưu", "lạc quan", "triết lý", "khám phá"],
        keywords_en=["free", "adventurous", "optimistic", "philosophical", "exploring"],
        house_theme_vi="du lịch, triết học",
        house_theme_en="travel, philosophy",
    ),
    "capricorn": Sign(
        key="capricorn",
        name_vi="Ma Kết",
        name_en="Capricorn",
        symbol="♑",
        element="earth",
        quality="cardinal",
        polarity="negative",
        ruler="saturn",
        exaltation_planet="mars",
        fall_planet="jupiter",
        detriment_planet="moon",
        keywords_vi=["tham vọng", "kỷ luật", "trách nhiệm", "kiên trì", "thực dụng"],
        keywords_en=[
            "ambitious",
            "disciplined",
            "responsible",
            "persistent",
            "pragmatic",
        ],
        house_theme_vi="sự nghiệp, địa vị",
        house_theme_en="career, status",
    ),
    "aquarius": Sign(
        key="aquarius",
        name_vi="Bảo Bình",
        name_en="Aquarius",
        symbol="♒",
        element="air",
        quality="fixed",
        polarity="positive",
        ruler="saturn",
        exaltation_planet=None,
        fall_planet=None,
        detriment_planet="sun",
        keywords_vi=["độc đáo", "nhân đạo", "sáng tạo", "phóng khoáng", "tập thể"],
        keywords_en=[
            "original",
            "humanitarian",
            "innovative",
            "progressive",
            "collective",
        ],
        house_theme_vi="bạn bè, lý tưởng",
        house_theme_en="friends, ideals",
    ),
    "pisces": Sign(
        key="pisces",
        name_vi="Song Ngư",
        name_en="Pisces",
        symbol="♓",
        element="water",
        quality="mutable",
        polarity="negative",
        ruler="jupiter",
        exaltation_planet="venus",
        fall_planet="mercury",
        detriment_planet="mercury",
        keywords_vi=["mơ mộng", "đồng cảm", "tâm linh", "nghệ thuật", "thích nghi"],
        keywords_en=["dreamy", "compassionate", "spiritual", "artistic", "adaptable"],
        house_theme_vi="tiềm thức, tâm linh",
        house_theme_en="subconscious, spirituality",
    ),
}


ASPECTS: Dict[str, Aspect] = {
    "conjunction": Aspect(
        key="conjunction",
        name_vi="Hợp",
        name_en="Conjunction",
        symbol="☌",
        angle=0,
        orb=8,
        weight=5,
        nature="neutral",
    ),
    "sextile": Aspect(
        key="sextile",
        name_vi="Lục Hợp",
        name_en="Sextile",
        symbol="⚹",
        angle=60,
        orb=6,
        weight=2,
        nature="harmonious",
    ),
    "square": Aspect(
        key="square",
        name_vi="Vuông Góc",
        name_en="Square",
        symbol="□",
        angle=90,
        orb=8,
        weight=3,
        nature="challenging",
    ),
    "trine": Aspect(
        key="trine",
        name_vi="Tam Hợp",
        name_en="Trine",
        symbol="△",
        angle=120,
        orb=8,
        weight=3,
        nature="harmonious",
    ),
    "opposition": Aspect(
        key="opposition",
        name_vi="Đối Xung",
        name_en="Opposition",
        symbol="☍",
        angle=180,
        orb=8,
        weight=4,
        nature="challenging",
    ),
    "quincunx": Aspect(
        key="quincunx",
        name_vi="Bát Xung",
        name_en="Quincunx",
        symbol="⚻",
        angle=150,
        orb=3,
        weight=1,
        nature="challenging",
    ),
    "semisextile": Aspect(
        key="semisextile",
        name_vi="Bán Lục Hợp",
        name_en="Semisextile",
        symbol="⚺",
        angle=30,
        orb=3,
        weight=1,
        nature="neutral",
    ),
    "semisquare": Aspect(
        key="semisquare",
        name_vi="Bán Vuông",
        name_en="Semisquare",
        symbol="∠",
        angle=45,
        orb=2,
        weight=1,
        nature="challenging",
    ),
    "sesquiquadrate": Aspect(
        key="sesquiquadrate",
        name_vi="Bán Vuông Kép",
        name_en="Sesquiquadrate",
        symbol="⚼",
        angle=135,
        orb=2,
        weight=1,
        nature="challenging",
    ),
    "quintile": Aspect(
        key="quintile",
        name_vi="Ngũ Hợp",
        name_en="Quintile",
        symbol="Q",
        angle=72,
        orb=2,
        weight=1,
        nature="neutral",
    ),
}


HOUSES: Dict[int, House] = {
    1: House(
        1,
        "Nhà 1",
        "1st House",
        "angular",
        3,
        ["bản thân", "ngoại hình", "cá tính", "khởi đầu"],
        ["self", "appearance", "personality", "beginnings"],
        "aries",
    ),
    2: House(
        2,
        "Nhà 2",
        "2nd House",
        "succedent",
        1,
        ["tài chính", "giá trị", "sở hữu", "thu nhập"],
        ["finances", "values", "possessions", "income"],
        "taurus",
    ),
    3: House(
        3,
        "Nhà 3",
        "3rd House",
        "cadent",
        -1,
        ["giao tiếp", "anh chị em", "học tập", "du lịch ngắn"],
        ["communication", "siblings", "learning", "short trips"],
        "gemini",
    ),
    4: House(
        4,
        "Nhà 4",
        "4th House",
        "angular",
        3,
        ["gia đình", "nhà cửa", "cội nguồn", "cảm xúc nền tảng"],
        ["family", "home", "roots", "emotional foundation"],
        "cancer",
    ),
    5: House(
        5,
        "Nhà 5",
        "5th House",
        "succedent",
        1,
        ["sáng tạo", "tình yêu", "giải trí", "con cái"],
        ["creativity", "romance", "entertainment", "children"],
        "leo",
    ),
    6: House(
        6,
        "Nhà 6",
        "6th House",
        "cadent",
        -1,
        ["công việc", "sức khỏe", "phục vụ", "thói quen hàng ngày"],
        ["work", "health", "service", "daily routine"],
        "virgo",
    ),
    7: House(
        7,
        "Nhà 7",
        "7th House",
        "angular",
        3,
        ["hôn nhân", "đối tác", "quan hệ", "hợp đồng"],
        ["marriage", "partnerships", "relationships", "contracts"],
        "libra",
    ),
    8: House(
        8,
        "Nhà 8",
        "8th House",
        "cadent",
        -1,
        ["chuyển hóa", "tài chính chung", "bí mật", "tâm lý sâu"],
        ["transformation", "joint finances", "secrets", "deep psychology"],
        "scorpio",
    ),
    9: House(
        9,
        "Nhà 9",
        "9th House",
        "cadent",
        -1,
        ["triết học", "du lịch xa", "giáo dục cao", "tâm linh"],
        ["philosophy", "long travel", "higher education", "spirituality"],
        "sagittarius",
    ),
    10: House(
        10,
        "Nhà 10",
        "10th House",
        "angular",
        3,
        ["sự nghiệp", "danh tiếng", "địa vị", "mục tiêu"],
        ["career", "reputation", "status", "goals"],
        "capricorn",
    ),
    11: House(
        11,
        "Nhà 11",
        "11th House",
        "succedent",
        1,
        ["bạn bè", "mạng lưới", "hy vọng", "lợi ích tập thể"],
        ["friends", "network", "hopes", "group benefits"],
        "aquarius",
    ),
    12: House(
        12,
        "Nhà 12",
        "12th House",
        "cadent",
        -1,
        ["tiềm thức", "ẩn dật", "tâm linh", "kẻ thù"],
        ["subconscious", "seclusion", "spirituality", "hidden enemies"],
        "pisces",
    ),
}


ELEMENT_WEIGHTS = {"fire": 3, "earth": 3, "air": 3, "water": 3}
QUALITY_WEIGHTS = {"cardinal": 3, "fixed": 3, "mutable": 3}
HOUSE_TYPE_WEIGHTS = {"angular": 3, "succedent": 1, "cadent": -1}


DIGNITY_SCORES = {
    "rulership": 5,
    "exaltation": 4,
    "triplicity": 3,
    "term": 2,
    "face": 1,
    "neutral": 0,
    "detriment": -4,
    "fall": -5,
}


PLANET_IN_SIGN_DIGNITY: Dict[str, Dict[str, Dict[str, Optional[int]]]] = {
    "sun": {
        "aries": {"rulership": None, "exaltation": 4, "detriment": None, "fall": None},
        "taurus": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "gemini": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "cancer": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "leo": {"rulership": 5, "exaltation": None, "detriment": None, "fall": None},
        "virgo": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "libra": {"rulership": None, "exaltation": None, "detriment": None, "fall": -5},
        "scorpio": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "sagittarius": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "capricorn": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "aquarius": {
            "rulership": None,
            "exaltation": None,
            "detriment": -4,
            "fall": None,
        },
        "pisces": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
    },
    "moon": {
        "aries": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "taurus": {"rulership": None, "exaltation": 4, "detriment": None, "fall": None},
        "gemini": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "cancer": {"rulership": 5, "exaltation": None, "detriment": None, "fall": None},
        "leo": {"rulership": None, "exaltation": None, "detriment": None, "fall": None},
        "virgo": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "libra": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "scorpio": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": -5,
        },
        "sagittarius": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "capricorn": {
            "rulership": None,
            "exaltation": None,
            "detriment": -4,
            "fall": None,
        },
        "aquarius": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "pisces": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
    },
    "mercury": {
        "aries": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "taurus": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "gemini": {"rulership": 5, "exaltation": None, "detriment": None, "fall": None},
        "cancer": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "leo": {"rulership": None, "exaltation": None, "detriment": None, "fall": None},
        "virgo": {"rulership": 5, "exaltation": 4, "detriment": None, "fall": None},
        "libra": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "scorpio": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "sagittarius": {
            "rulership": None,
            "exaltation": None,
            "detriment": -4,
            "fall": None,
        },
        "capricorn": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "aquarius": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "pisces": {"rulership": None, "exaltation": None, "detriment": -4, "fall": -5},
    },
    "venus": {
        "aries": {"rulership": None, "exaltation": None, "detriment": -4, "fall": None},
        "taurus": {"rulership": 5, "exaltation": None, "detriment": None, "fall": None},
        "gemini": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "cancer": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "leo": {"rulership": None, "exaltation": None, "detriment": None, "fall": None},
        "virgo": {"rulership": None, "exaltation": None, "detriment": None, "fall": -5},
        "libra": {"rulership": 5, "exaltation": None, "detriment": None, "fall": None},
        "scorpio": {
            "rulership": None,
            "exaltation": None,
            "detriment": -4,
            "fall": None,
        },
        "sagittarius": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "capricorn": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "aquarius": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "pisces": {"rulership": None, "exaltation": 4, "detriment": None, "fall": None},
    },
    "mars": {
        "aries": {"rulership": 5, "exaltation": None, "detriment": None, "fall": None},
        "taurus": {
            "rulership": None,
            "exaltation": None,
            "detriment": -4,
            "fall": None,
        },
        "gemini": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "cancer": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": -5,
        },
        "leo": {"rulership": None, "exaltation": None, "detriment": None, "fall": None},
        "virgo": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "libra": {"rulership": None, "exaltation": None, "detriment": -4, "fall": None},
        "scorpio": {
            "rulership": 5,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "sagittarius": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "capricorn": {
            "rulership": None,
            "exaltation": 4,
            "detriment": None,
            "fall": None,
        },
        "aquarius": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "pisces": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
    },
    "jupiter": {
        "aries": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "taurus": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "gemini": {
            "rulership": None,
            "exaltation": None,
            "detriment": -4,
            "fall": None,
        },
        "cancer": {"rulership": None, "exaltation": 4, "detriment": None, "fall": None},
        "leo": {"rulership": None, "exaltation": None, "detriment": None, "fall": None},
        "virgo": {"rulership": None, "exaltation": None, "detriment": -4, "fall": None},
        "libra": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "scorpio": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "sagittarius": {
            "rulership": 5,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "capricorn": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": -5,
        },
        "aquarius": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "pisces": {"rulership": 5, "exaltation": None, "detriment": None, "fall": None},
    },
    "saturn": {
        "aries": {"rulership": None, "exaltation": None, "detriment": None, "fall": -5},
        "taurus": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "gemini": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "cancer": {
            "rulership": None,
            "exaltation": None,
            "detriment": -4,
            "fall": None,
        },
        "leo": {"rulership": None, "exaltation": None, "detriment": -4, "fall": None},
        "virgo": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "libra": {"rulership": None, "exaltation": 4, "detriment": None, "fall": None},
        "scorpio": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "sagittarius": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "capricorn": {
            "rulership": 5,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "aquarius": {
            "rulership": 5,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
        "pisces": {
            "rulership": None,
            "exaltation": None,
            "detriment": None,
            "fall": None,
        },
    },
    "uranus": {
        "aquarius": {"rulership": 5},
        "scorpio": {"exaltation": 4},
        "taurus": {"fall": -5},
        "leo": {"detriment": -4},
    },
    "neptune": {
        "pisces": {"rulership": 5},
        "cancer": {"exaltation": 4},
        "capricorn": {"fall": -5},
        "virgo": {"detriment": -4},
    },
    "pluto": {
        "scorpio": {"rulership": 5},
        "taurus": {"detriment": -4},
    },
}


PLANET_ORDER = [
    "sun",
    "moon",
    "mercury",
    "venus",
    "mars",
    "jupiter",
    "saturn",
    "uranus",
    "neptune",
    "pluto",
    "chiron",
    "ceres",
    "pallas",
    "juno",
    "vesta",
    "lilith",
]
SIGN_ORDER = [
    "aries",
    "taurus",
    "gemini",
    "cancer",
    "leo",
    "virgo",
    "libra",
    "scorpio",
    "sagittarius",
    "capricorn",
    "aquarius",
    "pisces",
]
MAJOR_ASPECTS = ["conjunction", "sextile", "square", "trine", "opposition"]
ANGULAR_HOUSES = [1, 4, 7, 10]
SUCCEDENT_HOUSES = [2, 5, 8, 11]
CADENT_HOUSES = [3, 6, 9, 12]

ELEMENT_SIGNS = {
    "fire": ["aries", "leo", "sagittarius"],
    "earth": ["taurus", "virgo", "capricorn"],
    "air": ["gemini", "libra", "aquarius"],
    "water": ["cancer", "scorpio", "pisces"],
}

QUALITY_SIGNS = {
    "cardinal": ["aries", "cancer", "libra", "capricorn"],
    "fixed": ["taurus", "leo", "scorpio", "aquarius"],
    "mutable": ["gemini", "virgo", "sagittarius", "pisces"],
}

SIGN_RULERS = {s.key: s.ruler for s in SIGNS.values()}

SIGN_MODERN_RULERS = {
    "aries": "mars",
    "taurus": "venus",
    "gemini": "mercury",
    "cancer": "moon",
    "leo": "sun",
    "virgo": "mercury",
    "libra": "venus",
    "scorpio": "pluto",
    "sagittarius": "jupiter",
    "capricorn": "saturn",
    "aquarius": "uranus",
    "pisces": "neptune",
}

SIGN_NUMBERS = {s: i + 1 for i, s in enumerate(SIGN_ORDER)}
NUMBER_SIGNS = {i + 1: s for i, s in enumerate(SIGN_ORDER)}


def get_sign_by_degree(degree: float) -> str:
    idx = int(degree // 30) % 12
    return SIGN_ORDER[idx]


def get_position_in_sign(degree: float) -> float:
    return degree % 30


def calculate_aspect_angle(deg1: float, deg2: float) -> float:
    diff = abs(deg1 - deg2) % 360
    return min(diff, 360 - diff)


def get_element(sign_key: str) -> str:
    return SIGNS[sign_key].element


def get_quality(sign_key: str) -> str:
    return SIGNS[sign_key].quality


def get_polarity(sign_key: str) -> str:
    return SIGNS[sign_key].polarity


def get_ruler(sign_key: str) -> str:
    return SIGNS[sign_key].ruler


def get_dignity_score(planet_key: str, sign_key: str) -> int:
    dignities = PLANET_IN_SIGN_DIGNITY.get(planet_key, {}).get(sign_key, {})
    if not dignities:
        return 0
    for dtype, score in dignities.items():
        if score is not None:
            return score
    return 0


def get_dignity_label(planet_key: str, sign_key: str) -> str:
    dignities = PLANET_IN_SIGN_DIGNITY.get(planet_key, {}).get(sign_key, {})
    for dtype, score in dignities.items():
        if score is not None and score > 0:
            return dtype
        elif score is not None and score < 0:
            return dtype
    return "neutral"


def angular_distance(deg1: float, deg2: float) -> float:
    return min((deg1 - deg2) % 360, (deg2 - deg1) % 360)


def is_retrograde(speed: float) -> bool:
    return speed < 0


def sign_from_degree(degree: float) -> str:
    return SIGN_ORDER[int(degree // 30) % 12]
