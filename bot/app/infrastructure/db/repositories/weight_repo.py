from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.weight_log import WeightLogModel


class WeightRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, pet_id: int, weight_kg: float, local_date: date) -> None:
        self.session.add(WeightLogModel(pet_id=pet_id, weight_kg=weight_kg, local_date=local_date))
        await self.session.commit()

    async def recent(self, pet_id: int, limit: int = 60) -> list[WeightLogModel]:
        res = await self.session.execute(
            select(WeightLogModel)
            .where(WeightLogModel.pet_id == pet_id)
            .order_by(WeightLogModel.local_date.desc(), WeightLogModel.id.desc())
            .limit(limit)
        )
        return list(res.scalars().all())
