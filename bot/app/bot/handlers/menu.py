import asyncio
import io
import re
import urllib.parse
from datetime import date, datetime

from aiogram import F, Router, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup, default_state
from dependency_injector.wiring import Provide, inject
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.bot.handlers.help import build_help_text
from app.bot.keyboards.edit_profile import translate_option
from app.bot.keyboards.main_menu import (
    LANGUAGE_OPTIONS,
    get_back_keyboard,
    get_help_keyboard,
    get_language_keyboard,
    get_main_menu,
    get_settings_keyboard,
)
from app.bot.keyboards.training import get_task_keyboard, get_week_day_keyboard
from app.core.config import settings
from app.core.container import AppContainer
from app.core.shop import SHOP_URL_BY_SIZE, SHOP_URL_LONGPLAY, SHOP_URL_MAIN, SHOP_URL_TRAINING
from app.core.shop_recommendations import AFTER_COMPLETION, AFTER_EXERCISE, get_shop_button
from app.i18n import normalize_locale, pluralize, t
from app.infrastructure.db.models.coach_thread import CoachThreadModel
from app.infrastructure.db.models.training import TrainingPlanModel
from app.infrastructure.db.repositories.ai_conversation_repo import AiConversationRepository
from app.infrastructure.db.repositories.coach_thread_repo import CoachThreadRepository
from app.infrastructure.redis.ai_rate_limit import AiRateLimiter
from app.infrastructure.redis.metrics import BotMetrics
from app.services.ai_service import AiService
from app.services.coach_service import CoachService
from app.services.pet_service import PetService
from app.services.referral_service import (
    REFERRAL_BONUS_DAYS,
    REFERRAL_MILESTONES,
    ReferralService,
    milestone_label,
    milestone_reward,
)
from app.services.training_service import TrainingService
from app.services.user_service import UserService

router = Router(name="menu_router")


def _rate_limit_kb(lang: str = "ru") -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=t("ai.rate_limit.btn", lang), callback_data="menu_premium"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text=t("common.back_menu.btn", lang), callback_data="menu_main"
                )
            ],
        ]
    )


class ReminderState(StatesGroup):
    waiting_for_time = State()


class CoachState(StatesGroup):
    waiting_for_question = State()


def _ai_error_kb(retry_cb: str = "menu_main", lang: str = "ru") -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(text=t("ai.retry.btn", lang), callback_data=retry_cb),
                types.InlineKeyboardButton(
                    text=t("ai.back_menu.btn", lang), callback_data="menu_main"
                ),
            ]
        ]
    )


def _streak_emoji(n: int) -> str:
    if n <= 3:
        return "🌱"
    if n <= 6:
        return "🔥"
    if n <= 14:
        return "⚡"
    return "🏆"


def _menu_text(streak: int = 0, lang: str = "ru") -> str:
    if streak:
        emoji = _streak_emoji(streak)
        days_word = pluralize(
            streak,
            lang,
            one=t("menu.main.streak.days.one", lang),
            few=t("menu.main.streak.days.few", lang),
            many=t("menu.main.streak.days.many", lang),
            other=t("menu.main.streak.days.many", lang),
        )
        streak_line = t("menu.main.streak", lang, emoji=emoji, n=streak, days=days_word)
    else:
        streak_line = ""
    return f"{t('menu.main.greeting', lang)}\n\n{streak_line}{t('menu.main.choose', lang)}"


# ─── /menu command ───────────────────────────────────────────────────────────


@router.message(Command("menu"))
@inject
async def show_menu(
    msg: types.Message,
    state: FSMContext,
    u_svc: UserService = Provide[AppContainer.user_service],
    p_svc: PetService = Provide[AppContainer.pet_service],
) -> None:
    await state.clear()
    tmp = await msg.answer("⌛️", reply_markup=types.ReplyKeyboardRemove())
    await tmp.delete()
    usr = await u_svc.get_or_create_telegram_user(telegram_id=msg.from_user.id)
    pet = await p_svc.get_pet(usr.id)
    streak = pet.training_days or 0 if pet else 0
    lang = normalize_locale(usr.language_code)
    await msg.answer(
        _menu_text(streak, lang),
        reply_markup=get_main_menu(
            usr.is_premium, webapp_url=settings.WEBAPP_PUBLIC_URL, lang=lang
        ),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "menu_main")
@inject
async def back_to_main(
    cb: types.CallbackQuery,
    state: FSMContext,
    u_svc: UserService = Provide[AppContainer.user_service],
    p_svc: PetService = Provide[AppContainer.pet_service],
) -> None:
    await state.clear()
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    pet = await p_svc.get_pet(usr.id)
    streak = pet.training_days or 0 if pet else 0
    lang = normalize_locale(usr.language_code)
    await cb.message.edit_text(
        _menu_text(streak, lang),
        reply_markup=get_main_menu(
            usr.is_premium, webapp_url=settings.WEBAPP_PUBLIC_URL, lang=lang
        ),
        parse_mode="HTML",
    )
    await cb.answer()


# ─── settings submenu ────────────────────────────────────────────────────────


@router.callback_query(F.data == "menu_settings")
@inject
async def show_settings(
    cb: types.CallbackQuery,
    state: FSMContext,
    u_svc: UserService = Provide[AppContainer.user_service],
) -> None:
    await state.clear()
    await cb.answer()
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)
    rt = usr.reminder_time
    tz = usr.timezone or "UTC"
    if rt == "off":
        reminder_line = t("settings.main.reminder_off", lang)
    elif rt:
        reminder_line = t("settings.main.reminder_on", lang, time=rt, tz=tz)
    else:
        reminder_line = t("settings.main.reminder_default", lang, tz=tz)
    await cb.message.edit_text(
        f"{t('settings.main.title', lang)}\n\n{reminder_line}",
        reply_markup=get_settings_keyboard(lang),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "menu_help")
@inject
async def show_help_cb(
    cb: types.CallbackQuery,
    state: FSMContext,
    u_svc: UserService = Provide[AppContainer.user_service],
) -> None:
    await state.clear()
    await cb.answer()
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)
    await cb.message.edit_text(
        build_help_text(lang),
        reply_markup=get_help_keyboard(lang, settings.SUPPORT_URL),
        parse_mode="HTML",
    )


# ─── training plan ───────────────────────────────────────────────────────────


@router.callback_query(F.data == "menu_training")
@inject
async def show_training_plan(
    cb: types.CallbackQuery,
    state: FSMContext,
    u_svc: UserService = Provide[AppContainer.user_service],
    p_svc: PetService = Provide[AppContainer.pet_service],
    t_svc: TrainingService = Provide[AppContainer.training_service],
) -> None:
    await state.clear()
    await cb.answer()
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)
    pet = await p_svc.get_pet(usr.id)
    if not pet:
        await cb.message.edit_text(t("error.no_pet", lang), reply_markup=get_back_keyboard(lang))
        return

    await cb.message.edit_text(t("training.loading", lang, name=pet.name), parse_mode="HTML")
    try:
        plan = await t_svc.get_or_create_today(usr.id, pet, lang=lang)
    except Exception:
        await cb.message.edit_text(
            t("ai.fallback", lang),
            reply_markup=_ai_error_kb("menu_training", lang),
            parse_mode="HTML",
        )
        return
    text = TrainingService.format_plan(plan, lang)
    plan_done = plan.tasks and all(t.is_completed for t in plan.tasks)
    shop = get_shop_button(pet, usr.is_premium, AFTER_COMPLETION) if plan_done else None
    await cb.message.edit_text(
        text,
        reply_markup=get_task_keyboard(plan.tasks, shop_btn=shop, lang=lang),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "refresh_confirm")
