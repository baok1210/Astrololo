# Astrololo — Kiến trúc Luận Giải Chiêm Tinh (Astrology Synthesis Engine Spec)

## 1. Tổng quan Sản phẩm

**Tên:** Astrololo  
**Loại:** Công cụ luận giải chiêm tinh học dựa trên bản đồ sao sinh (natal chart)  
**Đầu vào chính:** Ngày, giờ, tháng, năm, tọa độ sinh của người dùng  
**Ngôn ngữ chính:** Tiếng Việt, có hỗ trợ tiếng Anh cho dữ liệu curated  
**Repo:** `C:\Users\BabaBun\Downloads\Astrololo\Astrololo`  
**Backend:** Python 3.11+, FastAPI, pyswisseph  
**Frontend:** React + TypeScript + Vite  

### 1.1 Giá trị cốt lõi
Astrololo không chỉ liệt kê vị trí các hành tinh. Nó phân tích, tổng hợp và suy luận logic qua nhiều lớp của bản đồ sao, giống như một nhà chiêm tinh thực thụ đọc bản đồ — không phải máy móc "A ở B → text".

### 1.2 Vấn đề thị trường
Các tool hiện có (Astrodienst, CafeAstrology, AstroSeek) chủ yếu là lookup engine:
- Hành tinh ở cung → văn bản cố định
- Hành tinh ở nhà → văn bản cố định
- Góc chiếu đơn lẻ → văn bản cố định

Kết quả: danh sách đoạn rời rạc, không có liên kết với nhau, đọc xong không biết người này là ai.

### 1.3 Điểm khác biệt của Astrololo
Astrolalo đọc bản đồ theo 4 lớp:
1. **Mapping** — Mọi thứ ở đâu? (vị trí, góc chiếu, phẩm chất)
2. **Weighing** — Cái nào mạnh? Cái nào nhấn mạnh? (phân điểm trọng số)
3. **Synthesizing** — Các yếu tố này tương tác thế nào? (phân tích chéo)
4. **Narrating** — Kể câu chuyện của người đó bằng văn xuôi liên tục, không bullet list.

### 1.4 Personas
- `User` — nhập dữ liệu sinh, đọc luận giải bản đồ sao.
- `Astrologer Reviewer` — kiểm tra độ chính xác chiêm tinh học.
- `Developer` — mở rộng rules/templates mà không sửa core engine.

---

## 2. Kiến trúc Hệ thống (AS-IS)

```
frontend/
  src/                        # React/TS/Vite client

backend/
  astrololo/
    api/main.py               # FastAPI router
    core/
      ephemeris.py            # Swiss Ephemeris + pure-Python fallback
      aspects.py              # Aspect detection + orb handling
      houses.py               # House cusps + system selection
      points.py               # Planets, nodes, angles, calculated points
      constants.py            # Planet/sign/aspect dictionaries
    models/
      subject.py              # AstrologicalSubject
      chart.py                # Chart model + interpretation contract
    interpretation/
      engine.py               # Rule engine main loop
      template_loader.py      # EN/VI YAML templates + normalization
      keywords.py             # VI keyword fallback
      knowledge_base.py       # Scraped KB corpus loader
      knowledge_retriever.py  # Markdown KB retriever
      ai_engine.py            # Optional LLM layer (fallback only)
      ai_provider.py          # OpenAI + Ollama abstraction
      rules/
        registry.py
        planet_in_sign_rule.py
        planet_in_house_rule.py
        aspect_rules.py
        aspect_group_rule.py
        aspect_synthesis_rule.py
        combination_rules.py
        house_placement_rule.py
        house_cusp_rule.py
        ascendant_rule.py
        mc_rule.py
        node_rule.py
        pof_rule.py
        sun_moon_rule.py
        dignity_rules.py
        dispositor_rules.py
        element_rules.py
        house_distribution_rule.py
        hemisphere_rule.py
        aspect_pattern_rule.py
        chart_shape_rule.py
        moon_phase_rule.py
        retrograde_rule.py
        fixed_star_rule.py
        midpoint_rule.py
        strength_weakness_rule.py
        executive_summary_rule.py
        life_area_rule.py
        karmic_psych_rule.py
        synthesis_rules.py
        cross_synthesis_rule.py
```

