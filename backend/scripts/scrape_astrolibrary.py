"""
Scrape AstroLibrary.org for planet-in-sign, planet-in-house, and house-cusp content.
Outputs YAML to stdout.
"""
import sys
import time
import re
import argparse
import requests
from bs4 import BeautifulSoup
import yaml


def fetch(url):
    resp = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    return resp.text


def clean_text(text):
    """Remove navigation links, ads, and boilerplate from extracted text."""
    text = re.sub(r'\bBack to Interpretations\b.*?(?=\n|$)', '', text)
    text = re.sub(r'\bRead more about\b.*?(?=\n|$)', '', text)
    text = re.sub(r'\bSee gift ideas\b.*?(?=\n|$)', '', text)
    text = re.sub(r'\bSee .*? Rising Sign combinations\b.*?(?=\n|$)', '', text)
    text = re.sub(r'\bMore about\b.*?(?=\n|$)', '', text)
    text = re.sub(r'\bGo to top\b.*?(?=\n|$)', '', text)
    text = re.sub(r'\bJump down to:?\b.*?(?=\n)', '', text, flags=re.DOTALL)
    text = re.sub(r'\bHelpful Resources\b.*$', '', text, flags=re.DOTALL)
    text = re.sub(r'\bSearch for:\b.*$', '', text, flags=re.DOTALL)
    text = re.sub(r'\bInterpretations Credits:?\b.*$', '', text, flags=re.DOTALL)
    text = re.sub(r'\bCopyright\b.*$', '', text, flags=re.DOTALL)
    text = re.sub(r'\bExplore What.*$', '', text, flags=re.DOTALL)
    text = re.sub(r'\bBirth Chart Interpretations\b.*$', '', text, flags=re.DOTALL)
    text = re.sub(r'\bPlanets and Points in Signs\b.*$', '', text, flags=re.DOTALL)
    text = re.sub(r'\bPlanets in Houses\b.*$', '', text, flags=re.DOTALL)
    text = re.sub(r'\bHouse Cusp Signs\b.*$', '', text, flags=re.DOTALL)
    text = re.sub(r'\bAspects\b.*$', '', text, flags=re.DOTALL)
    text = re.sub(r'\bBalance of Elements\b.*$', '', text, flags=re.DOTALL)
    text = re.sub(r'\bBalance of Qualities\b.*$', '', text, flags=re.DOTALL)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_by_heading(html, heading_patterns, label_key, label_values):
    """Generic extractor: find heading matching pattern, extract text until next heading or end."""
    soup = BeautifulSoup(html, "html.parser")
    content = soup.find("div", id="readwidth") or soup.find("article") or soup.find("main") or soup.find("body")
    raw = str(content)
    text_content = content.get_text("\n")

    results = []

    for i, lv in enumerate(label_values):
        # Find where this heading starts in the text content
        heading = heading_patterns[i]
        # Search get_text output for heading text
        idx = text_content.find(heading)
        if idx < 0:
            continue

        start = idx + len(heading)
        # Find next heading (or end)
        end = len(text_content)
        for j in range(i + 1, len(label_values)):
            nidx = text_content.find(heading_patterns[j], start)
            if nidx >= 0 and nidx < end:
                end = nidx
                break

        section = text_content[start:end]
        section = clean_text(section)
        if len(section) > 50:
            results.append({label_key: lv, "text": section[:2000]})

    return results


SIGN_ORDER = ["aries", "taurus", "gemini", "cancer", "leo", "virgo",
              "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"]
SIGN_LABELS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
               "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
PLANETS = ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]
HOUSE_LABELS = [f"{n}{'st' if n==1 else 'nd' if n==2 else 'rd' if n==3 else 'th'} House" for n in range(1, 13)]


def scrape_planet_in_sign(planet, html):
    """Extract planet-in-sign interpretations."""
    # The heading in text form is like "Sun in Aries" or "Mercury in Aries"
    cap = planet.capitalize()
    patterns = [f"{cap} in {sl}" for sl in SIGN_LABELS]
    return extract_by_heading(html, patterns, "sign", SIGN_ORDER)


