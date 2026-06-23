from typing import Optional
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.models.chart import ChartData
from astrololo.interpretation.template_loader import get_quality_text
from astrololo.core.constants import PLANETS, SIGNS

_QUALITY_LABEL_VI = {"cardinal": "Thống Lĩnh", "fixed": "Cố Định", "mutable": "Linh Hoạt"}
_QUALITY_LABEL_EN = {"cardinal": "Cardinal", "fixed": "Fixed", "mutable": "Mutable"}

_QUALITY_SIGNS_VI = {
    "cardinal": "Bạch Dương, Cự Giải, Thiên Bình, Ma Kết",
    "fixed": "Kim Ngưu, Sư Tử, Bọ Cạp, Bảo Bình",
    "mutable": "Song Tử, Xử Nữ, Nhân Mã, Song Ngư",
}


class QualityRule(InterpretationRule):
    """Interpret quality distribution (cardinal/fixed/mutable) using YAML templates."""

    def __init__(self):
        super().__init__(priority=22)

    def matches(self, chart: ChartData) -> bool:
        return chart.quality_distribution is not None

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[RuleResult]:
        qd = chart.quality_distribution
        if not qd:
            return None

        total = qd.cardinal + qd.fixed + qd.mutable
        if total == 0:
            return None

        qty_map = {"cardinal": qd.cardinal, "fixed": qd.fixed, "mutable": qd.mutable}
        dominant = max(qty_map, key=qty_map.get)
        deficient = min(qty_map, key=qty_map.get)

        labels = _QUALITY_LABEL_VI if lang == "vi" else _QUALITY_LABEL_EN
        signs_str = _QUALITY_SIGNS_VI if lang == "vi" else _QUALITY_SIGNS_VI

        # Group planets by quality
        quality_planets: dict[str, list] = {"cardinal": [], "fixed": [], "mutable": []}
        for p in chart.planets:
            if p.body_type != "planet":
                continue
            s = SIGNS.get(p.sign)
            qual = s.quality if s else ""
            quality_planets.setdefault(qual, []).append(p)

        # Build lines
        lines = []
        for qual in ("cardinal", "fixed", "mutable"):
            count = round(qty_map[qual], 1)
            planets_list = quality_planets.get(qual, [])
            names = []
            for pp in planets_list:
                pl = PLANETS.get(pp.name)
                n = pl.name_vi if pl and lang == "vi" else pl.name_en if pl else pp.name
                names.append(n)
            names_str = ", ".join(names) if names else "(không có)" if lang == "vi" else "(none)"
            if lang == "vi":
                lines.append(f"• {labels[qual]}: {count} — {signs_str[qual]}")
                if names_str:
                    lines.append(f"  Hành tinh: {names_str}")
            else:
                lines.append(f"• {labels[qual]}: {count}")
                if names_str and "(none)" not in names_str:
                    lines.append(f"  Planets: {names_str}")

        # Template text
        dom_text = get_quality_text(f"dominant_{dominant}", lang) or ""
        def_text = get_quality_text(f"deficient_{deficient}", lang) or ""

        combined = "\n".join(lines)
        if dom_text:
            combined += f"\n\n{dom_text}"
        if def_text:
            combined += f"\n\n{def_text}"

        return RuleResult(
            title_vi="Phân Bố Năng Lượng Hoàng Đạo" if lang == "vi" else "",
            title_en="Zodiacal Energy Distribution" if lang == "en" else "",
            text_vi=combined if lang == "vi" else "",
            text_en=combined if lang == "en" else "",
            score=int(qty_map[dominant] * 3),
            priority=self.priority,
            category="quality",
            tags=[dominant, deficient],
            metadata={
                "distribution": qty_map,
                "dominant": dominant,
                "deficient": deficient,
            },
        )


RuleRegistry.register(QualityRule())
