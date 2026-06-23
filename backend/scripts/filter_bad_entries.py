"""Remove bad entries from en/planet_in_sign.yaml and en/planet_in_house.yaml.

Removes entries where:
- Planet Neptune, sign Aries: just dates + "Read about" link text (73 chars)
"""
import os
import yaml

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "astrololo", "interpretation", "templates", "en")

def load_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def save_yaml(path, data):
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

def is_short_link_entry(val):
    """Check if entry is just dates + 'Read about' link text."""
    if isinstance(val, dict):
        text = val.get("detailed", "") or val.get("short", "") or ""
    elif isinstance(val, str):
        text = val
    else:
        return False
    text = text.strip()
    if len(text) < 80 and ("Read about" in text):
        return True
    return False

def clean_entries(data):
    """Remove short link-only entries from yaml data."""
    changes = []
    for planet in list(data.keys()):
        planet_data = data[planet]
        if isinstance(planet_data, dict):
            for key in list(planet_data.keys()):
                entry = planet_data[key]
                if is_short_link_entry(entry):
                    del planet_data[key]
                    changes.append((planet, key))
        elif isinstance(planet_data, list):
            # List-based format (shouldn't happen but handle it)
            filtered = [e for e in planet_data if not is_short_link_entry(e)]
            if len(filtered) != len(planet_data):
                changes.append((planet, f"removed {len(planet_data) - len(filtered)} entries"))
                data[planet] = filtered
    return changes

def main():
    sign_path = os.path.join(TEMPLATES_DIR, "planet_in_sign.yaml")
    house_path = os.path.join(TEMPLATES_DIR, "planet_in_house.yaml")
    
    sign_data = load_yaml(sign_path)
    house_data = load_yaml(house_path)
    
    sign_changes = clean_entries(sign_data)
    house_changes = clean_entries(house_data)
    
    if sign_changes:
        save_yaml(sign_path, sign_data)
        print(f"planet_in_sign.yaml: removed {len(sign_changes)} entries")
        for planet, key in sign_changes:
            print(f"  {planet}/{key}")
    
    if house_changes:
        save_yaml(house_path, house_data)
        print(f"planet_in_house.yaml: removed {len(house_changes)} entries")
        for planet, key in house_changes:
            print(f"  {planet}/{key}")
    
    if not sign_changes and not house_changes:
        print("No bad entries found.")

if __name__ == "__main__":
    main()
