"""🎁 Gift Premium to a friend who already uses the bot (one-time packs only)."""

import logging

from aiogram import F, Router, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dependency_injector.wiring import Provide, inject

from app.core.container import AppContainer
from app.core.context import current_tg_id
from app.i18n import normalize_locale, t
from app.infrastructure.db.repositories.user_repo import UserRepository
from app.infrastructure.redis.funnel import track_soon
from app.services.gifts import make_gift_payload
from app.services.products import PRODUCTS, get_product
from app.services.user_service import UserService

logger = logging.getLogger(__name__)
router = Router(name="gift_router")


class GiftState(StatesGroup):
    waiting_recipient = State()


def giftable() -> list:
    return [p for p in PRODUCTS.values() if not p.recurring]


@router.callback_query(F.data == "gift_start")
@inject
async def start_gift(
    cb: types.CallbackQuery,
    state: FSMContext,
    u_svc: UserService = Provide[AppContainer.user_service],
) -> None:
    await cb.answer()
    await state.clear()
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)
    rows = [
        [
            types.InlineKeyboardButton(
                text=t(f"premium.plan.{p.code}.btn", lang, stars=p.stars),
                callback_data=f"gift_pick:{p.code}",
            )
        ]
        for p in giftable()
    ]
    rows.append(
        [
            types.InlineKeyboardButton(
                text=t("common.back_menu.btn", lang), callback_data="menu_premium"
            )
        ]
    )
    await cb.message.edit_text(
        t("gift.choose", lang), reply_markup=types.InlineKeyboardMarkup(inline_keyboard=rows)
    )


@router.callback_query(F.data.startswith("gift_pick:"))
@inject
async def pick_product(
    cb: types.CallbackQuery,
    state: FSMContext,
    u_svc: UserService = Provide[AppContainer.user_service],
) -> None:
    await cb.answer()
    code = cb.data.split(":", 1)[1]
    product = get_product(code)
    if product is None or product.recurring:  # only one-time packs can be gifted
        return
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    await state.update_data(gift_code=product.code)
    await state.set_state(GiftState.waiting_recipient)
    await cb.message.edit_text(t("gift.ask_username", normalize_locale(usr.language_code)))


@router.message(StateFilter(GiftState.waiting_recipient), F.text)
@inject
async def receive_recipient(
    msg: types.Message,
    state: FSMContext,
    u_svc: UserService = Provide[AppContainer.user_service],
    user_repo: UserRepository = Provide[AppContainer.user_repo],
) -> None:
    usr = await u_svc.get_or_create_telegram_user(telegram_id=msg.from_user.id)
    lang = normalize_locale(usr.language_code)
    raw = (msg.text or "").strip()
    if not raw or raw.startswith("/"):
        await msg.answer(t("gift.ask_username", lang))
        return
    product = get_product((await state.get_data()).get("gift_code"))
    if product is None or product.recurring:
        await state.clear()
        return
    recipient = await user_repo.get_by_username(raw)
    if recipient is None:
        await msg.answer(t("gift.notfound", lang))
        return
    if recipient.telegram_id == msg.from_user.id:
        await msg.answer(t("gift.self", lang))
        return
    await state.clear()
    track_soon("invoice", current_tg_id.get())
    await msg.answer_invoice(
        title=t("gift.invoice.title", lang),
        description=t(
            "gift.invoice.description", lang, name=recipient.first_name or raw, days=product.days
        ),
        payload=make_gift_payload(product.code, recipient.telegram_id),
        provider_token="",  # Telegram Stars
        currency="XTR",
        prices=[types.LabeledPrice(label=t("gift.invoice.title", lang), amount=product.stars)],
    )
