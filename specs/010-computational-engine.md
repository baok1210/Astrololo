# Spec: Computational Astrology Engine

## Conventions
- Spec ID: `010`
- Status: Draft
- Related: `005` (Scoring Weight Algorithm), `009` (Synthesis Engine Architecture), `007` (Error & Fallback)

---

## 1. Astronomical Engine

### 1.1 Coordinate Standardization
MUST integrate Swiss Ephemeris (via `pyswisseph`) for all calculations.

| Concern | Requirement |
|---------|-------------|
| Zodiac | Tropical (default) AND Sidereal with selectable Ayanamsha (Lahiri, Fagan/Bradley). |
| House Systems | Placidus, Whole Sign, Koch, Equal, Regiomontanus, Campanus — selectable per `ChartRequest.house_system`. |
| Bodies | 10 major planets + Chiron, Ceres, Pallas, Juno, Vesta, Lilith, North Node, South Node, Part of Fortune, Vertex, Ascendant, Midheaven. |

### 1.2 Aspect Matrix Engine

#### Orb Tolerance by Body Type
- **Major aspects** (Conjunction, Opposition, Trine, Square, Sextile): orb 6°–10°. Sun/Moon pairs allow 10°–12°.
- **Minor aspects** (Semi-Sextile, Quincunx, Semi-Square, Sesquiquadrate): orb 1°–2°. Configurable via `ChartRequest.orb_*` fields (see spec `005`).

#### Applying vs. Separating
- Compute relative velocity to classify aspect status:
  - **Applying** — aspect narrowing toward exact; energy accumulating.
  - **Separating** — aspect widening from exact; energy dissipating.
  - **Exact** — within user-configurable exactness threshold.

#### Aspect Status MUST be reported in `AspectData.status` for every aspect entry.

---

## 2. Feature Extraction Engine

### 2.1 Dignity & Debility Scoring (Ptolemaic Standard)

#### Essential Dignities

| State | Points |
|-------|--------|
| Domicile (Rulership) | +5 |
| Exaltation | +4 |
| Triplicity | +3 |
| Term | +2 |
| Face (Decan) | +1 |
| Detriment | −5 |
| Fall | −4 |
| Peregrine (no essential dignity) | 0 |

#### Accidental Dignities

| Condition | Points |
|-----------|--------|
| Angular house (1, 4, 7, 10) | +5 |
| Succedent house (2, 5, 8, 11) | +3 |
| Cadent house (3, 6, 9, 12) | +1 |
| Retrograde | −5 |
| Combustion (within 15° of Sun, excluding Cazimi) | −5 |
| Cazimi (within 17′ of Sun) | +5 |

#### Dignity Composite Notes
- Domicile + angular **do not stack additively**; take the higher weight.
- Exaltation is a modifier; does not replace domicile. Both may apply simultaneously.
- Peregrine + cadent = weakest state; suppress from dominant narrative (see §3.1 Layering Rule).

### 2.2 Dominant Planet Algorithm

$$
Score_{Planet} = w_1 \cdot DignityScore + w_2 \cdot AspectDensity + w_3 \cdot Angularity
$$

- `DignityScore`: essential + accidental total.
- `AspectDensity`: count of major aspects received (weight 1 each).
- `Angularity`: 1 if angular, 0.5 if succedent, 0.25 if cadent.
- Weights `w1=0.5, w2=0.3, w3=0.2` are defaults; MUST be configurable via engine settings if linked to spec `005`.

### 2.3 Geometric Pattern Recognition (Graph Theory)

The engine MUST detect and record the following patterns in `chart.aspect_patterns`:

| Pattern | Detection Logic |
|---------|----------------|
| Grand Trine | 3 planets forming 3 × 120° (±orb) |
| T-Square | 2 planets opposite (180°) + both square (90°) a 3rd |
| Grand Cross | 2 pairs of oppositions + 4 squares |
| Yod | 2 planets sextile (60°) + both quincunx (150°) to apex |
| Stellium | ≥3 bodies in same sign **or** same house within ≥8° longitudinal span |

