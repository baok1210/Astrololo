import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from astrololo.models.subject import AstrologicalSubject
from astrololo.analysis.natal import create_natal_chart

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="Astrololo API",
    description="High-precision astrology interpretation engine",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChartRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Subject name")
    year: int = Field(..., ge=1900, le=2100, description="Birth year (1900-2100)")
    month: int = Field(..., ge=1, le=12, description="Birth month (1-12)")
    day: int = Field(..., ge=1, le=31, description="Birth day (1-31)")
    hour: int = Field(0, ge=0, le=23, description="Birth hour (0-23)")
    minute: int = Field(0, ge=0, le=59, description="Birth minute (0-59)")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude (-90 to 90)")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude (-180 to 180)")
    timezone_str: str = Field("UTC", description="Timezone name (e.g., Asia/Ho_Chi_Minh, UTC)")
    house_system: str = Field("placidus", pattern="^(placidus|koch|equal|whole_sign|regiomontanus|campanus|porphyry)$")
    node_type: str = Field("mean", pattern="^(mean|true)$")
    lang: str = Field("vi", pattern="^(vi|en)$")
    esoteric: bool = Field(True, description="Show esoteric astrology content")
    zodiac_type: str = Field("tropical", pattern="^(tropical|sidereal)$", description="Zodiac system")
    ayanamsa: str = Field("lahiri", pattern="^(lahiri|raman|krishnamurti)$", description="Ayanamsa for sidereal")
    include_minor_aspects: bool = Field(True, description="Include minor aspects (quincunx, semisextile, etc.)")
    orb_conjunction: float = Field(8.0, ge=0.0, le=15.0, description="Orb for conjunction (degrees)")
    orb_opposition: float = Field(8.0, ge=0.0, le=15.0, description="Orb for opposition (degrees)")
    orb_square: float = Field(8.0, ge=0.0, le=15.0, description="Orb for square (degrees)")
    orb_trine: float = Field(8.0, ge=0.0, le=15.0, description="Orb for trine (degrees)")
    orb_sextile: float = Field(6.0, ge=0.0, le=15.0, description="Orb for sextile (degrees)")
    orb_quincunx: float = Field(3.0, ge=0.0, le=10.0, description="Orb for quincunx (degrees)")
    orb_semisextile: float = Field(3.0, ge=0.0, le=10.0, description="Orb for semisextile (degrees)")
    orb_semisquare: float = Field(2.0, ge=0.0, le=10.0, description="Orb for semisquare (degrees)")
    orb_sesquiquadrate: float = Field(2.0, ge=0.0, le=10.0, description="Orb for sesquiquadrate (degrees)")
    orb_quintile: float = Field(2.0, ge=0.0, le=10.0, description="Orb for quintile (degrees)")


class TransitRequest(ChartRequest):
    transit_year: int = Field(..., ge=1900, le=2100, description="Transit year")
    transit_month: int = Field(..., ge=1, le=12, description="Transit month")
    transit_day: int = Field(..., ge=1, le=31, description="Transit day")


class ProgressionRequest(ChartRequest):
    age: float = Field(..., ge=0.0, le=120.0, description="Age in years for secondary progression")


class SolarReturnRequest(ChartRequest):
    target_year: int = Field(..., ge=1900, le=2100, description="Year for solar return calculation")


