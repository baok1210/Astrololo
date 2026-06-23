import math
import logging
from typing import Tuple, List, Optional

import os

logger = logging.getLogger(__name__)

HAS_SWISSEPH = False
EPHE_PATH = None
try:
    import swisseph as swe
    HAS_SWISSEPH = True
    # Look for ephe/ relative to project root or this file
    _root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    _ephe_candidates = [
        os.path.join(_root, "ephe"),
        os.path.join(os.path.dirname(_root), "ephe"),
        os.path.join(os.getcwd(), "ephe"),
        os.environ.get("SE_EPHE_PATH", ""),
    ]
    for _p in _ephe_candidates:
        if _p and os.path.isdir(_p):
            swe.set_ephe_path(_p)
            EPHE_PATH = _p
            break
except ImportError:
    swe = None

_PLANET_CODES = {
    "sun": 0, "moon": 1, "mercury": 2, "venus": 3, "mars": 4,
    "jupiter": 5, "saturn": 6, "uranus": 7, "neptune": 8, "pluto": 9,
    "mean_node": 10, "true_node": 11,
    "chiron": 15, "ceres": 17, "pallas": 18, "juno": 19, "vesta": 20,
}

_MEAN_ORBITAL_SPEEDS = {
    "sun": 0.9856, "moon": 13.176, "mercury": 1.383, "venus": 1.204,
    "mars": 0.524, "jupiter": 0.083, "saturn": 0.033, "uranus": 0.012,
    "neptune": 0.006, "pluto": 0.004,
}


def calc_julian_day(year: int, month: int, day: int, hour: int = 0, minute: int = 0) -> float:
    if HAS_SWISSEPH:
        return swe.julday(year, month, day, hour + minute / 60.0)
    y, m = year, month
    if m <= 2:
        y -= 1
        m += 12
    a = math.floor(y / 100)
    b = 2 - a + math.floor(a / 4)
    jd = math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + day + (hour + minute / 60.0) / 24.0 + b - 1524.5
    return jd


def calc_delta_t(year: int, month: int) -> float:
    if HAS_SWISSEPH:
        try:
            return swe.deltat(year + (month - 0.5) / 12.0)
        except Exception as e:
            logger.warning(f"Swiss Ephemeris failed to calculate delta_t: {e}")
            pass
    y = year + (month - 0.5) / 12.0
    if y < 1900:
        return 5.0
    elif y < 2000:
        return 60.0
    else:
        return 65.0 + 0.3 * (y - 2000)


def calc_planet_position_ut(jd_ut: float, planet: str) -> Tuple[float, float, float, float]:
    lon, lat, dist = 0.0, 0.0, 1.0
    speed = _MEAN_ORBITAL_SPEEDS.get(planet, 1.0)
    code = _PLANET_CODES.get(planet)
    if HAS_SWISSEPH and code is not None:
        try:
            flags = swe.FLG_SWIEPH | swe.FLG_SPEED
            result = swe.calc_ut(jd_ut, code, flags)
            lon = result[0][0]
            lat = result[0][1]
            dist = result[0][2]
            speed = result[0][3]
        except Exception as e:
            logger.warning(f"Swiss Ephemeris failed to calculate position for {planet}: {e}")
            pass
    elif code is None:
        logger.warning(f"No planet code found for {planet}")
        pass
    if lon == 0.0:
        t = (jd_ut - 2451545.0) / 365.25
        t_p = t / 365.25  # centuries
        if planet == "sun":
            M = (357.5291 + 35999.0503 * t) % 360
            C = (1.9148 * math.sin(math.radians(M)) + 0.02 * math.sin(math.radians(2 * M)) + 0.0003 * math.sin(math.radians(3 * M)))
            lon = (M + C + 180 + 102.9372) % 360
        elif planet == "moon":
            lon = (218.3165 + 481267.8813 * t) % 360
            lat = 5.13 * math.sin(math.radians(83.35 + 477198.85 * t_p))
        elif planet in ("mercury", "venus", "mars", "jupiter", "saturn"):
            _elem = {
                "mercury":  (252.2509, 538101628.29, 7.0048, 48.3317, 77.4561, 0.387098),
                "venus":    (181.9798, 210664136.06, 3.3947, 76.6799, 131.5637, 0.723332),
                "mars":     (355.4530, 68905077.44,  1.8497, 49.5595, 336.0602, 1.523712),
                "jupiter":  (34.3515,  10925660.57,   1.3033, 100.4644, 14.3314, 5.202887),
                "saturn":   (50.0774,  4399609.86,    2.4889, 113.6655, 93.0568, 9.536676),
            }[planet]
            L, N_dot, i, Omega, w, a = _elem
            L_deg = (L + N_dot * t_p) % 360
            M_deg = (L_deg - w) % 360
            e = {"mercury": 0.2056, "venus": 0.0068, "mars": 0.0934, "jupiter": 0.0484, "saturn": 0.0539}[planet]
            E = M_deg
            for _ in range(5):
                E = M_deg + math.degrees(e * math.sin(math.radians(E)))
            lon = (math.degrees(math.atan2(math.sqrt(1-e*e)*math.sin(math.radians(E)), math.cos(math.radians(E))-e)) + w) % 360
    return (lon % 360), lat, dist, speed


