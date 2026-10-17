from __future__ import annotations

import json
import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.mobile_auth import issue_jwt, verify_vk_token
from app.api.v1.dependencies import get_current_user, get_db_session, get_redis
from app.api.v1.schemas.auth import (
    AccountLinkRequest,
    AccountLinkResponse,
    EmailCodeRequest,
    EmailVerifyRequest,
    GuestAuthRequest,
    TelegramCheckResponse,
    TelegramCodeRequest,
    TelegramSessionResponse,
    TokenResponse,
    VkAuthRequest,
)
from app.core.config import settings
from app.infrastructure.db.models.mobile_auth import MobileAuthModel
from app.infrastructure.db.models.user import UserModel

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/guest",
    response_model=TokenResponse,
    summary="Guest login via Device ID",
    description="Authenticates anonymously with a device identifier. Safe for offline-first start.",
)
async def auth_guest(
    body: GuestAuthRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    redis: Annotated[Redis, Depends(get_redis)],
) -> TokenResponse:
    # Key in redis for fast lookup: device -> user_id
    dev_key = f"mobile:device:{body.device_id}"
    cached_uid = await redis.get(dev_key)

    is_new = False
    if cached_uid:
        user_id = int(cached_uid)
        res = await session.execute(select(UserModel).where(UserModel.id == user_id))
        user = res.scalar_one_or_none()
        if user is None:
            cached_uid = None

    if not cached_uid:
        # Create deterministic synthetic telegram_id for guest users: negative int
        # using hash of device_id to avoid collision
        synth_tid = -(abs(hash(f"guest:{body.device_id}")) % 8000000000000000 + 100000)
        res = await session.execute(select(UserModel).where(UserModel.telegram_id == synth_tid))
        user = res.scalar_one_or_none()
        if user is None:
            user = UserModel(
                telegram_id=synth_tid,
                first_name=body.device_name or "Guest",
                language_code="ru",
                timezone="UTC",
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            is_new = True

        user_id = user.id
        await redis.set(dev_key, str(user_id), ex=30 * 86400)

    token = issue_jwt(user_id, settings.MOBILE_JWT_SECRET, settings.MOBILE_JWT_EXPIRE_DAYS)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user_id,
        is_new=is_new,
        expires_in_days=settings.MOBILE_JWT_EXPIRE_DAYS,
    )


@router.post(
    "/telegram/session",
    response_model=TelegramSessionResponse,
    summary="Create Telegram deep-link login session",
    description="Initiates authorization via the Telegram bot. Returns a deep link for the user to open in Telegram.",
)
async def create_telegram_session(
    redis: Annotated[Redis, Depends(get_redis)],
) -> TelegramSessionResponse:
    session_token = secrets.token_urlsafe(16)
    bot_name = settings.BOT_USERNAME or "pepito_bot"
    deep_link = f"https://t.me/{bot_name}?start=auth_{session_token}"

    session_data = {"status": "pending", "user_id": None}
    await redis.set(f"tg_session:{session_token}", json.dumps(session_data), ex=600)

    return TelegramSessionResponse(
        session_token=session_token,
        bot_username=bot_name,
        deep_link=deep_link,
        expires_in_sec=600,
    )


@router.get(
    "/telegram/check",
    response_model=TelegramCheckResponse,
    summary="Check Telegram deep-link login session status",
    description="Polls session state. When user confirms in the Telegram bot, returns the JWT access token.",
)
async def check_telegram_session(
    session_token: str,
    redis: Annotated[Redis, Depends(get_redis)],
) -> TelegramCheckResponse:
    raw = await redis.get(f"tg_session:{session_token}")
    if not raw:
        return TelegramCheckResponse(status="expired", token_data=None)

    data = json.loads(raw)
    st = data.get("status", "pending")
    if st == "authenticated" and data.get("user_id"):
        user_id = int(data["user_id"])
        await redis.delete(f"tg_session:{session_token}")
        token = issue_jwt(user_id, settings.MOBILE_JWT_SECRET, settings.MOBILE_JWT_EXPIRE_DAYS)
        token_data = TokenResponse(
            access_token=token,
            token_type="bearer",
            user_id=user_id,
            is_new=False,
            expires_in_days=settings.MOBILE_JWT_EXPIRE_DAYS,
        )
        return TelegramCheckResponse(status="authenticated", token_data=token_data)

    return TelegramCheckResponse(status="pending", token_data=None)