---

## 3. Quy trình Luận giải 5 Bước (Pipeline Architecture)

### Bước 1 — Input Validation Gate
Kiểm tra tính đầy đủ của tham số đầu vào:
- Ngày, giờ, tháng, năm phải hợp lệ.
- Tọa độ phải trong range: latitude [-90, 90], longitude [-180, 180].
- Timezone string phải khớp với tệp `zoneinfo`.

Nếu thiếu hoặc invalid → trả về HTTP 422 với message rõ ràng.

**Output:** Validated Chart Data

### Bước 2 — Primary Mapping
Phân cấp dữ liệu thành 3 tầng:
- **Tầng 1 (Cốt lõi):** Cung Mọc (ASC), Mặt Trời, Mặt Trăng.
- **Tầng 2 (Phổ che):** 10 Hành tinh chính, 12 Cung, 12 Nhà.
- **Tầng 3 (Chi tiết):** Góc chiếu (aspects), phẩm chất (dignities).

**Output:** Structured Chart Matrix

### Bước 3 — Matrix Evaluation
Tính điểm trọng số $W$ cho từng hành tinh:

$$
W = \text{Base Value} \times \text{Dignity Multiplier} \times \text{House Weight}
$$

| Tham số | Giá trị |
|---|---|
| **Base Value** | Sun/Moon/ASC Ruler = 1.5; Mercury/Venus/Mars = 1.2; Jupiter/Saturn = 1.0; Uranus/Neptune/Pluto = 0.8 |
| **Dignity Multiplier** | Domicile/Exaltation = 1.3; Peregrine = 1.0; Detriment/Fall = 0.7 |
| **House Weight** | Angular (1,4,7,10) = 1.4; Succeedent (2,5,8,11) = 1.1; Cadent (3,6,9,12) = 0.8 |

Lập ma trận góc chiếu so sánh lực $W_A$ vs $W_B$.

**Output:** Planet Weight Matrix

### Bước 4 — Cross-Reference
Đối chiếu liên kết giữa các Nhà qua Chủ nhà (House Rulers) và phủ dữ liệu biến đổi theo thời gian:
- House Ruler là hành tinh cai quản cung mốc của nhà đó.
- Nếu House Ruler của nhà 10 là Mars, thì Mars phải được đọc kết hợp với nhà 10.
- Xác định chuỗi Dispositor (đơn, hỗn, thừa kế).

**Output:** Context-Linked Map

### Bước 5 — Synthesis Output
Chuyển đổi ma trận logic thành văn bản luận giải dạng văn xuôi liên tục, kèm Traceability Block để kiểm chứng minh bạch.

**Output:** Final Narrative Report

---

## 4. Thuật toán Tính Trọng số Năng lượng ($W$)

Công thức chính thức:

$$W = \text{Base} \times \text{Dignity} \times \text{House}$$

### 4.1 Base Value
- **1.5:** Sun, Moon, ASC Ruler
- **1.2:** Mercury, Venus, Mars
- **1.0:** Jupiter, Saturn
- **0.8:** Uranus, Neptune, Pluto
- **1.3:** Chiron (tiêu chuẩn áp dụng cho asteroids theo body_type="planet")

### 4.2 Dignity Multiplier
Tính từ ephemeris/essential dignity rules:
- **1.3:** Domicile, Exaltation
- **1.0:** Peregrine
- **0.7:** Detriment, Fall

### 4.3 House Weight
- **1.4:** Angular: 1, 4, 7, 10
- **1.1:** Succeedent: 2, 5, 8, 11
- **0.8:** Cadent: 3, 6, 9, 12

### 4.4 Ví dụ tính toán
- Mars tại Aries, nhà 10 (angular), domicile:  
  $W = 1.2 \times 1.3 \times 1.4 = 2.184$ → **hành tinh mạnh**
