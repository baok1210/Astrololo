"""
AI provider abstraction layer for Astrololo.
Supports OpenAI-compatible APIs (OpenAI, Claude, local LLMs).
"""

import os
import logging
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logger = logging.getLogger(__name__)

AI_ENABLED = False
AI_PROVIDER = os.environ.get("ASTRO_AI_PROVIDER", "openai").lower()
AI_API_KEY = os.environ.get("ASTRO_AI_API_KEY", "")
AI_MODEL = os.environ.get("ASTRO_AI_MODEL", "gpt-4o-mini")
AI_ENDPOINT = os.environ.get("ASTRO_AI_ENDPOINT", "")
AI_MAX_TOKENS = int(os.environ.get("ASTRO_AI_MAX_TOKENS", "1024"))
AI_TEMPERATURE = float(os.environ.get("ASTRO_AI_TEMPERATURE", "0.7"))


@dataclass
class AIResponse:
    text: str
    model: str
    tokens_used: int = 0
    success: bool = True
    error: str = ""


def _call_openai(messages: list, system_prompt: str) -> AIResponse:
    import httpx
    import json
    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": AI_MODEL,
        "messages": [{"role": "system", "content": system_prompt}] + messages,
        "max_tokens": AI_MAX_TOKENS,
        "temperature": AI_TEMPERATURE,
    }
    url = AI_ENDPOINT or "https://api.openai.com/v1/chat/completions"
    try:
        resp = httpx.post(url, headers=headers, json=body, timeout=60)
        resp.raise_for_status()
        raw = resp.text
        # Handle SSE-wrapped responses (data: {...}\n\ndata: [DONE])
        if raw.startswith("data: "):
            text_parts = []
            tokens = 0
            for line in raw.split("\n"):
                line = line.strip()
                if line.startswith("data: ") and line != "data: [DONE]":
                    data = json.loads(line[6:])
                    choices = data.get("choices", [])
                    if choices:
                        msg = choices[0].get("message", {}) or choices[0].get("delta", {})
                        if msg.get("content"):
                            text_parts.append(msg["content"])
                    usage = data.get("usage", {})
                    if usage:
                        tokens = usage.get("total_tokens", 0)
            text = "".join(text_parts)
            logger.info(f"OpenAI API call successful (SSE), model={AI_MODEL}, tokens={tokens}")
            return AIResponse(text=text, model=AI_MODEL, tokens_used=tokens)
        # Standard JSON response
        data = resp.json()
        text = data["choices"][0]["message"]["content"]
        tokens = data.get("usage", {}).get("total_tokens", 0)
        logger.info(f"OpenAI API call successful, model={AI_MODEL}, tokens={tokens}")
        return AIResponse(text=text, model=AI_MODEL, tokens_used=tokens)
    except Exception as e:
        logger.error(f"OpenAI API call failed: {e}")
        return AIResponse(text="", model=AI_MODEL, success=False, error=str(e))


def _call_ollama(messages: list, system_prompt: str) -> AIResponse:
    import httpx
    url = AI_ENDPOINT or "http://localhost:11434/api/chat"
    body = {
        "model": AI_MODEL,
        "messages": [{"role": "system", "content": system_prompt}] + messages,
        "stream": False,
    }
    try:
        resp = httpx.post(url, json=body, timeout=120)
        resp.raise_for_status()
        data = resp.json()
        text = data.get("message", {}).get("content", "")
        logger.info(f"Ollama API call successful, model={AI_MODEL}")
        return AIResponse(text=text, model=AI_MODEL, success=bool(text))
    except Exception as e:
        logger.error(f"Ollama API call failed: {e}")
        return AIResponse(text="", model=AI_MODEL, success=False, error=str(e))


def ai_complete(messages: list, system_prompt: str = "") -> AIResponse:
    if not AI_API_KEY and AI_PROVIDER != "ollama":
        return AIResponse(text="", model="", success=False,
                          error="ASTRO_AI_API_KEY not set. Set env var or use provider='ollama'.")
    if AI_PROVIDER == "ollama":
        return _call_ollama(messages, system_prompt)
    return _call_openai(messages, system_prompt)
