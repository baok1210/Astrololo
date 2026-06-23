"""Chart-aware synthesis — weave sign, house, dignity, and aspects into narratives."""
from typing import Optional, List, Dict, Any

from astrololo.core.constants import PLANETS, SIGNS, SIGN_RULERS, get_dignity_label
from astrololo.interpretation.keywords import (
    get_planet_function,
    get_sign_keywords,
    get_sign_short_description,
    get_house_keywords,
    HOUSE_NAME_VI,
)
from astrololo.interpretation.knowledge_base import get_3ntk_keywords, is_kb_available
from astrololo.models.chart import ChartData, AspectData

_PERSONAL = frozenset({"sun", "moon", "mercury", "venus", "mars"})
_PLACEHOLDER_PHRASES = (
    "sự kết hợp đặc biệt mang ý nghĩa quan trọng",
    "significant combination in the chart",
    "a significant combination",
)

_DIGNITY_VI = {
    "rulership": "quản gia — rất mạnh",
    "exaltation": "cao quý — mạnh",
    "detriment": "suy giảm — yếu",
    "fall": "sa sút — rất yếu",
    "neutral": "trung bình",
}
_DIGNITY_EN = {
    "rulership": "domicile — very strong",
    "exaltation": "exalted — strong",
    "detriment": "detriment — weak",
    "fall": "fall — very weak",
    "neutral": "neutral",
}


def is_placeholder_combination(entry: Optional[Dict[str, Any]]) -> bool:
    if not entry:
        return True
    text = (entry.get("text") or entry.get("detailed") or "").lower()
    return any(p in text for p in _PLACEHOLDER_PHRASES)


def _body(chart: ChartData, name: str):
    return next((b for b in chart.planets if b.name == name), None)


def _planet_display(pbody, lang: str) -> str:
    if lang == "vi":
        return pbody.name_vi or pbody.name
    return pbody.name_en or pbody.name


def _sign_display(pbody, lang: str) -> str:
    if lang == "vi":
        return pbody.sign_name_vi or pbody.sign
    return pbody.sign_name_en or pbody.sign


def _dignity_text(planet: str, sign: str, lang: str) -> str:
    label = get_dignity_label(planet, sign)
    mapping = _DIGNITY_VI if lang == "vi" else _DIGNITY_EN
    return mapping.get(label, label)


def _chart_roles(chart: ChartData, planet_name: str, lang: str) -> List[str]:
    roles: List[str] = []
    asc = chart.ascendant_sign or ""
    mc = chart.mc_sign or ""
    if SIGN_RULERS.get(asc) == planet_name:
        roles.append("chủ tinh Cung Mọc" if lang == "vi" else "Ascendant ruler")
    if SIGN_RULERS.get(mc) == planet_name:
        roles.append("chủ tinh MC" if lang == "vi" else "MC ruler")
    for anchor, label_vi, label_en in (
        ("sun", "chủ tinh cung Mặt Trời", "Sun sign ruler"),
        ("moon", "chủ tinh cung Mặt Trăng", "Moon sign ruler"),
    ):
        body = _body(chart, anchor)
        if body and SIGN_RULERS.get(body.sign) == planet_name:
            roles.append(label_vi if lang == "vi" else label_en)
    return roles


def _aspect_links_for_planet(
    chart: ChartData, planet_name: str, lang: str, limit: int = 3
) -> List[str]:
    scored: List[tuple] = []
    for a in chart.aspects:
        if a.planet1 != planet_name and a.planet2 != planet_name:
            continue
        other = a.planet2 if a.planet1 == planet_name else a.planet1
        ob = _body(chart, other)
        if not ob:
            continue
        priority = 0
        if other in _PERSONAL:
            priority += 10
        if other in ("jupiter", "saturn"):
            priority += 5
        priority += max(0, 6 - int(a.orb))
        if a.nature == "challenging":
            priority += 2
        scored.append((priority, a, other, ob))

    scored.sort(key=lambda x: x[0], reverse=True)
    lines: List[str] = []
    for _, a, other, ob in scored[:limit]:
        a_name = a.aspect_name_vi if lang == "vi" else (
            a.aspect_type.replace("_", " ").title()
        )
        if lang == "vi":
            lines.append(
                f"{a_name} {_planet_display(ob, lang)} "
                f"({_sign_display(ob, lang)}, Nhà {ob.house}, orb {a.orb:.1f}°)"
            )
        else:
            lines.append(
                f"{a_name} {_planet_display(ob, lang)} "
                f"({_sign_display(ob, lang)}, House {ob.house}, orb {a.orb:.1f}°)"
            )
    return lines


