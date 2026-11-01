import io
import logging
from datetime import datetime

from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from dependency_injector.wiring import Provide, inject

from app.bot.keyboards.main_menu import get_main_menu
from app.bot.keyboards.onboarding import (
    AGES,
    BREEDS,
    GOALS,
    age_kb,
    breed_kb,
    confirm_breed_kb,
    goal_kb,
)
from app.bot.keyboards.training import get_task_keyboard
from app.bot.states.onboarding import OnboardingStates
from app.core.config import settings
from app.core.container import AppContainer
from app.i18n import normalize_locale, t
from app.infrastructure.db.models.pet import PetModel
from app.services.ai_service import AiService
from app.services.pet_service import PetService
from app.services.referral_service import (
    REFERRAL_BONUS_DAYS,
    ReferralService,
    milestone_label,
    milestone_reward,
    notify_referrer,
)
from app.services.training_service import TrainingService
from app.services.user_service import UserService

logger = logging.getLogger(__name__)
router = Router(name="onboarding_router")


async def _finish_onboarding(
    msg: types.Message,
    tg_id: int,
    state: FSMContext,
    profile: dict,
    state_data: dict,
    user_svc: UserService,
    pet_svc: PetService,
    ref_svc: ReferralService,
    t_svc: TrainingService,
    lang: str,
) -> None:
    user = await user_svc.get_or_create_telegram_user(telegram_id=tg_id)

    pet = PetModel(
        user_id=user.id,
        name=profile.get("name") or t("defaults.pet_name", lang),
        breed=profile.get("breed"),
        age_category=profile.get("age_category"),
        size_category=profile.get("size_category"),
        behavior_issues=profile.get("behavior_issues"),
        goal=profile.get("goal"),
    )
    await pet_svc.repo.create(pet)

    user.onboarding_completed_at = datetime.utcnow()
    referrer_tid = state_data.get("referrer_telegram_id")
    if referrer_tid and not user.referrer_telegram_id:
        user.referrer_telegram_id = referrer_tid

    await user_svc.repo.session.commit()
    referral_result = await ref_svc.award_if_eligible(user)
    if referral_result.base_awarded:
        await notify_referrer(
            msg.bot, referral_result, normalize_locale(referral_result.referrer_lang)
        )
    await state.clear()

    # Notify admins about new user
    uname = "@" + user.username if user.username else "—"
    ref_note = "\nПришёл по реферальной ссылке" if referral_result.base_awarded else ""
    notify_text = (
        f"🐾 <b>Новый пользователь!</b>\n"
        f"{user.first_name or '—'} ({uname})\n"
        f"ID: <code>{user.telegram_id}</code>{ref_note}"
    )
    for admin_id in settings.ADMIN_TELEGRAM_IDS:
        try:
            await msg.bot.send_message(chat_id=admin_id, text=notify_text, parse_mode="HTML")
        except Exception:
            pass

    welcome = t("onboarding.done.welcome", lang, name=user.first_name, pet=pet.name)
    if referral_result.base_awarded:
        welcome += t("onboarding.done.referral_bonus", lang, days=REFERRAL_BONUS_DAYS)
    if referral_result.milestone:
        m = referral_result.milestone
        welcome += t(
            "onboarding.done.milestone",
            lang,
            label=milestone_label(m, lang),
            reward=milestone_reward(m, lang),
        )

    await msg.answer(welcome, parse_mode="HTML")

    loading = await msg.answer(
        t("onboarding.done.plan_loading", lang, pet=pet.name),
        parse_mode="HTML",
    )
    try:
        plan = await t_svc.get_or_create_today(user.id, pet, lang=lang)
        plan_text = TrainingService.format_plan(plan, lang)
        await loading.edit_text(
            t("onboarding.done.first_plan", lang, plan=plan_text),
            reply_markup=get_task_keyboard(plan.tasks, lang=lang),
            parse_mode="HTML",
        )
    except Exception:
        logger.exception("Failed to generate first plan for user %s", user.id)
        await loading.edit_text(
            t("onboarding.done.fallback", lang),
            reply_markup=get_main_menu(webapp_url=settings.WEBAPP_PUBLIC_URL, lang=lang),
        )


def _clean_name(text: str | None) -> str | None:
    name = " ".join((text or "").split())[:40]
    return name or None


@router.message(OnboardingStates.collecting, F.text)
@inject
async def step_name(
    msg: types.Message,
    state: FSMContext,
    user_svc: UserService = Provide[AppContainer.user_service],
) -> None:
    user = await user_svc.get_or_create_telegram_user(telegram_id=msg.from_user.id)
    lang = normalize_locale(user.language_code)
    name = _clean_name(msg.text)
    if not name or name.startswith("/"):
        await msg.answer(t("onboarding.name.need_text", lang))
        return
    await state.update_data(name=name)
    await state.set_state(OnboardingStates.age)
    await msg.answer(
        t("onboarding.q.age", lang, name=name), reply_markup=age_kb(lang), parse_mode="HTML"
    )


@router.message(OnboardingStates.collecting)
@inject
async def step_name_not_text(
    msg: types.Message, user_svc: UserService = Provide[AppContainer.user_service]
) -> None:
    user = await user_svc.get_or_create_telegram_user(telegram_id=msg.from_user.id)
    await msg.answer(t("onboarding.name.need_text", normalize_locale(user.language_code)))


