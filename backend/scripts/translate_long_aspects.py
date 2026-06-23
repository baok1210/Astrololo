"""Translate the 51 remaining long English aspect entries to Vietnamese.
Uses chunking for entries over 2000 chars."""
import sys, os, yaml, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.chdir(os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
print("Starting long entry translation...", flush=True)

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

missing = {k: v for k, v in en_data.items() if k not in vi_data and len(get_entry_text(v)) > 2000}
print(f"Remaining long entries: {len(missing)}", flush=True)

CHUNK_SIZE = 1000
translated = {}
success_count = 0
keys = list(missing.keys())

SYSTEM_PROMPT = (
    "You are an expert astrology translator. Translate English to Vietnamese.\n"
    "Planet names: Sun=Sao Mat Troi, Moon=Sao Mat Trang, Mercury=Sao Thuy, "
    "Venus=Sao Kim, Mars=Sao Hoa, Jupiter=Sao Moc, Saturn=Sao Tho, "
    "Uranus=Sao Thien Vuong, Neptune=Sao Hai Vuong, Pluto=Sao Diem Vuong\n"
    "Aspect names: conjunction=Hop, sextile=Luc Hop, square=Vuong Goc, "
    "trine=Tam Hop, opposition=Doi Xung, quincunx=Bat Xung\n"
    "Return ONLY the translated text."
)

for i, k in enumerate(keys):
    entry_text = get_entry_text(missing[k]).strip()
    total_len = len(entry_text)
    print(f"[{i+1}/{len(keys)}] {k} ({total_len} chars)...", flush=True)

    # Split into chunks
    chunks = []
    for ci in range(0, total_len, CHUNK_SIZE):
        chunks.append(entry_text[ci:ci+CHUNK_SIZE])

    translated_parts = []
    all_ok = True
    for ci, chunk in enumerate(chunks):
        context = f"Part {ci+1}/{len(chunks)} of astrological text. Translate to Vietnamese:\n\n{chunk}"
        r = ai_complete([{"role": "user", "content": context}], system_prompt=SYSTEM_PROMPT)
        if r.success and r.text.strip():
            translated_parts.append(r.text.strip())
        else:
            print(f"  Chunk {ci+1}/{len(chunks)} FAILED: {r.error}", flush=True)
            all_ok = False
            # Try once more
            time.sleep(1)
            r2 = ai_complete([{"role": "user", "content": context}], system_prompt=SYSTEM_PROMPT)
            if r2.success and r2.text.strip():
                translated_parts.append(r2.text.strip())
                all_ok = True
                print(f"  Chunk {ci+1}/{len(chunks)} OK (retry)", flush=True)
            else:
                print(f"  Chunk {ci+1}/{len(chunks)} FAILED again", flush=True)
                break
        time.sleep(0.3)

    if all_ok and translated_parts:
        full = "\n\n".join(translated_parts)
        orig = missing[k]
        if isinstance(orig, dict):
            translated[k] = {**orig, "detailed": full}
        else:
            translated[k] = full
        success_count += 1
        print(f"  OK ({len(full)} chars)", flush=True)
    else:
        # Save for manual review
        with open(f"failed_{k}.txt", "w", encoding="utf-8") as f:
            f.write(entry_text)
        print(f"  SKIPPED (saved to failed_{k}.txt)", flush=True)

    # Save every 3
    if (i + 1) % 3 == 0 or i == len(keys) - 1:
        merged = {**vi_data, **translated}
        with open(VI_PATH, "w", encoding="utf-8") as f:
            yaml.dump(merged, f, allow_unicode=True, default_flow_style=False, sort_keys=False, width=120)
        print(f"  Saved: {len(merged)} entries", flush=True)

    time.sleep(0.3)

print(f"\nDone! {success_count}/{len(keys)} long entries translated", flush=True)
