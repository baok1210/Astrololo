"""Zero-Error Validation Pipeline — 7 checks.

Check 1: ASC == House I cusp
Check 2: MC  == House X cusp
Check 3: Planet-House inequality C(n) <= P < C(n+1)
Check 4: Retrograde flags match ephemeris speed
Check 5: 5-Degree Cusp Rule
Check 6: Opposition + Conjunction on same axis == 180°
Check 7: Interpretation text house == actual house index
"""
from typing import List, Dict, Any
import re
from astrololo.models.chart import ChartData


def validate_chart(chart: ChartData) -> Dict[str, Any]:
    checks = []
    errors = []
    warnings = []

    cusps = [h.cusp_degree % 360 for h in chart.houses] if chart.houses else []

    # ------------------------------------------------------------------ #
    # Check 1: ASC == House I cusp                                        #
    # ------------------------------------------------------------------ #
    c1_passed, c1_detail = False, ""
    if chart.houses and len(chart.houses) > 0:
        diff = abs(chart.houses[0].cusp_degree - chart.ascendant)
        if diff < 0.01:
            c1_passed = True
            c1_detail = f"ASC ({chart.ascendant:.4f}) matches House I cusp ({chart.houses[0].cusp_degree:.4f})"
        else:
            c1_detail = f"MISMATCH: ASC ({chart.ascendant:.4f}) != House I cusp ({chart.houses[0].cusp_degree:.4f})"
            errors.append(c1_detail)
    else:
        c1_detail = "No houses — cannot validate ASC"
        errors.append(c1_detail)
    checks.append({"check": "ASC == House I cusp", "passed": c1_passed, "detail": c1_detail})

    # ------------------------------------------------------------------ #
    # Check 2: MC == House X cusp                                         #
    # ------------------------------------------------------------------ #
    c2_passed, c2_detail = False, ""
    if len(chart.houses) >= 10:
        diff = abs(chart.houses[9].cusp_degree - chart.mc)
        if diff < 0.01:
            c2_passed = True
            c2_detail = f"MC ({chart.mc:.4f}) matches House X cusp ({chart.houses[9].cusp_degree:.4f})"
        else:
            c2_detail = f"MISMATCH: MC ({chart.mc:.4f}) != House X cusp ({chart.houses[9].cusp_degree:.4f})"
            errors.append(c2_detail)
    else:
        c2_detail = "No houses — cannot validate MC"
        errors.append(c2_detail)
    checks.append({"check": "MC == House X cusp", "passed": c2_passed, "detail": c2_detail})

    # ------------------------------------------------------------------ #
    # Check 3: Planet-House inequality C(n) <= P < C(n+1)                 #
    # ------------------------------------------------------------------ #
    c3_passed = True
    c3_details = []
    for p in chart.planets:
        lon = p.longitude % 360
        expected = _find_house_strict(lon, cusps) if cusps else 1
        if expected != p.house:
            c3_passed = False
            msg = f"HOUSE MISMATCH: {p.name} at {lon:.4f} assigned H{p.house} but inequality gives H{expected}"
            errors.append(msg)
            c3_details.append(msg)
        else:
            c3_details.append(f"{p.name} H{p.house} OK")
    checks.append({"check": "Planet-House inequality", "passed": c3_passed, "detail": "; ".join(c3_details)})

    # ------------------------------------------------------------------ #
    # Check 4: Retrograde flags match ephemeris speed (only body_type="planet") #
    # ------------------------------------------------------------------ #
    c4_passed = True
    c4_details = []
    for p in chart.planets:
        if p.body_type != "planet":
            c4_details.append(f"{p.name} retro skipped ({p.body_type})")
            continue
        retro_flag = p.is_retrograde
        expected_retro = p.speed < 0
        if retro_flag != expected_retro:
            c4_passed = False
            msg = f"RETROFLAG MISMATCH: {p.name} speed={p.speed:.6f}, is_retrograde={retro_flag}, expected={expected_retro}"
            errors.append(msg)
            c4_details.append(msg)
        else:
            c4_details.append(f"{p.name} retro={retro_flag} OK")
    checks.append({"check": "Retrograde flags", "passed": c4_passed, "detail": "; ".join(c4_details)})

    # ------------------------------------------------------------------ #
    # Check 5: 5-Degree Cusp Rule                                         #
    # ------------------------------------------------------------------ #
    c5_details = []
    for p in chart.planets:
        cp = _check_cusp_proximity(p.longitude % 360, cusps, threshold=5.0) if cusps else {"near_cusp": False}
        if cp["near_cusp"]:
            w = f"{p.name} at {p.sign} {p.position_in_sign:.2f} is {cp['distance_deg']:.2f}° before H{cp['next_house']} cusp"
            warnings.append(w)
            c5_details.append(w)
    checks.append({"check": "5-Degree Cusp Rule", "passed": True, "detail": "; ".join(c5_details) if c5_details else "No planets near cusps"})

    # ------------------------------------------------------------------ #
    # Check 6: Opposition + Conjunction on same axis == 180°              #
    # ------------------------------------------------------------------ #
    c6_passed = True
    c6_details = []
    axes = [("ascendant", "descendant"), ("mc", "ic")]
    for body in chart.planets:
        for ax_a, ax_b in axes:
            opp = _find_aspect(chart.aspects, body.name, ax_a, "opposition")
            conj = _find_aspect(chart.aspects, body.name, ax_b, "conjunction")
            if opp and conj:
                total = opp.angle + conj.angle
                if abs(total - 180) > 0.5:
                    c6_passed = False
                    msg = f"Axis FAIL: {body.name} {ax_a} opp ({opp.angle:.2f}) + {ax_b} conj ({conj.angle:.2f}) = {total:.2f} ≠ 180"
                    errors.append(msg)
                    c6_details.append(msg)
                else:
                    c6_details.append(f"{body.name} axis {ax_a}/{ax_b}: {opp.angle:.2f}+{conj.angle:.2f}={total:.2f} OK")
    checks.append({"check": "Axis Opposition+Conjunction == 180°", "passed": c6_passed, "detail": "; ".join(c6_details) if c6_details else "No axis aspects to check"})

    # ------------------------------------------------------------------ #
    # Check 7: Interpretation text house == actual house index            #
    # ------------------------------------------------------------------ #
    c7_passed = True
    c7_details = []
    if chart.interpretation:
        for section_key, section_items in chart.interpretation.items():
            if not isinstance(section_items, list):
                continue
            for item in section_items:
                title = item.get("title", "")
                # Match patterns like "ở Nhà 10" or "ở Nhà 1"
                m = re.search(r"Nhà\s+(\d+)", title)
                if m:
                    text_house = int(m.group(1))
                    body_key = item.get("key") or item.get("name", "")
                    actual_body = next((p for p in chart.planets if p.name == body_key), None)
                    if actual_body and actual_body.house != text_house:
                        c7_passed = False
                        msg = f"TEXT MISMATCH: {body_key} title says 'Nhà {text_house}' but actual H{actual_body.house}"
                        errors.append(msg)
                        c7_details.append(msg)
                    elif actual_body:
                        c7_details.append(f"{body_key}: text H{text_house} = actual H{actual_body.house} OK")
    checks.append({"check": "Interpretation text house matches actual house", "passed": c7_passed, "detail": "; ".join(c7_details) if c7_details else "No interpretation to check"})

    return {
        "passed": all(c["passed"] for c in checks),
        "checks": checks,
        "errors": errors,
        "warnings": warnings,
    }


def _find_house_strict(longitude: float, cusps: List[float]) -> int:
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


def _check_cusp_proximity(longitude: float, cusps: List[float], threshold: float = 5.0) -> Dict[str, Any]:
    for i in range(12):
        start = cusps[i]
        end = cusps[(i + 1) % 12]
        if start <= end:
            if start <= longitude < end:
                dist = end - longitude
                if dist <= threshold:
                    nh = i + 2 if i + 2 <= 12 else 1
                    return {"near_cusp": True, "next_house": nh, "distance_deg": round(dist, 4)}
        else:
            if longitude >= start or longitude < end:
                dist = (end + 360 - longitude) % 360
                if dist <= threshold:
                    nh = i + 2 if i + 2 <= 12 else 1
                    return {"near_cusp": True, "next_house": nh, "distance_deg": round(dist, 4)}
    return {"near_cusp": False, "next_house": 0, "distance_deg": 0.0}


def _find_aspect(aspects, p1: str, p2: str, asp_type: str):
    """Find an aspect between p1 and p2 of given type."""
    for a in aspects:
        if a.aspect_type == asp_type:
            if (a.planet1 == p1 and a.planet2 == p2) or (a.planet1 == p2 and a.planet2 == p1):
                return a
    return None
