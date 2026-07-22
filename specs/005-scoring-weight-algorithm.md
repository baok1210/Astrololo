# Astrololo — Scoring & Weight Algorithm Spec

## 1. Mục đích
Định nghĩa chính xác thuật toán tính trọng số năng lượng $W$ cho từng hành tinh  
và ma trận so sánh lực giữa các hành tinh trong cùng một bản đồ sao.

Spec này là **implementation contract** cho:
- `interpretation/scoring.py`
- `interpretation/rules/strength_weakness_rule.py`
- Tất cả rules tham chiếu `chart.planet_weights` hoặc `W_A vs W_B`.

---

## 2. Công thức Cốt lõi

$$W = \text{Base Value} \times \text{Dignity Multiplier} \times \text{House Weight}$$

### 2.1 Base Value
Dựa trên phạm vi ảnh hưởng chiêm tinh học của hành tinh:

| Hành tinh / Điểm | Base |
|---|---|
| Sun, Moon, ASC Ruler | 1.5 |
| Mercury, Venus, Mars | 1.2 |
| Jupiter, Saturn | 1.0 |
| Uranus, Neptune, Pluto | 0.8 |
| Chiron | 1.3 |
| Ceres, Pallas, Juno, Vesta | 1.1 |
| Lilith | 0.9 |
| North Node, South Node | 0.9 |

**ASC Ruler xác định:** hành tinh cai quản cung mọc (rising sign).  
VD: ASC ở Bạch Dương → Mars; ASC ở Cự Giải → Moon.

### 2.2 Dignity Multiplier
Từ essential dignity rules:

| Trạng thái phẩm chất | Multiplier |
|---|---|
| Domicile | 1.3 |
| Exaltation | 1.3 |
| Peregrine | 1.0 |
| Detriment | 0.7 |
| Fall | 0.7 |
| Mutual Reception | 1.2 |
| Combustion | 0.6 |
| Under Sun beams (<17°) | 0.8 |

**Mutual Reception:** hai hành tinh A, B đứng ở cung mà nhau cai quản.  
VD: Mars ở Bảo Bình (Mars cai quản) + Venus ở Bạch Dương (Venus cai quản) → không phải MR.  
Mars ở Kim Ngưu (Venus cai quản) + Venus ở Bạch Dương → Mars ở Kim Ngưu là MR với Venus ở Bạch Dương.

**Combustion:** hành tinh cách Mặt Trời < 3° (orb chặt).  
**Sun beams 17°:** 3°-17° là reduced light.

### 2.3 House Weight
Từ vị trí nhà:

| Loại nhà | Số nhà | Weight |
|---|---|---|
| Angular | 1, 4, 7, 10 | 1.4 |
| Succeedent | 2, 5, 8, 11 | 1.1 |
| Cadent | 3, 6, 9, 12 | 0.8 |

### 2.4 Aspect Bonus
Nếu hành tinh nhận góc chiếu hài hòa từ benefic (Jupiter/Venus)  
hoặc góc chiếu thách thức từ malefic (Saturn/Mars) mà không được hỗ trợ:

| Điều kiện | Bonus |
|---|---|
| Nhận sextile/trine từ Jupiter | +0.1 |
| Nhận sextile/trine từ Venus | +0.1 |
| Nhận conjunction từ benefic | +0.05 (max 2 conjunctions) |
| Nhận square/opposition từ Saturn không có hỗ trợ | -0.15 |
| Nhận square/opposition từ Mars không có hỗ trợ | -0.1 |
| Nhận opposition từ Mars/Saturn đồng thời (T-Square apex) | -0.25 |

Aspect bonus cộng vào $W$ cuối cùng, nhưng clamp về [0.3, 3.0].

