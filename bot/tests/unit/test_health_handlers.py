from datetime import UTC, date, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.bot.handlers import health as hh
from app.scheduler.jobs import reminders as rem

TODAY = date(2026, 11, 1)


def _usr(tz="UTC"):
    return MagicMock(
        get_or_create_telegram_user=AsyncMock(
            return_value=SimpleNamespace(language_code="ru", id=1, timezone=tz)
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


def test_text_shows_each_status():
    ev = lambda i, k, due: SimpleNamespace(id=i, kind=k, done_at=date(2026, 1, i), next_due_at=due)  # noqa: E731
    txt = hh.health_text("Рекс", [ev(1, "ticks", date(2026, 10, 30))], TODAY, "ru")
    assert "просрочено на 2" in txt
    assert "не отмечено" in txt  # vaccine / worms never logged


def test_keyboard_labels_fit_14():
    for lg in ("ru", "en", "de", "es", "fr", "pt"):
        for row in hh.health_kb(lg).inline_keyboard[:1]:
            assert all(len(b.text) <= 14 for b in row)


@pytest.mark.asyncio
async def test_log_today_creates_next_cycle():
    repo = MagicMock(add=AsyncMock(return_value=SimpleNamespace(next_due_at=date(2026, 12, 1))))
    await hh.log_today.__wrapped__(_cb("hl_today:ticks"), _usr(), _pets(), repo)
    pet_id, kind, done, due = repo.add.await_args.args
    assert (pet_id, kind) == (7, "ticks") and due.toordinal() - done.toordinal() == 30


@pytest.mark.asyncio
async def test_unknown_kind_is_rejected():
    repo = MagicMock(add=AsyncMock())
    await hh.log_today.__wrapped__(_cb("hl_today:evil"), _usr(), _pets(), repo)
    repo.add.assert_not_awaited()


@pytest.mark.asyncio
async def test_done_and_snooze_are_ownership_scoped():
    repo = MagicMock(get_owned=AsyncMock(return_value=None), add=AsyncMock(), snooze=AsyncMock())
    await hh.push_done.__wrapped__(_cb("hl_done:42"), _usr(), _pets(), repo)
    await hh.push_snooze.__wrapped__(_cb("hl_snooze:42"), _usr(), repo)
    repo.get_owned.assert_awaited_with(42, 1)  # user id from DB, not from the callback
    repo.add.assert_not_awaited()
    repo.snooze.assert_not_awaited()


@pytest.mark.asyncio
async def test_snooze_moves_due_date():
    ev = SimpleNamespace(next_due_at=date(2026, 11, 4))
    repo = MagicMock(get_owned=AsyncMock(return_value=ev), snooze=AsyncMock())
    cb = _cb("hl_snooze:1")
    await hh.push_snooze.__wrapped__(cb, _usr(), repo)
    repo.snooze.assert_awaited_once_with(ev, 3)


@pytest.mark.asyncio
async def test_bad_date_text_is_rejected():
    st = MagicMock(get_data=AsyncMock(return_value={"health_kind": "ticks"}), clear=AsyncMock())
    msg = MagicMock(text="завтра")
    msg.from_user.id = 5
    msg.answer = AsyncMock()
    repo = MagicMock(add=AsyncMock())
    await hh.save_date.__wrapped__(msg, st, _usr(), _pets(), repo)
    repo.add.assert_not_awaited()


@pytest.mark.asyncio
async def test_push_job_sends_once_and_marks_notified(monkeypatch):
    ev = SimpleNamespace(
        id=3,
        kind="ticks",
        pet_id=7,
        done_at=date(2026, 10, 2),
        next_due_at=date(2026, 11, 1),
        last_notified_on=None,
    )
    user = SimpleNamespace(
        id=1, telegram_id=99, language_code="ru", timezone="UTC", reminder_time="10:00"
    )
    pet = SimpleNamespace(id=7, name="Рекс", user_id=1)

    def result(rows):
        r = MagicMock()
        r.scalars.return_value.all.return_value = rows
        return r

    session = MagicMock()
    session.execute = AsyncMock(side_effect=[result([pet]), result([ev])])
    session.commit = AsyncMock()
    ctx = MagicMock(
        __aenter__=AsyncMock(return_value=session), __aexit__=AsyncMock(return_value=False)
    )
    monkeypatch.setattr(rem, "_get_users_due_now", AsyncMock(return_value=[user]))
    bot = MagicMock(send_message=AsyncMock())
    real = rem.datetime
    monkeypatch.setattr(
        rem,
        "datetime",
        SimpleNamespace(now=lambda tz=None: datetime(2026, 11, 1, 10, 0, tzinfo=UTC)),
    )
    await rem.send_health_reminders(MagicMock(return_value=ctx), bot)
    rem.datetime = real
    bot.send_message.assert_awaited_once()
    assert ev.last_notified_on == date(2026, 11, 1)
    assert "hl_done:3" in str(bot.send_message.await_args.kwargs["reply_markup"])