@router.post(
    "/telegram/code",
    response_model=TokenResponse,
    summary="Login via 6-digit code from Telegram bot",
    description="Exchanges the linking code generated by /connect in the Telegram bot for a JWT token.",
)
async def auth_telegram_code(
    body: TelegramCodeRequest,
    redis: Annotated[Redis, Depends(get_redis)],
) -> TokenResponse:
    raw = await redis.get(f"tg_connect_code:{body.code.strip()}")
    if not raw:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный или просроченный код подтверждения",
        )

    user_id = int(raw)
    # delete single-use code
    await redis.delete(f"tg_connect_code:{body.code.strip()}")

    token = issue_jwt(user_id, settings.MOBILE_JWT_SECRET, settings.MOBILE_JWT_EXPIRE_DAYS)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user_id,
        is_new=False,
        expires_in_days=settings.MOBILE_JWT_EXPIRE_DAYS,
    )


@router.post(
    "/vk",
    response_model=TokenResponse,
    summary="Login via VK ID",
    description="Authenticates with VK OAuth token and user ID.",
)
async def auth_vk(
    body: VkAuthRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> TokenResponse:
    valid = await verify_vk_token(body.vk_access_token, body.vk_user_id)
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Проверка токена VK завершилась ошибкой",
        )

    res = await session.execute(
        select(MobileAuthModel).where(MobileAuthModel.vk_id == body.vk_user_id)
    )
    mobile_auth = res.scalar_one_or_none()

    is_new = False
    if mobile_auth is None:
        placeholder_telegram_id = -body.vk_user_id
        new_user = UserModel(
            telegram_id=placeholder_telegram_id,
            first_name=body.first_name or "VK User",
            language_code="ru",
        )
        session.add(new_user)
        await session.flush()

        mobile_auth = MobileAuthModel(
            user_id=new_user.id,
            vk_id=body.vk_user_id,
        )
        session.add(mobile_auth)
        await session.commit()
        user_id = new_user.id
        is_new = True
    else:
        user_id = mobile_auth.user_id

    token = issue_jwt(user_id, settings.MOBILE_JWT_SECRET, settings.MOBILE_JWT_EXPIRE_DAYS)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user_id,
        is_new=is_new,
        expires_in_days=settings.MOBILE_JWT_EXPIRE_DAYS,
    )


@router.post(
    "/email/request-code",
    summary="Request email verification code",
    description="Generates a 6-digit code for passwordless email login.",
)
async def request_email_code(
    body: EmailCodeRequest,
    redis: Annotated[Redis, Depends(get_redis)],
) -> dict:
    email = body.email.strip().lower()
    code = f"{secrets.randbelow(900000) + 100000}"
    # Store in redis with 15 min TTL
    await redis.set(f"email_code:{email}", code, ex=900)
    # Note: In production SMTP / SendGrid is hooked here; code is stored in redis
    return {"status": "ok", "message": f"Код подтверждения отправлен на {email}"}


@router.post(
    "/email/verify",
    response_model=TokenResponse,
    summary="Verify email code and authenticate",
)
async def verify_email_code(
    body: EmailVerifyRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    redis: Annotated[Redis, Depends(get_redis)],
) -> TokenResponse:
    email = body.email.strip().lower()
    stored_code = await redis.get(f"email_code:{email}")
    if not stored_code or stored_code != body.code.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный или просроченный код из email",
        )

    await redis.delete(f"email_code:{email}")

    # Find or create user associated with email
    uid_raw = await redis.get(f"user_by_email:{email}")
    is_new = False
    if uid_raw:
        user_id = int(uid_raw)
    else:
        synth_tid = -(abs(hash(f"email:{email}")) % 8000000000000000 + 200000)
        new_user = UserModel(
            telegram_id=synth_tid,
            first_name=email.split("@")[0],
            language_code="ru",
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        user_id = new_user.id
        is_new = True
        await redis.set(f"user_by_email:{email}", str(user_id))

    token = issue_jwt(user_id, settings.MOBILE_JWT_SECRET, settings.MOBILE_JWT_EXPIRE_DAYS)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user_id=user_id,
        is_new=is_new,
        expires_in_days=settings.MOBILE_JWT_EXPIRE_DAYS,
    )


