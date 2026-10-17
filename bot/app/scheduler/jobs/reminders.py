import logging
from datetime import UTC, datetime

from aiogram import Bot
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

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


async def _get_users_due_now(session: AsyncSession, current_utc: str) -> list[UserModel]:
    """Return users whose local reminder time equals current UTC moment.

    Builds one SQL OR clause per UTC offset (−12…+14) so all filtering
    happens in the database instead of loading every user into Python.
    """
    now_h, now_m = int(current_utc[:2]), int(current_utc[3:])
    now_total = now_h * 60 + now_m

    conditions = []
    for offset_h in range(-12, 15):
        local_total = (now_total + offset_h * 60) % (24 * 60)
        local_hm = f"{local_total // 60:02d}:{local_total % 60:02d}"

        if offset_h == 0:
            tz_cond = or_(UserModel.timezone.is_(None), UserModel.timezone == "UTC")
        elif offset_h > 0:
            tz_cond = UserModel.timezone == f"UTC+{offset_h}"
        else:
            tz_cond = UserModel.timezone == f"UTC{offset_h}"

        if local_hm == DEFAULT_REMINDER_TIME:
            # NULL reminder_time means "use default at local DEFAULT_REMINDER_TIME"
            time_cond = or_(UserModel.reminder_time == local_hm, UserModel.reminder_time.is_(None))
        else:
            time_cond = UserModel.reminder_time == local_hm

        conditions.append(and_(tz_cond, time_cond))

    result = await session.execute(
        select(UserModel).where(
            UserModel.telegram_id > 0,
            UserModel.onboarding_completed_at.isnot(None),
            or_(*conditions),
        )
    )
    return list(result.scalars().all())
