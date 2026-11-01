"""Recover Stars payments whose ``successful_payment`` update never reached the bot.

Telegram keeps the full ledger (``getStarTransactions``); ``StarTransaction.id`` equals
``SuccessfulPayment.telegram_payment_charge_id``. Anything paid there but unknown to us is
granted retroactively. Activation is idempotent (UNIQUE charge id), so re-running is safe.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from app.i18n import normalize_locale, t
from app.infrastructure.redis.funnel import track_soon
from app.services.products import get_product

logger = logging.getLogger(__name__)

PAGE = 100


@dataclass(frozen=True)
class PaidTx:
    charge_id: str
    telegram_id: int
    payload: str | None
    amount: int


def extract_payments(transactions: list[Any]) -> list[PaidTx]:
    """Incoming user payments only; a charge that was later refunded is dropped."""
    refunded = {
        tx.id
        for tx in transactions
        if getattr(tx, "receiver", None) is not None and getattr(tx, "source", None) is None
    }
    out: list[PaidTx] = []
    for tx in transactions:
        src = getattr(tx, "source", None)
        if src is None or getattr(src, "type", None) != "user" or tx.id in refunded:
            continue
        user = getattr(src, "user", None)
        if user is None:
            continue
        out.append(
            PaidTx(
                charge_id=tx.id,
                telegram_id=user.id,
                payload=getattr(src, "invoice_payload", None),
                amount=int(tx.amount),
            )
        )
    return out


async def fetch_transactions(bot: Any, max_pages: int = 3) -> list[Any]:
    """Newest-first pages of the bot's Stars ledger, stopping at the first short page."""
    out: list[Any] = []
    for page in range(max_pages):
        res = await bot.get_star_transactions(offset=page * PAGE, limit=PAGE)
        batch = list(res.transactions)
        out.extend(batch)
        if len(batch) < PAGE:
            break
    return out


async def recover(
    payments: list[PaidTx], sub_repo: Any, user_repo: Any, sub_svc: Any, bot: Any
) -> int:
    """Grant every genuinely paid, still-unknown payment. Returns how many were granted."""
    granted = 0
    for p in payments:
        product = get_product(p.payload)
        if product is None or p.amount != product.stars:
            logger.warning(
                "reconcile: skip %s (payload=%r amount=%s)", p.charge_id, p.payload, p.amount
            )
            continue
        try:
            if await sub_repo.get_by_charge_id(p.charge_id):
                continue
            user = await user_repo.get_by_telegram_id(p.telegram_id)
            if user is None:
                logger.warning(
                    "reconcile: paid charge %s from unknown user %s", p.charge_id, p.telegram_id
                )
                continue
            await sub_svc.activate(
                user_id=user.id,
                telegram_id=p.telegram_id,
                charge_id=p.charge_id,
                days=product.days,
                plan_code=product.code,
            )
        except Exception:
            logger.exception("reconcile: failed to grant charge %s", p.charge_id)
            continue
        granted += 1
        track_soon("paid", p.telegram_id)
        logger.warning(
            "reconcile: RECOVERED lost payment %s for user %s", p.charge_id, p.telegram_id
        )
        try:
            await bot.send_message(
                p.telegram_id,
                t("premium.activated", normalize_locale(user.language_code)),
                parse_mode="HTML",
            )
        except Exception:
            logger.info("reconcile: could not notify %s", p.telegram_id)
    return granted


async def reconcile_stars(bot: Any, session_factory: Any) -> int:
    """Scheduler entry point. Never raises: a Telegram outage must not kill the job."""
    from app.infrastructure.db.repositories.subscription_repo import SubscriptionRepository
    from app.infrastructure.db.repositories.user_repo import UserRepository
    from app.services.subscription_service import SubscriptionService

    try:
        payments = extract_payments(await fetch_transactions(bot))
    except Exception:
        logger.exception("reconcile: could not read Stars ledger")
        return 0
    if not payments:
        return 0
    async with session_factory() as session:
        sub_repo = SubscriptionRepository(session)
        user_repo = UserRepository(session)
        svc = SubscriptionService(sub_repo, user_repo)
        return await recover(payments, sub_repo, user_repo, svc, bot)
