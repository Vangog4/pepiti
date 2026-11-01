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
from app.infrastructure.db.repositories.user_repo import UserRepository
from app.infrastructure.redis.funnel import track_soon
from app.services import rub
from app.services.entitlements import has_premium
from app.services.gifts import parse_payload, target_telegram_id
from app.services.pricing import allowed_stars, stars_for, variant_for
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
    user_id = current_tg_id.get() or getattr(getattr(target, "chat", None), "id", None)
    stars = stars_for(product, variant_for(user_id))
    prices = [types.LabeledPrice(label=t("premium.invoice.label", lang), amount=stars)]
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
                inline_keyboard=[[types.InlineKeyboardButton(text=f"⭐ {stars}", url=link)]]
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


async def send_rub_invoice(
    target: types.Message, lang: str, product_code: str = "premium_1m"
) -> None:
    """Rubles via T-Bank (Telegram Payments). No-op unless fully configured (see rub.py)."""
    product = get_product(product_code)
    if product is None or not rub.rub_enabled():
        return
    title = t("premium.invoice.title", lang)
    provider_data = rub.render_provider_data(product, title)
    if provider_data is None:
        return
    track_soon("invoice", current_tg_id.get())
    await target.answer_invoice(
        title=title,
        description=t("premium.invoice.description", lang),
        payload=product.code,
        provider_token=settings.TBANK_PROVIDER_TOKEN,
        currency=rub.CURRENCY,
        prices=[
            types.LabeledPrice(label=t("premium.invoice.label", lang), amount=rub.kopecks(product))
        ],
        provider_data=provider_data,
    )


def _plans_keyboard(lang: str, user_id: int | None = None) -> types.InlineKeyboardMarkup:
    variant = variant_for(user_id)
    rows = [
        [
            types.InlineKeyboardButton(
                text=t(f"premium.plan.{p.code}.btn", lang, stars=stars_for(p, variant)),
                callback_data=f"buy:{p.code}",
            )
        ]
        for p in PRODUCTS.values()
    ]
    if lang == "ru" and rub.rub_enabled():
        rows += [
            [
                types.InlineKeyboardButton(
                    text=t(f"premium.rub.{p.code}.btn", lang, rub=p.rub),
                    callback_data=f"buyrub:{p.code}",
                )
            ]
            for p in PRODUCTS.values()
        ]
    rows.append([types.InlineKeyboardButton(text=t("gift.btn", lang), callback_data="gift_start")])
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
        t(
            "premium.upsell.body",
            lang,
            price=stars_for(PRODUCTS["premium_1m"], variant_for(cb.from_user.id)),
        ),
        reply_markup=_plans_keyboard(lang, cb.from_user.id),
        parse_mode="HTML",
    )


@router.callback_query(
    F.data.in_({"buy_premium"}) | F.data.startswith("buy:") | F.data.startswith("buyrub:")
)
@inject
async def send_invoice(
    cb: types.CallbackQuery,
    u_svc: UserService = Provide[AppContainer.user_service],
) -> None:
    await cb.answer()
    usr = await u_svc.get_or_create_telegram_user(telegram_id=cb.from_user.id)
    lang = normalize_locale(usr.language_code)
    code = cb.data.split(":", 1)[1] if ":" in cb.data else "premium_1m"
    if cb.data.startswith("buyrub:"):
        await send_rub_invoice(cb.message, lang, code)
        return
    await send_premium_invoice(cb.message, lang, code)


@router.pre_checkout_query()
@inject
async def pre_checkout(
    pcq: types.PreCheckoutQuery,
    user_repo: UserRepository = Provide[AppContainer.user_repo],
) -> None:
    """Telegram gives us 10 s: validate everything BEFORE the money moves."""
    parsed = parse_payload(pcq.invoice_payload)
    if parsed is None:
        await pcq.answer(ok=False, error_message="Unknown product")
        return
    if pcq.currency == rub.CURRENCY:
        # Rubles: one-off purchases of a catalog product only (never a gift), exact kopecks.
        if (
            not rub.rub_enabled()
            or parsed.is_gift
            or pcq.total_amount != rub.kopecks(parsed.product)
        ):
            await pcq.answer(ok=False, error_message="Invalid amount")
            return
        await pcq.answer(ok=True)
        return
    if pcq.currency != "XTR":
        await pcq.answer(ok=False, error_message="Invalid currency")
        return
    if pcq.total_amount not in allowed_stars(parsed.product):
        await pcq.answer(ok=False, error_message="Invalid amount")
        return
    if parsed.is_gift:
        if parsed.recipient_tg_id == pcq.from_user.id:
            await pcq.answer(ok=False, error_message="Cannot gift yourself")
            return
        if await user_repo.get_by_telegram_id(parsed.recipient_tg_id) is None:
            await pcq.answer(ok=False, error_message="Recipient not found")
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
    charge = payment.telegram_payment_charge_id
    parsed = parse_payload(payment.invoice_payload)
    if parsed is None:
        # Stars were taken but the payload is unknown: make it loud so it can be refunded.
        logger.error(
            "UNKNOWN PAID PAYLOAD %r user=%s charge=%s: refund manually",
            payment.invoice_payload,
            msg.from_user.id,
            charge,
        )
        return

    is_rub = payment.currency == rub.CURRENCY
    if is_rub and (
        not rub.rub_enabled()
        or parsed.is_gift
        or payment.total_amount != rub.kopecks(parsed.product)
    ):
        logger.error(
            "RUB payment REJECTED payload=%r amount=%s user=%s charge=%s provider_charge=%s: "
            "check with the provider / refund manually",
            payment.invoice_payload,
            payment.total_amount,
            msg.from_user.id,
            charge,
            getattr(payment, "provider_payment_charge_id", None),
        )
        return

    payer = await u_svc.get_or_create_telegram_user(telegram_id=msg.from_user.id)
    track_soon("paid", msg.from_user.id)
    target_tg = target_telegram_id(parsed, msg.from_user.id)
    target = (
        payer if target_tg == msg.from_user.id else await u_svc.repo.get_by_telegram_id(target_tg)
    )
    if target is None:
        logger.error(
            "gift paid but recipient %s is gone: payer=%s charge=%s: refund manually",
            target_tg,
            msg.from_user.id,
            charge,
        )
        return

    await sub_svc.activate(
        user_id=target.id,
        telegram_id=target_tg,
        charge_id=charge,
        days=parsed.product.days,
        plan_code=rub.rub_plan_code(parsed.product) if is_rub else parsed.product.code,
        provider=rub.PROVIDER if is_rub else "telegram_stars",
    )
    logger.info(
        "Premium activated for user %s (charge %s, gift=%s)", target_tg, charge, parsed.is_gift
    )
    payer_lang = normalize_locale(payer.language_code)
    if not parsed.is_gift:
        await msg.answer(t("premium.activated", payer_lang), parse_mode="HTML")
        return
    await msg.answer(
        t(
            "gift.sent",
            payer_lang,
            name=getattr(target, "first_name", None) or "",
            days=parsed.product.days,
        ),
        parse_mode="HTML",
    )
    try:
        await msg.bot.send_message(
            target_tg,
            t(
                "gift.received",
                normalize_locale(target.language_code),
                days=parsed.product.days,
                name=msg.from_user.first_name or "",
            ),
            parse_mode="HTML",
        )
    except Exception:
        logger.info("could not notify gift recipient %s", target_tg)


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
