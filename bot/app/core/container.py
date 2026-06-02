from dependency_injector import containers, providers

from app.core.config import settings
from app.infrastructure.db.engine import create_db_engine
from app.infrastructure.db.repositories.ai_conversation_repo import AiConversationRepository
from app.infrastructure.db.repositories.coach_thread_repo import CoachThreadRepository
from app.infrastructure.db.repositories.pet_repo import PetRepository
from app.infrastructure.db.repositories.subscription_repo import SubscriptionRepository
from app.infrastructure.db.repositories.training_repo import TrainingPlanRepository
from app.infrastructure.db.repositories.user_repo import UserRepository
from app.infrastructure.db.session import create_session_factory, get_current_session
from app.infrastructure.redis.admin_log import AdminLog
from app.infrastructure.redis.ai_rate_limit import AiRateLimiter
from app.infrastructure.redis.metrics import BotMetrics
from app.services.ai_service import AiService
from app.services.coach_service import CoachService
from app.services.pet_service import PetService
from app.services.referral_service import ReferralService
from app.services.subscription_service import SubscriptionService
from app.services.training_service import TrainingService
from app.services.user_service import UserService


class AppContainer(containers.DeclarativeContainer):
    ai_service = providers.Singleton(AiService, api_key=settings.GEMINI_API_KEY)
    ai_rate_limiter = providers.Singleton(AiRateLimiter, redis_url=settings.REDIS_URL)
    metrics = providers.Singleton(BotMetrics, redis_url=settings.REDIS_URL)
    admin_log = providers.Singleton(AdminLog, redis_url=settings.REDIS_URL)
    wiring_config = containers.WiringConfiguration(packages=["app.bot.handlers"])

    # База данных
    db_engine = providers.Singleton(create_db_engine)
    session_factory = providers.Singleton(create_session_factory, engine=db_engine)

    # Сессия берётся из ContextVar, установленного middleware
    db_session = providers.Callable(get_current_session)

    # Репозитории
    user_repo = providers.Factory(UserRepository, session=db_session)
    pet_repo = providers.Factory(PetRepository, session=db_session)
    training_plan_repo = providers.Factory(TrainingPlanRepository, session=db_session)
    ai_conversation_repo = providers.Factory(AiConversationRepository, session=db_session)

    # Сервисы
    user_service = providers.Factory(UserService, repo=user_repo)
    pet_service = providers.Factory(PetService, repo=pet_repo)
    training_service = providers.Factory(
        TrainingService, plan_repo=training_plan_repo, ai_service=ai_service
    )
    subscription_repo = providers.Factory(SubscriptionRepository, session=db_session)
    subscription_service = providers.Factory(
        SubscriptionService, sub_repo=subscription_repo, user_repo=user_repo
    )
    referral_service = providers.Factory(ReferralService, user_repo=user_repo)
    coach_thread_repo = providers.Factory(CoachThreadRepository, session=db_session)
    coach_service = providers.Factory(CoachService, repo=coach_thread_repo)
