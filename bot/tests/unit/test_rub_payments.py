"""P1.1: rubles via Telegram Payments (T-Bank). Dormant unless token AND receipt template are set."""

import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.config import settings
from app.services import rub

TEMPLATE = '{"Receipt": {"Taxation": "usn_income", "Items": [{"Name": %TITLE%, "Price": %KOP%, "Quantity": 1, "Amount": %KOP%, "Tax": "none"}]}}'


@pytest.fixture
def rub_on(monkeypatch):
    monkeypatch.setattr(settings, "TBANK_PROVIDER_TOKEN", "123:TEST:abc")
    monkeypatch.setattr(settings, "TBANK_PROVIDER_DATA", TEMPLATE)


def test_dormant_by_default_and_needs_both_settings(monkeypatch):
    assert rub.rub_enabled() is False
    monkeypatch.setattr(settings, "TBANK_PROVIDER_TOKEN", "tok")
    assert rub.rub_enabled() is False  # token without a receipt template: still off
    monkeypatch.setattr(settings, "TBANK_PROVIDER_TOKEN", "")
    monkeypatch.setattr(settings, "TBANK_PROVIDER_DATA", TEMPLATE)
    assert rub.rub_enabled() is False


def test_amounts_are_in_kopecks_from_the_catalog(rub_on):
    from app.services.products import get_product

    assert rub.kopecks(get_product("premium_1m")) == 149_000
    assert rub.kopecks(get_product("premium_3m")) == 349_000
    assert rub.kopecks(get_product("premium_12m")) == 799_000


def test_provider_data_is_rendered_escaped_and_validated(rub_on):
    from app.services.products import get_product

    data = rub.render_provider_data(get_product("premium_3m"), 'Pepito "Premium" <3 мес>')
    parsed = json.loads(data)  # valid JSON even with quotes in the title
    item = parsed["Receipt"]["Items"][0]
    assert (
        item["Price"] == 349_000
        and item["Amount"] == 349_000
        and 'Pepito "Premium"' in item["Name"]
    )


def test_broken_template_renders_nothing_instead_of_a_bad_receipt(monkeypatch):
    from app.services.products import get_product

    monkeypatch.setattr(settings, "TBANK_PROVIDER_TOKEN", "tok")
    monkeypatch.setattr(settings, "TBANK_PROVIDER_DATA", '{"Receipt": %KOP% broken')
    assert rub.render_provider_data(get_product("premium_1m"), "x") is None


def _plans(lang="ru"):
    from app.bot.handlers.subscription import _plans_keyboard

    return [b for r in _plans_keyboard(lang, 5).inline_keyboard for b in r]


def test_no_rub_buttons_when_off_and_only_for_russian_when_on(rub_on, monkeypatch):
    assert any(b.callback_data == "buyrub:premium_3m" for b in _plans("ru"))
    assert not any((b.callback_data or "").startswith("buyrub:") for b in _plans("en"))
    monkeypatch.setattr(settings, "TBANK_PROVIDER_TOKEN", "")
    assert not any((b.callback_data or "").startswith("buyrub:") for b in _plans("ru"))


def test_rub_buttons_fit_14_characters(rub_on):
    for b in _plans("ru"):
        assert len(b.text) <= 14, b.text


@pytest.mark.asyncio
async def test_invoice_is_rub_with_kopecks_token_and_receipt(rub_on):
    from app.bot.handlers import subscription as sh

    target = MagicMock()
    target.chat.id = 5
    target.answer_invoice = AsyncMock()
    await sh.send_rub_invoice(target, "ru", "premium_3m")
    kw = target.answer_invoice.await_args.kwargs
    assert kw["currency"] == "RUB" and kw["provider_token"] == "123:TEST:abc"
    assert kw["prices"][0].amount == 349_000 and kw["payload"] == "premium_3m"
    assert json.loads(kw["provider_data"])["Receipt"]["Items"][0]["Price"] == 349_000


@pytest.mark.asyncio
async def test_invoice_not_sent_when_off_or_template_broken(monkeypatch):
    from app.bot.handlers import subscription as sh

    target = MagicMock()
    target.answer_invoice = AsyncMock()
    await sh.send_rub_invoice(target, "ru", "premium_3m")  # off
    monkeypatch.setattr(settings, "TBANK_PROVIDER_TOKEN", "tok")
    monkeypatch.setattr(settings, "TBANK_PROVIDER_DATA", "{not json %KOP%")
    await sh.send_rub_invoice(target, "ru", "premium_3m")
    target.answer_invoice.assert_not_awaited()


