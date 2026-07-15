"""Lightweight knowledge retriever over the crawled astrology markdown corpus.

The corpus (cafe_astrology / astrosage / astro_com / astrologyland) lives under
a folder of .md files, each with YAML frontmatter:
    ---
    title, url, source, category, subcategory, crawled_at
    ---
    <prose...>

We index every file once (lazy) and answer lookups like
``retrieve_planet_in_sign("sun", "aries")``. Matching prefers an EXACT
filename match (files are named ``planet_mars_sign/mars_in_scorpio_*.md`` etc.),
falling back to category/subcategory + token scoring. Returns a cleaned,
deduped prose snippet. This powers the English interpretation branch so
Astrololo's EN output matches the quality of the source sites.

Enabled via env ASTRO_KB_MARKDOWN (defaults to the known local corpus path).
"""
import os
import re
import glob
from typing import Dict, List, Optional, Tuple

_DEFAULT_PATH = r"C:\Users\BabaBun\Downloads\crawl kiến thức astro\data\markdown"

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_YAML_KV_RE = re.compile(r'^(\w+):\s*"?([^"\n]*)"?\s*$', re.MULTILINE)
_SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z])")
# Strip tables, nav menus, sponsored blocks, non-latin script, link-only lines
_TABLE_RE = re.compile(r"\|[^\n]*\|", re.MULTILINE)
_NAV_RE = re.compile(r"^(Home|Shop|Horoscopes|Site Map|Search|Site Menu|Charts|About|Contact|Skip to|Menu)\b.*$", re.MULTILINE | re.IGNORECASE)
_SPONSORED_RE = re.compile(r"Sponsored Links?:?", re.IGNORECASE)
_NONLATIN_RE = re.compile(r"[^\x00-\x7F\u00C0-\u024F]")  # drop anything outside basic + latin-extended
_HEADING_RE = re.compile(r"^#+.*$", re.MULTILINE)
_LINKMENU_RE = re.compile(r"^[\s\|]*\[?\]?\(?https?://", re.MULTILINE)  # lines that are basically URLs
_CLICK_RE = re.compile(r"click (on|here)|read (more|about)|see what the year|the following are interpretations|sign up|subscribe", re.IGNORECASE)
# A line that just enumerates all 12 signs is a menu, not content.
_SIGNLIST_RE = re.compile(r"^(aries taurus gemini cancer leo virgo libra scorpio sagittarius capricorn aquarius pisces|aries taurus gemini cancer leo virgo libra scorpio sagittarius capricorn aquarius and pisces)", re.IGNORECASE)
# Corpus "index" pages that only list links to sub-pages (not real content).
_INDEX_RE = re.compile(r"aspect page|the following aspects are presented|presented on this page|the meaning of the following|this page lists|following (aspects|pages)|aspects? (index|overview)", re.IGNORECASE)


def _is_index_page(text: str) -> bool:
    """True if the doc is a nav/index page listing sub-links, not real prose."""
    head = text[:400].lower()
    return bool(_INDEX_RE.search(head))

_HOUSE_WORDS = {
    1: "first", 2: "second", 3: "third", 4: "fourth", 5: "fifth", 6: "sixth",
    7: "seventh", 8: "eighth", 9: "ninth", 10: "tenth", 11: "eleventh", 12: "twelfth",
}

# Source quality preference (higher = better, more curated EN content)
_SOURCE_QUALITY = {
    "cafe_astrology": 3.0,
    "astro_com": 2.5,
    "www_astrologyland_com": 2.0,
    "astrosage": 1.0,
}

