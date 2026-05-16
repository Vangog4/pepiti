from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.i18n import t

# Reverse mapping: stored DB value (Russian) → i18n key for display translation
STORED_OPTION_TO_KEY: dict[str, str] = {
    "Маленький (до 10 кг)": "edit_profile.size.small",
    "Средний (10–25 кг)":   "edit_profile.size.medium",
    "Крупный (25–45 кг)":   "edit_profile.size.large",
    "Гигант (45+ кг)":      "edit_profile.size.giant",
    "Щенок (до 4 мес)":     "edit_profile.age.1",
    "Щенок (4–12 мес)":     "edit_profile.age.2",
    "Молодой (1–3 года)":   "edit_profile.age.3",
    "Взрослый (3–7 лет)":   "edit_profile.age.4",
    "Пожилой (7+ лет)":     "edit_profile.age.5",
}


def translate_option(val: str | None, lang: str) -> str:
    """Translate a stored Russian option value to the user's language. Passthrough for unknown values."""
    if not val:
        return val or "—"
    key = STORED_OPTION_TO_KEY.get(val)
    return t(key, lang) if key else val

# (offset_code, ru_label, en_label)
TIMEZONE_OPTIONS: list[tuple[str, str, str]] = [
    ("UTC-12", "UTC-12 — Острова Дейт",          "UTC-12 — Baker Island"),
    ("UTC-11", "UTC-11 — Самоа",                  "UTC-11 — Samoa, Midway"),
    ("UTC-10", "UTC-10 — Гавайи",                 "UTC-10 — Hawaii"),
    ("UTC-9",  "UTC-9 — Аляска",                  "UTC-9 — Alaska"),
    ("UTC-8",  "UTC-8 — Лос-Анджелес, Ванкувер",  "UTC-8 — Los Angeles, Vancouver"),
    ("UTC-7",  "UTC-7 — Денвер, Феникс",          "UTC-7 — Denver, Phoenix"),
    ("UTC-6",  "UTC-6 — Чикаго, Мехико",          "UTC-6 — Chicago, Mexico City"),
    ("UTC-5",  "UTC-5 — Нью-Йорк, Богота",        "UTC-5 — New York, Bogota"),
    ("UTC-4",  "UTC-4 — Сантьяго, Каракас",       "UTC-4 — Santiago, Caracas"),
    ("UTC-3",  "UTC-3 — Буэнос-Айрес, Бразилиа",  "UTC-3 — Buenos Aires, Brasilia"),
    ("UTC-2",  "UTC-2 — Среднеатлантический",     "UTC-2 — Mid-Atlantic"),
    ("UTC-1",  "UTC-1 — Азорские острова",         "UTC-1 — Azores"),
    ("UTC",    "UTC+0 — Лондон, Дублин",           "UTC+0 — London, Dublin"),
    ("UTC+1",  "UTC+1 — Берлин, Париж, Варшава",  "UTC+1 — Berlin, Paris, Warsaw"),
    ("UTC+2",  "UTC+2 — Калининград, Афины",       "UTC+2 — Kaliningrad, Athens"),
    ("UTC+3",  "UTC+3 — Москва, Минск, Стамбул",  "UTC+3 — Moscow, Minsk, Istanbul"),
    ("UTC+4",  "UTC+4 — Баку, Самара, Дубай",     "UTC+4 — Baku, Dubai"),
    ("UTC+5",  "UTC+5 — Екатеринбург, Ташкент",   "UTC+5 — Yekaterinburg, Tashkent"),
    ("UTC+6",  "UTC+6 — Омск, Астана",             "UTC+6 — Omsk, Astana"),
    ("UTC+7",  "UTC+7 — Красноярск, Бангкок",     "UTC+7 — Krasnoyarsk, Bangkok"),
    ("UTC+8",  "UTC+8 — Иркутск, Пекин, Сингапур","UTC+8 — Irkutsk, Beijing, Singapore"),
    ("UTC+9",  "UTC+9 — Якутск, Токио, Сеул",     "UTC+9 — Yakutsk, Tokyo, Seoul"),
    ("UTC+10", "UTC+10 — Владивосток, Сидней",    "UTC+10 — Vladivostok, Sydney"),
    ("UTC+11", "UTC+11 — Магадан",                 "UTC+11 — Magadan"),
    ("UTC+12", "UTC+12 — Камчатка, Окленд",        "UTC+12 — Kamchatka, Auckland"),
    ("UTC+13", "UTC+13 — Тонга",                   "UTC+13 — Tonga"),
    ("UTC+14", "UTC+14 — Острова Лайн",            "UTC+14 — Line Islands"),
]


