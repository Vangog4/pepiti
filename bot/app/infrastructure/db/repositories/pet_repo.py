from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.pet import PetModel
from app.infrastructure.db.models.user import UserModel
from app.services.entitlements import has_premium
from app.services.pets import resolve_active


class PetRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_for_user(self, user_id: int) -> list[PetModel]:
        result = await self.session.execute(
            select(PetModel).where(PetModel.user_id == user_id).order_by(PetModel.id)
        )
        return list(result.scalars().all())

    async def get_by_user_id(self, user_id: int) -> PetModel | None:
        """The ACTIVE dog (never raises with several dogs). Locked dogs are never returned."""
        user = await self.session.get(UserModel, user_id)
        pets = await self.list_for_user(user_id)
        return resolve_active(
            pets, getattr(user, "active_pet_id", None), has_premium(user) if user else False
        )

    async def create(self, pet: PetModel) -> PetModel:
        self.session.add(pet)
        await self.session.commit()
        await self.session.refresh(pet)
        return pet
