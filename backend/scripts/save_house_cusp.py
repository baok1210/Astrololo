"""Save AstroLibrary house_cusp data as a standalone template file.

Usage: python save_house_cusp.py
"""
import os
import yaml

SCRIPTS_DIR = os.path.dirname(__file__)
ASTRO_FULL = os.path.join(SCRIPTS_DIR, "astrolib_full.yaml")
TEMPLATES_DIR = os.path.join(SCRIPTS_DIR, "..", "astrololo", "interpretation", "templates", "en")
OUTPUT = os.path.join(TEMPLATES_DIR, "house_cusp.yaml")

def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def save_yaml(path, data):
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

def main():
    full = load_yaml(ASTRO_FULL)
    cusp_data = full.get("house_cusp", {})
    
    # Convert from AstroLibrary format to template format
    # AstroLibrary: {sign_cap: [{house: N, text: "...", title: "..."}, ...]}
    # Template:   {sign_lower: {str(house): {title, short, detailed}}}
    output = {}
    for sign_cap, entries in cusp_data.items():
        sign_lower = sign_cap.lower()
        sign_dict = {}
        for e in entries:
            h = e.get("house")
            if h is None:
                continue
            text = e.get("text", "").strip()
            if not text or len(text) < 50:
                continue
            lines = text.split("\n")
            short = lines[0].strip() if lines else text[:100]
            if len(short) > 200:
                short = short[:200]
            sign_dict[str(h)] = {
                "title": e.get("title") or f"{sign_cap} on House {h} cusp",
                "short": short,
                "detailed": text,
                "source": "astrolibrary.org"
            }
        if sign_dict:
            output[sign_lower] = sign_dict
    
    save_yaml(OUTPUT, output)
    total = sum(len(v) for v in output.values())
    print(f"Saved {total} house_cusp entries across {len(output)} signs to {OUTPUT}")
    for s, d in sorted(output.items()):
        print(f"  {s}: {len(d)} houses")

if __name__ == "__main__":
    main()
