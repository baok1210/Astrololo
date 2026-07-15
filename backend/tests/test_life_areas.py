"""Tests for life-area scoring (tra-cuu-ban-do-sao-1, P0)."""
import os
import sys

sys.path.insert(0, r"C:\Users\BabaBun\Downloads\Astrololo\Astrololo\backend")

from astrololo.models.subject import AstrologicalSubject
from astrololo.analysis.natal import create_natal_chart
from astrololo.analysis.life_areas import calculate_life_areas


def _chart(lang="vi"):
    sub = AstrologicalSubject(
        name="Doan Viet Bao", year=1996, month=11, day=15, hour=6, minute=30,
        latitude=20.95, longitude=105.85, timezone_str="Asia/Ho_Chi_Minh",
    )
    return create_natal_chart(sub, lang=lang)


def test_life_areas_count_and_range():
    chart = _chart()
    areas = calculate_life_areas(chart)
    assert len(areas) == 14
    for a in areas:
        assert 0 <= a["score"] <= 100
        assert a["title_vi"] and a["title_en"]


def test_life_areas_in_engine_output():
    chart = _chart("vi")
    secs = {s["category"]: s for s in chart.interpretation.get("sections", [])}
    assert "life_area" in secs
    assert len(secs["life_area"]["items"]) == 14
    assert "moon_sign" in secs


def test_career_area_present():
    chart = _chart()
    areas = {a["key"]: a for a in calculate_life_areas(chart)}
    assert "career" in areas
    # Mars is in house 10 for this chart -> career should be non-trivial
    assert areas["career"]["score"] >= 40
