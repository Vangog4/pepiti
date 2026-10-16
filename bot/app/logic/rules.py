"""Load and query declarative business rules (JSON).

Single source of truth for limits, pricing, referral milestones, model routing.
Call ``reload_rules()`` in tests after patching the JSON file.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_RULES_PATH = Path(__file__).with_name("rules.json")
_cache: dict[str, Any] | None = None


def load_rules(path: Path | None = None) -> dict[str, Any]:
    p = path or _RULES_PATH
    with p.open(encoding="utf-8") as f:
        return json.load(f)


def get_rules() -> dict[str, Any]:
    global _cache
    if _cache is None:
        _cache = load_rules()
    return _cache


def reload_rules(path: Path | None = None) -> dict[str, Any]:
    """Force re-read from disk (tests / hot-reload)."""
    global _cache
    _cache = load_rules(path)
    return _cache


def rule(path: str, default: Any = None) -> Any:
    """Dotted path lookup, e.g. ``rule("ai.free_daily_limit")``."""
    node: Any = get_rules()
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            return default
        node = node[part]
    return node


def contains_forbidden(text: str) -> str | None:
    """Return first matched forbidden phrase (lowercased) or None."""
    lowered = (text or "").lower()
    for phrase in rule("ai.forbidden_phrases", []) or []:
        if phrase.lower() in lowered:
            return phrase
    return None
