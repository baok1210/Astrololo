"""Vimshottari Dasha calculator based on Moon's nakshatra position at birth."""
from datetime import datetime, timedelta
from typing import List
from astrololo.models.chart import DashaPeriod, DashaData
from astrololo.core.jyotish_constants import (
    NAVAGRAHA, DASHA_YEARS, DASHA_SEQUENCE, TOTAL_DASHA_YEARS,
    NAKSHATRA_SPAN, calc_nakshatra,
)


def _graha_name_vi(graha_key: str) -> str:
    g = NAVAGRAHA.get(graha_key)
    return g.name_vi if g else graha_key


def _years_to_days(years: float) -> float:
    return years * 365.25


def calc_vimshottari_dasha(
    moon_sidereal_lon: float,
    birth_dt: datetime,
    levels: int = 2,
) -> DashaData:
    """Calculate Vimshottari Dasha from Moon's sidereal longitude.

    Args:
        moon_sidereal_lon: Moon's sidereal longitude in degrees
        birth_dt: Birth datetime (UTC)
        levels: 1 = Mahadasha only, 2 = include Antardasha
    """
    nak_idx, nak_info, pada = calc_nakshatra(moon_sidereal_lon)
    nak_ruler = nak_info.ruler

    nak_start_deg = nak_idx * NAKSHATRA_SPAN
    elapsed_in_nak = (moon_sidereal_lon % 360) - nak_start_deg
    elapsed_fraction = elapsed_in_nak / NAKSHATRA_SPAN

    ruler_total_years = DASHA_YEARS[nak_ruler]
    balance_years = ruler_total_years * (1 - elapsed_fraction)

    start_idx = DASHA_SEQUENCE.index(nak_ruler)

    mahadashas: List[DashaPeriod] = []
    current_date = birth_dt

    for i in range(9):
        graha_key = DASHA_SEQUENCE[(start_idx + i) % 9]
        if i == 0:
            years = balance_years
        else:
            years = DASHA_YEARS[graha_key]

        end_date = current_date + timedelta(days=_years_to_days(years))

        sub_periods: List[DashaPeriod] = []
        if levels >= 2:
            sub_periods = _calc_antardasha(
                graha_key, current_date, years, start_idx + i
            )

        mahadashas.append(DashaPeriod(
            graha=graha_key,
            graha_name_vi=_graha_name_vi(graha_key),
            start_date=current_date,
            end_date=end_date,
            years=round(years, 4),
            sub_periods=sub_periods,
        ))
        current_date = end_date

    return DashaData(
        birth_nakshatra=nak_info.name_sa,
        birth_nakshatra_ruler=nak_ruler,
        balance_at_birth=round(balance_years, 4),
        mahadasha_sequence=mahadashas,
    )


def _calc_antardasha(
    maha_graha: str,
    maha_start: datetime,
    maha_years: float,
    maha_seq_idx: int,
) -> List[DashaPeriod]:
    """Calculate Antardasha (sub-periods) within a Mahadasha.

    Sub-periods follow the same Dasha sequence starting from the Mahadasha lord.
    Each sub-period's duration is proportional to its own Dasha years relative to
    the total 120-year cycle, scaled to the Mahadasha duration.
    """
    sub_start_idx = DASHA_SEQUENCE.index(maha_graha)
    current = maha_start
    periods: List[DashaPeriod] = []

    for j in range(9):
        sub_graha = DASHA_SEQUENCE[(sub_start_idx + j) % 9]
        sub_years = maha_years * DASHA_YEARS[sub_graha] / TOTAL_DASHA_YEARS
        sub_end = current + timedelta(days=_years_to_days(sub_years))

        periods.append(DashaPeriod(
            graha=sub_graha,
            graha_name_vi=_graha_name_vi(sub_graha),
            start_date=current,
            end_date=sub_end,
            years=round(sub_years, 4),
        ))
        current = sub_end

    return periods
