"""Life-area scoring (0-100) for the full natal report (tra-cuu-ban-do-sao-1).

Each life area aggregates the planets placed in its associated houses plus
the aspects those planets make, producing a 0-100 score and a VI/EN prose
summary. Mirrors the MystechX "14 khía cạnh" structure (B6-B19).
"""
from typing import Dict, Any, List, Optional
from astrololo.models.chart import ChartData
from astrololo.interpretation.scoring import body_weight

# life-area key -> (houses, seed planets, VI label, EN label)
_AREAS: Dict[str, Dict[str, Any]] = {
    "career":      {"houses": [10], "seed": ["sun", "saturn", "uranus"], "vi": "Công danh, sự nghiệp", "en": "Career"},
    "self":        {"houses": [1], "seed": ["sun", "ascendant"], "vi": "Bản thân", "en": "Self"},
    "love":        {"houses": [5], "seed": ["venus", "mars"], "vi": "Tình yêu", "en": "Love"},
    "finance":     {"houses": [2], "seed": ["venus", "jupiter"], "vi": "Tài chính cá nhân", "en": "Personal Finance"},
    "transformation": {"houses": [8], "seed": ["pluto"], "vi": "Chuyển hóa bản thân", "en": "Transformation"},
    "social":      {"houses": [11], "seed": ["uranus"], "vi": "Mối quan hệ xã hội", "en": "Social Relations"},
    "family":      {"houses": [4], "seed": ["moon"], "vi": "Gia đình", "en": "Family"},
    "children":    {"houses": [5], "seed": [], "vi": "Con cái", "en": "Children"},
    "health":      {"houses": [6], "seed": ["mars"], "vi": "Sức khỏe", "en": "Health"},
    "learning":    {"houses": [9], "seed": ["mercury"], "vi": "Học tập, phát triển", "en": "Learning"},
    "communication": {"houses": [3], "seed": ["mercury"], "vi": "Giao tiếp", "en": "Communication"},
    "marriage":    {"houses": [7], "seed": ["venus"], "vi": "Hôn nhân", "en": "Marriage"},
    "subconscious": {"houses": [12], "seed": ["neptune"], "vi": "Tiềm thức, nội tâm", "en": "Subconscious"},
    "travel":      {"houses": [9], "seed": [], "vi": "Di chuyển", "en": "Travel"},
}


def _planet_score_in_house(planet, house: int) -> float:
    if planet.house != house:
        return 0.0
    from astrololo.core.constants import get_dignity_score
    dign = get_dignity_score(planet.name, planet.sign)
    bw = body_weight(planet.name)
    return (5.0 + max(0.0, dign) * 2.0) * bw


def _aspect_contrib(chart: ChartData, names: set) -> tuple:
    """Return (harmonious_pts, challenging_pts) for aspects involving `names`."""
    harm = chall = 0.0
    for a in chart.aspects:
        if a.planet1 in names or a.planet2 in names:
            if getattr(a, "nature", "neutral") == "harmonious":
                harm += 3.0 * body_weight(a.planet1) * 0.5 + 3.0 * body_weight(a.planet2) * 0.5
            elif getattr(a, "nature", "neutral") == "challenging":
                chall += 3.0 * body_weight(a.planet1) * 0.5 + 3.0 * body_weight(a.planet2) * 0.5
    return harm, chall


def calculate_life_areas(chart: ChartData) -> List[Dict[str, Any]]:
    """Compute 14 life-area scores (0-100) from a natal chart."""
    results: List[Dict[str, Any]] = []
    for key, cfg in _AREAS.items():
        houses = cfg["houses"]
        # planets actually in the area's houses
        in_area = [p for p in chart.planets if p.house in houses]
        names = {p.name for p in in_area} | set(cfg["seed"])
        # base from house placement
        base = sum(_planet_score_in_house(p, h) for p in chart.planets for h in houses)
        # aspect contributions
        harm, chall = _aspect_contrib(chart, names)
        raw = 50.0 + base + harm - chall
        score = max(0, min(100, int(round(raw))))
        label = ("Tốt" if score >= 70 else "Khá" if score >= 50 else "Trung bình" if score >= 30 else "Cần chú ý")
        label_en = ("Good" if score >= 70 else "Fair" if score >= 50 else "Average" if score >= 30 else "Needs attention")
        results.append({
            "key": key,
            "title_vi": cfg["vi"],
            "title_en": cfg["en"],
            "score": score,
            "label_vi": label,
            "label_en": label_en,
            "planets_in_area": [p.name for p in in_area],
        })
    return results