### 2.5 Speed / Direction Bonus
| Điều kiện | Bonus |
|---|---|
| Direct motion (không retrograde) | +0.05 |
| Retrograde | -0.1 |
| Combust | -0.15 (đã tính ở Dignity) |
| Cazimi (within Sun beams < 3.5', inside disc) | +0.3 |

---

## 3. Ví dụ Tính Toán

### 3.1 Ví dụ 1 — Mạnh
- **Mars** at Aries 17°, house 10.
- Base = 1.2, Domicile = 1.3, Angular = 1.4.
- Nhận trine từ Jupiter → +0.1
- Direct motion → +0.05

$W = 1.2 \times 1.3 \times 1.4 + 0.15 = 2.34$  
→ **hành tinh rất mạnh**

### 3.2 Ví dụ 2 — Trung bình
- **Moon** at Taurus 8°, house 3.
- Base = 1.5, Exaltation = 1.3, Cadent = 0.8.
- Retrograde → -0.1

$W = 1.5 \times 1.3 \times 0.8 - 0.1 = 1.46$  
→ **hành tinh trung bình**

### 3.3 Ví dụ 3 — Yếu
- **Mars** at Cancer 23°, house 6.
- Base = 1.2, Detriment = 0.7, Cadent = 0.8.
- Square Saturn không hỗ trợ → -0.15
- Retrograde → -0.1
- Under Sun beams → -0.05

$W = 1.2 \times 0.7 \times 0.8 - 0.3 = 0.378$  
→ **hành tinh yếu**

---

## 4. Ma trận So sánh Lực $W_A$ vs $W_B$

### 4.1 Cơ chế
Mỗi aspect pair có thể được so sánh lực:

- $W_A$: trọng số hành tinh A sau khi tính Section 2.
- $W_B$: trọng số hành tinh B sau khi tính Section 2.

| Điều kiện | Kết quả synthesis |
|---|---|
| $W_A > W_B + 0.4$ | A chi phối B. Tính chất A định hình biểu hiện B. |
| $W_A < W_B - 0.4$ | B kiềm chế/áp đặt A. B tạo rào cản cho A. |
| $|W_A - W_B| \leq 0.4$ | Cân bằng. Nội bộ xung đột, biểu hiện phụ thuộc ngữ cảnh nhà/cung. |

### 4.2 Áp dụng vào Synthesis Rule
Khi viết narrative cho aspect Mars-Saturn:
1. Đọc $W_{Mars}$, $W_{Saturn}$.
2. Nếu $W_{Mars} > W_{Saturn}$ → "Động lực hành động của bạn thường đè lên cấu trúc, bạn tạo ra thay vì tuân theo."
3. Nếu $W_{Mars} < W_{Saturn}$ → "Cấu trúc bên ngoài kiểm soát hành động, bạn cảm thấy bị kìm hãm trước khi thực hiện."
4. Nếu cân bằng → "Bạn nội bộ đấu tranh giữa muốn hành động ngay và cần có kế hoạch vững chắc."

---

## 5. Planet Weight Matrix Output

Mỗi chart sau khi evaluate sẽ có `chart.planet_weights`:

```python
chart.planet_weights = {
  "sun": {
    "W": 2.1,
    "base": 1.5,
    "dignity_multiplier": 1.0,
    "house_weight": 1.4,
    "aspect_bonus": 0.1,
    "dignity": "peregrine",
    "house_type": "angular",
    "house": 10,
    "sign": "aries",
    "retrograde": False,
  },
  "mars": {
    "W": 2.34,
    ...
  }
}
```

Engine có thể serialize `planet_weights` vào response để frontend hiển thị heatmap hoặc tooltip.

---

## 6. Strength / Weakness Table Rule

Rule `strength_weakness_rule.py` phải:
1. Lặp qua tất cả planets trong chart.
2. Tính $W$ cho từng planet theo công thức Section 2.
3. Phân loại:
   - $W \geq 2.0$ → **Mạnh**
   - $1.0 \leq W < 2.0$ → **Trung bình**
   - $0.5 \leq W < 1.0$ → **Yếu**
   - $W < 0.5$ → **Rất yếu / Suy yếu**
4. Output dạng prose, không bảng:
   - "Hành tinh mạnh nhất trong bản đồ là Sao Hỏa (W=2.34), đặt ở cung 10 tuổi Bạch Dương, tạo động lực sự nghiệp lớn."
   - "Hành tinh yếu nhất là Mặt Trăng (W=0.84), ở cung 3 tuôi Ma Kết, cảm xúc dễ bị logic kiềm chế."

### 6.1 Guardrails
- Không xuất ra bảng điểm. Chỉ xuất prose mô tả phân bố.
- Nếu 3+ planets cùng mạnh → ghi "có nhiều hành tinh mạnh, năng lượng phân tán."
- Nếu không có hành tinh nào > 1.5 → ghi "bản đồ có xu hướng thụ động, cần kích thích từ bên ngoài."

---

## 7. Pattern Override Logic

### 7.1 Stellium
Nếu ≥3 planets trong cùng 1 cung:
- Mỗi planet trong cung đó được bonus `+0.2` vào $W$.
- Tổng bonus capped tại `+0.4` mỗi planet.
**Lý do:** Stellium tập trung năng lượng, override individual weaknesses.

### 7.2 Grand Trine
- Mỗi planet trong Grand Trine nhận `+0.15`.
- Grand Trine với 3 planets cùng element → pattern bonus.
- Lưu ý: Grand Trine có thể tạo inertia, nên nếu không có planet tạo góc thách thức → penalty `-0.05` cho mỗi planet (thiếu động lực).

### 7.3 T-Square
- Apex planet (apex của T-Square):
  - Nếu $W_{apex} > 1.5$ → bonus `+0.2` (điểm tập trung xung đột, có thể vượt qua).
  - Nếu $W_{apex} \leq 1.0$ → penalty `-0.2` (áp lực lớn nhưng không đủ lực giải quyết).
- Leg planets:
  - Mỗi leg nhận `+0.05`.

### 7.4 Yod
- Apex planet nhận `+0.15` (điểm số phát triển đặc biệt).
- Base planets không bonus.

### 7.5 Grand Cross
- Mỗi planet nhận `+0.1` (cấu trúc cứng nhưng dễ căng thẳng).
- Nếu ≥2 planets retrograde trong cross → penalty `-0.1`.

### 7.6 Kite
- Apex của Grand Trine nhận `+0.1`.
- Planet tạo cánh kite nhận `+0.2`.

---

## 8. Edge Cases

### 8.1 Intercepted / Void
- Intercepted sign: planet ở cung mà cusp sign bị kẹp giữa 2 cung khác → penalty `-0.1`.
- Moon void of course: không có aspect nào trước khi rời cung → penalty `-0.05`.

### 8.2 Combustion & Cazimi
- Under Sun beams 3°-17°: $W$ bị giảm 7.5%.
- Combustion (<3°): $W$ bị giảm 15%.
- Cazimi (<3.5', trong disc): $W$ được tăng 30% thay vì giảm.

### 8.3 Stationary Retrograde
- Planet gần retrograde station (speed gần 0):
  - Retrograde stationary → $W$ giảm 5%.
  - Direct stationary → $W$ tăng 5%.

### 8.4 Mutual Reception Clamp
- Mutual reception giữa 2 planets: cả hai được multiplier 1.2.
- Nếu đồng thời có dignity khác → lấy max, không stack.

---

## 9. Implementation Checklist

### 9.1 `scoring.py`
- [ ] Function `calculate_planet_weights(chart)` trả dict `planet_weights`.
- [ ] Áp dụng Base × Dignity × House.
- [ ] Áp dụng Aspect Bonus clamp [0.3, 3.0].
- [ ] Áp dụng Pattern Override.
- [ ] Áp dụng Speed/Direction/Combustion.
- [ ] ASC Ruler detection.
- [ ] Mutual Reception detection từ `chart.planets`.

### 9.2 `strength_weakness_rule.py`
- [ ] Đọc `chart.planet_weights`.
- [ ] Sắp xếp theo $W$ giảm dần.
- [ ] Phân loại mạnh/trung bình/yếu.
- [ ] Xuất prose, không bảng.

### 9.3 `rules/*.py` khác
- [ ] Tham chiếu `W` thay vì equality assumption.
- [ ] Sử dụng so sánh $W_A$ vs $W_B$ với threshold ±0.4.

---

## 10. Test Cases

### 10.1 Unit Tests
- [ ] Mars domicile angular direct → W ≈ 2.18-2.34.
- [ ] Moon detriment cadent retrograde → W ≈ 0.84-0.95.
- [ ] Combustion Mars → -15%.
- [ ] Cazimi Mercury → +30%.
- [ ] Stellium bonus clamp.
- [ ] T-Square apex bonus/penalty.

### 10.2 Integration Tests
- [ ] 50-profile benchmark: mỗi chart có `planet_weights`.
- [ ] ASC Ruler đúng với cusp sign.
- [ ] Mutual Reception đúng với cross-check.
- [ ] Pattern Override không overflow W > 3.0.

---

## 11. Out of Scope
- Heliacal rise/set calculations.
- Traditional vs modern dignity weighting debate. Spec này dùng modern.
- Out-of-sign aspects trong scoring.
- Fixed star conjunctions weighting.

---

## 12. Glossary
- $W$ — trọng số năng lượng hành tinh.
- Dignity — phẩm chất chiêm tinh học: domicile, exaltation, detriment, fall, peregrine.
- House Weight — trọng số theo vị trí nhà: angular/succeedent/cadent.
- Pattern Override — bonus/penalty từ cấu hình đặc biệt trong bản đồ.
- ASC Ruler — hành tinh cai quản cung mọc.
- Cazimi — hành tinh ở trong đĩa Mặt Trời (<3.5').
