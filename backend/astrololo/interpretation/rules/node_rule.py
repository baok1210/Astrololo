"""North/South Node axis — karmic lessons & developmental direction (Step 5).

Fills the gap: Astrololo had node data but no dedicated reading linking the
North Node (where you're growing toward) with the South Node (karmic past).
"""
from typing import Optional, List
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.interpretation.template_loader import get_planet_in_sign
from astrololo.core.constants import SIGNS
from astrololo.models.chart import ChartData

_SIGN_VI = {
    "aries":"Bạch Dương","taurus":"Kim Ngưu","gemini":"Song Tử","cancer":"Cự Giải","leo":"Sư Tử","virgo":"Xử Nữ",
    "libra":"Thiên Bình","scorpio":"Bọ Cạp","sagittarius":"Nhân Mã","capricorn":"Ma Kết","aquarius":"Bảo Bình","pisces":"Song Ngư",
}
_SIGN_EN = {
    "aries":"Aries","taurus":"Taurus","gemini":"Gemini","cancer":"Cancer","leo":"Leo","virgo":"Virgo",
    "libra":"Libra","scorpio":"Scorpio","sagittarius":"Sagittarius","capricorn":"Capricorn","aquarius":"Aquarius","pisces":"Pisces",
}


class NodeAxisRule(InterpretationRule):
    """North Node (growth direction) + South Node (karmic past) synthesis."""

    def __init__(self):
        super().__init__(priority=9)

    def matches(self, chart: ChartData) -> bool:
        return any(b.name in ("north_node", "south_node") for b in chart.planets)

    def _body(self, chart, name):
        return next((b for b in chart.planets if b.name == name), None)

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[List[RuleResult]]:
        nn = self._body(chart, "north_node")
        sn = self._body(chart, "south_node")
        if not nn or not sn:
            return None

        nn_sign = SIGNS[nn.sign].name_en.lower()
        sn_sign = SIGNS[sn.sign].name_en.lower()
        nn_vi = _SIGN_VI.get(nn.sign, nn_sign)
        sn_vi = _SIGN_VI.get(sn.sign, sn_sign)

        nn_entry = get_planet_in_sign("north_node", nn_sign, lang) or {}
        sn_entry = get_planet_in_sign("south_node", sn_sign, lang) or {}
        nn_text = nn_entry.get("detailed", "") or nn_entry.get("short", "")
        sn_text = sn_entry.get("detailed", "") or sn_entry.get("short", "")

        if lang == "vi":
            title = f"Trục La Hầu – Kế Hầu: {nn_vi} – {sn_vi}"
            intro = (f"La Hầu (North Node) tại {nn_vi} chỉ hướng phát triển bạn cần hướng tới trong đời này — "
                     f"đây là vùng năng lượng còn mới mẻ, đòi hỏi nỗ lực ý thức. "
                     f"Ngược lại, Kế Hầu (South Node) tại {sn_vi} là nơi bạn đã thuần thục từ quá khứ "
                     f"(nghiệp quả cũ), dễ sa vào thói quen nhưng ít mang lại sự tăng trưởng.")
            closing = (f"Nhiệm vụ của bạn là dịch chuyển dần từ {sn_vi} (an toàn nhưng tù túng) "
                       f"sang {nn_vi} (thử thách nhưng là nơi tiềm năng bung nở).")
        else:
            title = f"Node Axis: {_SIGN_EN.get(nn.sign, nn_sign)} – {_SIGN_EN.get(sn.sign, sn_sign)}"
            intro = (f"The North Node in {nn_vi} points to the growth direction you must consciously develop this lifetime. "
                     f"The South Node in {sn_vi} is your karmic comfort zone — familiar, easy, but where growth stalls.")
            closing = (f"Your task is to gradually shift from {sn_vi} (safe but stagnant) toward {nn_vi} (challenging but where potential blooms).")

        text = f"{intro}\n\n"
        if nn_text:
            text += (f"**La Hầu {nn_vi}:** {nn_text}\n\n" if lang == "vi" else f"**North Node {nn_vi}:** {nn_text}\n\n")
        if sn_text:
            text += (f"**Kế Hầu {sn_vi}:** {sn_text}\n\n" if lang == "vi" else f"**South Node {sn_vi}:** {sn_text}\n\n")
        text += closing

        ev = [f"La Hầu: {nn_vi}", f"Kế Hầu: {sn_vi}",
              f"Nhà La Hầu: {nn.house}" if lang == "vi" else f"North Node House: {nn.house}"]

        return [RuleResult(
            title_vi=title if lang == "vi" else "",
            title_en=title if lang == "en" else "",
            text_vi=text if lang == "vi" else "",
            text_en=text if lang == "en" else "",
            score=6.0,
            priority=self.priority,
            category="node_axis",
            tags=["node", nn_sign, sn_sign],
            evidence=ev,
            metadata={"north_node_sign": nn.sign, "south_node_sign": sn.sign,
                      "north_node_house": nn.house, "south_node_house": sn.house},
        )]


RuleRegistry.register(NodeAxisRule())