@inject
async def confirm_refresh(
    cb: types.CallbackQuery,
    u_svc: UserService = Provide[AppContainer.user_service],
) -> None:
    await cb.answer()
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=t("training.refresh.confirm.yes", lang), callback_data="refresh"
                ),
                types.InlineKeyboardButton(
                    text=t("training.refresh.confirm.no", lang), callback_data="menu_training"
                ),
            ]
        ]
    )
    await cb.message.edit_text(
        t("training.refresh.confirm", lang),
        reply_markup=kb,
        parse_mode="HTML",
    )


@router.callback_query(F.data == "refresh")
@inject
async def refresh_plan(
    cb: types.CallbackQuery,
    u_svc: UserService = Provide[AppContainer.user_service],
    p_svc: PetService = Provide[AppContainer.pet_service],
    t_svc: TrainingService = Provide[AppContainer.training_service],
    rate_limiter: AiRateLimiter = Provide[AppContainer.ai_rate_limiter],
) -> None:
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)
    await cb.answer(t("training.refresh.toast", lang))
    pet = await p_svc.get_pet(usr.id)
    if not pet:
        await cb.message.edit_text(t("error.no_pet", lang), reply_markup=get_back_keyboard(lang))
        return

    if not usr.is_premium and not await rate_limiter.is_allowed(cb.from_user.id):
        await cb.message.edit_text(
            t("ai.rate_limit", lang), reply_markup=_rate_limit_kb(lang), parse_mode="HTML"
        )
        return

    await cb.message.edit_text(
        t("training.refresh.loading", lang, name=pet.name), parse_mode="HTML"
    )
    try:
        plan = await t_svc.refresh_plan(usr.id, pet, lang=lang)
    except Exception:
        await cb.message.edit_text(
            t("ai.fallback", lang),
            reply_markup=_ai_error_kb("menu_training", lang),
            parse_mode="HTML",
        )
        return
    if not usr.is_premium:
        await rate_limiter.increment(cb.from_user.id)
    text = TrainingService.format_plan(plan, lang)
    await cb.message.edit_text(
        text,
        reply_markup=get_task_keyboard(plan.tasks, lang=lang),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("task_done:"))
@inject
async def toggle_task(
    cb: types.CallbackQuery,
    p_svc: PetService = Provide[AppContainer.pet_service],
    u_svc: UserService = Provide[AppContainer.user_service],
    t_svc: TrainingService = Provide[AppContainer.training_service],
) -> None:
    parts = cb.data.split(":")
    try:
        task_id = int(parts[1])
    except (IndexError, ValueError):
        await cb.answer()
        return

    # New format encodes current state — answer immediately before any DB work
    answered = False
    if len(parts) >= 3:
        current_done = parts[2] == "1"
        toast_key = (
            "training.task.toggle.done" if not current_done else "training.task.toggle.undone"
        )
        await cb.answer(t(toast_key, normalize_locale(cb.from_user.language_code)))
        answered = True

    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)
    pet = await p_svc.get_pet(usr.id)
    if not pet:
        if not answered:
            await cb.answer()
        return

    task, plan_done = await t_svc.toggle_task(task_id, pet)
    if not answered:
        toast_key = (
            "training.task.toggle.done" if task.is_completed else "training.task.toggle.undone"
        )
        await cb.answer(t(toast_key, lang))

    result = await p_svc.repo.session.execute(
        select(TrainingPlanModel)
        .where(TrainingPlanModel.id == task.plan_id)
        .options(selectinload(TrainingPlanModel.tasks))
    )
    plan = result.scalar_one_or_none()
    if not plan:
        return

    text = TrainingService.format_plan(plan, lang)
    share_btn = None
    if plan_done:
        streak_n = pet.training_days or 1
        emoji = _streak_emoji(streak_n)
        days_word = pluralize(
            streak_n,
            lang,
            one=t("menu.main.streak.days.one", lang),
            few=t("menu.main.streak.days.few", lang),
            many=t("menu.main.streak.days.many", lang),
            other=t("menu.main.streak.days.many", lang),
        )
        text += t("training.done", lang, emoji=emoji, n=streak_n, days=days_word)
        share_text = t("training.share.text", lang, name=pet.name, n=streak_n, days=days_word)
        share_url = "https://t.me/share/url?text=" + urllib.parse.quote(share_text)
        share_btn = types.InlineKeyboardButton(text=t("training.share.btn", lang), url=share_url)

    shop = get_shop_button(pet, usr.is_premium, AFTER_COMPLETION) if plan_done else None
    extra = [btn for btn in [share_btn, shop] if btn]
    await cb.message.edit_text(
        text,
        reply_markup=get_task_keyboard(plan.tasks, extra_btns=extra, lang=lang),
        parse_mode="HTML",
    )


# ─── profile ─────────────────────────────────────────────────────────────────


@router.callback_query(F.data == "menu_profile")
@inject
async def show_profile(
    cb: types.CallbackQuery,
    state: FSMContext,
    u_svc: UserService = Provide[AppContainer.user_service],
    p_svc: PetService = Provide[AppContainer.pet_service],
) -> None:
    await state.clear()
    await cb.answer()
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)
    pet = await p_svc.get_pet(usr.id)
    if not pet:
        await cb.message.edit_text(t("error.no_pet", lang), reply_markup=get_back_keyboard(lang))
        return

    weight = (
        f"{pet.weight_kg} {t('profile.weight.unit', lang)}"
        if pet.weight_kg
        else t("profile.weight.unknown", lang)
    )
    issues = pet.behavior_issues or t("profile.issues.none", lang)
    schedule = pet.training_schedule or t("profile.schedule.unknown", lang)
    text = (
        t("profile.header", lang, name=pet.name)
        + t("profile.breed", lang, val=pet.breed or "—")
        + t("profile.sex", lang, val=pet.sex or "—")
        + t("profile.age", lang, val=translate_option(pet.age_category, lang) or "—")
        + t("profile.size", lang, val=translate_option(pet.size_category, lang) or "—")
        + t("profile.weight", lang, val=weight)
        + t("profile.level", lang, val=pet.training_level or "—")
        + t("profile.goal", lang, val=pet.goal or "—")
        + t("profile.issues", lang, val=issues)
        + t("profile.schedule", lang, val=schedule)
        + t("profile.training_count", lang, n=pet.training_days or 0)
    )
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=t("profile.edit.btn", lang), callback_data="menu_edit_profile"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text=t("common.back_menu.btn", lang), callback_data="menu_main"
                )
            ],
        ]
    )
    await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


# ─── stats ───────────────────────────────────────────────────────────────────


