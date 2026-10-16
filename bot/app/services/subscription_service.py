from datetime import datetime, timedelta

from app.infrastructure.db.models.subscription import SubscriptionModel
from app.infrastructure.db.repositories.subscription_repo import SubscriptionRepository
from app.infrastructure.db.repositories.user_repo import UserRepository
from app.logic.rules import rule

PREMIUM_1M_STARS = int(rule("premium.stars_1m", 299))
PREMIUM_DURATION_DAYS = int(rule("premium.duration_days", 30))


class SubscriptionService:
    def __init__(self, sub_repo: SubscriptionRepository, user_repo: UserRepository):
        self.sub_repo = sub_repo
        self.user_repo = user_repo

    async def activate(
        self,
        user_id: int,
        telegram_id: int,
        charge_id: str,
        *,
        days: int | None = None,
        plan_code: str = "premium_1m",
    ) -> SubscriptionModel:
        """Activate paid premium, stacking on remaining paid/referral days.

        New expiry = max(now, current_max_expires) + days.
        Idempotent if the same charge_id already exists.
        """
        existing = await self.sub_repo.get_by_charge_id(charge_id)
        if existing:
            return existing

        duration = days if days is not None else PREMIUM_DURATION_DAYS
        now = datetime.utcnow()
        current_end = await self.sub_repo.max_active_expires_at(user_id)
        base = max(current_end or now, now)
        expires_at = base + timedelta(days=duration)

        sub = await self.sub_repo.create(
            user_id=user_id,
            expires_at=expires_at,
            charge_id=charge_id,
            plan_code=plan_code,
        )

        user = await self.user_repo.get_by_telegram_id(telegram_id)
        if user:
            user.is_premium = True
            user.subscription_expires_at = expires_at
            await self.sub_repo.session.commit()

        return sub

    async def get_active(self, user_id: int) -> SubscriptionModel | None:
        return await self.sub_repo.get_active(user_id)
