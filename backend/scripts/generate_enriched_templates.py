#!/usr/bin/env python
"""Generate enriched Vietnamese YAML templates from knowledge base.

Usage:
    python scripts/generate_enriched_templates.py          # preview only
    python scripts/generate_enriched_templates.py --apply   # write files
    python scripts/generate_enriched_templates.py --apply --lang en  # English too
"""
import sys
import os
import shutil
import yaml

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from astrololo.interpretation.knowledge_base import (
    is_kb_available, get_sign_synthesis
)
from astrololo.interpretation.template_loader import (
    get_planet_in_sign, get_planet_in_house, _load_yaml
)

PLANET_KEYS = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]
SIGN_KEYS = ["aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"]

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "astrololo", "interpretation", "templates")


def backup_file(filepath: str):
    if os.path.exists(filepath):
        bak = filepath + ".bak"
        if not os.path.exists(bak):
            shutil.copy2(filepath, bak)
            print(f"  Backup: {os.path.basename(bak)}")


def generate_planet_in_sign(lang: str) -> dict:
    """Generate enriched planet_in_sign YAML data."""
    data = _load_yaml(lang, "planet_in_sign.yaml")

    if not data:
        data = {}

    enriched = {}
    for planet in PLANET_KEYS:
        planet_data = data.get(planet, {})
        enriched[planet] = {}
        for sign in SIGN_KEYS:
            # Get existing entry (either from YAML or from fallback)
            entry = get_planet_in_sign(planet, sign, lang) if lang == "vi" else (
                planet_data.get(sign) if isinstance(planet_data.get(sign), dict)
                else {"title": f"{planet} in {sign}", "short": "", "detailed": str(planet_data.get(sign, ""))}
            )
            if entry is None:
                continue

            # Collect knowledge base content
            kb_parts = []
            if lang == "vi":
                synth = get_sign_synthesis(sign)
                if synth:
                    for label, key in [("📖 Nội môn", "cthnm"), ("💼 Ứng dụng", "cthud"), ("🔑 Từ khóa", "ntk")]:
                        text = synth.get(key, "")
                        if text:
                            clean = text.replace("**", "").strip()
                            lines = [l.strip() for l in clean.split("\n") if l.strip() and not l.startswith("#") and not l.startswith("|")]
                            if lines:
                                preview = "; ".join(l[:120] for l in lines[:4])
                                kb_parts.append(f"{label}: {preview}")

            existing_detailed = entry.get("detailed", "") if isinstance(entry, dict) else str(entry)

            # Build enriched entry
            if kb_parts:
                new_detailed = existing_detailed + "\n\n" + "\n\n".join(kb_parts)
            else:
                new_detailed = existing_detailed

            if isinstance(entry, dict):
                enriched[planet][sign] = dict(entry)
                enriched[planet][sign]["detailed"] = new_detailed
            else:
                enriched[planet][sign] = new_detailed

    return enriched


def generate_planet_in_house(lang: str) -> dict:
    """Generate enriched planet_in_house YAML data."""
    data = _load_yaml(lang, "planet_in_house.yaml")
    if not data:
        data = {}

    enriched = {}
    for planet in PLANET_KEYS:
        planet_data = data.get(planet, {})
        enriched[planet] = {}
        for h in range(1, 13):
            entry = get_planet_in_house(planet, h, lang) if lang == "vi" else (
                planet_data.get(str(h)) if isinstance(planet_data.get(str(h)), dict) or isinstance(planet_data.get(str(h)), str)
                else None
            )
            if entry is None:
                continue

            kb_parts = []
            if lang == "vi":
                # Get 3NTK knowledge for this house
                from astrololo.interpretation.knowledge_base import get_3ntk_keywords
                for sk in SIGN_KEYS:
                    ntk = get_3ntk_keywords(planet, sk, h)
                    if ntk:
                        func = ntk.get("function", [])
                        hkw = ntk.get("house_keywords", [])
                        skw = ntk.get("sign_keywords", [])
                        if func:
                            kb_parts.append(f"🔑 Chức năng: {'; '.join(l.replace('**','').strip()[:100] for l in func[:2])}")
                        if hkw:
                            kb_parts.append(f"📋 Nhà {h}: {'; '.join(l.replace('**','').strip()[:100] for l in hkw[:2])}")
                        if skw:
                            kb_parts.append(f"🏠 Cung: {'; '.join(l.replace('**','').strip()[:100] for l in skw[:2])}")
                        break

            existing_detailed = entry.get("detailed", "") if isinstance(entry, dict) else str(entry)

            if kb_parts:
                new_detailed = existing_detailed + "\n\n" + "\n\n".join(kb_parts[:3])
            else:
                new_detailed = existing_detailed

            if isinstance(entry, dict):
                enriched[planet][str(h)] = dict(entry)
                enriched[planet][str(h)]["detailed"] = new_detailed
            else:
                enriched[planet][str(h)] = new_detailed

    return enriched


def main():
    apply = "--apply" in sys.argv
    lang = "en" if "--lang" in sys.argv and sys.argv[sys.argv.index("--lang") + 1] == "en" else "vi"

    if not is_kb_available():
        print("❌ Knowledge base not found. Run from project root or set ASTRO_KNOWLEDGE_BASE.")
        sys.exit(1)

    print(f"✅ Knowledge base found. Language: {lang}")
    print(f"   Apply mode: {'WRITE FILES' if apply else 'preview only'}")
    print()

    # Generate planet_in_sign
    print("Generating planet_in_sign.yaml...")
    sign_data = generate_planet_in_sign(lang)

    sign_path = os.path.join(TEMPLATES_DIR, lang, "planet_in_sign.yaml")
    total_sign_entries = sum(len(planets) for planets in sign_data.values())
    print(f"  Total entries: {total_sign_entries}")

    # Count enriched entries
    enriched_count = 0
    for planet, signs in sign_data.items():
        for sign, entry in signs.items():
            if isinstance(entry, dict) and "📖" in entry.get("detailed", ""):
                enriched_count += 1
    print(f"  Enriched with KB: {enriched_count}")

    if apply:
        backup_file(sign_path)
        with open(sign_path, "w", encoding="utf-8") as f:
            yaml.dump(sign_data, f, allow_unicode=True, sort_keys=True, default_flow_style=None, width=120)
        print(f"  Written: {sign_path}")

    print()

    # Generate planet_in_house
    print("Generating planet_in_house.yaml...")
    house_data = generate_planet_in_house(lang)

    house_path = os.path.join(TEMPLATES_DIR, lang, "planet_in_house.yaml")
    total_house_entries = sum(len(planets) for planets in house_data.values())
    print(f"  Total entries: {total_house_entries}")

    enriched_house = 0
    for planet, houses in house_data.items():
        for house, entry in houses.items():
            if isinstance(entry, dict) and ("🔑" in entry.get("detailed", "") or "📋" in entry.get("detailed", "")):
                enriched_house += 1
    print(f"  Enriched with KB: {enriched_house}")

    if apply:
        backup_file(house_path)
        with open(house_path, "w", encoding="utf-8") as f:
            yaml.dump(house_data, f, allow_unicode=True, sort_keys=True, default_flow_style=None, width=120)
        print(f"  Written: {house_path}")

    print()
    print("Done!")
    if not apply:
        print("Use --apply to write files. Backups created as .bak.")


if __name__ == "__main__":
    main()
