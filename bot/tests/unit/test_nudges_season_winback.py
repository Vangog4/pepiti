"""P1.4 seasonal pushes (opt-out) and P2 win-back after a paid plan ends."""

from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.infrastructure.redis.once import OnceGuard
from app.services import nudges as n
from tests.unit.test_nudges import FakeRedis


@pytest.mark.parametrize(
    "month,key", [(4, "ticks"), (7, "heat"), (12, "reagents"), (1, None), (9, None)]
)
def test_season_calendar(month, key):
    assert n.season_key(month) == key


def test_seasonal_only_on_the_send_day():
    assert n.seasonal_due(datetime(2026, 4, 5, 7, 0, tzinfo=UTC), "UTC") == "ticks"
    assert n.seasonal_due(datetime(2026, 4, 6, 7, 0, tzinfo=UTC), "UTC") is None
    assert n.seasonal_due(datetime(2026, 5, 5, 7, 0, tzinfo=UTC), "UTC") is None  # no May season


@pytest.mark.parametrize(
    "days_ago,premium,expect",
    [(3, False, True), (2, False, False), (4, False, False), (3, True, False)],
)
def test_winback_three_days_after_expiry(days_ago, premium, expect):
    now = datetime(2026, 11, 10, 7, 0, tzinfo=UTC)
    exp = (now - timedelta(days=days_ago)).replace(tzinfo=None)
    assert n.winback_due(exp, "UTC", now, premium) is expect


def _ctx(session):
    return MagicMock(
        return_value=MagicMock(
            __aenter__=AsyncMock(return_value=session), __aexit__=AsyncMock(return_value=False)
        )
    )


def _user(**kw):
    base = dict(
        id=1,
        telegram_id=99,
        language_code="ru",
        timezone="UTC",
        reminder_time="10:00",
        is_premium=False,
        subscription_expires_at=None,
        notify_seasonal=True,
    )
    base.update(kw)
    return SimpleNamespace(**base)


def _res(obj):
    r = MagicMock()
    r.scalars.return_value.first.return_value = obj
    return r


@pytest.mark.asyncio
async def test_seasonal_sent_once_per_month_and_respects_opt_out(monkeypatch):
    now = datetime(2026, 4, 5, 7, 0, tzinfo=UTC)
    bot, guard = MagicMock(send_message=AsyncMock()), OnceGuard(FakeRedis())
    monkeypatch.setattr(n, "due_users", AsyncMock(return_value=[_user()]))
    s = MagicMock(execute=AsyncMock(return_value=_res(SimpleNamespace(name="Рекс"))))
    assert await n.send_seasonal_nudges(_ctx(s), bot, guard, now_utc=now) == 1
    assert "Рекс" in bot.send_message.await_args.args[1]
    assert await n.send_seasonal_nudges(_ctx(s), bot, guard, now_utc=now) == 0  # same month

    monkeypatch.setattr(n, "due_users", AsyncMock(return_value=[_user(notify_seasonal=False)]))
    assert (
        await n.send_seasonal_nudges(
            _ctx(s), MagicMock(send_message=AsyncMock()), OnceGuard(FakeRedis()), now_utc=now
        )
        == 0
    )


@pytest.mark.asyncio
async def test_winback_only_for_lapsed_paid_users_and_once(monkeypatch):
    now = datetime(2026, 11, 10, 7, 0, tzinfo=UTC)
    exp = (now - timedelta(days=3)).replace(tzinfo=None)
    sub = SimpleNamespace(id=5, provider="telegram_stars", expires_at=exp)
    monkeypatch.setattr(n, "due_users", AsyncMock(return_value=[_user()]))
    s = MagicMock(execute=AsyncMock(side_effect=[_res(sub), _res(SimpleNamespace(name="Рекс"))]))
    bot, guard = MagicMock(send_message=AsyncMock()), OnceGuard(FakeRedis())
    assert await n.send_winback(_ctx(s), bot, guard, now_utc=now) == 1
    assert (
        bot.send_message.await_args.kwargs["reply_markup"].inline_keyboard[0][0].callback_data
        == "menu_premium"
    )
    s.execute = AsyncMock(side_effect=[_res(sub), _res(SimpleNamespace(name="Рекс"))])
    assert await n.send_winback(_ctx(s), bot, guard, now_utc=now) == 0  # once per lapsed plan

    # no paid history (e.g. only referral gifts) -> nothing
    s2 = MagicMock(execute=AsyncMock(return_value=_res(None)))
    assert (
        await n.send_winback(
            _ctx(s2), MagicMock(send_message=AsyncMock()), OnceGuard(FakeRedis()), now_utc=now
        )
        == 0
    )


@pytest.mark.asyncio
async def test_currently_premium_user_gets_no_winback(monkeypatch):
    now = datetime(2026, 11, 10, 7, 0, tzinfo=UTC)
    u = _user(
        is_premium=True, subscription_expires_at=(now + timedelta(days=9)).replace(tzinfo=None)
    )
    monkeypatch.setattr(n, "due_users", AsyncMock(return_value=[u]))
    s = MagicMock(execute=AsyncMock())
    assert (
        await n.send_winback(
            _ctx(s), MagicMock(send_message=AsyncMock()), OnceGuard(FakeRedis()), now_utc=now
        )
        == 0
    )
    s.execute.assert_not_awaited()


@pytest.mark.asyncio
async def test_settings_toggle_flips_the_flag_and_button_label():
    from app.bot.handlers import menu as mh
    from app.bot.keyboards.main_menu import get_settings_keyboard

    usr = SimpleNamespace(
        id=1,
        language_code="ru",
        timezone="UTC",
        reminder_time=None,
        notify_seasonal=True,
        is_premium=False,
        subscription_expires_at=None,
    )
    u_svc = MagicMock(get_or_create_telegram_user=AsyncMock(return_value=usr))
    u_svc.repo.session.commit = AsyncMock()
    cb = MagicMock(data="toggle_seasonal")
    cb.answer = AsyncMock()
    cb.from_user.id = 5
    cb.message.edit_reply_markup = AsyncMock()
    await mh.toggle_seasonal.__wrapped__(cb, u_svc)
    assert usr.notify_seasonal is False
    await mh.toggle_seasonal.__wrapped__(cb, u_svc)
    assert usr.notify_seasonal is True

    for lg in ("ru", "en", "de", "es", "fr", "pt"):
        for flag in (True, False):
            btns = [b for r in get_settings_keyboard(lg, seasonal=flag).inline_keyboard for b in r]
            seasonal = [b for b in btns if b.callback_data == "toggle_seasonal"]
            assert len(seasonal) == 1 and len(seasonal[0].text) <= 14, (lg, seasonal[0].text)


def test_scheduler_registers_new_jobs():
    from app.scheduler.setup import create_scheduler

    s = create_scheduler(MagicMock(), MagicMock())
    assert s.get_job("seasonal_nudges") and s.get_job("winback")
