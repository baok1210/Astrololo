"""Functional keyword composer — shared by synthesis rules.

Turns a (planet, house) pair into a fluent Vietnamese/English phrase by combining
the planet's FUNCTION with the house's DOMAIN. This is the "smart dictionary"
layer the user asked for: e.g. Saturn in house 7 -> "giới hạn / khó khăn trong
quan hệ" rather than two disconnected facts.

Normalization: VI and EN fully separate; no labels; same structure across inputs.
"""
from typing import Dict

# Short FUNCTION phrase per planet (the "what it does" word).
PLANET_FUNC_VI: Dict[str, str] = {
    "sun": "thể hiện bản thân, ý chí", "moon": "cảm xúc, thói quen",
    "mercury": "giao tiếp, tư duy", "venus": "yêu thương, hưởng thụ",
    "mars": "hành động, xung động", "jupiter": "mở rộng, tin tưởng",
    "saturn": "giới hạn, kỷ luật, khó khăn", "uranus": "đột phá, đổi mới, khác biệt",
    "neptune": "mơ mộng, hòa tan, mơ hồ", "pluto": "đối mặt bản chất sâu, biến đổi",
    "chiron": "chữa lành vết thương", "ceres": "nuôi dưỡng, gắn kết",
    "pallas": "chiến lược, trí tuệ", "juno": "cam kết, trung thành",
    "vesta": "tập trung, tận tâm", "lilith": "nổi loạn, bản năng bị kìm nén",
    "north_node": "hướng phát triển", "south_node": "quá khứ, thói quen cũ",
}
PLANET_FUNC_EN: Dict[str, str] = {
    "sun": "self-expression, will", "moon": "emotion, habit",
    "mercury": "communication, thought", "venus": "love, pleasure",
    "mars": "action, impulse", "jupiter": "expansion, belief",
    "saturn": "limit, discipline, difficulty", "uranus": "breakthrough, change, difference",
    "neptune": "dream, dissolve, vagueness", "pluto": "confront deep core, transformation",
    "chiron": "heal the wound", "ceres": "nurture, attachment",
    "pallas": "strategy, intellect", "juno": "commitment, loyalty",
    "vesta": "focus, devotion", "lilith": "rebellion, repressed instinct",
    "north_node": "direction of growth", "south_node": "past, old habit",
}


def compose_phrase(planet: str, house: int, lang: str) -> str:
    """Return '<planet> (<function>) in house <n> (<domain>) -> <blend>'."""
    func = (PLANET_FUNC_VI if lang == "vi" else PLANET_FUNC_EN).get(planet, "")
    if lang == "vi":
        return f"{func} (qua nhà {house})"
    return f"{func} (through house {house})"
