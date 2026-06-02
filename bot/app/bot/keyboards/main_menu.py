from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.i18n import t

# Language name shown on picker buttons — always in the target language itself
LANGUAGE_OPTIONS: list[tuple[str, str]] = [
    ("ru", "🇷🇺 Русский"),
    ("en", "🇬🇧 English"),
    ("de", "🇩🇪 Deutsch"),
    ("fr", "🇫🇷 Français"),
    ("es", "🇲🇽 Español"),
    ("pt", "🇧🇷 Português"),
]


def get_main_menu(
    is_premium: bool = False, webapp_url: str = "", lang: str = "ru"
) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text=t("menu.btn.training", lang), callback_data="menu_training"))
    b.row(
        InlineKeyboardButton(text=t("menu.btn.week_plan", lang), callback_data="menu_week_plan"),
        InlineKeyboardButton(text=t("menu.btn.stats", lang), callback_data="menu_stats"),
    )
    b.row(
        InlineKeyboardButton(text=t("menu.btn.coach", lang), callback_data="menu_coach"),
        InlineKeyboardButton(text=t("menu.btn.profile", lang), callback_data="menu_profile"),
    )
    premium_key = "menu.btn.premium.active" if is_premium else "menu.btn.premium"
    b.row(
        InlineKeyboardButton(text=t(premium_key, lang), callback_data="menu_premium"),
        InlineKeyboardButton(text=t("settings.btn", lang), callback_data="menu_settings"),
    )
    b.row(
        InlineKeyboardButton(text=t("menu.btn.shop", lang), callback_data="menu_shop"),
        InlineKeyboardButton(text=t("menu.btn.invite", lang), callback_data="menu_invite"),
    )
    if webapp_url:
        b.row(
            InlineKeyboardButton(
                text=t("menu.btn.webapp", lang), web_app=WebAppInfo(url=webapp_url)
            )
        )
    return b.as_markup()


def get_settings_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(text=t("settings.reminder.btn", lang), callback_data="menu_reminder")
    )
    b.row(InlineKeyboardButton(text=t("profile.edit.btn", lang), callback_data="menu_edit_profile"))
    b.row(
        InlineKeyboardButton(text=t("settings.language.btn", lang), callback_data="menu_language")
    )
    b.row(InlineKeyboardButton(text=t("help.btn", lang), callback_data="menu_help"))
    b.row(InlineKeyboardButton(text=t("common.back_menu.btn", lang), callback_data="menu_main"))
    return b.as_markup()


def get_help_keyboard(lang: str = "ru", support_url: str = "") -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    if support_url:
        b.row(InlineKeyboardButton(text=t("help.support.btn", lang), url=support_url))
    b.row(
        InlineKeyboardButton(text=t("help.back_settings.btn", lang), callback_data="menu_settings")
    )
    return b.as_markup()


def get_language_keyboard(current_lang: str = "ru") -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for code, label in LANGUAGE_OPTIONS:
        checkmark = " ✓" if code == current_lang else ""
        b.row(InlineKeyboardButton(text=f"{label}{checkmark}", callback_data=f"set_lang_{code}"))
    b.row(InlineKeyboardButton(text="🔙 Назад / Back", callback_data="menu_settings"))
    return b.as_markup()


def get_back_keyboard(lang: str = "ru") -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text=t("common.back_menu.btn", lang), callback_data="menu_main"))
    return b.as_markup()
