from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.ai_conversation import AiConversationModel


class AiConversationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        user_id: int,
        question: str,
        answer: str,
        pet_id: int | None = None,
        topic: str | None = None,
    ) -> AiConversationModel:
        record = AiConversationModel(
            user_id=user_id,
            pet_id=pet_id,
            question=question[:2000],
            answer=answer[:4000],
            topic=topic,
        )
        self.session.add(record)
        await self.session.commit()
        return record