@router.post(
    "/link",
    response_model=AccountLinkResponse,
    summary="Link guest account to Telegram / VK / Email",
    description="Merges the currently authenticated guest account with a target Telegram/VK/Email account.",
)
async def link_account(
    body: AccountLinkRequest,
    current_user: Annotated[UserModel, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    redis: Annotated[Redis, Depends(get_redis)],
) -> AccountLinkResponse:
    target_user_id: int | None = None

    if body.provider == "telegram_code":
        raw = await redis.get(f"tg_connect_code:{body.credential.strip()}")
        if not raw:
            raise HTTPException(status_code=400, detail="Неверный код привязки")
        target_user_id = int(raw)
        await redis.delete(f"tg_connect_code:{body.credential.strip()}")

    elif body.provider == "telegram_session":
        raw = await redis.get(f"tg_session:{body.credential.strip()}")
        if not raw:
            raise HTTPException(status_code=400, detail="Сессия истекла")
        data = json.loads(raw)
        if data.get("status") != "authenticated" or not data.get("user_id"):
            raise HTTPException(status_code=400, detail="Сессия еще не подтверждена в боте")
        target_user_id = int(data["user_id"])

    elif body.provider == "email":
        uid_raw = await redis.get(f"user_by_email:{body.credential.strip().lower()}")
        if uid_raw:
            target_user_id = int(uid_raw)

    if not target_user_id or target_user_id == current_user.id:
        token = issue_jwt(
            current_user.id, settings.MOBILE_JWT_SECRET, settings.MOBILE_JWT_EXPIRE_DAYS
        )
        return AccountLinkResponse(
            success=True,
            merged_user_id=current_user.id,
            message="Аккаунты уже объединены",
            token_data=TokenResponse(
                access_token=token,
                token_type="bearer",
                user_id=current_user.id,
                is_new=False,
                expires_in_days=settings.MOBILE_JWT_EXPIRE_DAYS,
            ),
        )

    # Re-link pets, training plans, conversations, and threads
    from app.infrastructure.db.models.ai_conversation import AiConversationModel
    from app.infrastructure.db.models.coach_thread import CoachThreadModel
    from app.infrastructure.db.models.pet import PetModel
    from app.infrastructure.db.models.training import TrainingPlanModel

    pets_res = await session.execute(select(PetModel).where(PetModel.user_id == current_user.id))
    for pet in pets_res.scalars().all():
        pet.user_id = target_user_id

    plans_res = await session.execute(
        select(TrainingPlanModel).where(TrainingPlanModel.user_id == current_user.id)
    )
    for plan in plans_res.scalars().all():
        plan.user_id = target_user_id

    convs_res = await session.execute(
        select(AiConversationModel).where(AiConversationModel.user_id == current_user.id)
    )
    for conv in convs_res.scalars().all():
        conv.user_id = target_user_id

    threads_res = await session.execute(
        select(CoachThreadModel).where(CoachThreadModel.user_id == current_user.id)
    )
    for thread in threads_res.scalars().all():
        thread.user_id = target_user_id

    # Update device mapping in redis if device_id provided
    if body.device_id:
        await redis.set(
            f"mobile:device:{body.device_id.strip()}", str(target_user_id), ex=30 * 86400
        )

    await session.commit()

    new_token = issue_jwt(
        target_user_id, settings.MOBILE_JWT_SECRET, settings.MOBILE_JWT_EXPIRE_DAYS
    )
    return AccountLinkResponse(
        success=True,
        merged_user_id=target_user_id,
        message="Данные успешно перенесены в основной аккаунт",
        token_data=TokenResponse(
            access_token=new_token,
            token_type="bearer",
            user_id=target_user_id,
            is_new=False,
            expires_in_days=settings.MOBILE_JWT_EXPIRE_DAYS,
        ),
    )
