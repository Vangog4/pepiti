"""📤 Story cards: streak, badge, weekly summary, dog passport. Sent as a document so the
2x PNG is not recompressed by Telegram."""

import asyncio
import logging

from aiogram import F, Router, types
from dependency_injector.wiring import Provide, inject

from app.bot.keyboards.edit_profile import translate_option
from app.cards import data as card_data
from app.cards.render import render_card
from app.core.container import AppContainer
from app.core.tz_utils import local_now
from app.i18n import normalize_locale, t
from app.infrastructure.db.repositories.activity_repo import ActivityRepository
from app.infrastructure.db.repositories.health_repo import HealthRepository
from app.infrastructure.db.repositories.pet_fact_repo import PetFactRepository
from app.services.entitlements import has_premium
from app.services.passport_pdf import MAX_FACTS, generate_passport_pdf, passport_pdf_data
from app.services.pet_service import PetService
from app.services.tracker import snapshot
from app.services.user_service import UserService

logger = logging.getLogger(__name__)
router = Router(name="cards_router")

KINDS = ("streak", "badge", "week", "passport")


def build_payload(kind: str, pet, snap: dict, lang: str) -> tuple[str, dict] | None:
    """(renderer kind, data) or None when there is nothing worth sharing yet."""
    if kind == "streak":
        return (
            ("streak", card_data.streak_card(pet.name, snap["streak"], lang))
            if snap["streak"]
            else None
        )
    if kind == "badge":
        code = card_data.top_badge(snap["badges"])
        return ("badge", card_data.badge_card(code, pet.name, lang)) if code else None
    if kind == "week":
        wk = snap["week"]
        if not (wk.task_days or wk.walk_count):
            return None
        return ("week", card_data.week_card(pet.name, wk, snap["streak"], lang))
    if kind == "passport":
        age = translate_option(pet.age_category, lang) or ""
        return ("passport", card_data.passport_card(pet, age, lang))
    return None


@router.callback_query(F.data.startswith("card:"))
@inject
async def send_card(
    cb: types.CallbackQuery,
    u_svc: UserService = Provide[AppContainer.user_service],
    p_svc: PetService = Provide[AppContainer.pet_service],
    repo: ActivityRepository = Provide[AppContainer.activity_repo],
) -> None:
    kind = cb.data.split(":", 1)[1]
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)
    pet = await p_svc.get_pet(usr.id)
    if kind not in KINDS or not pet:
        await cb.answer()
        return
    today = local_now(usr.timezone).date()
    snap = snapshot(await repo.rows(pet.id, today), today, has_premium(usr))
    payload = build_payload(kind, pet, snap, lang)
    if payload is None:
        await cb.answer(t("card.nothing", lang), show_alert=True)
        return
    await cb.answer(t("card.drawing", lang))
    try:
        png = await render_card(*payload)
    except Exception:
        logger.exception("card render failed kind=%s", kind)
        await cb.message.answer(t("card.error", lang))
        return
    await cb.message.answer_document(
        types.BufferedInputFile(png, filename=f"pepito-{kind}.png"),
        caption=t("card.caption", lang),
    )


@router.callback_query(F.data == "pf_pdf")
@inject
async def send_passport_pdf(
    cb: types.CallbackQuery,
    u_svc: UserService = Provide[AppContainer.user_service],
    p_svc: PetService = Provide[AppContainer.pet_service],
    health: HealthRepository = Provide[AppContainer.health_repo],
    facts: PetFactRepository = Provide[AppContainer.pet_fact_repo],
) -> None:
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)
    pet = await p_svc.get_pet(usr.id)  # always the caller's own dog
    if not pet:
        await cb.answer()
        return
    await cb.answer(t("pdf.drawing", lang))
    try:
        data = passport_pdf_data(
            pet,
            await health.for_pet(pet.id),
            [f.fact for f in await facts.list_active(pet.id, MAX_FACTS)],
            local_now(usr.timezone).date(),
        )
        pdf = await asyncio.to_thread(generate_passport_pdf, data, lang)
    except Exception:
        logger.exception("passport pdf failed")
        await cb.message.answer(t("card.error", lang))
        return
    await cb.message.answer_document(
        types.BufferedInputFile(pdf, filename=f"pepito-passport-{pet.id}.pdf"),
        caption=t("pdf.caption", lang),
    )