@router.callback_query(OnboardingStates.age, F.data.startswith("ob_age:"))
@inject
async def step_age(
    cb: types.CallbackQuery,
    state: FSMContext,
    user_svc: UserService = Provide[AppContainer.user_service],
) -> None:
    await cb.answer()
    age = AGES.get(cb.data.split(":", 1)[1])
    if age is None:
        return
    user = await user_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(user.language_code)
    await state.update_data(age_category=age)
    await state.set_state(OnboardingStates.breed)
    await cb.message.edit_text(t("onboarding.q.breed", lang), reply_markup=breed_kb(lang))


@router.callback_query(OnboardingStates.breed, F.data.startswith("ob_breed:"))
@router.callback_query(OnboardingStates.breed_text, F.data.startswith("ob_breed:"))
@inject
async def step_breed(
    cb: types.CallbackQuery,
    state: FSMContext,
    user_svc: UserService = Provide[AppContainer.user_service],
) -> None:
    await cb.answer()
    user = await user_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(user.language_code)
    choice = cb.data.split(":", 1)[1]
    if choice in ("other", "photo"):
        await state.set_state(OnboardingStates.breed_text)
        await cb.message.edit_text(t("onboarding.q.breed_text", lang))
        return
    if choice == "yes":
        breed = (await state.get_data()).get("guessed_breed")
    elif choice.isdigit() and int(choice) < len(BREEDS):
        breed = BREEDS[int(choice)][1]
    else:
        return
    await _ask_goal(cb.message, state, lang, breed)


async def _ask_goal(target: types.Message, state: FSMContext, lang: str, breed: str | None) -> None:
    await state.update_data(breed=breed)
    await state.set_state(OnboardingStates.goal)
    text = t("onboarding.q.goal", lang)
    try:
        await target.edit_text(text, reply_markup=goal_kb(lang))
    except Exception:  # message is not ours to edit (typed answer): send a new one
        await target.answer(text, reply_markup=goal_kb(lang))


@router.message(OnboardingStates.breed_text, F.text)
@inject
async def step_breed_typed(
    msg: types.Message,
    state: FSMContext,
    user_svc: UserService = Provide[AppContainer.user_service],
) -> None:
    user = await user_svc.get_or_create_telegram_user(telegram_id=msg.from_user.id)
    lang = normalize_locale(user.language_code)
    breed = " ".join((msg.text or "").split())[:60]
    if not breed or breed.startswith("/"):
        await msg.answer(t("onboarding.q.breed_text", lang))
        return
    await _ask_goal(msg, state, lang, breed)


@router.message(OnboardingStates.breed_text, F.photo)
@router.message(OnboardingStates.breed, F.photo)
@inject
async def step_breed_photo(
    msg: types.Message,
    state: FSMContext,
    user_svc: UserService = Provide[AppContainer.user_service],
    ai_svc: AiService = Provide[AppContainer.ai_service],
) -> None:
    user = await user_svc.get_or_create_telegram_user(telegram_id=msg.from_user.id)
    lang = normalize_locale(user.language_code)
    bio = io.BytesIO()
    await msg.bot.download(msg.photo[-1], destination=bio)
    try:
        guess = await ai_svc.guess_breed(bio.getvalue())
    except Exception:
        guess = None
    if guess is None:
        await state.set_state(OnboardingStates.breed_text)
        await msg.answer(t("onboarding.photo.fail", lang))
        return
    await state.update_data(guessed_breed=guess.breed)
    await state.set_state(OnboardingStates.breed_text)
    await msg.answer(
        t("onboarding.photo.guess", lang, breed=guess.breed),
        reply_markup=confirm_breed_kb(lang, guess.breed),
        parse_mode="HTML",
    )


@router.callback_query(OnboardingStates.goal, F.data.startswith("ob_goal:"))
@inject
async def step_goal(
    cb: types.CallbackQuery,
    state: FSMContext,
    user_svc: UserService = Provide[AppContainer.user_service],
    pet_svc: PetService = Provide[AppContainer.pet_service],
    ref_svc: ReferralService = Provide[AppContainer.referral_service],
    t_svc: TrainingService = Provide[AppContainer.training_service],
) -> None:
    await cb.answer()
    goal = GOALS.get(cb.data.split(":", 1)[1])
    if goal is None:
        return
    data = await state.get_data()
    user = await user_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(user.language_code)
    profile = {
        "name": data.get("name"),
        "age_category": data.get("age_category"),
        "breed": data.get("breed"),
        "goal": goal,
    }
    await _finish_onboarding(
        cb.message, cb.from_user.id, state, profile, data, user_svc, pet_svc, ref_svc, t_svc, lang
    )


@router.message(StateFilter("OnboardingStates:clarifying"))
@inject
async def legacy_clarifying_restart(
    msg: types.Message,
    state: FSMContext,
    user_svc: UserService = Provide[AppContainer.user_service],
) -> None:
    """Users parked in the removed AI-dialog state: restart them on the button flow."""
    user = await user_svc.get_or_create_telegram_user(telegram_id=msg.from_user.id)
    await state.clear()
    await state.set_state(OnboardingStates.collecting)
    await msg.answer(t("onboarding.q.name", normalize_locale(user.language_code)))
