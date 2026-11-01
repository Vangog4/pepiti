import logging
from datetime import UTC, datetime

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.scheduler.jobs.expire_subscriptions import expire_subscriptions
from app.scheduler.jobs.heartbeat import beat
from app.scheduler.jobs.reminders import send_daily_reminders, send_health_reminders
from app.scheduler.jobs.reports import send_weekly_reports
from app.services.payment_reconcile import reconcile_stars

logger = logging.getLogger(__name__)


def create_scheduler(session_factory: async_sessionmaker, bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="UTC")

    scheduler.add_job(beat, "interval", seconds=30, id="heartbeat", replace_existing=True)

    # Safety net for money: grant Stars payments whose update was lost (outage, restart).
    scheduler.add_job(
        reconcile_stars,
        trigger=CronTrigger(minute="*/15", timezone="UTC"),
        kwargs={"bot": bot, "session_factory": session_factory},
        id="reconcile_stars",
        replace_existing=True,
        next_run_time=datetime.now(UTC),  # also once at startup
        max_instances=1,
    )

    scheduler.add_job(
        send_daily_reminders,
        trigger=CronTrigger(
            minute="*", timezone="UTC"
        ),  # runs every minute, filters by reminder_time
        kwargs={"session_factory": session_factory, "bot": bot},
        id="daily_reminders",
        replace_existing=True,
    )

    scheduler.add_job(
        send_health_reminders,
        trigger=CronTrigger(minute="*", timezone="UTC"),
        kwargs={"session_factory": session_factory, "bot": bot},
        id="health_reminders",
        replace_existing=True,
    )

    scheduler.add_job(
        send_weekly_reports,
        trigger=CronTrigger(minute="*/15", timezone="UTC"),  # local Sunday evening per user
        kwargs={"session_factory": session_factory, "bot": bot},
        id="weekly_reports",
        replace_existing=True,
    )

    scheduler.add_job(
        expire_subscriptions,
        trigger=CronTrigger(minute="*/10", timezone="UTC"),
        kwargs={"session_factory": session_factory},
        id="expire_subscriptions",
        replace_existing=True,
    )

    logger.info(
        "Scheduler configured: daily_reminders (every minute, per-user time), "
        "weekly_reports (every 15 min, per-user Sunday evening), expire_subscriptions (every 10 min)"
    )
    return scheduler
