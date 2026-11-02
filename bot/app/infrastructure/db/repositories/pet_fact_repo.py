from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.pet_fact import PetFactModel


class PetFactRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_active(self, pet_id: int, limit: int = 100) -> list[PetFactModel]:
        result = await self.session.execute(
            select(PetFactModel)
            .where(PetFactModel.pet_id == pet_id, PetFactModel.deleted_at.is_(None))
            .order_by(PetFactModel.id.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def add_many(self, pet_id: int, facts: list[str], source: str = "ai") -> int:
        for text in facts:
            self.session.add(PetFactModel(pet_id=pet_id, fact=text, source=source))
        await self.session.commit()
        return len(facts)

    async def soft_delete(self, fact_id: int, pet_id: int) -> bool:
        """Delete only if the fact belongs to this pet (callback data is user-controlled)."""
        result = await self.session.execute(
            update(PetFactModel)
            .where(
                PetFactModel.id == fact_id,
                PetFactModel.pet_id == pet_id,
                PetFactModel.deleted_at.is_(None),
            )
            .values(deleted_at=datetime.utcnow())
        )
        await self.session.commit()
        return (result.rowcount or 0) > 0