class SynastryRequest(BaseModel):
    person1_name: str = Field(..., min_length=1)
    person1_year: int = Field(..., ge=1900, le=2100)
    person1_month: int = Field(..., ge=1, le=12)
    person1_day: int = Field(..., ge=1, le=31)
    person1_hour: int = Field(0, ge=0, le=23)
    person1_minute: int = Field(0, ge=0, le=59)
    person1_latitude: float = Field(..., ge=-90, le=90)
    person1_longitude: float = Field(..., ge=-180, le=180)
    person1_timezone: str = Field("UTC")
    person2_name: str = Field(..., min_length=1)
    person2_year: int = Field(..., ge=1900, le=2100)
    person2_month: int = Field(..., ge=1, le=12)
    person2_day: int = Field(..., ge=1, le=31)
    person2_hour: int = Field(0, ge=0, le=23)
    person2_minute: int = Field(0, ge=0, le=59)
    person2_latitude: float = Field(..., ge=-90, le=90)
    person2_longitude: float = Field(..., ge=-180, le=180)
    person2_timezone: str = Field("UTC")
    house_system: str = Field("placidus", pattern="^(placidus|koch|equal|whole_sign|regiomontanus|campanus|porphyry)$")
    node_type: str = Field("mean", pattern="^(mean|true)$")
    lang: str = Field("vi", pattern="^(vi|en)$")
    esoteric: bool = Field(True, description="Show esoteric astrology content")
    include_minor_aspects: bool = Field(True, description="Include minor aspects (quincunx, semisextile, etc.)")
    orb_conjunction: float = Field(8.0, ge=0.0, le=15.0)
    orb_opposition: float = Field(8.0, ge=0.0, le=15.0)
    orb_square: float = Field(8.0, ge=0.0, le=15.0)
    orb_trine: float = Field(8.0, ge=0.0, le=15.0)
    orb_sextile: float = Field(6.0, ge=0.0, le=15.0)
    orb_quincunx: float = Field(3.0, ge=0.0, le=10.0)
    orb_semisextile: float = Field(3.0, ge=0.0, le=10.0)
    orb_semisquare: float = Field(2.0, ge=0.0, le=10.0)
    orb_sesquiquadrate: float = Field(2.0, ge=0.0, le=10.0)
    orb_quintile: float = Field(2.0, ge=0.0, le=10.0)


def _build_subject(req: ChartRequest) -> AstrologicalSubject:
    try:
        datetime(req.year, req.month, req.day, req.hour, req.minute)
    except ValueError as e:
        logger.error(f"Invalid date/time for subject {req.name}: {e}")
        raise HTTPException(status_code=422, detail="Invalid date/time")
    return AstrologicalSubject(
        name=req.name,
        year=req.year,
        month=req.month,
        day=req.day,
        hour=req.hour,
        minute=req.minute,
        latitude=req.latitude,
        longitude=req.longitude,
        timezone_str=req.timezone_str,
    )


@app.get("/")
async def root():
    return {"service": "Astrololo", "version": "0.1.0", "status": "active"}


@app.get("/health")
async def health():
    from astrololo.core.ephemeris import HAS_SWISSEPH
    from astrololo.interpretation.ai_provider import AI_PROVIDER, AI_MODEL, AI_API_KEY
    return {
        "status": "healthy",
        "swiss_ephemeris": HAS_SWISSEPH,
        "ai_enabled": bool(AI_API_KEY),
        "ai_provider": AI_PROVIDER,
        "ai_model": AI_MODEL,
    }


