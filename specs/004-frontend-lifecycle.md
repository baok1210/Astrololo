# Astrololo — Frontend Lifecycle Spec

## 1. Mục đích
Định nghĩa chính xác luồng dữ liệu, state management, component lifecycle  
và contract giữa frontend và backend cho ứng dụng Astrololo.

Luồng này phải đảm bảo kết quả cuối cùng là văn bản luận giải liên tục,  
không phải danh sách rời rạc. Frontend có nhiệm vụ **present**, không phải **synthesis**.

---

## 2. Runtime & Tech Stack
- React 18+ với TypeScript strict.
- Vite làm bundler/build tool.
- Axios làm HTTP client (`/api/v1` baseURL).
- D3.js render chart wheel.
- No global state management library trong scope hiện tại. State nội bộ từng panel.

---

## 3. Tab Structure

### 3.1 Tabs chính
```ts
type Tab = 'natal' | 'transit' | 'synastry' | 'predictive'
```

| Tab | Label VI | Label EN | Icon |
|---|---|---|---|
| natal | Lá Số Cá Nhân | Natal Chart | ☉ |
| transit | Quá Cảnh | Transits | ♄ |
| synastry | Tương Hợp | Synastry | ♀♂ |
| predictive | Tiến Trình | Predictive | ⏳ |

- Default tab: `natal`.
- Chuyển tab không giữ state của tab trước. Mỗi panel tự quản lý input/data riêng.

### 3.2 Language Toggle
- Global toggle `lang: 'vi' | 'en'` trong `App.tsx`.
- Lang được pass xuống tất cả panels như prop.
- Lang đồng thời gửi kèm request body sang backend (`lang=vi|en`).
- Backend trả về content tương ứng. Frontend không fallback translate.

---

## 4. State Model

### 4.1 App-Level State
```ts
tab: Tab
lang: 'vi' | 'en'
```

### 4.2 NatalPanel State
```ts
birthData: BirthData | null      // form state
chart: any | null                // raw chart from /natal
interpretation: SectionData[]    // synthesized sections from /interpret
overall: string | null           // executive summary
loading: boolean
error: string | null
```

Loading flow:
1. User submit form → set `loading = true`, `error = null`.
2. Call `getNatalRaw()` và `getNatal()` song song hoặc tuần tự.
3. `getNatalRaw()` trả về chart data gốc cho wheel/table.
4. `getNatal()` trả về interpretation đã synthesis.
5. Set chart + interpretation + overall, set `loading = false`.

### 4.3 TransitPanel State
```ts
birthData: BirthData | null
transitDate: { year, month, day } | null
result: TransitResponse | null
loading: boolean
error: string | null
```

### 4.4 SynastryPanel State
```ts
person1: BirthData | null
person2: BirthData | null
result: SynastryResponse | null
loading: boolean
error: string | null
```

### 4.5 PredictivePanel State
```ts
birthData: BirthData | null
mode: 'progression' | 'solar-return'
param: number | null    // age hoặc target_year
result: PredictiveResponse | null
loading: boolean
error: string | null
```

---

## 5. Component Lifecycle

### 5.1 Mount
1. `App` mounts → default `tab='natal'`, `lang='vi'`.
2. `NatalPanel` mounts → render form trống + wheel skeleton.
3. Gọi `getConstants()` để preload sign/planet metadata cho wheel? Optional optimization.

### 5.2 Submit
1. Validate form local:
   - date/time valid
   - lat/lon trong range
   - timezone_str có vẻ hợp lý
2. Nếu invalid → hiển thị inline error, không gửi request.
3. Nếu valid → set loading, gọi API.

### 5.3 API Response
1. **Success chart:**
   - `birthData` giữ nguyên.
   - `chart` được set.
   - Wheel re-render với placements mới.
   - Interpretation view render sections từng cái một, priority thấp đến cao.
   - Mỗi section là card có header màu riêng.
   - `overall` render ở đầu cùng card riêng.
2. **API error:**
   - Set `error`.
   - Render error banner với message từ backend (`detail`).
   - Loading spinner dừng.

### 5.4 Unmount / Switch Tab
- Không cần cleanup axios request. Axios cancel token không bắt buộc.
- State của panel trước có thể được giữ lại trong memory React, nhưng không persist qua refresh.

---

## 6. Data Boundaries (Frontend vs Backend)

### 6.1 Frontend Không Được Làm
- **Không tính toán ephemeris.** Backend trả về kết quả cuối cùng.
- **Không merge templates.** Backend đã synthesis xong.
- **Không retry logic phức tạp.** 1 retry với backoff 2s là đủ.
- **Không chạy keyword fallback.** Backend lo.
- **Không chuyển ngôn ngữ client-side.** Frontend gửi `lang`, backend trả về đúng lang.

### 6.2 Frontend Phải Làm
- Render văn xuôi liên tục, không wrap text thành bullet.
- Giữ nguyên paragraph breaks từ backend (`whiteSpace: 'pre-wrap'`).
- Không cắt đoạn `overall` hay `content` của section. Nếu quá dài, scroll container.
- PDF download: dùng `Blob` + `<a download>` cho endpoint binary.
- Loading state: spinner/overlay cho toàn panel, không partial loading.

---

## 7.natal Panel Layout

