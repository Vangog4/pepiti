import logging

from aiogram import F, Router, types
from aiogram.filters import Command
from dependency_injector.wiring import Provide, inject
from sqlalchemy import update

from app.bot.keyboards.main_menu import get_back_keyboard
from app.core.config import settings
from app.core.container import AppContainer
from app.core.context import current_tg_id
from app.i18n import normalize_locale, t
from app.infrastructure.db.models.user import UserModel
from app.infrastructure.db.repositories.subscription_repo import SubscriptionRepository
from app.infrastructure.redis.funnel import track_soon
from app.services.entitlements import has_premium
from app.services.products import PRODUCTS, STARS_SUBSCRIPTION_PERIOD, get_product
from app.services.subscription_service import SubscriptionService
from app.services.user_service import UserService

logger = logging.getLogger(__name__)
router = Router(name="subscription_router")


async def send_premium_invoice(
    target: types.Message, lang: str, product_code: str = "premium_1m"
) -> None:
    """Send a Stars invoice for ``product_code`` (also the WebApp deep-link /start premium).

    The monthly plan is a native auto-renewing Stars subscription; longer packs are one-off.
    """
    product = get_product(product_code)
    if product is None:
        return
    track_soon("invoice", current_tg_id.get())
    prices = [types.LabeledPrice(label=t("premium.invoice.label", lang), amount=product.stars)]
    title = t("premium.invoice.title", lang)
    description = t("premium.invoice.description", lang)
    if product.recurring:
        link = await target.bot.create_invoice_link(
            title=title,
            description=description,
            payload=product.code,
            provider_token="",  # empty = Telegram Stars (XTR)
            currency="XTR",
            prices=prices,
            subscription_period=STARS_SUBSCRIPTION_PERIOD,
        )
        await target.answer(
            title,
            reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[[types.InlineKeyboardButton(text=f"⭐ {product.stars}", url=link)]]
            ),
        )
        return
    await target.answer_invoice(
        title=title,
        description=description,
        payload=product.code,
        provider_token="",
        currency="XTR",
        prices=prices,
    )


def _plans_keyboard(lang: str) -> types.InlineKeyboardMarkup:
    rows = [
        [
            types.InlineKeyboardButton(
                text=t(f"premium.plan.{p.code}.btn", lang, stars=p.stars),
                callback_data=f"buy:{p.code}",
            )
        ]
        for p in PRODUCTS.values()
    ]
    rows.append(
        [
            types.InlineKeyboardButton(
                text=t("common.back_menu.btn", lang), callback_data="menu_main"
            )
        ]
    )
    return types.InlineKeyboardMarkup(inline_keyboard=rows)


@router.callback_query(F.data == "menu_premium")
@inject
async def show_premium(
    cb: types.CallbackQuery,
    u_svc: UserService = Provide[AppContainer.user_service],
    sub_svc: SubscriptionService = Provide[AppContainer.subscription_service],
) -> None:
    await cb.answer()
    track_soon("plans", cb.from_user.id)
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)

    if has_premium(usr):
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
        t("premium.upsell.body", lang, price=PRODUCTS["premium_1m"].stars),
        reply_markup=_plans_keyboard(lang),
        parse_mode="HTML",
    )


@router.callback_query(F.data.in_({"buy_premium"}) | F.data.startswith("buy:"))
@inject
async def send_invoice(
    cb: types.CallbackQuery,
    u_svc: UserService = Provide[AppContainer.user_service],
) -> None:
    await cb.answer()
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)
    code = cb.data.split(":", 1)[1] if cb.data.startswith("buy:") else "premium_1m"
    await send_premium_invoice(cb.message, lang, code)


@router.pre_checkout_query()
async def pre_checkout(pcq: types.PreCheckoutQuery) -> None:
    # Only accept known premium invoice payloads
    product = get_product(pcq.invoice_payload)
    if product is None:
        await pcq.answer(ok=False, error_message="Unknown product")
        return
    if pcq.currency != "XTR":
        await pcq.answer(ok=False, error_message="Invalid currency")
        return
    if pcq.total_amount != product.stars:
        await pcq.answer(ok=False, error_message="Invalid amount")
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
    product = get_product(payment.invoice_payload)
    if product is None:
        logger.warning(
            "Ignoring successful_payment with payload=%s user=%s",
            payment.invoice_payload,
            msg.from_user.id,
        )
        return

    usr = await u_svc.get_or_create_telegram_user(telegram_id=msg.from_user.id)
    track_soon("paid", msg.from_user.id)
    await sub_svc.activate(
        user_id=usr.id,
        telegram_id=msg.from_user.id,
        charge_id=payment.telegram_payment_charge_id,
        days=product.days,
        plan_code=product.code,
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


@router.message(Command("paysupport"))
async def cmd_paysupport(msg: types.Message) -> None:
    lang = normalize_locale(msg.from_user.language_code)
    text = t("premium.paysupport", lang)
    contact = (settings.SUPPORT_CONTACT or "").strip()
    if contact:
        text += f"\n\n{contact}"
    await msg.answer(text, parse_mode="HTML")


@router.message(Command("terms"))
async def cmd_terms(msg: types.Message) -> None:
    lang = normalize_locale(msg.from_user.language_code)
    await msg.answer(t("premium.terms", lang), parse_mode="HTML")
