# Astrololo — Error Handling & Fallback Spec

## 1. Mục đích
Định nghĩa chiến lược xử lý lỗi và fallback cho tất cả dependencies:
- Swiss Ephemeris
- Template/KB retriever
- AI provider
- Input validation

Spec này đảm bảo backend **không bao giờ fail cứng** vì một dependency lỗi,  
trừ khi input hoàn toàn invalid.

---

## 2. nguyên tắc Chung

| Nguyên tắc | Chi tiết |
|---|---|
| **Graceful degradation** | Mỗi layer có fallback. Không fail request vì layer trên fail. |
| **Circuit breaker** | AI provider fail → trả về template-only, không crash. |
| **Logging** | Mọi fallback phải log ở `warning` hoặc `info`. Không silent fail. |
| **Observability** | Backend expose fallback status qua `/health`. |
| **Client contract** | Client luôn nhận `{success: true, data: ...}` trừ khi input invalid hoặc exception không catch được. |

---

## 3. Swiss Ephemeris Fallback

### 3.1 Detection
`core/ephemeris.py`:
- `HAS_SWISSEPH = False` nếu `import swisseph` fail.
- `EPHE_PATH = None` nếu không tìm thấy thư mục `ephe/`.

### 3.2 Fallback Path
Nếu `HAS_SWISSEPH = False` hoặc `EPHE_PATH` missing:
1. **Julian Day:** dùng pure-Python formula trong `calc_julian_day()`.
2. **Delta T:** dùng polynomial approximation trong `calc_delta_t()`.
3. **Planet positions:** dùng Keplerian elements cho Sun/Moon/Mercury/Venus/Mars/Jupiter/Saturn.  
   Các planets khác trả về longitude giả lập từ mean motion.
4. **Asteroids:** log debug, không warning, vì đây là expected fallback.

### 3.3 Behavior
- `HAS_SWISSEPH` vẫn được expose qua `/health`.
- Frontend có thể hiển thị warning badge nếu `swiss_ephemeris=false`, nhưng không chặn chart generation.
- Accuracy giảm khoảng 0.5-2 arcminutes cho các asteroids khi dùng Keplerian fallback.

---

## 4. Template/KB Fallback Chain

### 4.1 Loading Order
`template_loader.py` phải thử theo thứ tự:

```
1. curated YAML           (templates/{en,vi}/*.yaml)
2. baked YAML             (templates/{en,vi}/*_baked.yaml)
3. KB retriever           (interpretation/knowledge_retriever.py)
4. keywords fallback      (interpretation/keywords.py)
```

### 4.2 Contract
- Mỗi `get_*()` function phải trả về `dict` với ít nhất `title`, `short`, `detailed`.
- Không bao giờ trả `None` hoặc `""`.
- Nếu tất cả layers fail → auto-generate từ planet/sign/house keywords.

### 4.3 KB Retriever Failure
Nếu `knowledge_retriever.py` fail:
1. Log warning với exception message.
2. Rơi xuống layer tiếp theo.
3. Không throw exception lên caller.

### 4.4 Template Quality Gate
- Nếu YAML parse fail → log error + fallback keywords.
- Nếu YAML entry có `confidence: low` → optional: log info, vẫn dùng.

---

## 5. AI Provider Fallback

### 5.1 Circuit Breaker
`ai_provider.py`:
- `AI_API_KEY` missing + provider != ollama → trả `AIResponse(success=False, error="...")`.
- Provider call fail → trả `AIResponse(success=False, error=str(e))`.
- Không throw exception.

### 5.2 API Endpoint Behavior
`POST /api/v1/interpret/ai`:
1. Tạo chart. Nếu fail → 500.
2. Gọi `ai_interpret()`. Nếu AI fail → vẫn trả `success=true` với phần template.
3. Gọi `synthesize_all_planets()`. Nếu fail → `syntheses=[]`, log warning.
4. Response luôn có `template` field.

### 5.3 Frontend Handling
- Nếu `ai.success=false` → ẩn tab AI, không hiển thị error.
- Nếu `syntheses=[]` → không render empty state.
- Không retry AI call automatically.

---

## 6. Input Validation Errors

### 6.1 Validation Flow
`_build_subject()` trong `api/main.py`:
```python
try:
    datetime(req.year, req.month, req.day, req.hour, req.minute)
except ValueError:
    raise HTTPException(status_code=422, detail="Invalid date/time")
```

