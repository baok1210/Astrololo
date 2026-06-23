"""Clean 77 VI aspect entries with translation artifacts via LLM."""
import io, re, sys, yaml, time, logging
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from astrololo.interpretation.ai_provider import ai_complete

ASPECTS_VI = Path(__file__).resolve().parent.parent / "astrololo" / "interpretation" / "templates" / "vi" / "aspects.yaml"

ARTIFACT_RE = re.compile(r'Phần \d+/\d+ của văn bản chiêm tinh( học)?\.? Dịch sang tiếng Việt:')

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

PROMPT_TMPL = """Sau đây là một đoạn luận giải chiêm tinh tiếng Việt bị lỗi do dịch thuật máy: nó bị chia cắt bởi các header "Phần X/Y của văn bản chiêm tinh học. Dịch sang tiếng Việt:". Nhiệm vụ của bạn: gộp các mảnh lại thành một đoạn văn trôi chảy, tự nhiên, loại bỏ hoàn toàn các header dịch thuật. VIẾT BẰNG TIẾNG VIỆT. Chỉ trả về đoạn văn đã gộp, không thêm giải thích.

Nội dung lỗi:
---
{content}
---"""

def clean_entry(content: str) -> str | None:
    r = ai_complete([{"role": "user", "content": PROMPT_TMPL.format(content=content[:2000])}],
                    system_prompt="Bạn là chuyên gia chiêm tinh, viết tiếng Việt tự nhiên.")
    if r.success and r.text.strip():
        return r.text.strip()
    logging.warning(f"LLM failed: {r.error}")
    return None

def main():
    with open(ASPECTS_VI, encoding="utf-8") as f:
        raw = f.read()

    # Find all entries with artifacts
    affected_keys = []
    current_key = None
    for line in raw.splitlines():
        m = re.match(r'^([a-z_]+[a-z]):', line)
        if m:
            current_key = m.group(1)
        if ARTIFACT_RE.search(line):
            if current_key:
                affected_keys.append(current_key)

    # Deduplicate and count
    affected_keys = list(dict.fromkeys(affected_keys))
    logging.info(f"Found {len(affected_keys)} entries with artifacts")

    # Load YAML
    data = yaml.safe_load(raw)
    entries = list(data.items()) if data else []
    logging.info(f"Total entries: {len(entries)}")

    cleaned = 0
    for key, entry in entries:
        if key not in affected_keys:
            continue
        if isinstance(entry, str):
            content = entry
        elif isinstance(entry, dict):
            content = entry.get("detailed", entry.get("text", ""))
        else:
            continue

        if not content or not ARTIFACT_RE.search(content):
            continue

        cleaned_text = clean_entry(content)
        if cleaned_text:
            if isinstance(entry, str):
                data[key] = cleaned_text
            elif isinstance(entry, dict):
                if "detailed" in entry:
                    data[key]["detailed"] = cleaned_text
                else:
                    data[key]["text"] = cleaned_text
            cleaned += 1
            logging.info(f"  [{cleaned}] Cleaned: {key}")
        else:
            logging.warning(f"  Skipped: {key}")
        time.sleep(0.5)  # rate limit

    # Write back
    with open(ASPECTS_VI, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False, width=120)

    logging.info(f"\nDone: {cleaned}/{len(affected_keys)} entries cleaned")

if __name__ == "__main__":
    main()
