from datetime import UTC, date, datetime

from app.i18n import t
from app.infrastructure.db.models.pet import PetModel
from app.infrastructure.db.models.training import TrainingPlanModel, TrainingTaskModel
from app.infrastructure.db.repositories.training_repo import TrainingPlanRepository
from app.services.ai_service import AiService


def iso_weekday(d: date | None = None) -> int:
    """Monday=1 … Sunday=7 — same as bot week-plan `training.day.N`."""
    return (d or date.today()).isoweekday()


def tasks_for_today(plan: TrainingPlanModel | None) -> list[TrainingTaskModel]:
    """Tasks the WebApp / bot treat as 'today'.

    Week plan (`week_number` set): only this ISO weekday.
    Daily plan: all tasks (day_of_week there is just insertion order).
    """
    if plan is None or not plan.tasks:
        return []
    if plan.week_number is not None:
        dow = iso_weekday()
        return [task for task in plan.tasks if task.day_of_week == dow]
    return list(plan.tasks)


class TrainingService:
    def __init__(self, plan_repo: TrainingPlanRepository, ai_service: AiService):
        self.plan_repo = plan_repo
        self.ai_service = ai_service

    async def get_or_create_today(
        self, user_id: int, pet: PetModel, lang: str = "ru"
    ) -> TrainingPlanModel:
        plan = await self.plan_repo.get_active_today(pet.id)
        if plan:
            return plan
        plan_data = await self.ai_service.generate_training_plan(pet, lang=lang)
        plan_data["goal"] = plan_data.get("goal") or pet.goal
        # Deactivate any stale active plans (e.g. yesterday's) before creating
        await self.plan_repo.deactivate_for_pet(pet.id)
        return await self.plan_repo.create_with_tasks(user_id, pet.id, plan_data)

    async def refresh_plan(
        self, user_id: int, pet: PetModel, lang: str = "ru"
    ) -> TrainingPlanModel:
        await self.plan_repo.deactivate_for_pet(pet.id)
        plan_data = await self.ai_service.generate_training_plan(pet, lang=lang)
        plan_data["goal"] = plan_data.get("goal") or pet.goal
        return await self.plan_repo.create_with_tasks(user_id, pet.id, plan_data)

    async def get_or_create_week(
        self, user_id: int, pet: PetModel, lang: str = "ru"
    ) -> TrainingPlanModel:
        plan = await self.plan_repo.get_active_week_plan(pet.id)
        if plan:
            return plan
        week_number = date.today().isocalendar()[1]
        # Deactivate prior active plans for this pet (old week / stale day)
        await self.plan_repo.deactivate_for_pet(pet.id)
        plan_data = await self.ai_service.generate_week_plan(pet, lang=lang)
        plan_data["goal"] = plan_data.get("goal") or pet.goal
        return await self.plan_repo.create_week_plan(user_id, pet.id, plan_data, week_number)

    async def toggle_task(self, task_id: int, pet: PetModel) -> tuple[TrainingTaskModel, bool]:
        """Toggle task completion. Returns (task, scope_completed).

        Daily plan: scope = whole plan (`counted_at`).
        Week plan: scope = that weekday (`counted_day_N`) — same as bot week_task.
        """
        task = await self.plan_repo.get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        task.is_completed = not task.is_completed
        if task.is_completed:
            task.completed_at = datetime.now(UTC).replace(tzinfo=None)
        else:
            task.completed_at = None

        await self.plan_repo.session.commit()

        plan = await self.plan_repo.get_plan(task.plan_id)
        if plan is not None and plan.week_number is not None and task.day_of_week is not None:
            day_done = await self.plan_repo.day_tasks_done(task.plan_id, task.day_of_week)
            if day_done and task.is_completed:
                meta = plan.plan_json or {}
                day_key = f"counted_day_{task.day_of_week}"
                if not meta.get(day_key):
                    pet.training_days = (pet.training_days or 0) + 1
                    plan.plan_json = {**meta, day_key: date.today().isoformat()}
                    await self.plan_repo.session.commit()
            return task, day_done

        plan_done = False
        if task.is_completed:
            plan_done = await self.plan_repo.all_tasks_done(task.plan_id)
            if plan_done and plan is not None:
                meta = plan.plan_json or {}
                if not meta.get("counted_at"):
                    pet.training_days = (pet.training_days or 0) + 1
                    plan.plan_json = {**meta, "counted_at": date.today().isoformat()}
                    await self.plan_repo.session.commit()

        return task, plan_done

    async def mark_task_by_hint(
        self, pet: PetModel, hint: str
    ) -> tuple["TrainingTaskModel | None", bool]:
        """Find today's incomplete task matching hint and mark it done.

        Matching rules (strict → safe):
        1. Substring match between hint and title (either way).
        2. If exactly one incomplete task remains — mark it (safe default).
        3. Otherwise no match — do not guess (avoids wrong task marked).
        Returns (task, plan_fully_done).
        """
        plan = await self.plan_repo.get_active_plan(pet.id)
        today_tasks = tasks_for_today(plan)
        if not today_tasks:
            return None, False

        incomplete = [task for task in today_tasks if not task.is_completed]
        if not incomplete:
            return None, True

        hint_lower = (hint or "").strip().lower()
        matched = None
        if hint_lower:
            matched = next(
                (
                    t
                    for t in incomplete
                    if hint_lower in t.title.lower() or t.title.lower() in hint_lower
                ),
                None,
            )
        if matched is None and len(incomplete) == 1:
            matched = incomplete[0]
        if matched is None:
            return None, False
        return await self.toggle_task(matched.id, pet)

    @staticmethod
    def format_week_day(plan: TrainingPlanModel, day: int, lang: str = "ru") -> str:
        diff_map = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}
        day_tasks = sorted(
            [task for task in plan.tasks if task.day_of_week == day],
            key=lambda task: task.id,
        )
        day_name = t(f"training.day.{day}", lang)
        lines = [f"📅 <b>{plan.title}</b>", f"<i>{day_name}</i>\n"]
        for i, task in enumerate(day_tasks, 1):
            done_icon = "✅" if task.is_completed else "⬜"
            diff = diff_map.get(task.difficulty or "", "")
            min_abbr = t("training.minutes.abbr", lang)
            duration = f"⏱ {task.duration_minutes} {min_abbr}" if task.duration_minutes else ""
            meta = " ".join(filter(None, [diff, duration]))
            lines.append(f"{done_icon} <b>{i}. {task.title}</b>")
            if task.description:
                lines.append(task.description)
            if meta:
                lines.append(f"<i>{meta}</i>")
            lines.append("")
        if plan.goal:
            lines.append(f"🎯 <i>{t('training.goal.label', lang)}: {plan.goal}</i>")
        return "\n".join(lines).strip()

    @staticmethod
    def format_plan(plan: TrainingPlanModel, lang: str = "ru") -> str:
        diff_map = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}
        lines = [f"🏋️ <b>{plan.title}</b>\n"]

        tasks = sorted(plan.tasks, key=lambda task: task.day_of_week or 0)
        for i, task in enumerate(tasks, 1):
            done_icon = "✅" if task.is_completed else "⬜"
            diff = diff_map.get(task.difficulty or "", "")
            min_abbr = t("training.minutes.abbr", lang)
            duration = f"⏱ {task.duration_minutes} {min_abbr}" if task.duration_minutes else ""
            meta = " ".join(filter(None, [diff, duration]))

            lines.append(f"{done_icon} <b>{i}. {task.title}</b>")
            if task.description:
                lines.append(task.description)
            if meta:
                lines.append(f"<i>{meta}</i>")
            lines.append("")

        if plan.goal:
            lines.append(f"🎯 <i>{t('training.goal.label', lang)}: {plan.goal}</i>")
        return "\n".join(lines).strip()
