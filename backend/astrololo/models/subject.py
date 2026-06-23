from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import pytz


class GeoLocation(BaseModel):
    latitude: float
    longitude: float
    timezone_str: str


class SubjectData(BaseModel):
    name: str
    year: int
    month: int
    day: int
    hour: int
    minute: int
    latitude: float
    longitude: float
    timezone_str: str = "UTC"
    city: Optional[str] = None
    nation: Optional[str] = None


class AstrologicalSubject(BaseModel):
    name: str
    year: int
    month: int
    day: int
    hour: int
    minute: int
    latitude: float
    longitude: float
    timezone_str: str = "UTC"
    city: Optional[str] = None
    nation: Optional[str] = None
    julian_day_ut: Optional[float] = None
    julian_day_tt: Optional[float] = None
    delta_t: Optional[float] = None

    @property
    def birth_datetime(self) -> datetime:
        import pytz
        tz = pytz.timezone(self.timezone_str)
        return tz.localize(datetime(self.year, self.month, self.day, self.hour, self.minute))

    @property
    def birth_datetime_utc(self) -> datetime:
        return self.birth_datetime.astimezone(pytz.UTC)
