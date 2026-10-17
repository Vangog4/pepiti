from __future__ import annotations

from typing import Annotated
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user, get_db_session
from app.api.v1.schemas.training import PlanResponse, TaskResponse, TaskToggleResponse
from app.infrastructure.db.models.pet import PetModel
from app.infrastructure.db.models.training import TrainingPlanModel, TrainingTaskModel
from app.infrastructure.db.models.user import UserModel
from app.infrastructure.db.repositories.training_repo import TrainingPlanRepository
from app.services.pdf_service import generate_training_pdf
from app.services.training_service import TrainingService, tasks_for_today

router = APIRouter(prefix="/training", tags=["Training"])


def _to_task_response(task: TrainingTaskModel) -> TaskResponse:
    return TaskResponse(
        id=task.id,
        plan_id=task.plan_id,
        day_of_week=task.day_of_week,
        title=task.title,
        description=task.description,
        duration_minutes=task.duration_minutes,
        difficulty=task.difficulty,
        is_completed=bool(task.is_completed),
        completed_at=task.completed_at,
    )


def _to_plan_response(plan: TrainingPlanModel) -> PlanResponse:
    tasks = [_to_task_response(t) for t in (plan.tasks or [])]
    return PlanResponse(
        id=plan.id,
        pet_id=plan.pet_id,
        title=plan.title,
        goal=plan.goal,
        week_number=plan.week_number,
        is_active=bool(plan.is_active),
        tasks=tasks,
        created_at=plan.created_at,
    )


async def _get_target_pet(
    session: AsyncSession, user_id: int, pet_id: int | None = None
) -> PetModel:
    if pet_id:
        stmt = select(PetModel).where(PetModel.id == pet_id, PetModel.user_id == user_id)
    else:
        stmt = select(PetModel).where(PetModel.user_id == user_id).order_by(PetModel.id)
    res = await session.execute(stmt)
    pet = res.scalars().first()
    if pet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Питомец не найден. Сначала добавьте питомца в профиль.",
        )
    return pet


@router.get("/plan", response_model=PlanResponse, summary="Get active training plan")
async def get_active_plan(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    pet_id: Annotated[int | None, Query(description="Target pet ID (optional)")] = None,
) -> PlanResponse:
    pet = await _get_target_pet(session, current_user.id, pet_id)
    repo = TrainingPlanRepository(session)
    plan = await repo.get_active_plan(pet.id)
    if plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Активный план не найден")
    return _to_plan_response(plan)


@router.get("/today", response_model=list[TaskResponse], summary="Get tasks for today")
async def get_today_tasks(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    pet_id: Annotated[int | None, Query(description="Target pet ID (optional)")] = None,
) -> list[TaskResponse]:
    pet = await _get_target_pet(session, current_user.id, pet_id)
    repo = TrainingPlanRepository(session)
    plan = await repo.get_active_plan(pet.id)
    if plan is None:
        return []
    tasks = tasks_for_today(plan)
    return [_to_task_response(t) for t in tasks]


@router.post(
    "/tasks/{task_id}/toggle",
    response_model=TaskToggleResponse,
    summary="Toggle training task completion",
)
async def toggle_task(
    task_id: int,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> TaskToggleResponse:
    repo = TrainingPlanRepository(session)
    task = await repo.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задание не найдено")

    plan = await repo.get_plan(task.plan_id)
    if plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="План не найден")

    # Verify ownership
    pet_res = await session.execute(
        select(PetModel).where(PetModel.id == plan.pet_id, PetModel.user_id == current_user.id)
    )
    pet = pet_res.scalar_one_or_none()
    if pet is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа к этому заданию"
        )

    svc = TrainingService(repo, ai_service=None)  # type: ignore[arg-type]
    updated_task, day_done = await svc.toggle_task(task_id, pet)

    # Keep user.training_days in sync with pet.training_days
    if pet.training_days and (current_user.training_days or 0) < pet.training_days:
        current_user.training_days = pet.training_days
        await session.commit()

    return TaskToggleResponse(
        task_id=updated_task.id,
        is_completed=bool(updated_task.is_completed),
        completed_at=updated_task.completed_at,
        day_done=day_done,
        streak_days=pet.training_days or 0,
    )


@router.get("/pdf", summary="Export active training plan as PDF")
async def export_training_pdf(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    pet_id: Annotated[int | None, Query()] = None,
) -> Response:
    pet = await _get_target_pet(session, current_user.id, pet_id)
    repo = TrainingPlanRepository(session)
    plan = await repo.get_active_plan(pet.id)
    if plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="План не найден")

    tasks_data = [
        {
            "day_of_week": t.day_of_week,
            "title": t.title,
            "description": t.description,
            "duration_minutes": t.duration_minutes,
            "difficulty": t.difficulty,
            "is_completed": bool(t.is_completed),
        }
        for t in (plan.tasks or [])
    ]

    pdf_bytes = generate_training_pdf(
        pet_name=pet.name or "Питомец",
        plan_title=plan.title or "План тренировок",
        plan_goal=plan.goal or "",
        tasks=tasks_data,
        lang=current_user.language_code or "ru",
    )

    safe_ascii = "pepito_plan.pdf"
    encoded_filename = quote(f"pepito_plan_{pet.name or 'pet'}.pdf")
    return Response(
        content=bytes(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=\"{safe_ascii}\"; filename*=UTF-8''{encoded_filename}"
        },
    )
