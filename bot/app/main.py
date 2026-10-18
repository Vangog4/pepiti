import asyncio
import logging
import os
import signal

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiohttp import web

from app.api.server import create_web_app
from app.bot.handlers import setup_routers
from app.bot.middlewares.db import DbSessionMiddleware
from app.bot.middlewares.throttle import ThrottlingMiddleware
from app.core.config import settings
from app.core.container import AppContainer
from app.scheduler.setup import create_scheduler

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def run_api(container: AppContainer, bot: Bot) -> None:
    session_factory = container.session_factory()
    web_app = create_web_app(
        session_factory,
        container.metrics(),
        bot,
        container.admin_log(),
        ai_service=container.ai_service(),
    )
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, settings.WEBAPP_BIND_HOST, settings.WEBAPP_BIND_PORT)
    await site.start()
    logger.info(
        "Pepito API Server listening on %s:%d (Swagger docs at /docs, mobile sync at /api/v1/)",
        settings.WEBAPP_BIND_HOST,
        settings.WEBAPP_BIND_PORT,
    )

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            loop.add_signal_handler(sig, stop_event.set)
        except (NotImplementedError, RuntimeError):
            pass

    try:
        await stop_event.wait()
    finally:
        logger.info("Shutting down Pepito API Server...")
        await runner.cleanup()
        await bot.session.close()


async def run_bot(container: AppContainer, bot: Bot) -> None:
    session_factory = container.session_factory()
    storage = RedisStorage.from_url(settings.REDIS_URL)
    dp = Dispatcher(storage=storage)

    dp.update.middleware(
        ThrottlingMiddleware(
            redis_url=settings.REDIS_URL,
            admin_ids=set(settings.ADMIN_TELEGRAM_IDS),
        )
    )
    dp.update.middleware(DbSessionMiddleware(session_factory))
    setup_routers(dp)

    scheduler = create_scheduler(session_factory, bot)
    scheduler.start()
    logger.info("Pepito Bot Worker & Scheduler started.")

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Start polling")
        await dp.start_polling(bot)
    finally:
        logger.info("Shutting down Pepito Bot Worker...")
        scheduler.shutdown(wait=False)
        await storage.close()
        await bot.session.close()


async def run_all(container: AppContainer, bot: Bot) -> None:
    session_factory = container.session_factory()
    storage = RedisStorage.from_url(settings.REDIS_URL)
    dp = Dispatcher(storage=storage)

    dp.update.middleware(
        ThrottlingMiddleware(
            redis_url=settings.REDIS_URL,
            admin_ids=set(settings.ADMIN_TELEGRAM_IDS),
        )
    )
    dp.update.middleware(DbSessionMiddleware(session_factory))
    setup_routers(dp)

    scheduler = create_scheduler(session_factory, bot)
    scheduler.start()

    web_app = create_web_app(
        session_factory,
        container.metrics(),
        bot,
        container.admin_log(),
        ai_service=container.ai_service(),
    )
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, settings.WEBAPP_BIND_HOST, settings.WEBAPP_BIND_PORT)
    await site.start()
    logger.info(
        "Web server listening on %s:%d", settings.WEBAPP_BIND_HOST, settings.WEBAPP_BIND_PORT
    )

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Start polling")
        await dp.start_polling(bot)
    finally:
        scheduler.shutdown(wait=False)
        await runner.cleanup()
        await storage.close()
        await bot.session.close()


async def main() -> None:
    import sentry_sdk

    if settings.SENTRY_DSN:
        sentry_sdk.init(dsn=settings.SENTRY_DSN, traces_sample_rate=0.1, environment="production")

    # Expose optional Langfuse keys to process env for app.logic.trace
    if settings.LANGFUSE_PUBLIC_KEY:
        os.environ.setdefault("LANGFUSE_PUBLIC_KEY", settings.LANGFUSE_PUBLIC_KEY)
    if settings.LANGFUSE_SECRET_KEY:
        os.environ.setdefault("LANGFUSE_SECRET_KEY", settings.LANGFUSE_SECRET_KEY)
    if settings.LANGFUSE_HOST:
        os.environ.setdefault("LANGFUSE_HOST", settings.LANGFUSE_HOST)

    container = AppContainer()
    bot = Bot(token=settings.BOT_TOKEN)

    role = os.getenv("PEPITO_ROLE", "all").lower().strip()
    logger.info("Initializing Pepito with role='%s'", role)

    if role == "api":
        await run_api(container, bot)
    elif role == "bot":
        await run_bot(container, bot)
    else:
        await run_all(container, bot)


if __name__ == "__main__":
    asyncio.run(main())
