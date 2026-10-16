from dataclasses import dataclass
from datetime import date, datetime, timedelta

from sqlalchemy import func, select

from app.i18n import t
from app.infrastructure.db.models.subscription import SubscriptionModel
from app.infrastructure.db.models.user import UserModel
from app.infrastructure.db.repositories.user_repo import UserRepository
from app.logic.rules import rule

REFERRAL_BONUS_DAYS = int(rule("referral.bonus_days", 3))
REFERRAL_DAILY_LIMIT = int(rule("referral.daily_limit", 10))

# Milestone tiers from rules.json — plan_code is idempotency key in SubscriptionModel.
REFERRAL_MILESTONES = list(
    rule(
        "referral.milestones",
        [
            {"count": 3, "bonus_days": 7, "plan_code": "milestone_3"},
            {"count": 5, "bonus_days": 14, "plan_code": "milestone_5"},
            {"count": 10, "bonus_days": 30, "plan_code": "milestone_10"},
            {"count": 25, "bonus_days": 90, "plan_code": "milestone_25"},
        ],
    )
)


def milestone_label(m: dict, lang: str) -> str:
    return t(f"referral.milestone.label.{m['count']}", lang)


def milestone_reward(m: dict, lang: str) -> str:
    return t("referral.reward.days", lang, days=m["bonus_days"])


@dataclass
class ReferralAwardResult:
    base_awarded: bool = False
    milestone: dict | None = None
    referrer_telegram_id: int | None = None
    referrer_lang: str = "ru"
    new_referral_count: int = 0


class ReferralService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def award_if_eligible(self, new_user: UserModel) -> ReferralAwardResult:
        """Award referral bonus to new_user and their referrer. Also checks milestones for referrer."""
        result = ReferralAwardResult()
        if new_user.referral_bonus_given:
            return result
        referrer_tid = new_user.referrer_telegram_id
        if not referrer_tid or referrer_tid == new_user.telegram_id:
            return result

        session = self.user_repo.session
        referrer = await self.user_repo.get_by_telegram_id(referrer_tid)
        if not referrer:
            return result

        daily_count = await self._count_referrer_bonuses_today(session, referrer.id)
        if daily_count >= REFERRAL_DAILY_LIMIT:
            return result

        now = datetime.utcnow()
        bonus = timedelta(days=REFERRAL_BONUS_DAYS)

        # Award new user
        new_user.is_premium = True
        new_user.subscription_expires_at = max(new_user.subscription_expires_at or now, now) + bonus
        new_user.referral_bonus_given = True
        session.add(
            SubscriptionModel(
                user_id=new_user.id,
                plan_code="referral_bonus",
                status="active",
                provider="referral",
                expires_at=new_user.subscription_expires_at,
            )
        )

        # Award referrer base bonus
        referrer.is_premium = True
        referrer.subscription_expires_at = max(referrer.subscription_expires_at or now, now) + bonus
        session.add(
            SubscriptionModel(
                user_id=referrer.id,
                plan_code="referral_bonus",
                status="active",
                provider="referral",
                expires_at=referrer.subscription_expires_at,
            )
        )

        await session.commit()
        result.base_awarded = True
        result.referrer_telegram_id = referrer.telegram_id
        result.referrer_lang = referrer.language_code or "ru"

        # Count AFTER commit so the new referral is included
        count = await self.count_successful_referrals(referrer.telegram_id)
        result.new_referral_count = count
        result.milestone = await self.check_and_award_milestones(referrer, count=count)

        return result

    async def check_and_award_milestones(
        self, referrer: UserModel, count: int | None = None
    ) -> dict | None:
        """Award any newly reached milestone bonuses. Returns the highest newly awarded milestone or None."""
        if count is None:
            count = await self.count_successful_referrals(referrer.telegram_id)
        session = self.user_repo.session
        now = datetime.utcnow()
        last_awarded = None

        for milestone in REFERRAL_MILESTONES:
            if count < milestone["count"]:
                break

            already = await session.scalar(
                select(func.count())
                .select_from(SubscriptionModel)
                .where(
                    SubscriptionModel.user_id == referrer.id,
                    SubscriptionModel.plan_code == milestone["plan_code"],
                    SubscriptionModel.provider == "referral",
                )
            )
            if already:
                continue

            referrer.is_premium = True
            referrer.subscription_expires_at = max(
                referrer.subscription_expires_at or now, now
            ) + timedelta(days=milestone["bonus_days"])
            session.add(
                SubscriptionModel(
                    user_id=referrer.id,
                    plan_code=milestone["plan_code"],
                    status="active",
                    provider="referral",
                    expires_at=referrer.subscription_expires_at,
                )
            )
            last_awarded = milestone

        if last_awarded:
            await session.commit()

        return last_awarded

    async def count_successful_referrals(self, referrer_telegram_id: int) -> int:
        result = await self.user_repo.session.execute(
            select(func.count())
            .select_from(UserModel)
            .where(
                UserModel.referrer_telegram_id == referrer_telegram_id,
                UserModel.referral_bonus_given == True,
            )
        )
        return result.scalar() or 0

    async def get_milestone_progress(self, referrer_telegram_id: int) -> dict:
        """Returns current referral count, next milestone, and how many invites are needed."""
        count = await self.count_successful_referrals(referrer_telegram_id)
        next_milestone = next(
            (m for m in REFERRAL_MILESTONES if count < m["count"]),
            None,
        )
        return {
            "count": count,
            "next_milestone": next_milestone,
            "needed": (next_milestone["count"] - count) if next_milestone else 0,
        }

    @staticmethod
    async def _count_referrer_bonuses_today(session, referrer_user_id: int) -> int:
        today_start = datetime.combine(date.today(), datetime.min.time())
        result = await session.execute(
            select(func.count())
            .select_from(SubscriptionModel)
            .where(
                SubscriptionModel.user_id == referrer_user_id,
                SubscriptionModel.plan_code == "referral_bonus",
                SubscriptionModel.provider == "referral",
                SubscriptionModel.created_at >= today_start,
            )
        )
        return result.scalar() or 0


