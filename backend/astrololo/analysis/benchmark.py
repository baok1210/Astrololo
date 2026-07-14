"""Benchmark Validation — runs 50 sample profiles and validates output quality."""
from datetime import datetime

from astrololo.models.subject import AstrologicalSubject
from astrololo.analysis.natal import create_natal_chart
from astrololo.interpretation.engine import InterpretationEngine


# 50 diverse birth profiles covering all 12 signs, different eras, and locations
SAMPLE_PROFILES = [
    {"name": "Profile_01", "year": 1990, "month": 1, "day": 15, "hour": 14, "minute": 30, "lat": 21.0285, "lon": 105.8542, "tz": "Asia/Ho_Chi_Minh"},  # Capricorn sun
    {"name": "Profile_02", "year": 1990, "month": 2, "day": 10, "hour": 8, "minute": 0, "lat": 40.7128, "lon": -74.0060, "tz": "America/New_York"},  # Aquarius
    {"name": "Profile_03", "year": 1990, "month": 3, "day": 20, "hour": 6, "minute": 30, "lat": 48.8566, "lon": 2.3522, "tz": "Europe/Paris"},  # Pisces
    {"name": "Profile_04", "year": 1990, "month": 4, "day": 5, "hour": 12, "minute": 0, "lat": 55.7558, "lon": 37.6173, "tz": "Europe/Moscow"},  # Aries
    {"name": "Profile_05", "year": 1990, "month": 5, "day": 18, "hour": 23, "minute": 15, "lat": 35.6762, "lon": 139.6503, "tz": "Asia/Tokyo"},  # Taurus
    {"name": "Profile_06", "year": 1985, "month": 6, "day": 1, "hour": 10, "minute": 45, "lat": -33.8688, "lon": 151.2093, "tz": "Australia/Sydney"},  # Gemini
    {"name": "Profile_07", "year": 1985, "month": 7, "day": 12, "hour": 5, "minute": 30, "lat": 19.0760, "lon": 72.8777, "tz": "Asia/Kolkata"},  # Cancer
    {"name": "Profile_08", "year": 1985, "month": 8, "day": 8, "hour": 20, "minute": 0, "lat": -34.6037, "lon": -58.3816, "tz": "America/Argentina/Buenos_Aires"},  # Leo
    {"name": "Profile_09", "year": 1985, "month": 9, "day": 22, "hour": 15, "minute": 30, "lat": 30.0444, "lon": 31.2357, "tz": "Africa/Cairo"},  # Virgo
    {"name": "Profile_10", "year": 1980, "month": 10, "day": 10, "hour": 4, "minute": 0, "lat": 52.5200, "lon": 13.4050, "tz": "Europe/Berlin"},  # Libra
    {"name": "Profile_11", "year": 1980, "month": 11, "day": 5, "hour": 9, "minute": 15, "lat": 1.3521, "lon": 103.8198, "tz": "Asia/Singapore"},  # Scorpio
    {"name": "Profile_12", "year": 1980, "month": 12, "day": 25, "hour": 18, "minute": 30, "lat": -23.5505, "lon": -46.6333, "tz": "America/Sao_Paulo"},  # Sagittarius
    {"name": "Profile_13", "year": 1995, "month": 1, "day": 28, "hour": 22, "minute": 0, "lat": 51.5074, "lon": -0.1278, "tz": "Europe/London"},
    {"name": "Profile_14", "year": 1995, "month": 3, "day": 15, "hour": 11, "minute": 30, "lat": 34.0522, "lon": -118.2437, "tz": "America/Los_Angeles"},
    {"name": "Profile_15", "year": 1995, "month": 5, "day": 2, "hour": 7, "minute": 0, "lat": 31.2304, "lon": 121.4737, "tz": "Asia/Shanghai"},
    {"name": "Profile_16", "year": 1995, "month": 7, "day": 4, "hour": 16, "minute": 45, "lat": 25.0343, "lon": 121.5645, "tz": "Asia/Taipei"},
    {"name": "Profile_17", "year": 1995, "month": 9, "day": 10, "hour": 3, "minute": 15, "lat": 37.7749, "lon": -122.4194, "tz": "America/Los_Angeles"},
    {"name": "Profile_18", "year": 1995, "month": 11, "day": 22, "hour": 13, "minute": 0, "lat": 43.6532, "lon": -79.3832, "tz": "America/Toronto"},
    {"name": "Profile_19", "year": 2000, "month": 2, "day": 29, "hour": 10, "minute": 30, "lat": -1.2864, "lon": 36.8172, "tz": "Africa/Nairobi"},
    {"name": "Profile_20", "year": 2000, "month": 4, "day": 16, "hour": 1, "minute": 0, "lat": 53.3498, "lon": -6.2603, "tz": "Europe/Dublin"},
    {"name": "Profile_21", "year": 2000, "month": 6, "day": 21, "hour": 5, "minute": 0, "lat": 59.3293, "lon": 18.0686, "tz": "Europe/Stockholm"},
    {"name": "Profile_22", "year": 2000, "month": 8, "day": 15, "hour": 20, "minute": 30, "lat": -22.9068, "lon": -43.1729, "tz": "America/Sao_Paulo"},
    {"name": "Profile_23", "year": 2000, "month": 10, "day": 1, "hour": 14, "minute": 15, "lat": 28.6139, "lon": 77.2090, "tz": "Asia/Kolkata"},
    {"name": "Profile_24", "year": 2000, "month": 12, "day": 7, "hour": 8, "minute": 0, "lat": 41.9028, "lon": 12.4964, "tz": "Europe/Rome"},
    {"name": "Profile_25", "year": 2005, "month": 1, "day": 3, "hour": 0, "minute": 0, "lat": 39.9042, "lon": 116.4074, "tz": "Asia/Shanghai"},
    {"name": "Profile_26", "year": 2005, "month": 3, "day": 28, "hour": 12, "minute": 0, "lat": 33.6844, "lon": 73.0479, "tz": "Asia/Karachi"},
    {"name": "Profile_27", "year": 2005, "month": 6, "day": 5, "hour": 18, "minute": 45, "lat": 3.1390, "lon": 101.6869, "tz": "Asia/Kuala_Lumpur"},
    {"name": "Profile_28", "year": 2005, "month": 8, "day": 20, "hour": 7, "minute": 15, "lat": 42.6977, "lon": 23.3219, "tz": "Europe/Sofia"},
    {"name": "Profile_29", "year": 2005, "month": 10, "day": 12, "hour": 22, "minute": 0, "lat": 41.0082, "lon": 28.9784, "tz": "Europe/Istanbul"},
    {"name": "Profile_30", "year": 2005, "month": 12, "day": 30, "hour": 16, "minute": 30, "lat": -26.2041, "lon": 28.0473, "tz": "Africa/Johannesburg"},
    {"name": "Profile_31", "year": 1975, "month": 2, "day": 14, "hour": 9, "minute": 0, "lat": 45.4642, "lon": 9.1900, "tz": "Europe/Rome"},  # Older generation
    {"name": "Profile_32", "year": 1975, "month": 5, "day": 9, "hour": 14, "minute": 30, "lat": 50.8503, "lon": 4.3517, "tz": "Europe/Brussels"},
    {"name": "Profile_33", "year": 1975, "month": 8, "day": 18, "hour": 3, "minute": 0, "lat": 36.1627, "lon": -86.7816, "tz": "America/Chicago"},
    {"name": "Profile_34", "year": 1975, "month": 11, "day": 1, "hour": 21, "minute": 15, "lat": 40.4168, "lon": -3.7038, "tz": "Europe/Madrid"},
    {"name": "Profile_35", "year": 1965, "month": 1, "day": 20, "hour": 6, "minute": 45, "lat": 47.3769, "lon": 8.5417, "tz": "Europe/Zurich"},  # Baby boomer
    {"name": "Profile_36", "year": 1965, "month": 4, "day": 12, "hour": 17, "minute": 0, "lat": 38.7223, "lon": -9.1393, "tz": "Europe/Lisbon"},
    {"name": "Profile_37", "year": 1965, "month": 7, "day": 8, "hour": 11, "minute": 30, "lat": 39.9334, "lon": 32.8597, "tz": "Europe/Istanbul"},
    {"name": "Profile_38", "year": 1965, "month": 10, "day": 3, "hour": 2, "minute": 0, "lat": 56.1629, "lon": 10.2039, "tz": "Europe/Copenhagen"},
    {"name": "Profile_39", "year": 2010, "month": 3, "day": 15, "hour": 10, "minute": 0, "lat": 14.5995, "lon": 120.9842, "tz": "Asia/Manila"},  # Gen Alpha
    {"name": "Profile_40", "year": 2010, "month": 6, "day": 25, "hour": 15, "minute": 30, "lat": 31.5497, "lon": 74.3436, "tz": "Asia/Karachi"},
    {"name": "Profile_41", "year": 2010, "month": 9, "day": 8, "hour": 4, "minute": 15, "lat": 44.4268, "lon": 26.1025, "tz": "Europe/Bucharest"},
    {"name": "Profile_42", "year": 2010, "month": 12, "day": 1, "hour": 22, "minute": 0, "lat": 29.7604, "lon": -95.3698, "tz": "America/Chicago"},
    {"name": "Profile_43", "year": 1955, "month": 4, "day": 5, "hour": 7, "minute": 30, "lat": 45.5017, "lon": -73.5673, "tz": "America/Toronto"},  # Silent generation
    {"name": "Profile_44", "year": 1955, "month": 8, "day": 22, "hour": 19, "minute": 15, "lat": 34.6937, "lon": 135.5023, "tz": "Asia/Tokyo"},
    {"name": "Profile_45", "year": 1955, "month": 11, "day": 11, "hour": 1, "minute": 0, "lat": 55.9533, "lon": -3.1883, "tz": "Europe/London"},
    {"name": "Profile_46", "year": 1998, "month": 2, "day": 28, "hour": 16, "minute": 30, "lat": -41.2865, "lon": 174.7762, "tz": "Pacific/Auckland"},  # Millennial
    {"name": "Profile_47", "year": 1998, "month": 7, "day": 14, "hour": 11, "minute": 0, "lat": 18.5204, "lon": 73.8567, "tz": "Asia/Kolkata"},
    {"name": "Profile_48", "year": 1998, "month": 10, "day": 31, "hour": 5, "minute": 45, "lat": 36.7783, "lon": -119.4179, "tz": "America/Los_Angeles"},
    {"name": "Profile_49", "year": 2008, "month": 4, "day": 29, "hour": 13, "minute": 0, "lat": 59.9343, "lon": 30.3351, "tz": "Europe/Moscow"},  # Gen Z
    {"name": "Profile_50", "year": 2008, "month": 9, "day": 17, "hour": 20, "minute": 30, "lat": 45.8150, "lon": 15.9819, "tz": "Europe/Zagreb"},
]


