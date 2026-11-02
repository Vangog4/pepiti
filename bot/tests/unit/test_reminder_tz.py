from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.tz_utils import local_now
from app.scheduler.jobs.reminders import _get_users_due_now


def test_iana_zone_with_half_hour_and_offset_formats():
    now = datetime(2026, 11, 1, 7, 0, tzinfo=UTC)
    assert local_now("Europe/Moscow", now).strftime("%H:%M") == "10:00"
    assert local_now("Asia/Kolkata", now).strftime("%H:%M") == "12:30"
    assert local_now("UTC+3", now).strftime("%H:%M") == "10:00"
    assert local_now(None, now).strftime("%H:%M") == "07:00"
    assert local_now("Not/AZone", now).strftime("%H:%M") == "07:00"


@pytest.mark.asyncio
async def test_due_users_by_local_time():
    now = datetime(2026, 11, 1, 7, 0, tzinfo=UTC)
    mk = lambda tz, rt: SimpleNamespace(timezone=tz, reminder_time=rt)  # noqa: E731
    users = [
        mk("Europe/Moscow", None),
        mk("UTC", None),
        mk("UTC+3", "10:00"),
        mk("Asia/Kolkata", "12:30"),
    ]
    res = MagicMock()
    res.scalars.return_value.all.return_value = users
    session = MagicMock()
    session.execute = AsyncMock(return_value=res)
    due = await _get_users_due_now(session, "07:00", now)
    assert due == [users[0], users[2], users[3]]
