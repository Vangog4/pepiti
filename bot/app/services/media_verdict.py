"""Render a MediaVerdict into Telegram HTML. Model text is escaped, never trusted as markup."""

from __future__ import annotations

from html import escape

from app.i18n import t
from app.logic.schemas import MediaVerdict


def render_verdict(v: MediaVerdict, lang: str) -> str:
    parts: list[str] = []
    if v.urgency == "vet_now":
        parts.append(t("media.verdict.vet_now", lang))
    elif v.urgency == "vet_soon":
        parts.append(t("media.verdict.vet_soon", lang))
    parts.append(t("media.verdict.see", lang) + " " + escape(v.summary))
    if v.steps:
        steps = "\n".join(f"{i}. {escape(s)}" for i, s in enumerate(v.steps, 1))
        parts.append(t("media.verdict.steps", lang) + "\n" + steps)
    parts.append(t("media.verdict.disclaimer", lang))
    return "\n\n".join(parts)