def calc_house_cusps_ut(jd_ut: float, lat: float, lng: float, hsys: str = "P") -> Tuple[List[float], List[float]]:
    if HAS_SWISSEPH:
        try:
            cusps, ascmc = swe.houses_ex(jd_ut, lat, lng, hsys.encode())
            return list(cusps), list(ascmc)
        except Exception as e:
            logger.warning(f"Swiss Ephemeris failed to calculate house cusps: {e}")
            pass
    logger.info(f"Using equal house cusps for {hsys} system")
    cusps = [(i * 30.0) for i in range(13)]
    ascmc = [0.0, 0.0]
    return cusps, ascmc


def calc_sunrise_sunset(jd_ut: float, lat: float, lng: float) -> Tuple[Optional[float], Optional[float]]:
    if HAS_SWISSEPH:
        try:
            rise = swe.rise_trans(jd_ut, 0, 0, b"")
            _set = swe.rise_trans(jd_ut, 0, 0, b"")
            return rise, _set
        except Exception as e:
            logger.warning(f"Swiss Ephemeris failed to calculate sunrise/sunset: {e}")
            pass
    return None, None


def calc_moon_phase(jd_ut: float) -> dict:
    try:
        sun_lon, _, _, _ = calc_planet_position_ut(jd_ut, "sun")
        moon_lon, _, _, _ = calc_planet_position_ut(jd_ut, "moon")
        diff = (moon_lon - sun_lon) % 360
        phase_names = ["New Moon", "Waxing Crescent", "First Quarter", "Waxing Gibbous",
                       "Full Moon", "Waning Gibbous", "Last Quarter", "Waning Crescent"]
        idx = int((diff / 45) % 8)
        illumination = (1 - math.cos(math.radians(diff))) / 2 * 100
        return {"phase": phase_names[idx], "illumination": round(illumination, 1), "angle": round(diff, 2)}
    except Exception as e:
        logger.warning(f"Failed to calculate moon phase: {e}")
        return {"phase": "Unknown", "illumination": 0, "angle": 0}


def _obliquity(jd_ut: float) -> float:
    """Compute true obliquity of the ecliptic for given JD using IAU 1980 formula."""
    t = (jd_ut - 2451545.0) / 36525.0
    eps = 23.439291 - 0.0130042 * t - 1.64e-7 * t * t + 5.04e-7 * t * t * t
    return math.radians(eps)


def calc_declination(jd_ut: float, planet: str) -> float:
    code = _PLANET_CODES.get(planet)
    if HAS_SWISSEPH and code is not None:
        try:
            result = swe.calc_ut(jd_ut, code, swe.FLG_SWIEPH)
            lon_deg = result[0][0]
            lat_deg = result[0][1]
            eps = _obliquity(jd_ut)
            lon_r = math.radians(lon_deg)
            lat_r = math.radians(lat_deg)
            sin_dec = math.sin(lat_r) * math.cos(eps) + math.cos(lat_r) * math.sin(eps) * math.sin(lon_r)
            return math.degrees(math.asin(max(-1, min(1, sin_dec))))
        except Exception as e:
            logger.warning(f"Swiss Ephemeris failed to calculate declination for {planet}: {e}")
            pass
    return 0.0


def is_daytime(jd_ut: float, lat: float, lng: float) -> bool:
    try:
        code = _PLANET_CODES.get("sun")
        if HAS_SWISSEPH and code is not None:
            result = swe.calc_ut(jd_ut, code, swe.FLG_SWIEPH)
            sun_lon = math.radians(result[0][0])
            sun_lat = math.radians(result[0][1])
            eps = _obliquity(jd_ut)
            gmst = swe.sidtime(jd_ut) * 15.0
            lat_r = math.radians(lat)
            lst = gmst + lng
            ra = math.degrees(math.atan2(math.sin(sun_lon) * math.cos(eps) - math.tan(sun_lat) * math.sin(eps), math.cos(sun_lon)))
            ha = math.radians(lst - ra)
            alt = math.asin(math.sin(lat_r) * math.sin(sun_lat) + math.cos(lat_r) * math.cos(sun_lat) * math.cos(ha))
            return alt > 0
    except Exception as e:
        logger.warning(f"Failed to determine if daytime: {e}")
    return True