@router.callback_query(F.data == "menu_stats")
@inject
async def show_stats(
    cb: types.CallbackQuery,
    state: FSMContext,
    u_svc: UserService = Provide[AppContainer.user_service],
    p_svc: PetService = Provide[AppContainer.pet_service],
) -> None:
    await state.clear()
    await cb.answer()
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)
    pet = await p_svc.get_pet(usr.id)
    if not pet:
        await cb.message.edit_text(t("error.no_pet", lang), reply_markup=get_back_keyboard(lang))
        return

    days_with_us = 1
    if usr.onboarding_completed_at:
        delta = datetime.now(datetime.UTC).replace(tzinfo=None) - usr.onboarding_completed_at
        days_with_us = max(1, delta.days)

    completed = pet.training_days or 0
    if completed == 0:
        empty_text = t("stats.header", lang, name=pet.name) + t("training.stats.empty", lang)
        empty_kb = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text=t("training.stats.empty.cta", lang), callback_data="menu_training"
                    )
                ],
                [
                    types.InlineKeyboardButton(
                        text=t("common.back_menu.btn", lang), callback_data="menu_main"
                    )
                ],
            ]
        )
        await cb.message.edit_text(empty_text, reply_markup=empty_kb, parse_mode="HTML")
        return

    text = (
        t("stats.header", lang, name=pet.name)
        + t("stats.days_with_us", lang, n=days_with_us)
        + t("stats.completed", lang, emoji=_streak_emoji(completed), n=completed)
        + t("stats.level", lang, level=pet.training_level or "—")
        + t("stats.motivate", lang, name=pet.name)
    )
    analysis_btn = (
        t("stats.analysis.premium.btn", lang)
        if usr.is_premium
        else t("stats.analysis.free.btn", lang)
    )
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text=analysis_btn, callback_data="menu_ai_progress")],
            [
                types.InlineKeyboardButton(
                    text=t("common.back_menu.btn", lang), callback_data="menu_main"
                )
            ],
        ]
    )
    await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


# ─── ai progress ─────────────────────────────────────────────────────────────


@router.callback_query(F.data == "menu_ai_progress")
@inject
async def show_ai_progress(
    cb: types.CallbackQuery,
    state: FSMContext,
    u_svc: UserService = Provide[AppContainer.user_service],
    p_svc: PetService = Provide[AppContainer.pet_service],
    a_svc: AiService = Provide[AppContainer.ai_service],
    rate_limiter: AiRateLimiter = Provide[AppContainer.ai_rate_limiter],
) -> None:
    await state.clear()
    await cb.answer()
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)
    pet = await p_svc.get_pet(usr.id)
    if not pet:
        await cb.message.edit_text(t("error.no_pet", lang), reply_markup=get_back_keyboard(lang))
        return

    if usr.is_premium:
        await cb.message.edit_text(t("ai.analyzing.premium", lang), parse_mode="HTML")
        try:
            result = await a_svc.premium_deep_analysis(pet, pet.training_days or 0, lang=lang)
        except Exception:
            await cb.message.edit_text(
                t("ai.fallback", lang),
                reply_markup=_ai_error_kb("menu_ai_progress", lang),
                parse_mode="HTML",
            )
            return
        header = t("ai.progress.premium.header", lang, name=pet.name)
    else:
        if not await rate_limiter.is_allowed(cb.from_user.id):
            await cb.message.edit_text(
                t("ai.rate_limit", lang), reply_markup=_rate_limit_kb(lang), parse_mode="HTML"
            )
            return
        await cb.message.edit_text(t("ai.analyzing.free", lang), parse_mode="HTML")
        try:
            result = await a_svc.summarize_progress(pet, pet.training_days or 0, lang=lang)
        except Exception:
            await cb.message.edit_text(
                t("ai.fallback", lang),
                reply_markup=_ai_error_kb("menu_ai_progress", lang),
                parse_mode="HTML",
            )
            return
        await rate_limiter.increment(cb.from_user.id)
        header = t("ai.progress.free.header", lang, name=pet.name)

    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=t("ai.progress.back.btn", lang), callback_data="menu_stats"
                )
            ],
        ]
    )
    await cb.message.edit_text(header + result, reply_markup=kb, parse_mode="HTML")


# ─── coach ───────────────────────────────────────────────────────────────────


def _coach_hub_keyboard(lang: str) -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=t("coach.hub.archive_btn", lang), callback_data="coach_archive"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text=t("common.back_menu.btn", lang), callback_data="menu_main"
                )
            ],
        ]
    )


def _coach_reply_keyboard(lang: str) -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=t("coach.new_thread.btn", lang), callback_data="coach_archive"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text=t("common.back_menu.btn", lang), callback_data="menu_main"
                )
            ],
        ]
    )


async def _bg_generate_title(thread_id: int, question: str, session_fac, a_svc: AiService) -> None:
    try:
        title = await a_svc.generate_thread_title(question)
        async with session_fac() as session:
            thread = await session.get(CoachThreadModel, thread_id)
            if thread and not thread.title:
                thread.title = title
                await session.commit()
    except Exception:
        pass


async def _bg_refresh_summary(thread_id: int, session_fac, a_svc: AiService) -> None:
    try:
        async with session_fac() as session:
            thread = await session.get(CoachThreadModel, thread_id)
            if thread:
                summary = await a_svc.refresh_thread_summary(
                    thread.messages_json or [], thread.summary
                )
                if summary:
                    thread.summary = summary
                    await session.commit()
    except Exception:
        pass


@router.callback_query(F.data == "menu_coach")
@inject
async def ask_coach_hub(
    cb: types.CallbackQuery,
    state: FSMContext,
    u_svc: UserService = Provide[AppContainer.user_service],
    coach_thread_repo: CoachThreadRepository = Provide[AppContainer.coach_thread_repo],
) -> None:
    await cb.answer()

    data = await state.get_data()
    if "coach_history" in data:
        await state.update_data(coach_history=None)

    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)

    active_thread = None
    if usr.active_coach_thread_id:
        active_thread = await coach_thread_repo.get_by_id(usr.active_coach_thread_id)
        if active_thread and active_thread.status != "active":
            usr.active_coach_thread_id = None
            await u_svc.repo.session.commit()
            active_thread = None

    await state.set_state(CoachState.waiting_for_question)

    if active_thread:
        title = active_thread.title or t("coach.thread.title_default", lang)
        count = active_thread.message_count or 0
        text = t("coach.hub.active_thread", lang).format(title=title, count=count)
        kb = _coach_hub_keyboard(lang)
    else:
        text = t("coach.entry", lang)
        kb = get_back_keyboard(lang)

    await cb.message.edit_text(text, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data == "coach_archive")
@inject
async def coach_archive_thread(
    cb: types.CallbackQuery,
    state: FSMContext,
    u_svc: UserService = Provide[AppContainer.user_service],
    coach_thread_repo: CoachThreadRepository = Provide[AppContainer.coach_thread_repo],
) -> None:
    await cb.answer()
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)

    if usr.active_coach_thread_id:
        thread = await coach_thread_repo.get_by_id(usr.active_coach_thread_id)
        if thread:
            thread.status = "archived"
        usr.active_coach_thread_id = None
        await u_svc.repo.session.commit()

    await state.set_state(CoachState.waiting_for_question)
    await cb.message.edit_text(
        t("coach.thread.archived", lang) + "\n\n" + t("coach.entry", lang),
        reply_markup=get_back_keyboard(lang),
        parse_mode="HTML",
    )