def get_edit_profile_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text=t("edit_profile.btn.name", lang),  callback_data="edit_field_name"),
        InlineKeyboardButton(text=t("edit_profile.btn.breed", lang), callback_data="edit_field_breed"),
    )
    b.row(
        InlineKeyboardButton(text=t("edit_profile.btn.goal", lang),  callback_data="edit_field_goal"),
        InlineKeyboardButton(text=t("edit_profile.btn.level", lang), callback_data="edit_field_training_level"),
    )
    b.row(
        InlineKeyboardButton(text=t("edit_profile.btn.age", lang),  callback_data="edit_field_age_category"),
        InlineKeyboardButton(text=t("edit_profile.btn.size", lang), callback_data="edit_field_size_category"),
    )
    b.row(InlineKeyboardButton(text=t("edit_profile.btn.timezone", lang), callback_data="edit_field_timezone"))
    b.row(InlineKeyboardButton(text=t("common.back_menu.btn", lang), callback_data="menu_main"))
    return b.as_markup()


def get_training_level_inline(lang: str = "ru") -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for i in range(1, 6):
        b.row(InlineKeyboardButton(
            text=t(f"edit_profile.level.{i}", lang),
            callback_data=f"set_level_{i}",
        ))
    b.row(InlineKeyboardButton(text=t("edit_profile.cancel.btn", lang), callback_data="menu_edit_profile"))
    return b.as_markup()


def get_size_inline(lang: str = "ru") -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text=t("edit_profile.size.small",  lang), callback_data="set_size_small"))
    b.row(InlineKeyboardButton(text=t("edit_profile.size.medium", lang), callback_data="set_size_medium"))
    b.row(InlineKeyboardButton(text=t("edit_profile.size.large",  lang), callback_data="set_size_large"))
    b.row(InlineKeyboardButton(text=t("edit_profile.size.giant",  lang), callback_data="set_size_giant"))
    b.row(InlineKeyboardButton(text=t("edit_profile.cancel.btn",  lang), callback_data="menu_edit_profile"))
    return b.as_markup()


def get_timezone_inline(lang: str = "ru") -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for i, (_, ru_label, en_label) in enumerate(TIMEZONE_OPTIONS):
        label = ru_label if lang == "ru" else en_label
        b.row(InlineKeyboardButton(text=label, callback_data=f"set_tz_{i}"))
    b.row(InlineKeyboardButton(text=t("edit_profile.cancel.btn", lang), callback_data="menu_edit_profile"))
    return b.as_markup()


def get_age_inline(lang: str = "ru") -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text=t("edit_profile.age.1", lang), callback_data="set_age_1"),
        InlineKeyboardButton(text=t("edit_profile.age.2", lang), callback_data="set_age_2"),
    )
    b.row(
        InlineKeyboardButton(text=t("edit_profile.age.3", lang), callback_data="set_age_3"),
        InlineKeyboardButton(text=t("edit_profile.age.4", lang), callback_data="set_age_4"),
    )
    b.row(InlineKeyboardButton(text=t("edit_profile.age.5", lang), callback_data="set_age_5"))
    b.row(InlineKeyboardButton(text=t("edit_profile.cancel.btn", lang), callback_data="menu_edit_profile"))
    return b.as_markup()
