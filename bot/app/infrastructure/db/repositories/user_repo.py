from datetime import date

from sqlalchemy import distinct, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models.training import TrainingPlanModel, TrainingTaskModel
from app.infrastructure.db.models.user import UserModel


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int) -> UserModel | None:
        query = select(UserModel).where(UserModel.telegram_id == telegram_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create(
        self,
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        language_code: str | None = None,
    ) -> UserModel:
        user = UserModel(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)  # ИСПРАВЛЕНИЕ: обновляем объект асинхронно
        return user

    async def get_all_with_onboarding(self) -> list[UserModel]:
        result = await self.session.execute(
            select(UserModel).where(UserModel.onboarding_completed_at.isnot(None))
        )
        return list(result.scalars().all())

    async def get_by_username(self, username: str) -> UserModel | None:
        clean = username.lstrip("@").lower()
        result = await self.session.execute(
            select(UserModel).where(func.lower(UserModel.username) == clean)
        )
        return result.scalar_one_or_none()

    async def search_users(self, q: str, limit: int = 20) -> list[UserModel]:
        q = q.strip()
        if q.lstrip("-").isdigit():
            result = await self.session.execute(
                select(UserModel).where(UserModel.telegram_id == int(q)).limit(1)
            )
        else:
            clean = q.lstrip("@")
            result = await self.session.execute(
                select(UserModel)
                .where(
                    or_(
                        UserModel.username.ilike(f"%{clean}%"),
                        UserModel.first_name.ilike(f"%{clean}%"),
                    )
                )
                .limit(limit)
            )
        return list(result.scalars().all())

    async def get_stats(self) -> dict:
        total = (await self.session.execute(select(func.count()).select_from(UserModel))).scalar()
        premium = (
            await self.session.execute(
                select(func.count()).select_from(UserModel).where(UserModel.is_premium == True)
            )
        ).scalar()
        onboarded = (
            await self.session.execute(
                select(func.count())
                .select_from(UserModel)
                .where(UserModel.onboarding_completed_at.isnot(None))
            )
        ).scalar()
        return {"total": total, "premium": premium, "onboarded": onboarded}

    async def get_referral_stats(self) -> dict:
        total_referred = (
            await self.session.execute(
                select(func.count())
                .select_from(UserModel)
                .where(UserModel.referral_bonus_given == True)
            )
        ).scalar() or 0

        top_result = await self.session.execute(
            select(UserModel.referrer_telegram_id, func.count().label("cnt"))
            .where(
                UserModel.referral_bonus_given == True,
                UserModel.referrer_telegram_id.isnot(None),
            )
            .group_by(UserModel.referrer_telegram_id)
            .order_by(func.count().desc())
            .limit(5)
        )
        top = top_result.all()
        return {"total_referred": total_referred, "top": top}

    async def get_rich_stats(self) -> dict:
        today = date.today()
        total = (
            await self.session.execute(select(func.count()).select_from(UserModel))
        ).scalar() or 0
        premium = (
            await self.session.execute(
                select(func.count()).select_from(UserModel).where(UserModel.is_premium == True)
            )
        ).scalar() or 0
        onboarded = (
            await self.session.execute(
                select(func.count())
                .select_from(UserModel)
                .where(UserModel.onboarding_completed_at.isnot(None))
            )
        ).scalar() or 0
        new_today = (
            await self.session.execute(
                select(func.count())
                .select_from(UserModel)
                .where(func.date(UserModel.created_at) == today)
            )
        ).scalar() or 0
        active_today = (
            await self.session.execute(
                select(func.count(distinct(TrainingPlanModel.user_id)))
                .select_from(TrainingTaskModel)
                .join(TrainingPlanModel, TrainingTaskModel.plan_id == TrainingPlanModel.id)
                .where(
                    TrainingTaskModel.is_completed == True,
                    func.date(TrainingTaskModel.completed_at) == today,
                )
            )
        ).scalar() or 0
        conversion_pct = round(premium / onboarded * 100) if onboarded else 0
        return {
            "total": total,
            "premium": premium,
            "onboarded": onboarded,
            "new_today": new_today,
            "active_today": active_today,
            "conversion_pct": conversion_pct,
        }
