# Astrololo — API Contract

## 1. Tổng quan
Spec này định nghĩa chính xác schema, behavior và error contract của tất cả endpoints backend hiện có.  
Mục tiêu: frontend/consumer có thể implement chính xác mà không cần đọc code backend.  
Mọi thay đổi breaking phải được ghi rõ ở đây trước khi merge.

**Base URL:** `/api/v1`  
**Content-Type:** `application/json`  
**Auth:** không yêu cầu trong scope hiện tại.

---

## 2. Envelope chuẩn

### 2.1 Thành công
```json
{ "success": true, "data": { ... } }
```

### 2.2 Thất bại
FastAPI sẽ throw `HTTPException`. Body:
```json
{ "detail": "Error message" }
```

| Status | Ngữ cảnh |
|---|---|
| `400` | Query param invalid |
| `422` | Body validation failed, date invalid |
| `500` | Calculation/interpretation engine error |
| `503` | Dependency unavailable (Swiss Ephemeris/AI fallback fails) |

---

## 3. Shared Models

### 3.1 `ChartRequest`
Dùng cho: `/natal`, `/interpret`, `/interpret/ai`, `/export/pdf`, `/transit`, `/progression`, `/solar-return`, `/daily`, `/jyotish/dasha`, `/jyotish/remedies`.

```text
name             : str            required, 1-100 chars
year             : int            required, 1900-2100
month            : int            required, 1-12
day              : int            required, 1-31
hour             : int            optional, default 0, 0-23
minute           : int            optional, default 0, 0-59
latitude         : float          required, -90 to 90
longitude        : float          required, -180 to 180
timezone_str     : str            optional, default "UTC"
house_system     : str            optional, default "placidus"
                    values: placidus, koch, equal, whole_sign, regiomontanus, campanus, porphyry
node_type        : str            optional, default "mean"
                    values: mean, true
lang             : str            optional, default "vi"
                    values: vi, en
esoteric         : bool           optional, default true
zodiac_type      : str            optional, default "tropical"
                    values: tropical, sidereal
ayanamsa         : str            optional, default "lahiri"
                    values: lahiri, raman, krishnamurti
include_minor_aspects : bool      optional, default true
orb_conjunction  : float          optional, default 8.0, 0-15
orb_opposition   : float          optional, default 8.0, 0-15
orb_square       : float          optional, default 8.0, 0-15
orb_trine       : float          optional, default 8.0, 0-15
orb_sextile       : float          optional, default 6.0, 0-15
orb_quincunx      : float         optional, default 3.0, 0-10
orb_semisextile   : float         optional, default 3.0, 0-10
orb_semisquare    : float         optional, default 2.0, 0-10
orb_sesquiquadrate: float         optional, default 2.0, 0-10
orb_quintile      : float         optional, default 2.0, 0-10
```

**Validation logic:**
- `_build_subject()` kiểm tra `datetime(year, month, day, hour, minute)`. Nếu invalid → 422 `Invalid date/time`.
- Các orb fields override default nếu truyền vào; nếu không truyền thì dùng default.
- `lang=vi` means output Vietnamese; `lang=en` means output English labels/content where available.

### 3.2 `TransitRequest` extends `ChartRequest`
Thêm:
```text
transit_year     : int            required, 1900-2100
transit_month    : int            required, 1-12
transit_day      : int            required, 1-31
```

### 3.3 `ProgressionRequest` extends `ChartRequest`
Thêm:
```text
age              : float          required, 0-120
```

### 3.4 `SolarReturnRequest` extends `ChartRequest`
Thêm:
```text
target_year      : int            required, 1900-2100
```

### 3.5 `SynastryRequest`
Dùng cho `/synastry`.

```text
person1_name     : str            required
person1_year     : int            required, 1900-2100
person1_month    : int            required, 1-12
person1_day      : int            required, 1-31
person1_hour     : int            optional, default 0
person1_minute   : int            optional, default 0
person1_latitude : float          required, -90 to 90
person1_longitude: float          required, -180 to 180
person1_timezone : str            optional, default "UTC"

person2_name     : str            required
person2_year     : int            required, 1900-2100
person2_month    : int            required, 1-12
person2_day      : int            required, 1-31
person2_hour     : int            optional, default 0
person2_minute   : int            optional, default 0
person2_latitude : float          required, -90 to 90
person2_longitude: float          required, -180 to 180
person2_timezone : str            optional, default "UTC"

house_system     : str            optional, default "placidus"
node_type        : str            optional, default "mean"
lang             : str            optional, default "vi"
esoteric         : bool           optional, default true
include_minor_aspects : bool      optional, default true
orb_conjunction  : float          optional, default 8.0, 0-15
orb_opposition   : float          optional, default 8.0, 0-15
orb_square       : float          optional, default 8.0, 0-15
orb_trine       : float          optional, default 8.0, 0-15
orb_sextile       : float          optional, default 6.0, 0-15
orb_quincunx      : float         optional, default 3.0, 0-10
orb_semisextile   : float         optional, default 3.0, 0-10
orb_semisquare    : float         optional, default 2.0, 0-10
orb_sesquiquadrate: float         optional, default 2.0, 0-10
orb_quintile      : float         optional, default 2.0, 0-10
```

