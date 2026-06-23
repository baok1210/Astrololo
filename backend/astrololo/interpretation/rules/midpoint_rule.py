"""MidpointRule — lists key midpoints in the chart with sign/position."""
from typing import Optional, List
from astrololo.models.chart import ChartData
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult


_KEY_MIDPOINTS = {
    ("sun", "moon"): "Sun/Moon",
    ("ascendant", "mc"): "ASC/MC",
    ("sun", "ascendant"): "Sun/ASC",
    ("moon", "ascendant"): "Moon/ASC",
    ("sun", "mc"): "Sun/MC",
    ("moon", "mc"): "Moon/MC",
    ("venus", "mars"): "Venus/Mars",
    ("sun", "saturn"): "Sun/Saturn",
    ("moon", "saturn"): "Moon/Saturn",
}


class MidpointRule(InterpretationRule):
    priority = 12

    def __init__(self):
        super().__init__(priority=12)

    def matches(self, chart: ChartData) -> bool:
        return len(chart.midpoints) > 0

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[RuleResult | List[RuleResult]]:
        if not chart.midpoints:
            return None

        items = []
        seen = set()
        for mp in chart.midpoints:
            k1 = (mp.body1, mp.body2)
            k2 = (mp.body2, mp.body1)
            label = _KEY_MIDPOINTS.get(k1) or _KEY_MIDPOINTS.get(k2)
            if label and label not in seen:
                seen.add(label)
                label_vi = label  # keep EN label for now
                items.append(
                    RuleResult(
                        title_vi=f"Trung Điểm {label_vi}",
                        title_en=f"Midpoint {label}",
                        text_vi=f"{mp.body1}/{mp.body2} tại {mp.position_in_sign:.2f}° {mp.sign_vi}",
                        text_en=f"{mp.body1}/{mp.body2} at {mp.position_in_sign:.2f}° {mp.sign}",
                        score=50,
                        priority=12,
                        category="midpoints",
                        tags=["midpoint", label],
                        metadata={"body1": mp.body1, "body2": mp.body2,
                                  "midpoint": mp.midpoint, "sign": mp.sign,
                                  "position_in_sign": mp.position_in_sign},
                    )
                )
        return items if items else None
