"""Translate English aspect entries to Vietnamese via LLM, one at a time.
Skips entries over 2000 chars (too long for the model)."""
import sys, os, yaml, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.chdir(os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
print("Starting...", flush=True)

from astrololo.interpretation.ai_provider import ai_complete

EN_PATH = "astrololo/interpretation/templates/en/aspects.yaml"
VI_PATH = "astrololo/interpretation/templates/vi/aspects.yaml"

with open(EN_PATH, "r", encoding="utf-8") as f:
    en_data = yaml.safe_load(f)
with open(VI_PATH, "r", encoding="utf-8") as f:
    vi_data = yaml.safe_load(f) or {}

def get_entry_text(entry):
    if isinstance(entry, str):
        return entry
    if isinstance(entry, dict):
        return entry.get("detailed") or entry.get("text") or entry.get("short", "")
    return str(entry)

MAX_LEN = 2000  # skip entries longer than this

to_translate = {k: v for k, v in en_data.items() if k not in vi_data}
short_entries = {k: v for k, v in to_translate.items() if len(get_entry_text(v)) <= MAX_LEN}
long_entries = {k: v for k, v in to_translate.items() if len(get_entry_text(v)) > MAX_LEN}

print(f"Total EN: {len(en_data)}", flush=True)
print(f"Already in VI: {len(vi_data)}", flush=True)
print(f"To translate: {len(to_translate)}", flush=True)
print(f"Short (<={MAX_LEN} chars): {len(short_entries)}", flush=True)
print(f"Long (>{MAX_LEN} chars): {len(long_entries)}", flush=True)

SYSTEM_PROMPT = (
    "You are an expert astrology translator. Translate English to Vietnamese.\n"
    "Planet names: Sun=Sao Mat Troi, Moon=Sao Mat Trang, Mercury=Sao Thuy, "
    "Venus=Sao Kim, Mars=Sao Hoa, Jupiter=Sao Moc, Saturn=Sao Tho, "
    "Uranus=Sao Thien Vuong, Neptune=Sao Hai Vuong, Pluto=Sao Diem Vuong\n"
    "Aspect names: conjunction=Hop, sextile=Luc Hop, square=Vuong Goc, "
    "trine=Tam Hop, opposition=Doi Xung, quincunx=Bat Xung\n"
    "Return ONLY the translated text, no JSON, no markdown."
)

keys = list(short_entries.keys())
translated = {}
success_count = 0

for i, k in enumerate(keys):
    entry_text = get_entry_text(short_entries[k]).strip()
    if not entry_text or len(entry_text) < 5:
        print(f"[{i+1}/{len(keys)}] SKIP: {k} (too short)", flush=True)
        continue

    user_msg = f"Translate this to Vietnamese:\n\n{entry_text}"
    r = ai_complete([{"role": "user", "content": user_msg}], system_prompt=SYSTEM_PROMPT)

    if r.success and r.text.strip():
        orig = short_entries[k]
        if isinstance(orig, dict):
            translated[k] = {**orig, "detailed": r.text.strip()}
        else:
            translated[k] = r.text.strip()
        success_count += 1
        print(f"[{i+1}/{len(keys)}] OK: {k} ({len(r.text)} chars)", flush=True)
    else:
        print(f"[{i+1}/{len(keys)}] FAIL: {k} - {r.error}", flush=True)

    # Save progress every 10 entries
    if (i + 1) % 10 == 0 or i == len(keys) - 1:
        merged = {**vi_data, **translated}
        with open(VI_PATH, "w", encoding="utf-8") as f:
            yaml.dump(merged, f, allow_unicode=True, default_flow_style=False, sort_keys=False, width=120)
        print(f"  Saved: {len(vi_data) + len(translated)} entries total", flush=True)

    time.sleep(0.3)

# Write long entries list to file
if long_entries:
    with open("long_entries_remaining.txt", "w", encoding="utf-8") as f:
        for k, v in long_entries.items():
            f.write(f"{k}: {len(get_entry_text(v))} chars\n")
    print(f"Long entries ({len(long_entries)}) written to long_entries_remaining.txt", flush=True)

print(f"\nDone! {success_count}/{len(keys)} short entries translated", flush=True)
print(f"{len(long_entries)} long entries saved to long_entries_remaining.txt", flush=True)
