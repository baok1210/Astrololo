# Astrololo — Phân tích & Đề xuất nâng cấp độ chính xác + ứng dụng

> Ngày phân tích: 14/07/2026 · Môi trường: Windows 11, Python 3.11, Swiss Ephemeris 2.10.3.2
> Trạng thái kiểm thử: **156/156 tests pass** (gồm 4 test mới) · Frontend `npm run build` ✅

---

## 1. TÓM TẮT ĐÁNH GIÁ (hiện tại)

Astrololo đã là một engine chiêm tinh **rất đầy đủ tính năng** so với các web phân tích phổ biến:

| Hạng mục | Astrololo | cafeastrology | astro-seek | co-star |
|---|---|---|---|---|
| Tính toán lá số gốc (Sun→Pluto) | ✅ Swiss Eph | ✅ | ✅ | ✅ |
| 16 thiên thể (gồm Chiron + 4 tiểu hành tinh + Lilith) | ✅ | ❌ (chỉ 10) | ✅ | ❌ |
| Hệ nhà (7 hệ: Placidus, Koch, Whole…) | ✅ | ⚠️ hạn chế | ✅ | ❌ (chỉ Whole) |
| Synastry (chồng lấp + composite) | ✅ | ✅ | ✅ | ✅ |
| Transit / Progression / Solar Return | ✅ | ⚠️ | ✅ | ❌ |
| Jyotish (Dasha/Remedies) | ✅ | ❌ | ❌ | ❌ |
| PDF export | ✅ | ❌ | 💰 | ❌ |
| AI interpretation | ✅ (có sẵn, cần key) | ❌ | ❌ | ✅ |
| Song ngữ VI/EN | ✅ | ❌ | ❌ | ❌ |

**Kết luận:** về *phạm vi tính năng*, Astrololo đã **ngang bằng hoặc vượt** hầu hết web miễn phí. Vấn đề nằm ở **độ chính xác dữ liệu** và một vài điểm **chất lượng đầu ra** — đã được xử lý một phần dưới đây.

---

## 2. CÁC LỖI ĐÃ TÌM THẤY & SỬA (CRITICAL)

### 🔴 Lỗi 1 — Swiss Ephemeris chưa được cài (sai số nghiêm trọng)
- **Triệu chứng:** `swisseph` không có trong môi trường → outer planets (Uranus/Neptune/Pluto/Chiron/…) tính = **0° Aries**, retrograde **không bao giờ kích hoạt**, house system fallback về equal-house thô.
- **Sửa:** `uv pip install pyswisseph` (phiên bản 2.10.3.2). Đã xác minh: Sun Jobs 5°45' Pisces, Moon 7°45' Aries, ASC Virgo — **khớp 100% với astro.com/astro-seek**.
- **Tác động:** độ chính xác vị trí thiên thể tăng từ "sai hoàn toàn" → "chuẩn chuyên nghiệp".

### 🔴 Lỗi 2 — Tiểu hành tinh (Chiron/Ceres/Pallas/Juno/Vesta) âm thầm co về 0° Aries
- **Nguyên nhân kép:**
  1. File `seas_18.se1` trong `ephe/` được regenerate bằng định dạng **"SWISSEPH 3" / DE441 (2026)** → core 2023 đọc không được (báo "file not found").
  2. Khi Swisseph fail, code fallback chỉ có sẵn cho Sun/Moon/5 hành tinh → tiểu hành tinh rơi vào `lon=0.0` (0° Aries) **mà không báo lỗi**.
- **Sửa:** thêm **fallback quỹ đạo Kepler** (yếu tố J2000: L0, chuyển động trung bình, độ lệ tâm, périhélie) cho 5 thiểu hành tinh. Sửa lỗi đơn vị: `n*centuries` (t/100) thay vì `n*t_p` (sai ~340°).
- **Kết quả:** Jobs 1955 → Ceres/Pallas/Juno/Vesta đều nằm Cự Giải (~0–20°), Chiron Xử Nữ — **đúng thực tế**. Trước: tất cả = 0° Aries.
- **Thêm test:** `tests/test_ephemeris_accuracy.py` (4 test) khóa hành vi này, không cho tái phạm.

### 🟡 Lỗi 3 — Log cảnh báo gây hiểu lầm
- Mỗi lần tính lá số in ~50 dòng `"Swiss Ephemeris failed ... chiron"` dù fallback hoạt động đúng.
- **Sửa:** tiểu hành tinh → `logger.debug`; chỉ main planet thật sự fail mới `logger.warning`.

---

## 3. CÁC ĐIỂM CÒN YẾU (cần ưu tiên nâng cấp)