@app.post("/api/v1/natal")
async def natal_chart(request: ChartRequest):
    logger.info(f"Generating {request.zodiac_type} natal chart for {request.name} ({request.year}-{request.month}-{request.day} {request.hour:02d}:{request.minute:02d} {request.latitude},{request.longitude})")
    subject = _build_subject(request)
    try:
        if request.zodiac_type == "sidereal":
            from astrololo.analysis.jyotish_natal import create_jyotish_chart
            chart = create_jyotish_chart(
                subject, house_system=request.house_system,
                node_type=request.node_type, lang=request.lang,
                ayanamsa_system=request.ayanamsa,
                include_minor_aspects=request.include_minor_aspects,
                orb_conjunction=request.orb_conjunction, orb_opposition=request.orb_opposition,
                orb_square=request.orb_square, orb_trine=request.orb_trine, orb_sextile=request.orb_sextile,
                orb_quincunx=request.orb_quincunx, orb_semisextile=request.orb_semisextile,
                orb_semisquare=request.orb_semisquare, orb_sesquiquadrate=request.orb_sesquiquadrate,
                orb_quintile=request.orb_quintile,
            )
        else:
            chart = create_natal_chart(subject, house_system=request.house_system, node_type=request.node_type, lang=request.lang, esoteric=request.esoteric,
                include_minor_aspects=request.include_minor_aspects,
                orb_conjunction=request.orb_conjunction, orb_opposition=request.orb_opposition,
                orb_square=request.orb_square, orb_trine=request.orb_trine, orb_sextile=request.orb_sextile,
                orb_quincunx=request.orb_quincunx, orb_semisextile=request.orb_semisextile,
                orb_semisquare=request.orb_semisquare, orb_sesquiquadrate=request.orb_sesquiquadrate,
                orb_quintile=request.orb_quintile,
            )
        logger.info(f"Natal chart generated successfully with {len(chart.planets)} planets, {len(chart.aspects)} aspects")
    except Exception as e:
        logger.exception(f"Error generating natal chart for {request.name}: {e}")
        raise HTTPException(status_code=500, detail="Chart calculation failed")
    return {"success": True, "data": chart.model_dump()}


@app.post("/api/v1/interpret")
async def interpret_chart(request: ChartRequest):
    logger.info(f"Generating interpretation for {request.name} ({request.year}-{request.month}-{request.day} {request.hour:02d}:{request.minute:02d})")
    subject = _build_subject(request)
    try:
        chart = create_natal_chart(subject, house_system=request.house_system, node_type=request.node_type, lang=request.lang, esoteric=request.esoteric,
            include_minor_aspects=request.include_minor_aspects,
            orb_conjunction=request.orb_conjunction, orb_opposition=request.orb_opposition,
            orb_square=request.orb_square, orb_trine=request.orb_trine, orb_sextile=request.orb_sextile,
            orb_quincunx=request.orb_quincunx, orb_semisextile=request.orb_semisextile,
            orb_semisquare=request.orb_semisquare, orb_sesquiquadrate=request.orb_sesquiquadrate,
            orb_quintile=request.orb_quintile,
        )
        logger.info(f"Chart generated for interpretation with {len(chart.planets)} planets")
    except Exception as e:
        logger.exception(f"Error generating chart for interpretation: {e}")
        raise HTTPException(status_code=500, detail="Chart calculation failed")

    interp = chart.interpretation or {}
    logger.info(f"Returning interpretation with {len(interp.get('sections', []))} sections")
    return {
        "success": True,
        "data": {
            "summary": interp.get("chart_summary"),
            "interpretation": interp.get("sections"),
            "overall": interp.get("overall_interpretation"),
        },
    }


@app.post("/api/v1/export/pdf")
async def export_pdf(request: ChartRequest):
    logger.info(f"Generating PDF export for {request.name}")
    subject = _build_subject(request)
    from astrololo.analysis.export_pdf import create_pdf_export
    from fastapi.responses import Response
    try:
        pdf_bytes = create_pdf_export(
            subject, lang=request.lang,
            house_system=request.house_system, node_type=request.node_type,
            esoteric=request.esoteric,
        )
        name_slug = request.name.replace(" ", "_").lower()
        filename = f"astrololo_{name_slug}.pdf"
        logger.info(f"PDF generated: {len(pdf_bytes)} bytes")
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except Exception as e:
        logger.exception(f"Error generating PDF: {e}")
        raise HTTPException(status_code=500, detail="PDF generation failed")


