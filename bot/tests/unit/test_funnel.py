"""P2 conversion funnel: unique users per stage (paywall -> plans -> invoice -> paid)."""

import asyncio
from datetime import UTC, date, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.infrastructure.redis.funnel import STAGES, Funnel, conversion_rates


class FakeHLL:
    """Minimal PFADD/PFCOUNT/EXPIRE stand-in: exact sets behave like HLL at small scale."""

    def __init__(self):
        self.sets: dict[str, set] = {}
        self.fail = False

    async def pfadd(self, key, *vals):
        if self.fail:
            raise ConnectionError("down")
        self.sets.setdefault(key, set()).update(vals)
        return 1

    async def pfcount(self, *keys):
        if self.fail:
            raise ConnectionError("down")
        return len(set().union(*(self.sets.get(k, set()) for k in keys)))

    async def expire(self, key, ttl):
        return True


NOW = datetime(2026, 11, 10, 12, 0, tzinfo=UTC)


@pytest.mark.asyncio
async def test_counts_unique_users_not_events():
    f = Funnel(FakeHLL())
    for uid in (1, 1, 1, 2):
        await f.track("paywall", uid, now=NOW)
    await f.track("paid", 1, now=NOW)
    s = await f.summary(7, now=NOW)
    assert s["paywall"] == 2 and s["paid"] == 1 and s["plans"] == 0 and s["invoice"] == 0


@pytest.mark.asyncio
async def test_window_covers_only_the_last_n_days():
    f = Funnel(FakeHLL())
    await f.track("paywall", 1, now=NOW - timedelta(days=10))
    await f.track("paywall", 2, now=NOW - timedelta(days=2))
    assert (await f.summary(7, now=NOW))["paywall"] == 1
    assert (await f.summary(30, now=NOW))["paywall"] == 2


@pytest.mark.asyncio
async def test_same_user_on_two_days_counts_once_in_the_window():
    f = Funnel(FakeHLL())
    await f.track("paywall", 5, now=NOW - timedelta(days=1))
    await f.track("paywall", 5, now=NOW)
    assert (await f.summary(7, now=NOW))["paywall"] == 1


@pytest.mark.asyncio
async def test_unknown_stage_is_rejected_and_redis_failure_is_swallowed():
    r = FakeHLL()
    f = Funnel(r)
    with pytest.raises(ValueError):
        await f.track("nope", 1)
    r.fail = True
    await f.track("paywall", 1)  # must not raise: metrics never break the bot
    assert await f.summary(7) == dict.fromkeys(STAGES, 0)


def test_conversion_rates():
    r = conversion_rates({"paywall": 200, "plans": 50, "invoice": 20, "paid": 5})
    assert r["plans_from_paywall"] == 25.0 and r["invoice_from_plans"] == 40.0
    assert r["paid_from_invoice"] == 25.0 and r["paid_from_paywall"] == 2.5
    z = conversion_rates(dict.fromkeys(STAGES, 0))
    assert all(v == 0.0 for v in z.values())  # no ZeroDivisionError


@pytest.mark.asyncio
async def test_paywall_keyboard_tracks_the_current_user_once_per_build(monkeypatch):
    from app.bot.handlers import menu
    from app.core.context import current_tg_id
    from app.infrastructure.redis import funnel as fmod

    fake = Funnel(FakeHLL())
    monkeypatch.setattr(fmod, "_funnel", fake)
    token = current_tg_id.set(777)
    try:
        menu._rate_limit_kb("ru")
        await asyncio.sleep(0.05)  # let the spawned task run
    finally:
        current_tg_id.reset(token)
    assert (await fake.summary(7))["paywall"] == 1


def test_keyboard_without_user_context_or_loop_does_not_crash():
    from app.bot.handlers import menu

    assert menu._rate_limit_kb("ru").inline_keyboard  # sync, no loop, no user: silent


@pytest.mark.asyncio
async def test_middleware_sets_the_current_user_for_handlers():
    from app.bot.middlewares.db import DbSessionMiddleware
    from app.core.context import current_tg_id

    seen = {}

    async def handler(event, data):
        seen["id"] = current_tg_id.get()

    factory = MagicMock(
        return_value=MagicMock(__aenter__=AsyncMock(), __aexit__=AsyncMock(return_value=False))
    )
    mw = DbSessionMiddleware(factory)
    await mw(handler, MagicMock(), {"event_from_user": SimpleNamespace(id=42)})
    assert seen["id"] == 42
    assert current_tg_id.get(None) is None  # reset after the update


@pytest.mark.asyncio
async def test_admin_funnel_screen_shows_stages_and_rates(monkeypatch):
    from app.bot.handlers import admin as ah
    from app.infrastructure.redis import funnel as fmod

    fake = Funnel(FakeHLL())
    for uid in range(10):
        await fake.track("paywall", uid)
    for uid in range(4):
        await fake.track("plans", uid)
    await fake.track("paid", 0)
    monkeypatch.setattr(fmod, "_funnel", fake)
    cb = MagicMock()
    cb.answer = AsyncMock()
    cb.message.edit_text = AsyncMock()
    await ah.admin_funnel(cb)
    text = cb.message.edit_text.await_args.args[0]
    assert "10" in text and "40" in text  # paywall users and 40% -> plans
    assert date.today().isoformat()[:4] in text or "7" in text