_PLANET_ALIASES = {
    "sun": "sun", "moon": "moon", "mercury": "mercury", "venus": "venus",
    "mars": "mars", "jupiter": "jupiter", "saturn": "saturn",
    "uranus": "uranus", "neptune": "neptune", "pluto": "pluto",
    "chiron": "chiron", "north_node": "north node|rahu", "south_node": "south node|ketu",
    "lilith": "lilith", "ceres": "ceres", "pallas": "pallas", "juno": "juno", "vesta": "vesta",
}
_SIGN_WORDS = {
    "aries": "aries", "taurus": "taurus", "gemini": "gemini", "cancer": "cancer",
    "leo": "leo", "virgo": "virgo", "libra": "libra", "scorpio": "scorpio",
    "sagittarius": "sagittarius", "capricorn": "capricorn", "aquarius": "aquarius", "pisces": "pisces",
}
_ASPECT_WORDS = {
    "conjunction": "conjunct", "opposition": "opposition", "square": "square",
    "trine": "trine", "sextile": "sextile", "quincunx": "quincunx",
    "semisextile": "semisextile", "semisquare": "semisquare", "sesquiquadrate": "sesquiquadrate",
}


class _Doc:
    __slots__ = ("title", "source", "category", "subcategory", "text", "tokens")

    def __init__(self, title, source, category, subcategory, text):
        self.title = title
        self.source = source
        self.category = (category or "").lower()
        self.subcategory = (subcategory or "").lower()
        self.text = text
        self.tokens = set(re.findall(r"[a-z]{3,}", text.lower()))


_INDEX: List[_Doc] = []
_BY_CAT: Dict[str, List[_Doc]] = {}
_BY_FILE: Dict[str, List[_Doc]] = {}  # normalized filename key -> docs
_LOADED = False
_KB_DIR: Optional[str] = None


def _parse_frontmatter(raw: str) -> Tuple[Dict[str, str], str]:
    m = _FRONTMATTER_RE.match(raw)
    meta: Dict[str, str] = {}
    body = raw
    if m:
        for k, v in _YAML_KV_RE.findall(m.group(1)):
            meta[k] = v.strip()
        body = raw[m.end():]
    return meta, body


def _clean_prose(body: str) -> str:
    body = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", body)
    body = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", body)  # keep link text
    body = _TABLE_RE.sub("", body)
    body = _HEADING_RE.sub("", body)
    lines = [ln.strip() for ln in body.splitlines()]
    out: List[str] = []
    for ln in lines:
        if _SPONSORED_RE.search(ln):
            continue
        if _NAV_RE.match(ln):
            continue
        if _LINKMENU_RE.match(ln):
            continue
        if _CLICK_RE.search(ln):
            continue
        if _SIGNLIST_RE.match(ln):
            continue
        if _NONLATIN_RE.search(ln):  # drop non-latin (Tamil/Telugu/etc) lines
            continue
        if len(ln) < 45:  # drop fragments/short menu labels
            continue
        out.append(ln)
    return "\n".join(out).strip()


def _norm_file_key(fp: str) -> str:
    base = os.path.basename(fp).lower()
    base = re.sub(r"20[0-9]{6}_[0-9]{6}", "", base)  # strip datestamp
    base = re.sub(r"[^a-z0-9]+", "_", base).strip("_")
    return base


def _load_all() -> None:
    global _LOADED, _KB_DIR, _INDEX, _BY_CAT, _BY_FILE
    if _LOADED:
        return
    _LOADED = True
    env = os.environ.get("ASTRO_KB_MARKDOWN", "").strip()
    _KB_DIR = env if env and os.path.isdir(env) else _DEFAULT_PATH
    if not _KB_DIR or not os.path.isdir(_KB_DIR):
        return
    files = glob.glob(os.path.join(_KB_DIR, "**", "*.md"), recursive=True)
    seen: set = set()
    for fp in files:
        try:
            with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                raw = f.read()
        except Exception:
            continue
        meta, body = _parse_frontmatter(raw)
        title = meta.get("title", os.path.basename(fp))
        key = (title.lower(), meta.get("source", ""))
        if key in seen:
            continue
        seen.add(key)
        text = _clean_prose(body)
        if len(text) < 120:  # skip stubs
            continue
        doc = _Doc(title, meta.get("source", ""), meta.get("category", ""),
                   meta.get("subcategory", ""), text)
        _INDEX.append(doc)
        _BY_CAT.setdefault(doc.category, []).append(doc)
        _BY_FILE.setdefault(_norm_file_key(fp), []).append(doc)


