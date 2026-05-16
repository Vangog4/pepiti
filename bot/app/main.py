import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiohttp import web

from app.core.config import settings
from app.core.container import AppContainer
from app.bot.handlers import setup_routers
from app.bot.middlewares.db import DbSessionMiddleware
from app.bot.middlewares.throttle import ThrottlingMiddleware
from app.scheduler.setup import create_scheduler
from app.api.server import create_web_app

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    container = AppContainer()
    logger.info("Starting bot...")

    bot = Bot(token=settings.BOT_TOKEN)
    storage = RedisStorage.from_url(settings.REDIS_URL)
    dp = Dispatcher(storage=storage)

    session_factory = container.session_factory()
    dp.update.middleware(ThrottlingMiddleware(
        redis_url=settings.REDIS_URL,
        admin_ids=set(settings.ADMIN_TELEGRAM_IDS),
    ))
    dp.update.middleware(DbSessionMiddleware(session_factory))

    setup_routers(dp)

    scheduler = create_scheduler(session_factory, bot)
    scheduler.start()

    # Start aiohttp web server alongside the bot.
    web_app = create_web_app(session_factory, container.metrics(), bot, container.admin_log())
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


if __name__ == "__main__":
    asyncio.run(main())
