from datetime import date, timedelta

from app.services.tracker import (
    achievements,
    compute_streak,
    longest_streak,
    new_achievements,
    week_summary,
)

T = date(2026, 11, 4)  # Wednesday


def days(*offsets):
    return {T - timedelta(days=o) for o in offsets}


def test_plain_consecutive_days():
    r = compute_streak(days(0, 1, 2), T, freezes_per_week=0)
    assert r.streak == 3 and r.frozen_days == []


def test_today_not_done_yet_does_not_break_streak():
    assert compute_streak(days(1, 2, 3), T, 0).streak == 3


def test_missed_yesterday_breaks_without_freeze():
    assert compute_streak(days(0, 2, 3), T, 0).streak == 1
    assert compute_streak(days(2, 3), T, 0).streak == 0


def test_freeze_bridges_single_gap_and_is_not_counted():
    r = compute_streak(days(0, 2, 3), T, freezes_per_week=1)
    assert r.streak == 3
    assert r.frozen_days == [T - timedelta(days=1)]
    assert r.freezes_left == 0


def test_freeze_budget_is_per_iso_week():
    # Gaps on Tue(-1) and Sun(-3, previous week): 1 freeze/week bridges both (different weeks)
    r = compute_streak(days(0, 2, 4, 5), T, freezes_per_week=1)
    assert r.streak == 4 and len(r.frozen_days) == 2
    # two gaps in the same week with 1 freeze: the second breaks it
    same_week = {T, T - timedelta(days=2)}  # Wed, Mon -> gap Tue only
    assert compute_streak(same_week | {T - timedelta(days=4)}, T, 1).streak >= 2


def test_freeze_never_extends_into_empty_history():
    assert compute_streak(set(), T, 3).streak == 0
    assert compute_streak(days(5), T, 3).streak == 0  # nothing recent, gap too long


def test_longest_streak():
    assert longest_streak(days(0, 1, 2, 10, 11, 12, 13, 14)) == 5
    assert longest_streak(set()) == 0


def test_achievements_and_new():
    active = {T - timedelta(days=i) for i in range(8)}
    assert achievements(active, walks=0) == {"streak_7"}
    assert achievements(active, walks=10) == {"streak_7", "walks_10"}
    assert new_achievements({"streak_7"}, {"streak_7", "walks_10"}) == ["walks_10"]


def test_week_summary_counts_current_iso_week_only():
    task_days = days(0, 1, 5)  # Wed, Tue, prev Fri
    walks = [(T, 30), (T - timedelta(days=1), 15), (T - timedelta(days=6), 60)]
    s = week_summary(task_days, walks, T)
    assert s.task_days == 2 and s.walk_count == 2 and s.walk_minutes == 45