### 6.2 Pydantic Validation
FastAPI tự động trả 422 nếu:
- `year < 1900` hoặc `year > 2100`
- `month < 1` hoặc `month > 12`
- `day < 1` hoặc `day > 31` (precise validation do Pydantic/Marshmallow không check calendar days)
- `latitude < -90` hoặc `latitude > 90`
- `longitude < -180` hoặc `longitude > 180`
- `house_system` không trong whitelist
- `lang` không phải `vi` hoặc `en`

### 6.3 Response Shape
```json
{"detail": "Invalid date/time"}
```
hoặc FastAPI validation error format. Frontend parse `detail` để hiển thị.

---

## 7. Server Error Handling

### 7.1 500 Errors
Mọi endpoints có `try/except` bọc logic chính:

| Endpoint | 500 Message |
|---|---|
| `/natal` | Chart calculation failed |
| `/interpret` | Chart calculation failed |
| `/interpret/ai` | Chart calculation failed |
| `/transit` | Transit calculation failed |
| `/progression` | Progression calculation failed |
| `/solar-return` | Solar return calculation failed |
| `/daily` | Daily horoscope calculation failed |
| `/synastry` | Synastry calculation failed |
| `/export/pdf` | PDF generation failed |
| `/jyotish/dasha` | Dasha calculation failed |
| `/jyotish/remedies` | Chart calculation failed |

### 7.2 Logging
- Mọi 500 phải có `logger.exception()` với context rõ ràng.
- Stack trace được ghi vào backend log.
- Client chỉ nhận generic message, không exposed internal error.

### 7.3 Recovery
- Client retry 1 lần với backoff 2s.
- Nếu retry vẫn 500 → hiển thị error page.

---

## 8. Health Endpoint Contract

`GET /health`:

```json
{
  "status": "healthy",
  "swiss_ephemeris": true,
  "ai_enabled": true,
  "ai_provider": "openai",
  "ai_model": "gpt-4o-mini"
}
```

| Field | Type | Meaning |
|---|---|---|
| `status` | str | `"healthy"` hoặc `"degraded"` |
| `swiss_ephemeris` | bool | `HAS_SWISSEPH` |
| `ai_enabled` | bool | `bool(AI_API_KEY)` |
| `ai_provider` | str \| null | provider name |
| `ai_model` | str \| null | model name |

`status=degraded` khi:
- `swiss_ephemeris=false` hoặc
- `ai_enabled=true` nhưng last AI call failed.

---

## 9. Frontend Error UX

### 9.1 Error Banner
- Màu đỏ, inline.
- Message lấy từ `error.response?.data?.detail` hoặc generic.
- Có button "Thử lại" retry lần cuối.

### 9.2 Loading State
- Spinner/overlay khi API đang chạy.
- Disable form inputs.
- Timeout sau 60s → hiển thị timeout error.

### 9.3 Degraded State
- Nếu `/health` cho `swiss_ephemeris=false` → hiển thị warning badge.
- Không chặn user nhập liệu.
- Nếu KB retriever fail → không hiển thị gì, engine vẫn chạy tốt nhờ fallback.

---

## 10. Monitoring & Alerting

### 10.1 Log Patterns
Backend log phải có các markers:
```
[EPHE_FALLBACK] Swiss Ephemeris unavailable, using pure-Python
[KB_FALLBACK] knowledge_retriever failed: ..., falling back to keywords
[AI_FAIL] OpenAI API call failed: ..., template-only mode
[VALIDATION_FAIL] Invalid date/time for subject {name}: {e}
[CALC_FAIL] Error generating natal chart for {name}: {e}
```

### 10.2 Metrics (future)
- Fallback rate per dependency.
- P95 latency per endpoint.
- Error rate per endpoint.

---

## 11. Related Specs
- `001-astrololo-spec.md` — synthesis engine charter
- `002-api-contract.md` — error status codes
- `005-scoring-weight-algorithm.md` — scoring fallback khi data missing

---

## 12. Glossary
- `Graceful degradation` — hệ thống vẫn hoạt động với chất lượng giảm khi dependency fail.
- `Circuit breaker` — ngắt phụ thuộc, trả về safe default.
- `Keplerian fallback` — approximate planet positions từ orbital elements khi Swiss Ephemeris unavailable.