---

## 4. Endpoints chi tiết

### 4.1 `GET /`
- **Purpose:** service ping / version check
- **Auth:** không yêu cầu
- **Response:** `{ "service": "Astrololo", "version": "0.1.0", "status": "active" }`

### 4.2 `GET /health`
- **Purpose:** kiểm tra sức khỏe service + config runtime
- **Response:**
```json
{
  "status": "healthy",
  "swiss_ephemeris": true,
  "ai_enabled": true,
  "ai_provider": "openai",
  "ai_model": "gpt-4o-mini"
}
```

- **Notes:**
  - `swiss_ephemeris`: flag từ `core.ephemeris.HAS_SWISSEPH`.
  - `ai_enabled`: true nếu `AI_API_KEY` tồn tại và non-empty.
  - Nếu provider/khóa không tồn tại, field vẫn trả về, chỉ có giá trị false/None.

### 4.3 `POST /api/v1/natal`
- **Mục đích:** Tính bản đồ sao sinh.
- **Auth:** không yêu cầu
- **Request:** `ChartRequest`
- **Response:** `{ "success": true, "data": <chart.model_dump()> }`
- **Logic:**
  - `zodiac_type=tropical` → `create_natal_chart()`
  - `zodiac_type=sidereal` → `create_jyotish_chart()`
  - Chart object bao gồm: planets, aspects, angles, calculated points, interpretation khi có.
- **Error:**
  - `422`: invalid datetime
  - `500`: engine exception
- **Example:** xem `tests/backtest.py` hoặc dùng request thật từ frontend.

### 4.4 `POST /api/v1/interpret`
- **Mục đích:** Lấy luận giải template-based cho natal chart.
- **Auth:** không yêu cầu
- **Request:** `ChartRequest`
- **Response:**
```json
{
  "success": true,
  "data": {
    "summary": "...",
    "interpretation": [
      {
        "title": "...",
        "content": "Văn xuôi liên tục, 150-400 từ, xưng bạn",
        "priority": 1
      }
    ],
    "overall": "..."
  }
}
```
- **Logic:**
  - Tạo chart như `/natal`.
  - Chạy `InterpretationEngine`.
  - `summary` = `chart_summary` từ engine.
  - `interpretation` = `sections` từ engine, mỗi section có `title`, `content`, `priority`.
  - `overall` = `overall_interpretation` từ engine.
- **AI circuit breaker:** Luôn trả về template interpretation, không phụ thuộc AI key.

### 4.5 `POST /api/v1/interpret/ai`
- **Mục đích:** Luận giải tăng cường AI (optional).
- **Auth:** không yêu cầu, nhưng AI chỉ hoạt động nếu key tồn tại.
- **Request:** `ChartRequest`
- **Response:**
```json
{
  "success": true,
  "data": {
    "summary": { "name": "...", "ascendant": "..." },
    "template": "Template-only overall interpretation",
    "ai": { ... },
    "syntheses": [ ... ]
  }
}
```
- **Logic:**
  - Tạo chart như `/interpret`.
  - Chạy `ai_interpret()`.
  - Chạy `synthesize_all_planets()`; nếu fail → `syntheses = []`, log warning.
  - Luôn trả `success=true` với phần template dù AI fail.
- **Error:**
  - `500`: chart calculation failed
  - AI failure được xử lý nội bộ, không trả error.

### 4.6 `POST /api/v1/transit`
- **Mục đích:** Tính transit chart cho ngày chỉ định.
- **Request:** `TransitRequest`
- **Response:** `{ "success": true, "data": <transit result dict> }`
- **Logic:**
  - Dùng input birth data để tạo natal subject.
  - Gọi `create_transits()` với `transit_year/month/day`.
  - Kết quả chứa `transit_aspects`, `transit_to_natal`.
- **Error:** `500` nếu transit calculation fail.

### 4.7 `POST /api/v1/progression`
- **Mục đích:** Tính secondary progression (day-for-year).
- **Request:** `ProgressionRequest`
- **Response:** `{ "success": true, "data": <progression result dict> }`
- **Logic:**
  - Birth subject + `age` → progressed JD = birth JD + age_days.
  - Tính progressed chart + progressed→natal aspects.