def run_benchmark(lang: str = "vi") -> dict:
    """Run validation on 50 profiles. Returns quality metrics."""
    results = []
    passed = 0
    failed = 0

    for profile in SAMPLE_PROFILES:
        profile_result = _validate_profile(profile, lang)
        results.append(profile_result)
        if profile_result["valid"]:
            passed += 1
        else:
            failed += 1

    # Aggregate metrics
    metrics = _compute_metrics(results)
    summary = {
        "total_profiles": len(SAMPLE_PROFILES),
        "passed": passed,
        "failed": failed,
        "pass_rate": round(passed / len(SAMPLE_PROFILES) * 100, 1),
        "metrics": metrics,
        "timestamp": datetime.utcnow().isoformat(),
        "lang": lang,
    }
    return summary


def _validate_profile(profile: dict, lang: str) -> dict:
    """Generate chart for a single profile and validate output quality."""
    try:
        subject = AstrologicalSubject(
            name=profile["name"],
            year=profile["year"], month=profile["month"], day=profile["day"],
            hour=profile["hour"], minute=profile["minute"],
            latitude=profile["lat"], longitude=profile["lon"],
            timezone_str=profile["tz"],
        )
        chart = create_natal_chart(subject, lang=lang)
        engine = InterpretationEngine(lang=lang)
        interp = engine.interpret(chart)

        sections = interp.sections
        cats = {s.get("category") for s in sections if isinstance(s, dict)}
        if not cats:
            cats = {s.category for s in sections if hasattr(s, "category")}

        # Validation checks
        issues = []
        if "planet_in_sign" not in cats:
            issues.append("missing_planet_in_sign")
        if "aspect" not in cats:
            issues.append("missing_aspect")
        if "element" not in cats:
            issues.append("missing_element")
        if "dignity" not in cats:
            issues.append("missing_dignity")

        planet_count = len([b for b in chart.planets if b.body_type == "planet"])
        if planet_count < 10:
            issues.append(f"low_planet_count:{planet_count}")

        aspect_count = len(chart.aspects)
        if aspect_count < 10:
            issues.append(f"low_aspect_count:{aspect_count}")

        # Check for non-empty interpretation text
        empty_sections = []
        for s in sections:
            item_list = s.get("items", []) if isinstance(s, dict) else (s.items if hasattr(s, "items") else [])
            for item in item_list:
                text = item.get("text", "") if isinstance(item, dict) else ""
                if not text or len(text.strip()) < 20:
                    cat_name = s.get("category", "?") if isinstance(s, dict) else (s.category if hasattr(s, "category") else "?")
                    empty_sections.append(cat_name)
                    break
        if empty_sections:
            issues.append(f"empty_text:{','.join(set(empty_sections))}")

        valid = len(issues) == 0
        return {
            "name": profile["name"],
            "valid": valid,
            "planet_count": planet_count,
            "aspect_count": aspect_count,
            "section_count": len(sections),
            "categories": list(cats),
            "issues": issues,
        }
    except Exception as e:
        return {
            "name": profile["name"],
            "valid": False,
            "error": str(e),
            "issues": ["exception"],
        }


