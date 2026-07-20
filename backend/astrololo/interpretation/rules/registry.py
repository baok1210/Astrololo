from typing import List
import importlib
from astrololo.interpretation.rules.base import InterpretationRule

_RULE_MODULES = [
    "astrololo.interpretation.rules.ascendant_rule",
    "astrololo.interpretation.rules.mc_rule",
    "astrololo.interpretation.rules.pof_rule",
    "astrololo.interpretation.rules.sun_moon_rule",
    "astrololo.interpretation.rules.dominant_planet_rule",
    "astrololo.interpretation.rules.planet_in_sign_rule",
    "astrololo.interpretation.rules.planet_in_house_rule",
    "astrololo.interpretation.rules.aspect_rules",
    "astrololo.interpretation.rules.aspect_synthesis_rule",
    "astrololo.interpretation.rules.dignity_rules",
    "astrololo.interpretation.rules.retrograde_rule",
    "astrololo.interpretation.rules.moon_phase_rule",
    "astrololo.interpretation.rules.midpoint_rule",
    "astrololo.interpretation.rules.hemisphere_rule",
    "astrololo.interpretation.rules.house_ruler_rule",
    "astrololo.interpretation.rules.declination_rule",
    "astrololo.interpretation.rules.house_cusp_rule",
    "astrololo.interpretation.rules.house_placement_rule",
    "astrololo.interpretation.rules.house_distribution_rule",
    "astrololo.interpretation.rules.element_rules",
    "astrololo.interpretation.rules.quality_rules",
    "astrololo.interpretation.rules.dispositor_rules",
    "astrololo.interpretation.rules.pattern_rules",
    "astrololo.interpretation.rules.combination_rules",
    "astrololo.interpretation.rules.synthesis_rules",
    "astrololo.interpretation.rules.fixed_star_rule",
    "astrololo.interpretation.rules.strength_weakness_rule",
    "astrololo.interpretation.rules.life_area_rule",
    "astrololo.interpretation.rules.moon_sign_rule",
    "astrololo.interpretation.rules.aspect_group_rule",
    "astrololo.interpretation.rules.node_rule",
    "astrololo.interpretation.rules.mc_ic_axis_rule",
    "astrololo.interpretation.rules.chart_shape_rule",
    "astrololo.interpretation.rules.micro_synthesis_rule",
    "astrololo.interpretation.rules.cross_synthesis_rule",
    "astrololo.interpretation.rules.release_point_rule",
    "astrololo.interpretation.rules.rulership_axes_rule",
    "astrololo.interpretation.rules.encyclopedia_rule",
    "astrololo.interpretation.rules.executive_summary_rule",
]


class RuleRegistry:
    _rules: List[InterpretationRule] = []
    _loaded: bool = False

    @classmethod
    def register(cls, rule: InterpretationRule) -> None:
        cls._rules.append(rule)
        cls._rules.sort(key=lambda r: r.priority)

    @classmethod
    def get_rules(cls) -> List[InterpretationRule]:
        if not cls._loaded:
            cls._auto_discover()
            cls._loaded = True
        return cls._rules

    @classmethod
    def _auto_discover(cls) -> None:
        for mod_name in _RULE_MODULES:
            try:
                importlib.import_module(mod_name)
            except Exception:
                pass
