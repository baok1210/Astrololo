# CHANGELOG — Astrololo

Ghi chép các thay đổi theo từng đợt làm việc. Đẩy lên GitHub sau mỗi đợt chỉnh sửa.
Log ngôn ngữ: tiếng Việt (mô tả) + tiếng Anh (commit message).

---

## 2026-07-20 — Cross-Cutting Synthesis module (luận giải chéo)

Bổ sung lớp "abduction" mà descriptive rules thiếu — ghép các mẩu rời thành narrative có judgment (giống astrologer người thật). Mới: `cross_synthesis_rule.py` (priority 3, sau micro_synthesis).

### 6 sub-features (sau khi "làm mạnh")
- **Sign amplification**: phát hiện 2+ điểm then chốt (Mặt Trời/Cung Mọc/Thiên Đỉnh/Mặt Trăng) cùng 1 cung → "chủ đề bị khuếch đại gấp bội, SỐNG nó ở cốt lõi". (vd Lang Son: MC + Sun cùng Song Ngư.)
- **House worldly mapping**: ánh xạ đỉnh mỗi nhà sang "màu sắc thực tế" của lĩnh vực đó. **Nhà 8 (thân mật) nay có 12 reading riêng biệt** — mỗi đỉnh cung (Bạch Dương…Song Ngư) ra một flavor thực tế khác nhau (vd Song Tử = ĐA DẠNG/18+; Bọ Cạp = sâu/chiếm hữu; Kim Ngưu = sensual/trung thành; Sư Tử = nồng nhiệt/sân khấu…). Không còn fallback chung chung.
- **Contrarian nuance**: lớp "hiểu lầm vs thực tế" cho mỗi cung then chốt (vd Bọ Cạp: "sâu sắc về tâm hồn/tri thức, không chỉ tình dục bề mặt"). **Đã verify cả 12 cung Mặt Trời đều render.**
- **Tension (mới)**: phát hiện điểm kéo ngược — (a) Mặt Trời⇄Mặt Trăng (là ai vs cảm thế nào), (b) Mọc⇄Mặt Trời (mặt nạ vs cốt lõi), (c) mất cân bằng nguyên tố (vd 1 nguyên tố = 0 hành tinh → điểm mạnh + mù).
- **Life-Theme Synthesis (mới, capstone)**: gom mọi layer trên thành 1 narrative "MỘT mạch sống" đặt đầu section — phần astrologer thật làm (abduction thay vì liệt kê).

### Backend wiring
- `registry.py`: đăng ký module.
- `engine.py`: thêm `cross_synthesis` vào `section_order` (sau micro_synthesis) + `category_titles` ("Tổng Hợp Chéo (Cross-Cutting)").
- `cross_synthesis_rule.py`: thêm `_HOUSE8_VI`/`_HOUSE8_EN` (12 entry, mỗi entry có cờ diverse) → Nhà 8 luôn ra reading riêng, bất kể đỉnh cung nào.

### Verification (ad-hoc)
- **Coverage test (2026-07-20, fix theo feedback user)**: sinh 1 chart cho mỗi 12 Mặt Trời → tất cả 12 cung đều render contrarian nuance; tất cả 12 đỉnh Nhà 8 (kể cả Bọ Cạp/Kim Ngưu/Sư Tử…) đều có reading riêng biệt, không trùng, không fallback. PASS.
- Scorpio sample 1985 (ASC Song Ngư / Sun Bọ Cạp / Moon Sư Tử): kích hoạt Life-Theme capstone + 2 tension (Sun⇄Moon, Asc⇄Sun) + contrarian Bọ Cạp + 8th=Thiên Bình reading.
- Lang Son 1996: báo đúng MC+Sun cùng Song Ngư (amplification), governance Sun/Mars @ Nhà 10, contrarian Song Ngư/Nhân Mã/Song Tử.
- Chart 8th=Gemini (1992-03-20 22:00): kích hoạt note "ĐA DẠNG / 18+ / flavor khác nhau" — khớp exactly ví dụ user đưa.
- `pytest tests/` → 159 passed.

