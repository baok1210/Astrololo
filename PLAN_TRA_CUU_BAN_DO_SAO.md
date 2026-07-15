# PLAN: tra-cuu-ban-do-sao-1 — Full Natal Report (theo chuẩn MystechX)

**Ngày:** 2026-07-14
**Mục tiêu:** Nâng Astrololo từ "engine luận giải kỹ thuật" → "bản báo cáo lá số đọc được như bản mẫu MystechX" (Đoàn Việt Bảo).

---

## 1. SO SÁNH THỰC TẾ (chạy 1996-11-15 6:30 HN)

| Mục mẫu | Astrololo hiện tại | Trạng thái |
|---|---|---|
| A1 Mặt Trời trong cung | `planet_in_sign` (Sun in Scorpio: "mãnh liệt, sâu sắc...") | ✅ CÓ (prose ngắn) |
| A2 Mặt Trăng trong cung | Có position, **thiếu prose sâu** | ⚠️ THIẾU prose |
| A3 Cung Mọc + hành tinh cai quản | `ascendant_rule` + Pluto nhà 1 | ✅ CÓ |
| A4 Bán cầu | `hemisphere_rule` | ✅ CÓ |
| A5 Nguyên tố / Tính chất | `element` + `quality` | ✅ CÓ |
| B6–B19 (14 khía cạnh đời sống + **điểm 0–100**) | **KHÔNG CÓ** | ❌ THIẾU (core gap) |
| C20 Góc hợp nổi bật | `aspect` phẳng (50 items) | ⚠️ CHƯA phân nhóm |
| C21 Hài hòa / C22 Thử thách | `aspect` phẳng | ⚠️ CHƯA phân nhóm |
| Tọa độ JPL chính xác | pyswisseph (DE431-equivalent) | ✅ CÓ |

**Kết luận:** Astrololo đã có nền (20 sections, 22 planets, prose EN/VI). Nhưng **chưa phải là "bản báo cáo đọc được"** vì thiếu: (1) prose sâu cho Mặt Trăng, (2) **14 life-area scoring 0–100**, (3) phân nhóm góc hợp.

---

## 2. KIẾN TRÚC `tra-cuu-ban-do-sao-1`

### Module mới
1. **`analysis/life_areas.py`** — tính **14 khía cạnh** bằng cách aggregate planets trong houses tương ứng + dignity + aspects:
   - B6 Công danh (Nhà 10 + Mặt Trời + Sao Thổ/Thiên Vương)
   - B7 Bản thân (Nhà 1 + ASC + Mặt Trời)
   - B8 Tình yêu (Nhà 5 + Venus + Sao Hỏa)
   - B9 Tài chính (Nhà 2 + Sao Kim + Sao Mộc)
   - B10 Chuyển hóa (Nhà 8 + Pluto)
   - B11 Xã hội (Nhà 11 + Sao Thiên Vương)
   - B12 Gia đình (Nhà 4 + Mặt Trăng)
   - B13 Con cái (Nhà 5)
   - B14 Sức khỏe (Nhà 6 + Sao Hỏa)
   - B15 Học tập (Nhà 9 + Sao Thủy)
   - B16 Giao tiếp (Nhà 3 + Sao Thủy)
   - B17 Hôn nhân (Nhà 7 + Venus)
   - B18 Tiềm thức (Nhà 12 + Sao Hải Vương)
   - B19 Di chuyển (Nhà 9 + Sao Thủy)
   - Mỗi area → **score 0–100** (dựa trên: planet strength × dignity weight × harmonious aspect bonus − challenging penalty).
2. **`interpretation/rules/life_area_rule.py`** — rule priority thấp, generate 14 items với prose VI/EN (từ corpus `house_*` + `planet_in_house` đã có).
3. **`interpretation/rules/aspect_group_rule.py`** — tách `aspect` thành 3 nhóm: nổi bật (tight orb <2° hoặc liên quan ASC/MC), hài hòa (trine/sextile), thử thách (square/opposition/quincunx).
4. **`moon_sign_rule.py`** — prose sâu cho Mặt Trăng (dùng corpus `planet_in_sign` moon files).
5. **Frontend `ReportPanel.tsx`** — render báo cáo theo cấu trúc A1→C22, hiển thị **score badge 0–100** mỗi life-area (giống mẫu).

### Scoring logic (đơn giản, KISS)
```
score(area) = clamp(
  50
  + 10 * sum(dignity_weight(planet in area_houses))
  + 5  * harmonious_aspects_involving_area_planets
  - 5  * challenging_aspects_involving_area_planets
  + 3  * (planet_count_in_area_houses)
, 0, 100)
```
Tái dùng `ChartScorer` (đã có `BODY_WEIGHT`) để nhất quán.

---

## 3. GIAI ĐOẠN THỰC HIỆN

| Phase | Việc | Verify |
|---|---|---|
| P0 | `life_areas.py` + unit test scoring (Đoàn Việt Bảo → Công danh ~89, Bản thân ~84 như mẫu) | pytest |
| P1 | `life_area_rule.py` + `moon_sign_rule.py` (prose VI/EN từ corpus) | ad-hoc |
| P2 | `aspect_group_rule.py` (3 nhóm) | ad-hoc |
| P3 | `ReportPanel.tsx` + tab "Báo Cáo" (A1→C22 + score badges) | npm build + browser |
| P4 | Re-bake EN YAML (moon prose) + CHANGELOG + commit/push | git |

**Ưu tiên:** P0 trước (scoring là core gap). P1–P3 song song sau.

---

## 4. RỦI RO
- Score 0–100 khó khớp Y CHÍNH xác với mẫu (mẫu dùng thuật toán riêng). → Chấp nhận **tương đối** (Tốt/Xấu), khồng cần = 89.
- Prose sâu cần corpus `moon_in_*` (có 12 files trong crawl). → Dùng retriever.
- EN chưacó moon prose đầy đủ → fallback keyword (như hiện tại).

---

## 5. ĐÁNH GIÁ CUỐI
Astrololo **đã luân giải được ~70%** cấu trúc mẫu (vị trí, cung, nhà, góc, nguyên tố, bán cầu, ASC). Để đạt chuẩn `tra-cuu-ban-do-sao-1` cần bổ sung **14 life-area scoring + prose sâu Mặt Trăng + phân nhóm góc hợp** — đã có plan ở trên.
