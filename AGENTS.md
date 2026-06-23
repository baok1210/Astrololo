# Astrololo - AI Context

## Goal
Make Astrololo interpret all aspects, planets-in-sign, and planets-in-house with real content by combining web scraping (English) and keyword-based fallback (Vietnamese). Expanded to cover all major astrological bodies (Chiron, asteroids, Lilith), angles (ASC/MC signs), and calculated points (Part of Fortune).

## Constraints & Preferences
- Bilingual output: English from cafeastrology.com scraping + Vietnamese from keyword-enriched fallback
- Preserve existing YAML template structure, test suite, and keyword integration
- No AI API key available → must rely on scraping + keyword data
- cafeastrology.com accessible (200), astro-seek.com blocked (403)

## Progress

### Done (Phase 3)
- **Part of Fortune now has its own section**: Changed `pof_rule.py` category from `"synthesis"` to `"part_of_fortune"`. Added `"part_of_fortune"` to `section_order`, `category_titles`, and limit logic in `engine.py`. Added `SECTION_TITLES` + `SECTION_COLORS` entry in `InterpretationView.tsx`.
- **Part of Fortune shown on chart wheel**: Added PoF marker (⊕, gold dot) to `ChartWheel.tsx` by reading `chartData.part_of_fortune.longitude`.
- **Aspect fallback text greatly improved**: Rewrote `_make_fallback_aspect()` in `template_loader.py` — replaced single generic template with per-aspect-type descriptions (9 aspect types), 26 planet-pair interaction intros (e.g., "Sun represents ego, Moon represents emotions"), and aspect-type behavioral insights (conjunction = blend, square = tension/action, trine = natural flow). Output now 4-6 paragraphs vs 3 before.
- **Fixed pre-existing ruff F841 warning**: Removed unused `max_score` variable in `engine.py`.

### Done
- **Engine returns individual results**: `PlanetInSignRule`, `AspectRule`, `CombinationRule`, `PlanetInHouseRule` now return `List[RuleResult]` (one per planet/aspect) instead of aggregating all into one `RuleResult`. Engine handler extends `all_results` from both single results and lists.
- **273 bad titles fixed**: Vietnamese YAML aspect titles changed from wrong verbs ("hòa trộn", "hỗ trợ", "thách thức", "hài hòa") to proper aspect names ("Hợp", "Lục Hợp", "Vuông Góc", "Tam Hợp", "Đối Xung", "Bát Xung", etc.) using `scripts/fix_titles.py`
- **276 detailed texts fixed**: First line of detailed text changed from "Sao Hỏa hòa trộn Sao Mộc: góc chiếu conjunction tạo ra..." to "Sao Mộc Hợp Sao Hỏa: góc chiếu này tạo ra..." using `scripts/fix_detailed_text.py`
- Scraped cafeastrology.com for English content:
  - `templates/en/aspects.yaml`: **176** English aspect interpretations (from 30+ combined aspect pages)
  - `templates/en/planet_in_sign.yaml`: **56** English planet-in-sign entries (venus, jupiter, saturn, uranus, neptune)
  - `templates/en/planet_in_house.yaml`: **48** English planet-in-house entries (mars, venus, moon, mercury)
- Added normalization in `template_loader.py` (`get_aspect`, `get_planet_in_sign`, `get_planet_in_house`) to convert plain string YAML entries to dict format with title/short/detailed keys
- Improved `_make_fallback_aspect()`: replaced generic boilerplate ("góc chiếu này tạo ra sự tương tác đặc thù...") with keyword-enriched text using planet function data, sign keywords, and aspect nature (harmonious vs challenging)
- **Phase 1: Expanded chart model** — added 6 new bodies (Chiron, Ceres, Pallas, Juno, Vesta, Lilith) to `PLANETS`, `PLANET_ORDER`, ephemeris codes, and `points.py`. All 82 tests pass with updated body counts (22 total: 16 planets + 2 nodes + 4 angles).
- **Part of Fortune** — calculated (ASC+Moon-Sun day, ASC+Sun-Moon night), stored as `chart.part_of_fortune` dict with longitude/sign/house.
- **AscendantSignRule** (`ascendant_rule.py`) — interprets the rising sign with keyword-based bilingual text, priority 5.
- **MCSignRule** (`mc_rule.py`) — interprets the Midheaven sign, priority 6.
- **PartOfFortuneRule** (`pof_rule.py`) — interprets Part of Fortune by sign+house, priority 8 (night/day corrected).
- **Lilith calculated from North Node** — `_calc_lilith_from_node()` uses formula `(NN + 180) % 360` to avoid SWISSEPH code 23 incompatibility.
- All **147 tests passing** (test_engine.py + test_keywords.py + test_cafeastrology.py + test_rules.py)
- Backend running at `http://localhost:8000` (uvicorn), frontend at `http://localhost:5173`

