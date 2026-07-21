# Spec: Synthesis Engine Architecture

## Conventions
- Spec ID: `009`
- Status: Draft
- Related: `001` (Product + Synthesis Charter), `005` (Scoring Weight Algorithm)

---

## 1. Pipeline Architecture (5-Step Interpretation Flow)

The interpretation engine MUST process every chart through the following pipeline in strict order:

| Step | Name | Function | Output |
|------|------|----------|--------|
| 1 | **Input Validation Gate** | Check date/time/coordinates completeness. If missing → trigger Rectification Routine. | Validated Chart Data |
| 2 | **Primary Mapping** | Tier data into 3 layers: Tier 1 (Ascendant, Sun, Moon), Tier 2 (10 planets / 12 signs / 12 houses), Tier 3 (aspects, qualities). | Structured Chart Matrix |
| 3 | **Matrix Evaluation** | Compute energy weight W for each planet; build aspect-comparison matrix (W_A vs W_B). | Planet Weight Matrix |
| 4 | **Cross-Reference** | Link houses via House Rulers; overlay time-based data (Transits/Progressions). | Context-Linked Map |
| 5 | **Synthesis Output** | Convert logic matrix into continuous prose report + Traceability Block. | Final Narrative Report |

### Step 1 — Input Validation Gate
```
IF date OR time OR coordinates missing:
    ACTIVATE Rectification Routine
OUTPUT: Validated Chart Data
```

### Step 2 — Primary Mapping
Three-tier decomposition:
- **Tier 1:** Ascendant, Sun, Moon
- **Tier 2:** 10 planets, 12 signs, 12 houses
- **Tier 3:** Aspects, qualities

### Step 3 — Matrix Evaluation
For each planet, compute weight W using the formula in §2 below.

### Step 4 — Cross-Reference
- Dispositor chains: House X cusp sign → ruling planet → where that planet sits (another house).
- Axis symmetry analysis: always scan paired axes (1-7, 2-8, 4-10, 5-11).
- Overlay transits/progressions where available.

### Step 5 — Synthesis Output
- Generate continuous prose (not bullet lists or tables) in the Narrative section.
- Include Traceability Block listing Inputs Read and Logic Rules applied.
- Output structure per report:
  - LOGIC TRACEABILITY
  - SYNTHESIS NARRATIVE

---

## 2. Energy Weight Algorithm (W)

$$
W = \text{Base Value} \times \text{Dignity Multiplier} \times \text{House Weight}
$$

### Base Value
| Bodies | Value |
|--------|-------|
| Sun, Moon, Ascendant Ruler | 1.5 |
| Mercury, Venus, Mars | 1.2 |
| Jupiter, Saturn | 1.0 |
| Uranus, Neptune, Pluto | 0.8 |
| North Node, South Node | 0.5 (treat as background context, not dominant anchor) |
| Chiron, Vertex | 0.6 |

### Dignity Multiplier
| State | Multiplier |
|-------|-----------|
| Domicile / Exaltation | 1.3 |
| Peregrine (no strength) | 1.0 |
| Detriment / Fall | 0.7 |

### House Weight
| House Type | Houses | Weight |
|------------|--------|--------|
| Angular | 1, 4, 7, 10 | 1.4 |
| Succeedent | 2, 5, 8, 11 | 1.1 |
| Cadent | 3, 6, 9, 12 | 0.8 |

### Notes on Dignity Determination
- Use traditional (Ptolemaic) dignities where available; modern rulerships apply only for outer planets.
- A planet in its own sign (domicile) AND angular earns compounding (not additive) weight.
- Exaltation is a modifier, not a replacement for domicile — both may apply simultaneously but do not stack multiplicatively with each other, only with house weight.

---

## 3. Cross-Reference & Conflict Logic (Synthesis Logic)

### Mandatory Rule Structure
Every synthesis rule MUST have three components:
1. **Inputs Read** — what data the rule consumes
2. **Logic Analysis** — the conditional/weight comparison
3. **Narrative Link** — the text output connecting the analysis to human experience

### Force Comparison Mechanism
- Compute W_A and W_B for the two bodies/houses under analysis.
- **IF W_A > W_B:** Nature of A dominates and shapes expression of B.
- **IF W_A < W_B:** Nature of A is constrained by B, or B imposes restrictions/barriers on A.
- **IF |W_A − W_B| ≤ 0.2:** Treat as balanced tension — neither dominates; express as "dialectic" or "dual motivation" in narrative.

### Strict Prohibition
**NO fixed 1-to-1 template mapping.** Forbidden patterns include:
- `planet = X, sign = Y → fixed string`
- `house = Z → fixed paragraph`

Rules MUST compose dynamically from keyword contexts + weight comparisons + axis context.

---

## 4. Synthetic Rules (Reference Catalog)

The following rule families are REQUIRED in the engine. Each produces `RuleResult` with `category`, `tags`, `evidence`, `score`, and `text_vi`/`text_en`.

| Rule ID | Category | Purpose |
|---------|----------|---------|
| R-01 | `aspect_synthesis` | Per-planet aspect groups (conjunction/opposition/square/trine/sextile/key) |
| R-02 | `house_placement` | Planet-in-house with cusp proximity |
| R-03 | `planet_in_sign` | Planet dignity + sign expression |
| R-04 | `cross_synthesis` | 6-layer abduction: sign_repetition, house_cusp_worldly, planet_governance, contrarian_nuance, tension, life_theme |
| R-05 | `rulership_axes` | House ruler chain links + paired axis symmetry (1-7, 2-8, 4-10, 5-11) + axis tilt imbalance |
| R-06 | `karmic_psych` | Vertex (fate), Chiron+Vertex co-position, Node grading (South mature / North nascent), Script-vs-Core (ASC mask vs Sun/Moon core), social outcome links (10→7), functional keyword composer |
| R-07 | `pattern_release` | Configuration release points (structural relief valves in the chart) |
| R-08 | `executive_summary` | Condensed top-line synthesis for at-a-glance reading |
| R-09 | `custom_synthesis` | Fallback dynamic synthesis when no rule covers a planet pair |

