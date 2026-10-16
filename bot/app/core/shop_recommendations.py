"""
Rule-based contextual shop recommendations.
No AI — mapping from pet profile + context to a single shop button.
Token lists live in app/logic/rules.json (shop.*).
Principle: one recommendation per scenario, never blocking the main UX.
"""

from aiogram.types import InlineKeyboardButton

from app.core.shop import SHOP_URL_BY_SIZE, SHOP_URL_LONGPLAY, SHOP_URL_TRAINING
from app.i18n import t
from app.infrastructure.db.models.pet import PetModel
from app.logic.rules import rule

# Contexts
AFTER_EXERCISE = "after_exercise"  # explain_exercise finished
AFTER_COMPLETION = "after_completion"  # all tasks in a day/plan done


def _token_hit(text: str, tokens: list[str]) -> bool:
    return any(tok in text for tok in tokens)


def get_shop_button(
    pet: PetModel,
    is_premium: bool,
    context: str,
    lang: str = "ru",
) -> InlineKeyboardButton:
    """Return a single URL InlineKeyboardButton with a context-aware label."""
    age = (pet.age_category or "").lower()
    size = (pet.size_category or "").lower()

    puppy_tokens = [str(tok).lower() for tok in (rule("shop.puppy_age_tokens") or ["щенок"])]
    small_tokens = [str(tok).lower() for tok in (rule("shop.small_size_tokens") or ["маленький"])]

    is_puppy = _token_hit(age, puppy_tokens)
    is_small = _token_hit(size, small_tokens)

    if is_puppy or is_small:
        url = SHOP_URL_BY_SIZE
        if is_premium:
            key = "shop.rec.puppy_named" if is_puppy else "shop.rec.small_named"
            label = t(key, lang, name=pet.name)
        else:
            label = t("shop.rec.puppy_small_free", lang)

    elif context == AFTER_COMPLETION:
        url = SHOP_URL_LONGPLAY
        label = (
            t("shop.rec.longplay_named", lang, name=pet.name)
            if is_premium
            else t("shop.rec.longplay_free", lang)
        )

    else:
        url = SHOP_URL_TRAINING
        if is_premium:
            key = (
                "shop.rec.exercise_named"
                if context == AFTER_EXERCISE
                else "shop.rec.training_named"
            )
            label = t(key, lang, name=pet.name)
        else:
            label = t("shop.rec.training_free", lang)

    return InlineKeyboardButton(text=label, url=url)