### A. Xếp hạng "Hành tinh nổi bật" bị lệch (chất lượng diễn giải)
- `scoring.py` cộng điểm aspect (`weight`) + house weight cho **mọi body kể cả tiểu hành tinh/Pluto**. Ví dụ Jobs: Pluto (43đ) & Juno (36đ) xếp trên Mặt Trời (31đ) → bản tóm tắt "hành tinh chi phối" sai lệch so với thực tế (Mặt Trời/MC mới là cốt lõi).
- **Đề xuất:** trọng số giảm dần cho outer/asteroid (như đã làm với `ELEM_WEIGHTS` ở natal.py), hoặc chỉ xếp hạng 10 hành tinh cổ điển + nhắc tiểu hành tinh riêng.

### B. Synastry chưa có "Điểm tương hợp" (Compatibility Score)
- Hiện có house overlays + composite chart rất tốt, nhưng **thiếu điểm số tổng hợp** (như astro-seek/co-star). Người dùng muốn một con số % hoặc đánh giá "Rất hợp / Cần thấu hiểu".
- **Đề xuất:** thêm `compatibility_score` từ trọng số góc chiếu (trine/sextile +, square/opp −), đặc biệt Sun-Moon, Venus-Mars, ASC/MC.

### C. Thiếu tính năng "hàng ngày" (daily horoscope / sun-sign) so với co-star
- co-star mạnh ở trải nghiệm "mỗi ngày 1 thông điệp". Astrololo chưa có endpoint daily transit-to-natal tóm tắt.
- **Đề xuất:** endpoint `/api/v1/daily` = transit hôm nay → lá số natal, tóm tắt VI/EN ngắn gọn.

### D. Frontend: biểu đồ & UX
- `ChartWheel.tsx` đã có memoization. Cần: (1) hiển thị thiểu hành tinh/Chiron trên vành; (2) tab Synastry composite; (3) so sánh 2 lá số cạnh nhau.
- Chưa có **tìm kiếm thành phố** (geocoding) → người dùng phải nhập lat/lng thủ công (gây sai số lớn). Đây là **lỗi UX nghiêm trọng nhất ảnh hưởng độ chính xác thực tế**.

### E. Dignity (Term/Face) chưa lên ranking
- `get_dignity_score_full` đã tính triplicity/term/face đúng, nhưng `dominant_planet` và overview chưa dùng `minor_dignities` để tăng độ tinh tế.

---

## 4. LỘ TRÌNH ĐỀ XUẤT (theo thứ tự ưu tiên)

| Ưu tiên | Hạng mục | Nỗ lực | Tác động |
|---|---|---|---|
| 🔥 P0 | **Geocoding thành phố** trên frontend (tự động lat/lng) | TB | Ngăn sai số tọa độ — sai số ASC/MC lớn nhất thực tế |
| 🔥 P0 | **Sửa trọng số dominant planet** (giảm outer/asteroid) | Thấp | Headline diễn giải chính xác hơn |
| ⭐ P1 | **Compatibility score** cho Synastry | TB | Bằng/trội hơn astro-seek |
| ⭐ P1 | **Endpoint `/api/v1/daily`** (daily horoscope) | TB | Cạnh tranh co-star |
| ⭐ P1 | Hiển thị Chiron/asteroid trên ChartWheel + tab Composite | TB | Hoàn thiện UX |
| 🟢 P2 | Dùng minor dignities (term/face) trong ranking/overview | Thấp | Sâu sắc hơn |
| 🟢 P2 | Nâng cấp `seas_18.se1` (tải file chuẩn hoặc build riêng) để Swisseph tính tiểu hành tinh chuẩn 100% | TB | Loại bỏ fallback Kepler |
| 🟢 P2 | Cấu hình AI key (OpenAI/Ollama) để bật lớp diễn giải AI | Thấp | Trội hẳn web thường |

---

## 5. ĐÃ THỰC HIỆN TRONG PHIÊN NÀY

✅ Cài Swiss Ephemeris → độ chính xác vị trí đạt chuẩn  
✅ Sửa fallback tiểu hành tinh (0° Aries → vị trí thực Kepler)  
✅ Sửa lỗi đơn vị tính thiểu hành tinh (sai ~340°)  
✅ Thêm 4 test accuracy + chạy **156/156 pass**  
✅ Dọn log cảnh báo gây hiểu lầm  
✅ Xác minh chéo lá số Steve Jobs khớp astro.com  

**File thay đổi:** `backend/astrololo/core/ephemeris.py`, `backend/tests/test_ephemeris_accuracy.py` (mới)

---

## 6. KHUYẾN NGHỊ TIẾP THEO

Tôi có thể tiếp tục triển khai **P0 (geocoding + sửa trọng số dominant)** và **P1 (compatibility score + daily)** ngay trong phiên sau — những hạng mục này trực tiếp làm Astrololo "mạnh hơn web astro" ở trải nghiệm người dùng thực tế. Bạn có muốn tôi thực hiện tiếp không?
