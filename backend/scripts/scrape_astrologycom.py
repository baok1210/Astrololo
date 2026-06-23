"""Scrape astrology.com for missing planet-in-sign interpretations.

Focuses on Neptune/Taurus/Gemini/Pisces and Pluto/Aries/Taurus/Capricorn/Aquarius/Pisces
which are missing from AstroLibrary.

URL pattern: https://www.astrology.com/planets/{planet}-in-{sign}
"""
import sys
import os
import time
import re
import yaml
import requests
from bs4 import BeautifulSoup

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "astrololo", "interpretation", "templates", "en")

PLANET_MAP = {
    "sun": "sun", "moon": "moon", "mercury": "mercury",
    "venus": "venus", "mars": "mars", "jupiter": "jupiter",
    "saturn": "saturn", "uranus": "uranus", "neptune": "neptune",
    "pluto": "pluto"
}

def fetch(url):
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return resp.text

def clean_text(text):
    """Clean extracted text."""
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_content(html):
    """Extract the main interpretation content from an astrology.com page."""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Try multiple content containers
    content = None
    for selector in ['main', 'article', 'div.main-content', 'div.content-wrapper']:
        content = soup.select_one(selector)
        if content:
            break
    if not content:
        content = soup
    
    # Try to find the main article body - look for section with text
    # The content is typically in <p> tags or <div> with article content
    text_parts = []
    
    # Look for the Neptune/Taurus description paragraph
    # After the h1, there's usually a description paragraph
    descriptions = soup.find_all(['p', 'div'], string=lambda s: s and len(s) > 150)
    
    # More targeted: find sections with text about the planet
    # Look for content after "Significance & Meaning" or "Personality" headings
    article_sections = []
    for tag in soup.find_all(['h1', 'h2', 'h3']):
        parent = tag.find_parent(['section', 'div'])
        section_text = tag.get_text().strip()
        article_sections.append(section_text)
        # Collect text between this heading and the next
        current = tag.find_next_sibling()
        while current and current.name not in ['h1', 'h2', 'h3']:
            txt = current.get_text().strip()
            if txt and len(txt) > 30:
                text_parts.append(txt)
            current = current.find_next_sibling()
            if current is None:
                break
    
    # Alternative: extract all meaningful paragraphs
    paragraphs = []
    for p in soup.find_all('p'):
        txt = p.get_text().strip()
        if len(txt) > 60:  # Meaningful paragraph
            paragraphs.append(txt)
    
    if paragraphs:
        return '\n\n'.join(paragraphs)
    
    # Absolute fallback: just find large text blocks
    for tag in soup.find_all(['div', 'section']):
        txt = tag.get_text().strip()
        if len(txt) > 500:
            # Check if it's likely content (not nav/footer)
            if not any(x in (tag.get('class') or []) for x in ['nav', 'footer', 'menu', 'sidebar']):
                text_parts.append(txt)
    
    return '\n\n'.join(text_parts[:5]) if text_parts else ""

def scrape_planet_in_sign(planet, sign):
    """Scrape one planet-in-sign page."""
    url = f"https://www.astrology.com/planets/{planet}-in-{sign}"
    try:
        html = fetch(url)
        text = extract_content(html)
        return text if text and len(text) > 150 else None
    except Exception as e:
        print(f"  ERROR {planet}/{sign}: {e}")
        return None

def scrape_missing():
    """Scrape missing Neptune and Pluto sign entries."""
    missing = {
        'neptune': ['taurus', 'gemini', 'pisces'],
        'pluto': ['aries', 'taurus', 'capricorn', 'aquarius', 'pisces'],
    }
    
    results = {}
    for planet, signs in missing.items():
        for sign in signs:
            print(f"Scraping {planet}/{sign}...", end=' ')
            text = scrape_planet_in_sign(planet, sign)
            if text:
                results[f"{planet}_{sign}"] = text
                print(f"OK ({len(text)} chars)")
            else:
                print("NO CONTENT")
            time.sleep(0.5)
    
    return results

def merge_into_template(results):
    """Merge scraped content into the en/planet_in_sign.yaml template."""
    path = os.path.join(TEMPLATES_DIR, "planet_in_sign.yaml")
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}
    
    added = 0
    for key, text in results.items():
        planet, sign = key.split('_', 1)
        if planet not in data:
            data[planet] = {}
        
        planet_data = data[planet]
        if sign in planet_data:
            print(f"  SKIP {planet}/{sign}: already exists")
            continue
        
        lines = text.split('\n')
        short = lines[0].strip() if lines else text[:100]
        if len(short) > 200:
            short = short[:200]
        
        planet_data[sign] = {
            "title": f"{planet.capitalize()} in {sign.capitalize()}",
            "short": short,
            "detailed": text,
            "source": "astrology.com"
        }
        print(f"  ADD {planet}/{sign}")
        added += 1
    
    if added:
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        print(f"\nAdded {added} entries to {path}")
    else:
        print("\nNo new entries added.")
    return added

if __name__ == "__main__":
    apply = "--apply" in sys.argv
    
    if apply:
        results = scrape_missing()
        if results:
            merge_into_template(results)
        print("\nDone!")
    else:
        print("Preview of what would be scraped:")
        for planet, signs in {'neptune': ['taurus', 'gemini', 'pisces'], 'pluto': ['aries', 'taurus', 'capricorn', 'aquarius', 'pisces']}.items():
            for sign in signs:
                print(f"  https://www.astrology.com/planets/{planet}-in-{sign}")
        print("\nTotal: 8 pages")
        print("Run with --apply to execute scraping.")
