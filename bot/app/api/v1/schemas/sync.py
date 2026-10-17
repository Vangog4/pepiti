from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.api.v1.schemas.coach import CoachThreadResponse
from app.api.v1.schemas.pet import PetResponse, PetUpdateRequest
from app.api.v1.schemas.profile import ProfileResponse, ProfileUpdateRequest
from app.api.v1.schemas.subscription import SubscriptionStatusResponse
from app.api.v1.schemas.training import PlanResponse, TaskResponse


class SyncPullResponse(BaseModel):
    server_time: datetime = Field(..., description="Server timestamp at generation (UTC)")
    profile: ProfileResponse = Field(..., description="Current user profile and preferences")
    pets: list[PetResponse] = Field(
        default_factory=list, description="All registered pets of this user"
    )
    active_pet_id: int | None = Field(None, description="Primary/active pet ID")
    active_plan: PlanResponse | None = Field(None, description="Active training plan with tasks")
    today_tasks: list[TaskResponse] = Field(
        default_factory=list, description="Tasks scheduled for today"
    )
    coach_threads: list[CoachThreadResponse] = Field(
        default_factory=list, description="Recent active coaching threads"
    )
    subscription: SubscriptionStatusResponse = Field(..., description="Current subscription status")


class OfflineTaskChange(BaseModel):
    task_id: int = Field(..., description="Task ID toggled offline")
    is_completed: bool = Field(..., description="Completion state")
    completed_at: datetime | None = Field(
        None, description="Client timestamp when task was toggled"
    )


class SyncPushRequest(BaseModel):
    client_timestamp: datetime | None = Field(None, description="Client sync push timestamp")
    task_changes: list[OfflineTaskChange] = Field(
        default_factory=list, description="Offline task completions to apply"
    )
    profile_update: ProfileUpdateRequest | None = Field(
        None, description="Offline profile changes to apply"
    )
    pet_update: PetUpdateRequest | None = Field(None, description="Offline pet changes to apply")
    pet_id: int | None = Field(None, description="Target pet ID for pet_update")


class SyncPushResponse(BaseModel):
    synced_at: datetime = Field(..., description="Server timestamp of sync completion")
    tasks_applied: int = Field(0, description="Count of task changes processed")
    profile_updated: bool = Field(False, description="Whether profile was updated")
    pet_updated: bool = Field(False, description="Whether pet was updated")
    current_state: SyncPullResponse = Field(
        ..., description="Fresh full snapshot after applying push changes"
    )