**Stellium scope:** include planets **and** angles (ASC/MC) **and** major points (Node, Lilith) in the same sign/house. Exclude minor points (Vertex, Chiron) from stellium count.

---

## 3. Priority Hierarchy & De-conflicting Engine

### 3.1 Priority Matrix

Rules MUST be executed and results ranked in this order:

| Level | Factor |
|-------|--------|
| Cấp 1 | Angular house placements, chart ruler, Sun, Moon |
| Cấp 2 | Special geometric patterns (T-Square, Stellium, Yod, Grand Cross) |
| Cấp 3 | Highest `DominantScore` planets |
| Cấp 4 | Singletons, minor aspects |

### 3.2 De-conflicting Rules

#### Layering Rule
- When two planetary expressions conflict (e.g., Solar Leo outward confidence vs. Lunar Cancer inward sensitivity), the engine MUST NOT output two independent paragraphs.
- Output **one integrated paragraph** that names both layers explicitly: the outer/developmental layer (Sun) and the inner/emotional layer (Moon).
- Template: "Thể hiện bên ngoài là [Sun expression], nhưng động lực nội tâm lại cần [Moon expression]."

#### Override Rule
- When factor A has strictly higher `DominantScore` than factor B AND A is angular:
  - A's expression modifies rather than merely coexists with B's.
  - Narrative MUST reflect dominance: A shapes how B manifests.
- If |DominantScore_A − DominantScore_B| ≤ 0.15: treat as balanced — use dialectic language ("vừa... vừa..." in VI; "both... and..." in EN).

#### Suppression Rule
- A planet with DignityScore ≤ −8 **AND** in a cadent house MUST NOT be cited as a dominant personality driver.
- Such planets MAY appear only as background context or challenge notes, not as trait-defining anchors.

---

## 4. Predictive & Relationship Modules

### 4.1 Dynamic Time Engine

| Module | Method | Tolerance |
|--------|--------|-----------|
| Transits | Compare current planet longitudes to natal positions by target date | Outer planets (Jupiter–Pluto) ≤ 1.5°; inner planets per user-configured orb |
| Secondary Progressions | Day-for-Year: progressed JD = birth JD + (age × 1 day) | Target: progressed Moon house/sign changes; report key shifts |
| Solar Return | Find exact JD when Sun returns to natal longitude (tropical) within ±60 seconds using SWISSEPH `swe_solcross_ut` with binary-search fallback | ±1 minute absolute |

### 4.2 Synastry & Composite Engine

| Concern | Requirement |
|---------|-------------|
| Synastry overlay | For every planet in Chart A, compute house placement in Chart B. Output `house_overlays.{a_in_b, b_in_a}`. |
| Composite chart | Midpoint longitude for each body/angle between two charts. Build full `ChartData` from midpoints, run `InterpretationEngine`. |
| Aspect matrix | Compare all bodies of Chart A against all bodies of Chart B. Report major aspects only unless `include_minor_aspects=true`. |

---

## 5. NLP & Guardrail Pipeline

### 5.1 RAG Architecture (Preferred; AI-optional)

```
[Natal JSON] → [Feature Extractor] → [Structured JSON] → [Retriever]
                                                              │
                                                     [Vector DB lookup]
                                                     (label metadata:
                                                      Planet/Sign/House/Aspect/Weight)
                                                              │
                                                     [Context Assembly]
                                                     (filter by W score
                                                      threshold ≥ 0.6)
                                                              │
                                                     [Prompt Builder]
                                                     (inject JSON + traceability
                                                      rules + prose guardrails)
                                                              │
                                                     [LLM Editor Role]
                                                     (NO generative astrology —
                                                      ONLY editorial connector)
                                                              │
                                                     [Continuous Prose]
                                                     + [Traceability Block]
```

**LLM Role Constraint:** The LLM MUST NOT invent astrological theory. It is an editor that connects pre-computed structural facts into fluent prose. If the retriever returns no matching passages for a rule, emit a keyword-composed fallback via functional template (no LLM hallucination).

### 5.2 Guardrail Layer

