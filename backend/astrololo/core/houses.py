from typing import List, Dict, Any
from astrololo.core.constants import (
    SIGN_ORDER,
    HOUSES,
    SIGNS,
)


HOUSE_SYSTEMS = {
    "placidus": "P",
    "koch": "K",
    "equal": "E",
    "whole_sign": "W",
    "regiomontanus": "R",
    "campanus": "C",
    "porphyry": "O",
}


def calculate_house_cusps(
    ascendant: float,
    mc: float,
    lat: float,
    lng: float,
    system: str = "placidus",
    jd_ut: float = 0,
) -> List[Dict[str, Any]]:
    hsys = HOUSE_SYSTEMS.get(system, "P")

    try:
        import swisseph as swe

        cusps, ascmc = swe.houses_ex(jd_ut, lat, lng, hsys.encode())
    except (ImportError, Exception):
        cusps = _approx_cusps(ascendant, system)

    houses = []
    for i in range(12):
        cusp = cusps[i] if i < len(cusps) else (ascendant + i * 30) % 360
        sign_key = SIGN_ORDER[int(cusp // 30) % 12]
        house_num = i + 1
        h = HOUSES.get(house_num, HOUSES[1])
        houses.append(
            {
                "house_number": house_num,
                "cusp_degree": round(cusp, 4),
                "sign": sign_key,
                "sign_name_vi": SIGNS[sign_key].name_vi,
                "is_angular": h.type_ == "angular",
                "is_succedent": h.type_ == "succedent",
                "is_cadent": h.type_ == "cadent",
            }
        )

    return houses


def assign_planets_to_houses(
    planets: List[Dict], house_cusps: List[float]
) -> List[Dict]:
    assigned = []
    for p in planets:
        lon = p.get("longitude", 0)
        house = find_house(lon, house_cusps)
        p["house"] = house
        p["cusp_proximity"] = check_cusp_proximity(lon, house_cusps, threshold=5.0)
        assigned.append(p)
    return assigned


def find_house(longitude: float, cusps: List[float]) -> int:
    cusps = [c % 360 for c in cusps]

    for i in range(12):
        start = cusps[i]
        end = cusps[(i + 1) % 12]

        if start <= end:
            if start <= longitude < end:
                return i + 1
        else:
            if longitude >= start or longitude < end:
                return i + 1

    return 12


def check_cusp_proximity(longitude: float, cusps: List[float], threshold: float = 5.0) -> dict:
    cusps = [c % 360 for c in cusps]
    lon = longitude % 360
    for i in range(12):
        start = cusps[i]
        end = cusps[(i + 1) % 12]
        if start <= end:
            if start <= lon < end:
                dist = end - lon
                if dist <= threshold:
                    next_h = i + 2 if i + 2 <= 12 else 1
                    return {"near_cusp": True, "next_house": next_h, "distance_deg": round(dist, 4)}
        else:
            if lon >= start or lon < end:
                dist = (end + 360 - lon) % 360
                if dist <= threshold:
                    next_h = i + 2 if i + 2 <= 12 else 1
                    return {"near_cusp": True, "next_house": next_h, "distance_deg": round(dist, 4)}
    return {"near_cusp": False, "next_house": 0, "distance_deg": 0.0}


def _approx_cusps(ascendant: float, system: str) -> List[float]:
    if system == "whole_sign":
        asc_sign_idx = int(ascendant // 30)
        return [(asc_sign_idx * 30 + i * 30) % 360 for i in range(12)]
    elif system == "equal":
        return [(ascendant + i * 30) % 360 for i in range(12)]
    else:
        return [(ascendant + i * 30) % 360 for i in range(12)]


def get_house_systems() -> List[str]:
    return list(HOUSE_SYSTEMS.keys())
