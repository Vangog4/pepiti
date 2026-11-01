import logging
from datetime import UTC, datetime

from aiogram import Bot
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.tz_utils import local_now
from app.i18n import normalize_locale, t
from app.infrastructure.db.models.user import UserModel

logger = logging.getLogger(__name__)

DEFAULT_REMINDER_TIME = "10:00"  # local time used when reminder_time is NULL


async def send_daily_reminders(session_factory: async_sessionmaker, bot: Bot) -> None:
    now_utc = datetime.now(UTC)
    current_utc = now_utc.strftime("%H:%M")

    async with session_factory() as session:
        users = await _get_users_due_now(session, current_utc)

    if not users:
        return

    sent = 0
    for user in users:
        try:
            lang = normalize_locale(user.language_code)
            name = user.first_name or t("reminder.push.friend", lang)
            text = t("reminder.push.text", lang, name=name)
            await bot.send_message(chat_id=user.telegram_id, text=text)
            sent += 1
        except Exception as e:
            logger.warning("Failed to send reminder to %s: %s", user.telegram_id, e)

    logger.info("Daily reminders at %s UTC: sent %d/%d", current_utc, sent, len(users))


async def _get_users_due_now(
    session: AsyncSession, current_utc: str, now_utc: datetime | None = None
) -> list[UserModel]:
    """Users whose *local* wall-clock time equals their reminder time right now.

    Local time is computed per user (IANA zone or 'UTC±N'), so DST and half-hour
    zones work. Disabled reminders ("off") are skipped in SQL.
    """
    now = now_utc or datetime.now(UTC).replace(
        hour=int(current_utc[:2]), minute=int(current_utc[3:]), second=0, microsecond=0
    )
    result = await session.execute(
        select(UserModel).where(
            UserModel.telegram_id > 0,
            UserModel.onboarding_completed_at.isnot(None),
            or_(UserModel.reminder_time.is_(None), UserModel.reminder_time != "off"),
        )
    )
    due = []
    for user in result.scalars().all():
        local_hm = local_now(user.timezone, now).strftime("%H:%M")
        target = user.reminder_time or DEFAULT_REMINDER_TIME
        if local_hm == target:
            due.append(user)
    return due
