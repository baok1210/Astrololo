# Astrololo Spec Index

## Conventions
- Mỗi spec có số thứ tự `NNN-` và tên ngắn gọn.
- Khi nhận lệnh từ user, agent phải lookup index này trước để xác định đúng spec(s) liên quan.
- Nếu lệnh overlaps nhiều specs → đọc tất cả rồi merge context.

## Spec Map

| ID | Tên | Dùng khi... | Keywords |
|---|---|---|---|
| `001` | Product + Synthesis Charter | Lệnh liên quan đến: luận giải, synthesis, output format, tone, pipeline 5 bước, W algorithm tổng quát | "luận giải", "synthesis", "output", "narrative", "tone", "pipeline", "bản đồ sao", "nhà chiêm tinh" |
| `002` | API Contract | Lệnh liên quan đến: endpoint, request/response, schema, FastAPI, status code, error shape | "API", "endpoint", "request", "response", "FastAPI", "schema", "status code", "health", "constants", "keywords" |
| `003` | Template Coverage | Lệnh liên quan đến: YAML templates, coverage, content gap, template maintenance, curated/baked/retriever/keywords | "template", "YAML", "coverage", "gap", "curated", "baked", "retriever", "keywords", "content" |
| `004` | Frontend Lifecycle | Lệnh liên quan đến: React, panel, tab, state, loading, error UX, wheel rendering, interpretation view | "frontend", "React", "panel", "tab", "state", "loading", "error", "wheel", "rendering", "App.tsx" |
| `005` | Scoring Weight Algorithm | Lệnh liên quan đến: trọng số W, Base Value, Dignity Multiplier, House Weight, pattern override, strength/weakness | "W", "trọng số", "scoring", "weight", "Base Value", "Dignity Multiplier", "House Weight", "pattern bonus", "strength", "mạnh/yếu" |
| `006` | Chart Model Schema | Lệnh liên quan đến: BodyPosition, AspectData, Chart model, Pydantic, serialization, field naming | "model", "schema", "BodyPosition", "AspectData", "Chart", "Pydantic", "serialization", "field" |
|| `007` | Error & Fallback | Lệnh liên quan đến: Swiss Ephemeris fallback, AI circuit breaker, graceful degradation, health endpoint, retry | "fallback", "error", "graceful", "circuit breaker", "Swiss Ephemeris", "AI fail", "health", "retry", "Keplerian" |
|| `008` | Release & Versioning | Lệnh liên quan đến: version, semver, breaking change, migration, tag, CHANGELOG, hotfix | "version", "semver", "breaking", "migration", "tag", "CHANGELOG", "hotfix", "release" |
|| `009` | Synthesis Engine Architecture | Lệnh liên quan đến: pipeline 5 bước, thuật toán trọng số W, synthesis logic, output guardrails, continuous prose, traceability block, weighted comparison | "W", "trọng số", "scoring", "pipeline", "synthesis", "traceability", "narrative", "guardrails", "prose", "weight", "output format", "dignity", "house weight", "base value" |
|| `010` | Computational Astrology Engine | Lệnh liên quan đến: Swiss Ephemeris, house system, ayanamsha, aspect orb, applying/separating, dignity scoring, essential/accidental dignity, dominant planet, pattern recognition (T-Square, Yod, Grand Cross, Stellium), de-conflicting, priority hierarchy, transit, progression, solar return, synastry overlay, composite midpoint, RAG, guardrail, LLM circuit breaker, JSON inter-engine contract | "Swiss Ephemeris", "house system", "ayanamsha", "orb", "applying", "separating", "dignity", "essential", "accidental", "dominant planet", "T-Square", "Yod", "Grand Cross", "Stellium", "de-conflicting", "transit", "progression", "solar return", "synastry", "composite", "RAG", "guardrail", "circuit breaker", "JSON", "contract" |

## Routing Examples

| Lệnh user (VI) | Spec(s) ưu tiên |
|---|---|
| "Implement scoring algorithm" | `005` |
| "Viết lại phần luận giải cho đúng" | `001`, `005`, `003` |
| "Thêm endpoint mới" | `002`, `006` |
| "Fix frontend loading state" | `004` |
| "Làm template coverage đủ hơn" | `003` |
| "Sửa lỗi Swiss Ephemeris fail" | `007`, `005` |
| "Ra mắt version mới" | `008` |
| "Cải thiện tổng hợp bản đồ sao" | `001`, `005`, `006` |
| "Fix bug chart calculation" | `007`, `006`, `008` |