@app.post("/api/v1/transit")
async def transit_chart(request: TransitRequest):
    logger.info(f"Calculating transit from {request.year}-{request.month}-{request.day} for {request.name}")
    from astrololo.analysis.transit import create_transits
    subject = _build_subject(ChartRequest(
        name=request.name, year=request.year, month=request.month,
        day=request.day, hour=request.hour, minute=request.minute,
        latitude=request.latitude, longitude=request.longitude,
        timezone_str=request.timezone_str,
        house_system=request.house_system, node_type=request.node_type, lang=request.lang,
        esoteric=request.esoteric,
    ))
    try:
        result = create_transits(
            subject, request.transit_year, request.transit_month, request.transit_day,
            request.house_system, request.node_type, request.lang, request.esoteric,
            include_minor_aspects=request.include_minor_aspects,
            orb_conjunction=request.orb_conjunction, orb_opposition=request.orb_opposition,
            orb_square=request.orb_square, orb_trine=request.orb_trine, orb_sextile=request.orb_sextile,
            orb_quincunx=request.orb_quincunx, orb_semisextile=request.orb_semisextile,
            orb_semisquare=request.orb_semisquare, orb_sesquiquadrate=request.orb_sesquiquadrate,
            orb_quintile=request.orb_quintile,
        )
        logger.info(f"Transit calculated with {len(result.get('aspects', []))} aspects")
        return {"success": True, "data": result}
    except Exception as e:
        logger.exception(f"Error calculating transit: {e}")
        raise HTTPException(status_code=500, detail="Transit calculation failed")


@app.post("/api/v1/progression")
async def progression_chart(request: ProgressionRequest):
    logger.info(f"Calculating secondary progression at age {request.age} for {request.name}")
    from astrololo.analysis.progression import create_progressions
    subject = _build_subject(ChartRequest(
        name=request.name, year=request.year, month=request.month,
        day=request.day, hour=request.hour, minute=request.minute,
        latitude=request.latitude, longitude=request.longitude,
        timezone_str=request.timezone_str,
        house_system=request.house_system, node_type=request.node_type, lang=request.lang,
        esoteric=request.esoteric,
    ))
    try:
        result = create_progressions(
            subject, request.age,
            request.house_system, request.node_type, request.lang, request.esoteric,
            include_minor_aspects=request.include_minor_aspects,
            orb_conjunction=request.orb_conjunction, orb_opposition=request.orb_opposition,
            orb_square=request.orb_square, orb_trine=request.orb_trine, orb_sextile=request.orb_sextile,
            orb_quincunx=request.orb_quincunx, orb_semisextile=request.orb_semisextile,
            orb_semisquare=request.orb_semisquare, orb_sesquiquadrate=request.orb_sesquiquadrate,
            orb_quintile=request.orb_quintile,
        )
        logger.info(f"Progression calculated with {len(result.get('progressed_aspects', []))} aspects")
        return {"success": True, "data": result}
    except Exception as e:
        logger.exception(f"Error calculating progression: {e}")
        raise HTTPException(status_code=500, detail="Progression calculation failed")


@app.post("/api/v1/solar-return")
async def solar_return_chart(request: SolarReturnRequest):
    logger.info(f"Calculating solar return for {request.target_year} for {request.name}")
    from astrololo.analysis.solar_return import create_solar_return
    subject = _build_subject(ChartRequest(
        name=request.name, year=request.year, month=request.month,
        day=request.day, hour=request.hour, minute=request.minute,
        latitude=request.latitude, longitude=request.longitude,
        timezone_str=request.timezone_str,
        house_system=request.house_system, node_type=request.node_type, lang=request.lang,
        esoteric=request.esoteric,
    ))
    try:
        result = create_solar_return(
            subject, request.target_year,
            request.house_system, request.node_type, request.lang, request.esoteric,
            include_minor_aspects=request.include_minor_aspects,
            orb_conjunction=request.orb_conjunction, orb_opposition=request.orb_opposition,
            orb_square=request.orb_square, orb_trine=request.orb_trine, orb_sextile=request.orb_sextile,
            orb_quincunx=request.orb_quincunx, orb_semisextile=request.orb_semisextile,
            orb_semisquare=request.orb_semisquare, orb_sesquiquadrate=request.orb_sesquiquadrate,
            orb_quintile=request.orb_quintile,
        )
        logger.info(f"Solar return calculated for {request.target_year}")
        return {"success": True, "data": result}
    except Exception as e:
        logger.exception(f"Error calculating solar return: {e}")
        raise HTTPException(status_code=500, detail="Solar return calculation failed")


