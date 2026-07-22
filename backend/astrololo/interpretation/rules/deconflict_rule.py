"""De-conflicting engine: layering, override, suppression.

Spec 010 §4.
Does NOT mutate chart state; exposes strategies via RuleResult.metadata
so downstream rules can consult them.
"""
from typing import Optional, List, Dict, Any
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.models.chart import ChartData
from astrololo.core.constants import PLANETS


_SUPPRESSION_DIGNITY = -8
_SUPPRESSION_HOUSES = {3, 6, 9, 12}


class DeconflictRule(InterpretationRule):
    """Detects inner/outer contradictions and produces layered summaries."""

    def __init__(self):
        super().__init__(priority=6)

    def matches(self, chart: ChartData) -> bool:
        return len([p for p in chart.planets if p.body_type == "planet"]) >= 3

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[List[RuleResult]]:
        sun = next((p for p in chart.planets if p.body_type == "planet" and p.name == "sun"), None)
        moon = next((p for p in chart.planets if p.body_type == "planet" and p.name == "moon"), None)
        asc = next((p for p in chart.planets if p.body_type == "planet" and p.name == "ascendant"), None)
        if not sun or not moon:
            return None

        dominant_map = getattr(chart, "dominant_scores", {}) or {}

        strategies: List[str] = []
        layers: List[Dict[str, Any]] = []

        # Sun–Moon tension
        sun_sign_info = PLANETS.get(sun.sign)
        moon_sign_info = PLANETS.get(moon.sign)
        sun_elem = getattr(sun_sign_info, "element", "")
        moon_elem = getattr(moon_sign_info, "element", "")
        if sun_elem == "fire" and moon_elem == "water":
            note_vi = "Lớp ngoài mặt: bạn thể hiện lên như người mạnh mẽ, quyết đoán (Mặt Trời lửa). Lớp trong: cảm xúc lại cần sự êm dịu, an toàn (Mặt Trăng nước). Hai lớp này đan xen, không phải mâu thuẫn tuyệt đối."
            note_en = "Outer layer: you appear strong and decisive (Sun fire). Inner layer: emotions need softness and security (Moon water). intertwined, not absolute conflict."
            strategies.append("sun_moon_element_tension")
            layers.append({"type": "sun_moon", "data": {"sun": sun.sign, "moon": moon.sign, "note": note_vi if lang == "vi" else note_en}})

        # Asc-Sun contrast: if asc is opposite sun sign by element/quality
        if asc:
            asc_sign_info = PLANETS.get(asc.sign)
            asc_elem = getattr(asc_sign_info, "element", "")
            asc_qual = getattr(asc_sign_info, "quality", "")
            sun_qual = getattr(sun_sign_info, "quality", "")
            sun_sun_name = PLANETS.get("sun")
            sun_elem = getattr(sun_sign_info, "element", "")
            # e.g., asc mutable air vs sun cardinal fire
            if asc_qual == "mutable" and sun_qual == "cardinal":
                note_vi = "Mặt ngoài: dễ thích nghi. Mặt trong: cần khởi xướng. Hãy dung hòa bằng linh hoạt có chủ đích."
                note_en = "Outer: adaptive. Inner: initiating. Reconcile via flexible purposefulness."
                strategies.append("asc_sun_quality_contrast")
                layers.append({"type": "asc_sun", "data": {"asc": asc.sign, "sun": sun.sign, "note": note_vi if lang == "vi" else note_en}})

        # Override: when one planet clearly dominates, let it dominate
        if dominant_map:
            top = max(dominant_map, key=dominant_map.get)
            entry = {
                "type": "override",
                "top": top,
                "top_score": dominant_map[top],
                "note_vi": f"{PLANETS[top].name_vi} chi phối; các chiếu khác nên đọc qua lăng kính hành tinh này." if lang == "vi" else f"{top} dominates; other clues read through its lens.",
            }
            if lang != "vi":
                entry["note_en"] = entry.pop("note_vi")
                entry["note"] = entry["note_en"]
            else:
                entry["note"] = entry.pop("note_vi")
            layers.append(entry)

        # Suppression test
        for p in chart.planets:
            if p.body_type != "planet":
                continue
            pl = PLANETS.get(p.name)
            if not pl:
                continue
            score = getattr(chart, "dignity_scores", {}).get(p.name, 0)
            if score <= _SUPPRESSION_DIGNITY and p.house in _SUPPRESSION_HOUSES:
                layers.append({
                    "type": "suppression",
                    "planet": p.name,
                    "house": p.house,
                    "score": score,
                    "note_vi": f"{pl.name_vi} bị kìm nén (điểm bất lợi {score}) — chỉ phát huy khi biết chủ đích, không nên đặt hy vọng lớn." if lang == "vi" else f"{p.name} suppressed (score {score}) — needs deliberate effort.",
                })
                strategies.append("suppression_" + p.name)

        if not layers:
            return None

        vi_lines, en_lines = [], []
        for layer in layers:
            note = layer.get("note") or layer.get("note_vi") or layer.get("note_en") or ""
            if note:
                vi_lines.append(note) if lang == "vi" else en_lines.append(note)

        text_vi = "\n\n".join(vi_lines) if lang == "vi" else "\n\n".join(en_lines)
        if not text_vi and not en_lines:
            text_vi = en_lines = "\n\n".join(str(layer) for layer in layers)

        return [RuleResult(
            title_vi="Giải Quyết Mâu Thuẫn" if lang == "vi" else "",
            title_en="De-conflicting" if lang == "en" else "",
            text_vi=text_vi,
            text_en=text_vi,
            score=0.0,
            priority=self.priority,
            category="deconflict",
            tags=strategies + ["deconflict"],
            evidence=[f"{layer.get('type')}:{layer.get('planet', layer.get('top', ''))}" for layer in layers],
            metadata={
                "strategies": strategies,
                "layers": layers,
            },
        )]


RuleRegistry.register(DeconflictRule())
