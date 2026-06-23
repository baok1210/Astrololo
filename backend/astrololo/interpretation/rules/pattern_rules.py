from typing import Optional, List, Tuple
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.models.chart import ChartData
from astrololo.core.constants import (
    SIGNS,
    ELEMENT_SIGNS,
    QUALITY_SIGNS,
)
from astrololo.interpretation.template_loader import get_pattern


_pattern_titles = {
    "grand_trine": ("Grand Trine", "Grand Trine"),
    "tsquare": ("T-Square", "T-Square"),
    "stellium": ("Stellium", "Stellium"),
    "yod": ("Yod (Ngón Tay Thượng Đế)", "Yod (Finger of God)"),
    "grand_cross": ("Grand Cross", "Grand Cross"),
    "kite": ("Kite (Cánh Diều)", "Kite"),
    "mystic_rectangle": ("Mystic Rectangle", "Mystic Rectangle"),
}

_pattern_scores = {
    "grand_trine": 15,
    "tsquare": 12,
    "stellium": 10,
    "yod": 26,
    "grand_cross": 20,
    "kite": 14,
    "mystic_rectangle": 16,
}


def _detect_grand_trine(
    planets: list, aspects: list
) -> Optional[Tuple[str, str, List[str]]]:
    from itertools import combinations

    for el, signs in ELEMENT_SIGNS.items():
        el_planets = [p for p in planets if p.sign in signs]
        if len(el_planets) < 3:
            continue
        unique_signs = set(p.sign for p in el_planets)
        if len(unique_signs) < 3:
            continue
        for combo in combinations(el_planets, 3):
            if len(set(p.sign for p in combo)) < 3:
                continue
            if all(
                _has_aspect(a.name, b.name, "trine", aspects)
                for a, b in combinations(combo, 2)
            ):
                return ("grand_trine", el, [p.name for p in combo])
    return None


def _has_aspect(planet_a: str, planet_b: str, asp_type: str, aspects: list) -> bool:
    return any(
        (a.planet1 == planet_a and a.planet2 == planet_b and a.aspect_type == asp_type)
        or (
            a.planet1 == planet_b
            and a.planet2 == planet_a
            and a.aspect_type == asp_type
        )
        for a in aspects
    )


def _detect_tsquare(
    planets: list, aspects: list
) -> Optional[Tuple[str, str, List[str]]]:
    for p1 in planets:
        for p2 in planets:
            if p1.name >= p2.name:
                continue
            if not _has_aspect(p1.name, p2.name, "opposition", aspects):
                continue
            for p3 in planets:
                if p3.name in (p1.name, p2.name):
                    continue
                if _has_aspect(p1.name, p3.name, "square", aspects) and _has_aspect(
                    p2.name, p3.name, "square", aspects
                ):
                    quality = SIGNS[p3.sign].quality
                    return ("tsquare", quality, [p1.name, p2.name, p3.name])
    return None


def _detect_stellium(planets: list) -> Optional[Tuple[str, str, List[str]]]:
    from collections import Counter

    sign_counts = Counter(p.sign for p in planets)
    for sign, count in sign_counts.items():
        if count >= 3:
            names = [p.name for p in planets if p.sign == sign]
            return ("stellium", sign, names)
    return None


def _detect_grand_cross(
    planets: list, aspects: list
) -> Optional[Tuple[str, str, List[str]]]:
    for q, signs in QUALITY_SIGNS.items():
        q_planets = [p for p in planets if p.sign in signs]
        if len(q_planets) < 4:
            continue
        for p1 in q_planets:
            for p2 in q_planets:
                if p1.name >= p2.name:
                    continue
                if not _has_aspect(p1.name, p2.name, "opposition", aspects):
                    continue
                for p3 in q_planets:
                    if p3.name in (p1.name, p2.name):
                        continue
                    if not (
                        _has_aspect(p1.name, p3.name, "square", aspects)
                        and _has_aspect(p2.name, p3.name, "square", aspects)
                    ):
                        continue
                    for p4 in q_planets:
                        if p4.name in (p1.name, p2.name, p3.name):
                            continue
                        if (
                            _has_aspect(p3.name, p4.name, "opposition", aspects)
                            and _has_aspect(p1.name, p4.name, "square", aspects)
                            and _has_aspect(p2.name, p4.name, "square", aspects)
                        ):
                            return (
                                "grand_cross",
                                q,
                                [p1.name, p2.name, p3.name, p4.name],
                            )
    return None


def _detect_yod(planets: list, aspects: list) -> Optional[Tuple[str, str, List[str]]]:
    from itertools import combinations

    for p1, p2 in combinations(planets, 2):
        if not _has_aspect(p1.name, p2.name, "quincunx", aspects):
            continue
        for p3 in planets:
            if p3.name in (p1.name, p2.name):
                continue
            if _has_aspect(p1.name, p3.name, "sextile", aspects) and _has_aspect(
                p2.name, p3.name, "sextile", aspects
            ):
                return ("yod", p3.name, [p1.name, p2.name, p3.name])
    return None