@app.post("/api/v1/daily")
async def daily_chart(request: ChartRequest):
    logger.info(f"Calculating daily horoscope for {request.name}")
    from astrololo.analysis.transit import create_daily
    subject = _build_subject(request)
    try:
        result = create_daily(
            subject, request.house_system, request.node_type, request.lang, request.esoteric,
            include_minor_aspects=request.include_minor_aspects,
            orb_conjunction=request.orb_conjunction, orb_opposition=request.orb_opposition,
            orb_square=request.orb_square, orb_trine=request.orb_trine, orb_sextile=request.orb_sextile,
            orb_quincunx=request.orb_quincunx, orb_semisextile=request.orb_semisextile,
            orb_semisquare=request.orb_semisextile, orb_sesquiquadrate=request.orb_sesquiquadrate,
            orb_quintile=request.orb_quintile,
        )
        logger.info(f"Daily horoscope calculated with {len(result.get('daily', {}).get('aspect_picks', []))} picks")
        return {"success": True, "data": result}
    except Exception as e:
        logger.exception(f"Error calculating daily horoscope: {e}")
        raise HTTPException(status_code=500, detail="Daily horoscope calculation failed")


@app.post("/api/v1/synastry")
async def synastry_chart(request: SynastryRequest):
    logger.info(f"Calculating synastry between {request.person1_name} and {request.person2_name}")
    from astrololo.analysis.synastry import create_synastry
    p1 = _build_subject(ChartRequest(
        name=request.person1_name, year=request.person1_year,
        month=request.person1_month, day=request.person1_day,
        hour=request.person1_hour, minute=request.person1_minute,
        latitude=request.person1_latitude, longitude=request.person1_longitude,
        timezone_str=request.person1_timezone,
        house_system=request.house_system, node_type=request.node_type, lang=request.lang,
        esoteric=request.esoteric,
    ))
    p2 = _build_subject(ChartRequest(
        name=request.person2_name, year=request.person2_year,
        month=request.person2_month, day=request.person2_day,
        hour=request.person2_hour, minute=request.person2_minute,
        latitude=request.person2_latitude, longitude=request.person2_longitude,
        timezone_str=request.person2_timezone,
        house_system=request.house_system, node_type=request.node_type, lang=request.lang,
        esoteric=request.esoteric,
    ))
    try:
        result = create_synastry(p1, p2, request.house_system, request.node_type, request.lang, request.esoteric,
            include_minor_aspects=request.include_minor_aspects,
            orb_conjunction=request.orb_conjunction, orb_opposition=request.orb_opposition,
            orb_square=request.orb_square, orb_trine=request.orb_trine, orb_sextile=request.orb_sextile,
            orb_quincunx=request.orb_quincunx, orb_semisextile=request.orb_semisextile,
            orb_semisquare=request.orb_semisquare, orb_sesquiquadrate=request.orb_sesquiquadrate,
            orb_quintile=request.orb_quintile,
        )
        logger.info(f"Synastry calculated with {len(result.get('cross_aspects', []))} cross aspects")
        return {"success": True, "data": result}
    except Exception as e:
        logger.exception(f"Error calculating synastry: {e}")
        raise HTTPException(status_code=500, detail="Synastry calculation failed")


