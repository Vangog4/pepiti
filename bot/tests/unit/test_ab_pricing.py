"""P2: A/B pricing. Mechanism only; OFF by default so prices do not change until configured."""

from collections import Counter
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services import pricing
from app.services.products import get_product

RULES_ON = {
    "ab.enabled": True,
    "ab.salt": "s1",
    "ab.variants": {"B": {"weight": 30}, "C": {"weight": 20}},
    "products.premium_1m.variants": {"B": {"stars": 800}, "C": {"stars": 1100}},
    "products.premium_3m.variants": {"B": {"stars": 1900}},
}


@pytest.fixture
def ab_on(monkeypatch):
    monkeypatch.setattr(pricing, "rule", lambda path, default=None: RULES_ON.get(path, default))


def test_off_by_default_everyone_is_control_with_catalog_prices():
    p = get_product("premium_1m")
    assert pricing.ab_enabled() is False
    assert pricing.variant_for(123) == "control"
    assert pricing.stars_for(p, "control") == p.stars == 950
    assert pricing.allowed_stars(p) == {950}


def test_assignment_is_deterministic_and_sticky(ab_on):
    assert [pricing.variant_for(42) for _ in range(5)] == [pricing.variant_for(42)] * 5


def test_distribution_follows_weights(ab_on):
    counts = Counter(pricing.variant_for(uid) for uid in range(10_000))
    assert abs(counts["B"] / 100 - 30) < 3 and abs(counts["C"] / 100 - 20) < 3
    assert abs(counts["control"] / 100 - 50) < 3


def test_variant_price_falls_back_to_control_when_not_defined(ab_on):
    p1, p3, p12 = get_product("premium_1m"), get_product("premium_3m"), get_product("premium_12m")
    assert pricing.stars_for(p1, "B") == 800 and pricing.stars_for(p1, "C") == 1100
    assert (
        pricing.stars_for(p3, "B") == 1900 and pricing.stars_for(p3, "C") == p3.stars
    )  # C not set
    assert pricing.stars_for(p12, "B") == p12.stars  # product without variants


def test_allowed_stars_covers_every_configured_variant(ab_on):
    assert pricing.allowed_stars(get_product("premium_1m")) == {950, 800, 1100}
    assert pricing.allowed_stars(get_product("premium_12m")) == {5000}


def test_garbage_config_is_ignored(monkeypatch):
    bad = {
        "ab.enabled": True,
        "ab.salt": "s",
        "ab.variants": {"B": {"weight": "lots"}, "X": {"weight": -5}, "Y": {"weight": 500}},
        "products.premium_1m.variants": {"B": {"stars": -1}, "Y": {"stars": "x"}},
    }
    monkeypatch.setattr(pricing, "rule", lambda path, default=None: bad.get(path, default))
    p = get_product("premium_1m")
    assert pricing.allowed_stars(p) == {950}
    assert {pricing.variant_for(u) for u in range(500)} <= {
        "control",
        "Y",
    }  # weights are capped to 100 total
    assert pricing.stars_for(p, "B") == 950


@pytest.mark.asyncio
async def test_invoice_uses_the_users_variant_price(ab_on, monkeypatch):
    from app.bot.handlers import subscription as sh

    monkeypatch.setattr(pricing, "variant_for", lambda uid: "B")
    target = MagicMock()
    target.chat.id = 5
    target.answer_invoice = AsyncMock()
    await sh.send_premium_invoice(target, "ru", "premium_3m")
    assert target.answer_invoice.await_args.kwargs["prices"][0].amount == 1900
    assert target.answer_invoice.await_args.kwargs["payload"] == "premium_3m"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "amount,ok", [(950, True), (800, True), (1100, True), (700, False), (1, False)]
)
async def test_pre_checkout_accepts_any_configured_variant_price_only(ab_on, amount, ok):
    from app.bot.handlers.subscription import pre_checkout

    pcq = MagicMock(invoice_payload="premium_1m", total_amount=amount, currency="XTR")
    pcq.from_user.id = 5
    pcq.answer = AsyncMock()
    await pre_checkout.__wrapped__(pcq, MagicMock())
    assert pcq.answer.await_args.kwargs["ok"] is ok


