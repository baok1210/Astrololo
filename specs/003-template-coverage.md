# Astrololo — Template Coverage Spec

## 1. Mục đích
Định nghĩa chính xác coverage hiện tại của YAML templates, xác định gap,  
và quy định cách synthesis engine sử dụng từng template layer.

Template layers:
- `curated` — tệp YAML do người dùng/spec đánh giá là chất lượng cao.
- `baked` — tệp YAML sinh tự động hoặc scraped rồi normalize, dùng như fallback có cấu trúc.
- `retriever` — markdown KB corpus crawl từ internet, dùng RAG/lookup.
- `keywords` — VI keyword fallback trong `keywords.py`, dùng khi tất cả layer trên fail.

Priority order:
`curated > baked > retriever > keywords`

---

## 2. Coverage Matrix (AS-IS)

Legend:
- `full` = đủ coverage theo spec hiện tại
- `partial` = có data nhưng chưa đủ 100%
- `minimal` = chỉ vài entries, chủ yếu dựa vào fallback
- `none` = không có dữ liệu trong layer này

| Rule / Section | EN curated | EN baked | VI curated | VI baked | Retriever | Keywords |
|---|---|---|---|---|---|---|
| planet_in_sign | partial | partial | partial | — | available | full |
| planet_in_house | partial | partial | partial | — | available | full |
| aspects | partial | minimal | partial | — | partial | partial |
| ascendant | full | — | partial | — | available | full |
| mc | full | — | partial | — | partial | full |
| node_sign | partial | — | partial | — | partial | full |
| pof | — | — | — | — | partial | full |
| house_cusp | full | — | partial | — | partial | full |
| patterns | partial | — | partial | — | partial | full |
| elements | partial | — | partial | — | partial | full |
| qualities | partial | — | partial | — | partial | full |
| hemispheres | partial | — | partial | — | partial | full |
| house_types | partial | — | partial | — | partial | full |
| dignities | partial | — | partial | — | partial | full |
| retrogrades | partial | — | partial | — | partial | full |
| moon_phase | partial | — | partial | — | partial | full |
| combinations | partial | — | partial | — | partial | full |
| encyclopedia | partial | — | partial | — | available | full |
| synthesis | partial | — | partial | — | partial | full |
| house_rulers | partial | — | partial | — | partial | full |
| jyotish/dasha | — | — | partial | — | — | full |
| jyotish/nakshatra | — | — | partial | — | — | full |
| jyotish/dignity | — | — | partial | — | — | full |
| jyotish/remedies | — | — | partial | — | — | full |

Notes:
- `—` means the file/layer currently has no meaningful content or is missing.
- `EN planet_in_sign_baked.yaml` và `planet_in_house_baked.yaml` có baked content nhưng chỉ dùng như fallback khi curated fail.
- VI templates phần lớn là curated nhưng nhiều section chỉ có skeleton.

---

## 3. Content Quality Standard

### 3.1 Entry Structure
Mỗi entry trong template phải có ít nhất:

```yaml
planet_mars:
  aries: "Văn bản luận giải tiếng An..."
```

HOẶC normalized form:

```yaml
title: "Mars in Aries"
short: "Câu ngắn 1-2 dòng"
detailed: "Văn xuôi 150-400 từ..."
```

### 3.2 Normalization
`template_loader.py` phải:
- Chấp nhận cả plain string và dict form.
- Convert plain string → dict với `title`, `short`, `detailed` tự sinh.
- Trả về dict thống nhất cho engine.

### 3.3 Anti-patterns
- Không có placeholder text (`"TODO"`, `"Lorem ipsum"`, `"Coming soon"`).
- Không có duplicate keys.
- Không có entries chỉ chứa whitespace hoặc 1-2 từ.

---

## 4. Engine Integration Rules

### 4.1 Loading Order
1. Rule gọi `template_loader.get_*(...)`.
2. Loader check curated YAML trước.
3. Nếu miss, check baked YAML.
4. Nếu miss, check retriever/ger KB từ markdown corpus.
5. Nếu miss, fallback sang `keywords.py`.
6. Luôn trả dict có `title`, `short`, `detailed`; không bao giờ trả `None` hoặc `""`.

