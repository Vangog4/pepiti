from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class GuestAuthRequest(BaseModel):
    device_id: str = Field(..., description="Unique device identifier (UUID or Android/IDFV)")
    device_name: str | None = Field(None, description="Device model name, e.g. iPhone 15, Pixel 8")
    platform: Literal["ios", "android", "web", "other"] = Field(
        "other", description="Client platform"
    )


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT Bearer access token")
    token_type: str = Field("bearer", description="Token type")
    user_id: int = Field(..., description="User ID in Pepito system")
    is_new: bool = Field(False, description="Whether this is a newly created account")
    expires_in_days: int = Field(30, description="Token validity in days")


class TelegramSessionResponse(BaseModel):
    session_token: str = Field(..., description="Unique one-time auth session token")
    bot_username: str = Field(..., description="Telegram bot username")
    deep_link: str = Field(..., description="Direct link to open Telegram bot for authorization")
    expires_in_sec: int = Field(600, description="Session TTL in seconds")


class TelegramCheckResponse(BaseModel):
    status: Literal["pending", "authenticated", "expired"] = Field(..., description="Session state")
    token_data: TokenResponse | None = Field(
        None, description="Auth token if status is authenticated"
    )


class TelegramCodeRequest(BaseModel):
    code: str = Field(
        ...,
        min_length=4,
        max_length=10,
        description="6-digit code generated in Telegram bot via /connect",
    )


class VkAuthRequest(BaseModel):
    vk_access_token: str = Field(..., description="VK ID access token")
    vk_user_id: int = Field(..., description="VK User ID")
    first_name: str | None = Field(None, description="User first name from VK")


class EmailCodeRequest(BaseModel):
    email: str = Field(..., description="User email address")


class EmailVerifyRequest(BaseModel):
    email: str = Field(..., description="User email address")
    code: str = Field(
        ..., min_length=4, max_length=10, description="Verification code sent by email"
    )


class AccountLinkRequest(BaseModel):
    provider: Literal["telegram_code", "telegram_session", "vk", "email"] = Field(
        ..., description="Target auth provider to link with"
    )
    credential: str = Field(..., description="Linking code, session token, or VK/Email credential")
    device_id: str | None = Field(
        None, description="Optional device ID to update Redis device mapping"
    )


class AccountLinkResponse(BaseModel):
    success: bool = Field(..., description="Whether linking was successful")
    merged_user_id: int = Field(..., description="Active user ID after merge")
    message: str = Field(..., description="Human-readable result status")
    token_data: TokenResponse | None = Field(
        None, description="New JWT access token for the merged account"
    )