```
┌──────────────────────────────────────┐
│ Header: ASTROLO LO + Lang toggle     │
├──────────────────────────────────────┤
│ [Form: birth data inputs]            │
│ [Generate button]                    │
├──────────────┬───────────────────────┤
│  Chart Wheel │  Interpretation View  │
│  (D3.js)     │  - Overall            │
│              │  - Section cards       │
│              │  - Per-section prose   │
└──────────────┴───────────────────────┘
```

- Wheel hiển thị: ASC, MC, cusps, planets theo longitude.
- Click planet trên wheel → scroll to section tương ứng? Nice-to-have, không bắt buộc.
- Interpretation view scroll độc lập với wheel.

---

## 8. Transit Panel Layout

```
┌──────────────────────────────────────┐
│ Transit date selector (year/month/day)│
├──────────────┬───────────────────────┤
│  Natal Wheel │  Transit overlay       │
│  (static)    │  + transit aspects     │
├──────────────┴───────────────────────┤
│ Interpretation: transit→natal aspects│
└──────────────────────────────────────┘
```

---

## 9. Synastry Panel Layout

```
┌──────────────────────────────────────┐
│ Person 1 inputs + Person 2 inputs    │
├──────────────┬───────────────────────┤
│  Composite   │  Cross-aspect matrix   │
│  Wheel       │  + interpretation      │
└──────────────┴───────────────────────┘
```

---

## 10. Predictive Panel Layout

```
┌──────────────────────────────────────┐
│ Mode: [Progression] [Solar Return]   │
│ Param: age / year input              │
├──────────────────────────────────────┤
│ Progressed / SR chart wheel           │
│ Aspect list + interpretation         │
└──────────────────────────────────────┘
```

---

## 11. API Client Rules (`api.ts`)

- Mọi function trả về Promise.
- Không có `useEffect` gọi API tự động khi mount, trừ khi `getConstants()` cho metadata.
- Chart/interpretation APIs chỉ gọi khi user submit form.
- Axios baseURL: `/api/v1`.
- Timeout: KHÔNG set axios timeout mặc định. Để browser abort tự nhiên, hoặc 60s max.
- Error handling: `try/catch` trong mỗi panel. Lấy `error.response?.data?.detail` hoặc generic message.

### 11.1 Type Safety
- `SectionData` trong `api.ts` hiện là `{ category, title, items }`.
- Section content thực tế từ backend là `{ title, content, priority }`.
- **TODO:** update `SectionData` phản ánh đúng contract từ `002-api-contract.md`.

Frontend hiện đang dùng `SectionItem` shape:
- `section.title` → dùng làm section header
- `item.text` → dùng làm narrative paragraph
- `item.score` → optional, hiển thị badge

---

## 12. Rendering Rules

### 12.1 Narrative Display
Mỗi section trong `InterpretationView`:
- Render `overall` ở đầu nếu có, dạng paragraph.
- Mỗi section có header màu theo `SECTION_COLORS`.
- Section content: continuous prose, giữ nguyên `\n` từ backend.
- Không rút gọn, không ellipsize. Dùng scroll.

### 12.2 Wheel Rendering
- D3.js SVG trong `ChartWheel.tsx`.
- Input: `chart.planets`, `chart.angles`, `chart.house_cusps`.
- Vẽ: outer circle, cusp lines, planet symbols theo longitude, ASC/MC markers.
- color theo element: fire=red, earth=green, air=yellow, water=blue.
- Click planet → optional scroll to section.

### 12.3 Evidence Tags
Nếu `item.evidence` tồn tại, render dạng chips:
```
📍 Mars in 10th  •  📍 Mars Square Saturn  •  📍 T-Square
```

---

## 13. Loading & Error UX

### 13.1 Loading
- Panel-wide overlay hoặc spinner ngay bên dưới button.
- Disable form inputs khi loading.
- Show: "Đang lập bản đồ sao..." / "Interpreting chart..."

### 13.2 Error
- Inline banner màu đỏ.
- Message: `error || 'Đã xảy ra lỗi. Vui lòng thử lại.'`
- Button "Thử lại" retry lần cuối.

---

## 14. Performance Requirements
- Lần đầu load panel: < 200ms.
- Time-to-first-byte cho chart/interpretation: < 2s trên connection tốt.
- Wheel render: < 300ms sau khi nhận data.
- Scroll interpretation: 60fps, không jank.
- Không preload tất cả tabs. Lazy mount khi cần.

---

## 15. Accessibility
- Button có aria-label.
- Loading spinner có `aria-live="polite"`.
- Error banner có role `alert`.
- Color contrast đạt WCAG AA.
- Keyboard: tabindex hợp lý cho form inputs.

---

## 16. Notes
- Zodiac type tropical/sidereal, ayanamsa, house_system chỉ ảnh hưởng backend chart. Frontend chỉ pass qua.
- PDF export: frontend cần Blob URL handling.
- Health endpoint có thể poll mỗi 60s để hiển thị backend status badge.
- `/keywords` và `/constants` có thể prefetch khi app mount để có metadata sẵn.

---

## 17. Related Specs
- `001-astrololo-spec.md` — synthesis engine, output standards.
- `002-api-contract.md` — exact request/response schema.
- `003-template-coverage.md` — template data backend.
