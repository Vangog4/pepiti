"""Health calendar logic (vaccines / ticks / worms). Pure functions, no I/O."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from app.logic.rules import rule

KINDS = ("vaccine", "ticks", "worms")
_DEFAULT_INTERVALS = {"vaccine": 365, "ticks": 30, "worms": 90}


def interval_days(kind: str) -> int:
    if kind not in KINDS:
        raise ValueError(f"unknown health kind: {kind}")
    intervals = rule("health.intervals", _DEFAULT_INTERVALS) or _DEFAULT_INTERVALS
    return int(intervals.get(kind, _DEFAULT_INTERVALS[kind]))


def remind_days_before() -> int:
    return int(rule("health.remind_days_before", 3))


def snooze_days() -> int:
    return int(rule("health.snooze_days", 3))


def next_due_after(kind: str, done_on: date) -> date:
    return done_on + timedelta(days=interval_days(kind))


def status_of(next_due: date, today: date) -> str:
    """overdue | today | soon (within the reminder window) | later."""
    delta = (next_due - today).days
    if delta < 0:
        return "overdue"
    if delta == 0:
        return "today"
    if delta <= remind_days_before():
        return "soon"
    return "later"


def latest_per_kind(events: list[Any]) -> dict[str, Any]:
    """The current schedule per kind = the most recently done record."""
    out: dict[str, Any] = {}
    for e in sorted(events, key=lambda x: (x.done_at, x.id)):
        out[e.kind] = e
    return out


def reminders_due(events: list[Any], today: date) -> list[Any]:
    """Records to ping about today: exactly N days before, and on the day. Once per day."""
    due = []
    for e in latest_per_kind(events).values():
        if getattr(e, "last_notified_on", None) == today:
            continue
        if (e.next_due_at - today).days in (remind_days_before(), 0):
            due.append(e)
    return sorted(due, key=lambda e: e.id)


def parse_past_date(raw: str, today: date) -> date:
    """dd.mm.yyyy that is not in the future and not older than 5 years."""
    try:
        d, m, y = (
            int(x) for x in (raw or "").strip().replace("/", ".").replace("-", ".").split(".")
        )
        value = date(y, m, d)
    except ValueError as exc:
        raise ValueError("bad date") from exc
    if value > today or (today - value).days > 5 * 366:
        raise ValueError("date out of range")
    return value
