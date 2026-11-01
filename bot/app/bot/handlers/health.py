"""🩺 Health calendar: vaccines, ticks, worms. Two taps to log, pushes before the due date."""

import logging
from datetime import date

from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dependency_injector.wiring import Provide, inject

from app.bot.keyboards.main_menu import get_back_keyboard
from app.core.container import AppContainer
from app.core.tz_utils import local_now
from app.i18n import normalize_locale, t
from app.infrastructure.db.repositories.health_repo import HealthRepository
from app.services.health import (
    KINDS,
    latest_per_kind,
    next_due_after,
    parse_past_date,
    snooze_days,
    status_of,
)
from app.services.pet_service import PetService
from app.services.user_service import UserService

logger = logging.getLogger(__name__)
router = Router(name="health_router")

ICONS = {"vaccine": "💉", "ticks": "🕷", "worms": "🪱"}


class HealthState(StatesGroup):
    waiting_date = State()


def kind_label(kind: str, lang: str) -> str:
    return f"{ICONS[kind]} {t(f'health.kind.{kind}', lang)}"


def _fmt(d: date) -> str:
    return d.strftime("%d.%m.%Y")


def health_text(pet_name: str, events: list, today: date, lang: str) -> str:
    cur = latest_per_kind(events)
    lines = [t("health.title", lang, name=pet_name)]
    for kind in KINDS:
        ev = cur.get(kind)
        if ev is None:
            lines.append(t("health.row.none", lang, kind=kind_label(kind, lang)))
            continue
        status = status_of(ev.next_due_at, today)
        days = abs((ev.next_due_at - today).days)
        lines.append(
            t(
                f"health.row.{status}",
                lang,
                kind=kind_label(kind, lang),
                n=days,
                date=_fmt(ev.next_due_at),
            )
        )
    return "\n".join(lines)


def health_kb(lang: str) -> types.InlineKeyboardMarkup:
    rows = [
        [
            types.InlineKeyboardButton(text=kind_label(k, lang)[:14], callback_data=f"hl_add:{k}")
            for k in KINDS
        ],
        [
            types.InlineKeyboardButton(
                text=t("common.back_menu.btn", lang), callback_data="menu_main"
            )
        ],
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=rows)


async def _ctx(tg_id: int, u_svc: UserService, p_svc: PetService):
    usr = await u_svc.get_or_create_telegram_user(telegram_id=tg_id)
    lang = normalize_locale(usr.language_code)
    pet = await p_svc.get_pet(usr.id)
    return usr, lang, pet, local_now(usr.timezone).date()


async def _show(target: types.Message, pet, repo: HealthRepository, today: date, lang: str):
    events = await repo.for_pet(pet.id)
    await target.edit_text(
        health_text(pet.name, events, today, lang), reply_markup=health_kb(lang), parse_mode="HTML"
    )


@router.callback_query(F.data == "menu_health")
@inject
async def show_health(
    cb: types.CallbackQuery,
    state: FSMContext,
    u_svc: UserService = Provide[AppContainer.user_service],
    p_svc: PetService = Provide[AppContainer.pet_service],
    repo: HealthRepository = Provide[AppContainer.health_repo],
) -> None:
    await state.clear()
    await cb.answer()
    usr, lang, pet, today = await _ctx(cb.from_user.id, u_svc, p_svc)
    if not pet:
        await cb.message.edit_text(t("error.no_pet", lang), reply_markup=get_back_keyboard(lang))
        return
    await _show(cb.message, pet, repo, today, lang)


def _when_kb(kind: str, lang: str) -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=t("health.btn.today", lang), callback_data=f"hl_today:{kind}"
                ),
                types.InlineKeyboardButton(
                    text=t("health.btn.date", lang), callback_data=f"hl_date:{kind}"
                ),
            ],
            [
                types.InlineKeyboardButton(
                    text=t("health.btn.back", lang), callback_data="menu_health"
                )
            ],
        ]
    )


@router.callback_query(F.data.startswith("hl_add:"))
@inject
async def ask_when(
    cb: types.CallbackQuery,
    u_svc: UserService = Provide[AppContainer.user_service],
) -> None:
    await cb.answer()
    kind = cb.data.split(":", 1)[1]
    if kind not in KINDS:
        return
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)
    await cb.message.edit_text(
        t("health.add.prompt", lang, kind=kind_label(kind, lang)),
        reply_markup=_when_kb(kind, lang),
        parse_mode="HTML",
    )