| Check | Failure Action |
|-------|---------------|
| Regex cross-check: every sign/planet/house mentioned in prose MUST match chart JSON exactly | Reject output; trigger regenerate with constraint prompt |
| Prose format: no numbered lists, no bullets, no tables inside Narrative section | Reject; force prose formatter |
| Discourse marker requirement: "có thể", "thường", "xu hướng", "có khả năng" MUST appear ≥ 2× per 500 words | If absent, append probabilistic hedge sentence |
| Leak token prohibition | REJECT_BLOCK — do not include in any output layer |

### 5.3 LLM Circuit Breaker (spec `007` integration)
- If LLM provider returns error or latency > 8 s: fall back to **keyword-composed narrative** (no LLM).
- Fallback MUST disable only for the failing section, not the entire report.
- Log fallback trigger in `chart.validation.fallback_log` (list of section names + timestamp).

---

## 6. Inter-Engine JSON Data Contract

All subsystems MUST communicate via the following schema:

```json
{
  "planetary_positions": [
    {
      "id": "sun",
      "longitude": 289.5,
      "sign": "Scorpio",
      "sign_vi": "Bọ Cạp",
      "house": 5,
      "degree": 19.5,
      "retrograde": false,
      "speed": 0.98,
      "body_type": "planet",
      "dignity_score": 3
    }
  ],
  "aspect_list": [
    {
      "body_a": "sun",
      "body_b": "moon",
      "aspect": "square",
      "orb": 1.2,
      "exactness": 0.78,
      "status": "applying",
      "weight_a": 2.4,
      "weight_b": 3.1
    }
  ],
  "dignity_scores": { "sun": 3, "moon": -2, "mercury": 5 },
  "patterns_detected": ["T-Square", "Stellium_H10"],
  "conflict_resolution_rules": [
    "Sun expression shapes Moon via higher angular weight",
    "Layer Sun (outer) and Moon (inner) into single paragraph"
  ],
  "focus_topics": "NATAL"
}
```

| Field | Type | Contract Note |
|-------|------|---------------|
| `planetary_positions` | Array[Object] | MUST include `id`, `longitude`, `sign`, `sign_vi`, `house`, `degree`, `retrograde`, `speed`, `body_type`, `dignity_score` |
| `aspect_list` | Array[Object] | MUST include `body_a`, `body_b`, `aspect`, `orb`, `exactness`, `status`, `weight_a`, `weight_b` |
| `dignity_scores` | Map<String, Int> | Essential + accidental total; MUST be computed before synthesis |
| `patterns_detected` | Array[String] | Pattern IDs from spec §2.3; MUST be populated before Rule Engine |
| `conflict_resolution_rules` | Array[Directives] | Directives from De-conflicting Engine (§3.2) for LLM/Rule guidance |
| `focus_topics` | StringEnum | `NATAL`, `TRANSIT_YYYY`, `SOLAR_RETURN_YYYY`, `PROGRESSION_AGE`, `SYNASTRY`, `COMPOSITE` |

---

## 7. Implementation Order (Recommended)

1. **Phase 1**: §1.2 (Aspect Matrix with applying/separating) → touches `analysis/aspect_calculator.py`.
2. **Phase 2**: §2.1 (Dignity scoring) → new module `scoring/dignity.py`, integrate into `points.py`.
3. **Phase 3**: §2.2 + §2.3 (Dominant planet + patterns) → `scoring/dominant.py`, `pattern_recognition.py`.
4. **Phase 4**: §3.2 (De-conflicting) → extend `synthesis/engine.py` priority hierarchy.
5. **Phase 5**: §4 (Predictive/Synastry already built; add applying/separating + solar return JSOP fallback).
6. **Phase 6**: §5.1–5.3 (RAG + Guardrails) → requires LLM provider config; implement keyword-composed fallback first.

---

## Open Questions
- LLM provider selection (OpenAI, Anthropic, local GGUF via llama.cpp).
- Triplicity/Term/Face lookup tables — classical sources needed for all 12 signs.
- Combustion orb (±15° or ±8.5° traditional?); Cazimi absolute orb (±17′ or ±1°?).
- Sidereal Ayanamsha default value for Southeast Asian user base (Lahiri recommended).