---

### Backend
- `micro_synthesis_rule.py`: sửa bug `getattr(pbody, "retrograde", False)` → `"is_retrograde"`. Trước đây field sai → Micro-Synthesis luôn báo "không retrograde" dù thực tế có R (vd Pluto 1996 = R). Nay báo đúng.
- `models/chart.py`: thêm field `definition_note` (optional) vào `BodyPosition`.
- `core/points.py`: `_calc_lilith_from_node` gán `definition_note` = "Black Moon Lilith (Mean Apogee) = North Node + 180°. Khác với True/Mean Lilith của CafeAstrology (tính từ quỹ đạo Mặt Trăng thực tế)."
- `planet_in_sign_rule.py` + `house_placement_rule.py`: append `definition_note` vào evidence / text khi body có note (Lilith).

### Verification (ad-hoc)
- Lang Son 1996-03-11 11:23: Pluto `is_retrograde=True` (speed -0.003, khớp pyswisseph + CafeAstrology R). Micro-Synthesis Pluto giờ báo "đang đi lùi (retrograde)".
- Lilith note xuất hiện trong evidence của planet_in_sign.
- `pytest tests/` → 159 passed. `py_compile` OK.

---

Nối 5 quy trình hạt nhân thành 1 narrative luận giải (khác với dump rời rạc của 3 tool): (1) hành tinh ở cung/nha, (2) tương tác góc chiếu, (3) retrograde/đã chỉnh sửa, (4) năng lượng hoàng đạo của nhà, (5) kết hợp hành tinh×cung×nhà.

### Backend
- `micro_synthesis_rule.py` (mới, priority 4): pick hành tinh chi phối + góc khắc nghiệt nhất, walk steps 1→5, evidence chips.
- `registry.py`: đăng ký rule.
- `engine.py`: thêm `micro_synthesis` vào `category_titles` + `section_order` (sau chart_shape).

### Frontend
- `InterpretationView.tsx`: SECTION_TITLES cho `micro_synthesis`.

### Verification (ad-hoc)
- DVB: micro_synthesis (Sao Thủy Nhân Mã/Nhà 1, góc Bán Lục Hợp Ceres orb 0.1°, không retrograde). `npm run build` clean.

---

## 2026-07-14 — 7-bước luận giải: Chart Shape + Node Axis + MC-IC Axis

Bám sát pipeline 7 bước chuẩn (Chart Overview → Big Three → Personal Planets → Outer → Trục đặc biệt → Aspects → Synthesis). Astrololo đã cover ~90%; bổ sung 3 mảnh thiếu để đủ.

### Backend (rules mới)
- `chart_shape_rule.py` (priority 3): tổng hợp nguyên tố/tính chất/bán cầu thành "Hình Thái Bản Đồ" (bước 1).
- `node_rule.py` (priority 9): Trục La Hầu (phát triển) – Kế Hầu (nghiệp quả), từ `node_sign` (merged vào planet_in_sign).
- `mc_ic_axis_rule.py` (priority 10): Trục MC (sự nghiệp) – IC (cội nguồn), IC = MC+180°.
- `registry.py`: đăng ký 3 rule.
- `engine.py`: thêm `chart_shape`, `node_axis`, `mc_ic_axis` vào `category_titles` + `section_order`.

### Frontend
- `InterpretationView.tsx`: SECTION_TITLES cho 3 category mới.

### Verification (ad-hoc)
- DVB: chart_shape (Đất 15/16, Thống Lĩnh 14.5/16, Đông 12/Tây 4), node_axis (La Hầu Thiên Bình/Nhà 11), mc_ic_axis (MC Xử Nữ/IC Song Ngư). `npm run build` clean.

---

## 2026-07-14 — Executive Summary (vượt Astro-Seek/Cafe/Astro.com)

