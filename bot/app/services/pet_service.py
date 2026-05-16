from app.infrastructure.db.repositories.pet_repo import PetRepository
from app.infrastructure.db.models.pet import PetModel

class PetService:
    def __init__(self, repo: PetRepository):
        self.repo = repo

    async def get_pet(self, user_id: int) -> PetModel | None:
        return await self.repo.get_by_user_id(user_id)
