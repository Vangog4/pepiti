from pathlib import Path

from aiogram import Bot
from aiohttp import web
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.api.routes import routes
from app.infrastructure.redis.admin_log import AdminLog
from app.infrastructure.redis.metrics import BotMetrics

_WEBAPP_DIR = Path(__file__).parent.parent / "webapp"


def create_web_app(
    session_factory: async_sessionmaker,
    metrics: BotMetrics,
    bot: Bot,
    admin_log: AdminLog | None = None,
) -> web.Application:
    app = web.Application()
    app["session_factory"] = session_factory
    app["metrics"] = metrics
    app["bot"] = bot
    app["admin_log"] = admin_log
    app.add_routes(routes)
    app.router.add_static("/webapp/", path=str(_WEBAPP_DIR), name="webapp_static")
    return app
