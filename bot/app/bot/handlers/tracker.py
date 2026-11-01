"""🔥 Tracker: real streak (local dates, with freezes), walks, badges, week summary."""

import logging

from aiogram import F, Router, types
from dependency_injector.wiring import Provide, inject

from app.bot.keyboards.main_menu import get_back_keyboard
from app.core.container import AppContainer
from app.core.tz_utils import local_now
from app.i18n import normalize_locale, t
from app.infrastructure.db.repositories.activity_repo import ActivityRepository
from app.logic.rules import rule
from app.services.entitlements import has_premium
from app.services.pet_service import PetService
from app.services.tracker import achievements, new_achievements, snapshot
from app.services.user_service import UserService

logger = logging.getLogger(__name__)
router = Router(name="tracker_router")


def walk_minutes() -> list[int]:
    return [int(x) for x in rule("tracker.walk_minutes", [15, 30, 60])]


def badge_line(code: str, lang: str) -> str:
    return t(f"tracker.badge.{code}", lang)


def tracker_text(name: str, snap: dict, lang: str) -> str:
    wk = snap["week"]
    lines = [t("tracker.title", lang, name=name)]
    lines.append(
        t("tracker.streak", lang, n=snap["streak"])
        if snap["streak"]
        else t("tracker.streak.zero", lang)
    )
    lines.append(t("tracker.today.done" if snap["done_today"] else "tracker.today.todo", lang))
    lines.append(t("tracker.freezes", lang, n=snap["freezes_left"]))
    lines.append(
        t("tracker.week", lang, days=wk.task_days, walks=wk.walk_count, minutes=wk.walk_minutes)
    )
    if snap["badges"]:
        lines.append(
            t(
                "tracker.badges",
                lang,
                list=" ".join(badge_line(b, lang) for b in sorted(snap["badges"])),
            )
        )
    return "\n".join(lines)


def tracker_kb(lang: str) -> types.InlineKeyboardMarkup:
    walks = [
        types.InlineKeyboardButton(
            text=t("tracker.walk.btn", lang, m=m), callback_data=f"tr_walk:{m}"
        )
        for m in walk_minutes()
    ]
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            walks,
            [
                types.InlineKeyboardButton(
                    text=t("common.back_menu.btn", lang), callback_data="menu_main"
                )
            ],
        ]
    )


async def record_task_day(repo: ActivityRepository, pet, usr) -> list[str]:
    """Mark today's training day as done (idempotent). Returns newly earned badges."""
    today = local_now(usr.timezone).date()
    before = achievements({r.local_date for r in await repo.rows(pet.id, today)}, 0)
    if not await repo.log_task_day(pet.id, today):
        return []
    rows = await repo.rows(pet.id, today)
    after = achievements({r.local_date for r in rows}, sum(1 for r in rows if r.kind == "walk"))
    return new_achievements(before, after)


async def streak_for(repo: ActivityRepository, pet, usr) -> int:
    today = local_now(usr.timezone).date()
    return snapshot(await repo.rows(pet.id, today), today, has_premium(usr))["streak"]


@router.callback_query(F.data == "menu_tracker")
@inject
async def show_tracker(
    cb: types.CallbackQuery,
    u_svc: UserService = Provide[AppContainer.user_service],
    p_svc: PetService = Provide[AppContainer.pet_service],
    repo: ActivityRepository = Provide[AppContainer.activity_repo],
) -> None:
    await cb.answer()
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)
    pet = await p_svc.get_pet(usr.id)
    if not pet:
        await cb.message.edit_text(t("error.no_pet", lang), reply_markup=get_back_keyboard(lang))
        return
    today = local_now(usr.timezone).date()
    snap = snapshot(await repo.rows(pet.id, today), today, has_premium(usr))
    await cb.message.edit_text(
        tracker_text(pet.name, snap, lang), reply_markup=tracker_kb(lang), parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("tr_walk:"))
@inject
async def log_walk(
    cb: types.CallbackQuery,
    u_svc: UserService = Provide[AppContainer.user_service],
    p_svc: PetService = Provide[AppContainer.pet_service],
    repo: ActivityRepository = Provide[AppContainer.activity_repo],
) -> None:
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)
    pet = await p_svc.get_pet(usr.id)
    try:
        minutes = int(cb.data.split(":", 1)[1])
    except ValueError:
        await cb.answer()
        return
    if not pet or minutes not in walk_minutes():  # only the offered values are accepted
        await cb.answer()
        return
    today = local_now(usr.timezone).date()
    rows = await repo.rows(pet.id, today)
    before = achievements({r.local_date for r in rows}, sum(1 for r in rows if r.kind == "walk"))
    await repo.log_walk(pet.id, today, minutes)
    rows = await repo.rows(pet.id, today)
    after = achievements({r.local_date for r in rows}, sum(1 for r in rows if r.kind == "walk"))
    await cb.answer(t("tracker.walk.saved", lang, m=minutes))
    snap = snapshot(rows, today, has_premium(usr))
    text = tracker_text(pet.name, snap, lang)
    for code in new_achievements(before, after):
        text += "\n\n" + t("tracker.badge.new", lang, badge=badge_line(code, lang))
    await cb.message.edit_text(text, reply_markup=tracker_kb(lang), parse_mode="HTML")