- Moon tại Capricorn, nhà 3 (cadent), detriment:  
  $W = 1.5 \times 0.7 \times 0.8 = 0.84$ → **hành tinh yếu**

---

## 5. Quy tắc Tham chiếu Chéo & Xử lý Xung đột

### 5.1 Cấu trúc Rule Bắt buộc
Mỗi quy tắc luận giải phải có 3 thành phần:

```
INPUTS READ  →  LOGIC ANALYSIS  →  NARRATIVE LINK
```

- **Inputs Read:** liệt kê tất cả dữ liệu từ chart object mà rule này sử dụng.
- **Logic Analysis:** giải thích cách rule phân tích mối quan hệ giữa các inputs.
- **Narrative Link:** viết văn bản luận giải liên kết.

### 5.2 Cơ chế so sánh lực $W_A$ vs $W_B$

| Điều kiện | Kết quả |
|---|---|
| NẾU $W_A > W_B$ | Tính chất của A chi phối và định hình biểu hiện của B |
| NẾU $W_A < W_B$ | Tính chất của A bị B kiềm chế, áp đặt hoặc tạo rào cản |
| NẾU $W_A \approx W_B$ | Cả hai cân bằng: nội bộ xung đột, biểu hiện phụ thuộc ngữ cảnh |

### 5.3 Nguyên tắc Cấm tuyệt đối
- **Cấm** mô hình ánh xạ 1-1 cố định. VD: Mars in Aries → "Bạn là người hành động nhanh nhẹn" là KHÔNG ĐƯỢC.
- **Cấm** output là danh sách bullet points trong phần Narrative.
- **Cấm** dùng ngôn từ tiên đoán tuyệt đối: "bạn sẽ...", "định mệnh...", "chắc chắn...".
- **Bắt buộc** dùng từ xác suất: "có thể", "thường", "xu hướng", "có khả năng".

### 5.4 Ví dụ Luận giải Đúng/Sai

**SAI (lookup engine):**
```
Mars in Aries: Bạn có năng lượng hành động mạnh mẽ.
Mars Square Saturn: Bạn cảm thấy bị kìm hãm.
```

**ĐÚNG (synthesis engine):**
```
Mars tại Bạch Dương, cung 10, chủ nhà của cung mốc thứ 10 này đang ở
vị trí cực mạnh với trọng số 2.18. Tuy nhiên, góc vuông từ Sao Thổ tại
Ma Kết lại đặt áp lực từ môi trường bên ngoài lên tham vọng này. Bạn có
xu hướng khởi nghiệp nhanh, nhưng thường phải đối mặt với trách nhiệm
nặng nề hoặc sự kiềm chế từ cấp trên trước khi đạt được địa vị mong muốn.
Tình trạng này dễ gây nên cảm giác "đi chậm lại để đi vững vàng" — không
phải vì thiếu năng lượng, mà vì cấu trúc bên ngoài yêu cầu bạn xây dựng
nền móng trước khi bứt phá.
```

---

## 6. Chuẩn Định dạng Đầu ra (Output Standard)

### 6.1 Cấu trúc Báo cáo

Mỗi section trong báo cáo có cấu trúc:

```json
{
  "traceability": {
    "inputs_read": ["planet:Mars", "house:10", "aspect:Mars_Square_Saturn"],
    "logic_rules": ["WEIGHT_GREATER", "PATTERN_OVERRIDE"]
  },
  "narrative": "Văn bản luận giải văn xuôi liên tục...",
  "priority": 1
}
```

Trong JSON API response, `narrative` là text thường; `traceability` chỉ có mặt ở internal hoặc debug mode.

### 6.2 Ràng buộc Văn phong & Định dạng (Guardrails)

