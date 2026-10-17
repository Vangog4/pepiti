from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.v1.dependencies import get_current_user
from app.api.v1.schemas.subscription import PlanPricing, SubscriptionStatusResponse
from app.infrastructure.db.models.user import UserModel
from app.logic.rules import rule

router = APIRouter(prefix="/subscription", tags=["Subscription"])

_PLANS = [
    PlanPricing(
        plan_id="premium_1m",
        title="1 месяц",
        duration_days=int(rule("premium.duration_days", 30)),
        price_stars=int(rule("premium.stars_1m", 299)),
        price_rub=float(rule("premium.rub_1m", 590)),
        price_usd=5.99,
    ),
    PlanPricing(
        plan_id="premium_3m",
        title="3 месяца (выгодно)",
        duration_days=90,
        price_stars=749,
        price_rub=1490.0,
        price_usd=14.99,
    ),
    PlanPricing(
        plan_id="premium_1y",
        title="1 год (максимум)",
        duration_days=365,
        price_stars=2490,
        price_rub=4990.0,
        price_usd=49.99,
    ),
]


@router.get("/status", response_model=SubscriptionStatusResponse, summary="Get subscription status")
async def get_subscription_status(
    current_user: Annotated[UserModel, Depends(get_current_user)],
) -> SubscriptionStatusResponse:
    now = datetime.now(tz=UTC)
    is_active = False
    days_left = 0
    expires_at = current_user.subscription_expires_at

    if expires_at:
        # Normalize timezone if naive
        exp_aware = expires_at.replace(tzinfo=UTC) if expires_at.tzinfo is None else expires_at
        if exp_aware > now:
            is_active = True
            days_left = max(0, (exp_aware - now).days)
    elif bool(current_user.is_premium):
        is_active = True
        days_left = 9999

    return SubscriptionStatusResponse(
        is_premium=is_active,
        expires_at=expires_at,
        days_left=days_left,
        tier="premium" if is_active else "free",
        plans=_PLANS,
    )


@router.get("/plans", response_model=list[PlanPricing], summary="List available subscription plans")
async def get_subscription_plans() -> list[PlanPricing]:
    return _PLANS
