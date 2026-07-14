"""Template loader for Jyotish interpretations — nakshatra, dasha, dignity, remedies."""
import os
import yaml
from typing import Dict, Any, Optional

_CACHE: Dict[str, Any] = {}
_BASE_DIR = os.path.join(os.path.dirname(__file__), "templates")


def _load_jyotish_yaml(lang: str, filename: str) -> Dict[str, Any]:
    key = f"jyotish_{lang}_{filename}"
    if key in _CACHE:
        return _CACHE[key]

    path = os.path.join(_BASE_DIR, lang, "jyotish", filename)
    if not os.path.exists(path):
        path = os.path.join(_BASE_DIR, "vi", "jyotish", filename)
    if not os.path.exists(path):
        _CACHE[key] = {}
        return {}

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    _CACHE[key] = data
    return data


def get_nakshatra_interpretation(nakshatra: str, lang: str = "vi") -> Optional[Dict[str, Any]]:
    data = _load_jyotish_yaml(lang, "nakshatra.yaml")
    return data.get(nakshatra) or data.get(nakshatra.replace(" ", "_"))


def get_dasha_interpretation(graha_key: str, lang: str = "vi") -> Optional[Dict[str, Any]]:
    data = _load_jyotish_yaml(lang, "dasha.yaml")
    return data.get(graha_key)


def get_jyotish_dignity_text(dignity: str, lang: str = "vi") -> Optional[Dict[str, Any]]:
    data = _load_jyotish_yaml(lang, "dignity.yaml")
    return data.get(dignity)


def get_remedy(graha_key: str, lang: str = "vi") -> Optional[Dict[str, Any]]:
    data = _load_jyotish_yaml(lang, "remedies.yaml")
    return data.get(graha_key)
