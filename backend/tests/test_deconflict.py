"""Phase 4 TDD tests: de-conflicting engine strategies.

Spec 010 §4.
"""
import sys
import os
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from astrololo.models.subject import AstrologicalSubject
from astrololo.analysis.natal import create_natal_chart


def _chart():
    return create_natal_chart(AstrologicalSubject(
        name="LangSon", year=1996, month=3, day=11,
        hour=11, minute=23,
        latitude=21.85, longitude=106.76,
        timezone_str="Asia/Ho_Chi_Minh"
    ), lang="vi")


class TestDeconflictRule:
    def test_deconflict_section_present(self):
        c = _chart()
        sections = c.interpretation.get("sections", []) if isinstance(c.interpretation, dict) else []
        deconf = [s for s in sections if s.get("category") == "deconflict"]
        assert deconf, "deconflict section should appear"

    def test_layering_present(self):
        c = _chart()
        sections = c.interpretation.get("sections", []) if isinstance(c.interpretation, dict) else []
        deconf = [s for s in sections if s.get("category") == "deconflict"]
        assert deconf
        for item in deconf[0].get("items", []):
            if isinstance(item, dict):
                meta = item.get("metadata", {})
                assert "strategies" in meta or "layers" in meta, "metadata must expose strategies/layers"

    def test_no_leak_tokens_in_deconflict(self):
        c = _chart()
        banned = ["18+", "sensual", "sinh dục"]
        text = ""
        sections = c.interpretation.get("sections", []) if isinstance(c.interpretation, dict) else []
        for s in sections:
            if s.get("category") == "deconflict":
                for it in s.get("items", []):
                    if isinstance(it, dict):
                        text += it.get("text", "") + " "
        for token in banned:
            assert token not in text.lower()