@pytest.mark.asyncio
async def test_reconciliation_accepts_a_variant_price(ab_on):
    from app.services import payment_reconcile as pr

    users = MagicMock(
        get_by_telegram_id=AsyncMock(return_value=SimpleNamespace(id=2, language_code="ru"))
    )
    svc = MagicMock(activate=AsyncMock())
    n = await pr.recover(
        [pr.PaidTx("c", 7, "premium_1m", 800)],
        MagicMock(get_by_charge_id=AsyncMock(return_value=None)),
        users,
        svc,
        MagicMock(send_message=AsyncMock()),
    )
    assert n == 1 and svc.activate.await_args.kwargs["days"] == 30


def test_plan_buttons_show_the_variant_price(ab_on, monkeypatch):
    from app.bot.handlers.subscription import _plans_keyboard

    monkeypatch.setattr(pricing, "variant_for", lambda uid: "B")
    texts = [b.text for r in _plans_keyboard("ru", 5).inline_keyboard for b in r]
    assert any("800" in x for x in texts) and not any("950" in x for x in texts)
    for lg in ("ru", "en", "de", "es", "fr", "pt"):
        assert all(len(b.text) <= 14 for r in _plans_keyboard(lg, 5).inline_keyboard for b in r), lg


@pytest.mark.asyncio
async def test_funnel_splits_by_variant():
    from datetime import UTC, datetime

    from app.infrastructure.redis.funnel import Funnel
    from tests.unit.test_funnel import FakeHLL

    f, now = Funnel(FakeHLL()), datetime(2026, 11, 10, tzinfo=UTC)
    await f.track("invoice", 1, now=now, variant="B")
    await f.track("invoice", 2, now=now, variant="control")
    await f.track("invoice", 3, now=now, variant="B")
    assert (await f.summary(7, now=now))["invoice"] == 3  # overall unchanged
    assert (await f.summary(7, now=now, variant="B"))["invoice"] == 2
    assert (await f.summary(7, now=now, variant="control"))["invoice"] == 1


def test_variant_price_is_capped_to_four_digits(monkeypatch):
    cfg = {
        "ab.enabled": True,
        "ab.variants": {"B": {"weight": 50}},
        "products.premium_1m.variants": {"B": {"stars": 99999}},
    }
    monkeypatch.setattr(pricing, "rule", lambda path, default=None: cfg.get(path, default))
    assert pricing.allowed_stars(get_product("premium_1m")) == {950}


@pytest.mark.asyncio
async def test_admin_funnel_shows_a_line_per_variant_only_when_enabled(ab_on, monkeypatch):
    from app.bot.handlers import admin as ah
    from app.infrastructure.redis import funnel as fmod
    from app.infrastructure.redis.funnel import Funnel
    from tests.unit.test_funnel import FakeHLL

    fake = Funnel(FakeHLL())
    await fake.track("paywall", 1, variant="B")
    await fake.track("paid", 1, variant="B")
    monkeypatch.setattr(fmod, "_funnel", fake)
    cb = MagicMock()
    cb.answer = AsyncMock()
    cb.message.edit_text = AsyncMock()
    await ah.admin_funnel(cb)
    text = cb.message.edit_text.await_args.args[0]
    assert "A/B" in text and "<b>B</b>" in text and "<b>control</b>" in text and "<b>C</b>" in text


@pytest.mark.asyncio
async def test_admin_funnel_has_no_ab_block_when_disabled(monkeypatch):
    from app.bot.handlers import admin as ah
    from app.infrastructure.redis import funnel as fmod
    from app.infrastructure.redis.funnel import Funnel
    from tests.unit.test_funnel import FakeHLL

    monkeypatch.setattr(fmod, "_funnel", Funnel(FakeHLL()))
    cb = MagicMock()
    cb.answer = AsyncMock()
    cb.message.edit_text = AsyncMock()
    await ah.admin_funnel(cb)
    assert "A/B" not in cb.message.edit_text.await_args.args[0]


@pytest.mark.asyncio
async def test_subscription_button_shows_the_price_actually_charged(ab_on, monkeypatch):
    """Regression: the recurring plan's button showed the catalog price while the invoice
    charged the user's A/B variant price."""
    from app.bot.handlers import subscription as sh

    monkeypatch.setattr(pricing, "variant_for", lambda uid: "B")
    target = MagicMock()
    target.chat.id = 5
    target.bot.create_invoice_link = AsyncMock(return_value="https://t.me/invoice/x")
    target.answer = AsyncMock()
    await sh.send_premium_invoice(target, "ru", "premium_1m")
    assert target.bot.create_invoice_link.await_args.kwargs["prices"][0].amount == 800
    button = target.answer.await_args.kwargs["reply_markup"].inline_keyboard[0][0]
    assert "800" in button.text and "950" not in button.text
