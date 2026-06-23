import os
import re
from typing import Dict, List, Optional

_KB_PATH = None
_SIGN_SYNTHESIS: Dict[str, dict] = {}
_PLANET_SYNTHESIS: Dict[str, dict] = {}
_THREE_CROSSES: str = ""
_NTK_KEYWORDS: Dict[str, Dict[str, List[str]]] = {}
_loaded = False


def _find_kb_path() -> Optional[str]:
    env = os.environ.get("ASTRO_KNOWLEDGE_BASE", "")
    if env and os.path.isdir(env):
        return env
    candidates = [
        r"C:\Users\Admin\Downloads\Chiêm tinh kiến thức",
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "Chiêm tinh kiến thức"),
    ]
    for c in candidates:
        p = os.path.abspath(c)
        if os.path.isdir(p) and os.path.isdir(os.path.join(p, "_synthesis")):
            return p
    return None


def _load_all():
    global _loaded, _KB_PATH, _SIGN_SYNTHESIS, _THREE_CROSSES, _PLANET_SYNTHESIS, _NTK_KEYWORDS
    if _loaded:
        return
    _KB_PATH = _find_kb_path()
    if _KB_PATH:
        _load_synthesis_files()
        _load_3ntk()
    _loaded = True


def _load_synthesis_files():
    syn_dir = os.path.join(_KB_PATH, "_synthesis")
    if not os.path.isdir(syn_dir):
        return

    sign_map = [
        ("Bach_Duong_Aries.md", "aries"),
        ("Kim_Nguu_Taurus.md", "taurus"),
        ("Song_Tu_Gemini.md", "gemini"),
        ("Cu_Giai_Cancer.md", "cancer"),
        ("Su_Tu_Leo.md", "leo"),
        ("Xu_Nu_Virgo.md", "virgo"),
        ("Thien_Binh_Libra.md", "libra"),
        ("Bo_Cap_Scorpio.md", "scorpio"),
        ("Nhan_Ma_Sagittarius.md", "sagittarius"),
        ("Ma_Ket_Capricorn.md", "capricorn"),
        ("Bao_Binh_Aquarius.md", "aquarius"),
        ("Song_Ngu_Pisces.md", "pisces"),
    ]

    for filename, sign_key in sign_map:
        fp = os.path.join(syn_dir, filename)
        if os.path.isfile(fp):
            with open(fp, "r", encoding="utf-8") as f:
                text = f.read()
            parsed = _parse_sign_synthesis(text)
            if parsed:
                _SIGN_SYNTHESIS[sign_key] = parsed

    cross_fp = os.path.join(syn_dir, "Ba_Thap_Gia.md")
    if os.path.isfile(cross_fp):
        with open(cross_fp, "r", encoding="utf-8") as f:
            _THREE_CROSSES = f.read()

    planet_fp = os.path.join(syn_dir, "Hanh_Tinh.md")
    if os.path.isfile(planet_fp):
        with open(planet_fp, "r", encoding="utf-8") as f:
            text = f.read()
        _PLANET_SYNTHESIS = _parse_planet_synthesis(text)

    overview_fp = os.path.join(syn_dir, "12_Cung_Hoang_Dao.md")
    if os.path.isfile(overview_fp):
        with open(overview_fp, "r", encoding="utf-8") as f:
            for row in _parse_overview_table(f.read()):
                sign_key = row.get("sign_key", "").lower()
                if sign_key in _SIGN_SYNTHESIS:
                    _SIGN_SYNTHESIS[sign_key].update({
                        "element": row.get("element", ""),
                        "mode": row.get("mode", ""),
                        "cross": row.get("cross", ""),
                    })


def _parse_sign_synthesis(text: str) -> Optional[dict]:
    result = {}
    current_source = None
    lines = text.split("\n")

    for line in lines:
        hl = line.strip()
        is_heading = hl.startswith("#") and not hl.startswith("# ")
        if is_heading:
            lower = hl.lower()
            if "cthnm" in lower or "nội môn" in lower:
                current_source = "cthnm"
                result["cthnm"] = ""
            elif "cthud" in lower or "ứng dụng" in lower:
                current_source = "cthud"
                result["cthud"] = ""
            elif "3ntk" in lower or "3 nhóm" in lower or "từ khóa" in lower:
                current_source = "ntk"
                result["ntk"] = ""
            elif ("cth " in lower and "cthnm" not in lower) or "chiêm tinh học" in lower:
                if "cth" not in result:
                    current_source = "cth"
                    result["cth"] = ""
                else:
                    current_source = None
            elif "đối chiếu" in lower or "tổng quan" in lower:
                current_source = "summary"
                if "summary" not in result:
                    result["summary"] = ""
                else:
                    current_source = None
            else:
                current_source = None
        elif current_source and hl and not hl.startswith("#"):
            if current_source in ("cth", "cthnm", "cthud", "ntk", "summary"):
                content = result.get(current_source, "")
                result[current_source] = content + "\n" + line

    for k in ("cth", "cthnm", "cthud", "ntk", "summary"):
        if k in result:
            result[k] = result[k].strip()

    return result if result else None


