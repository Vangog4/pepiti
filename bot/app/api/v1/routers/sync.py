from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user, get_db_session
from app.api.v1.routers.coach import _to_thread_response
from app.api.v1.routers.pets import _to_pet_response
from app.api.v1.routers.profile import get_profile
from app.api.v1.routers.subscription import get_subscription_status
from app.api.v1.routers.training import _to_plan_response, _to_task_response
from app.api.v1.schemas.pet import PetResponse
from app.api.v1.schemas.sync import (
    SyncPullResponse,
    SyncPushRequest,
    SyncPushResponse,
)
from app.infrastructure.db.models.coach_thread import CoachThreadModel
from app.infrastructure.db.models.pet import PetModel
from app.infrastructure.db.models.user import UserModel
from app.infrastructure.db.repositories.training_repo import TrainingPlanRepository
from app.services.training_service import TrainingService, tasks_for_today

router = APIRouter(prefix="/sync", tags=["Synchronization"])


async def _build_full_snapshot(user: UserModel, session: AsyncSession) -> SyncPullResponse:
    now = datetime.now(tz=UTC)

    # Profile
    profile = await get_profile(user)

    # Pets
    pets_res = await session.execute(
        select(PetModel).where(PetModel.user_id == user.id).order_by(PetModel.id)
    )
    pets_models = pets_res.scalars().all()
    pets: list[PetResponse] = [_to_pet_response(p) for p in pets_models]
    active_pet_id = pets[0].id if pets else None

    # Active training plan and today tasks
    active_plan = None
    today_tasks = []
    if active_pet_id:
        repo = TrainingPlanRepository(session)
        plan_model = await repo.get_active_plan(active_pet_id)
        if plan_model:
            active_plan = _to_plan_response(plan_model)
            t_today = tasks_for_today(plan_model)
            today_tasks = [_to_task_response(t) for t in t_today]

    # Coach threads
    threads_res = await session.execute(
        select(CoachThreadModel)
        .where(CoachThreadModel.user_id == user.id, CoachThreadModel.status == "active")
        .order_by(CoachThreadModel.updated_at.desc())
        .limit(10)
    )
    coach_threads = [_to_thread_response(th) for th in threads_res.scalars().all()]

    # Subscription
    subscription = await get_subscription_status(user)

    return SyncPullResponse(
        server_time=now,
        profile=profile,
        pets=pets,
        active_pet_id=active_pet_id,
        active_plan=active_plan,
        today_tasks=today_tasks,
        coach_threads=coach_threads,
        subscription=subscription,
    )


@router.get(
    "/pull",
    response_model=SyncPullResponse,
    summary="Pull full application state for client synchronization",
    description="Returns full snapshot of profile, pets, active training plan, today tasks, and threads.",
)
async def sync_pull(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    last_synced_at: Annotated[
        datetime | None,
        Query(description="Client's last sync timestamp for incremental checks"),
    ] = None,
) -> SyncPullResponse:
    return await _build_full_snapshot(current_user, session)


@router.post(
    "/push",
    response_model=SyncPushResponse,
    summary="Push offline changes (batch synchronization)",
    description="Applies offline task completions, profile modifications, and pet updates in a single batch.",
)
async def sync_push(
    body: SyncPushRequest,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> SyncPushResponse:
    now = datetime.now(tz=UTC)
    tasks_count = 0
    profile_updated = False
    pet_updated = False

    # 1. Apply offline task toggles
    if body.task_changes:
        repo = TrainingPlanRepository(session)
        svc = TrainingService(repo, ai_service=None)  # type: ignore[arg-type]

        # Load user pets
        pets_res = await session.execute(
            select(PetModel).where(PetModel.user_id == current_user.id)
        )
        user_pets = {p.id: p for p in pets_res.scalars().all()}

        for change in body.task_changes:
            task = await repo.get_task(change.task_id)
            if not task:
                continue
            plan = await repo.get_plan(task.plan_id)
            if not plan or plan.pet_id not in user_pets:
                continue

            target_pet = user_pets[plan.pet_id]
            if task.is_completed != change.is_completed:
                await svc.toggle_task(change.task_id, target_pet)
                tasks_count += 1

            if change.is_completed:
                if change.completed_at:
                    dt = change.completed_at
                    if dt.tzinfo is not None:
                        dt = dt.astimezone(UTC).replace(tzinfo=None)
                    task.completed_at = dt
            else:
                task.completed_at = None

        # Sync user streak with max pet streak
        max_streak = max([p.training_days or 0 for p in user_pets.values()], default=0)
        if max_streak > (current_user.training_days or 0):
            current_user.training_days = max_streak

    # 2. Apply profile update
    if body.profile_update:
        pu = body.profile_update
        if pu.first_name is not None:
            current_user.first_name = pu.first_name.strip()
        if pu.reminder_time is not None:
            current_user.reminder_time = pu.reminder_time.strip()
        if pu.timezone is not None:
            current_user.timezone = pu.timezone.strip()
        if pu.language_code is not None:
            current_user.language_code = pu.language_code.strip()
        profile_updated = True

    # 3. Apply pet update
    if body.pet_update and body.pet_id:
        p_res = await session.execute(
            select(PetModel).where(PetModel.id == body.pet_id, PetModel.user_id == current_user.id)
        )
        pet = p_res.scalar_one_or_none()
        if pet:
            for k, v in body.pet_update.model_dump(exclude_unset=True).items():
                if isinstance(v, str):
                    v = v.strip()
                setattr(pet, k, v)
            pet_updated = True

    await session.commit()
    await session.refresh(current_user)

    fresh_state = await _build_full_snapshot(current_user, session)
    return SyncPushResponse(
        synced_at=now,
        tasks_applied=tasks_count,
        profile_updated=profile_updated,
        pet_updated=pet_updated,
        current_state=fresh_state,
    )