Tính năng luận giải cá nhân hóa: 1 đoạn overview duy nhất nối Sun+Moon+Rising+Dominant+key aspect+top life-area thành narrative như nhà chiêm tinh viết riêng (đối nghịch với text generic rời rạc của 3 tool kia).

### Backend
- `rules/executive_summary_rule.py` (mới, priority 1): sinh `executive_summary` section, evidence chips (Sun/Moon/ASC/Dominant/key aspect).
- `registry.py`: đăng ký rule.
- `engine.py`: thêm `executive_summary` vào `category_titles` + `section_order` (đầu tiên).

### Frontend
- `InterpretationView.tsx`: SECTION_TITLES cho `executive_summary`.

### Verification (ad-hoc)
- DVB: section đầu = executive_summary, text >200 chars, evidence ≥3 chips.
- `npm run build` clean.

---

## 2026-07-14 — Chart-Linked Interpretation (bằng chứng neo chart)

Cạnh tranh Astro-Seek/Cafe/Astro.com: gắn mỗi đoạn luận giải với bằng chứng chart cụ thể (hành tinh, cung, nhà, độ, góc, orb) để người dùng khồng phải tự so chiếu.

### Backend
- `rules/base.py`: thêm `evidence: List[str]` vào `RuleResult`.
- `rules/planet_in_sign_rule.py`: neo evidence (hành tinh ở cung, nhà, độ trong cung, dignity).
- `rules/aspect_rules.py`: neo evidence (góc + 2 hành tinh, orb, nhà của mỗi hành tinh).
- `engine.py`: truyền `evidence` vào item output (`_make_section`); thêm `_fallback_evidence()` sinh evidence từ metadata khi rule khộng cung cấp (cover mọi rule, đảm bảo 100% items có chip).

### Frontend
- `InterpretationView.tsx`: render chip `📍 evidence` dưới mỗi đoạn luận giải.

### Verification (ad-hoc)
- DVB: "Sao Kim ở Thiên Bình" → evidence ['Sao Kim ở Thiên Bình','Nhà 11','Độ 20.1° trong cung','Dignity: rulership'] ✓
- "Hợp: Sao Thủy - Sao Diêm Vương" → ['Hợp mercury–pluto','Orb 2.1°','mercury: Nhà 1','pluto: Nhà 1'] ✓
- `npm run build` clean.

---

## 2026-07-14 — tra-cuu-ban-do-sao-1: Life Areas + Moon + Aspect Groups (P0–P3)

Phát triển tính năng báo cáo lá số theo chuẩn MystechX (Đoàn Việt Bảo).

### Backend
- `analysis/life_areas.py` (mới): tính **14 khía cạnh đời sống** (Công danh, Bản thân, Tình yêu, Tài chính, Chuyển hóa, Xã hội, Gia đình, Con cái, Sức khỏe, Học tập, Giao tiếp, Hôn nhân, Tiềm thức, Di chuyển) → **score 0–100** (reuse `ChartScorer`/`body_weight`/`dignity`).
- `interpretation/rules/life_area_rule.py` (mới): section "14 Khía Cạnh Cuộc Sống" (14 items + điểm + prose corpus).
- `interpretation/rules/moon_sign_rule.py` (mới): prose sâu **Mặt Trăng** (lấp gap A2).
- `interpretation/rules/aspect_group_rule.py` (mới): tách góc hợp thành 3 nhóm (nổi bật / hài hòa / thử thách) — C20–C22.
- `registry.py`: đăng ký 3 rule mới.
- `engine.py`: thêm `moon_sign`/`life_area`/`aspect_group` vào `category_titles` + `section_order`; nới limit items 5→20 cho `life_area`.

### Frontend
- `InterpretationView.tsx`: thêm `moon_sign`/`life_area`/`aspect_group`/`encyclopedia` vào `SECTION_TITLES`; render **score badge 0–100** (màu theo mức) cho `life_area`.

### Tests
- `tests/test_life_areas.py` (mới): 3 tests (count/range, engine output, career score).