| Ràng buộc | Chi tiết |
|---|---|
| **Định dạng** | HOÀN TOÀN văn xuôi liên tục (Continuous Prose). Không danh sách số đếm, không gạch đầu dòng, không bảng biểu trong phần Narrative. |
| **Ngôi xưng** | Xưng "bạn". Tránh trung tính xa cách "người sở hữu...", "cá nhân này...". |
| **Độ tin cậy** | Bắt buộc dùng từ xác suất/khả năng: "có thể", "thường", "xu hướng", "có khả năng". |
| **Cấm** | Ngôn từ khẳng định định mệnh, giáo điều, tiên đoán tuyệt đối như "sẽ", "chắc chắn", "định mệnh", "mệnh". |
| **Độ dài** | Mỗi section 150-400 từ. Phần tổng hợp executive summary 300-600 từ. |
| **Tone** | Trung lập, giải thích, tôn trọng. Không phán xét. Không áp đặt. |

---

## 7. Kiến trúc Luận giải Chi tiết

### 7.1 Layer 1 — Placement Accuracy (Độ chính xác vị trí)
- Lấy dữ liệu từ Swiss Ephemeris hoặc fallback.
- Ánh xạ mỗi hành tinh/điểm: longitude → cung → nhà → retrograde/speed.
- Không có "poetic license" mâu thuẫn với dữ liệu ephemeris.

### 7.2 Layer 2 — Dignity & Strength Analysis (Phân tích phẩm chất và lực)
Mỗi hành tinh có score $W$ theo công thức Section 4.
- Output: bảng "Điểm mạnh / Điểm yếu" cho từng hành tinh.
- Không chỉ liệt kê; phải so sánh $W$ giữa các hành tinh để xác định bản đồ nghiêng về đâu.

### 7.3 Layer 3 — Pattern Recognition (Nhận diện mô hình)
Các mô hình phải được phát hiện tự động:
- Grand Trine, T-Square, Grand Cross, Yod, Kite, Mystic Rectangle
- Stellium
- Dispositor Chain (đơn, hỗn, mutual reception)
- Emphasize: Angular vs Cadent, Hemisphere imbalance, Element imbalance

**Rule quan trọng:** Mô hình phải override các individual placements. Stellium ở một cung thay đổi cách đọc từng hành tinh trong cung đó.

### 7.4 Layer 4 — Aspect Synthesis (Tổng hợp góc chiếu)
Khi đọc góc vuông Mars-Saturn:
- Xác định $W_Mars$ vs $W_Saturn$.
- Nếu $W_{Mars} > W_{Saturn}$: Mars chi phối — hành động tạo ra kết cấu.
- Nếu $W_{Mars} < W_{Saturn}$: Saturn chi phối — hành động bị kiềm chế.
- Đồng thời: Mars ở cung gì? Nhà nào? Bị ảnh hưởng bởi góc nào khác?
- Output: một đoạn văn kết nối tất cả yếu tố trên.

### 7.5 Layer 5 — Cross-Cutting Narrative (Luận giải chéo theo chủ đề)
Gom tất cả yếu tố vào các chủ đề lớn:
- **Nội lực:** Sun, Moon, ASC, Mars, 1st house ruler.
- **Công danh:** MC, 10th house ruler, Saturn, planets in 10th.
- **Tình duyên:** Venus, Mars, 7th house, Moon, ASC/DSC axis.
- **Xung đột nội tâm:** T-Square, oppositions, dignity conflicts.

### 7.6 Layer 6 — Executive Summary (Tổng kết)
Một narrative 300-600 từ, có thể đọc như một bài luận ngắn về người này. Không bullet points. Kể câu chuyện của họ, không liệt kê vị trí.

---

## 8. API Contract

