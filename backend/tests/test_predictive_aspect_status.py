"""Phase 5 TDD tests: aspect status integration for predictive endpoints."""
import sys, os
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from astrololo.models.subject import AstrologicalSubject
from astrololo.analysis.transit import create_transits
from astrololo.analysis.progression import create_progressions
from astrololo.analysis.solar_return import create_solar_return

SUBJECT = AstrologicalSubject(
    name="LangSon", year=1996, month=3, day=11,
    hour=11, minute=23, latitude=21.85, longitude=106.76,
    timezone_str="Asia/Ho_Chi_Minh",
)


class TestPredictiveAspectStatusIntegration:
    def test_transit_payload_has_aspect_status(self):
        data = create_transits(SUBJECT, 1996, 3, 18)
        assert "aspect_status_summary" in data
        summary = data["aspect_status_summary"] or {}
        assert {
            "applying", "separating", "exact", "total",
        }.issubset(summary.keys())
        assert summary.get("applying", 0) + summary.get("separating", 0) == summary.get("total", 0)
        assert summary.get("exact", 0) <= summary.get("total", 0)
        for x in data.get("transit_aspects", []):
            assert x.get("applying") is not None
            assert x.get("separating") is not None
            assert x.get("exact") is not None
            assert "aspect_status" in x
            assert x["aspect_status"] in {"applying", "separating", "exact", "unknown"}

    def test_progression_payload_has_aspect_status(self):
        data = create_progressions(SUBJECT, age_years=30.0)
        assert "aspect_status_summary" in data
        summary = data["aspect_status_summary"] or {}
        for key in {"applying", "separating", "exact", "total"}:
            assert key in summary

    def test_solar_return_payload_has_aspect_status(self):
        data = create_solar_return(SUBJECT, target_year=2026)
        assert "aspect_status_summary" in data
        summary = data["aspect_status_summary"] or {}
        for key in {"applying", "separating", "exact", "total"}:
            assert key in summary

    def test_no_leak_tokens(self):
        for builder, *args in (
            (create_transits, SUBJECT, 1996, 3, 18),
            (create_progressions, SUBJECT, 30.0),
            (create_solar_return, SUBJECT, 2026),
        ):
            data = builder(*args)
            tokens = str(data.get("aspect_status_summary", {}))
            assert "18+" not in tokens.lower()
            assert "sensual" not in tokens.lower()
            assert "sinh dục" not in tokens.lower()