### Suppression Rules
- If `W_A == 0` (no strength) AND `W_B ≤ 0.5`, suppress the pair from the dominant narrative. Do not fabricate expression for weak combinations.
- North/South Node commentary MUST be grouped with the axis ruler, not presented as standalone planetary expressions.

---

## 5. Output Standard (Guardrails)

### Report Structure
1. **LOGIC TRACEABILITY**
   - Enumerate all Inputs Read (which planets, houses, aspects, weights, axes).
   - Enumerate all Logic Rules applied (rule IDs + brief description of comparison).
   - Format: table or bullet list (allowed in Traceability Block only).

2. **SYNTHESIS NARRATIVE**
   - **Continuous prose only.** No numbered lists, no bullet points, no markdown tables in this section.
   - **Pronouns:** Always use second-person singular ("bạn" in VI, "you" in EN).
   - **Probabilistic language:** ALWAYS hedge with "có thể", "thường", "xu hướng", "có khả năng". NEVER assert absolute identity ("Bạn là người XYZ").
   - **Tone:** Neutral, descriptive, non-judgmental. Avoid psychological diagnosis language ("rối loạn", "phụ thuộc"). Use structural/experiential framing instead.
   - **Length:** Per chart, Narrative MUST be between 800–3000 words. Below 800 → incomplete synthesis. Above 3000 → dilute signal with noise.

### Leak Token Prohibition
The following tokens MUST NOT appear in any output layer:
- "18+"
- "sensual"
- "desire" (when used as a standalone dominant descriptor without structural context)
- Any term functioning as erotic innuendo in Vietnamese cultural context.

Violation of §5 prose rules in any rule class constitutes a `REVIEW_BLOCK` on the release pipeline.

---

## 6. Engine Assembly Order

Rules execute in descending `priority` (highest first). Within same priority, results sort by `score` descending.

**Mandated category order in final report:**

1. `executive_summary` (priority 1)
2. `chart_shape` (1)
3. `micro_synthesis` (2)
4. `cross_synthesis` (3)
5. `rulership_axes` (4)
6. `synthesis` (5)
7. `karmic_psych` (6)
8. `pattern_release` (7)
9. `strength_weakness` (8)
10. `fixed_stars` (8)
11. `sun_moon` (8)
12. `dominant_planet` (8)
13. `part_of_fortune` (8)
14. `dispositor` (8)
15. `pattern` (9)
16. `combination` (9)
17. `house_placement` (10)
18. `house_distribution` (10)
19. `dignity` (10)
20. `element` (10)
21. `quality` (10)
22. `planet_in_sign` (10)
23. `planet_in_house` (10)
24. `house_cusp` (10)
25. `aspect` (10)
26. `midpoints` (10)
27. `moon_sign` (10)
28. `node_axis` (10)
29. `mc_ic_axis` (10)
30. `life_area` (10)
31. `aspect_group` (10)
32. `encyclopedia` (10)

New categories added after this spec MUST be assigned a priority slot and inserted into this ordered list. Failure to insert causes silent drop (prior §3 wiring gap precedent).

---

## 7. Data Contracts

### ChartData (Pydantic Model)
- `subject_name: str`
- `chart_type: str` ("natal", "transit", "synastry", "composite")
- `datetime_utc: datetime`
- `julian_day: float`
- `house_system: str`
- `node_type: str`
- `houses: List[Dict]` — cusps as degrees + sign
- `planets: List[BodyPosition]` — name, longitude, sign, house, body_type, speed, retrograde flag
- `aspects: List[AspectData]` — planet A, planet B, type, orb, exactness
- `midpoints: List[MidpointData]`
- `ascendant: float` + `ascendant_sign: str`
- `mc: float` + `mc_sign: str`
- `element_distribution` + `quality_distribution`
- `dispositor: DispositorResult`
- `part_of_fortune: Optional[Dict]`
- `vertex: Optional[Dict]` — longitude, sign, sign_vi, house, position_in_sign
- `is_daytime: bool`
- `moon_phase: str`

### RuleResult (Pydantic Model)
- `title_vi`, `title_en: str`
- `text_vi`, `text_en: str`
- `score: float`
- `priority: int`
- `category: str` — MUST match a key in engine's `section_order`
- `tags: List[str]`
- `evidence: List[Dict] | None`
- `metadata: Dict[str, Any] | None`

---

## 8. Registry & Wiring Contract

Every rule class MUST:
1. Call `RuleRegistry.register(MyRule())` at module bottom (side-effect import).
2. Live in `astrololo/interpretation/rules/<name>_rule.py`.
3. Be listed in `registry.py`'s `_RULE_MODULES`.

The engine `InterpretationEngine` reads from `RuleRegistry.get_rules()`. Rules NOT in `_RULE_MODULES` silently do not execute — this is the required wiring pattern.

Adding a new category requires updating **three** places atomically:
1. `engine.py` → `section_order` list
2. `engine.py` → `category_titles` dict
3. `frontend/src/components/InterpretationView.tsx` → `SECTION_TITLES` + `SECTION_COLORS`

Failure to update all three defaults the section to empty or untitled.

---

## Open questions
- Rectification Routine algorithm (not yet specified).
- Transit/Progression overlay time resolution (yearly? monthly? daily?).
- LLM-assisted synthesis fallback (if rules cover <70% of chart weight, invoke generative model — requires AI circuit breaker per spec `007`).
