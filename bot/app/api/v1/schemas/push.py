from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class PushRegisterRequest(BaseModel):
    push_token: str = Field(..., description="Device push notification token (APNs or FCM)")
    platform: Literal["ios", "android"] = Field(..., description="Operating system platform")
    device_id: str | None = Field(None, description="Client device UUID if available")


class PushRegisterResponse(BaseModel):
    success: bool = Field(True, description="True if push token was stored")
    platform: str = Field(..., description="Registered platform")