### 4.2 Score Tagging
Optional: mỗi entry trong curated/baked YAML có thể có `confidence: high|medium|low`.
- `high`: scraped từ single source page.
- `medium`: merged từ nhiều source hoặc synthesized.
- `low`: keyword-generated fallback.

Engine có thể dùng `confidence` để:
- Ưu tiên `high` trong synthesis.
- Log warning khi dùng `low`.
- Exclude `low` khỏi executive summary nếu muốn.

### 4.3 Multi-language
- EN: dùng cho tất cả curated/baked/retriever entries.
- VI: dùng cho curated/fallback.  
- Một entry có thể có song ngữ:

```yaml
mars_aries:
  en:
    title: "Mars in Aries"
    detailed: "..."
  vi:
    title: "Sao Hỏa ở Bạch Dương"
    detailed: "..."
```

---

## 5. Gap Analysis & Priority Fill

### 5.1 Critical Gaps (must fill)
| Gap | Impact | Proposal |
|---|---|---|
| VI planet_in_sign 10/60 entries | natal reading thiếu | merge EN baked sang VI |
| EN planet_in_sign 11/60 entries | same | complete baked/curated |
| EN aspects 227/225 entries claimed | overlap/duplicate | audit unique combos |
| VI aspects 52/225 entries | major gap | batch fill curated |
| house_rulers EN/VI | synthesis logic phụ thuộc | add curated YAML |

### 5.2 High Priority Gaps
| Gap | Impact |
|---|---|
| combinations 0 entries | planet+sign+house synthesis thiếu raw material |
| retrogrades minimal | retrograde rule bị generic |
| house_cusp EN partial | ASC/MC reading thiếu chiều sâu |
| pof absent | Part of Fortune rule phải auto-generate |

### 5.3 Medium Priority
- `encyclopedia` chỉ 7 entries — cần expand.
- `moon_phase` minimal.
- `synthesis` templates minimal.

---

## 6. Template Maintenance Rules

### 6.1 Add New Template
1. Create file at `templates/{en,vi}/{section}.yaml`.
2. Loader tự động pick up nếu section name khớp rule name.
3. Nếu muốn ưu tiên, đặt tên `curated_{section}.yaml` loader sẽ ưu tiên hơn.

### 6.2 Rename / Merge Template
1. Cập nhật `template_loader.py` mapping.
2. Giữ file cũ ít nhất 1 cycle trước khi xóa.
3. Ghi chú trong CHANGELOG.md.

### 6.3 Quality Check
Trước khi promote curated:
- `python -c "import yaml; yaml.safe_load(open('path'))"` → valid YAML.
- No keys shorter than 2 chars.
- Each value has at least 50 chars or is marked `skip: true`.

---

## 7. Relationships to Other Specs
- `001-astrololo-spec.md` Section 6: interpretation content requirements.
- `002-api-contract.md` Section 4: endpoints that consume templates.
- Future `004-frontend-lifecycle.md`: frontend may request keywords/constants from these templates.

---

## 8. Success Metrics
- Curated coverage ≥ 80% cho tất cả rules listed in Section 6.1.
- Zero `blank` or `TODO` entries in shipped YAMLs.
- All YAMLs load without YAML parsing errors on startup.
- KB retriever fallback rate < 20% (engine uses curated/baked > 80%).

---

## 9. Out of Scope
- Auto-translation template content. EN curated phải là human-reviewed source.
- Commercial redistribution of template text.
- Dynamic template fetching từ internet ở runtime.

---

## 10. Glossary
- `curated` — template do người kiểm soát quality review.
- `baked` — template tự sinh hoặc scraped rồi normalize, dùng làm fallback.
- `retriever` — KB corpus crawl từ cafeastrology/astrolibrary/astro.com.
- `keywords` — fallback cuối cùng trong `keywords.py`.
- `entry` — một record trong YAML, ví dụ `jupiter_aries` hoặc `mars` → `aries`.
