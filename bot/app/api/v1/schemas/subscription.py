from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class PlanPricing(BaseModel):
    plan_id: str = Field(..., description="Internal plan identifier, e.g. '1_month', '3_months'")
    title: str = Field(..., description="Localized title")
    duration_days: int = Field(..., description="Duration in days")
    price_stars: int | None = Field(None, description="Price in Telegram Stars")
    price_rub: float | None = Field(None, description="Price in RUB (Tinkoff / Russian cards)")
    price_usd: float | None = Field(None, description="Price in USD (Apple In-App / Google Play)")


class SubscriptionStatusResponse(BaseModel):
    is_premium: bool = Field(..., description="True if premium subscription is currently active")
    expires_at: datetime | None = Field(None, description="Expiration date and time in UTC")
    days_left: int = Field(0, description="Remaining days of subscription")
    tier: str = Field("free", description="'free' or 'premium'")
    plans: list[PlanPricing] = Field(default_factory=list, description="Available purchase options")
