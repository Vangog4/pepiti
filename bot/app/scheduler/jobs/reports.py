import logging
from datetime import UTC, datetime

from aiogram import Bot
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import selectinload

from app.core.tz_utils import local_now
from app.i18n import normalize_locale, t
from app.infrastructure.db.models.user import UserModel
from app.infrastructure.db.repositories.activity_repo import ActivityRepository
from app.logic.rules import rule
from app.services.entitlements import has_premium
from app.services.tracker import snapshot

logger = logging.getLogger(__name__)


def report_due(user, now_utc: datetime) -> bool:
    """Sunday, at/after the report hour in the user's own time, once per local date."""
    loc = local_now(user.timezone, now_utc)
    hour = int(rule("tracker.weekly_report_hour", 19))
    return (
        loc.weekday() == 6
        and loc.hour >= hour
        and getattr(user, "weekly_report_sent_on", None) != loc.date()
    )


async def send_weekly_reports(
    session_factory: async_sessionmaker, bot: Bot, now_utc: datetime | None = None
) -> None:
    """Runs every 15 min; each user gets exactly one report on Sunday evening local time."""
    now_utc = now_utc or datetime.now(UTC)
    sent = 0
    async with session_factory() as session:
        users = (
            (
                await session.execute(
                    select(UserModel)
                    .where(
                        UserModel.telegram_id > 0,
                        UserModel.onboarding_completed_at.isnot(None),
                    )
                    .options(selectinload(UserModel.pets))
                )
            )
            .scalars()
            .all()
        )
        repo = ActivityRepository(session)
        for user in users:
            if not user.pets or not report_due(user, now_utc):
                continue
            today = local_now(user.timezone, now_utc).date()
            user.weekly_report_sent_on = today  # at-most-once: mark before sending
            await session.commit()
            try:
                pet = user.pets[0]
                snap = snapshot(await repo.rows(pet.id, today), today, has_premium(user))
                wk = snap["week"]
                lang = normalize_locale(user.language_code)
                name = (
                    (user.first_name or t("reminder.push.friend", lang))
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                )
                text = t(
                    "report.weekly.stats",
                    lang,
                    name=name,
                    pet=pet.name,
                    days=wk.task_days,
                    walks=wk.walk_count,
                    minutes=wk.walk_minutes,
                    streak=snap["streak"],
                )
                await bot.send_message(chat_id=user.telegram_id, text=text, parse_mode="HTML")
                sent += 1
            except Exception as e:
                logger.warning("Failed to send report to %s: %s", user.telegram_id, e)

    if sent:
        logger.info("Weekly reports sent: %d", sent)
