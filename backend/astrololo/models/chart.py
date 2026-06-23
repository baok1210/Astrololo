from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime


class BodyPosition(BaseModel):
    body_type: Literal["planet", "node", "angle"] = "planet"
    name: str
    name_vi: str
    name_en: str = ""
    longitude: float
    latitude: float = 0.0
    distance: float = 0.0
    speed: float = 0.0
    sign: str
    sign_name_vi: str
    sign_name_en: str = ""
    position_in_sign: float
    house: int = 0
    is_retrograde: bool = False
    element: str = ""
    quality: str = ""
    dignity_score: int = 0
    dignity_label: str = "neutral"
    declination: float = 0.0
    cusp_proximity: Optional[Dict[str, Any]] = None


# Backward-compatible alias — existing code using PlanetPosition still works
PlanetPosition = BodyPosition


class HouseData(BaseModel):
    house_number: int
    cusp_degree: float
    sign: str
    sign_name_vi: str
    is_angular: bool = False
    is_succedent: bool = False
    is_cadent: bool = False


class AspectData(BaseModel):
    planet1: str
    planet2: str
    aspect_type: str
    aspect_name_vi: str
    angle: float
    orb: float
    exact: bool = False
    orb_formatted: str = ""  # degrees & arc-minutes e.g. "2°04'"
    nature: str = "neutral"  # harmonious / challenging / neutral
    weight: int = 0
    applying: bool = False
    separating: bool = False


class ElementDistribution(BaseModel):
    fire: float = 0
    earth: float = 0
    air: float = 0
    water: float = 0
    dominant: Optional[str] = None
    deficient: Optional[str] = None


class QualityDistribution(BaseModel):
    cardinal: float = 0
    fixed: float = 0
    mutable: float = 0
    dominant: Optional[str] = None
    deficient: Optional[str] = None


class DispositorResult(BaseModel):
    chain: Dict[str, str] = {}
    final_dispositor: Optional[str] = None
    final_dispositors: List[str] = Field(default_factory=list)
    mutual_receptions: List[tuple] = Field(default_factory=list)


class AspectPattern(BaseModel):
    name: str
    name_vi: str
    score: int
    planets: List[str]
    description_vi: str = ""
    description_en: str = ""


class MidpointData(BaseModel):
    body1: str
    body2: str
    midpoint: float
    sign: str
    sign_vi: str
    position_in_sign: float


class ChartData(BaseModel):
    subject_name: str = "Unknown"
    chart_type: str = "natal"
    datetime_utc: Optional[datetime] = None
    julian_day: Optional[float] = None
    house_system: str = "placidus"
    node_type: str = "mean"
    houses: List[HouseData] = Field(default_factory=list)
    planets: List[PlanetPosition] = Field(default_factory=list)
    aspects: List[AspectData] = Field(default_factory=list)
    aspect_patterns: List[AspectPattern] = Field(default_factory=list)
    ascendant: float = 0.0
    ascendant_sign: str = ""
    mc: float = 0.0
    mc_sign: str = ""
    element_distribution: Optional[ElementDistribution] = None
    quality_distribution: Optional[QualityDistribution] = None
    dispositor: Optional[DispositorResult] = None
    is_daytime: bool = True
    moon_phase: Optional[str] = None
    part_of_fortune: Optional[Dict[str, Any]] = None  # longitude, sign, sign_vi, house
    midpoints: List[MidpointData] = Field(default_factory=list)
    interpretation: Optional[Dict[str, Any]] = None
    validation: Optional[Dict[str, Any]] = None


class InterpretationResult(BaseModel):
    chart_summary: Dict[str, Any] = Field(default_factory=dict)
    planet_interpretations: List[Dict[str, Any]] = Field(default_factory=list)
    aspect_interpretations: List[Dict[str, Any]] = Field(default_factory=list)
    pattern_interpretations: List[Dict[str, Any]] = Field(default_factory=list)
    element_interpretations: List[Dict[str, Any]] = Field(default_factory=list)
    dispositor_interpretation: Optional[str] = None
    overall_interpretation: str = ""
    sections: List[Dict[str, Any]] = Field(default_factory=list)
