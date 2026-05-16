from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from dependency_injector.wiring import Provide, inject
from sqlalchemy import delete, select

from app.core.container import AppContainer
from app.services.user_service import UserService
from app.infrastructure.db.models.pet import PetModel
from app.infrastructure.db.models.training import TrainingPlanModel, TrainingTaskModel
from app.infrastructure.db.models.ai_conversation import AiConversationModel
from app.bot.states.onboarding import OnboardingStates
from app.i18n import t, normalize_locale

router = Router(name="reset_router")


@router.message(Command("reset"))
@inject
async def reset_profile(
    msg: types.Message,
    state: FSMContext,
    u_svc: UserService = Provide[AppContainer.user_service],
) -> None:
    await state.clear()

    usr = await u_svc.get_or_create_telegram_user(telegram_id=msg.from_user.id)
    session = u_svc.repo.session

    # Собираем id питомцев
    pet_ids_result = await session.execute(
        select(PetModel.id).where(PetModel.user_id == usr.id)
    )
    pet_ids = [r[0] for r in pet_ids_result.fetchall()]

    if pet_ids:
        # id планов → удаляем задачи
        plan_ids_result = await session.execute(
            select(TrainingPlanModel.id).where(TrainingPlanModel.pet_id.in_(pet_ids))
        )
        plan_ids = [r[0] for r in plan_ids_result.fetchall()]
        if plan_ids:
            await session.execute(
                delete(TrainingTaskModel).where(TrainingTaskModel.plan_id.in_(plan_ids))
            )
        await session.execute(
            delete(TrainingPlanModel).where(TrainingPlanModel.pet_id.in_(pet_ids))
        )
        await session.execute(
            delete(AiConversationModel).where(AiConversationModel.pet_id.in_(pet_ids))
        )

    await session.execute(delete(PetModel).where(PetModel.user_id == usr.id))

    # Сбрасываем онбординг; coach_threads сохраняются — только сбрасываем активный тред
    usr.onboarding_completed_at = None
    usr.active_coach_thread_id = None
    await session.commit()

    lang = normalize_locale(usr.language_code)
    await msg.answer(
        t("onboarding.ai.welcome", lang, name=msg.from_user.first_name),
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(OnboardingStates.collecting)
