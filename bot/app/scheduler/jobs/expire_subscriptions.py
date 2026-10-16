import logging

from sqlalchemy import update
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.infrastructure.db.models.user import UserModel
from app.infrastructure.db.repositories.subscription_repo import SubscriptionRepository

logger = logging.getLogger(__name__)


async def expire_subscriptions(session_factory: async_sessionmaker) -> None:
    """Expire past-due subscription rows, then recompute is_premium per user.

    Critical: do NOT mark all of a user's active subs as expired when only one
    row is past due (paid Stars + referral stack is common).
    """
    downgraded = 0
    expired_rows = 0

    async with session_factory() as session:
        repo = SubscriptionRepository(session)
        sub_ids = await repo.get_expired_subscription_ids()
        if not sub_ids:
            logger.info("Subscriptions expired: 0 rows, 0 users downgraded")
            return

        user_ids = await repo.mark_expired_by_ids(sub_ids)
        expired_rows = len(sub_ids)
        await session.flush()

        for uid in user_ids:
            still_active = await repo.get_active(uid)
            if still_active:
                # Keep premium; sync expires_at to the longest remaining sub
                await session.execute(
                    update(UserModel)
                    .where(UserModel.id == uid)
                    .values(
                        is_premium=True,
                        subscription_expires_at=still_active.expires_at,
                    )
                )
            else:
                await session.execute(
                    update(UserModel)
                    .where(UserModel.id == uid)
                    .values(is_premium=False, subscription_expires_at=None)
                )
                downgraded += 1

        await session.commit()

    logger.info(
        "Subscriptions expired: %d rows, %d users fully downgraded",
        expired_rows,
        downgraded,
    )
