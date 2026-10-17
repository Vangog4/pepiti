from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class TaskResponse(BaseModel):
    id: int = Field(..., description="Task unique ID")
    plan_id: int = Field(..., description="Parent plan ID")
    day_of_week: int | None = Field(None, description="ISO weekday (1=Mon ... 7=Sun) or 0")
    title: str = Field(..., description="Exercise / task title")
    description: str | None = Field(None, description="Detailed instructions and steps")
    duration_minutes: int | None = Field(None, description="Recommended duration in minutes")
    difficulty: str | None = Field(None, description="Difficulty level, e.g. easy, medium, hard")
    is_completed: bool = Field(False, description="Whether the task has been marked completed")
    completed_at: datetime | None = Field(None, description="Completion timestamp")


class PlanResponse(BaseModel):
    id: int = Field(..., description="Plan ID")
    pet_id: int = Field(..., description="Associated Pet ID")
    title: str = Field(..., description="Plan title")
    goal: str | None = Field(None, description="Plan objective")
    week_number: int | None = Field(None, description="Calendar week number if weekly plan")
    is_active: bool = Field(True, description="Whether this is the current active training plan")
    tasks: list[TaskResponse] = Field(default_factory=list, description="All tasks in this plan")
    created_at: datetime | None = Field(None, description="Plan generation date")


class TaskToggleResponse(BaseModel):
    task_id: int = Field(..., description="Toggled task ID")
    is_completed: bool = Field(..., description="New completion status")
    completed_at: datetime | None = Field(None, description="Completion timestamp")
    day_done: bool = Field(..., description="Whether all exercises for today are completed")
    streak_days: int = Field(..., description="Current total training streak in days")