def _pcq(payload, amount, currency, payer=7):
    p = MagicMock(invoice_payload=payload, total_amount=amount, currency=currency)
    p.from_user.id = payer
    p.answer = AsyncMock()
    return p


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload,amount,currency,ok",
    [
        ("premium_3m", 349_000, "RUB", True),
        ("premium_3m", 3_490, "RUB", False),  # rubles, not kopecks
        ("premium_3m", 2200, "RUB", False),  # Stars amount in RUB
        ("premium_1m", 149_000, "RUB", True),  # 30 days one-off in RUB
        ("gift:premium_3m:99", 349_000, "RUB", False),  # gifts are Stars only
        ("premium_3m", 349_000, "USD", False),
    ],
)
async def test_pre_checkout_rub_when_enabled(rub_on, payload, amount, currency, ok):
    from app.bot.handlers.subscription import pre_checkout

    pcq = _pcq(payload, amount, currency)
    await pre_checkout.__wrapped__(
        pcq, MagicMock(get_by_telegram_id=AsyncMock(return_value=object()))
    )
    assert pcq.answer.await_args.kwargs["ok"] is ok


@pytest.mark.asyncio
async def test_pre_checkout_rejects_rub_when_off():
    from app.bot.handlers.subscription import pre_checkout

    pcq = _pcq("premium_3m", 349_000, "RUB")
    await pre_checkout.__wrapped__(pcq, MagicMock())
    assert pcq.answer.await_args.kwargs["ok"] is False


def _paid(currency, amount, payload="premium_3m"):
    msg = MagicMock()
    msg.from_user.id = 7
    msg.answer = AsyncMock()
    sp = msg.successful_payment
    sp.invoice_payload, sp.currency, sp.total_amount = payload, currency, amount
    sp.telegram_payment_charge_id, sp.provider_payment_charge_id = "tg1", "tb1"
    return msg


@pytest.mark.asyncio
async def test_rub_payment_grants_days_with_provider_tbank_and_rub_plan(rub_on):
    from app.bot.handlers import subscription as sh

    u_svc = MagicMock(
        get_or_create_telegram_user=AsyncMock(
            return_value=SimpleNamespace(id=1, language_code="ru")
        )
    )
    sub_svc = MagicMock(activate=AsyncMock())
    await sh.successful_payment.__wrapped__(_paid("RUB", 349_000), u_svc, sub_svc)
    kw = sub_svc.activate.await_args.kwargs
    assert kw["days"] == 90 and kw["provider"] == "tbank" and kw["plan_code"] == "premium_3m_rub"
    assert kw["charge_id"] == "tg1"


@pytest.mark.asyncio
async def test_rub_payment_with_wrong_amount_is_logged_not_granted(rub_on, caplog):
    from app.bot.handlers import subscription as sh

    u_svc = MagicMock(
        get_or_create_telegram_user=AsyncMock(
            return_value=SimpleNamespace(id=1, language_code="ru")
        )
    )
    sub_svc = MagicMock(activate=AsyncMock())
    with caplog.at_level("ERROR"):
        await sh.successful_payment.__wrapped__(_paid("RUB", 100), u_svc, sub_svc)
    sub_svc.activate.assert_not_awaited()
    assert "tg1" in caplog.text


def test_rub_plans_are_one_time_packs_for_renewal_reminders():
    from app.services.nudges import is_one_time_pack

    assert is_one_time_pack("premium_1m_rub") is True  # RUB 30 days does not auto-renew
    assert is_one_time_pack("premium_3m_rub") is True
    assert is_one_time_pack("premium_1m") is False
    assert is_one_time_pack("evil_rub") is False


@pytest.mark.asyncio
async def test_activate_passes_the_provider_to_the_repo():
    from app.services.subscription_service import SubscriptionService

    repo = MagicMock(
        get_by_charge_id=AsyncMock(return_value=None),
        max_active_expires_at=AsyncMock(return_value=None),
        create=AsyncMock(return_value=MagicMock()),
        session=MagicMock(commit=AsyncMock()),
    )
    users = MagicMock(
        get_by_telegram_id=AsyncMock(
            return_value=SimpleNamespace(is_premium=False, subscription_expires_at=None)
        )
    )
    await SubscriptionService(repo, users).activate(
        1, 7, "c", days=30, plan_code="premium_1m_rub", provider="tbank"
    )
    assert repo.create.await_args.kwargs["provider"] == "tbank"
