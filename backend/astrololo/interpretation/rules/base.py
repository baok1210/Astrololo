from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from astrololo.models.chart import ChartData


@dataclass
class RuleResult:
    title_vi: str = ""
    title_en: str = ""
    text_vi: str = ""
    text_en: str = ""
    score: float = 0.0
    priority: int = 0
    category: str = "general"
    tags: List[str] = field(default_factory=list)
    planet: Optional[str] = None
    aspect: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class InterpretationRule(ABC):
    def __init__(self, priority: int = 50):
        self.priority = priority

    @abstractmethod
    def matches(self, chart: ChartData) -> bool:
        """Check if this rule applies to the given chart."""
        pass

    @abstractmethod
    def interpret(self, chart: ChartData, lang: str = "vi") -> Optional[RuleResult] | List[RuleResult]:
        """Generate interpretation text. Returns None if rule doesn't apply.
        Can return a single RuleResult or a list of RuleResults."""
        pass

    def __lt__(self, other: "InterpretationRule") -> bool:
        return self.priority < other.priority
