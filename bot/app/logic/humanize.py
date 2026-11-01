"""Keep bot copy human: no bureaucratic Russian, no AI-assistant filler.

Word lists live in ``rules.json`` -> ``copy`` so they can be tuned without code changes.
"""

from __future__ import annotations

import re

from app.logic.rules import rule

_TAGS = r"(?:<[^>]+>\s*)*"


def banned_ru() -> list[str]:
    return [w.lower() for w in (rule("copy.banned_ru", []) or [])]


def find_banned(text: str) -> list[str]:
    """Bureaucratic stems present in ``text`` (case-insensitive)."""
    low = text.lower()
    return [w for w in banned_ru() if w in low]


def _cliche_re() -> re.Pattern | None:
    words = [re.escape(c) for c in (rule("copy.ai_cliches", []) or [])]
    if not words:
        return None
    return re.compile("(?:" + "|".join(words) + ")", re.IGNORECASE)


def strip_cliches(text: str) -> str:
    """Drop a short opening/closing sentence that is pure AI filler ("Отличный вопрос!")."""
    cliche = _cliche_re()
    if cliche is None or not text:
        return text
    out = text.strip()
    opening = re.compile(rf"^({_TAGS})([^.!?\n]{{0,100}}[.!?]+)(?:\s*</[^>]+>)*\s*")
    m = opening.match(out)
    if m and cliche.search(m.group(2)):
        out = out[m.end() :]
    closing = re.compile(r"(?:^|(?<=[.!?\n]))\s*([^.!?\n]{0,100}[.!?]+)\s*$")
    m = closing.search(out)
    if m and cliche.search(m.group(1)) and m.start() > 0:
        out = out[: m.start()].rstrip()
    return out.strip()
