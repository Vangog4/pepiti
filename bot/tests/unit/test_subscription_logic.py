"""Logic tests for premium stacking / expire / task matching (no DB)."""

from __future__ import annotations

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.subscription_service import PREMIUM_DURATION_DAYS, SubscriptionService
from app.services.training_service import TrainingService


@pytest.mark.asyncio
async def test_activate_stacks_on_existing_expiry():
    """Paid Stars must extend from current end, not overwrite with now+30."""
    now = datetime.utcnow()
    far = now + timedelta(days=40)

    sub_repo = MagicMock()
    sub_repo.get_by_charge_id = AsyncMock(return_value=None)
    sub_repo.max_active_expires_at = AsyncMock(return_value=far)
    created = MagicMock()
    sub_repo.create = AsyncMock(return_value=created)
    sub_repo.session = MagicMock()
    sub_repo.session.commit = AsyncMock()

    user = MagicMock()
    user.is_premium = False
    user.subscription_expires_at = far
    user_repo = MagicMock()
    user_repo.get_by_telegram_id = AsyncMock(return_value=user)

    svc = SubscriptionService(sub_repo, user_repo)
    await svc.activate(user_id=1, telegram_id=100, charge_id="ch_1")

    kwargs = sub_repo.create.await_args.kwargs
    expires = kwargs["expires_at"]
    # must be ~ far + 30d, not now+30
    assert expires > far + timedelta(days=PREMIUM_DURATION_DAYS - 1)
    assert expires < far + timedelta(days=PREMIUM_DURATION_DAYS + 1)
    assert user.is_premium is True
    assert user.subscription_expires_at == expires


@pytest.mark.asyncio
async def test_activate_idempotent_on_same_charge():
    existing = MagicMock()
    sub_repo = MagicMock()
    sub_repo.get_by_charge_id = AsyncMock(return_value=existing)
    sub_repo.create = AsyncMock()
    user_repo = MagicMock()

    svc = SubscriptionService(sub_repo, user_repo)
    out = await svc.activate(user_id=1, telegram_id=100, charge_id="ch_dup")
    assert out is existing
    sub_repo.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_mark_task_by_hint_no_guess_when_ambiguous():
    """With 2 incomplete tasks and bad hint — do not mark random task."""
    t1 = MagicMock()
    t1.id = 1
    t1.title = "Сидеть"
    t1.is_completed = False
    t2 = MagicMock()
    t2.id = 2
    t2.title = "Лежать"
    t2.is_completed = False

    plan = MagicMock()
    plan.week_number = None
    plan.tasks = [t1, t2]

    plan_repo = MagicMock()
    plan_repo.get_active_plan = AsyncMock(return_value=plan)
    ai = MagicMock()
    svc = TrainingService(plan_repo, ai)
    svc.toggle_task = AsyncMock()

    task, done = await svc.mark_task_by_hint(MagicMock(), "непонятный хинт")
    assert task is None
    assert done is False
    svc.toggle_task.assert_not_awaited()


@pytest.mark.asyncio
async def test_mark_task_by_hint_single_incomplete_ok():
    t1 = MagicMock()
    t1.id = 7
    t1.title = "Сидеть"
    t1.is_completed = False
    plan = MagicMock()
    plan.week_number = None
    plan.tasks = [t1]

    plan_repo = MagicMock()
    plan_repo.get_active_plan = AsyncMock(return_value=plan)
    svc = TrainingService(plan_repo, MagicMock())
    svc.toggle_task = AsyncMock(return_value=(t1, True))

    task, done = await svc.mark_task_by_hint(MagicMock(), "")
    assert task is t1
    assert done is True
    svc.toggle_task.assert_awaited_once_with(7, svc.toggle_task.await_args.args[1])


@pytest.mark.asyncio
async def test_mark_task_by_hint_week_plan_filters_by_today():
    from app.services.training_service import iso_weekday

    dow = iso_weekday()
    other_dow = (dow % 7) + 1

    t_today = MagicMock()
    t_today.id = 10
    t_today.day_of_week = dow
    t_today.title = "Рядом"
    t_today.is_completed = False

    t_other = MagicMock()
    t_other.id = 11
    t_other.day_of_week = other_dow
    t_other.title = "Голос"
    t_other.is_completed = False

    plan = MagicMock()
    plan.week_number = 35
    plan.tasks = [t_today, t_other]

    plan_repo = MagicMock()
    plan_repo.get_active_plan = AsyncMock(return_value=plan)
    svc = TrainingService(plan_repo, MagicMock())
    svc.toggle_task = AsyncMock(return_value=(t_today, False))

    task, done = await svc.mark_task_by_hint(MagicMock(), "рядом")
    assert task is t_today
    assert done is False
    svc.toggle_task.assert_awaited_once_with(10, svc.toggle_task.await_args.args[1])
