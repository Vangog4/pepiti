from __future__ import annotations

from pathlib import Path
from typing import Any

from aiogram import Bot
from aiohttp import web
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.api.routes import routes
from app.api.v1.app import create_fastapi_app
from app.core.config import settings
from app.infrastructure.redis.admin_log import AdminLog
from app.infrastructure.redis.metrics import BotMetrics
from app.services.ai_service import AiService

_WEBAPP_DIR = Path(__file__).parent.parent / "webapp"


async def _asgi_bridge_handler(request: web.Request) -> web.StreamResponse:
    """Bridge incoming aiohttp request to internal FastAPI ASGI application."""
    fastapi_app = request.app["fastapi_app"]
    body = await request.read()
    response_status = 200
    response_headers: list[tuple[str, str]] = []
    response_body = bytearray()

    async def receive() -> dict[str, Any]:
        return {"type": "http.request", "body": body, "more_body": False}

    async def send(message: dict[str, Any]) -> None:
        nonlocal response_status, response_headers, response_body
        if message["type"] == "http.response.start":
            response_status = message["status"]
            response_headers = [
                (k.decode("latin1"), v.decode("latin1")) for k, v in message.get("headers", [])
            ]
        elif message["type"] == "http.response.body":
            response_body.extend(message.get("body", b""))

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": request.method,
        "path": request.path,
        "raw_path": request.raw_path.encode(),
        "query_string": request.query_string.encode(),
        "headers": [
            (k.lower().encode("latin1"), v.encode("latin1")) for k, v in request.headers.items()
        ],
        "client": (request.remote or "127.0.0.1", 0),
        "server": ("127.0.0.1", 8080),
        "scheme": request.scheme,
    }

    await fastapi_app(scope, receive, send)

    resp = web.Response(body=bytes(response_body), status=response_status)
    for k, v in response_headers:
        k_lower = k.lower()
        if k_lower not in ("content-length", "content-type"):
            resp.headers[k] = v
        elif k_lower == "content-type":
            resp.content_type = v
    return resp


def create_web_app(
    session_factory: async_sessionmaker,
    metrics: BotMetrics,
    bot: Bot,
    admin_log: AdminLog | None = None,
    redis: Redis | None = None,
    ai_service: AiService | None = None,
) -> web.Application:
    app = web.Application()
    app["session_factory"] = session_factory
    app["metrics"] = metrics
    app["bot"] = bot
    app["admin_log"] = admin_log

    if redis is None:
        redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    app["redis"] = redis

    if ai_service is None:
        ai_service = AiService(api_key=settings.GEMINI_API_KEY)
    app["ai_service"] = ai_service

    # Initialize FastAPI application with OpenAPI and Swagger
    fastapi_app = create_fastapi_app(
        session_factory=session_factory,
        metrics=metrics,
        bot=bot,
        admin_log=admin_log,
        redis=redis,
        ai_service=ai_service,
    )
    app["fastapi_app"] = fastapi_app

    # Existing aiohttp routes for WebApp
    app.add_routes(routes)
    app.router.add_static("/webapp/", path=str(_WEBAPP_DIR), name="webapp_static")

    # FastAPI endpoints: /docs, /redoc, /openapi.json, /api/v1/*
    app.router.add_route("*", "/docs{tail:.*}", _asgi_bridge_handler)
    app.router.add_route("*", "/redoc{tail:.*}", _asgi_bridge_handler)
    app.router.add_route("*", "/openapi.json", _asgi_bridge_handler)
    app.router.add_route("*", "/api/v1{tail:.*}", _asgi_bridge_handler)

    async def _on_cleanup(web_app: web.Application) -> None:
        if "redis" in web_app and web_app["redis"]:
            await web_app["redis"].aclose()

    app.on_cleanup.append(_on_cleanup)

    return app
