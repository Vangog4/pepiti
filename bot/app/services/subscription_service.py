from datetime import datetime, timedelta

from app.infrastructure.db.models.subscription import SubscriptionModel
from app.infrastructure.db.repositories.subscription_repo import SubscriptionRepository
from app.infrastructure.db.repositories.user_repo import UserRepository

PREMIUM_1M_STARS = 299
PREMIUM_DURATION_DAYS = 30


class SubscriptionService:
    def __init__(self, sub_repo: SubscriptionRepository, user_repo: UserRepository):
        self.sub_repo = sub_repo
        self.user_repo = user_repo

    async def activate(self, user_id: int, telegram_id: int, charge_id: str) -> SubscriptionModel:
        expires_at = datetime.utcnow() + timedelta(days=PREMIUM_DURATION_DAYS)
        sub = await self.sub_repo.create(
            user_id=user_id, expires_at=expires_at, charge_id=charge_id
        )

        user = await self.user_repo.get_by_telegram_id(telegram_id)
        if user:
            user.is_premium = True
            user.subscription_expires_at = expires_at
            await self.sub_repo.session.commit()

        return sub

    async def get_active(self, user_id: int) -> SubscriptionModel | None:
        return await self.sub_repo.get_active(user_id)
