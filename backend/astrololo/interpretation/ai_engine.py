"""AI-powered interpretation engine. Falls back gracefully when AI is unavailable."""

from typing import Optional, Dict, Any
from astrololo.interpretation.ai_provider import ai_complete
from astrololo.interpretation.ai_prompts import (
    SYSTEM_PROMPT_VI, SYSTEM_PROMPT_EN,
    build_chart_context, CHART_ANALYSIS_PROMPT_VI, CHART_ANALYSIS_PROMPT_EN,
)


def ai_interpret(chart: Any, lang: str = "vi") -> Optional[Dict[str, Any]]:
    try:
        interp = chart.interpretation
        if not interp:
            return None
        if isinstance(interp, dict):
            chart_data = interp
        elif hasattr(interp, "model_dump"):
            chart_data = interp.model_dump()
        else:
            chart_data = interp

        context = build_chart_context(chart_data)
        system_prompt = SYSTEM_PROMPT_VI if lang == "vi" else SYSTEM_PROMPT_EN
        user_prompt = (CHART_ANALYSIS_PROMPT_VI if lang == "vi" else CHART_ANALYSIS_PROMPT_EN).format(chart_context=context)

        result = ai_complete(
            messages=[{"role": "user", "content": user_prompt}],
            system_prompt=system_prompt,
        )

        if result.success and result.text:
            return {
                "text": result.text,
                "model": result.model,
                "tokens_used": result.tokens_used,
                "success": True,
            }
        return {"text": "", "model": "", "success": False, "error": result.error}
    except Exception as e:
        return {"text": "", "model": "", "success": False, "error": str(e)}
