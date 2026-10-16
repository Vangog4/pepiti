from datetime import date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.db.models.training import TrainingPlanModel, TrainingTaskModel


class TrainingPlanRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_active_plan(self, pet_id: int) -> TrainingPlanModel | None:
        """Latest active plan for the pet (week or daily)."""
        result = await self.session.execute(
            select(TrainingPlanModel)
            .where(
                TrainingPlanModel.pet_id == pet_id,
                TrainingPlanModel.is_active == True,
            )
            .options(selectinload(TrainingPlanModel.tasks))
            .order_by(TrainingPlanModel.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_active_today(self, pet_id: int) -> TrainingPlanModel | None:
        result = await self.session.execute(
            select(TrainingPlanModel)
            .where(
                TrainingPlanModel.pet_id == pet_id,
                TrainingPlanModel.is_active == True,
                func.date(TrainingPlanModel.created_at) == date.today(),
            )
            .options(selectinload(TrainingPlanModel.tasks))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def deactivate_for_pet(self, pet_id: int) -> None:
        plans = await self.session.execute(
            select(TrainingPlanModel).where(
                TrainingPlanModel.pet_id == pet_id,
                TrainingPlanModel.is_active == True,
            )
        )
        for plan in plans.scalars():
            plan.is_active = False
        await self.session.commit()

    async def create_with_tasks(
        self, user_id: int, pet_id: int, plan_data: dict
    ) -> TrainingPlanModel:
        plan = TrainingPlanModel(
            user_id=user_id,
            pet_id=pet_id,
            title=plan_data.get("title", "Тренировка дня"),
            goal=plan_data.get("goal"),
            is_active=True,
        )
        self.session.add(plan)
        await self.session.flush()

        for idx, t in enumerate(plan_data.get("tasks", [])):
            self.session.add(
                TrainingTaskModel(
                    plan_id=plan.id,
                    day_of_week=idx,
                    title=t.get("title", f"Задача {idx + 1}"),
                    description=t.get("description"),
                    duration_minutes=t.get("duration_minutes"),
                    difficulty=t.get("difficulty"),
                )
            )

        await self.session.commit()

        result = await self.session.execute(
            select(TrainingPlanModel)
            .where(TrainingPlanModel.id == plan.id)
            .options(selectinload(TrainingPlanModel.tasks))
        )
        return result.scalar_one()

    async def get_active_week_plan(self, pet_id: int) -> TrainingPlanModel | None:
        created_after = datetime.utcnow() - timedelta(days=7)
        result = await self.session.execute(
            select(TrainingPlanModel)
            .where(
                TrainingPlanModel.pet_id == pet_id,
                TrainingPlanModel.is_active == True,
                TrainingPlanModel.week_number.isnot(None),
                TrainingPlanModel.created_at >= created_after,
            )
            .options(selectinload(TrainingPlanModel.tasks))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def create_week_plan(
        self, user_id: int, pet_id: int, plan_data: dict, week_number: int
    ) -> TrainingPlanModel:
        plan = TrainingPlanModel(
            user_id=user_id,
            pet_id=pet_id,
            title=plan_data.get("title", "Недельный план"),
            goal=plan_data.get("goal"),
            week_number=week_number,
            is_active=True,
        )
        self.session.add(plan)
        await self.session.flush()

        for day_data in plan_data.get("days", []):
            day = day_data.get("day", 1)
            for t in day_data.get("tasks", []):
                self.session.add(
                    TrainingTaskModel(
                        plan_id=plan.id,
                        day_of_week=day,
                        title=t.get("title", "Задача"),
                        description=t.get("description"),
                        duration_minutes=t.get("duration_minutes"),
                        difficulty=t.get("difficulty"),
                    )
                )

        await self.session.commit()
        result = await self.session.execute(
            select(TrainingPlanModel)
            .where(TrainingPlanModel.id == plan.id)
            .options(selectinload(TrainingPlanModel.tasks))
        )
        return result.scalar_one()

    async def day_tasks_done(self, plan_id: int, day_of_week: int) -> bool:
        result = await self.session.execute(
            select(func.count())
            .select_from(TrainingTaskModel)
            .where(
                TrainingTaskModel.plan_id == plan_id,
                TrainingTaskModel.day_of_week == day_of_week,
                TrainingTaskModel.is_completed == False,
            )
        )
        return result.scalar() == 0

    async def get_plan(self, plan_id: int) -> TrainingPlanModel | None:
        result = await self.session.execute(
            select(TrainingPlanModel).where(TrainingPlanModel.id == plan_id)
        )
        return result.scalar_one_or_none()

    async def get_task(self, task_id: int) -> TrainingTaskModel | None:
        result = await self.session.execute(
            select(TrainingTaskModel).where(TrainingTaskModel.id == task_id)
        )
        return result.scalar_one_or_none()

    async def all_tasks_done(self, plan_id: int) -> bool:
        result = await self.session.execute(
            select(func.count())
            .select_from(TrainingTaskModel)
            .where(
                TrainingTaskModel.plan_id == plan_id,
                TrainingTaskModel.is_completed == False,
            )
        )
        return result.scalar() == 0