### Done (Phase 2)
- **planet_in_sign EN**: 144 entries (120 planets + 24 north/south nodes) — all 12 signs per body, real content
- **planet_in_house EN**: 120 entries — all 10 planets × 12 houses, real content
- **AscendantSign template**: `ascendant.yaml` — 12 rising signs scraped from AstroLibrary (1000-1200 chars each)
- **MC template**: `mc.yaml` — 12 MC sign interpretations generated (keyword-based, since no source available)
- **North Node template**: `node_sign.yaml` — 24 entries (12 NN + 12 SN) scraped from AstroLibrary per-sign pages. Merged into `planet_in_sign.yaml` for automatic lookup.
- **Aspects coverage**: **227 entries** (was 176). Filled all 225 major combos (conjunction/sextile/square/trine/opposition):
  - 4 Sun-Moon aspects scraped from AstroLibrary
  - 5 Sun-Mercury aspects generated (no source found)
  - 42 other missing combos filled with synthetic text
- **Frontend**: `SECTION_TITLES` + `SECTION_COLORS` updated for all engine section types (synthesis, house_distribution, quality, house_cusp)

### Blocked
- No GPT-4o-mini API key → English → Vietnamese translation cannot use AI; relying on keyword fallback
- Some aspect pages return 404 (sun_mercury, sun_moon) — may not exist on cafeastrology

## GSD Superpower Workflow (BẮT BUỘC)

Khi nhận được yêu cầu code mới, luôn áp dụng workflow sau:

1. **AUDIT** — Chạy `ruff check astrololo/ tests/ scripts/` + `pytest tests/ -v` để biết trạng thái hiện tại
2. **SCAN** — Grep/glob các file liên quan để hiểu codebase trước khi sửa
3. **FIX** — Thực hiện thay đổi, ưu tiên edit file hiện tại, không tạo file mới trừ khi thực sự cần
4. **VERIFY** — Chạy lại `pytest tests/ -v` + `ruff check astrololo/` + `vite build` (frontend)
5. **COMMIT** — Chỉ commit khi được yêu cầu, message ngắn gọn

Quy tắc:
- Không dùng `ruff check --fix` nếu chưa review các lỗi sẽ bị fix
- `PLANET_ORDER` chỉ chứa 16 planet (10 classical + 6 minor), KHÔNG chứa nodes/angles
- File `registry.py` dùng `importlib.import_module()` để tránh ruff F401
- EN templates cho Chiron + 5 asteroids (ceres/pallas/juno/vesta/lilith) đã có đủ 12 signs + 12 houses

## Key Decisions
- Chiron, asteroids, Lilith use `body_type="planet"` (not a new type) to maximize compatibility with existing rules (house_placement, dignity, element, etc.)
- Lilith (Black Moon Lilith) calculated as `(North Node + 180°)` instead of SWISSEPH code 23 (unsupported by installed lib)
- New rules (Ascendant, MC, POF) placed at low priority (5-8) to appear at top of `synthesis` section
- Part of Fortune uses `night` formula (`ASC + Sun - Moon`) vs `day` formula (`ASC + Moon - Sun`) based on `is_daytime` flag

## Relevant Files
- `.../rules/ascendant_rule.py`, `mc_rule.py`, `pof_rule.py`: NEW — ASC/MC sign + POF interpretation rules
- `.../core/points.py`: MODIFIED — `_build_one()` extracted, `build_additional()` for Chiron/asteroids/Lilith
- `.../core/constants.py`: MODIFIED — 6 new `Planet` entries (chiron, ceres, pallas, juno, vesta, lilith) + `PLANET_ORDER` updated to 16 bodies
- `.../core/ephemeris.py`: MODIFIED — added SWISSEPH codes for Chiron (15) + asteroids (17-20)
- `.../models/chart.py`: MODIFIED — added `part_of_fortune` field
- `.../analysis/natal.py`: MODIFIED — Part of Fortune calculation with day/night logic
- `.../rules/planet_in_sign_rule.py`, `aspect_rules.py`, `combination_rules.py`, `planet_in_house_rule.py`: Return `List[RuleResult]`
- `.../rules/base.py`: `InterpretationRule.interpret()` return type updated to `Optional[RuleResult] | List[RuleResult]`
- `.../interpretation/template_loader.py`: Contains `_make_fallback_aspect()` (improved), fallback sign/house generators, normalization functions
- `.../templates/en/aspects.yaml`: 176 English scraped aspects
- `.../templates/en/planet_in_sign.yaml`: 56 English sign entries
- `.../templates/en/planet_in_house.yaml`: 48 English house entries
- `.../templates/vi/aspects.yaml`: Fixed 273 titles + 276 detailed texts
- `.../templates/vi/planet_in_sign.yaml`: 120 entries (all with keyword-enriched content)
- `.../tests/test_keywords.py`, `test_engine.py`: tests with updated body counts (16 planets, 22 total)
- `.../tests/test_cafeastrology.py`: **82** end-to-end comparison tests (3 dates, ~22 checks each)