- **Error:** `500` nếu progression calculation fail.

### 4.8 `POST /api/v1/solar-return`
- **Mục đích:** Tính solar return chart cho năm chỉ định.
- **Request:** `SolarReturnRequest`
- **Response:** `{ "success": true, "data": <solar return result dict> }`
- **Logic:**
  - Tìm thời điểm Mặt Trời return到 vị trí natal.
  - Tính SR chart + SR→natal aspects.
- **Error:** `500` nếu SR calculation fail.

### 4.9 `POST /api/v1/daily`
- **Mục đích:** Tính daily horoscope picks từ transits.
- **Request:** `ChartRequest`
- **Response:** `{ "success": true, "data": <daily result dict> }`
- **Logic:**
  - Tính transit của hôm nay.
  - Chọn các transit quan trọng làm daily picks.
- **Error:** `500` nếu daily calculation fail.

### 4.10 `POST /api/v1/synastry`
- **Mục đích:** Tính synastry giữa hai người.
- **Request:** `SynastryRequest`
- **Response:** `{ "success": true, "data": <synastry result dict> }`
- **Logic:**
  - Tạo hai subjects.
  - Gọi `create_synastry()`.
  - Kết quả chứa `cross_aspects`, `house_overlays`, `composite`.
- **Error:** `500` nếu synastry calculation fail.

### 4.11 `POST /api/v1/export/pdf`
- **Mục đích:** Xuất PDF multi-page chart report.
- **Request:** `ChartRequest`
- **Response:** binary PDF (`application/pdf`), không phải JSON.
- **Headers:**
  - `Content-Disposition: attachment; filename="astrololo_{name_slug}.pdf"`
- **Logic:**
  - Tạo subject.
  - Gọi `create_pdf_export()`.
  - Trả về bytes.
- **Error:** `500` nếu PDF generation fail.

### 4.12 `GET /api/v1/constants`
- **Mục đích:** Lấy metadata cố định: planets, signs, aspects, houses, elements, qualities.
- **Auth:** không yêu cầu
- **Query params:** không
- **Response:**
```json
{
  "success": true,
  "data": {
    "planets": {
      "sun": { "name_vi": "Mặt Trời", "name_en": "Sun", "symbol": "☉" },
      ...
    },
    "signs": {
      "aries": { "name_vi": "Bạch Dương", "name_en": "Aries", "symbol": "♈", "element": "fire", "quality": "cardinal" },
      ...
    },
    "aspects": {
      "conjunction": { "name_vi": "Hợp", "name_en": "Conjunction", "angle": 0, "nature": "neutral" },
      ...
    },
    "houses": {
      "1": { "name_vi": "Nhà 1", "name_en": "1st House", "type": "angular" },
      ...
    },
    "elements": ["fire", "earth", "air", "water"],
    "qualities": ["cardinal", "fixed", "mutable"]
  }
}
```

### 4.13 `GET /api/v1/keywords`
- **Mục đích:** Expose VI keyword library cho frontend.
- **Auth:** không yêu cầu
- **Query params:**
  - `type`: `sign` | `house` | `planet` | null (all)
  - `q`: search term, strip diacritics insensitive
  - `planet`: filter exact planet key
  - `sign`: filter exact sign key
  - `house`: filter exact house number 1-12

- **Response:**
```json
{
  "success": true,
  "data": {
    "signs": {
      "aries": {
        "name_vi": "Bạch Dương",
        "element": "fire",
        "quality": "cardinal",
        "positive": ["năng động", "tự tin"],
        "negative": ["ích kỷ", "bốc đồng"],
        "core": ["lãnh đạo", "khởi xướng"],
        "short_description": "...",
        "potential_issues": "..."
      }
    },
    "houses": {
      "1": {
        "title": "Nhà 1",
        "name_vi": "Nhà Bản Mệnh",
        "keywords": ["bản thân", "hình ảnh"],
        "description": "..."
      }
    },
    "planets": {
      "sun": {
        "function": "Ý thức, sức sống, danh tiếng",
        "represents": "Người cha, âm tính, sự tỏa sáng"
      }
    }
  }
}
```

- **Logic:** filter theo `q` bằng cách strip diacritics rồi so khớp substring. Search cover positive/negative/core/name_vi cho signs; keywords/title cho houses; function/represents cho planets.

