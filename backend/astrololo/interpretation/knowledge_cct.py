"""
CCT Table of Contents → Astrololo mapping.

This file maps the public knowledge taxonomy from
https://www.choichiemtinh.net/bài-viết/mục-lục into Astrololo
interpretation categories, template sections, and KB fallback hints.

Integration points:
- `astrololo/interpretation/knowledge_base.py` uses this mapping to decide
  which corpus files or synthesized entries should be loaded.
- `astrololo/interpretation/keywords.py` can use `vi_keywords` as extra
  probabilistic cues when curated/baked templates are missing.
- The frontend `SECTION_TITLES`/`SECTION_COLORS` already cover the merged
  categories without adding new UI sections.
"""

CCT_TOC = [
    "101.001", "101.002", "101.003", "101.004", "101.005", "101.006", "101.007",
    "102", "102.001", "102.002", "102.003", "102.004",
    "103", "103.001",
    "104",
    "105",
    "110.001", "110.002", "110.003", "110.004", "110.005", "110.006", "110.007", "110.008",
    "111.001", "111.002", "111.003", "111.004", "111.005",
    "112.001", "112.002", "112.003", "112.004", "112.005", "112.006", "112.007",
    "114.001", "114.002", "114.003", "114.004", "114.005",
    "115.001", "115.010",
    "122.001", "123.001",
    "124.001", "124.002",
    "125.001", "125.002", "125.003",
    "126.001",
    "127.001", "127.002",
    "130.001", "130.002", "130.003",
    "131.001", "131.002", "131.003", "131.004",
    "135.001",
    "140.001", "140.002", "140.003", "140.004",
    "141.001",
    "143.001", "143.002", "143.003",
    "145.001", "145.002",
    "170.001",
    "171",
    "172.001", "172.002",
    "175.001",
    "180", "180.001", "180.002", "180.003",
    "190.001",
    "200.001", "200.002", "200.003",
    "202.001", "202.002", "202.003",
    "204.001",
    "210.001",
    "230", "230.001", "230.002",
    "247.001",
    "301.001", "301.002", "301.003",
    "302.001",
    "303.001",
    "305.001",
    "310.001",
    "315.001",
    "350.001",
    "401.001", "401.002", "401.003", "401.004",
    "420.001",
    "430.001",
    "501.001", "501.002", "501.003", "501.004",
    "510.001",
    "511.001", "511.002", "511.003",
    "521.001", "521.002",
    "531.001",
    "cct_principle_0001", "cct_principle_0002", "cct_principle_0003",
    "cct_principle_0004", "cct_principle_0005", "cct_principle_0006",
    "cct_principle_0007", "cct_principle_0008", "cct_principle_0009",
    "cct_principle_0010",
]

