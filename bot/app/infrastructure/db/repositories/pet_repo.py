from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.models.pet import PetModel

class PetRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_id(self, user_id: int) -> PetModel | None:
        query = select(PetModel).where(PetModel.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, pet: PetModel) -> PetModel:
        self.session.add(pet)
        await self.session.commit()
        await self.session.refresh(pet)
        return pet
