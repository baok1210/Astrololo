"""Encyclopedia rule: emit a foundational astrology-knowledge section.

Pulls from templates/{lang}/encyclopedia.yaml (user-supplied reference
content, 2026-07-14). Always matches (non-chart-specific), low
priority so it appears last in the synthesis output.
"""
from typing import Optional

from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.models.chart import ChartData
from astrololo.interpretation.template_loader import _load_yaml


class EncyclopediaRule(InterpretationRule):
    """Emit the encyclopedia / reference section."""

    def __init__(self):
        super().__init__(priority=30)

    def matches(self, chart: ChartData) -> bool:
        return True

    def _fmt(self, data: dict, lang: str) -> str:
        if not data:
            return ""
        lines: list = []
        # chart types
        ct = data.get("chart_types")
        if ct:
            lines.append(f"### {ct.get('title','')}")
            for k in ("natal", "synastry", "composite", "progressed", "solar_return", "lunar_return", "transit"):
                item = (ct.get(k) or {})
                if item.get("name") and item.get("text"):
                    lines.append(f"- **{item['name']}**: {item['text']}")
        # structure
        st = data.get("structure")
        if st:
            lines.append(f"\n### {st.get('title','')}")
            if st.get("intro"):
                lines.append(st["intro"])
            for e in (st.get("elements") or []):
                lines.append(f"- {e}")
        # houses
        hs = data.get("houses")
        if hs:
            lines.append(f"\n### {hs.get('title','')}")
            if hs.get("intro"):
                lines.append(hs["intro"])
            for k, v in (hs.get("items") or {}).items():
                lines.append(f"- {v}")
        # hemispheres
        hm = data.get("hemispheres")
        if hm:
            lines.append(f"\n### {hm.get('title','')}")
            if hm.get("intro"):
                lines.append(hm["intro"])
            for e in (hm.get("upper_lower") or []):
                lines.append(f"- {e}")
            for e in (hm.get("left_right") or []):
                lines.append(f"- {e}")
        # planets
        pl = data.get("planets")
        if pl:
            lines.append(f"\n### {pl.get('title','')}")
            for k, v in (pl.get("items") or {}).items():
                lines.append(f"- **{k.capitalize()}**: {v}")
            deg = pl.get("degree")
            if deg:
                lines.append(f"\n**{deg.get('title','')}**: {deg.get('text','')}")
        # elements & qualities
        eq = data.get("elements_qualities")
        if eq:
            lines.append(f"\n### {eq.get('title','')}")
            if eq.get("intro"):
                lines.append(eq["intro"])
            if eq.get("elements"):
                lines.append(f"- {eq['elements']}")
            if eq.get("qualities"):
                lines.append(f"- {eq['qualities']}")
            if eq.get("example"):
                lines.append(f"- {eq['example']}")
        # aspects
        ap = data.get("aspects")
        if ap:
            lines.append(f"\n### {ap.get('title','')}")
            if ap.get("intro"):
                lines.append(ap["intro"])
            for k in ("good", "challenging", "conjunction", "square", "opposition", "trine_sextile"):
                if ap.get(k):
                    lines.append(f"- {ap[k]}")
        return "\n".join(lines).strip()

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[RuleResult]:
        data = _load_yaml(lang, "encyclopedia.yaml")
        text = self._fmt(data, lang)
        if not text:
            return None
        title_vi = "Bách Khoa Chiêm Tinh" if lang == "vi" else ""
        title_en = "Astrology Encyclopedia" if lang == "en" else ""
        return RuleResult(
            title_vi=title_vi,
            title_en=title_en,
            text_vi=text if lang == "vi" else "",
            text_en=text if lang == "en" else "",
            score=5.0,
            priority=self.priority,
            category="encyclopedia",
            tags=["encyclopedia"],
            metadata={},
        )


RuleRegistry.register(EncyclopediaRule())
