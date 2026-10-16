import logging

from aiogram import F, Router, types
from dependency_injector.wiring import Provide, inject
from sqlalchemy import update

from app.bot.keyboards.main_menu import get_back_keyboard
from app.core.container import AppContainer
from app.i18n import normalize_locale, t
from app.infrastructure.db.models.user import UserModel
from app.infrastructure.db.repositories.subscription_repo import SubscriptionRepository
from app.services.subscription_service import PREMIUM_1M_STARS, SubscriptionService
from app.services.user_service import UserService

logger = logging.getLogger(__name__)
router = Router(name="subscription_router")


async def send_premium_invoice(target: types.Message, lang: str) -> None:
    """Send Stars invoice. Used by bot button and WebApp deep-link /start premium."""
    await target.answer_invoice(
        title=t("premium.invoice.title", lang),
        description=t("premium.invoice.description", lang),
        payload="premium_1m",
        provider_token="",  # empty string = Telegram Stars (XTR)
        currency="XTR",
        prices=[
            types.LabeledPrice(label=t("premium.invoice.label", lang), amount=PREMIUM_1M_STARS)
        ],
    )


@router.callback_query(F.data == "menu_premium")
@inject
async def show_premium(
    cb: types.CallbackQuery,
    u_svc: UserService = Provide[AppContainer.user_service],
    sub_svc: SubscriptionService = Provide[AppContainer.subscription_service],
) -> None:
    await cb.answer()
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)

    if usr.is_premium:
        sub = await sub_svc.get_active(usr.id)
        expires = sub.expires_at.strftime("%d.%m.%Y") if sub else "—"
        await cb.message.edit_text(
            f"{t('premium.active.title', lang)}\n\n"
            f"{t('premium.active.expires', lang, date=expires)}"
            f"{t('premium.active.features', lang)}",
            reply_markup=get_back_keyboard(lang),
            parse_mode="HTML",
        )
        return

    await cb.message.edit_text(
        t("premium.upsell.body", lang, price=PREMIUM_1M_STARS),
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text=t("premium.upsell.btn", lang, price=PREMIUM_1M_STARS),
                        callback_data="buy_premium",
                    )
                ],
                [
                    types.InlineKeyboardButton(
                        text=t("common.back_menu.btn", lang), callback_data="menu_main"
                    )
                ],
            ]
        ),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "buy_premium")
@inject
async def send_invoice(
    cb: types.CallbackQuery,
    u_svc: UserService = Provide[AppContainer.user_service],
) -> None:
    await cb.answer()
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)
    await send_premium_invoice(cb.message, lang)


@router.pre_checkout_query()
async def pre_checkout(pcq: types.PreCheckoutQuery) -> None:
    # Only accept known premium invoice payloads
    if pcq.invoice_payload != "premium_1m":
        await pcq.answer(ok=False, error_message="Unknown product")
        return
    if pcq.currency != "XTR":
        await pcq.answer(ok=False, error_message="Invalid currency")
        return
    await pcq.answer(ok=True)


@router.message(F.successful_payment)
@inject
async def successful_payment(
    msg: types.Message,
    u_svc: UserService = Provide[AppContainer.user_service],
    sub_svc: SubscriptionService = Provide[AppContainer.subscription_service],
) -> None:
    payment = msg.successful_payment
    if payment.invoice_payload != "premium_1m":
        logger.warning(
            "Ignoring successful_payment with payload=%s user=%s",
            payment.invoice_payload,
            msg.from_user.id,
        )
        return

    usr = await u_svc.get_or_create_telegram_user(telegram_id=msg.from_user.id)
    await sub_svc.activate(
        user_id=usr.id,
        telegram_id=msg.from_user.id,
        charge_id=payment.telegram_payment_charge_id,
    )
    logger.info(
        "Premium activated for user %s (charge %s)",
        msg.from_user.id,
        payment.telegram_payment_charge_id,
    )
    lang = normalize_locale(usr.language_code)
    await msg.answer(t("premium.activated", lang), parse_mode="HTML")


@router.message(F.refunded_payment)
@inject
async def refunded_payment(
    msg: types.Message,
    sub_repo: SubscriptionRepository = Provide[AppContainer.subscription_repo],
) -> None:
    charge_id = msg.refunded_payment.telegram_payment_charge_id
    logger.info("Refund received for charge %s (user %s)", charge_id, msg.from_user.id)

    sub = await sub_repo.get_by_charge_id(charge_id)
    if not sub:
        logger.warning("Refund: subscription not found for charge %s", charge_id)
        return

    sub.status = "refunded"
    await sub_repo.session.flush()
    # Keep premium if another valid active sub remains (referral stack, etc.)
    still = await sub_repo.get_active(sub.user_id)
    if still:
        await sub_repo.session.execute(
            update(UserModel)
            .where(UserModel.id == sub.user_id)
            .values(is_premium=True, subscription_expires_at=still.expires_at)
        )
    else:
        await sub_repo.session.execute(
            update(UserModel)
            .where(UserModel.id == sub.user_id)
            .values(is_premium=False, subscription_expires_at=None)
        )
    await sub_repo.session.commit()

    logger.info("Premium recalculated for user_id=%s after refund", sub.user_id)
    lang = normalize_locale(msg.from_user.language_code)
    await msg.answer(t("premium.refunded", lang), parse_mode="HTML")
