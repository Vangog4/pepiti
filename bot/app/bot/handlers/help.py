from aiogram import Router, types
from aiogram.filters import Command
from dependency_injector.wiring import Provide, inject

from app.core.container import AppContainer
from app.core.config import settings
from app.services.user_service import UserService
from app.bot.keyboards.main_menu import get_help_keyboard
from app.i18n import t, normalize_locale

router = Router(name="help_router")


def build_help_text(lang: str) -> str:
    return "".join([
        t("help.guide.title", lang),
        t("help.guide.plan.header", lang),
        t("help.guide.plan.text", lang),
        t("help.guide.streak.header", lang),
        t("help.guide.streak.text", lang),
        t("help.guide.shop.header", lang),
        t("help.guide.shop.text", lang),
        t("help.guide.premium.header", lang),
        t("help.guide.premium.text", lang),
        t("help.guide.commands", lang),
    ])


@router.message(Command("help"))
@inject
async def show_help(
    msg: types.Message,
    u_svc: UserService = Provide[AppContainer.user_service],
) -> None:
    usr = await u_svc.get_or_create_telegram_user(telegram_id=msg.from_user.id)
    lang = normalize_locale(usr.language_code)
    await msg.answer(
        build_help_text(lang),
        parse_mode="HTML",
        reply_markup=get_help_keyboard(lang, settings.SUPPORT_URL),
    )
