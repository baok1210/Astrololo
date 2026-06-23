"""Scrape Capricorn cusp from AstroLibrary (typo URL) and add to house_cusp.yaml."""
import os
import yaml
import re
import requests
from bs4 import BeautifulSoup

SCRIPTS_DIR = os.path.dirname(__file__)
TEMPLATES_DIR = os.path.join(SCRIPTS_DIR, "..", "astrololo", "interpretation", "templates", "en")

HEADERS = {'User-Agent': 'Mozilla/5.0'}

def fetch(url):
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.text

def clean_text(text):
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def scrape_capricorn_cusp():
    """Scrape capricorn cusp from typo URL with same structure as other cusp pages."""
    url = "https://astrolibrary.org/interpretations/capricon-cusp/"
    html = fetch(url)
    soup = BeautifulSoup(html, "html.parser")
    content = soup.find("div", id="readwidth") or soup.find("article") or soup.find("main") or soup.find("body")
    text_content = content.get_text("\n")
    
    HOUSE_SUFFIXES = ["1st", "2nd", "3rd", "4th", "5th", "6th", "7th", "8th", "9th", "10th", "11th", "12th"]
    patterns = [f"Capricorn on {hs} House Cusp" for hs in HOUSE_SUFFIXES]
    
    entries = []
    for i, (pattern, hs) in enumerate(zip(patterns, range(1, 13))):
        idx = text_content.find(pattern)
        if idx < 0:
            print(f"  H{hs}: heading not found")
            continue
        start = idx + len(pattern)
        end = len(text_content)
        for j in range(i + 1, len(patterns)):
            nidx = text_content.find(patterns[j], start)
            if nidx >= 0 and nidx < end:
                end = nidx
                break
        section = text_content[start:end]
        text = clean_text(section)
        if text:
            entries.append({"house": hs, "text": text, "title": f"Capricorn on {hs}{'st' if hs==1 else 'nd' if hs==2 else 'rd' if hs==3 else 'th'} House Cusp"})
    
    return entries

def merge_into_template(entries):
    """Add capricorn entries to house_cusp.yaml."""
    path = os.path.join(TEMPLATES_DIR, "house_cusp.yaml")
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}
    
    cap_dict = {}
    for e in entries:
        h = str(e["house"])
        text = e["text"]
        lines = text.split("\n")
        short = lines[0].strip() if lines else text[:100]
        if len(short) > 200:
            short = short[:200]
        cap_dict[h] = {
            "title": e["title"],
            "short": short,
            "detailed": text,
            "source": "astrolibrary.org"
        }
    data["capricorn"] = cap_dict
    
    with open(path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    print(f"Added capricorn cusp ({len(entries)}/12 entries)")

if __name__ == "__main__":
    entries = scrape_capricorn_cusp()
    if len(entries) == 12:
        merge_into_template(entries)
    else:
        print(f"Only got {len(entries)}/12 entries, aborting")
        for e in entries:
            print(f"  H{e['house']}: {len(e['text'])} chars")