CCT_MAPPING = [
    {
        "topic_id": "101.001",
        "source_url": "https://cct.tips/cth101001",
        "cct_label": "Vấn đề \"Giờ Sinh\" trước và sau 1975",
        "astrololo_section": "ascendant",
        "astrololo_category": "Natal Basics",
        "vi_keywords": [
            "giờ sinh", "điểm mọc", "ascendant", "ora diem nascendi", "sơ đồ sinh"
        ],
        "en_keywords": ["birth time", "rising sign", "ascendant"],
        "priority": 1,
    },
    {
        "topic_id": "101.003",
        "source_url": "https://cct.tips/cth101003",
        "cct_label": "Tên Của Các \"Sao\"",
        "astrololo_section": "encyclopedia",
        "astrololo_category": "Reference",
        "vi_keywords": ["tên sao", "hành tinh", "tiểu hành tinh", "long thủ", "long vĩ"],
        "en_keywords": ["planet names", "asteroid names", "node names"],
        "priority": 1,
    },
    {
        "topic_id": "101.007",
        "source_url": "https://cct.tips/cth101007",
        "cct_label": "Các Hành Tinh Trên Trời Ảnh Hưởng Đến Chúng Ta Như Thế Nào",
        "astrololo_section": "encyclopedia",
        "astrololo_category": "Reference",
        "vi_keywords": [
            "hành tinh ảnh hưởng", "kim tinh", "thủy tinh", "hỏa tinh", "mộc tinh",
            "thổ tinh", "thiên vương", "hải vương", "diêm vương"
        ],
        "en_keywords": ["planetary influence", "traditional planets", "outer planets"],
        "priority": 1,
    },
    {
        "topic_id": "112.001",
        "source_url": "https://cct.tips/chutinh",
        "cct_label": "Chủ Tinh Của Các Dấu Hiệu Hoàng Đạo",
        "astrololo_section": "house_rulers",
        "astrololo_category": "Natal Basics",
        "vi_keywords": ["chủ tinh", "cung hoàng đạo", "cung mọc", "đương cư"],
        "en_keywords": ["sign ruler", "domicile ruler", "house ruler"],
        "priority": 1,
    },
    {
        "topic_id": "125.001",
        "source_url": "https://cct.tips/cth125001",
        "cct_label": "Hỏa Tinh Trong 12 Cung Nhà: Dũng Cảm và Sợ Hãi",
        "astrololo_section": "planet_in_house",
        "astrololo_category": "House Placement",
        "vi_keywords": ["hỏa tinh trong nhà", "hành động", "dũng cảm", "sợ hãi"],
        "en_keywords": ["mars in houses", "courage", "action", "fear"],
        "priority": 2,
    },
    {
        "topic_id": "127.001",
        "source_url": "https://cct.tips/cth127001",
        "cct_label": "Thổ Tinh: Nỗ Lực Và Rèn Luyện Trong Quá Trình Trưởng Thành",
        "astrololo_section": "planet_in_house",
        "astrololo_category": "House Placement",
        "vi_keywords": ["thổ tinh", "nỗ lực", "kỷ luật", "trưởng thành", "cấu trúc"],
        "en_keywords": ["saturn", "effort", "discipline", "maturity", "structure"],
        "priority": 2,
    },
    {
        "topic_id": "131.001",
        "source_url": "https://cct.tips/cth131001",
        "cct_label": "Chiron Hồi Vị",
        "astrololo_section": "encyclopedia",
        "astrololo_category": "Sensitive Points",
        "vi_keywords": ["chiron hồi vị", "chiron", "vết thương chữa lành"],
        "en_keywords": ["chiron return", "wounded healer", "chiron"],
        "priority": 2,
    },
    {
        "topic_id": "131.003",
        "source_url": "https://cct.tips/cth131003",
        "cct_label": "Cách hóa giải Chiron trong cung Nhà 7 hay 8...",
        "astrololo_section": "encyclopedia",
        "astrololo_category": "Sensitive Points",
        "vi_keywords": ["chiron trong nhà 7", "chiron trong nhà 8", "hóa giải chiron"],
        "en_keywords": ["chiron house 7", "chiron house 8", "chiron healing"],
        "priority": 2,
    },
    {
        "topic_id": "140.001",
        "source_url": "https://cct.tips/gocchieu",
        "cct_label": "Giải Mã Các Góc Chiếu Trong Lá Số",
        "astrololo_section": "aspects",
        "astrololo_category": "Aspects",
        "vi_keywords": ["góc chiếu", "hợp", "vuông góc", "tam hợp", "đối xung"],
        "en_keywords": ["aspects", "conjunction", "square", "trine", "opposition"],
        "priority": 1,
    },
    {
        "topic_id": "140.002",
        "source_url": "https://cct.tips/cth140002",
        "cct_label": "Các Mẫu Hình Cụm Sao Và Góc Chiếu Đặc Biệt",
        "astrololo_section": "patterns",
        "astrololo_category": "Patterns",
        "vi_keywords": ["cụm sao", "mẫu hình", "đặc biệt", "t-square", "grand cross"],
        "en_keywords": ["aspect patterns", "t-square", "grand cross", "stellium"],
        "priority": 1,
    },
    {
        "topic_id": "140.004",
        "source_url": "https://cct.tips/cth140004",
        "cct_label": "\"Ngón Tay của Chúa\" và vai trò của \"Yod\"",
        "astrololo_section": "patterns",
        "astrololo_category": "Patterns",
        "vi_keywords": ["yod", "ngón tay chúa", "quincunx", "mẫu yod"],
        "en_keywords": ["yod", "finger of god", "quincunx", "150 degree"],
        "priority": 1,
    },
    {
        "topic_id": "141.001",
        "source_url": "https://cct.tips/cth141001",
        "cct_label": "Các Loại Trùng Tụ \"Trong\", Trùng Tụ \"Ngoài\", Tình Trạng \"Bị Thiêu Đốt\" Combust",
        "astrololo_section": "aspects",
        "astrololo_category": "Aspects",
        "vi_keywords": ["trùng tụ trong", "trùng tụ ngoài", "thiêu đốt", "combust", "cazimi"],
        "en_keywords": ["stellium", "combustion", "cazimi", "under the beams"],
        "priority": 1,
    },
    {
        "topic_id": "143.001",
        "source_url": "https://cct.tips/cth143001",
        "cct_label": "Người Có Mặt Trăng Và Mặt Trời Đối Góc 180°",
        "astrololo_section": "aspects",
        "astrololo_category": "Aspects",
        "vi_keywords": ["mặt trăng đối góc mặt trời", "full moon personality", "180 độ"],
        "en_keywords": ["sun moon opposition", "full moon birth", "180 aspect"],
        "priority": 2,
    },
    {
        "topic_id": "114.003",
        "source_url": "https://cct.tips/n61Ak",
        "cct_label": "Loạt bài về tính chất Long Thủ / Long Vĩ",
        "astrololo_section": "encyclopedia",
        "astrololo_category": "Nodes",
        "vi_keywords": [
            "long thủ", "long vĩ", "la hầu", "kế đô", "north node", "south node",
            "đầu đuôi rồng", "tiền kiếp", "kiếp này"
        ],
        "en_keywords": ["north node", "south node", "rahu", "ketu", "dragon head", "dragon tail"],
        "priority": 1,
    },
    {
        "topic_id": "115.001",
        "source_url": "https://cct.tips/lilith",
        "cct_label": "Lilith trong Chiêm Tinh Học",
        "astrololo_section": "encyclopedia",
        "astrololo_category": "Sensitive Points",
        "vi_keywords": ["lilith", "hắc nguyệt", "bóng tối", "độc lập", "nam tính"],
        "en_keywords": ["black moon lilith", "lilith", "dark moon", "independence"],
        "priority": 1,
    },
    {
        "topic_id": "175.001",
        "source_url": "https://cct.tips/cth175001",
        "cct_label": "3 Loại Nghiệp Quả Của Đời Người",
        "astrololo_section": "karmic_psych",
        "astrololo_category": "Karma",
        "vi_keywords": ["nghiệp quả", "kiếp trước", "nghiệp chướng", "3 loại nghiệp"],
        "en_keywords": ["karma", "past life", "karmic Debt", "3 types karma"],
        "priority": 2,
    },
    {
        "topic_id": "180",
        "source_url": "https://cct.tips/cth180",
        "cct_label": "Nhận Biết Khả Năng Tâm Linh Qua Một Lá Số",
        "astrololo_section": "karmic_psych",
        "astrololo_category": "Karma",
        "vi_keywords": ["tâm linh", "khả năng tâm linh", "nhận biết tâm linh"],
        "en_keywords": ["spirituality", "psychic ability", "spiritual sensitivity"],
        "priority": 2,
    },
    {
        "topic_id": "180.001",
        "source_url": "https://cct.tips/cth180001",
        "cct_label": "Cách Nhận Biết Nguyên Nhân \"Chết\" Trên Lá Số",
        "astrololo_section": "karmic_psych",
        "astrololo_category": "Karma",
        "vi_keywords": ["nguyên nhân chết", "tử vong", "sức khỏe", "kiếp sống"],
        "en_keywords": ["death", "longevity", "health", "8th house"],
        "priority": 2,
    },
    {
        "topic_id": "180.002",
        "source_url": "https://cct.tips/cth180002",
        "cct_label": "Số Đi Tu được hay không ?",
        "astrololo_section": "karmic_psych",
        "astrololo_category": "Karma",
        "vi_keywords": ["đi tu", "xuất gia", "số xuất gia", "tâm linh"],
        "en_keywords": ["monastic life", "spiritual vocation", "renunciation"],
        "priority": 2,
    },
    {
        "topic_id": "301.001",
        "source_url": "https://cct.tips/cth301001",
        "cct_label": "Nhận Diện Kẻ Lừa Dối & Giả Hình Trong Quan Hệ Tình Cảm",
        "astrololo_section": "synastry",
        "astrololo_category": "Relationships",
        "vi_keywords": ["lừa dối", "giả hình", "quan hệ tình cảm", "không chân thành"],
        "en_keywords": ["deception", "untrustworthy", "relationship red flags"],
        "priority": 2,
    },
    {
        "topic_id": "301.003",
        "source_url": "https://cct.tips/cth301003",
        "cct_label": "Cách Tìm Người Yêu / Bạn Đời Trên Một Lá Số",
        "astrololo_section": "synastry",
        "astrololo_category": "Relationships",
        "vi_keywords": ["người yêu", "bạn đời", "hôn nhân", "quan hệ đối tác"],
        "en_keywords": ["partner", "spouse", "marriage", "relationship indicators"],
        "priority": 2,
    },
    {
        "topic_id": "302.001",
        "source_url": "https://cct.tips/cth302001",
        "cct_label": "Mặt Trăng Trong Quan Hệ Tình Cảm",
        "astrololo_section": "synastry",
        "astrololo_category": "Relationships",
        "vi_keywords": ["mặt trăng trong quan hệ", "cảm xúc", "an toàn", "gắn bó"],
        "en_keywords": ["moon in relationships", "emotional needs", "attachment"],
        "priority": 2,
    },
    {
        "topic_id": "303.001",
        "source_url": "https://cct.tips/cth303001",
        "cct_label": "Vị Trí Kim Tinh và Mong Muốn Trong Tình Yêu",
        "astrololo_section": "synastry",
        "astrololo_category": "Relationships",
        "vi_keywords": ["kim tinh trong tình yêu", "mong muốn", "sắc đẹp", "yêu thương"],
        "en_keywords": ["venus love", "desire", "attraction", "relationship values"],
        "priority": 2,
    },
    {
        "topic_id": "350.001",
        "source_url": "https://cct.tips/cth350001",
        "cct_label": "Cách Nhận Diện \"Minh Sư\"",
        "astrololo_section": "karmic_psych",
        "astrololo_category": "Karma",
        "vi_keywords": ["minh sư", "người dẫn đường", "thầy", "duyên nợ"],
        "en_keywords": ["spiritual guide", "mentor", "karmic connection"],
        "priority": 3,
    },
    {
        "topic_id": "501.001",
        "source_url": "https://cct.tips/cth501001",
        "cct_label": "Cách Nhận Diện \"Chiêm Tinh Gia\" vs. \"Thầy Bói\"",
        "astrololo_section": "encyclopedia",
        "astrololo_category": "Reference",
        "vi_keywords": ["chiêm tinh gia", "thầy bói", "bói toán", "khác biệt"],
        "en_keywords": ["astrologer", "fortune teller", "divination"],
        "priority": 3,
    },
]
"""
CCT topic mapping from choichiemtinh.net table of contents into Astrololo sections.
"""


def topic_ids() -> list[str]:
    return [item["topic_id"] for item in CCT_MAPPING]


def mapping_for_section(section: str) -> list[dict]:
    return [item for item in CCT_MAPPING if item["astrololo_section"] == section]


def mapping_for_category(category: str) -> list[dict]:
    return [item for item in CCT_MAPPING if item["astrololo_category"] == category]


def high_priority_mapping(limit: int = 20) -> list[dict]:
    ordered = sorted(CCT_MAPPING, key=lambda item: item.get("priority", 99))
    return ordered[:limit]