def _compute_metrics(results: list) -> dict:
    """Compute aggregate quality metrics."""
    valid_results = [r for r in results if r.get("valid")]
    if not valid_results:
        return {"avg_planet_count": 0, "avg_aspect_count": 0, "avg_section_count": 0}

    avg_planets = sum(r["planet_count"] for r in valid_results) / len(valid_results)
    avg_aspects = sum(r["aspect_count"] for r in valid_results) / len(valid_results)
    avg_sections = sum(r["section_count"] for r in valid_results) / len(valid_results)

    all_cats = set()
    for r in valid_results:
        all_cats.update(r.get("categories", []))
    cat_coverage = sorted(all_cats)

    # Common issues
    all_issues = []
    for r in results:
        all_issues.extend(r.get("issues", []))
    from collections import Counter
    top_issues = Counter(all_issues).most_common(5)

    return {
        "avg_planet_count": round(avg_planets, 1),
        "avg_aspect_count": round(avg_aspects, 1),
        "avg_section_count": round(avg_sections, 1),
        "category_coverage": cat_coverage,
        "coverage_count": len(cat_coverage),
        "top_issues": [{"issue": k, "count": v} for k, v in top_issues],
    }


def print_benchmark_report(summary: dict):
    """Print a human-readable benchmark report."""
    print("=" * 60)
    print(f"BENCHMARK REPORT — {summary['lang'].upper()}")
    print(f"Timestamp: {summary['timestamp']}")
    print("=" * 60)
    print(f"Total profiles: {summary['total_profiles']}")
    print(f"Passed: {summary['passed']}  |  Failed: {summary['failed']}")
    print(f"Pass rate: {summary['pass_rate']}%")
    print()

    if "error" in summary:
        print(f"ERROR: {summary['error']}")
        return

    metrics = summary.get("metrics", {})
    print("--- Quality Metrics ---")
    print(f"Avg planets per chart: {metrics.get('avg_planet_count', 'N/A')}")
    print(f"Avg aspects per chart: {metrics.get('avg_aspect_count', 'N/A')}")
    print(f"Avg sections per chart: {metrics.get('avg_section_count', 'N/A')}")
    print(f"Unique categories: {metrics.get('coverage_count', 0)}")
    print(f"Categories: {', '.join(metrics.get('category_coverage', []))}")
    print()

    top_issues = metrics.get("top_issues", [])
    if top_issues:
        print("--- Top Issues ---")
        for issue in top_issues:
            print(f"  {issue['issue']}: {issue['count']} profiles")
    else:
        print("  No issues found!")
    print("=" * 60)


if __name__ == "__main__":
    print("Running benchmark (vi)...")
    summary_vi = run_benchmark("vi")
    print_benchmark_report(summary_vi)
    print()
    print("Running benchmark (en)...")
    summary_en = run_benchmark("en")
    print_benchmark_report(summary_en)