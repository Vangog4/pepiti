from datetime import date
from types import SimpleNamespace

import pytest

from app.services.health import (
    KINDS,
    latest_per_kind,
    next_due_after,
    parse_past_date,
    reminders_due,
    status_of,
)

T = date(2026, 11, 1)


def ev(id, kind, done, due, notified=None):
    return SimpleNamespace(
        id=id, kind=kind, done_at=done, next_due_at=due, last_notified_on=notified
    )


def test_intervals_from_rules():
    assert next_due_after("ticks", date(2026, 11, 1)) == date(2026, 12, 1)
    assert next_due_after("worms", date(2026, 11, 1)) == date(2027, 1, 30)
    assert next_due_after("vaccine", date(2026, 11, 1)) == date(2027, 11, 1)
    assert set(KINDS) == {"vaccine", "ticks", "worms"}
    with pytest.raises(ValueError):
        next_due_after("bogus", T)


@pytest.mark.parametrize(
    "due,expected",
    [
        (date(2026, 10, 30), "overdue"),
        (date(2026, 11, 1), "today"),
        (date(2026, 11, 4), "soon"),
        (date(2026, 11, 5), "later"),
    ],
)
def test_status(due, expected):
    assert status_of(due, T) == expected


def test_latest_per_kind_picks_newest_done():
    old = ev(1, "ticks", date(2026, 8, 1), date(2026, 8, 31))
    new = ev(2, "ticks", date(2026, 10, 2), date(2026, 11, 1))
    other = ev(3, "worms", date(2026, 9, 1), date(2026, 11, 30))
    out = latest_per_kind([old, new, other])
    assert out["ticks"].id == 2 and out["worms"].id == 3 and "vaccine" not in out


def test_reminders_three_days_before_and_on_day_once():
    events = [
        ev(1, "ticks", date(2026, 10, 2), date(2026, 11, 4)),  # in 3 days
        ev(2, "worms", date(2026, 8, 1), date(2026, 11, 1)),  # today
        ev(3, "vaccine", date(2026, 1, 1), date(2026, 11, 10)),  # later
        ev(4, "ticks", date(2026, 9, 1), date(2026, 11, 1), notified=T),  # already pinged today
    ]
    got = reminders_due(events, T)
    assert [e.id for e in got] == [1, 2]


def test_overdue_events_do_not_spam_after_day_of():
    assert reminders_due([ev(1, "ticks", date(2026, 9, 1), date(2026, 10, 1))], T) == []


def test_parse_past_date():
    assert parse_past_date("01.10.2026", T) == date(2026, 10, 1)
    for bad in ("02.11.2026", "x", "31.02.2026", "01.01.2000"):
        with pytest.raises(ValueError):
            parse_past_date(bad, T)