@router.message(CoachState.waiting_for_question)
@inject
async def process_coach_question(
    msg: types.Message,
    state: FSMContext,
    u_svc: UserService = Provide[AppContainer.user_service],
    p_svc: PetService = Provide[AppContainer.pet_service],
    a_svc: AiService = Provide[AppContainer.ai_service],
    conv_repo: AiConversationRepository = Provide[AppContainer.ai_conversation_repo],
    rate_limiter: AiRateLimiter = Provide[AppContainer.ai_rate_limiter],
    coach_svc: CoachService = Provide[AppContainer.coach_service],
    session_fac=Provide[AppContainer.session_factory],
) -> None:
    if not msg.text or len(msg.text.strip()) < 2:
        return

    question = msg.text.strip()[:1000]

    usr = await u_svc.get_or_create_telegram_user(telegram_id=msg.from_user.id)
    lang = normalize_locale(usr.language_code)
    pet = await p_svc.get_pet(usr.id)
    if not pet:
        await state.clear()
        await msg.answer(t("error.no_pet", lang))
        return

    if not usr.is_premium and not await rate_limiter.is_allowed(msg.from_user.id):
        await state.clear()
        try:
            await msg.delete()
        except Exception:
            pass
        await msg.answer(
            t("ai.rate_limit", lang), reply_markup=_rate_limit_kb(lang), parse_mode="HTML"
        )
        return

    session = u_svc.repo.session

    thread = None
    if usr.active_coach_thread_id:
        thread = await coach_svc.repo.get_by_id(usr.active_coach_thread_id)
        if thread and thread.status != "active":
            thread = None
    if thread is None:
        thread = await coach_svc.repo.create(usr.id)
        usr.active_coach_thread_id = thread.id

    context = coach_svc.build_prompt_context(thread, usr.is_premium, lang)
    owner_label = t("coach.role.owner", lang)
    history_with_q = (context + "\n" if context else "") + f"{owner_label}: {question}\n"

    try:
        await msg.delete()
    except Exception:
        pass

    m = await msg.answer(t("coach.thinking", lang), parse_mode="HTML")
    try:
        answer = await a_svc.answer_coach_question(pet, history_with_q, lang=lang)
    except Exception:
        await m.edit_text(
            t("ai.fallback", lang), reply_markup=_ai_error_kb("menu_coach", lang), parse_mode="HTML"
        )
        return

    if not usr.is_premium:
        await rate_limiter.increment(msg.from_user.id)

    coach_svc.save_exchange(thread, question, answer)
    await session.commit()

    if coach_svc.should_generate_title(thread):
        asyncio.create_task(_bg_generate_title(thread.id, question, session_fac, a_svc))
    if coach_svc.should_refresh_summary(thread):
        asyncio.create_task(_bg_refresh_summary(thread.id, session_fac, a_svc))

    await conv_repo.create(
        user_id=usr.id,
        pet_id=pet.id,
        question=question,
        answer=answer,
        topic="coach",
    )

    await m.edit_text(answer, parse_mode="HTML", reply_markup=_coach_reply_keyboard(lang))


# ─── coach — photo (free, counts as 1 AI request) ────────────────────────────


@router.message(CoachState.waiting_for_question, F.photo)
@inject
async def process_coach_photo(
    msg: types.Message,
    state: FSMContext,
    u_svc: UserService = Provide[AppContainer.user_service],
    p_svc: PetService = Provide[AppContainer.pet_service],
    a_svc: AiService = Provide[AppContainer.ai_service],
    conv_repo: AiConversationRepository = Provide[AppContainer.ai_conversation_repo],
    rate_limiter: AiRateLimiter = Provide[AppContainer.ai_rate_limiter],
    coach_svc: CoachService = Provide[AppContainer.coach_service],
    session_fac=Provide[AppContainer.session_factory],
) -> None:
    usr = await u_svc.get_or_create_telegram_user(telegram_id=msg.from_user.id)
    lang = normalize_locale(usr.language_code)
    pet = await p_svc.get_pet(usr.id)
    if not pet:
        await state.clear()
        await msg.answer(t("error.no_pet", lang))
        return

    if not usr.is_premium and not await rate_limiter.is_allowed(msg.from_user.id):
        await state.clear()
        await msg.answer(
            t("ai.rate_limit", lang), reply_markup=_rate_limit_kb(lang), parse_mode="HTML"
        )
        return

    session = u_svc.repo.session
    caption = (msg.caption or "").strip()[:500] or None

    thread = None
    if usr.active_coach_thread_id:
        thread = await coach_svc.repo.get_by_id(usr.active_coach_thread_id)
        if thread and thread.status != "active":
            thread = None
    if thread is None:
        thread = await coach_svc.repo.create(usr.id)
        usr.active_coach_thread_id = thread.id

    context = coach_svc.build_prompt_context(thread, usr.is_premium, lang)

    m = await msg.answer(t("coach.media.thinking", lang), parse_mode="HTML")
    bio = io.BytesIO()
    await msg.bot.download(msg.photo[-1], destination=bio)
    try:
        answer = await a_svc.analyze_media_question(
            pet, bio.getvalue(), "image/jpeg", caption, context, lang=lang
        )
    except Exception:
        await m.edit_text(
            t("ai.fallback", lang), reply_markup=_ai_error_kb("menu_coach", lang), parse_mode="HTML"
        )
        return

    if not usr.is_premium:
        await rate_limiter.increment(msg.from_user.id)

    q_display = f"{t('coach.display.photo', lang)}{(' — ' + caption) if caption else ''}"
    coach_svc.save_exchange(thread, q_display, answer)
    await session.commit()

    if coach_svc.should_generate_title(thread):
        asyncio.create_task(_bg_generate_title(thread.id, q_display, session_fac, a_svc))

    await conv_repo.create(
        user_id=usr.id,
        pet_id=pet.id,
        question=q_display,
        answer=answer,
        topic="coach_media",
    )
    await m.edit_text(answer, parse_mode="HTML", reply_markup=_coach_reply_keyboard(lang))


# ─── coach — voice (Premium only) ────────────────────────────────────────────


@router.message(CoachState.waiting_for_question, F.voice)
@inject
async def process_coach_voice(
    msg: types.Message,
    state: FSMContext,
    u_svc: UserService = Provide[AppContainer.user_service],
    p_svc: PetService = Provide[AppContainer.pet_service],
    a_svc: AiService = Provide[AppContainer.ai_service],
    conv_repo: AiConversationRepository = Provide[AppContainer.ai_conversation_repo],
    coach_svc: CoachService = Provide[AppContainer.coach_service],
    session_fac=Provide[AppContainer.session_factory],
) -> None:
    usr = await u_svc.get_or_create_telegram_user(telegram_id=msg.from_user.id)
    lang = normalize_locale(usr.language_code)

    if not usr.is_premium:
        await msg.answer(
            t("coach.media.voice.premium", lang),
            reply_markup=_rate_limit_kb(lang),
            parse_mode="HTML",
        )
        return

    pet = await p_svc.get_pet(usr.id)
    if not pet:
        await state.clear()
        await msg.answer(t("error.no_pet", lang))
        return

    session = u_svc.repo.session

    thread = None
    if usr.active_coach_thread_id:
        thread = await coach_svc.repo.get_by_id(usr.active_coach_thread_id)
        if thread and thread.status != "active":
            thread = None
    if thread is None:
        thread = await coach_svc.repo.create(usr.id)
        usr.active_coach_thread_id = thread.id

    context = coach_svc.build_prompt_context(thread, usr.is_premium, lang)

    m = await msg.answer(t("coach.media.thinking", lang), parse_mode="HTML")
    bio = io.BytesIO()
    await msg.bot.download(msg.voice, destination=bio)
    try:
        answer = await a_svc.analyze_media_question(
            pet, bio.getvalue(), "audio/ogg", None, context, lang=lang
        )
    except Exception:
        await m.edit_text(
            t("ai.fallback", lang), reply_markup=_ai_error_kb("menu_coach", lang), parse_mode="HTML"
        )
        return

    voice_label = t("coach.display.voice", lang)
    coach_svc.save_exchange(thread, voice_label, answer)
    await session.commit()

    if coach_svc.should_generate_title(thread):
        asyncio.create_task(_bg_generate_title(thread.id, voice_label, session_fac, a_svc))

    await conv_repo.create(
        user_id=usr.id,
        pet_id=pet.id,
        question=voice_label,
        answer=answer,
        topic="coach_media",
    )
    await m.edit_text(answer, parse_mode="HTML", reply_markup=_coach_reply_keyboard(lang))


