"""MC–IC axis synthesis — career/vocation vs roots/family foundation (Step 5).

Links the Midheaven (public status, vocation) with the Imum Coeli (home,
family roots, private foundation) into one reading, since they sit on the
same structural axis (IC = MC + 180°).
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


class McIcAxisRule(InterpretationRule):
    """Midheaven (MC) and Imum Coeli (IC) as one vocational-rooted axis."""

    def __init__(self):
        super().__init__(priority=10)

    def matches(self, chart: ChartData) -> bool:
        return chart.mc_sign is not None

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[List[RuleResult]]:
        if chart.mc_sign is None:
            return None
        mc_name = chart.mc_sign  # e.g. "virgo"
        mc_idx = list(SIGNS.keys()).index(mc_name) if mc_name in SIGNS else None
        if mc_idx is None:
            return None
        mc_sign = mc_name
        ic_sign_idx = (mc_idx + 6) % 12
        ic_sign = list(SIGNS.keys())[ic_sign_idx]

        mc_vi = _SIGN_VI.get(mc_name, mc_sign)
        ic_vi = _SIGN_VI.get(ic_sign, ic_sign)

        from astrololo.interpretation.template_loader import _load_yaml
        mc_tpl = _load_yaml(lang, "mc") or {}
        mc_text = mc_tpl.get(mc_sign, "") if isinstance(mc_tpl, dict) else ""

        if lang == "vi":
            title = f"Trục MC – IC: Sự Nghiệp ({mc_vi}) & Cội Nguồn ({ic_vi})"
            intro = (f"Thiên đỉnh (MC) tại {mc_vi} là mặt bạn trình diện với xã hội — con đường sự nghiệp, "
                     f"vị thế và những gì bạn muốn đạt được ở đời. Đối diện qua tâm bản đồ, "
                     f"Thiên đế (IC) tại {ic_vi} là nền tảng riêng tư: gia đình, nguồn cội và cảm giác an toàn sâu thẳm.")
            link = (f"Sự nghiệp {mc_vi} của bạn vững nhất khi được nuôi dưỡng bởi nền tảng {ic_vi} — "
                    f"thành công bên ngoài chỉ bền nếu căn nhà bên trong (IC) được chăm sóc.")
        else:
            title = f"MC–IC Axis: Career ({mc_vi}) & Roots ({ic_vi})"
            intro = (f"The Midheaven (MC) in {mc_vi} is the face you show society — vocation, status, life goals. "
                     f"Opposite through the chart's heart, the Imum Coeli (IC) in {ic_vi} is the private foundation: "
                     f"family, origins, deep security.")
            link = (f"Your {mc_vi} career is strongest when fed by the {ic_vi} foundation — outer success lasts only "
                    f"if the inner home (IC) is tended.")

        text = f"{intro}\n\n"
        if mc_text:
            text += (f"**MC {mc_vi}:** {mc_text}\n\n" if lang == "vi" else f"**MC {mc_vi}:** {mc_text}\n\n")
        text += link

        ev = [f"MC: {mc_vi}", f"IC: {ic_vi}"]

        return [RuleResult(
            title_vi=title if lang == "vi" else "",
            title_en=title if lang == "en" else "",
            text_vi=text if lang == "vi" else "",
            text_en=text if lang == "en" else "",
            score=6.0,
            priority=self.priority,
            category="mc_ic_axis",
            tags=["mc", "ic", mc_sign, ic_sign],
            evidence=ev,
            metadata={"mc_sign": mc_name, "ic_sign": ic_sign},
        )]


RuleRegistry.register(McIcAxisRule())
