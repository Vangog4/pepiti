"""Build card payloads from bot data. Text comes from i18n; the renderer stays language-free."""

from __future__ import annotations

from typing import Any

from app.cards.render import ellipsize
from app.i18n import t

NAME_IN_HEADLINE = 16


def short_name(name: str, limit: int = NAME_IN_HEADLINE) -> str:
    """Long dog names must not push the message out of a headline."""
    return ellipsize(" ".join((name or "").split()), limit)


BADGE_PRIORITY = ("streak_100", "streak_30", "streak_7", "walks_10")
_BADGE_BIG = {"streak_100": "100", "streak_30": "30", "streak_7": "7", "walks_10": "10"}


def streak_card(pet_name: str, streak: int, lang: str) -> dict[str, Any]:
    return {
        "big": str(streak),
        "caption": t("card.unit.streak", lang),
        "headline": t("card.headline.streak", lang, pet=short_name(pet_name)),
    }


def top_badge(badges: set[str]) -> str | None:
    return next((b for b in BADGE_PRIORITY if b in badges), None)


def badge_card(code: str, pet_name: str, lang: str) -> dict[str, Any]:
    return {
        "big": _BADGE_BIG.get(code, "★"),
        "caption": t("card.badge.caption", lang),
        "headline": t(f"tracker.badge.{code}", lang) + " · " + short_name(pet_name),
    }


def week_card(pet_name: str, week: Any, streak: int, lang: str) -> dict[str, Any]:
    return {
        "big": str(week.task_days),
        "caption": t("card.week.caption", lang),
        "headline": pet_name,
        "rows": [
            (t("card.row.walks", lang), str(week.walk_count)),
            (t("card.row.minutes", lang), str(week.walk_minutes)),
            (t("card.row.streak", lang), str(streak)),
        ],
    }


def passport_card(pet: Any, age_text: str, lang: str) -> dict[str, Any]:
    rows = [(t("card.row.age", lang), age_text)] if age_text else []
    if getattr(pet, "weight_kg", None):
        rows.append((t("card.row.weight", lang), f"{pet.weight_kg} {t('card.unit.kg', lang)}"))
    if getattr(pet, "allergies", None):
        rows.append((t("card.row.allergies", lang), ", ".join(pet.allergies)))
    return {
        "big": pet.name,
        "caption": t("card.passport.caption", lang),
        "headline": pet.breed or "",
        "rows": rows,
    }
