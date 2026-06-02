import logging

from sqlalchemy import update
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.infrastructure.db.models.user import UserModel
from app.infrastructure.db.repositories.subscription_repo import SubscriptionRepository

logger = logging.getLogger(__name__)


async def expire_subscriptions(session_factory: async_sessionmaker) -> None:
    user_ids: list[int] = []
    async with session_factory() as session:
        repo = SubscriptionRepository(session)
        user_ids = await repo.get_expired_user_ids()

        if user_ids:
            await repo.mark_expired(user_ids)
            await session.execute(
                update(UserModel)
                .where(UserModel.id.in_(user_ids))
                .values(is_premium=False, subscription_expires_at=None)
            )
            await session.commit()

    logger.info("Subscriptions expired: %d users downgraded", len(user_ids))
