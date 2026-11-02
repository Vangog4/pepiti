"""P0 payment safety: idempotent activation, strict pre-checkout, no dropped updates."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.services.subscription_service import PREMIUM_1M_STARS, SubscriptionService


@pytest.mark.asyncio
async def test_activate_race_returns_existing_on_unique_violation():
    """Two identical updates racing: the loser hits the UNIQUE index, must not raise or double-grant."""
    winner = MagicMock(name="winner")
    sub_repo = MagicMock()
    sub_repo.get_by_charge_id = AsyncMock(side_effect=[None, winner])
    sub_repo.max_active_expires_at = AsyncMock(return_value=None)
    sub_repo.create = AsyncMock(side_effect=IntegrityError("insert", {}, Exception("dup")))
    sub_repo.session = MagicMock()
    sub_repo.session.rollback = AsyncMock()
    user_repo = MagicMock()
    user_repo.get_by_telegram_id = AsyncMock()

    out = await SubscriptionService(sub_repo, user_repo).activate(1, 100, "ch_race")

    assert out is winner
    sub_repo.session.rollback.assert_awaited_once()
    user_repo.get_by_telegram_id.assert_not_awaited()


def _pcq(payload="premium_1m", currency="XTR", amount=PREMIUM_1M_STARS):
    pcq = MagicMock()
    pcq.invoice_payload = payload
    pcq.currency = currency
    pcq.total_amount = amount
    pcq.answer = AsyncMock()
    return pcq


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "kw,ok",
    [
        ({}, True),
        ({"payload": "evil"}, False),
        ({"currency": "USD"}, False),
        ({"amount": 1}, False),
    ],
)
async def test_pre_checkout_validates_amount(kw, ok):
    from app.bot.handlers.subscription import pre_checkout

    pcq = _pcq(**kw)
    await pre_checkout(pcq)
    assert pcq.answer.await_args.kwargs["ok"] is ok


def test_polling_does_not_drop_pending_updates():
    import inspect

    import app.main as m

    src = inspect.getsource(m)
    assert "drop_pending_updates=True" not in src
