from app.api.v1.schemas.auth import (
    AccountLinkRequest,
    AccountLinkResponse,
    EmailCodeRequest,
    EmailVerifyRequest,
    GuestAuthRequest,
    TelegramCheckResponse,
    TelegramCodeRequest,
    TelegramSessionResponse,
    TokenResponse,
    VkAuthRequest,
)
from app.api.v1.schemas.coach import (
    CoachMessage,
    CoachThreadDetailResponse,
    CoachThreadResponse,
    SendMessageRequest,
    SendMessageResponse,
)
from app.api.v1.schemas.pet import PetCreateRequest, PetResponse, PetUpdateRequest
from app.api.v1.schemas.profile import ProfileResponse, ProfileUpdateRequest
from app.api.v1.schemas.push import PushRegisterRequest, PushRegisterResponse
from app.api.v1.schemas.subscription import PlanPricing, SubscriptionStatusResponse
from app.api.v1.schemas.sync import (
    OfflineTaskChange,
    SyncPullResponse,
    SyncPushRequest,
    SyncPushResponse,
)
from app.api.v1.schemas.training import PlanResponse, TaskResponse, TaskToggleResponse

__all__ = [
    "AccountLinkRequest",
    "AccountLinkResponse",
    "CoachMessage",
    "CoachThreadDetailResponse",
    "CoachThreadResponse",
    "EmailCodeRequest",
    "EmailVerifyRequest",
    "GuestAuthRequest",
    "OfflineTaskChange",
    "PetCreateRequest",
    "PetResponse",
    "PetUpdateRequest",
    "PlanPricing",
    "PlanResponse",
    "ProfileResponse",
    "ProfileUpdateRequest",
    "PushRegisterRequest",
    "PushRegisterResponse",
    "SendMessageRequest",
    "SendMessageResponse",
    "SubscriptionStatusResponse",
    "SyncPullResponse",
    "SyncPushRequest",
    "SyncPushResponse",
    "TaskResponse",
    "TaskToggleResponse",
    "TelegramCheckResponse",
    "TelegramCodeRequest",
    "TelegramSessionResponse",
    "TokenResponse",
    "VkAuthRequest",
]
