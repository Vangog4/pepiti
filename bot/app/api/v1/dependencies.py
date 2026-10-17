from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.api.mobile_auth import decode_jwt
from app.core.config import settings
from app.infrastructure.db.models.user import UserModel

security = HTTPBearer(auto_error=False)


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """Provide an asynchronous SQLAlchemy session from app state."""
    session_factory: async_sessionmaker[AsyncSession] = request.app.state.session_factory
    async with session_factory() as session:
        yield session


async def get_redis(request: Request) -> Redis:
    """Provide Redis connection from app state or create from URL."""
    redis: Redis | None = getattr(request.app.state, "redis", None)
    if redis is None:
        redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
        request.app.state.redis = redis
    return redis


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> int:
    """Validate Bearer JWT and return user_id (users.id PK)."""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    user_id = decode_jwt(token, settings.MOBILE_JWT_SECRET)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired JWT token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_id


async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db_session),
) -> UserModel:
    """Fetch current UserModel from DB by user_id."""
    stmt = select(UserModel).where(UserModel.id == user_id)
    res = await session.execute(stmt)
    user = res.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user
