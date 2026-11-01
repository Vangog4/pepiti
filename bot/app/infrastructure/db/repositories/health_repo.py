from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.health_event import HealthEventModel
from app.infrastructure.db.models.pet import PetModel


class HealthRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def for_pet(self, pet_id: int) -> list[HealthEventModel]:
        res = await self.session.execute(
            select(HealthEventModel).where(HealthEventModel.pet_id == pet_id)
        )
        return list(res.scalars().all())

    async def add(
        self, pet_id: int, kind: str, done_at: date, next_due_at: date
    ) -> HealthEventModel:
        ev = HealthEventModel(pet_id=pet_id, kind=kind, done_at=done_at, next_due_at=next_due_at)
        self.session.add(ev)
        await self.session.commit()
        await self.session.refresh(ev)
        return ev

    async def get_owned(self, event_id: int, user_id: int) -> HealthEventModel | None:
        """Event only if its dog belongs to this user (callback data is user-controlled)."""
        res = await self.session.execute(
            select(HealthEventModel)
            .join(PetModel, PetModel.id == HealthEventModel.pet_id)
            .where(HealthEventModel.id == event_id, PetModel.user_id == user_id)
        )
        return res.scalar_one_or_none()

    async def snooze(self, ev: HealthEventModel, days: int) -> None:
        ev.next_due_at = ev.next_due_at + timedelta(days=days)
        ev.last_notified_on = None
        await self.session.commit()

    async def mark_notified(self, ev: HealthEventModel, today: date) -> None:
        ev.last_notified_on = today
        await self.session.commit()
