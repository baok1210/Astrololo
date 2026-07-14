"""Bake the crawled markdown corpus into durable EN YAML templates.

Run once:  python scripts/import_crawl_kb.py
Generates:
  astrololo/interpretation/templates/en/planet_in_sign_baked.yaml
  astrololo/interpretation/templates/en/planet_in_house_baked.yaml
  astrololo/interpretation/templates/en/aspects_baked.yaml

These are consulted (in template_loader) AFTER the hand-curated EN templates
but BEFORE the live retriever / keyword fallback, so the integration is durable
and does not depend on the external corpus folder at runtime. Personal use.

Usage:
  ASTRO_KB_MARKDOWN="<path to markdown corpus>" python scripts/import_crawl_kb.py
"""
import os
import sys

# Make the backend importable when run as a script: scripts/ -> backend/
_BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _BACKEND)

from astrololo.interpretation.knowledge_retriever import (  # noqa: E402
    retrieve_planet_in_sign, retrieve_planet_in_house, retrieve_aspect, is_available,
)

_SIGNS = ["aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra",
          "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"]
_PLANETS = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn",
            "uranus", "neptune", "pluto", "chiron", "north_node", "south_node",
            "lilith", "ceres", "pallas", "juno", "vesta"]
_HOUSES = list(range(1, 13))
_ASPECTS = ["conjunction", "opposition", "square", "trine", "sextile",
            "quincunx", "semisextile", "semisquare", "sesquiquadrate"]
# Pairs worth baking for aspect templates (skip trivial self-pairs)
import itertools
_PAIRS = []
for a, b in itertools.combinations(_PLANETS, 2):
    _PAIRS.append((a, b))

_TPL_DIR = os.path.join(_BACKEND, "astrololo", "interpretation", "templates", "en")


def _entry(planet, sign, house, aspect_type, planet2, kind):
    if kind == "sign":
        text = retrieve_planet_in_sign(planet, sign)
        return _wrap(text)
    if kind == "house":
        text = retrieve_planet_in_house(planet, house)
        return _wrap(text)
    if kind == "aspect":
        text = retrieve_aspect(planet, planet2, aspect_type)
        return _wrap(text)
    return None


def _wrap(text):
    if not text:
        return None
    # strip the trailing "  (source: ...)" citation we added for live mode
    text = text.rsplit("  (source:", 1)[0].strip()
    if len(text) < 80:
        return None
    return {"title": "", "short": "", "detailed": text,
            "strength": "See description", "weakness": "See description"}


def _build_sign():
    data = {}
    for p in _PLANETS:
        data[p] = {}
        for s in _SIGNS:
            e = _entry(p, s, None, None, None, "sign")
            if e:
                data[p][s] = e
    return data


def _build_house():
    data = {}
    for p in _PLANETS:
        data[p] = {}
        for h in _HOUSES:
            e = _entry(p, None, h, None, None, "house")
            if e:
                data[p][str(h)] = e
    return data


def _build_aspect():
    data = {}
    for a in _ASPECTS:
        data[a] = {}
        for p1, p2 in _PAIRS:
            e = _entry(p1, None, None, a, p2, "aspect")
            if e:
                data[a][f"{p1}_{p2}"] = e
    return data


def _dump(fname, obj):
    import yaml
    path = os.path.join(_TPL_DIR, fname)
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(obj, f, allow_unicode=True, sort_keys=False, width=1000)
    # count filled
    n = sum(len(v) for v in obj.values()) if isinstance(obj, dict) else 0
    print(f"  wrote {fname}: {n} entries")


def main():
    if not is_available():
        print("ERROR: knowledge retriever not available. Set ASTRO_KB_MARKDOWN to the corpus folder.")
        sys.exit(1)
    print("Baking corpus into EN YAML templates...")
    _dump("planet_in_sign_baked.yaml", _build_sign())
    _dump("planet_in_house_baked.yaml", _build_house())
    _dump("aspects_baked.yaml", _build_aspect())
    print("Done. Templates are in:", _TPL_DIR)


if __name__ == "__main__":
    main()
