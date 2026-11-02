"""P2: gift Premium to a friend (one-time packs only), end to end through the payment paths."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.gifts import make_gift_payload, parse_payload, target_telegram_id


def test_plain_product_payload_still_works():
    p = parse_payload("premium_3m")
    assert p.product.code == "premium_3m" and p.recipient_tg_id is None


def test_gift_payload_roundtrip_and_size():
    s = make_gift_payload("premium_12m", 123456789012)
    assert len(s.encode()) <= 128  # Telegram's invoice payload limit
    p = parse_payload(s)
    assert p.product.code == "premium_12m" and p.recipient_tg_id == 123456789012


@pytest.mark.parametrize(
    "bad",
    [
        None,
        "",
        "gift",
        "gift:premium_3m",
        "gift:premium_3m:abc",
        "gift:premium_3m:0",
        "gift:premium_3m:-5",
        "gift:evil:5",
        "gift:premium_1m:5",
        "x:premium_3m:5",
        "gift:premium_3m:5:6",
        "premium_9m",
        "g" * 500,
    ],
)
def test_garbage_and_recurring_gift_payloads_are_rejected(bad):
    assert parse_payload(bad) is None  # a recurring subscription cannot be gifted


def test_target_is_the_recipient_for_gifts_and_the_payer_otherwise():
    assert target_telegram_id(parse_payload("premium_3m"), 7) == 7
    assert target_telegram_id(parse_payload("gift:premium_3m:99"), 7) == 99


def _pcq(payload, amount, payer=7, currency="XTR"):
    p = MagicMock()
    p.invoice_payload, p.total_amount, p.currency = payload, amount, currency
    p.from_user.id = payer
    p.answer = AsyncMock()
    return p


def _repo(exists=True):
    return MagicMock(
        get_by_telegram_id=AsyncMock(return_value=SimpleNamespace(id=2) if exists else None)
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload,amount,exists,payer,ok",
    [
        ("gift:premium_3m:99", 2200, True, 7, True),
        ("gift:premium_3m:99", 950, True, 7, False),  # wrong amount
        ("gift:premium_3m:99", 2200, False, 7, False),  # recipient never used the bot
        ("gift:premium_3m:7", 2200, True, 7, False),  # gifting yourself
        ("gift:premium_1m:99", 950, True, 7, False),  # subscription is not giftable
        ("premium_3m", 2200, True, 7, True),  # unchanged
    ],
)
async def test_pre_checkout_for_gifts(payload, amount, exists, payer, ok):
    from app.bot.handlers.subscription import pre_checkout

    pcq = _pcq(payload, amount, payer)
    await pre_checkout.__wrapped__(pcq, _repo(exists))
    assert pcq.answer.await_args.kwargs["ok"] is ok


def _pay_msg(payload, payer=7, charge="ch1"):
    msg = MagicMock()
    msg.from_user.id = payer
    msg.from_user.first_name = "Аня"
    msg.answer = AsyncMock()
    msg.bot.send_message = AsyncMock()
    msg.successful_payment.invoice_payload = payload
    msg.successful_payment.telegram_payment_charge_id = charge
    return msg


@pytest.mark.asyncio
async def test_gift_payment_activates_the_recipient_not_the_payer_and_notifies_both():
    from app.bot.handlers import subscription as h

    payer = SimpleNamespace(id=1, language_code="ru", first_name="Аня")
    recipient = SimpleNamespace(id=2, language_code="en", first_name="Боб")
    u_svc = MagicMock(
        get_or_create_telegram_user=AsyncMock(return_value=payer),
        repo=MagicMock(get_by_telegram_id=AsyncMock(return_value=recipient)),
    )
    sub_svc = MagicMock(activate=AsyncMock())
    msg = _pay_msg("gift:premium_12m:99")
    await h.successful_payment.__wrapped__(msg, u_svc, sub_svc)

    kw = sub_svc.activate.await_args.kwargs
    assert kw["user_id"] == 2 and kw["telegram_id"] == 99 and kw["days"] == 365
    assert kw["charge_id"] == "ch1" and kw["plan_code"] == "premium_12m"
    sent_to = [c.args[0] for c in msg.bot.send_message.await_args_list]
    assert 99 in sent_to  # recipient told about the gift
    msg.answer.assert_awaited()  # payer confirmed


@pytest.mark.asyncio
async def test_gift_to_a_user_who_vanished_is_logged_not_lost_silently(caplog):
    from app.bot.handlers import subscription as h

    u_svc = MagicMock(
        get_or_create_telegram_user=AsyncMock(
            return_value=SimpleNamespace(id=1, language_code="ru")
        ),
        repo=MagicMock(get_by_telegram_id=AsyncMock(return_value=None)),
    )
    sub_svc = MagicMock(activate=AsyncMock())
    with caplog.at_level("ERROR"):
        await h.successful_payment.__wrapped__(_pay_msg("gift:premium_3m:99"), u_svc, sub_svc)
    sub_svc.activate.assert_not_awaited()
    assert (
        "gift" in caplog.text.lower() and "ch1" in caplog.text
    )  # operator can refund by charge id


@pytest.mark.asyncio
async def test_reconciliation_grants_a_lost_gift_to_the_recipient():
    from app.services import payment_reconcile as pr

    recipient = SimpleNamespace(id=2, language_code="ru")
    users = MagicMock(
        get_by_telegram_id=AsyncMock(
            side_effect=lambda tid: (
                recipient if tid == 99 else SimpleNamespace(id=1, language_code="ru")
            )
        )
    )
    sub_repo = MagicMock(get_by_charge_id=AsyncMock(return_value=None))
    svc = MagicMock(activate=AsyncMock())
    bot = MagicMock(send_message=AsyncMock())
    n = await pr.recover(
        [pr.PaidTx("chX", 7, "gift:premium_3m:99", 2200)], sub_repo, users, svc, bot
    )
    assert n == 1
    kw = svc.activate.await_args.kwargs
    assert kw["user_id"] == 2 and kw["telegram_id"] == 99 and kw["days"] == 90


def _gift_env(found=True, recipient_tg=99):
    usr = SimpleNamespace(id=1, language_code="ru", telegram_id=5)
    u_svc = MagicMock(get_or_create_telegram_user=AsyncMock(return_value=usr))
    repo = MagicMock(
        get_by_username=AsyncMock(
            return_value=SimpleNamespace(
                id=2, telegram_id=recipient_tg, first_name="Боб", username="bob"
            )
            if found
            else None
        )
    )
    return u_svc, repo


@pytest.mark.asyncio
async def test_gift_flow_sends_an_invoice_with_the_gift_payload():
    from app.bot.handlers import gift as gh

    u_svc, repo = _gift_env()
    state = MagicMock(
        get_data=AsyncMock(return_value={"gift_code": "premium_3m"}), clear=AsyncMock()
    )
    msg = MagicMock(text="@Bob")
    msg.from_user.id = 5
    msg.answer = AsyncMock()
    msg.answer_invoice = AsyncMock()
    await gh.receive_recipient.__wrapped__(msg, state, u_svc, repo)
    kw = msg.answer_invoice.await_args.kwargs
    assert kw["payload"] == "gift:premium_3m:99" and kw["currency"] == "XTR"
    assert kw["prices"][0].amount == 2200
    repo.get_by_username.assert_awaited_once_with("@Bob")


@pytest.mark.asyncio
@pytest.mark.parametrize("found,tg,why", [(False, 99, "not found"), (True, 5, "self")])
async def test_gift_flow_refuses_unknown_or_self(found, tg, why):
    from app.bot.handlers import gift as gh

    u_svc, repo = _gift_env(found=found, recipient_tg=tg)
    state = MagicMock(
        get_data=AsyncMock(return_value={"gift_code": "premium_3m"}), clear=AsyncMock()
    )
    msg = MagicMock(text="bob")
    msg.from_user.id = 5
    msg.answer = AsyncMock()
    msg.answer_invoice = AsyncMock()
    await gh.receive_recipient.__wrapped__(msg, state, u_svc, repo)
    msg.answer_invoice.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("code", ["premium_1m", "evil", ""])
async def test_gift_pick_rejects_non_giftable_products(code):
    from app.bot.handlers import gift as gh

    usr = SimpleNamespace(id=1, language_code="ru")
    u_svc = MagicMock(get_or_create_telegram_user=AsyncMock(return_value=usr))
    state = MagicMock(set_state=AsyncMock(), update_data=AsyncMock())
    cb = MagicMock(data=f"gift_pick:{code}")
    cb.answer = AsyncMock()
    cb.from_user.id = 5
    cb.message.edit_text = AsyncMock()
    await gh.pick_product.__wrapped__(cb, state, u_svc)
    state.set_state.assert_not_awaited()


def test_gift_button_is_on_the_plans_screen_and_fits():
    from app.bot.handlers.subscription import _plans_keyboard
    from app.i18n import t

    for lg in ("ru", "en", "de", "es", "fr", "pt"):
        btns = [b for r in _plans_keyboard(lg).inline_keyboard for b in r]
        gift = [b for b in btns if b.callback_data == "gift_start"]
        assert len(gift) == 1 and len(gift[0].text) <= 14, lg
        assert "gift." not in t("gift.received", lg, days=90, name="x")