async def notify_referrer(bot, result: ReferralAwardResult, lang: str) -> None:
    """Send a push notification to the referrer after a successful referral.

    Silently skips if the referrer blocked the bot or any other network error.
    """
    tid = result.referrer_telegram_id
    if not tid:
        return

    count = result.new_referral_count

    if result.milestone:
        m = result.milestone
        idx = next(
            (i for i, ms in enumerate(REFERRAL_MILESTONES) if ms["plan_code"] == m["plan_code"]),
            -1,
        )
        next_m = REFERRAL_MILESTONES[idx + 1] if 0 <= idx < len(REFERRAL_MILESTONES) - 1 else None
        next_hint = (
            t(
                "referral.notify.next_hint",
                lang,
                next_label=milestone_label(next_m, lang),
                next_reward=milestone_reward(next_m, lang),
            )
            if next_m
            else t("referral.notify.all_done", lang)
        )
        text = t(
            "referral.notify.milestone",
            lang,
            label=milestone_label(m, lang),
            count=count,
            reward=milestone_reward(m, lang),
            next_hint=next_hint,
        )
    else:
        next_m = next((ms for ms in REFERRAL_MILESTONES if count < ms["count"]), None)
        ladder_hint = (
            t(
                "referral.notify.next_hint",
                lang,
                next_label=milestone_label(next_m, lang),
                next_reward=milestone_reward(next_m, lang),
            )
            if next_m
            else t("referral.notify.all_done", lang)
        )
        text = t(
            "referral.notify.base",
            lang,
            days=REFERRAL_BONUS_DAYS,
            count=count,
            ladder_hint=ladder_hint,
        )

    try:
        await bot.send_message(tid, text, parse_mode="HTML")
    except Exception:
        pass