# ─── coach — video / video note (Premium only) ───────────────────────────────


@router.message(CoachState.waiting_for_question, F.video | F.video_note)
@inject
async def process_coach_video(
    msg: types.Message,
    state: FSMContext,
    u_svc: UserService = Provide[AppContainer.user_service],
    p_svc: PetService = Provide[AppContainer.pet_service],
    a_svc: AiService = Provide[AppContainer.ai_service],
    conv_repo: AiConversationRepository = Provide[AppContainer.ai_conversation_repo],
    coach_svc: CoachService = Provide[AppContainer.coach_service],
    session_fac=Provide[AppContainer.session_factory],
) -> None:
    usr = await u_svc.get_or_create_telegram_user(telegram_id=msg.from_user.id)
    lang = normalize_locale(usr.language_code)

    if not usr.is_premium:
        await msg.answer(
            t("coach.media.video.premium", lang),
            reply_markup=_rate_limit_kb(lang),
            parse_mode="HTML",
        )
        return

    pet = await p_svc.get_pet(usr.id)
    if not pet:
        await state.clear()
        await msg.answer(t("error.no_pet", lang))
        return

    file_obj = msg.video or msg.video_note
    if file_obj.file_size and file_obj.file_size > 20 * 1024 * 1024:
        await msg.answer(t("coach.media.too_large", lang))
        return

    session = u_svc.repo.session
    caption = (msg.caption or "").strip()[:500] or None

    thread = None
    if usr.active_coach_thread_id:
        thread = await coach_svc.repo.get_by_id(usr.active_coach_thread_id)
        if thread and thread.status != "active":
            thread = None
    if thread is None:
        thread = await coach_svc.repo.create(usr.id)
        usr.active_coach_thread_id = thread.id

    context = coach_svc.build_prompt_context(thread, usr.is_premium, lang)

    m = await msg.answer(t("coach.media.thinking", lang), parse_mode="HTML")
    bio = io.BytesIO()
    await msg.bot.download(file_obj, destination=bio)
    try:
        answer = await a_svc.analyze_media_question(
            pet, bio.getvalue(), "video/mp4", caption, context, lang=lang
        )
    except Exception:
        await m.edit_text(
            t("ai.fallback", lang), reply_markup=_ai_error_kb("menu_coach", lang), parse_mode="HTML"
        )
        return

    q_display = f"{t('coach.display.video', lang)}{(' — ' + caption) if caption else ''}"
    coach_svc.save_exchange(thread, q_display, answer)
    await session.commit()

    if coach_svc.should_generate_title(thread):
        asyncio.create_task(_bg_generate_title(thread.id, q_display, session_fac, a_svc))

    await conv_repo.create(
        user_id=usr.id,
        pet_id=pet.id,
        question=q_display,
        answer=answer,
        topic="coach_media",
    )
    await m.edit_text(answer, parse_mode="HTML", reply_markup=_coach_reply_keyboard(lang))


# ─── weekly plan ─────────────────────────────────────────────────────────────


@router.callback_query(F.data == "menu_week_plan")
@inject
async def show_week_plan(
    cb: types.CallbackQuery,
    state: FSMContext,
    u_svc: UserService = Provide[AppContainer.user_service],
    p_svc: PetService = Provide[AppContainer.pet_service],
    t_svc: TrainingService = Provide[AppContainer.training_service],
) -> None:
    await state.clear()
    await cb.answer()
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)
    pet = await p_svc.get_pet(usr.id)
    if not pet:
        await cb.message.edit_text(t("error.no_pet", lang), reply_markup=get_back_keyboard(lang))
        return
    await cb.message.edit_text(t("training.week.loading", lang, name=pet.name), parse_mode="HTML")
    try:
        plan = await t_svc.get_or_create_week(usr.id, pet, lang=lang)
    except Exception:
        await cb.message.edit_text(
            t("ai.fallback", lang),
            reply_markup=_ai_error_kb("menu_week_plan", lang),
            parse_mode="HTML",
        )
        return
    if not plan.tasks:
        await cb.message.edit_text(
            t("training.week.empty", lang),
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text=t("training.week.empty.cta.btn", lang),
                            callback_data="menu_training",
                        ),
                        types.InlineKeyboardButton(
                            text=t("common.menu.btn", lang), callback_data="menu_main"
                        ),
                    ]
                ]
            ),
            parse_mode="HTML",
        )
        return
    text = TrainingService.format_week_day(plan, 1, lang)
    await cb.message.edit_text(
        text,
        reply_markup=get_week_day_keyboard(plan.tasks, plan.id, 1, lang=lang),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("week_day:"))
@inject
async def navigate_week_day(
    cb: types.CallbackQuery,
    p_svc: PetService = Provide[AppContainer.pet_service],
    u_svc: UserService = Provide[AppContainer.user_service],
    t_svc: TrainingService = Provide[AppContainer.training_service],
) -> None:
    await cb.answer()
    _, plan_id_s, day_s = cb.data.split(":")
    plan_id, day = int(plan_id_s), int(day_s)

    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    pet = await p_svc.get_pet(usr.id)
    if not pet:
        return

    result = await t_svc.plan_repo.session.execute(
        select(TrainingPlanModel)
        .where(TrainingPlanModel.id == plan_id)
        .options(selectinload(TrainingPlanModel.tasks))
    )
    plan = result.scalar_one_or_none()
    if not plan:
        lang = normalize_locale(usr.language_code)
        await cb.message.edit_text(
            t("training.plan.not_found", lang), reply_markup=get_back_keyboard(lang)
        )
        return

    lang = normalize_locale(usr.language_code)
    text = TrainingService.format_week_day(plan, day, lang)
    await cb.message.edit_text(
        text,
        reply_markup=get_week_day_keyboard(plan.tasks, plan_id, day, lang=lang),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("week_task:"))
