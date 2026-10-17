from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ProfileResponse(BaseModel):
    id: int = Field(..., description="User ID")
    telegram_id: int | None = Field(None, description="Telegram User ID if linked")
    first_name: str | None = Field(None, description="First name")
    last_name: str | None = Field(None, description="Last name")
    username: str | None = Field(None, description="Telegram username or handle")
    language_code: str = Field("ru", description="Selected language locale")
    timezone: str = Field("UTC", description="User timezone (e.g. Europe/Moscow, UTC+3)")
    reminder_time: str | None = Field(None, description="Daily reminder time (HH:MM) or 'off'")
    is_premium: bool = Field(False, description="Whether user has active premium subscription")
    subscription_expires_at: datetime | None = Field(
        None, description="Subscription expiration date"
    )
    training_days: int = Field(0, description="Total days streak of completed trainings")
    created_at: datetime | None = Field(None, description="Account registration date")


class ProfileUpdateRequest(BaseModel):
    first_name: str | None = Field(None, max_length=50, description="Updated first name")
    language_code: str | None = Field(None, description="Locale: ru, en, de, fr, es, pt")
    timezone: str | None = Field(None, description="Timezone (e.g. UTC, UTC+3, Europe/Moscow)")
    reminder_time: str | None = Field(None, description="Daily reminder time: HH:MM or 'off'")
