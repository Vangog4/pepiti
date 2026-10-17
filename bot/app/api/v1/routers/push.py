from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies import get_current_user, get_db_session, get_redis
from app.api.v1.schemas.push import PushRegisterRequest, PushRegisterResponse
from app.infrastructure.db.models.mobile_auth import MobileAuthModel
from app.infrastructure.db.models.user import UserModel

router = APIRouter(prefix="/push", tags=["Push Notifications"])


@router.post(
    "/register",
    response_model=PushRegisterResponse,
    summary="Register device push notification token",
)
async def register_push_token(
    body: PushRegisterRequest,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    redis: Annotated[Redis, Depends(get_redis)],
) -> PushRegisterResponse:
    # 1. Update in MobileAuthModel if one exists for user
    res = await session.execute(
        select(MobileAuthModel).where(MobileAuthModel.user_id == current_user.id)
    )
    mobile_auth = res.scalar_one_or_none()
    if mobile_auth is not None:
        mobile_auth.push_token = body.push_token
        await session.commit()

    # 2. Store in Redis for instant lookup for all mobile users
    await redis.set(f"mobile:push_token:{current_user.id}", body.push_token)
    if body.device_id:
        await redis.set(f"mobile:push_token:dev:{body.device_id}", body.push_token)

    return PushRegisterResponse(success=True, platform=body.platform)
