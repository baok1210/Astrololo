# Astrololo — Chart Model Schema Spec

## 1. Mục đích
Định nghĩa chính xác data model cho chart, subject, planets, aspects,  
và các computed fields. Spec này là contract giữa:
- `analysis/*.py` — producers
- `interpretation/rules/*.py` — consumers
- `api/main.py` — serializer
- Frontend — renderer

Mọi thay đổi breaking phải cập nhật spec này trước khi merge.

---

## 2. `AstrologicalSubject`

```python
class AstrologicalSubject(BaseModel):
    name: str
    year: int
    month: int
    day: int
    hour: int
    minute: int
    latitude: float
    longitude: float
    timezone_str: str = "UTC"
    city: Optional[str] = None
    nation: Optional[str] = None
    julian_day_ut: Optional[float] = None
    julian_day_tt: Optional[float] = None
    delta_t: Optional[float] = None
```

### 2.1 Properties
- `birth_datetime`: localized datetime trong timezone_str.
- `birth_datetime_utc`: chuyển sang UTC.

### 2.2 Constraints
- `timezone_str` phải là tzdata name hợp lệ: `Asia/Ho_Chi_Minh`, `Europe/London`, `UTC`.
- `latitude ∈ [-90, 90]`, `longitude ∈ [-180, 180]`.
- `year ∈ [1900, 2100]`.

---

## 3. `BodyPosition` (alias `PlanetPosition`)

```python
class BodyPosition(BaseModel):
    body_type: Literal["planet", "node", "angle", "fixed_star"] = "planet"
    name: str                          # key trong PLANETS dict
    name_vi: str                       # tên VI
    name_en: str = ""                  # tên EN
    longitude: float                   # 0-360 degrees
    latitude: float = 0.0
    distance: float = 0.0
    speed: float = 0.0                 # degrees/day; negative = retrograde
    sign: str                          # sign key, e.g. "aries"
    sign_name_vi: str                 # "Bạch Dương"
    sign_name_en: str = ""            # "Aries"
    position_in_sign: float            # 0-30 degrees
    house: int = 0                     # 1-12; 0 = chưa xác định / góc
    is_retrograde: bool = False
    element: str = ""
    quality: str = ""
    dignity_score: int = 0             # from essential dignity rules
    dignity_label: str = "neutral"     # domicile/exaltation/detriment/fall/peregrine/neutral
    minor_dignities: List[str] = []   # e.g. ["mutual_reception", "triplicity"]
    declination: float = 0.0
    cusp_proximity: Optional[Dict[str, Any]] = None
    definition_note: Optional[str] = None  # clarifies non-standard bodies
    # Jyotish fields (tropical charts bỏ qua)
    sidereal_longitude: Optional[float] = None
    sidereal_sign: Optional[str] = None
    sidereal_sign_degree: Optional[float] = None
    nakshatra: Optional[str] = None
    nakshatra_vi: Optional[str] = None
    nakshatra_pada: Optional[int] = None
    nakshatra_lord: Optional[str] = None
    graha_name: Optional[str] = None
    graha_name_vi: Optional[str] = None
    tattwa: Optional[str] = None
    guna: Optional[str] = None
    jyotish_dignity: Optional[str] = None
```

### 3.1 Construction Rules
- `body_type="planet"` cho tất cả physical planets + asteroids + calculated points được rules hiện tại xử lý như planet.
- `body_type="node"` cho North/South Node.
- `body_type="angle"` cho ASC, MC, DSC, IC.
- `body_type="fixed_star"` cho fixed stars gần conjunct.
- `house=0` nghĩa là chưa được assign house; xảy ra khi `houses.py` chưa chạy hoặc body là angle không belong vào nhà.

---

## 4. `HouseData`

```python
class HouseData(BaseModel):
    house_number: int          # 1-12
    cusp_degree: float         # 0-360
    sign: str                  # sign key at cusp
    sign_name_vi: str          # "Bạch Dương"
    is_angular: bool = False
    is_succeedent: bool = False
    is_cadent: bool = False
```

### 4.1 Relationships
- `HouseData.sign` cấu thành `House Ruler`: ruler = planet cai quản sign đó.
- `House Ruler` là `BodyPosition` nằm ở một house khác → tạo `House Ruler Placement`.

---

## 5. `AspectData`