async def _record(pet, kind: str, done_on: date, repo: HealthRepository):
    return await repo.add(pet.id, kind, done_on, next_due_after(kind, done_on))


@router.callback_query(F.data.startswith("hl_today:"))
@inject
async def log_today(
    cb: types.CallbackQuery,
    u_svc: UserService = Provide[AppContainer.user_service],
    p_svc: PetService = Provide[AppContainer.pet_service],
    repo: HealthRepository = Provide[AppContainer.health_repo],
) -> None:
    await cb.answer()
    kind = cb.data.split(":", 1)[1]
    usr, lang, pet, today = await _ctx(cb.from_user.id, u_svc, p_svc)
    if kind not in KINDS or not pet:
        return
    ev = await _record(pet, kind, today, repo)
    await cb.message.edit_text(
        t("health.saved", lang, kind=kind_label(kind, lang), date=_fmt(ev.next_due_at)),
        reply_markup=health_kb(lang),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("hl_date:"))
@inject
async def ask_date(
    cb: types.CallbackQuery,
    state: FSMContext,
    u_svc: UserService = Provide[AppContainer.user_service],
) -> None:
    await cb.answer()
    kind = cb.data.split(":", 1)[1]
    if kind not in KINDS:
        return
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    await state.update_data(health_kind=kind)
    await state.set_state(HealthState.waiting_date)
    await cb.message.edit_text(t("health.date.prompt", normalize_locale(usr.language_code)))


@router.message(StateFilter(HealthState.waiting_date), F.text)
@inject
async def save_date(
    msg: types.Message,
    state: FSMContext,
    u_svc: UserService = Provide[AppContainer.user_service],
    p_svc: PetService = Provide[AppContainer.pet_service],
    repo: HealthRepository = Provide[AppContainer.health_repo],
) -> None:
    usr, lang, pet, today = await _ctx(msg.from_user.id, u_svc, p_svc)
    kind = (await state.get_data()).get("health_kind")
    try:
        done_on = parse_past_date(msg.text, today)
    except ValueError:
        await msg.answer(t("health.date.invalid", lang))
        return
    if kind not in KINDS or not pet:
        await state.clear()
        return
    ev = await _record(pet, kind, done_on, repo)
    await state.clear()
    await msg.answer(
        t("health.saved", lang, kind=kind_label(kind, lang), date=_fmt(ev.next_due_at)),
        reply_markup=health_kb(lang),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("hl_done:"))
@inject
async def push_done(
    cb: types.CallbackQuery,
    u_svc: UserService = Provide[AppContainer.user_service],
    p_svc: PetService = Provide[AppContainer.pet_service],
    repo: HealthRepository = Provide[AppContainer.health_repo],
) -> None:
    usr, lang, pet, today = await _ctx(cb.from_user.id, u_svc, p_svc)
    try:
        event_id = int(cb.data.split(":", 1)[1])
    except ValueError:
        await cb.answer()
        return
    ev = await repo.get_owned(event_id, usr.id)
    if ev is None or ev.kind not in KINDS:
        await cb.answer()
        return
    new = await _record(pet, ev.kind, today, repo)
    await cb.answer("✅")
    await cb.message.edit_text(
        t("health.saved", lang, kind=kind_label(ev.kind, lang), date=_fmt(new.next_due_at)),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("hl_snooze:"))
@inject
async def push_snooze(
    cb: types.CallbackQuery,
    u_svc: UserService = Provide[AppContainer.user_service],
    repo: HealthRepository = Provide[AppContainer.health_repo],
) -> None:
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)
    try:
        event_id = int(cb.data.split(":", 1)[1])
    except ValueError:
        await cb.answer()
        return
    ev = await repo.get_owned(event_id, usr.id)
    if ev is None:
        await cb.answer()
        return
    await repo.snooze(ev, snooze_days())
    await cb.answer()
    await cb.message.edit_text(t("health.snoozed", lang, date=_fmt(ev.next_due_at)))
