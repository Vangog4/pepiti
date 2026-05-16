from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.subscription import SubscriptionModel


class SubscriptionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        user_id: int,
        expires_at: datetime,
        charge_id: str | None = None,
        plan_code: str = "premium_1m",
    ) -> SubscriptionModel:
        sub = SubscriptionModel(
            user_id=user_id,
            plan_code=plan_code,
            status="active",
            provider="telegram_stars",
            telegram_payment_charge_id=charge_id,
            expires_at=expires_at,
        )
        self.session.add(sub)
        await self.session.commit()
        await self.session.refresh(sub)
        return sub

    async def get_active(self, user_id: int) -> SubscriptionModel | None:
        result = await self.session.execute(
            select(SubscriptionModel).where(
                SubscriptionModel.user_id == user_id,
                SubscriptionModel.status == "active",
                SubscriptionModel.expires_at > datetime.utcnow(),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_charge_id(self, charge_id: str) -> SubscriptionModel | None:
        result = await self.session.execute(
            select(SubscriptionModel).where(
                SubscriptionModel.telegram_payment_charge_id == charge_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_expired_user_ids(self) -> list[int]:
        """Return user_ids of active subscriptions that have passed their expiry date."""
        result = await self.session.execute(
            select(SubscriptionModel.user_id).where(
                SubscriptionModel.status == "active",
                SubscriptionModel.expires_at <= datetime.utcnow(),
            )
        )
        return list(result.scalars().all())

    async def mark_expired(self, user_ids: list[int]) -> None:
        """Set status=expired for all active subscriptions belonging to given user_ids."""
        await self.session.execute(
            update(SubscriptionModel)
            .where(
                SubscriptionModel.user_id.in_(user_ids),
                SubscriptionModel.status == "active",
            )
            .values(status="expired")
        )