### Verification (ad-hoc)
- Đoàn Việt Bảo: `moon_sign` ✓, `life_area` = 14 items (Công danh 53, Bản thân 68, Giao tiếp 83...), `aspect_group` = 3 nhóm (nổi bật 59 / hài hòa 43 / thử thách 60) → PASS.
- pytest → 159 passed (156 + 3 mới). `npm run build` clean.

---

## 2026-07-14 — Vá EN aspect fallback + Nối Frontend Predictive (Làm đi)

### (a) Vá retriever EN aspect
- `knowledge_retriever.py`: thêm `_is_index_page()` lọc trang index/nav ("aspect page", "following aspects") khỏi `_file_match` + `_best_docs`. Mở rộng `retrieve_aspect` bắt file chứa CẢ 2 hành tinh (`sun_and_moon`...).
- Audit: EN aspect fallback-ish 45/400 → 43/400 (phần còn lại là cặp asteroid/node thiếu trong corpus — giới hạn nguồn).

### (b) Nối Frontend Predictive
- `api.ts`: thêm `PredictiveResponse` type + `getProgression` / `getSolarReturn` (giữ `getTransit` nguyên).
- `PredictivePanel.tsx` (mới): 3 tab Progressed / Solar Return / Transit, form birth riêng, hiển thị qua `InterpretationView`.
- `App.tsx`: thêm tab "Tiến Trình" → render `PredictivePanel`.
- Note: backend `/progression` `/solar-return` trả nested `progression.interpretation.sections` → Panel map nested → top-level `sections`.

### Verification (ad-hoc)
- Progression VI: 17 sections; Solar Return VI: 17 sections; Progression EN có `encyclopedia` → PASS.
- `pytest` → 156 passed. `npm run build` clean (655 modules).

---

## 2026-07-14 — Tích hợp Bách Khoa Chiêm Tinh (Encyclopedia)

### Nguồn
User cung cấp văn bản chi tiết (TIẾNG VIỆT) về: loại bản đồ, cấu trúc 4 yếu tố, 12 nhà, phân vùng bán cầu, hành tinh + chỉ số độ, nguyên tố/tính chất, góc chiếu. Yêu cầu tích hợp → **Cả VI + EN** (VI làm gốc).

### Thay đổi
- `templates/vi/encyclopedia.yaml` + `templates/en/encyclopedia.yaml` — nội dung bách khoa (chart_types, structure, houses 1-12, hemispheres, planets+degree, elements/qualities, aspects).
- `encyclopedia_rule.py` (mới) — rule priority 30, luôn `matches()`, trả 1 `RuleResult` category `encyclopedia`.
- `registry.py` — đăng ký `encyclopedia_rule`.
- `engine.py` — thêm `"encyclopedia"` vào `category_titles` + `section_order` (cuối cùng).

### Verification (ad-hoc)
- Rule VI/EN: title + text>500c đúng, category=encyclopedia.
- Engine VI + EN đều có section `encyclopedia` → PASS.
- `pytest` → 156 passed.

---

## 2026-07-14 — Mở rộng KB: Synastry + Compatibility (tiếp tục)

### Thay đổi
- `knowledge_retriever.py`: thêm `retrieve_compatibility(p1, p2)` → lấy overview từ corpus `love_compatibility` (100 file).
- `synastry.py`: thêm field `compatibility_text` (EN) lấy từ corpus, trả về trong response.
- `api.ts` + `SynastryPanel.tsx`: hiển thị `compatibility_text` (EN) dưới summary.
- Fix `_sign_of` để đọc `chart.planets` (list) thay vì `.get()` (dict).

### Verification (ad-hoc)
- Synastry EN: `compatibility_text` trả prose corpus ("**Synastry** is the art of relationship astrology..."), composite present, score 37/100 (in range).
- `pytest` → 156 passed. `npm run build` clean. `benchmark` 50/50 (19/19 categories, "No issues found!").

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
