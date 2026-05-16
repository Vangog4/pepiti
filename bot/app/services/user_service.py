from app.infrastructure.db.repositories.user_repo import UserRepository
from app.infrastructure.db.models.user import UserModel

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def get_or_create_telegram_user(self, telegram_id: int, username: str | None = None,
                                          first_name: str | None = None, last_name: str | None = None,
                                          language_code: str | None = None) -> UserModel:
        user = await self.repo.get_by_telegram_id(telegram_id)
        if not user:
            user = await self.repo.create(telegram_id, username, first_name, last_name, language_code)
        return user
