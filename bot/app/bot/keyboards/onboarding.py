"""4-tap onboarding keyboards: age -> breed -> goal. Stored values stay Russian (data model)."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.i18n import t

AGES = {
    "1": "Щенок (до 4 мес)",
    "2": "Щенок (4–12 мес)",
    "3": "Молодой (1–3 года)",
    "4": "Взрослый (3–7 лет)",
    "5": "Пожилой (7+ лет)",
}
# (button label ≤14 chars, stored breed name)
BREEDS = [
    ("Лабрадор", "Лабрадор"),
    ("Нем. овчарка", "Немецкая овчарка"),
    ("Хаски", "Хаски"),
    ("Йорк", "Йоркширский терьер"),
    ("Джек-рассел", "Джек-рассел-терьер"),
    ("Фр. бульдог", "Французский бульдог"),
    ("Такса", "Такса"),
    ("Корги", "Корги"),
]
GOALS = {
    "1": "Послушание и базовые команды",
    "2": "Исправить поведение",
    "3": "Воспитание щенка",
    "4": "Активность и спорт",
}


def age_kb(lang: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=t(f"onboarding.age.{k}", lang), callback_data=f"ob_age:{k}")]
        for k in AGES
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def breed_kb(lang: str) -> InlineKeyboardMarkup:
    rows = []
    for i in range(0, len(BREEDS), 2):
        rows.append(
            [
                InlineKeyboardButton(text=BREEDS[j][0], callback_data=f"ob_breed:{j}")
                for j in (i, i + 1)
            ]
        )
    rows.append(
        [
            InlineKeyboardButton(
                text=t("onboarding.btn.other", lang), callback_data="ob_breed:other"
            ),
            InlineKeyboardButton(
                text=t("onboarding.btn.photo", lang), callback_data="ob_breed:photo"
            ),
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def goal_kb(lang: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=t(f"onboarding.goal.{k}", lang), callback_data=f"ob_goal:{k}")]
        for k in GOALS
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def confirm_breed_kb(lang: str, breed: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=f"✅ {breed}"[:30], callback_data="ob_breed:yes"),
                InlineKeyboardButton(
                    text=t("onboarding.btn.other", lang), callback_data="ob_breed:other"
                ),
            ]
        ]
    )
