import io
import logging
from datetime import datetime

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from dependency_injector.wiring import Provide, inject

from app.core.container import AppContainer
from app.core.config import settings
from app.services.user_service import UserService
from app.services.pet_service import PetService
from app.services.training_service import TrainingService
from app.services.referral_service import (
    ReferralService, REFERRAL_BONUS_DAYS, notify_referrer,
    milestone_label, milestone_reward,
)
from app.services.ai_service import AiService
from app.infrastructure.db.models.pet import PetModel
from app.bot.states.onboarding import OnboardingStates
from app.bot.keyboards.main_menu import get_main_menu
from app.bot.keyboards.training import get_task_keyboard
from app.i18n import t, normalize_locale

logger = logging.getLogger(__name__)
router = Router(name="onboarding_router")


def _profile_summary(profile: dict) -> str:
    parts = []
    if profile.get("name"):
        parts.append(profile["name"])
    if profile.get("breed"):
        parts.append(profile["breed"])
    if profile.get("age_category"):
        parts.append(profile["age_category"])
    return ", ".join(parts)


async def _finish_onboarding(
    msg: types.Message,
    state: FSMContext,
    profile: dict,
    state_data: dict,
    user_svc: UserService,
    pet_svc: PetService,
    ref_svc: ReferralService,
    t_svc: TrainingService,
    lang: str,
) -> None:
    user = await user_svc.get_or_create_telegram_user(telegram_id=msg.from_user.id)

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
        await notify_referrer(msg.bot, referral_result, normalize_locale(referral_result.referrer_lang))
    await state.clear()

    # Notify admins about new user
    uname = f"@{user.username}" if user.username else "—"
    ref_note = f"\nПришёл по реферальной ссылке" if referral_result.base_awarded else ""
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
        welcome += t("onboarding.done.milestone", lang, label=milestone_label(m, lang), reward=milestone_reward(m, lang))

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


async def _handle_message(
    msg: types.Message,
    state: FSMContext,
    user_svc: UserService,
    pet_svc: PetService,
    ref_svc: ReferralService,
    t_svc: TrainingService,
    ai_svc: AiService,
    is_clarification: bool,
) -> None:
    # Photo without caption → ask for text/voice description
    if msg.photo and not msg.caption:
        user = await user_svc.get_or_create_telegram_user(telegram_id=msg.from_user.id)
        lang = normalize_locale(user.language_code)
        await msg.answer(t("onboarding.ai.photo_prompt", lang), reply_markup=ReplyKeyboardRemove())
        return

    audio_bytes: bytes | None = None
    mime_type: str | None = None
    if msg.voice:
        bio = io.BytesIO()
        await msg.bot.download(msg.voice, destination=bio)
        audio_bytes = bio.getvalue()
        mime_type = "audio/ogg"

    text = msg.text or msg.caption
    state_data = await state.get_data()
    partial = state_data.get("partial_profile") if is_clarification else None

    user = await user_svc.get_or_create_telegram_user(telegram_id=msg.from_user.id)
    lang = normalize_locale(user.language_code)

    thinking = await msg.answer(t("onboarding.ai.thinking", lang), reply_markup=ReplyKeyboardRemove())

    profile = await ai_svc.extract_pet_profile(
        language_code=lang,
        text=text,
        audio_bytes=audio_bytes,
        mime_type=mime_type,
        partial=partial,
    )

    await thinking.delete()

    missing = profile.get("missing_fields", [])

    # On first attempt: if fields are missing, ask one clarifying question
    if missing and not is_clarification:
        await state.update_data(partial_profile=profile)
        await state.set_state(OnboardingStates.clarifying)

        clarify_q = profile.get("clarify_question") or t(
            f"onboarding.ai.clarify.{missing[0]}", lang
        )
        summary = _profile_summary(profile)
        if summary:
            reply = t("onboarding.ai.clarify", lang, summary=summary, question=clarify_q)
        else:
            reply = clarify_q
        await msg.answer(reply, reply_markup=ReplyKeyboardRemove())
        return

    # Complete onboarding (either all fields present, or second attempt regardless)
    await _finish_onboarding(msg, state, profile, state_data, user_svc, pet_svc, ref_svc, t_svc, lang)


@router.message(OnboardingStates.collecting, F.text | F.voice | F.photo)
@inject
async def process_collecting(
    msg: types.Message,
    state: FSMContext,
    user_svc: UserService = Provide[AppContainer.user_service],
    pet_svc: PetService = Provide[AppContainer.pet_service],
    ref_svc: ReferralService = Provide[AppContainer.referral_service],
    t_svc: TrainingService = Provide[AppContainer.training_service],
    ai_svc: AiService = Provide[AppContainer.ai_service],
) -> None:
    await _handle_message(msg, state, user_svc, pet_svc, ref_svc, t_svc, ai_svc, is_clarification=False)


@router.message(OnboardingStates.clarifying, F.text | F.voice)
@inject
async def process_clarifying(
    msg: types.Message,
    state: FSMContext,
    user_svc: UserService = Provide[AppContainer.user_service],
    pet_svc: PetService = Provide[AppContainer.pet_service],
    ref_svc: ReferralService = Provide[AppContainer.referral_service],
    t_svc: TrainingService = Provide[AppContainer.training_service],
    ai_svc: AiService = Provide[AppContainer.ai_service],
) -> None:
    await _handle_message(msg, state, user_svc, pet_svc, ref_svc, t_svc, ai_svc, is_clarification=True)
