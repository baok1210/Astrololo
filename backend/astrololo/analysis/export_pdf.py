"""PDF Export — generates downloadable report from chart data."""
from io import BytesIO

from astrololo.models.chart import ChartData
from astrololo.models.subject import AstrologicalSubject
from astrololo.analysis.natal import create_natal_chart


def _build_report_text(chart: ChartData, lang: str = "vi") -> str:
    """Build plain text report from chart interpretation data."""
    lines = []
    interp = chart.interpretation or {}
    sections = interp.get("sections", [])
    summary = interp.get("chart_summary", {})

    lines.append("=" * 60)
    if lang == "vi":
        lines.append(f"BÁO CÁO CHIÊM TINH: {summary.get('name', '')}")
        lines.append(f"Cung Mọc: {summary.get('ascendant_sign', '')}")
        lines.append(f"Thiên Đỉnh: {summary.get('mc_sign', '')}")
        lines.append(f"Hệ thống Nhà: {summary.get('house_system', '')}")
    else:
        lines.append(f"ASTROLOGY REPORT: {summary.get('name', '')}")
        lines.append(f"Ascendant: {summary.get('ascendant_sign', '')}")
        lines.append(f"Midheaven: {summary.get('mc_sign', '')}")
        lines.append(f"House System: {summary.get('house_system', '')}")
    lines.append("=" * 60)
    lines.append("")

    overall = interp.get("overall_interpretation", "")
    if overall:
        lines.append(overall)
        lines.append("")

    for section in sections:
        title = section.get("title", "")
        items = section.get("items", [])

        if not items:
            continue

        lines.append(f"--- {title} ---")
        lines.append("")

        for item in items[:10]:
            t = item.get("title", "")
            text = item.get("text", "")
            if t:
                lines.append(t)
            if text:
                lines.append(text)
                lines.append("")

        lines.append("")

    return "\n".join(lines)


def _add_text_page(pdf, text: str, title: str):
    """Add a page of text to the PDF with proper wrapping."""
    from fpdf import FPDF
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    if isinstance(pdf, FPDF):
        pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)
        pdf.set_font("Helvetica", "", 10)

        for para in text.split("\n"):
            para_clean = para.strip()
            if not para_clean:
                pdf.ln(4)
                continue
            try:
                pdf.multi_cell(0, 5, para_clean)
            except Exception:
                pdf.multi_cell(0, 5, para_clean.encode("ascii", "replace").decode("ascii"))


def generate_pdf_report(chart: ChartData, lang: str = "vi") -> bytes:
    """Generate a multi-page PDF report from chart interpretation data."""
    from fpdf import FPDF

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)

    interp = chart.interpretation or {}
    sections = interp.get("sections", [])
    summary = interp.get("chart_summary", {})

    # Cover page
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 24)
    if lang == "vi":
        pdf.cell(0, 20, "Bao Cao Chiem Tinh", new_x="LMARGIN", new_y="NEXT", align="C")
    else:
        pdf.cell(0, 20, "Astrology Report", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(10)

    pdf.set_font("Helvetica", "", 14)
    pdf.cell(0, 10, f"Name: {summary.get('name', '')}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, f"Ascendant: {summary.get('ascendant_sign', '')}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, f"Midheaven: {summary.get('mc_sign', '')}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, f"Chart type: {summary.get('type', '')}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, f"House System: {summary.get('house_system', '')}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, f"Planets: {summary.get('planet_count', 0)}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, f"Aspects: {summary.get('aspect_count', 0)}", new_x="LMARGIN", new_y="NEXT")

    # Planet positions table
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Planet Positions", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 9)
    col_w = [35, 30, 30, 20, 15]
    headers = ["Planet", "Sign", "Position", "House", "Retro"]
    for h, w in zip(headers, col_w):
        pdf.cell(w, 7, h, border=1)
    pdf.ln()

    pdf.set_font("Helvetica", "", 9)
    for p in chart.planets:
        if p.body_type != "planet":
            continue
        p_name = p.name_vi if lang == "vi" else p.name_en
        s_name = p.sign_name_vi if lang == "vi" else p.sign_name_en
        pos = f"{p.position_in_sign:.1f}°"
        hse = str(p.house) if p.house else "-"
        retro = "R" if p.is_retrograde else ""
        vals = [p_name, s_name, pos, hse, retro]
        for v, w in zip(vals, col_w):
            pdf.cell(w, 6, v, border=1)
        pdf.ln()

    # Overall interpretation
    overall = interp.get("overall_interpretation", "")
    if overall:
        _add_text_page(pdf, overall, "Overview" if lang == "en" else "Tong Quan")

    # Each section
    for section in sections:
        title = section.get("title", "")
        items = section.get("items", [])

        if not items:
            continue

        section_text = ""
        for item in items[:10]:
            t = item.get("title", "")
            text = item.get("text", "")
            if t:
                section_text += t + "\n"
            if text:
                section_text += text + "\n\n"

        if section_text.strip():
            _add_text_page(pdf, section_text.strip(), title)

    output = BytesIO()
    pdf.output(output)
    return output.getvalue()


def create_pdf_export(natal_subject: AstrologicalSubject, lang: str = "vi",
                      house_system: str = "placidus", node_type: str = "mean",
                      esoteric: bool = True) -> bytes:
    chart = create_natal_chart(natal_subject, house_system, node_type, lang, esoteric)
    return generate_pdf_report(chart, lang)