@inject
async def toggle_week_task(
    cb: types.CallbackQuery,
    p_svc: PetService = Provide[AppContainer.pet_service],
    u_svc: UserService = Provide[AppContainer.user_service],
    t_svc: TrainingService = Provide[AppContainer.training_service],
) -> None:
    parts = cb.data.split(":")
    _, task_id_s, plan_id_s, day_s = parts[:4]
    task_id, plan_id, day = int(task_id_s), int(plan_id_s), int(day_s)

    # New format (5 parts) encodes current state — answer immediately before any DB work
    answered = False
    if len(parts) >= 5:
        current_done = parts[4] == "1"
        toast_key = (
            "training.task.toggle.done" if not current_done else "training.task.toggle.undone"
        )
        await cb.answer(t(toast_key, normalize_locale(cb.from_user.language_code)))
        answered = True

    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    pet = await p_svc.get_pet(usr.id)
    if not pet:
        if not answered:
            await cb.answer()
        return

    task = await t_svc.plan_repo.get_task(task_id)
    if not task:
        if not answered:
            await cb.answer()
        return
    lang = normalize_locale(usr.language_code)
    task.is_completed = not task.is_completed
    if not answered:
        toast_key = (
            "training.task.toggle.done" if task.is_completed else "training.task.toggle.undone"
        )
        await cb.answer(t(toast_key, lang))
    task.completed_at = (
        datetime.now(datetime.UTC).replace(tzinfo=None) if task.is_completed else None
    )
    await t_svc.plan_repo.session.commit()

    day_done = await t_svc.plan_repo.day_tasks_done(plan_id, day)
    if day_done and task.is_completed:
        plan_meta = await t_svc.plan_repo.get_plan(plan_id)
        meta = plan_meta.plan_json or {}
        day_key = f"counted_day_{day}"
        if not meta.get(day_key):
            pet.training_days = (pet.training_days or 0) + 1
            plan_meta.plan_json = {**meta, day_key: date.today().isoformat()}
            await t_svc.plan_repo.session.commit()

    result = await t_svc.plan_repo.session.execute(
        select(TrainingPlanModel)
        .where(TrainingPlanModel.id == plan_id)
        .options(selectinload(TrainingPlanModel.tasks))
    )
    plan = result.scalar_one_or_none()
    if not plan:
        return

    lang = normalize_locale(usr.language_code)
    text = TrainingService.format_week_day(plan, day, lang)
    if day_done and task.is_completed:
        streak_n = pet.training_days or 1
        days_word = pluralize(
            streak_n,
            lang,
            one=t("menu.main.streak.days.one", lang),
            few=t("menu.main.streak.days.few", lang),
            many=t("menu.main.streak.days.many", lang),
            other=t("menu.main.streak.days.many", lang),
        )
        text += t(
            "training.week_done",
            lang,
            day=t(f"training.day.{day}", lang),
            emoji=_streak_emoji(streak_n),
            n=streak_n,
            days=days_word,
        )

    shop = (
        get_shop_button(pet, usr.is_premium, AFTER_COMPLETION)
        if (day_done and task.is_completed)
        else None
    )
    await cb.message.edit_text(
        text,
        reply_markup=get_week_day_keyboard(plan.tasks, plan_id, day, shop_btn=shop, lang=lang),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "refresh_week_confirm")
@inject
async def confirm_refresh_week(
    cb: types.CallbackQuery,
    u_svc: UserService = Provide[AppContainer.user_service],
) -> None:
    await cb.answer()
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=t("training.refresh.confirm.yes", lang), callback_data="refresh_week"
                ),
                types.InlineKeyboardButton(
                    text=t("training.refresh.confirm.no", lang), callback_data="menu_week_plan"
                ),
            ]
        ]
    )
    await cb.message.edit_text(
        t("training.week.refresh.confirm", lang),
        reply_markup=kb,
        parse_mode="HTML",
    )


@router.callback_query(F.data == "refresh_week")
@inject
async def refresh_week_plan(
    cb: types.CallbackQuery,
    u_svc: UserService = Provide[AppContainer.user_service],
    p_svc: PetService = Provide[AppContainer.pet_service],
    t_svc: TrainingService = Provide[AppContainer.training_service],
    rate_limiter: AiRateLimiter = Provide[AppContainer.ai_rate_limiter],
) -> None:
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)
    await cb.answer(t("training.refresh.toast", lang))
    pet = await p_svc.get_pet(usr.id)
    if not pet:
        return

    if not usr.is_premium and not await rate_limiter.is_allowed(cb.from_user.id):
        await cb.message.edit_text(
            t("ai.rate_limit", lang), reply_markup=_rate_limit_kb(lang), parse_mode="HTML"
        )
        return

    await t_svc.plan_repo.deactivate_for_pet(pet.id)
    await cb.message.edit_text(
        t("training.week.refresh.loading", lang, name=pet.name), parse_mode="HTML"
    )
    try:
        plan = await t_svc.get_or_create_week(usr.id, pet, lang=lang)
    except Exception:
        await cb.message.edit_text(
            t("ai.fallback", lang),
            reply_markup=_ai_error_kb("menu_week_plan", lang),
            parse_mode="HTML",
        )
        return
    if not usr.is_premium:
        await rate_limiter.increment(cb.from_user.id)
    text = TrainingService.format_week_day(plan, 1, lang)
    await cb.message.edit_text(
        text,
        reply_markup=get_week_day_keyboard(plan.tasks, plan.id, 1, lang=lang),
        parse_mode="HTML",
    )


# ─── explain exercise ─────────────────────────────────────────────────────────


@router.callback_query(F.data.startswith("expl_d:"))
@inject
async def explain_daily(
    cb: types.CallbackQuery,
    t_svc: TrainingService = Provide[AppContainer.training_service],
    a_svc: AiService = Provide[AppContainer.ai_service],
    u_svc: UserService = Provide[AppContainer.user_service],
    p_svc: PetService = Provide[AppContainer.pet_service],
    rate_limiter: AiRateLimiter = Provide[AppContainer.ai_rate_limiter],
) -> None:
    task_id = int(cb.data.split(":")[1])
    task = await t_svc.plan_repo.get_task(task_id)
    if not task:
        lang = normalize_locale(cb.from_user.language_code)
        await cb.answer(t("training.task.not_found", lang), show_alert=True)
        return
    await cb.answer()
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)
    if not usr.is_premium and not await rate_limiter.is_allowed(cb.from_user.id):
        await cb.message.edit_text(
            t("ai.rate_limit", lang), reply_markup=_rate_limit_kb(lang), parse_mode="HTML"
        )
        return
    await cb.message.edit_text(
        t("training.explain.loading", lang, title=task.title), parse_mode="HTML"
    )
    try:
        explanation = await a_svc.explain_exercise(task.title, task.description or "", lang=lang)
    except Exception:
        await cb.message.edit_text(
            t("ai.fallback", lang),
            reply_markup=_ai_error_kb("menu_training", lang),
            parse_mode="HTML",
        )
        return
    if not usr.is_premium:
        await rate_limiter.increment(cb.from_user.id)
    pet = await p_svc.get_pet(usr.id)
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=t("training.explain.back_daily.btn", lang), callback_data="menu_training"
                )
            ],
            *([[get_shop_button(pet, usr.is_premium, AFTER_EXERCISE)]] if pet else []),
        ]
    )
    await cb.message.edit_text(explanation, reply_markup=kb, parse_mode="HTML")


@router.callback_query(F.data.startswith("expl_w:"))
@inject
async def explain_weekly(
    cb: types.CallbackQuery,
    t_svc: TrainingService = Provide[AppContainer.training_service],
    a_svc: AiService = Provide[AppContainer.ai_service],
    u_svc: UserService = Provide[AppContainer.user_service],
    p_svc: PetService = Provide[AppContainer.pet_service],
    rate_limiter: AiRateLimiter = Provide[AppContainer.ai_rate_limiter],
) -> None:
    _, task_id_s, plan_id_s, day_s = cb.data.split(":")
    task_id, plan_id, day = int(task_id_s), int(plan_id_s), int(day_s)
    task = await t_svc.plan_repo.get_task(task_id)
    if not task:
        lang = normalize_locale(cb.from_user.language_code)
        await cb.answer(t("training.task.not_found", lang), show_alert=True)
        return
    await cb.answer()
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)
    if not usr.is_premium and not await rate_limiter.is_allowed(cb.from_user.id):
        await cb.message.edit_text(
            t("ai.rate_limit", lang), reply_markup=_rate_limit_kb(lang), parse_mode="HTML"
        )
        return
    await cb.message.edit_text(
        t("training.explain.loading", lang, title=task.title), parse_mode="HTML"
    )
    try:
        explanation = await a_svc.explain_exercise(task.title, task.description or "", lang=lang)
    except Exception:
        await cb.message.edit_text(
            t("ai.fallback", lang),
            reply_markup=_ai_error_kb(f"week_day:{plan_id}:{day}", lang),
            parse_mode="HTML",
        )
        return
    if not usr.is_premium:
        await rate_limiter.increment(cb.from_user.id)
    pet = await p_svc.get_pet(usr.id)
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=t("training.explain.back_weekly.btn", lang),
                    callback_data=f"week_day:{plan_id}:{day}",
                )
            ],
            *([[get_shop_button(pet, usr.is_premium, AFTER_EXERCISE)]] if pet else []),
        ]
    )
    await cb.message.edit_text(explanation, reply_markup=kb, parse_mode="HTML")