def enrich_aspect_with_chart(
    chart: ChartData,
    aspect: AspectData,
    base_text: str,
    lang: str = "vi",
) -> str:
    p1 = _body(chart, aspect.planet1)
    p2 = _body(chart, aspect.planet2)
    if not p1 or not p2:
        return base_text

    ctx_lines: List[str] = []
    for pbody, pname in ((p1, aspect.planet1), (p2, aspect.planet2)):
        roles = _chart_roles(chart, pname, lang)
        role_str = f" ({', '.join(roles)})" if roles else ""
        dignity = _dignity_text(pname, pbody.sign, lang)
        if lang == "vi":
            ctx_lines.append(
                f"• {_planet_display(pbody, lang)} ở {_sign_display(pbody, lang)} "
                f"Nhà {pbody.house} ({dignity}){role_str}"
            )
        else:
            ctx_lines.append(
                f"• {_planet_display(pbody, lang)} in {_sign_display(pbody, lang)} "
                f"House {pbody.house} ({dignity}){role_str}"
            )

    h1_data = get_house_keywords(p1.house)
    h2_data = get_house_keywords(p2.house)
    if lang == "vi":
        h1_title = h1_data.get("title", f"Nhà {p1.house}")
        h2_title = h2_data.get("title", f"Nhà {p2.house}")
        h1_desc = (h1_data.get("description") or "")[:100]
        h2_desc = (h2_data.get("description") or "")[:100]
        activation = (
            f"Góc chiếu này kết nối {h1_title} với {h2_title}"
            + (f": {h1_desc} ↔ {h2_desc}." if h1_desc and h2_desc else ".")
        )
    else:
        h1_title = f"House {p1.house}"
        h2_title = f"House {p2.house}"
        h1_desc = (h1_data.get("description") or "")[:100]
        h2_desc = (h2_data.get("description") or "")[:100]
        activation = (
            f"This aspect links {h1_title} with {h2_title}"
            + (f": {h1_desc} ↔ {h2_desc}." if h1_desc and h2_desc else ".")
        )

    if aspect.nature == "challenging":
        if lang == "vi":
            conclusion = (
                "Kết luận: Trong bối cảnh lá số này, góc chiếu tạo căng thẳng sáng tạo — "
                "hai lĩnh vực trên cần được cân bằng thay vì chọn một bên."
            )
        else:
            conclusion = (
                "Conclusion: In this chart context, the aspect creates productive tension — "
                "both life areas need integration rather than choosing one side."
            )
    elif aspect.nature == "harmonious":
        if lang == "vi":
            conclusion = (
                "Kết luận: Năng lượng hai sao hỗ trợ nhau tự nhiên; "
                "hãy chủ động khai thác sự hài hòa này trong cả hai lĩnh vực nhà liên quan."
            )
        else:
            conclusion = (
                "Conclusion: These planets support each other naturally; "
                "actively use this harmony across both related house themes."
            )
    else:
        if lang == "vi":
            conclusion = (
                "Kết luận: Góc chiếu này hòa trộn hai chức năng thành một năng lượng thống nhất — "
                "cần nhận diện cả hai mặt biểu hiện trong đời sống hàng ngày."
            )
        else:
            conclusion = (
                "Conclusion: This aspect blends both functions into one unified drive — "
                "notice both expressions in daily life."
            )

    parts = [base_text.rstrip()] if base_text.strip() else []
    header = "Trong lá số của bạn:" if lang == "vi" else "In your chart:"
    parts.append(f"{header}\n" + "\n".join(ctx_lines))

    if aspect.orb < 3:
        orb_note = (
            "Góc chiếu rất chặt (orb < 3°) — tác động mạnh và khó bỏ qua."
            if lang == "vi"
            else "Tight aspect (orb < 3°) — strong influence, hard to ignore."
        )
        parts.append(orb_note)

    parts.extend([activation, conclusion])
    return "\n\n".join(parts)


