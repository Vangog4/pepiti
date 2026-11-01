"""P1.1 renewal reminders (packs only) and P1.5 evening streak nudge."""

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.infrastructure.redis.once import OnceGuard
from app.services import nudges as n

NOW = datetime(2026, 11, 1, 7, 0, tzinfo=UTC)  # 10:00 in Moscow


def test_renewal_days_in_user_local_time():
    # expires 2026-11-04 22:00 UTC = 01:00 on 2026-11-05 in Moscow -> 4 local days away
    exp = datetime(2026, 11, 4, 22, 0)
    assert n.renewal_days_left(exp, "UTC", NOW) == 3
    assert n.renewal_days_left(exp, "Europe/Moscow", NOW) == 4


@pytest.mark.parametrize(
    "days,send", [(3, True), (1, True), (2, False), (0, False), (7, False), (-1, False)]
)
def test_only_three_and_one_days_before_trigger(days, send):
    exp = datetime(2026, 11, 1 + days, 12, 0) if days >= 0 else datetime(2026, 10, 31, 12, 0)
    got = n.renewal_stage(exp, "UTC", NOW)
    assert (got is not None) is send


def test_only_one_time_packs_are_nagged_not_subscriptions():
    assert n.is_one_time_pack("premium_3m") is True
    assert n.is_one_time_pack("premium_12m") is True
    assert n.is_one_time_pack("premium_1m") is False  # auto-renews, Telegram handles it
    assert n.is_one_time_pack("referral_bonus") is False
    assert n.is_one_time_pack("admin_grant") is False
    assert n.is_one_time_pack(None) is False


def _snap(streak, done_today, freezes=1):
    return {"streak": streak, "done_today": done_today, "freezes_left": freezes}


@pytest.mark.parametrize(
    "snap,hour,expect",
    [
        (_snap(5, False), 20, True),
        (_snap(5, True), 20, False),  # already trained today
        (_snap(1, False), 20, False),  # nothing worth protecting yet
        (_snap(0, False), 20, False),
        (_snap(5, False), 19, False),  # not the evening hour
        (_snap(2, False), 20, True),
    ],
)
def test_evening_nudge_rules(snap, hour, expect):
    assert n.evening_nudge_due(snap, hour) is expect


class FakeRedis:
    def __init__(self):
        self.d, self.fail = {}, False

    async def set(self, key, val, nx=False, ex=None):
        if self.fail:
            raise ConnectionError("down")
        if nx and key in self.d:
            return None
        self.d[key] = val
        return True


@pytest.mark.asyncio
async def test_once_guard_is_once_and_fails_closed():
    r = FakeRedis()
    g = OnceGuard(r)
    assert await g.first("k", 60) is True
    assert await g.first("k", 60) is False
    r.fail = True
    assert await g.first("other", 60) is False  # Redis down: skip, never spam


def _env(
    user_tz="UTC", premium_until=None, plan="premium_3m", streak_rows=(), reminder_time="10:00"
):
    user = SimpleNamespace(
        id=1,
        telegram_id=99,
        language_code="ru",
        timezone=user_tz,
        reminder_time=reminder_time,
        is_premium=bool(premium_until),
        subscription_expires_at=premium_until,
    )
    return user


@pytest.mark.asyncio
async def test_renewal_job_sends_once_with_plans_button(monkeypatch):
    exp = datetime(2026, 11, 4, 12, 0)
    user = _env(premium_until=exp)
    sub = SimpleNamespace(id=5, plan_code="premium_3m", expires_at=exp)
    pet = SimpleNamespace(id=7, name="Рекс")
    monkeypatch.setattr(n, "due_users", AsyncMock(return_value=[user]))
    session = MagicMock()
    res_sub, res_pet = MagicMock(), MagicMock()
    res_sub.scalars.return_value.first.return_value = sub
    res_pet.scalars.return_value.first.return_value = pet
    session.execute = AsyncMock(side_effect=[res_sub, res_pet])
    ctx = MagicMock(
        __aenter__=AsyncMock(return_value=session), __aexit__=AsyncMock(return_value=False)
    )
    bot = MagicMock(send_message=AsyncMock())
    guard = OnceGuard(FakeRedis())

    sent = await n.send_renewal_reminders(MagicMock(return_value=ctx), bot, guard, now_utc=NOW)
    assert sent == 1
    kb = bot.send_message.await_args.kwargs["reply_markup"]
    assert kb.inline_keyboard[0][0].callback_data == "menu_premium"
    # same day, same stage: no second message
    session.execute = AsyncMock(side_effect=[res_sub, res_pet])
    assert await n.send_renewal_reminders(MagicMock(return_value=ctx), bot, guard, now_utc=NOW) == 0


