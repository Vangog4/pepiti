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


async def send_health_reminders(session_factory: async_sessionmaker, bot: Bot) -> None:
    """Health pushes at the user's reminder time: N days before and on the due day."""
    from aiogram import types

    from app.infrastructure.db.models.health_event import HealthEventModel
    from app.infrastructure.db.models.pet import PetModel
    from app.services.health import reminders_due, status_of

    now_utc = datetime.now(UTC)
    async with session_factory() as session:
        users = await _get_users_due_now(session, now_utc.strftime("%H:%M"))
        sent = 0
        for user in users:
            lang = normalize_locale(user.language_code)
            today = local_now(user.timezone, now_utc).date()
            pets = (
                (await session.execute(select(PetModel).where(PetModel.user_id == user.id)))
                .scalars()
                .all()
            )
            for pet in pets:
                events = (
                    (
                        await session.execute(
                            select(HealthEventModel).where(HealthEventModel.pet_id == pet.id)
                        )
                    )
                    .scalars()
                    .all()
                )
                for ev in reminders_due(list(events), today):
                    status = status_of(ev.next_due_at, today)
                    kind = f"{t(f'health.kind.{ev.kind}', lang)}"
                    text = t(
                        "health.push.today" if status == "today" else "health.push.soon",
                        lang,
                        name=pet.name,
                        kind=kind,
                        n=(ev.next_due_at - today).days,
                        date=ev.next_due_at.strftime("%d.%m.%Y"),
                    )
                    kb = types.InlineKeyboardMarkup(
                        inline_keyboard=[
                            [
                                types.InlineKeyboardButton(
                                    text=t("health.btn.done", lang),
                                    callback_data=f"hl_done:{ev.id}",
                                ),
                                types.InlineKeyboardButton(
                                    text=t("health.btn.snooze", lang),
                                    callback_data=f"hl_snooze:{ev.id}",
                                ),
                            ]
                        ]
                    )
                    try:
                        await bot.send_message(user.telegram_id, text, reply_markup=kb)
                        ev.last_notified_on = today
                        sent += 1
                    except Exception as e:
                        logger.warning("health push to %s failed: %s", user.telegram_id, e)
        await session.commit()
    if sent:
        logger.info("Health reminders sent: %d", sent)
