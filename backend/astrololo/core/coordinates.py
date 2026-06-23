"""Absolute longitude mapping and DMS conversion.

All computation in the pipeline uses raw float (0-360 degrees).
String conversion happens ONLY at the display/rendering boundary.

Rounding algorithm (exact arc-minute):
  deg = floor(lon_abs)
  total_minutes = (lon_abs - deg) * 60
  minutes = floor(total_minutes)
  seconds = (total_minutes - minutes) * 60
  extra = 1 if seconds >= 30 else 0
  display_minutes = minutes + extra
  if display_minutes == 60: deg += 1; display_minutes = 0
"""
from typing import Tuple

SIGN_NAMES_KEY = [
    "aries", "taurus", "gemini", "cancer",
    "leo", "virgo", "libra", "scorpio",
    "sagittarius", "capricorn", "aquarius", "pisces",
]

# Each sign occupies exactly 30 degrees starting from 0 (Aries)
# sign_index = floor(lon_abs / 30)
# position_in_sign = lon_abs % 30


def abs_to_sign(lon_abs: float) -> Tuple[str, float]:
    """Convert absolute longitude (0-360) to (sign_key, position_in_sign)."""
    idx = int(lon_abs // 30) % 12
    return SIGN_NAMES_KEY[idx], lon_abs % 30


def sign_to_abs(sign_key: str, position_in_sign: float) -> float:
    """Convert (sign_key, position_in_sign) to absolute longitude (0-360)."""
    try:
        idx = SIGN_NAMES_KEY.index(sign_key)
    except ValueError:
        raise ValueError(f"Unknown sign key: {sign_key}")
    return idx * 30 + position_in_sign


def decimal_to_dms(decimal_deg: float) -> Tuple[int, int, float]:
    """Convert decimal degrees to (degrees, minutes, seconds).

    Example: 205.9833 → (205, 58, 59.88)
    """
    deg = int(decimal_deg)
    frac = abs(decimal_deg - deg)
    total_minutes = frac * 60
    minutes = int(total_minutes)
    seconds = (total_minutes - minutes) * 60
    return deg, minutes, seconds


def decimal_to_rounded_dms(decimal_deg: float) -> Tuple[int, int]:
    """Convert decimal degrees to rounded (degrees, arc-minutes) for display.

    Rounding: if seconds >= 30, round minutes UP.
    Prevents 1-arc-minute mismatches between planet table and aspect table.

    Example: 205.9833 → (205, 59)
             296.1432 → (296, 9)
    """
    deg = int(decimal_deg)
    frac = abs(decimal_deg - deg)
    total_minutes = frac * 60
    minutes = int(total_minutes)
    seconds = (total_minutes - minutes) * 60
    if seconds >= 30.0:
        minutes += 1
        if minutes >= 60:
            deg += 1
            minutes = 0
    return deg, minutes


def dms_to_display_string(deg: int, minutes: int) -> str:
    """Format as 'DDD°MM' e.g. '205°59'."""
    return f"{deg}°{minutes:02d}'"


def lon_to_display_string(lon_abs: float) -> str:
    """Convert absolute longitude to display string without sign name.

    Example: 205.9833 → "205°59'"
    """
    d, m = decimal_to_rounded_dms(lon_abs)
    return dms_to_display_string(d, m)


def lon_to_sign_display(lon_abs: float) -> Tuple[str, int, int]:
    """Convert absolute longitude to (sign_name, display_deg, display_minutes).

    Example: 205.9833 → ("libra", 25, 59)
    This is the ONLY function that produces human-readable output.
    """
    sign_key, pos_in_sign = abs_to_sign(lon_abs)
    deg_in_sign, minutes = decimal_to_rounded_dms(pos_in_sign)
    return sign_key, deg_in_sign, minutes