```python
class AspectData(BaseModel):
    planet1: str                    # BodyPosition.name của planet A
    planet2: str                    # BodyPosition.name của planet B
    aspect_type: str                # "conjunction", "sextile", "square", "trine", "opposition", "quincunx", ...
    aspect_name_vi: str             # "Hợp", "Lục Hợp", "Vuông Góc", ...
    angle: float                    # exact angle, e.g. 90.0
    orb: float                      # deviation từ exact, degrees
    exact: bool = False             # orb <= 1°
    orb_formatted: str = ""         # "2°04'"
    nature: str = "neutral"         # "harmonious", "challenging", "neutral"
    weight: int = 0                 # aspect importance score
    applying: bool = False          # planet đang tiến đến exact
    separating: bool = False        # planet đang rời xa exact
```

### 5.1 Nature Mapping
| aspect_type | nature |
|---|---|
| conjunction | neutral |
| sextile | harmonious |
| square | challenging |
| trine | harmonious |
| opposition | challenging |
| quincunx | challenging |
| semisextile | neutral |
| semisquare | challenging |
| sesquiquadrate | challenging |
| quintile | neutral |

---

## 6. `Chart`

```python
class Chart(BaseModel):
    subject: AstrologicalSubject
    planets: List[BodyPosition]    # includes planets, nodes, angles, fixed stars
    houses: List[HouseData]        # 12 houses
    aspects: List[AspectData]      # all detected aspects
    angles: Dict[str, BodyPosition] # ASC, MC, DSC, IC as angle type
    house_cusps: List[float]       # degree cusps 1-12
    interpretation: Optional[Dict[str, Any]] = None
    planet_weights: Optional[Dict[str, Dict[str, Any]]] = None
    # Optional computed fields
    part_of_fortune: Optional[Dict[str, Any]] = None
   Composite: Optional[Any] = None # synastry only
    dasha: Optional[Any] = None    # jyotish only
    aspects_by_planet: Optional[Dict[str, List[AspectData]]] = None
```

### 6.1 Invariants
- `len(houses) == 12` cho western; jyotish có thể khác.
- `planets` luôn chứa ASC, MC, DSC, IC ở cuối hoặc được mark `body_type="angle"`.
- `aspects` không duplicate: mỗi pair chỉ có 1 aspect record, dù có thể có nhiều aspect types.
- `planet_weights` được tính sau chart creation, trước interpretation.

### 6.2 Computed Fields

#### 6.2.1 `aspects_by_planet`
```python
{
  "sun": [AspectData, AspectData, ...],
  "moon": [...],
  ...
}
```
Dùng cho aspect_synthesis_rule để lookup nhanh aspects của từng planet.

#### 6.2.2 `planet_weights`
```python
{
  "sun": {
    "W": 2.1,
    "base": 1.5,
    "dignity_multiplier": 1.0,
    "house_weight": 1.4,
    "aspect_bonus": 0.1,
    "pattern_bonus": 0.0,
    "dignity": "peregrine",
    "house_type": "angular",
    "house": 10,
    "sign": "aries",
    "retrograde": False,
    "final_W": 2.1,
  }
}
```

#### 6.2.3 `part_of_fortune`
```python
{
  "longitude": 123.45,
  "sign": "leo",
  "sign_name_vi": "Sư Tử",
  "house": 7,
  "formula": "ASC + Moon - Sun (day)"  # hoặc "ASC + Sun - Moon (night)"
}
```

---

## 7. Supporting Models

### 7.1 `ElementDistribution`
```python
class ElementDistribution(BaseModel):
    fire: float = 0
    earth: float = 0
    air: float = 0
    water: float = 0
    dominant: Optional[str] = None
    deficient: Optional[str] = None
```

### 7.2 `QualityDistribution`
```python
class QualityDistribution(BaseModel):
    cardinal: float = 0
    fixed: float = 0
    mutable: float = 0
    dominant: Optional[str] = None
    deficient: Optional[str] = None
```

### 7.3 `DispositorResult`
```python
class DispositorResult(BaseModel):
    chain: Dict[str, str] = {}             # planet -> its dispositor planet
    final_dispositor: Optional[str] = None # highest in chain
    final_dispositors: List[str] = []      # mutual reception final dispositors
    mutual_receptions: List[tuple] = []    # [(planet_a, planet_b), ...]
```

### 7.4 `AspectPattern`
```python
class AspectPattern(BaseModel):
    name: str                    # "Grand Trine", "T-Square", ...
    name_vi: str                 # "Tam Hợp Vĩ Đại", "T-Square", ...
    score: int                   # pattern strength score
    planets: List[str]           # participating planet names
    description_vi: str = ""
    description_en: str = ""
```

