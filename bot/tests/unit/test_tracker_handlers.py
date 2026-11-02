from datetime import UTC, date, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.bot.handlers import tracker as th
from app.scheduler.jobs import reports as rp


def _usr(tz="UTC", premium=False):
    return MagicMock(
        get_or_create_telegram_user=AsyncMock(
            return_value=SimpleNamespace(
                language_code="ru",
                id=1,
                timezone=tz,
                is_premium=premium,
                subscription_expires_at=None,
            )
        )
    )


def _pets():
    return MagicMock(get_pet=AsyncMock(return_value=SimpleNamespace(id=7, name="Рекс")))


def _cb(data):
    cb = MagicMock(data=data)
    cb.answer = AsyncMock()
    cb.from_user.id = 5
    cb.message.edit_text = AsyncMock()
    return cb


def row(kind, d, m=None):
    return SimpleNamespace(kind=kind, local_date=d, duration_min=m)


@pytest.mark.asyncio
async def test_walk_only_accepts_offered_durations():
    repo = MagicMock(log_walk=AsyncMock(), rows=AsyncMock(return_value=[]))
    await th.log_walk.__wrapped__(_cb("tr_walk:999"), _usr(), _pets(), repo)
    await th.log_walk.__wrapped__(_cb("tr_walk:x"), _usr(), _pets(), repo)
    repo.log_walk.assert_not_awaited()


@pytest.mark.asyncio
async def test_walk_logged_and_screen_updated():
    repo = MagicMock(
        log_walk=AsyncMock(), rows=AsyncMock(return_value=[row("walk", date.today(), 30)])
    )
    cb = _cb("tr_walk:30")
    await th.log_walk.__wrapped__(cb, _usr(), _pets(), repo)
    assert repo.log_walk.await_args.args[0] == 7 and repo.log_walk.await_args.args[2] == 30
    cb.message.edit_text.assert_awaited()


@pytest.mark.asyncio
async def test_record_task_day_idempotent_and_reports_new_badge():
    from datetime import timedelta

    today = datetime.now(UTC).date()
    history = [row("task", today - timedelta(days=i)) for i in range(1, 7)]
    repo = MagicMock(
        rows=AsyncMock(side_effect=[history, history + [row("task", today)]]),
        log_task_day=AsyncMock(return_value=True),
    )
    usr = SimpleNamespace(timezone="UTC")
    assert await th.record_task_day(repo, SimpleNamespace(id=7), usr) == ["streak_7"]

    repo2 = MagicMock(
        rows=AsyncMock(return_value=history), log_task_day=AsyncMock(return_value=False)
    )
    assert await th.record_task_day(repo2, SimpleNamespace(id=7), usr) == []


def test_keyboard_and_text_fit_all_locales():
    snap = {
        "streak": 3,
        "freezes_left": 1,
        "frozen": [],
        "done_today": True,
        "week": SimpleNamespace(task_days=2, walk_count=1, walk_minutes=30),
        "badges": {"streak_7"},
        "walks": 1,
        "active": set(),
    }
    for lg in ("ru", "en", "de", "es", "fr", "pt"):
        kb = th.tracker_kb(lg)
        assert all(len(b.text) <= 14 for b in kb.inline_keyboard[0])
        txt = th.tracker_text("Рекс", snap, lg)
        assert "{" not in txt and "tracker." not in txt


def test_report_due_uses_local_sunday_evening_once():
    sun_16_utc = datetime(2026, 11, 1, 16, 0, tzinfo=UTC)  # Sunday
    assert sun_16_utc.weekday() == 6
    msk = SimpleNamespace(timezone="Europe/Moscow", weekly_report_sent_on=None)  # 19:00 local
    utc = SimpleNamespace(timezone="UTC", weekly_report_sent_on=None)  # 16:00 local
    assert rp.report_due(msk, sun_16_utc) is True
    assert rp.report_due(utc, sun_16_utc) is False
    msk.weekly_report_sent_on = date(2026, 11, 1)
    assert rp.report_due(msk, sun_16_utc) is False
    assert (
        rp.report_due(
            SimpleNamespace(timezone="UTC", weekly_report_sent_on=None),
            datetime(2026, 11, 2, 20, 0, tzinfo=UTC),
        )
        is False
    )  # Monday