def _parse_overview_table(text: str) -> List[dict]:
    rows = []
    for line in text.split("\n"):
        if line.strip().startswith("|") and "**" in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 5:
                sign_cell = parts[1].replace("**", "").strip()
                sign_match = re.match(r"(\w[\w\s]+)\s*\((\w+)\)", sign_cell)
                if sign_match:
                    sign_vi = sign_match.group(1).strip()
                    sign_en = sign_match.group(2).strip()
                    mode = parts[3].strip() if len(parts) > 3 else ""
                    element = parts[4].strip() if len(parts) > 4 else ""
                    rows.append({
                        "sign_vi": sign_vi,
                        "sign_key": sign_en.lower(),
                        "mode": mode,
                        "element": element,
                    })
    return rows


_PLANET_VI_TO_EN = {
    "mặt trời": "sun", "sun": "sun",
    "mặt trăng": "moon", "moon": "moon",
    "sao thủy": "mercury", "mercury": "mercury",
    "sao kim": "venus", "venus": "venus",
    "sao hỏa": "mars", "mars": "mars",
    "sao mộc": "jupiter", "jupiter": "jupiter",
    "sao thổ": "saturn", "saturn": "saturn",
    "sao thiên vương": "uranus", "uranus": "uranus",
    "sao hải vương": "neptune", "neptune": "neptune",
    "sao diêm vương": "pluto", "pluto": "pluto",
}


def _parse_planet_synthesis(text: str) -> dict:
    planets = {}
    current_planet = None
    for line in text.split("\n"):
        m = re.match(r"##\s+(.+?)\s*\((\w+)\)", line)
        if m:
            name_vi = m.group(1).strip().lower()
            current_planet = _PLANET_VI_TO_EN.get(name_vi, name_vi)
            planets[current_planet] = {"name_vi": m.group(1).strip(), "entries": []}
        elif current_planet and line.strip().startswith("|"):
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 4:
                planets[current_planet]["entries"].append({
                    "source": parts[1],
                    "content": parts[2],
                })
    return planets