@app.post("/api/v1/interpret/ai")
async def interpret_ai(request: ChartRequest):
    logger.info(f"Generating AI interpretation for {request.name}")
    subject = _build_subject(request)
    try:
        chart = create_natal_chart(subject, house_system=request.house_system, node_type=request.node_type, lang=request.lang, esoteric=request.esoteric,
            include_minor_aspects=request.include_minor_aspects,
            orb_conjunction=request.orb_conjunction, orb_opposition=request.orb_opposition,
            orb_square=request.orb_square, orb_trine=request.orb_trine, orb_sextile=request.orb_sextile,
            orb_quincunx=request.orb_quincunx, orb_semisextile=request.orb_semisextile,
            orb_semisquare=request.orb_semisquare, orb_sesquiquadrate=request.orb_sesquiquadrate,
            orb_quintile=request.orb_quintile,
        )
        logger.info("Chart generated for AI interpretation")
    except Exception as e:
        logger.exception(f"Error generating chart for AI interpretation: {e}")
        raise HTTPException(status_code=500, detail="Chart calculation failed")

    from astrololo.interpretation.ai_engine import ai_interpret
    ai_result = ai_interpret(chart, lang=request.lang)
    logger.info(f"AI interpretation completed with success={ai_result.get('success', False)}")

    # Per-planet AI synthesis
    from astrololo.interpretation.ai_synthesis import synthesize_all_planets
    try:
        syntheses = synthesize_all_planets(chart, lang=request.lang)
        logger.info(f"AI per-planet synthesis generated for {len(syntheses)} planets")
    except Exception as e:
        logger.warning(f"Per-planet synthesis failed: {e}")
        syntheses = []

    return {
        "success": True,
        "data": {
            "summary": {
                "name": subject.name,
                "ascendant": chart.ascendant_sign,
            },
            "template": chart.interpretation.get("overall_interpretation") if chart.interpretation else "",
            "ai": ai_result,
            "syntheses": syntheses,
        },
    }


@app.get("/api/v1/constants")
async def get_constants():
    from astrololo.core.constants import PLANETS, SIGNS, ASPECTS, HOUSES, ELEMENT_SIGNS, QUALITY_SIGNS
    return {
        "success": True,
        "data": {
            "planets": {k: {"name_vi": v.name_vi, "name_en": v.name_en, "symbol": v.symbol} for k, v in PLANETS.items()},
            "signs": {k: {"name_vi": v.name_vi, "name_en": v.name_en, "symbol": v.symbol, "element": v.element, "quality": v.quality} for k, v in SIGNS.items()},
            "aspects": {k: {"name_vi": v.name_vi, "name_en": v.name_en, "angle": v.angle, "nature": v.nature} for k, v in ASPECTS.items()},
            "houses": {str(k): {"name_vi": v.name_vi, "name_en": v.name_en, "type": v.type_} for k, v in HOUSES.items()},
            "elements": list(ELEMENT_SIGNS.keys()),
            "qualities": list(QUALITY_SIGNS.keys()),
        },
    }