### 7.5 `MidpointData`
```python
class MidpointData(BaseModel):
    body1: str
    body2: str
    midpoint: float             # degree
    sign: str
    sign_vi: str
    position_in_sign: float
```

### 7.6 `DashaPeriod` (Jyotish)
```python
class DashaPeriod(BaseModel):
    graha: str
    graha_name_vi: str = ""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    level: int = 0              # 0=mahadasha, 1=antardasha, ...
```

---

## 8. Field Naming Convention

### 8.1 Python Internal
- `snake_case` cho tất cả fields.
- Boolean prefix `is_`: `is_retrograde`, `is_angular`, `is_daytime`.
- Collection prefix plural: `planets`, `houses`, `aspects`.

### 8.2 JSON Serialization
- `model_dump()` trả về `snake_case` keys.
- Frontend consume `snake_case`; không convert sang camelCase.
- Enum values lowercase: `"domicile"`, `"exaltation"`, `"detriment"`, `"fall"`, `"peregrine"`.

---

## 9. Validation Rules

### 9.1 Pydantic Validators
- `longitude`: `0 <= longitude < 360`
- `house`: `1 <= house <= 12` hoặc `0` cho unassigned
- `speed`: float, no range bound nhưng phải finite
- `position_in_sign`: `0 <= position_in_sign < 30`
- `orb`: `0 <= orb <= 15`
- `weight`: `int, >= 0`

### 9.2 Cross-Field Validation
- Nếu `body_type="angle"` → `house=0`, `speed=0`, `dignity_score=0`.
- Nếu `body_type="node"` → `house` có thể có, nhưng `dignity_score=0`.
- Nếu `is_retrograde=True` → `speed < 0`.
- Nếu `exact=True` → `orb <= 1.0`.

---

## 10. Serialization Contract

### 10.1 API Serialization
Tất cả chart endpoints trả về:
```json
{
  "success": true,
  "data": <chart.model_dump()>
}
```

`model_dump()` include:
- `subject`
- `planets`
- `houses`
- `aspects`
- `angles`
- `house_cusps`
- `interpretation`
- `planet_weights`
- `part_of_fortune`
- `aspects_by_planet`

### 10.2 Interpretation Serialization
```json
{
  "summary": "string",
  "sections": [
    {
      "title": "string",
      "content": "string",
      "priority": 1
    }
  ],
  "overall": "string"
}
```

---

## 11. Backward Compatibility

### 11.1 Legacy Aliases
- `PlanetPosition = BodyPosition` vẫn tồn tại.
- Code cũ dùng `planet.sign` thay vì `body_position.sign` vẫn works vì field name giữ nguyên.

### 11.2 Deprecation Policy
- Field mark `deprecated` → giữ ít nhất 2 minor versions trước khi xóa.
- Mỗi deprecated field phải có log warning khi access/serialize.

---

## 12. Implementation Checklist

### 12.1 `models/chart.py`
- [x] `BodyPosition`
- [x] `HouseData`
- [x] `AspectData`
- [x] `ElementDistribution`
- [x] `QualityDistribution`
- [x] `DispositorResult`
- [x] `AspectPattern`
- [x] `MidpointData`
- [x] `DashaPeriod`
- [ ] Pydantic validators cho cross-field rules (Section 9.2)
- [ ] `planet_weights` model class thay vì plain dict

### 12.2 `models/subject.py`
- [x] `AstrologicalSubject`
- [ ] `birth_datetime_utc` validator đảm bảo timezone validity

### 12.3 `core/points.py`
- [x] `build_planets()`, `build_additional()`, `build_angles()`
- [ ] Ensure all `BodyPosition` constructions respect cross-field invariants

---

## 13. Related Specs
- `001-astrololo-spec.md` — interpretation pipeline
- `002-api-contract.md` — API serialization
- `005-scoring-weight-algorithm.md` — planet_weights calculation

---

## 14. Glossary
- `BodyPosition` — unified model cho mọi celestial body/angle/fixed star.
- `house=0` — unassigned; dùng cho angles hoặc khi house calculation chưa hoàn tất.
- `model_dump()` — Pydantic v2 serialization sang dict.
- `aspects_by_planet` — index aspect theo từng planet để rule lookup nhanh.