# ─── shop ────────────────────────────────────────────────────────────────────


@router.callback_query(F.data == "menu_shop")
@inject
async def show_shop(
    cb: types.CallbackQuery,
    state: FSMContext,
    u_svc: UserService = Provide[AppContainer.user_service],
) -> None:
    await state.clear()
    await cb.answer()
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=t("shop.cat.training.btn", lang), url=SHOP_URL_TRAINING
                )
            ],
            [
                types.InlineKeyboardButton(
                    text=t("shop.cat.longplay.btn", lang), url=SHOP_URL_LONGPLAY
                )
            ],
            [
                types.InlineKeyboardButton(
                    text=t("shop.cat.by_size.btn", lang), url=SHOP_URL_BY_SIZE
                )
            ],
            [types.InlineKeyboardButton(text=t("shop.cat.all.btn", lang), url=SHOP_URL_MAIN)],
            [
                types.InlineKeyboardButton(
                    text=t("common.back_menu.btn", lang), callback_data="menu_main"
                )
            ],
        ]
    )
    await cb.message.edit_text(
        f"{t('shop.title', lang)}\n\n{t('shop.body', lang)}",
        reply_markup=kb,
        parse_mode="HTML",
    )


# ─── invite / referral ───────────────────────────────────────────────────────


@router.callback_query(F.data == "menu_invite")
@inject
async def show_invite(
    cb: types.CallbackQuery,
    state: FSMContext,
    u_svc: UserService = Provide[AppContainer.user_service],
    ref_svc: ReferralService = Provide[AppContainer.referral_service],
) -> None:
    await state.clear()
    await cb.answer()
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)

    bot_info = await cb.bot.get_me()
    invite_link = f"https://t.me/{bot_info.username}?start=ref_{usr.telegram_id}"
    progress = await ref_svc.get_milestone_progress(usr.telegram_id)
    count = progress["count"]
    _sep = "─" * 25

    lines = [t("invite.title", lang), ""]
    lines.append(t("invite.count", lang, n=count))
    if progress["next_milestone"]:
        nm = progress["next_milestone"]
        lines.append(
            t(
                "invite.goal",
                lang,
                needed=progress["needed"],
                next_label=milestone_label(nm, lang),
                reward=milestone_reward(nm, lang),
            )
        )
    else:
        lines.append(t("invite.all_done", lang))

    lines += ["", _sep, t("invite.ladder.title", lang)]

    base_icon = "✅" if count >= 1 else "▶️"
    base_goal = f"  {t('invite.current_goal', lang)}" if count == 0 else ""
    lines.append(
        f"  {base_icon} " + t("invite.base_tier", lang, days=REFERRAL_BONUS_DAYS) + base_goal
    )

    for m in REFERRAL_MILESTONES:
        if count >= m["count"]:
            icon = "✅"
        elif (
            count >= 1
            and progress["next_milestone"]
            and m["count"] == progress["next_milestone"]["count"]
        ):
            icon = "▶️"
        else:
            icon = "⬜"
        goal_tag = f"  {t('invite.current_goal', lang)}" if icon == "▶️" else ""
        lines.append(f"  {icon} {milestone_label(m, lang)} — {milestone_reward(m, lang)}{goal_tag}")

    lines += [_sep, "", t("invite.link_label", lang), f"<code>{invite_link}</code>", ""]
    lines += [
        t("invite.how.title", lang),
        t("invite.how.1", lang),
        t("invite.how.2", lang),
        t("invite.how.3", lang, days=REFERRAL_BONUS_DAYS),
    ]

    share_text = urllib.parse.quote(t("invite.share.text", lang), safe="")
    share_url = (
        f"https://t.me/share/url?url={urllib.parse.quote(invite_link, safe='')}&text={share_text}"
    )
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text=t("invite.share.btn", lang), url=share_url)],
            [
                types.InlineKeyboardButton(
                    text=t("common.back_menu.btn", lang), callback_data="menu_main"
                )
            ],
        ]
    )
    await cb.message.edit_text("\n".join(lines), reply_markup=kb, parse_mode="HTML")


# ─── reminder settings ───────────────────────────────────────────────────────

_TIME_RE = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")


def _reminder_input_kb(lang: str = "ru") -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=t("reminder.back.btn", lang), callback_data="menu_reminder"
                ),
            ]
        ]
    )


def _reminder_kb(
    is_off: bool, lang: str = "ru", tz_missing: bool = False
) -> types.InlineKeyboardMarkup:
    rows = []
    if tz_missing:
        rows.append(
            [
                types.InlineKeyboardButton(
                    text=t("reminder.tz_change.btn", lang), callback_data="menu_edit_profile"
                )
            ]
        )
    if is_off:
        rows += [
            [
                types.InlineKeyboardButton(
                    text=t("reminder.enable.btn", lang), callback_data="reminder_enable"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text=t("reminder.back_settings.btn", lang), callback_data="menu_settings"
                )
            ],
        ]
    else:
        rows += [
            [
                types.InlineKeyboardButton(
                    text=t("reminder.change.btn", lang), callback_data="reminder_change"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text=t("reminder.disable.btn", lang), callback_data="reminder_disable"
                )
            ],
            [
                types.InlineKeyboardButton(
                    text=t("reminder.back_settings.btn", lang), callback_data="menu_settings"
                )
            ],
        ]
    return types.InlineKeyboardMarkup(inline_keyboard=rows)


@router.callback_query(F.data == "menu_reminder")
@inject
async def show_reminder_settings(
    cb: types.CallbackQuery,
    state: FSMContext,
    u_svc: UserService = Provide[AppContainer.user_service],
) -> None:
    await cb.answer()
    await state.clear()
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)
    rt = usr.reminder_time

    tz_missing = usr.timezone is None
    tz = usr.timezone or "UTC"
    if rt == "off":
        status = t("reminder.status.off", lang)
        desc = t("reminder.status.off.desc", lang)
    elif rt:
        status = t("reminder.status.on", lang, time=rt, tz=tz)
        desc = t("reminder.status.on.desc", lang)
    else:
        status = t("reminder.status.default", lang, tz=tz)
        desc = t("reminder.status.on.desc", lang)

    body = f"{t('reminder.title', lang)}\n\n{status}\n{desc}"
    if tz_missing:
        body += f"\n\n{t('reminder.tz_missing', lang)}"
    await cb.message.edit_text(
        body,
        reply_markup=_reminder_kb(rt == "off", lang, tz_missing=tz_missing),
        parse_mode="HTML",
    )


@router.callback_query(F.data.in_({"reminder_change", "reminder_enable"}))
@inject
async def start_reminder_input(
    cb: types.CallbackQuery,
    state: FSMContext,
    u_svc: UserService = Provide[AppContainer.user_service],
) -> None:
    await cb.answer()
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)
    tz = usr.timezone or "UTC"
    await state.set_state(ReminderState.waiting_for_time)
    prompt = t("reminder.input.prompt", lang, tz=tz)
    if usr.timezone is None:
        prompt += f"\n\n{t('reminder.tz_missing', lang)}"
    await cb.message.edit_text(
        prompt,
        reply_markup=_reminder_input_kb(lang),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "reminder_disable")