### 4.14 `GET /api/v1/jyotish/constants`
- **Mục đích:** Lấy jyotish metadata: Navagraha, Nakshatras, Dasha, sign rulers.
- **Auth:** không yêu cầu
- **Response:**
```json
{
  "success": true,
  "data": {
    "navagraha": {
      "sun": { "name_sa": "Surya", "name_vi": "Mặt Trời", ... },
      ...
    },
    "nakshatras": [
      { "number": 1, "name_sa": "Ashwini", "name_vi": "Ashwini", "ruler": "Ketu", "deity": "Ashwins", "gana": "Deva" },
      ...
    ],
    "dasha_years": { "ketu": 7, "venus": 20, ... },
    "dasha_sequence": ["ketu", "venus", "sun", ...],
    "sign_rulers": { "aries": "mars", ... },
    "rashi_names": { "1": { "sa": "Mesha", "vi": "Bạch Dương" } },
    "tattwa_names": { "fire": "Hỏa", ... },
    "guna_names": { "sattva": "Sattva", "rajas": "Rajas", "tamas": "Tamas" },
    "dignity_names": { "exaltation": "Uchcha", ... }
  }
}
```

### 4.15 `POST /api/v1/jyotish/dasha`
- **Mục đích:** Tính Vimshottari Dasha cho natal chart.
- **Request:** `ChartRequest`
- **Response:** `{ "success": true, "data": <dasha.model_dump()> }`
- **Error:** `500` nếu Dasha data unavailable hoặc calculation fail.

### 4.16 `POST /api/v1/jyotish/remedies`
- **Mục đích:** Lấy Navagraha remedies dựa trên điểm yếu trong chart.
- **Request:** `ChartRequest`
- **Response:**
```json
{
  "success": true,
  "data": [
    {
      "graha": "mars",
      "graha_name_vi": "Sao Hỏa",
      "dignity": "neecha",
      "sign": "Vrishchika",
      "remedy": "..."
    }
  ]
}
```
- **Logic:** Chỉ trả remedy cho planets có `jyotish_dignity == "neecha"`.
- **Error:** `500` nếu chart calculation fail.

---

## 5. Chart Response Shape (shared)

### 5.1 Natal/Transit/Synastry/Progression/Solar Return/Daily
Tất cả trả về:
```json
{
  "success": true,
  "data": {
    ...result dict từ analysis module...
  }
}
```

Các field phổ biến trong `data`:
- `planets`: list planets với longitude, sign, house, retrograde, speed, dignities.
- `aspects`: list aspects với planet_a, planet_b, aspect_type, orb, applying/separating.
- `angles`: ASC, MC, DSC, IC longitudes + signs.
- `house_cusps`: 12 cusp longitudes/signs.
- `interpretation`: sections array khi có.
- `dasha`: jyotish dasha periods khi có.
- `composite`: synastry composite midpoint chart khi có.

### 5.2 Interpretation Shape
```text
chart_summary         : str   (150-400 từ)
section_title_i       : str
section_content_i     : str   (văn xuôi liên tục, xưng "bạn")
overall_interpretation: str   (300-600 từ)
```

---

## 6. Error Handling

### 6.1 Client Error
| Status | Condition | Body |
|---|---|---|
| 422 | Invalid date/time | `{"detail": "Invalid date/time"}` |
| 422 | Missing required field | FastAPI auto-validation response |
| 404 | No path match | FastAPI default |

### 6.2 Server Error
| Status | Condition | Body |
|---|---|---|
| 500 | Chart calculation exception | `{"detail": "Chart calculation failed"}` |
| 500 | PDF generation exception | `{"detail": "PDF generation failed"}` |
| 500 | Transit/Progression/etc failed | `{"detail": "<feature> calculation failed"}` |
| 500 | Dasha data unavailable | `{"detail": "Dasha data unavailable"}` |

### 6.3 Graceful Degradation
- Swiss Ephemeris unavailable → fallback to pure-Python, vẫn trả `success=true`.
- AI unavailable → trả template-only interpretation, không bao giờ trả `success=false` vì AI lỗi.
- KB retriever fail → rơi xuống keyword fallback, không fail request.

---

## 7. Notes Triển khai cho Consumer

1. `timezone_str` phải là tzdata name hợp lệ, ví dụ `Asia/Ho_Chi_Minh`, không phải `GMT+7`.
2. `house_system` chỉ áp dụng cho tropical western; jyotish chart dùng hệ cung đặc thù.
3. `zodiac_type=sidereal` yêu cầu `ayanamsa` hợp lệ.
4. Requests tới `/interpret`, `/interpret/ai`, `/transit`, `/progression`, `/solar-return`, `/synastry` có thể mất >2s. Consumer nên có spinner/loading state.
5. PDF endpoint trả binary; frontend nên dùng Blob + `<a download>`.
6. Swagger UI có sẵn ở `/docs` với đầy đủ schema động.
