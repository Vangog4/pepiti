from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class CoachMessage(BaseModel):
    role: str = Field(..., description="Message author: 'user' or 'coach'")
    content: str = Field(..., description="Message text")
    ts: int | None = Field(None, description="Unix timestamp of message")


class CoachThreadResponse(BaseModel):
    id: int = Field(..., description="Thread ID")
    title: str | None = Field(None, description="Conversation topic/title")
    status: str = Field("active", description="Thread status: active, archived")
    summary: str | None = Field(None, description="Short AI-generated discussion summary")
    message_count: int = Field(0, description="Total exchanges in this thread")
    created_at: datetime | None = Field(None, description="Thread creation time")
    updated_at: datetime | None = Field(None, description="Last message time")


class CoachThreadDetailResponse(BaseModel):
    id: int = Field(..., description="Thread ID")
    title: str | None = Field(None, description="Thread title")
    status: str = Field("active", description="active or archived")
    summary: str | None = Field(None, description="Discussion summary")
    messages: list[CoachMessage] = Field(
        default_factory=list, description="Ordered conversation messages"
    )


class SendMessageRequest(BaseModel):
    content: str = Field(
        ..., min_length=1, max_length=2000, description="Question or message to the AI cynologist"
    )


class SendMessageResponse(BaseModel):
    thread_id: int = Field(..., description="Active thread ID")
    user_message: CoachMessage = Field(..., description="Echo of user question")
    coach_message: CoachMessage = Field(..., description="AI cynologist answer")
    tokens_used: int | None = Field(None, description="Approximate token count if available")
