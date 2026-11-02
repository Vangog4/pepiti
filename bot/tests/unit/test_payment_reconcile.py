"""Recover paid Stars that never reached us as a successful_payment update."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services import payment_reconcile as pr


def user_tx(id, uid, payload, amount, refunded_to=None):
    src = SimpleNamespace(type="user", user=SimpleNamespace(id=uid), invoice_payload=payload)
    recv = SimpleNamespace(type="user", user=SimpleNamespace(id=uid)) if refunded_to else None
    return SimpleNamespace(id=id, amount=amount, source=None if refunded_to else src, receiver=recv)


def test_extract_keeps_only_real_incoming_payments():
    txs = [
        user_tx("a", 1, "premium_1m", 950),
        SimpleNamespace(id="b", amount=100, source=SimpleNamespace(type="fragment"), receiver=None),
        SimpleNamespace(id="c", amount=5, source=None, receiver=None),
        user_tx("d", 2, "premium_3m", 2200),
    ]
    got = pr.extract_payments(txs)
    assert [(p.charge_id, p.telegram_id, p.payload, p.amount) for p in got] == [
        ("a", 1, "premium_1m", 950),
        ("d", 2, "premium_3m", 2200),
    ]


def test_refunded_charge_is_never_granted():
    paid = user_tx("x", 1, "premium_1m", 950)
    refund = user_tx("x", 1, None, 950, refunded_to=True)  # same id, outgoing
    assert pr.extract_payments([paid, refund]) == []


def _env(existing_ids=(), user_exists=True, activate_side_effect=None):
    sub_repo = MagicMock(
        get_by_charge_id=AsyncMock(
            side_effect=lambda cid: object() if cid in existing_ids else None
        )
    )
    users = MagicMock(
        get_by_telegram_id=AsyncMock(
            return_value=SimpleNamespace(id=10, telegram_id=1, language_code="ru")
            if user_exists
            else None
        )
    )
    svc = MagicMock(activate=AsyncMock(side_effect=activate_side_effect))
    bot = MagicMock(send_message=AsyncMock())
    return sub_repo, users, svc, bot


@pytest.mark.asyncio
async def test_missing_payment_is_activated_with_product_days_and_user_notified():
    sub_repo, users, svc, bot = _env()
    n = await pr.recover([pr.PaidTx("ch1", 1, "premium_12m", 5000)], sub_repo, users, svc, bot)
    assert n == 1
    kw = svc.activate.await_args.kwargs
    assert kw["charge_id"] == "ch1" and kw["days"] == 365 and kw["plan_code"] == "premium_12m"
    bot.send_message.assert_awaited_once()


@pytest.mark.asyncio
async def test_already_known_payment_is_skipped():
    sub_repo, users, svc, bot = _env(existing_ids={"ch1"})
    assert (
        await pr.recover([pr.PaidTx("ch1", 1, "premium_1m", 950)], sub_repo, users, svc, bot) == 0
    )
    svc.activate.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "tx",
    [
        pr.PaidTx("c", 1, "evil", 950),  # unknown product
        pr.PaidTx("c", 1, "premium_3m", 950),  # amount of another product
        pr.PaidTx("c", 1, None, 950),  # no payload
    ],
)
async def test_suspicious_payments_are_not_granted(tx):
    sub_repo, users, svc, bot = _env()
    assert await pr.recover([tx], sub_repo, users, svc, bot) == 0
    svc.activate.assert_not_awaited()


@pytest.mark.asyncio
async def test_unknown_user_is_skipped_and_one_failure_does_not_stop_the_rest():
    sub_repo, users, svc, bot = _env(user_exists=False)
    assert await pr.recover([pr.PaidTx("c", 1, "premium_1m", 950)], sub_repo, users, svc, bot) == 0

    sub_repo, users, svc, bot = _env(activate_side_effect=[RuntimeError("db"), None])
    got = await pr.recover(
        [pr.PaidTx("c1", 1, "premium_1m", 950), pr.PaidTx("c2", 1, "premium_1m", 950)],
        sub_repo,
        users,
        svc,
        bot,
    )
    assert got == 1


@pytest.mark.asyncio
async def test_notification_failure_does_not_undo_the_grant():
    sub_repo, users, svc, bot = _env()
    bot.send_message = AsyncMock(side_effect=RuntimeError("blocked"))
    assert await pr.recover([pr.PaidTx("c", 1, "premium_1m", 950)], sub_repo, users, svc, bot) == 1


@pytest.mark.asyncio
async def test_fetch_pages_until_short_page():
    page1 = SimpleNamespace(
        transactions=[user_tx(str(i), 1, "premium_1m", 950) for i in range(100)]
    )
    page2 = SimpleNamespace(transactions=[user_tx("z", 1, "premium_1m", 950)])
    bot = MagicMock(get_star_transactions=AsyncMock(side_effect=[page1, page2]))
    txs = await pr.fetch_transactions(bot, max_pages=5)
    assert len(txs) == 101 and bot.get_star_transactions.await_count == 2


def test_scheduler_runs_reconciliation_at_startup_and_every_15_min():
    from app.scheduler.setup import create_scheduler

    job = create_scheduler(MagicMock(), MagicMock()).get_job("reconcile_stars")
    assert job is not None and job.max_instances == 1
    assert "*/15" in str(job.trigger)
