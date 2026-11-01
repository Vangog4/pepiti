"""Renewal reminders (one-time packs) and the evening streak nudge."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from aiogram import types
from sqlalchemy import or_, select

from app.core.tz_utils import local_now
from app.i18n import normalize_locale, t
from app.logic.rules import rule
from app.services.entitlements import has_premium
from app.services.products import get_product

logger = logging.getLogger(__name__)
DEFAULT_REMINDER_TIME = "10:00"


def _days(key: str, default: list[int]) -> list[int]:
    return [int(x) for x in (rule(key, default) or default)]


def renewal_days_left(expires_at: datetime, tz: str | None, now_utc: datetime) -> int:
    """Whole LOCAL calendar days between now and the expiry (naive ``expires_at`` is UTC)."""
    exp_local = local_now(tz, expires_at.replace(tzinfo=UTC)).date()
    return (exp_local - local_now(tz, now_utc).date()).days


def renewal_stage(expires_at: datetime, tz: str | None, now_utc: datetime) -> int | None:
    days = renewal_days_left(expires_at, tz, now_utc)
    return days if days in _days("nudges.renewal_days_before", [3, 1]) else None


def is_one_time_pack(plan_code: str | None) -> bool:
    """Auto-renewing Stars subscriptions renew themselves; referral/admin grants are gifts."""
    product = get_product(plan_code)
    return product is not None and not product.recurring


def evening_nudge_due(snap: dict, local_hour: int) -> bool:
    return (
        local_hour == int(rule("nudges.evening_local_hour", 20))
        and not snap["done_today"]
        and snap["streak"] >= int(rule("nudges.evening_min_streak", 2))
    )


async def due_users(session: Any, now_utc: datetime, target_hm: str | None = None) -> list:
    """Onboarded users whose local time equals ``target_hm`` (default: their reminder time).

    Users who switched reminders off ("off") are never returned.
    """
    from app.infrastructure.db.models.user import UserModel

    rows = (
        (
            await session.execute(
                select(UserModel).where(
                    UserModel.telegram_id > 0,
                    UserModel.onboarding_completed_at.isnot(None),
                    or_(UserModel.reminder_time.is_(None), UserModel.reminder_time != "off"),
                )
            )
        )
        .scalars()
        .all()
    )
    out = []
    for user in rows:
        want = target_hm or user.reminder_time or DEFAULT_REMINDER_TIME
        if local_now(user.timezone, now_utc).strftime("%H:%M") == want:
            out.append(user)
    return out


def _ttl() -> int:
    return int(rule("nudges.dedup_ttl_days", 10)) * 86400


async def send_renewal_reminders(
    session_factory: Any, bot: Any, guard: Any, now_utc: datetime | None = None
) -> int:
    """3 and 1 day(s) before a one-time pack ends. Subscriptions are not nagged."""
    from app.infrastructure.db.models.pet import PetModel
    from app.infrastructure.db.models.subscription import SubscriptionModel

    now_utc = now_utc or datetime.now(UTC)
    sent = 0
    async with session_factory() as session:
        for user in await due_users(session, now_utc):
            if not has_premium(user) or user.subscription_expires_at is None:
                continue
            sub = (
                (
                    await session.execute(
                        select(SubscriptionModel)
                        .where(
                            SubscriptionModel.user_id == user.id,
                            SubscriptionModel.provider == "telegram_stars",
                            SubscriptionModel.status == "active",
                        )
                        .order_by(SubscriptionModel.expires_at.desc())
                        .limit(1)
                    )
                )
                .scalars()
                .first()
            )
            if sub is None or not is_one_time_pack(sub.plan_code):
                continue
            stage = renewal_stage(user.subscription_expires_at, user.timezone, now_utc)
            if stage is None or not await guard.first(f"renew:{sub.id}:{stage}", _ttl()):
                continue
            pet = (
                (
                    await session.execute(
                        select(PetModel).where(PetModel.user_id == user.id).limit(1)
                    )
                )
                .scalars()
                .first()
            )
            lang = normalize_locale(user.language_code)
            exp_local = local_now(user.timezone, user.subscription_expires_at.replace(tzinfo=UTC))
            key = "nudge.renew.last" if stage == 1 else "nudge.renew.soon"
            text = t(
                key,
                lang,
                n=stage,
                date=exp_local.strftime("%d.%m.%Y"),
                pet=pet.name if pet else "",
            )
            kb = types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text=t("nudge.renew.btn", lang), callback_data="menu_premium"
                        )
                    ]
                ]
            )
            try:
                await bot.send_message(user.telegram_id, text, reply_markup=kb, parse_mode="HTML")
                sent += 1
            except Exception as e:
                logger.warning("renewal reminder to %s failed: %s", user.telegram_id, e)
    return sent


async def send_evening_nudges(
    session_factory: Any, bot: Any, guard: Any, now_utc: datetime | None = None
) -> int:
    """Once per local day, at the evening hour, if there is a streak to lose."""
    from app.infrastructure.db.models.pet import PetModel
    from app.infrastructure.db.repositories.activity_repo import ActivityRepository
    from app.services.tracker import snapshot

    now_utc = now_utc or datetime.now(UTC)
    hour = int(rule("nudges.evening_local_hour", 20))
    sent = 0
    async with session_factory() as session:
        repo = ActivityRepository(session)
        for user in await due_users(session, now_utc, target_hm=f"{hour:02d}:00"):
            local = local_now(user.timezone, now_utc)
            pet = (
                (
                    await session.execute(
                        select(PetModel).where(PetModel.user_id == user.id).limit(1)
                    )
                )
                .scalars()
                .first()
            )
            if pet is None:
                continue
            snap = snapshot(await repo.rows(pet.id, local.date()), local.date(), has_premium(user))
            if not evening_nudge_due(snap, local.hour):
                continue
            if not await guard.first(f"evening:{user.id}:{local.date().isoformat()}", 2 * 86400):
                continue
            lang = normalize_locale(user.language_code)
            text = t("nudge.evening", lang, n=snap["streak"], pet=pet.name)
            kb = types.InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        types.InlineKeyboardButton(
                            text=t("menu.btn.training", lang), callback_data="menu_training"
                        )
                    ]
                ]
            )
            try:
                await bot.send_message(user.telegram_id, text, reply_markup=kb, parse_mode="HTML")
                sent += 1
            except Exception as e:
                logger.warning("evening nudge to %s failed: %s", user.telegram_id, e)
    return sent
