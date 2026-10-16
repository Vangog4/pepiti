"""WebApp ↔ bot sync: today-filter, streak, initData, reminder 'off'."""

from __future__ import annotations

import hashlib
import hmac
import time
from datetime import date
from unittest.mock import AsyncMock, MagicMock
from urllib.parse import urlencode

import pytest

from app.api.auth import validate_init_data
from app.api.routes import _validate_settings
from app.services.training_service import TrainingService, iso_weekday, tasks_for_today


def test_tasks_for_today_week_plan_filters_iso_weekday():
    today = iso_weekday()
    other = 7 if today == 1 else 1
    t_today = MagicMock(day_of_week=today, title="today")
    t_other = MagicMock(day_of_week=other, title="other")
    plan = MagicMock(week_number=12, tasks=[t_today, t_other])
    assert tasks_for_today(plan) == [t_today]


def test_tasks_for_today_daily_plan_keeps_all():
    tasks = [MagicMock(day_of_week=0), MagicMock(day_of_week=1)]
    plan = MagicMock(week_number=None, tasks=tasks)
    assert tasks_for_today(plan) == tasks


def test_tasks_for_today_empty():
    assert tasks_for_today(None) == []
    assert tasks_for_today(MagicMock(tasks=[], week_number=3)) == []


def _sign(token: str, auth_date: int, user_id: int = 1) -> str:
    params = {
        "auth_date": str(auth_date),
        "query_id": "AAQA",
        "user": '{"id":%d,"first_name":"QA"}' % user_id,
    }
    data_check = "\n".join(f"{k}={v}" for k, v in sorted(params.items()))
    secret = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    params["hash"] = hmac.new(secret, data_check.encode(), hashlib.sha256).hexdigest()
    return urlencode(params)


def test_init_data_accepts_fresh_hash():
    token = "test-bot-token"
    raw = _sign(token, int(time.time()))
    parsed = validate_init_data(raw, token)
    assert parsed is not None
    assert parsed["user"]["id"] == 1


def test_init_data_rejects_bad_hash():
    token = "test-bot-token"
    raw = _sign(token, int(time.time())).replace("hash=", "hash=dead")
    assert validate_init_data(raw, token) is None


def test_init_data_rejects_stale_auth_date():
    token = "test-bot-token"
    raw = _sign(token, int(time.time()) - 3 * 24 * 3600)
    assert validate_init_data(raw, token) is None


def test_validate_settings_allows_off():
    assert _validate_settings({"reminder_time": "off"}, "en") == []
    assert _validate_settings({"reminder_time": "09:30"}, "en") == []
    errs = _validate_settings({"reminder_time": "99:99"}, "en")
    assert errs and errs[0]["field"] == "reminder_time"
    assert "HH:MM" in errs[0]["msg"] or "09:30" in errs[0]["msg"]


@pytest.mark.asyncio
async def test_toggle_week_task_increments_training_days_once():
    today = iso_weekday()
    task = MagicMock()
    task.id = 9
    task.plan_id = 3
    task.day_of_week = today
    task.is_completed = False
    task.completed_at = None

    plan = MagicMock()
    plan.week_number = 34
    plan.plan_json = {}

    pet = MagicMock()
    pet.training_days = 2

    repo = MagicMock()
    repo.get_task = AsyncMock(return_value=task)
    repo.get_plan = AsyncMock(return_value=plan)
    repo.day_tasks_done = AsyncMock(return_value=True)
    repo.session = MagicMock()
    repo.session.commit = AsyncMock()

    svc = TrainingService(repo, MagicMock())
    out, day_done = await svc.toggle_task(9, pet)
    assert out is task
    assert day_done is True
    assert task.is_completed is True
    assert pet.training_days == 3
    assert plan.plan_json.get(f"counted_day_{today}") == date.today().isoformat()

    # second completion of the same day must not double-count
    task.is_completed = False
    out, _ = await svc.toggle_task(9, pet)
    assert pet.training_days == 3


@pytest.mark.asyncio
async def test_toggle_daily_plan_uses_counted_at():
    task = MagicMock()
    task.id = 1
    task.plan_id = 8
    task.day_of_week = 0
    task.is_completed = False
    task.completed_at = None

    plan = MagicMock()
    plan.week_number = None
    plan.plan_json = {}

    pet = MagicMock()
    pet.training_days = 0

    repo = MagicMock()
    repo.get_task = AsyncMock(return_value=task)
    repo.get_plan = AsyncMock(return_value=plan)
    repo.all_tasks_done = AsyncMock(return_value=True)
    repo.session = MagicMock()
    repo.session.commit = AsyncMock()

    svc = TrainingService(repo, MagicMock())
    _, done = await svc.toggle_task(1, pet)
    assert done is True
    assert pet.training_days == 1
    assert plan.plan_json.get("counted_at") == date.today().isoformat()
