"""Merge AstroLibrary scraped data into existing en/ templates.

Usage: python merge_astrolibrary.py [--apply]

Without --apply, shows what would change.
With --apply, modifies the files in-place.
"""
import sys
import os
import yaml

BASE = os.path.join(os.path.dirname(__file__), "..", "astrololo", "interpretation")
TEMPLATES_DIR = os.path.join(BASE, "templates", "en")
ASTRO_FULL = os.path.join(os.path.dirname(__file__), "astrolib_full.yaml")

def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def save_yaml(path, data):
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

def format_text(entry, default_title="", source_label="astrolibrary.org"):
    """Convert a single AstroLibrary entry to standard {title, short, detailed} format."""
    text = entry.get("text", "").strip()
    if not text:
        return None
    lines = text.split("\n")
    short = lines[0].strip() if lines else text[:100]
    if len(short) > 200:
        short = short[:200]
    return {
        "title": entry.get("title") or default_title,
        "short": short,
        "detailed": text,
        "source": source_label
    }

def merge_signs(astrolib_data, existing, apply=False):
    """Merge planet_in_sign data. Format: {planet: {sign_key: text_or_dict}}"""
    changes = []
    src = astrolib_data.get("planet_in_sign", {})
    
    for planet, entries in src.items():
        existing_planet = existing.get(planet, {})
        existing_keys = set(existing_planet.keys())
        added = 0
        
        # Convert AstroLibrary entries to {sign_lower: formatted_dict}
        astro_dict = {}
        for e in entries:
            sign_raw = e.get("sign", "").strip().lower()
            sign_cap = sign_raw.capitalize()
            planet_cap = planet.capitalize()
            fmt = format_text(e, default_title=f"{planet_cap} in {sign_cap}")
            if fmt and sign_raw:
                astro_dict[sign_raw] = fmt
        
        # Merge: only add entries not already present
        merged = dict(existing_planet)
        for sk, val in astro_dict.items():
            if sk not in existing_keys:
                merged[sk] = val
                added += 1
        
        if added > 0:
            changes.append((planet, len(existing_planet), len(merged), added))
            if apply:
                existing[planet] = merged
    
    return changes

def merge_houses(astrolib_data, existing, apply=False):
    """Merge planet_in_house data. Format: {planet: {house_str: text_or_dict}}"""
    changes = []
    src = astrolib_data.get("planet_in_house", {})
    
    for planet, entries in src.items():
        existing_planet = existing.get(planet, {})
        existing_keys = set(existing_planet.keys())
        added = 0
        
        astro_dict = {}
        for e in entries:
            h = e.get("house")
            if h is None:
                continue
            h_key = str(h)
            suffix = "th" if h not in (1,2,3) else {1:"st",2:"nd",3:"rd"}[h]
            planet_cap = planet.capitalize()
            fmt = format_text(e, default_title=f"{planet_cap} in the {h}{suffix} House")
            if fmt:
                astro_dict[h_key] = fmt
        
        merged = dict(existing_planet)
        for hk, val in astro_dict.items():
            if hk not in existing_keys:
                merged[hk] = val
                added += 1
        
        if added > 0:
            changes.append((planet, len(existing_planet), len(merged), added))
            if apply:
                existing[planet] = merged
    
    return changes

def main():
    apply = "--apply" in sys.argv
    astrolib = load_yaml(ASTRO_FULL)

    sign_path = os.path.join(TEMPLATES_DIR, "planet_in_sign.yaml")
    house_path = os.path.join(TEMPLATES_DIR, "planet_in_house.yaml")
    
    existing_sign = load_yaml(sign_path)
    existing_house = load_yaml(house_path)
    
    sign_changes = merge_signs(astrolib, existing_sign, apply=apply)
    house_changes = merge_houses(astrolib, existing_house, apply=apply)
    
    all_changes = sign_changes + house_changes
    if not all_changes:
        print("No changes needed.")
        return
    
    label = "ADDED" if apply else "WOULD ADD"
    print(f"{label} {sum(c[3] for c in all_changes)} entries:")
    for name, old, new, added in all_changes:
        print(f"  {name}: {old} -> {new} (+{added})")
    
    if not apply:
        print("\nRun with --apply to write changes.")
    else:
        save_yaml(sign_path, existing_sign)
        save_yaml(house_path, existing_house)
        print(f"Saved planet_in_sign.yaml ({sum(len(v) for v in existing_sign.values())} total entries)")
        print(f"Saved planet_in_house.yaml ({sum(len(v) for v in existing_house.values())} total entries)")

if __name__ == "__main__":
    main()
