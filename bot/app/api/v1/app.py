from __future__ import annotations

from pathlib import Path

from aiogram import Bot
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.api.v1.routers import (
    auth_router,
    coach_router,
    pets_router,
    profile_router,
    push_router,
    subscription_router,
    sync_router,
    training_router,
)
from app.infrastructure.redis.admin_log import AdminLog
from app.infrastructure.redis.metrics import BotMetrics
from app.services.ai_service import AiService

_WEBAPP_DIR = Path(__file__).parent.parent.parent / "webapp"


def create_fastapi_app(
    session_factory: async_sessionmaker | None = None,
    metrics: BotMetrics | None = None,
    bot: Bot | None = None,
    admin_log: AdminLog | None = None,
    redis: Redis | None = None,
    ai_service: AiService | None = None,
) -> FastAPI:
    """Create and configure the FastAPI application for Pepito Mobile API."""
    app = FastAPI(
        title="Pepito Mobile API",
        version="1.0.0",
        description=(
            "REST API сервер для мобильного приложения Pepito (iOS / Android / Flutter) "
            "с поддержкой оффлайн-синхронизации, мульти-авторизации (Telegram, Guest, VK, Email), "
            "управления профилями питомцев, планами тренировок и диалогами с AI-кинологом."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Enable CORS for Flutter, React Native, iOS/Android webviews and local dev
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Attach shared dependencies to app.state
    app.state.session_factory = session_factory
    app.state.metrics = metrics
    app.state.bot = bot
    app.state.admin_log = admin_log
    app.state.redis = redis
    app.state.ai_service = ai_service

    # Public health check
    @app.get("/api/health", tags=["Health"])
    async def health_check() -> dict:
        return {
            "status": "ok",
            "app": "pepito-mobile-api",
            "version": "1.0.0",
        }

    # Mount all v1 routers under /api/v1
    v1_router = APIRouter(prefix="/api/v1")
    v1_router.include_router(auth_router)
    v1_router.include_router(sync_router)
    v1_router.include_router(profile_router)
    v1_router.include_router(pets_router)
    v1_router.include_router(training_router)
    v1_router.include_router(coach_router)
    v1_router.include_router(subscription_router)
    v1_router.include_router(push_router)

    app.include_router(v1_router)

    # Mount WebApp static assets if directory exists
    if _WEBAPP_DIR.exists():
        app.mount("/webapp", StaticFiles(directory=str(_WEBAPP_DIR), html=True), name="webapp")

    return app