def scrape_planet_in_house(planet, html):
    """Extract planet-in-house interpretations."""
    cap = planet.capitalize()
    # Try with and without "the"
    patterns = [f"{cap} in {hl}" for hl in HOUSE_LABELS]
    entries = extract_by_heading(html, patterns, "house", list(range(1, 13)))
    if len(entries) < 12:
        patterns2 = [f"{cap} in the {hl}" for hl in HOUSE_LABELS]
        entries2 = extract_by_heading(html, patterns2, "house", list(range(1, 13)))
        if len(entries2) > len(entries):
            entries = entries2
    return entries


def scrape_house_cusp(sign, html):
    """Extract house-cusp interpretations for a given sign."""
    cap = sign.capitalize()
    patterns = [f"{cap} on {hl} Cusp" for hl in HOUSE_LABELS]
    # Try shorter pattern too
    entries = extract_by_heading(html, patterns, "house", list(range(1, 13)))
    if len(entries) < 12:
        # Try alternative format: just "Sign on N House" without "Cusp"
        alt_patterns = [f"{cap} on {hl}" for hl in HOUSE_LABELS]
        alt_entries = extract_by_heading(html, alt_patterns, "house", list(range(1, 13)))
        if len(alt_entries) > len(entries):
            entries = alt_entries
    return entries


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--type", choices=["planet_in_sign", "planet_in_house", "house_cusp", "all"], default="all")
    ap.add_argument("--delay", type=float, default=0.5)
    args = ap.parse_args()

    base = "https://astrolibrary.org/interpretations"
    all_data = {}

    types = [args.type] if args.type != "all" else ["planet_in_sign", "planet_in_house", "house_cusp"]

    if "planet_in_sign" in types:
        for planet in PLANETS:
            url = f"{base}/{planet}/"
            print(f"[planet_in_sign] {url}", file=sys.stderr)
            try:
                html = fetch(url)
                entries = scrape_planet_in_sign(planet, html)
                for e in entries:
                    key = f"{planet}_{e['sign']}"
                    all_data[f"sign_{key}"] = {"type": "planet_in_sign", "planet": planet, "sign": e["sign"], "text": e["text"]}
                print(f"  -> {len(entries)} signs", file=sys.stderr)
                time.sleep(args.delay)
            except Exception as ex:
                print(f"  FAILED: {ex}", file=sys.stderr)

    if "planet_in_house" in types:
        for planet in PLANETS:
            url = f"{base}/{planet}-house/"
            print(f"[planet_in_house] {url}", file=sys.stderr)
            try:
                html = fetch(url)
                entries = scrape_planet_in_house(planet, html)
                for e in entries:
                    key = f"{planet}_{e['house']}"
                    all_data[f"house_{key}"] = {"type": "planet_in_house", "planet": planet, "house": e["house"], "text": e["text"]}
                print(f"  -> {len(entries)} houses", file=sys.stderr)
                time.sleep(args.delay)
            except Exception as ex:
                print(f"  FAILED: {ex}", file=sys.stderr)

    if "house_cusp" in types:
        for sign in SIGN_ORDER:
            url = f"{base}/{sign}-cusp/"
            print(f"[house_cusp] {url}", file=sys.stderr)
            try:
                html = fetch(url)
                entries = scrape_house_cusp(sign, html)
                for e in entries:
                    key = f"{sign}_{e['house']}"
                    all_data[f"cusp_{key}"] = {"type": "house_cusp", "sign": sign, "house": e["house"], "text": e["text"]}
                print(f"  -> {len(entries)} houses", file=sys.stderr)
                time.sleep(args.delay)
            except Exception as ex:
                print(f"  FAILED: {ex}", file=sys.stderr)

    # Output YAML
    print(yaml.dump({"entries": list(all_data.values())}, default_flow_style=False, allow_unicode=True, width=120))


if __name__ == "__main__":
    main()