@app.get("/api/v1/keywords")
async def get_keywords(
    type: Optional[str] = None,
    q: Optional[str] = None,
    planet: Optional[str] = None,
    sign: Optional[str] = None,
    house: Optional[int] = None,
):
    """Expose all enrichment keyword data to frontend.

    Params:
        type: filter by "sign", "house", or "planet"
        q: search term to filter keywords
        planet: specific planet name
        sign: specific sign name
        house: specific house number (1-12)
    """
    from astrololo.interpretation.keywords import (
        SIGN_KEYWORDS_VI, HOUSE_KEYWORDS_VI, SIGN_NAME_VI,
        HOUSE_NAME_VI, SIGN_ELEMENT_VI, SIGN_QUALITY_VI,
    )

    signs = {}
    if type is None or type == "sign":
        for sname, sdata in SIGN_KEYWORDS_VI.items():
            if sign and sname != sign:
                continue
            signs[sname] = {
                "name_vi": SIGN_NAME_VI.get(sname, sname),
                "element": SIGN_ELEMENT_VI.get(sname, ""),
                "quality": SIGN_QUALITY_VI.get(sname, ""),
                "positive": sdata.get("positive", []),
                "negative": sdata.get("negative", []),
                "core": sdata.get("core", []),
                "short_description": sdata.get("short_description", ""),
                "potential_issues": sdata.get("potential_issues", ""),
            }

    houses = {}
    if type is None or type == "house":
        for hnum, hdata in HOUSE_KEYWORDS_VI.items():
            if house is not None and hnum != house:
                continue
            houses[str(hnum)] = {
                "title": hdata.get("title", f"Nhà {hnum}"),
                "name_vi": HOUSE_NAME_VI.get(hnum, f"Nhà {hnum}"),
                "keywords": hdata.get("keywords", []),
                "description": hdata.get("description", ""),
            }

    planets = {}
    if type is None or type == "planet":
        from astrololo.interpretation.template_loader import PLANET_REPRESENTS_VI
        from astrololo.interpretation.keywords import PLANET_FUNCTIONS_VI
        for pname, func in PLANET_FUNCTIONS_VI.items():
            if planet and pname != planet:
                continue
            planets[pname] = {
                "function": func,
                "represents": PLANET_REPRESENTS_VI.get(pname, ""),
            }

    result = {"signs": signs, "houses": houses, "planets": planets}

    if q:
        def _norm(s: str) -> str:
            """Strip diacritics for accent-insensitive search."""
            replacements = {
                'à': 'a', 'á': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
                'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
                'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
                'è': 'e', 'é': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
                'ê': 'e', 'ề': 'e', 'ế': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
                'ì': 'i', 'í': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
                'ò': 'o', 'ó': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
                'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
                'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
                'ù': 'u', 'ú': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
                'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
                'ỳ': 'y', 'ý': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
                'đ': 'd',
            }
            result = []
            for c in s.lower():
                result.append(replacements.get(c, c))
            return ''.join(result)

        qn = _norm(q)
        filtered = {"signs": {}, "houses": {}, "planets": {}}
        for sname, sdata in signs.items():
            combined = " ".join(sdata.get("positive", []) + sdata.get("negative", []) + sdata.get("core", []))
            if qn in _norm(combined) or qn in _norm(sdata.get("name_vi", "")):
                filtered["signs"][sname] = sdata
        for hnum, hdata in houses.items():
            combined = " ".join(hdata.get("keywords", []))
            if qn in _norm(combined) or qn in _norm(hdata.get("title", "")):
                filtered["houses"][hnum] = hdata
        for pname, pdata in planets.items():
            combined = pdata.get("function", "") + " " + pdata.get("represents", "")
            if qn in _norm(combined):
                filtered["planets"][pname] = pdata
        result = filtered

    return {"success": True, "data": result}


@app.get("/api/v1/jyotish/constants")
async def get_jyotish_constants():
    """Return Jyotish-specific constants: Navagraha, Nakshatras, Dasha periods."""
    from astrololo.core.jyotish_constants import (
        NAVAGRAHA, NAKSHATRAS, DASHA_YEARS, DASHA_SEQUENCE,
        JYOTISH_SIGN_RULERS, RASHI_NAMES, TATTWA_NAMES_VI, GUNA_NAMES_VI,
        DIGNITY_NAMES_VI,
    )
    return {
        "success": True,
        "data": {
            "navagraha": {
                k: {
                    "name_sa": v.name_sa, "name_vi": v.name_vi, "name_en": v.name_en,
                    "symbol": v.symbol, "tattwa": v.tattwa, "guna": v.guna,
                    "nature": v.nature, "own_signs": v.own_signs,
                    "exaltation": v.exaltation_sign, "debilitation": v.debilitation_sign,
                    "vara_day": v.vara_day,
                }
                for k, v in NAVAGRAHA.items()
            },
            "nakshatras": [
                {
                    "number": n.number, "name_sa": n.name_sa, "name_vi": n.name_vi,
                    "ruler": n.ruler, "deity": n.deity, "gana": n.gana,
                }
                for n in NAKSHATRAS
            ],
            "dasha_years": DASHA_YEARS,
            "dasha_sequence": DASHA_SEQUENCE,
            "sign_rulers": JYOTISH_SIGN_RULERS,
            "rashi_names": {k: {"sa": v[0], "vi": v[1]} for k, v in RASHI_NAMES.items()},
            "tattwa_names": TATTWA_NAMES_VI,
            "guna_names": GUNA_NAMES_VI,
            "dignity_names": DIGNITY_NAMES_VI,
        },
    }