@pytest.mark.asyncio
async def test_renewal_job_skips_auto_renewing_subscription(monkeypatch):
    exp = datetime(2026, 11, 4, 12, 0)
    user = _env(premium_until=exp)
    sub = SimpleNamespace(id=5, plan_code="premium_1m", expires_at=exp)
    monkeypatch.setattr(n, "due_users", AsyncMock(return_value=[user]))
    session = MagicMock()
    r = MagicMock()
    r.scalars.return_value.first.return_value = sub
    session.execute = AsyncMock(return_value=r)
    ctx = MagicMock(
        __aenter__=AsyncMock(return_value=session), __aexit__=AsyncMock(return_value=False)
    )
    bot = MagicMock(send_message=AsyncMock())
    assert (
        await n.send_renewal_reminders(
            MagicMock(return_value=ctx), bot, OnceGuard(FakeRedis()), now_utc=NOW
        )
        == 0
    )
    bot.send_message.assert_not_awaited()


def test_scheduler_registers_both_jobs():
    from app.scheduler.setup import create_scheduler

    s = create_scheduler(MagicMock(), MagicMock())
    assert s.get_job("renewal_reminders") and s.get_job("evening_nudge")


def _evening_env(monkeypatch, rows):
    user = SimpleNamespace(
        id=1,
        telegram_id=99,
        language_code="ru",
        timezone="UTC",
        reminder_time="10:00",
        is_premium=False,
        subscription_expires_at=None,
    )
    pet = SimpleNamespace(id=7, name="Рекс")
    monkeypatch.setattr(n, "due_users", AsyncMock(return_value=[user]))
    res = MagicMock()
    res.scalars.return_value.first.return_value = pet
    session = MagicMock(execute=AsyncMock(return_value=res))
    ctx = MagicMock(
        __aenter__=AsyncMock(return_value=session), __aexit__=AsyncMock(return_value=False)
    )
    import app.infrastructure.db.repositories.activity_repo as ar

    monkeypatch.setattr(ar.ActivityRepository, "rows", AsyncMock(return_value=rows))
    return MagicMock(return_value=ctx)


def _task(d):
    return SimpleNamespace(kind="task", local_date=d, duration_min=None)


@pytest.mark.asyncio
async def test_evening_nudge_sent_once_when_streak_at_risk(monkeypatch):
    evening = datetime(2026, 11, 1, 20, 0, tzinfo=UTC)
    today = evening.date()
    rows = [_task(today - timedelta(days=i)) for i in (1, 2, 3)]  # 3-day streak, not trained today
    fac = _evening_env(monkeypatch, rows)
    bot = MagicMock(send_message=AsyncMock())
    guard = OnceGuard(FakeRedis())
    assert await n.send_evening_nudges(fac, bot, guard, now_utc=evening) == 1
    assert "3" in bot.send_message.await_args.args[1]
    assert await n.send_evening_nudges(fac, bot, guard, now_utc=evening) == 0  # same day


@pytest.mark.asyncio
async def test_evening_nudge_silent_if_already_trained_or_no_streak(monkeypatch):
    evening = datetime(2026, 11, 1, 20, 0, tzinfo=UTC)
    today = evening.date()
    bot = MagicMock(send_message=AsyncMock())
    done = _evening_env(monkeypatch, [_task(today), _task(today - timedelta(days=1))])
    assert await n.send_evening_nudges(done, bot, OnceGuard(FakeRedis()), now_utc=evening) == 0
    none = _evening_env(monkeypatch, [])
    assert await n.send_evening_nudges(none, bot, OnceGuard(FakeRedis()), now_utc=evening) == 0
    bot.send_message.assert_not_awaited()
