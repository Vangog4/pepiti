from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.activity_log import ActivityLogModel

HISTORY_DAYS = 400


class ActivityRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def rows(self, pet_id: int, today: date) -> list[ActivityLogModel]:
        res = await self.session.execute(
            select(ActivityLogModel).where(
                ActivityLogModel.pet_id == pet_id,
                ActivityLogModel.local_date >= today - timedelta(days=HISTORY_DAYS),
            )
        )
        return list(res.scalars().all())

    async def log_task_day(self, pet_id: int, local_date: date) -> bool:
        """One finished training day per local date. True if newly recorded."""
        exists = await self.session.execute(
            select(ActivityLogModel.id).where(
                ActivityLogModel.pet_id == pet_id,
                ActivityLogModel.kind == "task",
                ActivityLogModel.local_date == local_date,
            )
        )
        if exists.first():
            return False
        self.session.add(ActivityLogModel(pet_id=pet_id, kind="task", local_date=local_date))
        await self.session.commit()
        return True

    async def log_walk(self, pet_id: int, local_date: date, minutes: int) -> None:
        self.session.add(
            ActivityLogModel(
                pet_id=pet_id, kind="walk", local_date=local_date, duration_min=minutes
            )
        )
        await self.session.commit()
