from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.coach_thread import CoachThreadModel


class CoachThreadRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, thread_id: int) -> CoachThreadModel | None:
        result = await self.session.execute(
            select(CoachThreadModel).where(CoachThreadModel.id == thread_id)
        )
        return result.scalar_one_or_none()

    async def create(self, user_id: int) -> CoachThreadModel:
        thread = CoachThreadModel(user_id=user_id, messages_json=[], message_count=0)
        self.session.add(thread)
        await self.session.flush()
        return thread

    async def list_by_user(self, user_id: int, status: str | None = None) -> list[CoachThreadModel]:
        q = select(CoachThreadModel).where(CoachThreadModel.user_id == user_id)
        if status:
            q = q.where(CoachThreadModel.status == status)
        q = q.order_by(CoachThreadModel.updated_at.desc())
        result = await self.session.execute(q)
        return list(result.scalars().all())