def is_available() -> bool:
    _load_all()
    return len(_INDEX) > 0


def _score(doc: _Doc, want_tokens: set, cat_hint: str, sub_hint: str) -> float:
    s = 0.0
    if cat_hint and cat_hint in doc.category:
        s += 4.0
    if sub_hint and sub_hint and sub_hint in doc.subcategory:
        s += 6.0
    overlap = want_tokens & doc.tokens
    s += min(len(overlap), 12) * 1.0
    s += _SOURCE_QUALITY.get(doc.source, 1.0)
    return s


def _best_docs(want_tokens: set, cat_hint: str, sub_hint: str, limit: int = 3) -> List[_Doc]:
    _load_all()
    if not _INDEX:
        return []
    scored = [( _score(d, want_tokens, cat_hint, sub_hint), d) for d in _INDEX]
    scored = [x for x in scored if x[0] > 0]
    scored = [x for x in scored if (want_tokens & x[1].tokens)]  # require a wanted token
    scored = [x for x in scored if not _is_index_page(x[1].text)]  # skip nav/index
    scored.sort(key=lambda x: x[0], reverse=True)
    out: List[_Doc] = []
    used_src: set = set()
    for _, d in scored:
        if d.source in used_src:
            continue
        used_src.add(d.source)
        out.append(d)
        if len(out) >= limit:
            break
    return out


def _extract_relevant(text: str, want_tokens: set, max_chars: int = 900) -> str:
    sents = _SENT_SPLIT_RE.split(text)
    sents = [s.strip() for s in sents if len(s.strip()) > 45 and not _NONLATIN_RE.search(s)
             and not _LINKMENU_RE.search(s) and not _CLICK_RE.search(s)]
    if not sents:
        return ""
    def _rel(s: str) -> int:
        toks = set(re.findall(r"[a-z]{3,}", s.lower()))
        return len(want_tokens & toks)
    sents.sort(key=_rel, reverse=True)
    out: List[str] = []
    total = 0
    for s in sents:
        if total + len(s) > max_chars:
            if not out:
                out.append(s[:max_chars])
            break
        out.append(s)
        total += len(s) + 1
        if total >= max_chars:
            break
    return " ".join(out).strip()


def _tokens(*words: str) -> set:
    toks: set = set()
    for w in words:
        toks.update(re.findall(r"[a-z]{3,}", w.lower()))
    return toks


def _file_match(keys: List[str]) -> Optional[_Doc]:
    """Best doc whose normalized filename KEY CONTAINS one of the given keys
    (substring, since filename keys include a category prefix)."""
    _load_all()
    best: Optional[_Doc] = None
    best_score = -1.0
    for fk, docs in _BY_FILE.items():
        if not any(k in fk for k in keys):
            continue
        for doc in docs:
            if _is_index_page(doc.text):
                continue
            sc = _SOURCE_QUALITY.get(doc.source, 1.0)
            if sc > best_score:
                best_score = sc
                best = doc
    return best


def retrieve_planet_in_sign(planet: str, sign: str, max_chars: int = 1100) -> Optional[str]:
    p = _PLANET_ALIASES.get(planet, planet)
    s = _SIGN_WORDS.get(sign, sign)
    # Exact filename keys: "planet_mars_sign_mars_in_scorpio", "sun_in_aries", etc.
    doc = _file_match([f"{p}_{s}", f"{p}_in_{s}", f"{p}_{sign}"])
    if doc:
        snippet = _extract_relevant(doc.text, _tokens(p, s), max_chars)
        if snippet:
            return f"{snippet}  (source: {doc.source})"
    # Fallback: score-based
    want = _tokens(p, s)
    docs = _best_docs(want, "planet", f"{p}_{s}")
    if not docs:
        docs = _best_docs(want, "zodiac", s)
    if not docs:
        return None
    snippet = _extract_relevant(docs[0].text, want, max_chars)
    return f"{snippet}  (source: {docs[0].source})" if snippet else None


