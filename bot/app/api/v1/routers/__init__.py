from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.coach import router as coach_router
from app.api.v1.routers.pets import router as pets_router
from app.api.v1.routers.profile import router as profile_router
from app.api.v1.routers.push import router as push_router
from app.api.v1.routers.subscription import router as subscription_router
from app.api.v1.routers.sync import router as sync_router
from app.api.v1.routers.training import router as training_router

__all__ = [
    "auth_router",
    "coach_router",
    "pets_router",
    "profile_router",
    "push_router",
    "subscription_router",
    "sync_router",
    "training_router",
]
