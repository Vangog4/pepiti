"""
Rule-based contextual shop recommendations.
No AI — simple mapping from pet profile + context to a single shop button.
Principle: one recommendation per scenario, never blocking the main UX.
"""

from aiogram.types import InlineKeyboardButton

from app.core.shop import SHOP_URL_BY_SIZE, SHOP_URL_LONGPLAY, SHOP_URL_TRAINING
from app.infrastructure.db.models.pet import PetModel

# Contexts
AFTER_EXERCISE = "after_exercise"  # explain_exercise finished
AFTER_COMPLETION = "after_completion"  # all tasks in a day/plan done


def get_shop_button(
    pet: PetModel,
    is_premium: bool,
    context: str,
) -> InlineKeyboardButton:
    """Return a single URL InlineKeyboardButton with a context-aware label."""
    age = (pet.age_category or "").lower()
    size = (pet.size_category or "").lower()

    is_puppy = "щенок" in age
    is_small = "маленький" in size

    if is_puppy or is_small:
        url = SHOP_URL_BY_SIZE
        if is_premium:
            who = "щенков" if is_puppy else "маленьких пород"
            label = f"🐶 Лакомства для {who} — для {pet.name}"
        else:
            label = "🐶 Лакомства для щенков и малышей"

    elif context == AFTER_COMPLETION:
        url = SHOP_URL_LONGPLAY
        label = (
            f"🎁 Долгоиграющие лакомства — награда для {pet.name}"
            if is_premium
            else "🦴 Долгоиграющие лакомства"
        )

    else:
        url = SHOP_URL_TRAINING
        if is_premium:
            label = (
                f"🦴 Лакомства для упражнений {pet.name}"
                if context == AFTER_EXERCISE
                else f"🦴 Лакомства для тренировок {pet.name}"
            )
        else:
            label = "🦴 Лакомства для дрессировки"

    return InlineKeyboardButton(text=label, url=url)
