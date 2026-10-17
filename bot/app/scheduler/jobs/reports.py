import logging

from aiogram import Bot
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import selectinload

from app.i18n import normalize_locale, t
from app.infrastructure.db.models.user import UserModel

logger = logging.getLogger(__name__)


async def send_weekly_reports(session_factory: async_sessionmaker, bot: Bot) -> None:
    async with session_factory() as session:
        result = await session.execute(
            select(UserModel)
            .where(
                UserModel.telegram_id > 0,
                UserModel.onboarding_completed_at.isnot(None),
            )
            .options(selectinload(UserModel.pets))
        )
        users = list(result.scalars().all())

    sent = 0
    for user in users:
        try:
            days = user.pets[0].training_days if user.pets else 0
            lang = normalize_locale(user.language_code)
            name = (
                (user.first_name or t("reminder.push.friend", lang))
                .replace("<", "&lt;")
                .replace(">", "&gt;")
            )
            if user.is_premium:
                text = t("report.weekly.premium", lang, name=name, days=days)
            else:
                text = t("report.weekly.free", lang, name=name, days=days)
            await bot.send_message(chat_id=user.telegram_id, text=text, parse_mode="HTML")
            sent += 1
        except Exception as e:
            logger.warning("Failed to send report to %s: %s", user.telegram_id, e)

    logger.info("Weekly reports sent: %d/%d", sent, len(users))
