# CHANGELOG — Astrololo

Ghi chép các thay đổi theo từng đợt làm việc. Đẩy lên GitHub sau mỗi đợt chỉnh sửa.
Log ngôn ngữ: tiếng Việt (mô tả) + tiếng Anh (commit message).

---

## 2026-07-14 — Tích hợp kho kiến thức crawl (KB Integration) + P0/P1

### Mục tiêu
Tích hợp kho dữ liệu `crawl kiến thức astro` (997 file .md, cafe_astrology / astrosage / astro_com / astrologyland) vào Astrololo để cải thiện chất lượng interpret EN.

### Thay đổi chính
1. **`knowledge_retriever.py`** (MỚI) — retriever nhẹ over corpus:
   - Index 946 file theo normalized filename key + category.
   - Match ưu tiên **tên file chính xác** (`mars_in_scorpio`, `jupiter_in_eighth_house`), fallback scoring theo category/subcategory + token overlap.
   - Lọc rác: bảng, nav menu, link-only line, dòng non-latin (Tamil/Telugu), dòng liệt kê 12 cung, "click here/read more".
   - Ưu tiên nguồn: cafe_astrology (3.0) > astro_com (2.5) > astrologyland (2.0) > astrosage (1.0).
   - Bật bằng env `ASTRO_KB_MARKDOWN` (mặc định đường dẫn corpus local).
2. **`template_loader.py`** — 3 nhánh EN (`get_planet_in_sign` / `get_planet_in_house` / `get_aspect`) giờ chạy theo thứ tự:
   curated EN YAML → **baked YAML** → live retriever → keyword fallback. VI hoàn toàn không bị động.
3. **`scripts/import_crawl_kb.py`** (MỚI) — bake corpus thành YAML bền vững:
   - `planet_in_sign_baked.yaml` (216 entry), `planet_in_house_baked.yaml` (216), `aspects_baked.yaml` (1376).
   - Chạy: `python scripts/import_crawl_kb.py` (PYTHONPATH=backend).
4. **Bug fix `synthesis_rules.py`** — guard `ht`/`h` trước `.type_` (composite house ngoài 1–12 gây crash → composite bị `None`).
5. **P0/P1 trước đó** (cùng đợt): dominant-planet weighting (`scoring.py` BODY_WEIGHT), `compatibility_score` synastry (ratio-based), endpoint `/api/v1/daily` + `create_daily()`, geocoding UI (NatalPanel), Composite tab (SynastryPanel), ephemeris asteroids Keplerian fallback + fix đơn vị (`centuries = t/100.0`).

### Verification (ad-hoc, không chỉ suite)
- Retriever: 5/5 query trả prose đúng (sun/aries, mars/scorpio, jupiter/h2, saturn/h10, sun conjunct moon).
- Baked YAML load **khi tắt corpus** (durable): EN vẫn có prose, VI nguyên vẹn.
- `pytest tests/ -q` → **156 passed**.
- `npm run build` → clean (654 modules).

### Lưu ý
- Corpus là EN; nhánh VI vẫn dùng template VI có sẵn. Dùng nội bộ cá nhân (bản quyền cafeastrology/astro.com cấm thương mại).

---

## 2026-07-14 — Phase B: Essential Dignities (Triplicity/Term/Face)
- Thêm điểm dignities (rulership/exaltation/detriment/fall + triplicity/term/face) vào `dignity_rules.py`.
- Commit: `feat: Add Triplicity/Term/Face essential dignities (Phase B)`.

---

## Quy tắc
- Sau mỗi đợt: update CHANGELOG.md → `git add` → `git commit` → `git push origin master`.
- Không commit secret/token. Code KISS/DRY, match style repo.