def make_combination_synthesis(
    planet: str,
    sign: str,
    house: int,
    chart: Optional[ChartData] = None,
    lang: str = "vi",
) -> Dict[str, Any]:
    p = PLANETS.get(planet)
    s = SIGNS.get(sign)
    h_data = get_house_keywords(house)

    if lang == "vi":
        p_name = p.name_vi if p else planet
        s_name = s.name_vi if s else sign
        h_label = HOUSE_NAME_VI.get(house, f"Nhà {house}")
        h_title = h_data.get("title", h_label)
    else:
        p_name = p.name_en if p else planet
        s_name = s.name_en if s else sign
        h_label = f"House {house}"
        h_title = h_data.get("title", h_label)

    func = get_planet_function(planet) or ""
    if lang == "en" and p and p.keywords_en:
        func_short = p.keywords_en[0] + "."
    else:
        func_short = func.split(".")[0] + "." if func else ""
    sign_data = get_sign_keywords(sign) or {}
    sign_short = get_sign_short_description(sign) or ""
    core_kw = "; ".join(sign_data.get("core", [])[:3])
    pos_kw = "; ".join(sign_data.get("positive", [])[:3])
    h_desc = h_data.get("description", "")
    h_kw = "; ".join(h_data.get("keywords", [])[:4])
    dignity = _dignity_text(planet, sign, lang)

    kb_block = ""
    if is_kb_available():
        ntk = get_3ntk_keywords(planet, sign, house)
        if ntk:
            chunks = []
            for field, prefix_vi, prefix_en in (
                ("function", "Chức năng sâu", "Deep function"),
                ("sign_keywords", "Cung", "Sign"),
                ("house_keywords", "Nhà", "House"),
            ):
                items = ntk.get(field, [])
                if items:
                    preview = "; ".join(
                        str(x).replace("**", "").strip()[:120] for x in items[:2]
                    )
                    prefix = prefix_vi if lang == "vi" else prefix_en
                    chunks.append(f"{prefix}: {preview}")
            if chunks:
                kb_block = "\n".join(chunks)

    aspect_block = ""
    if chart:
        links = _aspect_links_for_planet(chart, planet, lang)
        if links:
            if lang == "vi":
                aspect_block = "Kết nối góc chiếu: " + "; ".join(links) + "."
            else:
                aspect_block = "Aspect links: " + "; ".join(links) + "."

    roles_block = ""
    if chart:
        pbody = _body(chart, planet)
        if pbody:
            roles = _chart_roles(chart, planet, lang)
            if roles:
                if lang == "vi":
                    roles_block = f"Vai trò trong lá số: {', '.join(roles)}."
                else:
                    roles_block = f"Chart roles: {', '.join(roles)}."

    if lang == "vi":
        title = f"{p_name} {s_name} — {h_title}"
        parts = [
            (
                f"{p_name} ở {s_name} tại {h_title} ({dignity}) tạo thành một trục ý nghĩa "
                f"trong lá số — không chỉ là vị trí riêng lẻ mà là cách năng lượng này vận hành trong đời bạn."
            ),
            f"Chức năng: {func_short}" if func_short else "",
            (
                f"Cách thể hiện: ở cung {s_name}, {sign_short or 'năng lượng cung này'} "
                + (f"— từ khóa: {core_kw}." if core_kw else ".")
            ),
            (
                f"Lĩnh vực đời: {h_desc or h_title}"
                + (f" — {h_kw}." if h_kw else ".")
            ),
            f"Điểm mạnh tiềm năng: {pos_kw}." if pos_kw else "",
            roles_block,
            kb_block,
            aspect_block,
            (
                f"Tổng hợp: Vì {p_name} đại diện {func_short or 'một chức năng tâm lý cốt lõi'}, "
                f"khi đặt ở {s_name} trong {h_title}, bạn thường thể hiện điều này qua "
                f"{h_desc.split('.')[0].lower() if h_desc else h_title.lower()} — "
                f"đây là nơi cần quan sát hành vi thực tế để hiểu lá số."
            ),
        ]
    else:
        title = f"{p_name} in {s_name} — {h_title}"
        parts = [
            (
                f"{p_name} in {s_name} in {h_title} ({dignity}) forms a meaningful axis "
                f"in the chart — not an isolated placement but how this energy runs through your life."
            ),
            f"Function: {func_short}" if func_short else "",
            (
                f"Expression: in {s_name}, {sign_short or 'this sign colors the planet'}"
                + (f" — keywords: {core_kw}." if core_kw else ".")
            ),
            (
                f"Life area: {h_desc or h_title}"
                + (f" — {h_kw}." if h_kw else ".")
            ),
            f"Potential strengths: {pos_kw}." if pos_kw else "",
            roles_block,
            kb_block,
            aspect_block,
            (
                f"Synthesis: Because {p_name} represents {func_short or 'a core psychological function'}, "
                f"in {s_name} in {h_title}, you typically express this through "
                f"{h_desc.split('.')[0].lower() if h_desc else h_title.lower()} — "
                f"watch real behavior here to understand the chart."
            ),
        ]

    text = "\n\n".join(p for p in parts if p)
    return {"title": title, "text": text, "title_en": title, "text_en": text}
