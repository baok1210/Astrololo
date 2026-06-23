import sys
sys.stdout.reconfigure(encoding='utf-8')

import scrape_astrolibrary as sa

# Test one planet in sign
html = sa.fetch('https://astrolibrary.org/interpretations/sun/')
entries = sa.scrape_planet_in_sign('sun', html)
print(f'Sun in signs: {len(entries)}/12')
for e in entries:
    print(f'  {e["sign"]}: {len(e["text"])} chars')
print()

# Test one planet in house
html2 = sa.fetch('https://astrolibrary.org/interpretations/sun-house/')
entries2 = sa.scrape_planet_in_house('sun', html2)
print(f'Sun in houses: {len(entries2)}/12')
for e in entries2:
    print(f'  H{e["house"]}: {len(e["text"])} chars')
print()

# Test one house cusp
html3 = sa.fetch('https://astrolibrary.org/interpretations/leo-cusp/')
entries3 = sa.scrape_house_cusp('leo', html3)
print(f'Leo on cusps: {len(entries3)}/12')
for e in entries3:
    print(f'  H{e["house"]}: {len(e["text"])} chars')
print()

# Show first 200 chars of one entry
if entries:
    print(f'First entry sample: {entries[0]["text"][:200]}')
