"""⚖️ Weight: log a weigh-in, see the trend against the dog's own history."""

import logging

from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dependency_injector.wiring import Provide, inject

from app.bot.keyboards.main_menu import get_back_keyboard
from app.core.container import AppContainer
from app.core.tz_utils import local_now
from app.i18n import normalize_locale, t
from app.infrastructure.db.repositories.weight_repo import WeightRepository
from app.services.passport import PassportValueError, parse_passport_value
from app.services.pet_service import PetService
from app.services.user_service import UserService
from app.services.weight import weight_trend

logger = logging.getLogger(__name__)
router = Router(name="weight_router")


class WeightState(StatesGroup):
    waiting = State()


def trend_text(name: str, tr: dict, lang: str) -> str:
    if tr["last"] is None:
        return t("weight.empty", lang, name=name)
    lines = [t("weight.title", lang, name=name, kg=tr["last"])]
    if tr["delta_kg"] is not None:
        sign = "+" if tr["delta_kg"] > 0 else ""
        lines.append(
            t(
                "weight.change",
                lang,
                delta=f"{sign}{tr['delta_kg']}",
                pct=f"{sign}{tr['delta_pct']}",
                prev=tr["prev"],
            )
        )
    if tr["alert"]:
        lines.append(t(f"weight.alert.{tr['alert']}", lang))
    return "\n".join(lines)


@router.callback_query(F.data == "wt_open")
@inject
async def open_weight(
    cb: types.CallbackQuery,
    state: FSMContext,
    u_svc: UserService = Provide[AppContainer.user_service],
    p_svc: PetService = Provide[AppContainer.pet_service],
    repo: WeightRepository = Provide[AppContainer.weight_repo],
) -> None:
    await cb.answer()
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)
    pet = await p_svc.get_pet(usr.id)
    if not pet:
        await cb.message.edit_text(t("error.no_pet", lang), reply_markup=get_back_keyboard(lang))
        return
    tr = weight_trend(await repo.recent(pet.id), local_now(usr.timezone).date())
    await state.set_state(WeightState.waiting)
    await cb.message.edit_text(
        trend_text(pet.name, tr, lang) + "\n\n" + t("weight.ask", lang),
        reply_markup=get_back_keyboard(lang),
        parse_mode="HTML",
    )


@router.message(StateFilter(WeightState.waiting), F.text)
@inject
async def receive_weight(
    msg: types.Message,
    state: FSMContext,
    u_svc: UserService = Provide[AppContainer.user_service],
    p_svc: PetService = Provide[AppContainer.pet_service],
    repo: WeightRepository = Provide[AppContainer.weight_repo],
) -> None:
    usr = await u_svc.get_or_create_telegram_user(telegram_id=msg.from_user.id)
    lang = normalize_locale(usr.language_code)
    pet = await p_svc.get_pet(usr.id)
    if not pet:
        await state.clear()
        return
    try:
        kg = parse_passport_value("weight_kg", msg.text or "")
    except PassportValueError:
        await msg.answer(t("edit_profile.error.invalid", lang))
        return
    today = local_now(usr.timezone).date()
    await repo.add(pet.id, kg, today)
    pet.weight_kg = kg  # keep the passport in sync with the latest weigh-in
    await p_svc.repo.session.commit()
    await state.clear()
    tr = weight_trend(await repo.recent(pet.id), today)
    await msg.answer(
        t("weight.saved", lang, kg=kg) + "\n\n" + trend_text(pet.name, tr, lang),
        reply_markup=get_back_keyboard(lang),
        parse_mode="HTML",
    )
