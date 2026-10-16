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
        provider: str = "telegram_stars",
    ) -> SubscriptionModel:
        sub = SubscriptionModel(
            user_id=user_id,
            plan_code=plan_code,
            status="active",
            provider=provider,
            telegram_payment_charge_id=charge_id,
            expires_at=expires_at,
        )
        self.session.add(sub)
        await self.session.commit()
        await self.session.refresh(sub)
        return sub

    async def get_active(self, user_id: int) -> SubscriptionModel | None:
        """Latest still-valid active subscription (users may have several)."""
        result = await self.session.execute(
            select(SubscriptionModel)
            .where(
                SubscriptionModel.user_id == user_id,
                SubscriptionModel.status == "active",
                SubscriptionModel.expires_at > datetime.utcnow(),
            )
            .order_by(SubscriptionModel.expires_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_by_charge_id(self, charge_id: str) -> SubscriptionModel | None:
        result = await self.session.execute(
            select(SubscriptionModel).where(
                SubscriptionModel.telegram_payment_charge_id == charge_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_expired_subscription_ids(self) -> list[int]:
        """IDs of active subscription rows that have passed expiry (not user ids)."""
        result = await self.session.execute(
            select(SubscriptionModel.id).where(
                SubscriptionModel.status == "active",
                SubscriptionModel.expires_at <= datetime.utcnow(),
            )
        )
        return list(result.scalars().all())

    async def mark_expired_by_ids(self, subscription_ids: list[int]) -> list[int]:
        """Expire only the given subscription rows. Returns affected user_ids."""
        if not subscription_ids:
            return []
        result = await self.session.execute(
            select(SubscriptionModel.user_id).where(SubscriptionModel.id.in_(subscription_ids))
        )
        user_ids = list({uid for uid in result.scalars().all() if uid is not None})
        await self.session.execute(
            update(SubscriptionModel)
            .where(
                SubscriptionModel.id.in_(subscription_ids),
                SubscriptionModel.status == "active",
            )
            .values(status="expired")
        )
        return user_ids

    async def has_valid_active(self, user_id: int) -> bool:
        sub = await self.get_active(user_id)
        return sub is not None

    async def max_active_expires_at(self, user_id: int) -> datetime | None:
        """Latest expires_at among still-valid active subs for stacking purchases."""
        result = await self.session.execute(
            select(SubscriptionModel.expires_at)
            .where(
                SubscriptionModel.user_id == user_id,
                SubscriptionModel.status == "active",
                SubscriptionModel.expires_at > datetime.utcnow(),
            )
            .order_by(SubscriptionModel.expires_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    # ── backward-compat aliases used by expire job (rewritten) ───────────────

    async def get_expired_user_ids(self) -> list[int]:
        """Deprecated path: prefer get_expired_subscription_ids + recompute premium."""
        result = await self.session.execute(
            select(SubscriptionModel.user_id).where(
                SubscriptionModel.status == "active",
                SubscriptionModel.expires_at <= datetime.utcnow(),
            )
        )
        return list({uid for uid in result.scalars().all() if uid is not None})

    async def mark_expired(self, user_ids: list[int]) -> None:
        """Expire only past-due rows for these users — never kill still-valid ones."""
        if not user_ids:
            return
        await self.session.execute(
            update(SubscriptionModel)
            .where(
                SubscriptionModel.user_id.in_(user_ids),
                SubscriptionModel.status == "active",
                SubscriptionModel.expires_at <= datetime.utcnow(),
            )
            .values(status="expired")
        )
