"""Streaks with freezes, achievements and weekly summary. Pure functions, no I/O.

All dates are the user's LOCAL dates; callers convert before calling.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta

from app.logic.rules import rule


def freezes_per_week(premium: bool) -> int:
    key = "tracker.freezes_per_week_premium" if premium else "tracker.freezes_per_week_free"
    return int(rule(key, 3 if premium else 1))


@dataclass
class StreakResult:
    streak: int = 0
    frozen_days: list[date] = field(default_factory=list)
    freezes_left: int = 0


def _week(d: date) -> tuple[int, int]:
    iso = d.isocalendar()
    return iso[0], iso[1]


def compute_streak(active: set[date], today: date, freezes_per_week: int) -> StreakResult:
    """Consecutive active days ending today (or yesterday while today is still open).

    A single missing day is bridged by a freeze if the week's budget allows and the
    day before it was active; a frozen day keeps the streak alive but is not counted.
    """
    used: dict[tuple[int, int], int] = {}
    frozen: list[date] = []
    streak = 0
    d = today if today in active else today - timedelta(days=1)
    while True:
        if d in active:
            streak += 1
            d -= timedelta(days=1)
            continue
        wk = _week(d)
        if used.get(wk, 0) < freezes_per_week and (d - timedelta(days=1)) in active:
            used[wk] = used.get(wk, 0) + 1
            frozen.append(d)
            d -= timedelta(days=1)
            continue
        break
    left = max(0, freezes_per_week - used.get(_week(today), 0))
    return StreakResult(streak=streak, frozen_days=sorted(frozen), freezes_left=left)


def longest_streak(active: set[date]) -> int:
    best = run = 0
    prev: date | None = None
    for d in sorted(active):
        run = run + 1 if prev is not None and (d - prev).days == 1 else 1
        best = max(best, run)
        prev = d
    return best


def achievements(active: set[date], walks: int) -> set[str]:
    out = {
        f"streak_{n}"
        for n in rule("tracker.streak_badges", [7, 30, 100])
        if longest_streak(active) >= n
    }
    if walks >= int(rule("tracker.walks_for_badge", 10)):
        out.add("walks_10")
    return out


def new_achievements(before: set[str], after: set[str]) -> list[str]:
    return sorted(after - before)


@dataclass
class WeekSummary:
    task_days: int
    walk_count: int
    walk_minutes: int


def week_summary(task_days: set[date], walks: list[tuple[date, int]], today: date) -> WeekSummary:
    wk = _week(today)
    in_week = [(d, m) for d, m in walks if _week(d) == wk]
    return WeekSummary(
        task_days=sum(1 for d in task_days if _week(d) == wk),
        walk_count=len(in_week),
        walk_minutes=sum(m for _, m in in_week),
    )


def snapshot(rows: list, today: date, premium: bool) -> dict:
    """Everything the tracker screen needs from raw activity rows."""
    task_days = {r.local_date for r in rows if r.kind == "task"}
    walks = [(r.local_date, r.duration_min or 0) for r in rows if r.kind == "walk"]
    active = task_days | {d for d, _ in walks}
    res = compute_streak(active, today, freezes_per_week(premium))
    return {
        "streak": res.streak,
        "freezes_left": res.freezes_left,
        "frozen": res.frozen_days,
        "done_today": today in active,
        "week": week_summary(task_days, walks, today),
        "badges": achievements(active, len(walks)),
        "active": active,
        "walks": len(walks),
    }