@inject
async def disable_reminder(
    cb: types.CallbackQuery,
    u_svc: UserService = Provide[AppContainer.user_service],
) -> None:
    await cb.answer()
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)
    usr.reminder_time = "off"
    await u_svc.repo.session.commit()
    await cb.message.edit_text(
        f"{t('reminder.title', lang)}\n\n{t('reminder.disabled', lang)}",
        reply_markup=_reminder_kb(is_off=True, lang=lang),
        parse_mode="HTML",
    )


@router.message(ReminderState.waiting_for_time)
@inject
async def set_reminder_time(
    msg: types.Message,
    state: FSMContext,
    u_svc: UserService = Provide[AppContainer.user_service],
) -> None:
    if not msg.text:
        return
    text = msg.text.strip()
    usr = await u_svc.get_or_create_telegram_user(telegram_id=msg.from_user.id)
    lang = normalize_locale(usr.language_code)
    if not _TIME_RE.match(text):
        await msg.answer(t("reminder.error.format", lang), parse_mode="HTML")
        return

    usr.reminder_time = text
    await u_svc.repo.session.commit()
    await state.clear()

    tz = usr.timezone or "UTC"
    await msg.answer(
        t("reminder.saved", lang, time=text, tz=tz),
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text=t("reminder.settings.btn", lang), callback_data="menu_reminder"
                    ),
                    types.InlineKeyboardButton(
                        text=t("reminder.menu.btn", lang), callback_data="menu_main"
                    ),
                ]
            ]
        ),
        parse_mode="HTML",
    )


# ─── language picker ─────────────────────────────────────────────────────────


@router.callback_query(F.data == "menu_language")
@inject
async def show_language_picker(
    cb: types.CallbackQuery,
    state: FSMContext,
    u_svc: UserService = Provide[AppContainer.user_service],
) -> None:
    await state.clear()
    await cb.answer()
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)
    await cb.message.edit_text(
        f"{t('settings.language.title', lang)}\n\n{t('settings.language.choose', lang)}",
        reply_markup=get_language_keyboard(lang),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("set_lang_"))
@inject
async def save_language(
    cb: types.CallbackQuery,
    u_svc: UserService = Provide[AppContainer.user_service],
) -> None:
    new_lang = cb.data.replace("set_lang_", "")
    # accept only known codes
    known = {code for code, _ in LANGUAGE_OPTIONS}
    if new_lang not in known:
        await cb.answer()
        return
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    usr.language_code = new_lang
    await u_svc.repo.session.commit()
    lang_name = next(name for code, name in LANGUAGE_OPTIONS if code == new_lang)
    await cb.message.edit_text(
        t("settings.language.saved", new_lang, name=lang_name),
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text=t("settings.btn", new_lang), callback_data="menu_settings"
                    ),
                    types.InlineKeyboardButton(
                        text=t("common.menu.btn", new_lang), callback_data="menu_main"
                    ),
                ]
            ]
        ),
        parse_mode="HTML",
    )
    await cb.answer()


# ─── hands-free voice-action (default state — no active FSM) ─────────────────


@router.message(
    StateFilter(default_state),
    (F.text & ~F.text.startswith("/")) | F.voice | F.photo,
)
@inject
async def handle_voice_action(
    msg: types.Message,
    u_svc: UserService = Provide[AppContainer.user_service],
    p_svc: PetService = Provide[AppContainer.pet_service],
    a_svc: AiService = Provide[AppContainer.ai_service],
    t_svc: TrainingService = Provide[AppContainer.training_service],
    conv_repo: AiConversationRepository = Provide[AppContainer.ai_conversation_repo],
    rate_limiter: AiRateLimiter = Provide[AppContainer.ai_rate_limiter],
    metrics: BotMetrics = Provide[AppContainer.metrics],
) -> None:
    usr = await u_svc.get_or_create_telegram_user(telegram_id=msg.from_user.id)
    lang = normalize_locale(usr.language_code)
    pet = await p_svc.get_pet(usr.id)
    if not pet:
        return

    if not usr.is_premium and not await rate_limiter.is_allowed(msg.from_user.id):
        try:
            await msg.delete()
        except Exception:
            pass
        await msg.answer(
            t("ai.rate_limit", lang), reply_markup=_rate_limit_kb(lang), parse_mode="HTML"
        )
        return

    # Determine content type and download media if needed
    media_bytes: bytes | None = None
    mime_type: str | None = None
    text_content: str | None = None
    is_media = bool(msg.voice or msg.photo)

    if msg.voice:
        bio = io.BytesIO()
        await msg.bot.download(msg.voice, destination=bio)
        media_bytes = bio.getvalue()
        mime_type = "audio/ogg"
    elif msg.photo:
        bio = io.BytesIO()
        await msg.bot.download(msg.photo[-1], destination=bio)
        media_bytes = bio.getvalue()
        mime_type = "image/jpeg"
        text_content = msg.caption
    else:
        text_content = (msg.text or "").strip()[:1000]
        if not text_content:
            return

    # Load today's task titles for AI context
    today_plan = await t_svc.plan_repo.get_active_today(pet.id)
    task_titles = [tk.title for tk in (today_plan.tasks if today_plan else [])]

    try:
        await msg.delete()
    except Exception:
        pass

    m = await msg.answer(t("voice_action.thinking", lang), parse_mode="HTML")

    try:
        intent = await a_svc.detect_training_intent(
            pet=pet,
            task_titles=task_titles,
            language_code=lang,
            text=text_content,
            media_bytes=media_bytes,
            mime_type=mime_type,
        )
    except Exception:
        await m.edit_text(
            t("ai.fallback", lang), reply_markup=_ai_error_kb("menu_main", lang), parse_mode="HTML"
        )
        return

    if not usr.is_premium:
        await rate_limiter.increment(msg.from_user.id)

    action = intent.get("action", "none")
    ai_message = (intent.get("message") or "").strip()

    if intent.get("_is_fallback"):
        await metrics.inc(BotMetrics.FALLBACK)

    if action == "mark_done" and task_titles:
        task, plan_done = await t_svc.mark_task_by_hint(pet, intent.get("task_hint", ""))
        if task:
            await metrics.inc(BotMetrics.MARK_DONE)
            reply = t("voice_action.marked", lang, task=task.title)
            if ai_message:
                reply += "\n\n" + ai_message
            if plan_done:
                reply += "\n\n" + t("voice_action.all_done", lang)
            updated_plan = await t_svc.plan_repo.get_active_today(pet.id)
            kb = (
                get_task_keyboard(updated_plan.tasks, lang=lang)
                if updated_plan
                else get_back_keyboard(lang)
            )
        else:
            reply = ai_message or t("voice_action.all_done", lang)
            kb = get_back_keyboard(lang)
    else:
        if is_media and not usr.is_premium:
            await metrics.inc(BotMetrics.PREMIUM_GATE)
            reply = t("coach.media.voice.premium", lang)
            kb = _rate_limit_kb(lang)
        else:
            reply = ai_message or t("ai.fallback", lang)
            kb = get_back_keyboard(lang)

    await m.edit_text(reply, parse_mode="HTML", reply_markup=kb)

    await conv_repo.create(
        user_id=usr.id,
        pet_id=pet.id,
        question=(text_content or f"[{mime_type}]")[:1000],
        answer=reply[:2000],
        topic="voice_action",
    )
