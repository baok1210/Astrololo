from typing import Optional
from astrololo.interpretation.rules.base import InterpretationRule, RuleResult
from astrololo.interpretation.rules.registry import RuleRegistry
from astrololo.models.chart import ChartData
from astrololo.interpretation.keywords import HOUSE_NAME_VI
from astrololo.interpretation.template_loader import get_house_type_text
from astrololo.core.constants import PLANETS, HOUSES


class HouseDistributionRule(InterpretationRule):
    """Summarize which planets are in which houses + house type analysis."""

    def __init__(self):
        super().__init__(priority=15)

    def matches(self, chart: ChartData) -> bool:
        return bool(chart.planets)

    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[RuleResult]:
        # Group planets by house
        house_map: dict[int, list] = {}
        for p in chart.planets:
            if p.body_type != "planet":
                continue
            house_map.setdefault(p.house, []).append(p)

        if not house_map:
            return None

        # House type counts
        angular = succedent = cadent = 0
        for hn, planets in house_map.items():
            h = HOUSES.get(hn)
            if h:
                t = h.type_
                count = len(planets)
                if t == "angular":
                    angular += count
                elif t == "succedent":
                    succedent += count
                elif t == "cadent":
                    cadent += count

        total = angular + succedent + cadent

        # Build lines
        lines = []
        for hn in sorted(house_map):
            planets_in = house_map[hn]
            names = []
            for p in planets_in:
                pl = PLANETS.get(p.name)
                n = pl.name_vi if pl and lang == "vi" else pl.name_en if pl else p.name
                if p.is_retrograde:
                    n += " (R)"
                names.append(n)
            house_label = HOUSE_NAME_VI.get(hn, f"Nhà {hn}")
            lines.append(f"{house_label}: {', '.join(names)}")

        # House type text
        type_parts = []
        type_map = {"angular": angular, "succedent": succedent, "cadent": cadent}
        dominant_type = max(type_map, key=type_map.get)
        balanced = all(abs(type_map[t] - type_map[dominant_type]) <= 1 for t in type_map)

        if balanced and total >= 8:
            type_key = "balanced_houses"
            type_text = get_house_type_text(type_key, lang)
            if type_text:
                type_parts.append(type_text)
        else:
            type_key = f"dominant_{dominant_type}"
            type_text = get_house_type_text(type_key, lang)
            if type_text:
                type_parts.append(type_text)

        # All houses info
        all_houses = set(range(1, 13))
        occupied = set(house_map.keys())
        empty = sorted(all_houses - occupied)
        full_list = [HOUSE_NAME_VI.get(hn, f"Nhà {hn}") for hn in empty]

        if lang == "vi":
            text = f"Có {total} hành tinh phân bố trên {len(house_map)} cung nhà:\n\n"
            text += "\n".join(lines)
            text += "\n\n---\n"
            text += f"Nhà góc (Angular 1-4-7-10): {angular} hành tinh\n"
            text += f"Nhà kế (Succedent 2-5-8-11): {succedent} hành tinh\n"
            text += f"Nhà cuối (Cadent 3-6-9-12): {cadent} hành tinh"
            if type_parts:
                text += f"\n\n{type_parts[0]}"
            if empty:
                text += f"\n\nNhà trống ({len(empty)}): {', '.join(full_list)}."
        else:
            text = f"{total} planets distributed across {len(house_map)} houses:\n\n"
            text += "\n".join(lines)
            text += "\n\n---\n"
            text += f"Angular houses (1-4-7-10): {angular} planets\n"
            text += f"Succedent houses (2-5-8-11): {succedent} planets\n"
            text += f"Cadent houses (3-6-9-12): {cadent} planets"
            if type_parts:
                text += f"\n\n{type_parts[0]}"
            if empty:
                empty_names = [HOUSE_NAME_VI.get(hn, f"House {hn}") for hn in empty]
                text += f"\n\nEmpty houses ({len(empty)}): {', '.join(empty_names)}."

        return RuleResult(
            title_vi="Phân Bố Hành Tinh Theo Nhà" if lang == "vi" else "",
            title_en="Planet Distribution by House" if lang == "en" else "",
            text_vi=text if lang == "vi" else "",
            text_en=text if lang == "en" else "",
            score=float(total),
            priority=self.priority,
            category="house_distribution",
            tags=["distribution", "house"],
            metadata={
                "house_counts": {k: len(v) for k, v in house_map.items()},
                "house_types": {"angular": angular, "succedent": succedent, "cadent": cadent},
            },
        )


RuleRegistry.register(HouseDistributionRule())
