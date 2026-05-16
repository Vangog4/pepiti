import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.scheduler.jobs.reminders import send_daily_reminders
from app.scheduler.jobs.reports import send_weekly_reports
from app.scheduler.jobs.expire_subscriptions import expire_subscriptions

logger = logging.getLogger(__name__)


def create_scheduler(session_factory: async_sessionmaker, bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="UTC")

    scheduler.add_job(
        send_daily_reminders,
        trigger=CronTrigger(minute="*", timezone="UTC"),  # runs every minute, filters by reminder_time
        kwargs={"session_factory": session_factory, "bot": bot},
        id="daily_reminders",
        replace_existing=True,
    )

    scheduler.add_job(
        send_weekly_reports,
        trigger=CronTrigger(day_of_week="sun", hour=18, minute=0, timezone="UTC"),
        kwargs={"session_factory": session_factory, "bot": bot},
        id="weekly_reports",
        replace_existing=True,
    )

    scheduler.add_job(
        expire_subscriptions,
        trigger=CronTrigger(hour=0, minute=5, timezone="UTC"),
        kwargs={"session_factory": session_factory},
        id="expire_subscriptions",
        replace_existing=True,
    )

    logger.info(
        "Scheduler configured: daily_reminders (every minute, per-user time), "
        "weekly_reports (Sun 18:00 UTC), expire_subscriptions (00:05 UTC)"
    )
    return scheduler
