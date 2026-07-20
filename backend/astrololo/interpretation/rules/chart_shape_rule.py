"""Chart Shape / Overview synthesis (Step 1).

Combines element balance, quality balance and hemisphere distribution into a
single 'chart shape' reading — the structural overview a pro astrologer opens
with, which the generic auto-reports of competitor sites never synthesize.
"""
from typing import Optional, List
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.models.chart import ChartData

_ELEM_VI = {"fire":"Lửa","earth":"Đất","air":"Khí","water":"Nước"}
_QUAL_VI = {"cardinal":"Thống Lĩnh","fixed":"Cố Định","mutable":"Linh Hoạt"}


class ChartShapeRule(InterpretationRule):
    """Element + quality + hemisphere synthesis → chart shape overview."""

    def __init__(self):
        super().__init__(priority=3)

    def matches(self, chart: ChartData) -> bool:
        return bool(chart.planets) and (chart.element_distribution is not None)

    def _hemispheres(self, chart):
        east = west = north = south = 0
        for b in chart.planets:
            if b.body_type != "planet":
                continue
            h = b.house
            if h in (1, 2, 3, 4, 5, 6):
                east += 1
            else:
                west += 1
            if h in (10, 11, 12, 1, 2, 3):
                north += 1
            else:
                south += 1
        return east, west, north, south

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[List[RuleResult]]:
        ed = chart.element_distribution
        qd = chart.quality_distribution
        east, west, north, south = self._hemispheres(chart)
        total = max(east + west, 1)

        emap = {"fire": ed.fire, "earth": ed.earth, "air": ed.air, "water": ed.water}
        dom_elem = max(emap, key=emap.get)
        qmap = {"cardinal": qd.cardinal, "fixed": qd.fixed, "mutable": qd.mutable}
        dom_qual = max(qmap, key=qmap.get)

        # chart shape name
        if east >= total * 0.7:
            shape = ("Tập trung bán cầu Đông (hướng ngoại, chủ động)", "Eastern-hemisphere concentrated (outward, proactive)")
        elif west >= total * 0.7:
            shape = ("Tập trung bán cầu Tây (hướng nội, tiếp nhận)", "Western-hemisphere concentrated (inner, receptive)")
        elif north >= total * 0.7:
            shape = ("Tập trung bán cầu Bắc (công khai, xã hội)", "Northern concentrated (public, social)")
        elif south >= total * 0.7:
            shape = ("Tập trung bán cầu Nam (riêng tư, nội tâm)", "Southern concentrated (private, inner)")
        else:
            shape = ("Cân bằng giữa các bán cầu", "Balanced across hemispheres")

        if lang == "vi":
            title = "Hình Thái Bản Đồ (Chart Shape & Balance)"
            text = (f"Bản đồ của bạn nghiêng về nguyên tố {_ELEM_VI[dom_elem]} "
                    f"({emap[dom_elem]}/{total} hành tinh) và nhóm {_QUAL_VI[dom_qual]} "
                    f"({qmap[dom_qual]}/{total}). ")
            text += (f"Về bán cầu: {shape[0]}. "
                     f"Đông {east}/Tây {west}, Bắc {north}/Nam {south}. ")
            text += ("Cấu trúc này cho thấy bạn vận hành thế nào: "
                     f"năng lượng {_ELEM_VI[dom_elem]} quyết định phong cách tiếp cận, "
                     f"nhóm {_QUAL_VI[dom_qual]} quyết định cách bạn duy trì hay khởi động, "
                     f"và sự phân bổ bán cầu cho thấy bạn hướng năng lượng ra ngoài hay giữ bên trong. "
                     "Đây là 'khung xương' mà mọi luận giải phía sau dựa vào.")
            ev = [f"Nguyên tố trội: {_ELEM_VI[dom_elem]} {emap[dom_elem]}/{total}",
                  f"Tính chất: {_QUAL_VI[dom_qual]} {qmap[dom_qual]}/{total}",
                  f"Đông {east}/Tây {west} · Bắc {north}/Nam {south}"]
        else:
            title = "Chart Shape & Balance"
            text = (f"Your chart leans toward the {dom_elem} element ({emap[dom_elem]}/{total}) "
                    f"and the {dom_qual} quality ({qmap[dom_qual]}/{total}). ")
            text += (f"Hemispheres: {shape[1]}. "
                     f"East {east}/West {west}, North {north}/South {south}. ")
            text += ("This structure shows how you operate: the dominant element sets your approach style, "
                     "the quality sets how you initiate or sustain, and the hemisphere split shows whether "
                     "you direct energy outward or inward. This is the skeleton every later reading builds on.")
            ev = [f"Dominant element: {dom_elem} {emap[dom_elem]}/{total}",
                  f"Quality: {dom_qual} {qmap[dom_qual]}/{total}",
                  f"E {east}/W {west} · N {north}/S {south}"]

        return [RuleResult(
            title_vi=title if lang == "vi" else "",
            title_en=title if lang == "en" else "",
            text_vi=text if lang == "vi" else "",
            text_en=text if lang == "en" else "",
            score=7.0,
            priority=self.priority,
            category="chart_shape",
            tags=["chart_shape", dom_elem, dom_qual],
            evidence=ev,
            metadata={"dominant_element": dom_elem, "dominant_quality": dom_qual,
                      "east": east, "west": west, "north": north, "south": south},
        )]


RuleRegistry.register(ChartShapeRule())
