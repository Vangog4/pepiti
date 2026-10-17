from __future__ import annotations

import asyncio
import time
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user, get_db_session
from app.api.v1.schemas.coach import (
    CoachMessage,
    CoachThreadDetailResponse,
    CoachThreadResponse,
    SendMessageRequest,
    SendMessageResponse,
)
from app.core.config import settings
from app.infrastructure.db.models.coach_thread import CoachThreadModel
from app.infrastructure.db.models.pet import PetModel
from app.infrastructure.db.models.user import UserModel
from app.infrastructure.db.repositories.coach_thread_repo import CoachThreadRepository
from app.services.ai_service import AiService
from app.services.coach_service import CoachService

router = APIRouter(prefix="/coach", tags=["AI Coach"])


def _to_thread_response(th: CoachThreadModel) -> CoachThreadResponse:
    return CoachThreadResponse(
        id=th.id,
        title=th.title,
        status=th.status or "active",
        summary=th.summary,
        message_count=th.message_count or 0,
        created_at=th.created_at,
        updated_at=th.updated_at,
    )


@router.get(
    "/threads",
    response_model=list[CoachThreadResponse],
    summary="List AI coach conversation threads",
)
async def list_threads(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    status_filter: Annotated[
        str, Query(alias="status", description="active, archived, or all")
    ] = "active",
) -> list[CoachThreadResponse]:
    stmt = select(CoachThreadModel).where(CoachThreadModel.user_id == current_user.id)
    if status_filter in ("active", "archived"):
        stmt = stmt.where(CoachThreadModel.status == status_filter)
    stmt = stmt.order_by(CoachThreadModel.updated_at.desc())

    res = await session.execute(stmt)
    threads = res.scalars().all()
    return [_to_thread_response(th) for th in threads]


@router.post(
    "/threads",
    response_model=CoachThreadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new conversation thread",
)
async def create_thread(
    current_user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    title: Annotated[str | None, Query(description="Optional custom title")] = None,
) -> CoachThreadResponse:
    thread = CoachThreadModel(
        user_id=current_user.id,
        title=title.strip() if title else None,
        status="active",
        message_count=0,
        messages_json=[],
    )
    session.add(thread)
    await session.commit()
    await session.refresh(thread)

    current_user.active_coach_thread_id = thread.id
    await session.commit()
    return _to_thread_response(thread)


@router.get(
    "/threads/{thread_id}",
    response_model=CoachThreadDetailResponse,
    summary="Get thread conversation history",
)
async def get_thread_detail(
    thread_id: int,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> CoachThreadDetailResponse:
    stmt = select(CoachThreadModel).where(
        CoachThreadModel.id == thread_id, CoachThreadModel.user_id == current_user.id
    )
    res = await session.execute(stmt)
    thread = res.scalar_one_or_none()
    if thread is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Диалог не найден")

    msgs = []
    for item in thread.messages_json or []:
        msgs.append(
            CoachMessage(
                role=item.get("role", "coach"),
                content=item.get("content", ""),
                ts=item.get("ts"),
            )
        )

    return CoachThreadDetailResponse(
        id=thread.id,
        title=thread.title,
        status=thread.status,
        summary=thread.summary,
        messages=msgs,
    )


@router.post(
    "/threads/{thread_id}/messages",
    response_model=SendMessageResponse,
    summary="Send question to AI coach and get response",
)
async def send_coach_message(
    thread_id: int,
    body: SendMessageRequest,
    request: Request,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> SendMessageResponse:
    stmt = select(CoachThreadModel).where(
        CoachThreadModel.id == thread_id, CoachThreadModel.user_id == current_user.id
    )
    res = await session.execute(stmt)
    thread = res.scalar_one_or_none()
    if thread is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Диалог не найден")

    # Get pet for context
    pet_stmt = select(PetModel).where(PetModel.user_id == current_user.id).order_by(PetModel.id)
    pet_res = await session.execute(pet_stmt)
    pet = pet_res.scalars().first()
    if pet is None:
        # Create minimal fallback pet so cynologist has context
        pet = PetModel(
            name="Собака", breed="Не указана", age_category="Взрослый (3–7 лет)", training_level="1"
        )

    repo = CoachThreadRepository(session)
    coach_svc = CoachService(repo)
    lang = current_user.language_code or "ru"
    context = coach_svc.build_prompt_context(
        thread, is_premium=bool(current_user.is_premium), lang=lang
    )

    history_with_q = (context + "\n" if context else "") + f"Владелец: {body.content}\n"

    from app.infrastructure.redis.ai_rate_limit import AiRateLimiter

    rate_limiter = AiRateLimiter(settings.REDIS_URL)
    user_uid = current_user.telegram_id or current_user.id
    if not current_user.is_premium:
        if not await rate_limiter.is_allowed(user_uid):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Дневной лимит бесплатных запросов к кинологу исчерпан. Оформите Premium.",
            )

    ai_service: AiService | None = getattr(request.app.state, "ai_service", None)
    if ai_service is None:
        ai_service = AiService(api_key=settings.GEMINI_API_KEY)
        request.app.state.ai_service = ai_service

    try:
        answer = await ai_service.answer_coach_question(pet, history_with_q, lang=lang)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Не удалось получить ответ кинолога: {e}",
        ) from e

    if not current_user.is_premium:
        await rate_limiter.increment(user_uid)

    now_ts = int(time.time())
    coach_svc.save_exchange(thread, body.content, answer)
    await session.commit()
    await session.refresh(thread)

    # Background title & summary generation if needed
    if coach_svc.should_generate_title(thread):

        async def _gen_title():
            session_factory = request.app.state.session_factory
            async with session_factory() as s:
                t_repo = CoachThreadRepository(s)
                th = await t_repo.get(thread.id)
                if th and not th.title:
                    th.title = await ai_service.generate_thread_title(body.content)
                    await s.commit()

        asyncio.create_task(_gen_title())

    return SendMessageResponse(
        thread_id=thread.id,
        user_message=CoachMessage(role="user", content=body.content, ts=now_ts),
        coach_message=CoachMessage(role="coach", content=answer, ts=now_ts),
    )


@router.patch(
    "/threads/{thread_id}/archive", response_model=CoachThreadResponse, summary="Archive thread"
)
async def archive_thread(
    thread_id: int,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> CoachThreadResponse:
    stmt = select(CoachThreadModel).where(
        CoachThreadModel.id == thread_id, CoachThreadModel.user_id == current_user.id
    )
    res = await session.execute(stmt)
    thread = res.scalar_one_or_none()
    if thread is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Диалог не найден")

    thread.status = "archived"
    await session.commit()
    await session.refresh(thread)
    return _to_thread_response(thread)