def retrieve_planet_in_house(planet: str, house: int, max_chars: int = 1100) -> Optional[str]:
    p = _PLANET_ALIASES.get(planet, planet)
    hword = _HOUSE_WORDS.get(house, str(house))
    doc = _file_match([f"{p}_{hword}_house", f"{p}_in_{hword}_house", f"planet_{p}_{hword}_house"])
    if doc:
        snippet = _extract_relevant(doc.text, _tokens(p, f"house {house}"), max_chars)
        if snippet:
            return f"{snippet}  (source: {doc.source})"
    want = _tokens(p, f"house {house}", f"{house}")
    docs = _best_docs(want, "planet", f"{p}_{house}")
    if not docs:
        docs = _best_docs(want, "houses", f"house_{house}")
    if not docs:
        return None
    snippet = _extract_relevant(docs[0].text, want, max_chars)
    return f"{snippet}  (source: {docs[0].source})" if snippet else None


def retrieve_aspect(planet1: str, planet2: str, aspect_type: str, max_chars: int = 1100) -> Optional[str]:
    a = _ASPECT_WORDS.get(aspect_type, aspect_type)
    p1 = _PLANET_ALIASES.get(planet1, planet1)
    p2 = _PLANET_ALIASES.get(planet2, planet2)
    for k in [f"{p1}_{p2}_{a}", f"{p1}_{a}_{p2}", f"{p2}_{p1}_{a}", f"{p1}_{p2}"]:
        doc = _file_match([k])
        if doc:
            snippet = _extract_relevant(doc.text, _tokens(p1, p2, a), max_chars)
            if snippet:
                return f"{snippet}  (source: {doc.source})"
    # broader: any corpus file whose name contains BOTH planets (e.g. sun_and_moon)
    for fk, docs in _BY_FILE.items():
        if p1 in fk and p2 in fk and not _is_index_page(docs[0].text):
            snippet = _extract_relevant(docs[0].text, _tokens(p1, p2, a), max_chars)
            if snippet:
                return f"{snippet}  (source: {docs[0].source})"
    want = _tokens(p1, p2, a)
    docs = _best_docs(want, "aspects", f"{p1}_{p2}")
    if not docs:
        docs = _best_docs(want, "aspects", "")
    if not docs:
        docs = _best_docs(want, "compatibility", f"{p1}_{p2}")
    if not docs:
        return None
    snippet = _extract_relevant(docs[0].text, want, max_chars)
    return f"{snippet}  (source: {docs[0].source})" if snippet else None


def retrieve_compatibility(person1: str, person2: str, max_chars: int = 1100) -> Optional[str]:
    """Whole-pair synastry overview from the love_compatibility corpus."""
    p1 = _PLANET_ALIASES.get(person1, person1)
    p2 = _PLANET_ALIASES.get(person2, person2)
    for k in [f"{p1}_{p2}", f"{p2}_{p1}", "synastry", "compatibility_overview"]:
        doc = _file_match([k])
        if doc:
            snippet = _extract_relevant(doc.text, _tokens(p1, p2), max_chars)
            if snippet:
                return f"{snippet}  (source: {doc.source})"
    want = _tokens(p1, p2)
    docs = _best_docs(want, "love_compatibility", f"{p1}_{p2}")
    if not docs:
        docs = _best_docs(want, "compatibility", "")
    if not docs:
        return None
    snippet = _extract_relevant(docs[0].text, want, max_chars)
    return f"{snippet}  (source: {docs[0].source})" if snippet else None