def _detect_kite(planets: list, aspects: list) -> Optional[Tuple[str, str, List[str]]]:
    from itertools import combinations

    for el, signs in ELEMENT_SIGNS.items():
        el_planets = [p for p in planets if p.sign in signs]
        if len(el_planets) < 3:
            continue
        unique_signs = set(p.sign for p in el_planets)
        if len(unique_signs) < 3:
            continue
        for combo in combinations(el_planets, 3):
            if len(set(p.sign for p in combo)) < 3:
                continue
            if not all(
                _has_aspect(a.name, b.name, "trine", aspects)
                for a, b in combinations(combo, 2)
            ):
                continue
            gt_names = [p.name for p in combo]
            for p in planets:
                if p.name in gt_names:
                    continue
                for i, gt_name in enumerate(gt_names):
                    if not _has_aspect(gt_name, p.name, "opposition", aspects):
                        continue
                    other_gt = [gt_names[j] for j in range(3) if j != i]
                    if (
                        _has_aspect(other_gt[0], p.name, "sextile", aspects)
                        and _has_aspect(other_gt[1], p.name, "sextile", aspects)
                    ):
                        return ("kite", el, gt_names + [p.name])
    return None


def _detect_mystic_rectangle(
    planets: list, aspects: list
) -> Optional[Tuple[str, str, List[str]]]:
    if len(planets) < 4:
        return None
    opp_pairs = []
    for i, p1 in enumerate(planets):
        for p2 in planets[i + 1 :]:
            if _has_aspect(p1.name, p2.name, "opposition", aspects):
                opp_pairs.append((p1.name, p2.name))
    if len(opp_pairs) < 2:
        return None
    for (a, b), (c, d) in [(opp_pairs[0], opp_pairs[1])]:
        all_names = list(set([a, b, c, d]))
        if len(all_names) < 4:
            return None
        trine_count = sum(
            1
            for x, y in [(a, c), (a, d), (b, c), (b, d)]
            if _has_aspect(x, y, "trine", aspects)
        )
        sextile_count = sum(
            1
            for x, y in [(a, c), (a, d), (b, c), (b, d)]
            if _has_aspect(x, y, "sextile", aspects)
        )
        if trine_count >= 2 and sextile_count >= 2:
            return ("mystic_rectangle", "", all_names)
    return None


class PatternRule(InterpretationRule):
    def __init__(self):
        super().__init__(priority=10)

    def matches(self, chart: ChartData) -> bool:
        return len(chart.planets) >= 3

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[RuleResult]:
        results = []

        detectors = [
            ("grand_trine", lambda: _detect_grand_trine(chart.planets, chart.aspects)),
            ("tsquare", lambda: _detect_tsquare(chart.planets, chart.aspects)),
            ("stellium", lambda: _detect_stellium(chart.planets)),
            ("grand_cross", lambda: _detect_grand_cross(chart.planets, chart.aspects)),
            ("yod", lambda: _detect_yod(chart.planets, chart.aspects)),
            ("kite", lambda: _detect_kite(chart.planets, chart.aspects)),
            (
                "mystic_rectangle",
                lambda: _detect_mystic_rectangle(chart.planets, chart.aspects),
            ),
        ]

        for name, detector in detectors:
            found = detector()
            if found:
                pat_type, qualifier, names = found
                text_data = get_pattern(pat_type, qualifier, lang)
                text = text_data.get("text", "") if text_data else ""
                score = _pattern_scores.get(pat_type, 10)

                base = _pattern_titles.get(pat_type, ("", ""))
                idx = 0 if lang == "vi" else 1
                if qualifier:
                    title = f"{base[idx]} - {qualifier.capitalize()}"
                else:
                    title = base[idx]

                results.append(
                    RuleResult(
                        title_vi=title if lang == "vi" else "",
                        title_en=title if lang == "en" else "",
                        text_vi=text if lang == "vi" else "",
                        text_en=text if lang == "en" else "",
                        score=score,
                        priority=self.priority,
                        category="pattern",
                        tags=[pat_type, qualifier] + names,
                        metadata={
                            "pattern_type": pat_type,
                            "qualifier": qualifier,
                            "planets": names,
                        },
                    )
                )

        return results[0] if len(results) == 1 else RuleResult(
            title_vi="Mẫu Hình Chiêm Tinh" if lang == "vi" else "",
            title_en="Chart Patterns" if lang == "en" else "",
            text_vi="\n\n".join(r.text_vi for r in results) if lang == "vi" else "",
            text_en="\n\n".join(r.text_en for r in results) if lang == "en" else "",
            score=sum(r.score for r in results),
            priority=self.priority,
            category="pattern",
            tags=[t for r in results for t in r.tags],
            metadata={"patterns": [r.metadata for r in results]},
        ) if results else None


RuleRegistry.register(PatternRule())
