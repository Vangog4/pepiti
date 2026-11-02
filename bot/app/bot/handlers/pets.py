"""Several dogs: switch the active dog, add another one (Free 1, Premium 3)."""

import logging

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from dependency_injector.wiring import Provide, inject

from app.bot.handlers.menu import _rate_limit_kb, build_profile_view
from app.bot.states.onboarding import OnboardingStates
from app.core.container import AppContainer
from app.i18n import normalize_locale, t
from app.services.entitlements import has_premium
from app.services.pet_service import PetService
from app.services.pets import allowed_pets, can_add, pet_limit
from app.services.user_service import UserService

logger = logging.getLogger(__name__)
router = Router(name="pets_router")


@router.callback_query(F.data.startswith("pet_sw:"))
@inject
async def switch_pet(
    cb: types.CallbackQuery,
    u_svc: UserService = Provide[AppContainer.user_service],
    p_svc: PetService = Provide[AppContainer.pet_service],
) -> None:
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)
    try:
        wanted = int(cb.data.split(":", 1)[1])
    except ValueError:
        await cb.answer()
        return
    pets = await p_svc.list_pets(usr.id)  # only the caller's own dogs
    chosen = next((p for p in allowed_pets(pets, has_premium(usr)) if p.id == wanted), None)
    if chosen is None:
        await cb.answer()
        return
    usr.active_pet_id = chosen.id
    await u_svc.repo.session.commit()
    await cb.answer(t("pets.switched", lang, name=chosen.name))
    text, kb = build_profile_view(chosen, pets, usr, lang)
    await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data == "pet_locked")
@inject
async def locked_pet(
    cb: types.CallbackQuery,
    u_svc: UserService = Provide[AppContainer.user_service],
) -> None:
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    await cb.answer(
        t("pets.locked", normalize_locale(usr.language_code), n=pet_limit(True)), show_alert=True
    )


@router.callback_query(F.data == "pet_add")
@inject
async def add_pet(
    cb: types.CallbackQuery,
    state: FSMContext,
    u_svc: UserService = Provide[AppContainer.user_service],
    p_svc: PetService = Provide[AppContainer.pet_service],
) -> None:
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)
    verdict = can_add(len(await p_svc.list_pets(usr.id)), has_premium(usr))
    if verdict == "max":
        await cb.answer(t("pets.limit.max", lang, n=pet_limit(True)), show_alert=True)
        return
    if verdict == "need_premium":
        await cb.answer()
        await cb.message.edit_text(
            t("pets.limit.free", lang, n=pet_limit(True)), reply_markup=_rate_limit_kb(lang)
        )
        return
    await cb.answer()
    await state.set_state(OnboardingStates.collecting)
    await state.update_data(adding_pet=True)
    await cb.message.edit_text(t("onboarding.q.name", lang))
