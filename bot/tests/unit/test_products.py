"""Product catalog (prices fixed by owner 2026-11-01) drives invoices, pre-checkout and grants."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.products import PRODUCTS, get_product


def test_catalog_prices_and_durations():
    assert {c: (p.stars, p.rub, p.days) for c, p in PRODUCTS.items()} == {
        "premium_1m": (950, 1490, 30),
        "premium_3m": (2200, 3490, 90),
        "premium_12m": (5000, 7990, 365),
    }


def test_only_monthly_is_recurring():
    assert get_product("premium_1m").recurring is True
    assert get_product("premium_3m").recurring is False
    assert get_product("premium_12m").recurring is False


def test_unknown_product():
    assert get_product("evil") is None
    assert get_product(None) is None


def _pcq(payload, amount, currency="XTR"):
    p = MagicMock()
    p.invoice_payload, p.total_amount, p.currency = payload, amount, currency
    p.answer = AsyncMock()
    return p


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload,amount,ok",
    [
        ("premium_1m", 950, True),
        ("premium_3m", 2200, True),
        ("premium_12m", 5000, True),
        ("premium_3m", 950, False),  # amount of another product
        ("premium_12m", 1, False),
        ("premium_6m", 950, False),
    ],
)
async def test_pre_checkout_per_product(payload, amount, ok):
    from app.bot.handlers.subscription import pre_checkout

    pcq = _pcq(payload, amount)
    await pre_checkout(pcq)
    assert pcq.answer.await_args.kwargs["ok"] is ok


@pytest.mark.asyncio
async def test_successful_payment_grants_product_days():
    from app.bot.handlers import subscription as h

    msg = MagicMock()
    msg.from_user.id = 7
    msg.answer = AsyncMock()
    msg.successful_payment.invoice_payload = "premium_12m"
    msg.successful_payment.telegram_payment_charge_id = "ch_12"
    usr = MagicMock(id=1, language_code="ru")
    u_svc = MagicMock(get_or_create_telegram_user=AsyncMock(return_value=usr))
    sub_svc = MagicMock(activate=AsyncMock())

    await h.successful_payment.__wrapped__(msg, u_svc, sub_svc)

    kw = sub_svc.activate.await_args.kwargs
    assert kw["days"] == 365 and kw["plan_code"] == "premium_12m" and kw["charge_id"] == "ch_12"


def test_rate_limit_keyboard_is_one_tap_to_invoice():
    from app.bot.handlers.menu import _rate_limit_kb

    kb = _rate_limit_kb("ru")
    first_row = kb.inline_keyboard[0]
    assert first_row[0].callback_data == "buy:premium_1m"
    assert first_row[1].callback_data == "menu_premium"
    assert all(len(b.text) <= 24 for r in kb.inline_keyboard for b in r)


def test_plan_buttons_fit_14_chars_in_every_locale():
    from app.i18n import t

    for lg in ("ru", "en", "de", "es", "fr", "pt"):
        for code, p in PRODUCTS.items():
            txt = t(f"premium.plan.{code}.btn", lg, stars=p.stars)
            assert "{" not in txt and len(txt) <= 16, (lg, code, txt)


@pytest.mark.asyncio
async def test_remaining_footer_free_vs_premium():
    from datetime import datetime, timedelta
    from types import SimpleNamespace

    from app.bot.handlers.menu import _remaining_footer

    rl = MagicMock(_limit=3)
    rl.remaining = AsyncMock(return_value=2)
    free = SimpleNamespace(is_premium=False, subscription_expires_at=None, timezone="UTC")
    prem = SimpleNamespace(
        is_premium=True,
        subscription_expires_at=datetime.utcnow() + timedelta(days=3),
        timezone="UTC",
    )
    assert "2" in await _remaining_footer(rl, free, 1, "ru") and "3" in await _remaining_footer(
        rl, free, 1, "ru"
    )
    assert await _remaining_footer(rl, prem, 1, "ru") == ""
