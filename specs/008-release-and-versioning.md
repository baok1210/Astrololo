# Astrololo — Release & Versioning Spec

## 1. Mục đích
Định nghĩa versioning scheme, release flow, migration policy,  
và breaking change rules cho Astrololo.

Scope: backend + frontend + specs + templates.

---

## 2. Versioning Scheme

### 2.1 Semantic Versioning
- Format: `MAJOR.MINOR.PATCH`
- **MAJOR** — breaking API/contract/model/spec change.
- **MINOR** — backward-compatible feature/spec addition.
- **PATCH** — bug fix, typo, template content update.

### 2.2 Current Version
- API version: `0.1.0` (hardcoded trong `api/main.py`).
- Package version: follow released tags.
- Spec version: tên file `NNN-*` thay đổi khi spec structure thay đổi.

### 2.3 API Versioning
- Base URL: `/api/v1`.
- Phải có breaking change mới bump lên `/api/v2`.
- Minor/patch changes không đổi URL path.
- Frontend hardcode `/api/v1` trong axios baseURL.

---

## 3. Release Flow

### 3.1 Backend/Frontend Code
1. Feature branch từ `origin/master`.
2. Tên branch: `feature/001-scoring` hoặc `fix/pdf-export`.
3. Tạo spec trước khi code nếu là feature mới.
4. Implement + test.
5. Pull request vào `master`.
6. CI checks: `ruff check`, `pytest tests/ -q`, `npm run build`.
7. Merge + tag release nếu cần.

### 3.2 Template/Spec Updates
- Template content update → `PATCH` version.
- New template section → `MINOR` version.
- Template schema change → `MAJOR` version.

### 3.3 CHANGELOG.md
Append entry mỗi khi merge:
```markdown
## [0.3.1] - YYYY-MM-DD
### Changed
- VI planet_in_sign coverage: 10 → 45 entries
- Scoring algorithm: added T-Square apex bonus

### Fixed
- PDF export: blank page on cover
```

---

## 4. Breaking Change Rules

### 4.1 What Counts as Breaking
| Change | Level |
|---|---|
| Remove/rename endpoint | MAJOR |
| Change request body required field | MAJOR |
| Change response field name/type | MAJOR |
| Remove template entry key | MAJOR |
| Change W formula constants | MAJOR |
| Add optional request field | MINOR |
| Add new endpoint | MINOR |
| Add new template section | MINOR |
| Fix template text | PATCH |
| Fix typo in spec | PATCH |

### 4.2 Breaking Change Process
1. Announce trong issue/discussion.
2. Bump MAJOR version.
3. Create `/api/v2` endpoint nếu API breaking.
4. Maintain `/api/v1` ít nhất 3 minor releases.
5. Update `002-api-contract.md`.
6. Update frontend migration guide.

---

## 5. Template Migration Policy

### 5.1 Add New Template
1. Create file `templates/{lang}/{section}.yaml`.
2. Add entry vào `template_loader.py` mapping.
3. Test: `python -c "import yaml; yaml.safe_load(open(...))"`.
4. CHANGELOG: "Add {section} template for {lang}".

### 5.2 Rename Template Key
1. Add alias trong `template_loader.py`.
2. Migrate entries sang key mới.
3. Mark alias `deprecated`.
4. Giữ alias 2 minor versions trước khi xóa.

### 5.3 Deprecate Template Section
1. Mark section `deprecated` trong spec.
2. Frontend/engine stop rendering nhung vẫn load data.
3. Xóa hoàn toàn sau 2 minor versions.

---

## 6. Frontend Contract Migrations

### 6.1 Section Title Changes
- `SECTION_TITLES` trong `InterpretationView.tsx` phải map đúng `category` key từ backend.
- Nếu backend đổi `category` string → frontend phải update song song.

### 6.2 API Client Updates
- `api.ts` type changes: update `SectionData`, `SectionItem` để match `002-api-contract.md`.
- Add/remove endpoint: update function list trong `api.ts`.

---

## 7. Backward Compatibility

### 7.1 Long-Term Support
- `/api/v1` được maintain cho ít nhất 6 tháng sau khi `/api/v2` release.
- Deprecated fields giữ ít nhất 2 minor versions.

### 7.2 Client Compatibility
- Backend không remove query param mà client đang dùng.
- Backend không đổi default value của field đang dùng.
- Backend thêm `?legacy=true` query param nếu cần support old behavior.

---

## 8. Hotfix Policy

### 8.1 Hotfix Criteria
- Security vulnerability.
- Chart calculation error với specific input.
- Crash trên `/interpret` endpoint.
- Data corruption.

### 8.2 Hotfix Flow
1. Tạo branch `hotfix/issue-XXX` từ `master`.
2. Fix + test.
3. Merge + tag `PATCH`.
4. Cherry-pick vào release branch nếu có.

---

## 9. Release Checklist

### 9.1 Code
- [ ] All tests pass: `pytest tests/ -q`
- [ ] `ruff check` clean
- [ ] `npm run build` thành công

### 9.2 Specs
- [ ] Update `CHANGELOG.md`
- [ ] Update version trong README nếu cần
- [ ] tag release

### 9.3 Templates
- [ ] `python -c "import yaml; yaml.safe_load(open(...))"` pass cho tất cả YAMLs
- [ ] No `TODO`, `Lorem ipsum`, empty values
- [ ] `003-template-coverage.md` updated nếu coverage thay đổi

### 9.4 Frontend
- [ ] `npm test` pass
- [ ] `npm run build` pass
- [ ] TypeScript strict mode: no implicit any

---

## 10. Deprecation Notice Format
```json
{
  "deprecated": true,
  "sunset_version": "0.5.0",
  "replacement": "/api/v2/interpret",
  "message": "Use /api/v2/interpret instead. /api/v1 will be removed in v0.5.0."
}
```

---

## 11. Out of Scope
- Blue/green deployment.
- Feature flags.
- A/B testing framework.

---

## 12. Glossary
- `MAJOR` — breaking change.
- `MINOR` — backward-compatible feature.
- `PATCH` — bug fix, content fix.
- `Hotfix` — emergency patch cho critical bug.
- `Sunset` — version khi deprecated endpoint bị remove.