def _load_3ntk():
    # Prefer raw source file over chunks (avoids cross-chunk state loss)
    raw_fp = os.path.join(_KB_PATH, "3nhomtukhoanew.md")
    if os.path.isfile(raw_fp):
        with open(raw_fp, "r", encoding="utf-8") as f:
            _parse_3ntk_text(f.read())
            return

    ntk_dir = os.path.join(_KB_PATH, "3nhomtukhoanew_ai")
    fp = os.path.join(ntk_dir, "chunks.ndjson")
    if os.path.isfile(fp):
        import json
        with open(fp, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        chunk = json.loads(line)
                        _parse_3ntk_text(chunk.get("text", ""))
                    except json.JSONDecodeError:
                        pass


def _parse_3ntk_text(text: str):
    """Parse 3NTK table-format text into structured keyword entries."""
    lines = text.split("\n")
    current_planet_en = None
    current_sign = None
    current_house = None
    func_buf = ""
    past_header = False

    import unicodedata
    def _norm(s):
        return unicodedata.normalize('NFKD', s).lower().encode('ascii', 'ignore').decode('ascii')

    PLANET_DETECT = [
        ("sao thiên vương", "uranus"),
        ("sao hải vương", "neptune"),
        ("sao diêm vương", "pluto"),
        ("sao hoả", "mars"), ("sao hoa", "mars"),
        ("sao kim", "venus"),
        ("sao thuỷ", "mercury"), ("sao thuy", "mercury"),
        ("mặt trăng", "moon"),
        ("mặt trời", "sun"),
        ("sao mộc", "jupiter"), ("sao moc", "jupiter"),
        ("sao thổ", "saturn"), ("sao tho", "saturn"),
        ("diêm vương", "pluto"),
    ]

    SIGN_VI_EN = {
        "bạch dương": "aries", "kim ngưu": "taurus",
        "song tử": "gemini", "cự giải": "cancer",
        "sư tử": "leo", "xử nữ": "virgo",
        "thiên bình": "libra", "bọ cạp": "scorpio", "bò cạp": "scorpio",
        "nhân mã": "sagittarius", "ma kết": "capricorn",
        "bảo bình": "aquarius", "song ngư": "pisces",
    }

    def _clean(s):
        return re.sub(r'!\[.*?\]', '', s).strip()

    def _find_house(cells):
        """Search ALL cells for 'Cung N' pattern (varies by column)."""
        for c in cells:
            hm = re.search(r"Cung\s+(\d+)", c)
            if hm:
                return int(hm.group(1))
        return None

    for line in lines:
        s = line.strip()
        if not s.startswith('|') or '-----' in s:
            continue
        cells = [c.strip() for c in s.split('|')]
        first = cells[1] if len(cells) > 1 else ''
        if not first:
            continue

        c1 = _clean(first)
        c1l = c1.lower()

        # 1) Planet header row (skip image rows like "Sao Hoả ![][image1]")
        is_planet = False
        for k, v in PLANET_DETECT:
            kn = _norm(k)
            if k in c1l or kn in _norm(c1):
                current_planet_en = v
                current_sign = None
                current_house = None
                func_buf = ""
                past_header = False
                is_planet = True
                break
        if is_planet:
            continue

        # 2) Accumulate text (rows before sign/house header)
        if not past_header:
            func_buf += " " + c1

        # 3) Sign/house header row
        is_header = False
        for k, v in SIGN_VI_EN.items():
            kn = _norm(k)
            if c1l.startswith(k) or _norm(c1).startswith(kn):
                current_sign = v
                is_header = True
                break
        if is_header:
            # Search all cells for house number
            house_found = _find_house(cells[1:])
            if house_found is not None:
                current_house = house_found
            past_header = True

            if current_planet_en and current_sign and current_house is not None:
                key = f"{current_planet_en}_{current_sign}_{current_house}"
                if key not in _NTK_KEYWORDS:
                    _NTK_KEYWORDS[key] = {
                        "planet_vi": c1[:30],
                        "sign_vi": "",
                        "house": current_house,
                        "function": [],
                        "represents": [],
                        "sign_keywords": [],
                        "house_keywords": [],
                    }
                if func_buf:
                    # Try structured parsing first
                    fm = re.search(r'Chức\s*năng\s*:\s*(.+?)(?:Đại\s*diện|$)', func_buf, re.IGNORECASE | re.DOTALL)
                    rm = re.search(r'Đại\s*diện\s*(?:cho)?\s*:\s*(.+)$', func_buf, re.IGNORECASE | re.DOTALL)
                    if fm or rm:
                        if fm:
                            _NTK_KEYWORDS[key]['function'].append(fm.group(1).strip().rstrip(','))
                        if rm:
                            _NTK_KEYWORDS[key]['represents'].append(rm.group(1).strip().rstrip(','))
                    else:
                        # Fallback: use whole buffered text as function description
                        clean_buf = func_buf.replace("**", "").strip()
                        if len(clean_buf) > 20:
                            _NTK_KEYWORDS[key]['function'].append(clean_buf[:300])
                func_buf = ""
            continue

        # 4) Keyword rows (after sign/house header)
        if past_header and current_planet_en and current_sign and current_house is not None:
            key = f"{current_planet_en}_{current_sign}_{current_house}"
            if key in _NTK_KEYWORDS:
                # Build sign_keywords from first cell, house_keywords from any other cell with "Cung" content
                if c1 and len(c1) > 5 and not c1.startswith("**"):
                    _NTK_KEYWORDS[key]['sign_keywords'].append(c1)
                # Find house-related content in other columns
                for ci in range(2, len(cells)):
                    if cells[ci].strip() and len(cells[ci].strip()) > 10:
                        _NTK_KEYWORDS[key]['house_keywords'].append(cells[ci].strip())
                        break


def get_sign_synthesis(sign_key: str) -> Optional[dict]:
    _load_all()
    return _SIGN_SYNTHESIS.get(sign_key.lower())


def get_planet_synthesis(planet_key: str) -> Optional[dict]:
    _load_all()
    return _PLANET_SYNTHESIS.get(planet_key.lower())


def get_3ntk_keywords(planet: str, sign: str, house: int) -> Optional[dict]:
    _load_all()
    key = f"{planet}_{sign}_{house}"
    return _NTK_KEYWORDS.get(key)


def get_three_crosses_text() -> str:
    _load_all()
    return _THREE_CROSSES


def is_kb_available() -> bool:
    _load_all()
    return _KB_PATH is not None and bool(_SIGN_SYNTHESIS)


def _extract_content_lines(text: str) -> List[str]:
    """Extract meaningful content lines from a parsed section."""
    lines = []
    for raw_line in text.split("\n"):
        ln = raw_line.strip()
        if not ln or ln.startswith("#") or ln.startswith("|") or ln.startswith("**File"):
            continue
        lines.append(ln)
    return lines


def _extract_bullet_points(text: str) -> List[str]:
    """Extract bullet point content."""
    points = []
    for raw_line in text.split("\n"):
        ln = raw_line.strip()
        if ln.startswith("- ") or ln.startswith("* ") or ln.startswith("1. ") or ln.startswith("2. ") or ln.startswith("3. "):
            points.append(ln.lstrip("- *123.").strip())
    return points


def enrich_planet_in_sign(planet: str, sign: str, detailed: str) -> str:
    """Append knowledge base content to planet-in-sign interpretation."""
    _load_all()
    synth = _SIGN_SYNTHESIS.get(sign.lower())
    if not synth:
        return detailed

    extra_parts = []

    cthnm = synth.get("cthnm", "")
    if cthnm:
        lines = _extract_content_lines(cthnm)
        key_lines = [ln for ln in lines if any(kw in ln for kw in ["Từ khóa", "chủ âm", "keynote", "⏣"])]
        if not key_lines:
            key_lines = [ln for ln in lines if len(ln) > 30 and ":" in ln]
        if not key_lines:
            key_lines = lines[:2]
        if key_lines:
            extra_parts.append("📖 Nội môn: " + " | ".join(ln.replace("**", "").strip()[:150] for ln in key_lines[:3]))

    cth = synth.get("cth", "")
    if cth and not cthnm:
        lines = _extract_content_lines(cth)
        if lines:
            extra_parts.append("📚 Chiêm tinh: " + " ".join(ln.replace("**", "").strip()[:150] for ln in lines[:2]))

    cthud = synth.get("cthud", "")
    if cthud:
        lines = _extract_content_lines(cthud)
        career = [ln for ln in lines if "Sự nghiệp" in ln or "nghề" in ln.lower() or "nghiệp" in ln.lower()]
        love = [ln for ln in lines if "Tình yêu" in ln or "yêu" in ln.lower()]
        ud_parts = []
        if career:
            ud_parts.append(career[0].replace("**", "").strip()[:150])
        if love:
            ud_parts.append(love[0].replace("**", "").strip()[:150])
        if ud_parts:
            extra_parts.append("💼 Ứng dụng: " + " | ".join(ud_parts))

    ntk = synth.get("ntk", "")
    if ntk:
        lines = _extract_content_lines(ntk)
        kw_lines = [ln for ln in lines if ln and not ln.startswith("Lưu ý") and len(ln) > 10]
        if kw_lines:
            extra_parts.append("🔑 Từ khóa: " + "; ".join(ln.replace("**", "").strip()[:100] for ln in kw_lines[:4]))

    if extra_parts:
        return detailed + "\n\n" + "\n\n".join(extra_parts)
    return detailed


def enrich_planet_in_house(planet: str, house: int, detailed: str) -> str:
    """Append knowledge base 3NTK content to planet-in-house interpretation."""
    _load_all()
    extra_parts = []

    for key, entry in _NTK_KEYWORDS.items():
        if entry.get("house") == house:
            sign_kw = entry.get("sign_keywords", [])
            house_kw = entry.get("house_keywords", [])
            function_text = entry.get("function", [])
            represents_text = entry.get("represents", [])

            if function_text:
                preview = "; ".join(ln.replace("**", "").strip()[:100] for ln in function_text[:2])
                extra_parts.append("🔑 Chức năng: " + preview)
            if sign_kw:
                preview = "; ".join(ln.replace("**", "").strip()[:100] for ln in sign_kw[:3])
                extra_parts.append("🏠 Cung: " + preview)
            if house_kw:
                preview = "; ".join(ln.replace("**", "").strip()[:100] for ln in house_kw[:3])
                extra_parts.append("📋 Nhà: " + preview)
            if represents_text:
                preview = "; ".join(ln.replace("**", "").strip()[:100] for ln in represents_text[:2])
                extra_parts.append("🎭 Đại diện: " + preview)
            break

    if extra_parts:
        return detailed + "\n\n" + "\n\n".join(extra_parts[:3])
    return detailed


def clear_cache():
    global _SIGN_SYNTHESIS, _PLANET_SYNTHESIS, _THREE_CROSSES, _NTK_KEYWORDS, _loaded
    _SIGN_SYNTHESIS.clear()
    _PLANET_SYNTHESIS.clear()
    _THREE_CROSSES = ""
    _NTK_KEYWORDS.clear()
    _loaded = False