@app.post("/api/v1/jyotish/dasha")
async def get_dasha(request: ChartRequest):
    """Calculate Vimshottari Dasha for a birth chart."""
    logger.info(f"Calculating Vimshottari Dasha for {request.name}")
    subject = _build_subject(request)
    try:
        from astrololo.analysis.jyotish_natal import create_jyotish_chart
        chart = create_jyotish_chart(
            subject, house_system=request.house_system,
            node_type=request.node_type, lang=request.lang,
            ayanamsa_system=request.ayanamsa,
            include_minor_aspects=request.include_minor_aspects,
            orb_conjunction=request.orb_conjunction, orb_opposition=request.orb_opposition,
            orb_square=request.orb_square, orb_trine=request.orb_trine, orb_sextile=request.orb_sextile,
            orb_quincunx=request.orb_quincunx, orb_semisextile=request.orb_semisextile,
            orb_semisquare=request.orb_semisquare, orb_sesquiquadrate=request.orb_sesquiquadrate,
            orb_quintile=request.orb_quintile,
        )
    except Exception as e:
        logger.exception(f"Error calculating Dasha: {e}")
        raise HTTPException(status_code=500, detail="Dasha calculation failed")

    if not chart.dasha:
        raise HTTPException(status_code=500, detail="Dasha data unavailable")

    return {"success": True, "data": chart.dasha.model_dump()}


@app.post("/api/v1/jyotish/remedies")
async def get_remedies(request: ChartRequest):
    """Get Navagraha remedies based on chart weaknesses."""
    logger.info(f"Getting remedies for {request.name}")
    subject = _build_subject(request)
    try:
        from astrololo.analysis.jyotish_natal import create_jyotish_chart
        from astrololo.interpretation.jyotish_loader import get_remedy
        chart = create_jyotish_chart(
            subject, house_system=request.house_system,
            node_type=request.node_type, lang=request.lang,
            ayanamsa_system=request.ayanamsa,
            include_minor_aspects=request.include_minor_aspects,
            orb_conjunction=request.orb_conjunction, orb_opposition=request.orb_opposition,
            orb_square=request.orb_square, orb_trine=request.orb_trine, orb_sextile=request.orb_sextile,
            orb_quincunx=request.orb_quincunx, orb_semisextile=request.orb_semisextile,
            orb_semisquare=request.orb_semisquare, orb_sesquiquadrate=request.orb_sesquiquadrate,
            orb_quintile=request.orb_quintile,
        )
    except Exception as e:
        logger.exception(f"Error calculating chart for remedies: {e}")
        raise HTTPException(status_code=500, detail="Chart calculation failed")

    from astrololo.core.jyotish_constants import WESTERN_TO_GRAHA
    remedies = []
    for bp in chart.planets:
        if bp.jyotish_dignity in ("neecha",):
            graha_key = WESTERN_TO_GRAHA.get(bp.name, "")
            remedy = get_remedy(graha_key, request.lang)
            if remedy:
                remedies.append({
                    "graha": graha_key,
                    "graha_name_vi": bp.graha_name_vi or bp.name_vi,
                    "dignity": bp.jyotish_dignity,
                    "sign": bp.sidereal_sign,
                    "remedy": remedy,
                })

    return {"success": True, "data": remedies}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("astrololo.api.main:app", host="0.0.0.0", port=8000, reload=True)