Base URL: `/api/v1`

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/` | Service/version ping |
| `GET` | `/health` | Swiss Ephemeris + AI config + status |
| `POST` | `/natal` | Compute natal chart from input fields |
| `POST` | `/interpret` | Generate full interpretation for the chart |
| `POST` | `/interpret/ai` | Optional AI-enhanced interpretation |
| `POST` | `/transit` | Transit chart for target date |
| `POST` | `/synastry` | Partner compatibility + composite |
| `POST` | `/progression` | Secondary progressions (day-for-year) |
| `POST` | `/solar-return` | Solar return chart |
| `POST` | `/export/pdf` | Multi-page PDF report |
| `GET` | `/constants` | Planets, signs, aspects, houses metadata |
| `GET` | `/keywords` | VI keyword library |

### 8.1 Request Shape (ChartRequest)
```
name: str
year: int, month: int, day: int
hour: int, minute: int
latitude: float, longitude: float
timezone_str: str
house_system: str (placidus|koch|equal|whole_sign|regiomontanus|campanus|porphyry)
node_type: str (mean|true)
lang: str (vi|en)
esoteric: bool
zodiac_type: str (tropical|sidereal)
ayanamsa: str (lahiri|raman|krishnamurti)
include_minor_aspects: bool
orb_conjunction: float .. orb_quintile: float
```

### 8.2 Response Envelope
```json
{ "success": true, "data": { ... } }
```

Interpretation response structure:
```json
{
  "summary": "Văn bản tổng quan 300-600 từ",
  "sections": [
    {
      "title": "Tên section",
      "content": "Văn xuôi liên tục, xưng bạn, dùng từ xác suất",
      "priority": 1
    }
  ],
  "overall": "Luận giải tổng hợp cuối cùng"
}
```

---

## 9. Data Model (Key Entities)

### 9.1 `AstrologicalSubject`
- Birth: name, year, month, day, hour, minute.
- Geo: latitude, longitude, timezone_str.
- Derived: `julian_day`, `local_sidereal_time`.

### 9.2 `Chart`
- Planets: longitude, sign, house, retrograde, speed, dignities, computed Weight $W$.
- Angles: ASC, MC, DSC, IC.
- Calculated points: Part of Fortune, North/South Node.
- Aspects: all within orb; includes applying/separating, aspect type, weights.
- Patterns: detected macro patterns with override priority.
- Interpretation: sections array + chart_summary + overall_interpretation.

### 9.3 `RuleResult`
- `rule_name`, `section_title`, `content`, `priority_order`, `language`.

---

## 10. Quality Gates (GSD Workflow)

```text
AUDIT   → ruff check astrololo/ tests/ scripts/ + pytest tests/ -v
SCAN    → đọc relevant rules/templates trước khi sửa
FIX     → edit existing files; add files only when necessary
VERIFY  → pytest tests/ -v + ruff + vite build
COMMIT  → short imperative EN subject + VI scope note
```

### 10.1 Non-Negotiables
- `PLANET_ORDER` chỉ chứa 16 planets (10 classical + 6 minor), không chứa nodes/angles.
- `registry.py` phải dùng `importlib.import_module()` để tránh ruff F401.
- Chiron, Ceres, Pallas, Juno, Vesta, Lilith dùng `body_type="planet"`.
- Ayanamsa và house system phải flow qua TẤT CẢ endpoints.
- Không có AI API key hardcoded. AI là optional.

### 10.2 AI Circuit Breaker
Nếu AI key missing hoặc provider lỗi → trả về template-only interpretation, log warning, vẫn trả `success=true`.

---

## 11. Testing Strategy

- **Unit tests:** 150+ backend tests cho calculations và rules.
- **Integration:** `test_ephemeris_accuracy.py` so với ngày chuẩn.
- **Benchmark:** 50-profile suite kiểm tra full natal → interpret pipeline.
- **Frontend:** `npm test` + `npm run build`.
- **Regression gate:** tất cả tests phải pass trước merge.

---

## 12. Out of Scope

- Commercial redistribution of scraped content.
- Real-time multi-user collaboration.
- Mobile-native native app builds.
- Third-party astrologer marketplace.

---

## 13. Glossary

- `Natal chart` — bản đồ sao tính tại thời điểm sinh.
- `Synthesis` — kết hợp nhiều yếu tố bản đồ thành một luận giải thống nhất.
- `Dignity` — sức mạnh của hành tinh theo cung, nhà, góc chiếu.
- `Lookup engine` — hệ thống ánh xạ 1-1 cố định, không suy luận.
- `Traceability Block` — khối metadata ghi inputs và logic rules đã dùng.
- `$W$` — trọng số năng lượng của hành tinh.
- `SDD` — Spec-Driven Development.
