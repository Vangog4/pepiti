from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes import _validate_settings
from app.api.v1.dependencies import get_current_user, get_db_session
from app.api.v1.schemas.profile import ProfileResponse, ProfileUpdateRequest
from app.infrastructure.db.models.user import UserModel

router = APIRouter(prefix="/profile", tags=["User Profile"])


@router.get("", response_model=ProfileResponse, summary="Get current user profile and settings")
async def get_profile(
    current_user: Annotated[UserModel, Depends(get_current_user)],
) -> ProfileResponse:
    tid = (
        current_user.telegram_id
        if current_user.telegram_id and current_user.telegram_id > 0
        else None
    )
    return ProfileResponse(
        id=current_user.id,
        telegram_id=tid,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        username=current_user.username,
        language_code=current_user.language_code or "ru",
        timezone=current_user.timezone or "UTC",
        reminder_time=current_user.reminder_time,
        is_premium=bool(current_user.is_premium),
        subscription_expires_at=current_user.subscription_expires_at,
        training_days=current_user.training_days or 0,
        created_at=current_user.created_at,
    )


@router.patch("", response_model=ProfileResponse, summary="Update user profile settings")
async def update_profile(
    body: ProfileUpdateRequest,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ProfileResponse:
    # Validate settings
    settings_dict = {}
    if body.reminder_time is not None:
        settings_dict["reminder_time"] = body.reminder_time
    if body.timezone is not None:
        settings_dict["timezone"] = body.timezone
    if body.language_code is not None:
        settings_dict["language_code"] = body.language_code

    if settings_dict:
        errors = _validate_settings(settings_dict, current_user.language_code or "ru")
        if errors:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=errors)

    if body.first_name is not None:
        current_user.first_name = body.first_name.strip()
    if body.reminder_time is not None:
        current_user.reminder_time = body.reminder_time.strip()
    if body.timezone is not None:
        current_user.timezone = body.timezone.strip()
    if body.language_code is not None:
        current_user.language_code = body.language_code.strip()

    await session.commit()
    await session.refresh(current_user)

    tid = (
        current_user.telegram_id
        if current_user.telegram_id and current_user.telegram_id > 0
        else None
    )
    return ProfileResponse(
        id=current_user.id,
        telegram_id=tid,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        username=current_user.username,
        language_code=current_user.language_code or "ru",
        timezone=current_user.timezone or "UTC",
        reminder_time=current_user.reminder_time,
        is_premium=bool(current_user.is_premium),
        subscription_expires_at=current_user.subscription_expires_at,
        training_days=current_user.training_days or 0,
        created_at=current_user.created_at,
    )
