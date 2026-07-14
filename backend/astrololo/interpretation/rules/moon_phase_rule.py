from typing import Optional
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.models.chart import ChartData
from astrololo.interpretation.template_loader import _load_yaml


_MOON_PHASE_FALLBACK = {
    "vi": {
        "New Moon": "Trăng Non: Bạn sinh ra trong kỳ Trăng Non — mang năng lượng của sự khởi đầu và tiềm năng thuần khiết. Đây là thời điểm của những dự án mới và sự khám phá bản thân.",
        "Waxing Crescent": "Trăng Lưỡi Liềm: Bạn sinh ra trong giai đoạn Trăng khuyết đầu tháng — thời điểm của hy vọng và dự định. Bạn có niềm tin vào tương lai và khả năng biến ước mơ thành hiện thực.",
        "First Quarter": "Trăng Bán Nguyệt: Bạn sinh ra vào kỳ Trăng Bán Nguyệt đầu tháng — thời điểm của hành động và quyết định. Bạn có tinh thần chiến đấu, sẵn sàng đối mặt với thử thách.",
        "Waxing Gibbous": "Trăng Khuyết Đầu: Bạn sinh ra khi Trăng đang dần tròn — thời điểm của sự hoàn thiện và điều chỉnh. Bạn có khả năng phân tích và tinh chỉnh mọi thứ.",
        "Full Moon": "Trăng Tròn: Bạn sinh ra vào kỳ Trăng Tròn — thời điểm của sự trọn vẹn và cao trào. Bạn mang năng lượng mạnh mẽ của sự đối cực, cuộc sống xoay quanh các mối quan hệ và cân bằng.",
        "Waning Gibbous": "Trăng Khuyết Cuối: Bạn sinh ra khi Trăng bắt đầu khuyết — thời điểm của sự chia sẻ và truyền đạt. Bạn có khả năng truyền cảm hứng cho người khác.",
        "Last Quarter": "Trăng Bán Nguyệt Cuối: Bạn sinh ra vào kỳ Trăng Bán Nguyệt cuối tháng — thời điểm của sự buông bỏ và chuyển hóa. Bạn có khả năng kết thúc mọi việc một cách gọn gàng.",
        "Waning Crescent": "Trăng Lưỡi Liềm Cuối: Bạn sinh ra vào giai đoạn cuối chu kỳ Trăng — thời điểm của sự nghỉ ngơi và tái tạo. Bạn có trực giác tâm linh sâu sắc.",
    },
    "en": {
        "New Moon": "New Moon: Born during the New Moon — carrying pure initiating energy and tremendous potential. This is a time of new beginnings and self-discovery.",
        "Waxing Crescent": "Waxing Crescent: Born during the Crescent Moon — a time of hope and intention. You have faith in the future and ability to turn dreams into reality.",
        "First Quarter": "First Quarter: Born during the First Quarter Moon — a time of action and decision. You have a fighting spirit and readiness to face challenges.",
        "Waxing Gibbous": "Waxing Gibbous: Born during the Gibbous Moon — a time of refinement and adjustment. You have the ability to analyze, perfect, and improve.",
        "Full Moon": "Full Moon: Born during the Full Moon — a time of culmination and peak awareness. You carry powerful energy of opposites; your life revolves around relationships and balance.",
        "Waning Gibbous": "Waning Gibbous: Born during the Disseminating Moon — a time of sharing and teaching. You have the ability to inspire and teach others.",
        "Last Quarter": "Last Quarter: Born during the Last Quarter Moon — a time of release and transformation. You have the ability to end things cleanly and reorient.",
        "Waning Crescent": "Waning Crescent: Born in the final lunar phase — a time of rest and regeneration. You have deep spiritual intuition and connection to the unconscious.",
    }
}


class MoonPhaseRule(InterpretationRule):
    def __init__(self):
        super().__init__(priority=8)

    def matches(self, chart: ChartData) -> bool:
        return bool(chart.moon_phase) and chart.moon_phase != "Unknown"

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[RuleResult]:
        phase = chart.moon_phase
        if not phase or phase == "Unknown":
            return None

        data = _load_yaml(lang, "moon_phase.yaml")
        text = data.get(phase, "") if data else ""
        if not text:
            text = _MOON_PHASE_FALLBACK.get(lang, {}).get(phase, "")

        if lang == "vi":
            title = f"Tuần Trăng: {phase}"
        else:
            title = f"Moon Phase: {phase}"

        return RuleResult(
            title_vi=title if lang == "vi" else "",
            title_en=title if lang == "en" else "",
            text_vi=text if lang == "vi" else "",
            text_en=text if lang == "en" else "",
            score=8.0,
            priority=self.priority,
            category="synthesis",
            planet="moon",
            tags=["moon_phase", phase.lower().replace(" ", "_")],
            metadata={"moon_phase": phase},
        )


RuleRegistry.register(MoonPhaseRule())