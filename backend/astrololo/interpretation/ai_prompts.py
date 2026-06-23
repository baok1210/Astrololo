"""AI-powered interpretation prompts for Astrololo."""


SYSTEM_PROMPT_VI = """Bạn là chuyên gia chiêm tinh học (astrologer) cao cấp, tên Astrololo. 
Nhiệm vụ: luận giải lá số chiêm tinh dựa trên dữ liệu có cấu trúc được cung cấp.

Nguyên tắc:
1. Luận giải CHÍNH XÁC dựa trên dữ liệu, không bịa đặt vị trí hành tinh.
2. Phân tích thế sao (planetary configurations): chủ tinh (dispositor), các góc chiếu (aspects), pattern đặc biệt, nguyên tố, phẩm chất.
3. Viết bằng tiếng Việt tự nhiên, mạch lạc, có chiều sâu.
4. Kết hợp phân tích kỹ thuật (technical) với lời khuyên thực tế.
5. Độ dài: 300-800 từ, chia thành các đoạn ngắn.
6. Tập trung vào: điểm mạnh, thách thức, xu hướng cuộc đời, mối quan hệ, sự nghiệp.
7. KHÔNG đưa ra dự đoán cụ thể về thời gian (ngày tháng năm).
8. KHÔNG nói về cái chết, bệnh hiểm nghèo, hoặc các chủ đề nhạy cảm.
"""

SYSTEM_PROMPT_EN = """You are Astrololo, a senior astrologer.
Your task: interpret natal chart data with precision and depth.

Rules:
1. Base all analysis on the provided data. Do NOT fabricate planet positions.
2. Analyze planetary configurations: dispositor chains, aspects, patterns, elements, qualities.
3. Write in natural English, well-structured, with depth.
4. Combine technical analysis with practical guidance.
5. Length: 200-500 words, divided into short paragraphs.
6. Focus on: strengths, challenges, life trends, relationships, career.
7. Do NOT give specific time predictions (dates).
8. Do NOT discuss death, terminal illness, or sensitive topics.
"""


def _format_element_distribution(ed: dict) -> str:
    if not ed:
        return "N/A"
    return f"Lửa/Fire={ed.get('fire',0)}, Đất/Earth={ed.get('earth',0)}, Khí/Air={ed.get('air',0)}, Nước/Water={ed.get('water',0)} (ưu thế/Dominant: {ed.get('dominant','?')})"


def _format_aspects(aspects: list) -> str:
    lines = []
    for a in aspects[:15]:
        lines.append(f"  - {a.get('planet1','?')} {a.get('aspect_type','?')} {a.get('planet2','?')} (angle={a.get('angle',0):.1f}°, orb={a.get('orb',0):.2f}°)")
    return "\n".join(lines)


def _format_planets(planets: list) -> str:
    lines = []
    for p in planets:
        house = p.get("house", "?")
        sign = p.get("sign", "?")
        retro = " (R)" if p.get("is_retrograde") else ""
        lines.append(f"  - {p.get('name','?')} in {sign} Nhà/House {house}{retro} [{p.get('position_in_sign',0):.1f}°]")
    return "\n".join(lines)


def build_chart_context(chart_data: dict) -> str:
    summary = chart_data.get("chart_summary", {})
    planets = chart_data.get("planet_interpretations", [])
    aspects = chart_data.get("aspect_interpretations", [])
    ed = chart_data.get("element_distributions", [{}])
    patterns = chart_data.get("pattern_interpretations", [])

    ctx = f"""=== DỮ LIỆU LÁ SỐ / CHART DATA ===

Thông tin / Info:
- Tên/Name: {summary.get('name','?')}
- Cung Mọc/Ascendant: {summary.get('ascendant_sign','?')} ({summary.get('ascendant','?')})
- Thiên Đỉnh/MC: {summary.get('mc_sign','?')} ({summary.get('mc','?')})
- Giờ/Daytime: {'Ngày/Day' if summary.get('is_daytime') else 'Đêm/Night'}
- Hệ thống nhà/House System: {summary.get('house_system','?')}
- Số hành tinh/Planets: {summary.get('planet_count',0)}
- Số góc chiếu/Aspects: {summary.get('aspect_count',0)}

Phân bố nguyên tố / Element Distribution: {_format_element_distribution(ed[0] if ed else {})}

Hành tinh trong cung và nhà / Planets in Signs & Houses:
{_format_planets(planets)}

Các góc chiếu chính / Major Aspects:
{_format_aspects(aspects)}
"""
    if patterns:
        ctx += "\nCấu hình đặc biệt / Special Patterns:\n"
        for pat in patterns[:3]:
            ctx += f"  - {pat}\n"

    return ctx


CHART_ANALYSIS_PROMPT_VI = """Dựa trên dữ liệu lá số sau đây, hãy luận giải chi tiết bằng tiếng Việt. 
Phân tích các khía cạnh: tính cách, điểm mạnh, thách thức, sự nghiệp, mối quan hệ, và xu hướng phát triển.

{chart_context}

Hãy viết luận giải tự nhiên, sâu sắc, có cấu trúc rõ ràng."""


CHART_ANALYSIS_PROMPT_EN = """Based on the following chart data, provide a detailed interpretation in English.
Analyze: personality, strengths, challenges, career, relationships, and growth trends.

{chart_context}

Write naturally, with depth and clear structure."""
