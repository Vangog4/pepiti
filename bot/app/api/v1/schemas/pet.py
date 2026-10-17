from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class PetResponse(BaseModel):
    id: int = Field(..., description="Pet ID")
    user_id: int = Field(..., description="Owner User ID")
    name: str = Field(..., description="Pet name")
    breed: str | None = Field(None, description="Pet breed")
    sex: str | None = Field(None, description="Sex (male/female/etc)")
    age_category: str | None = Field(None, description="Age group: Puppy, Young, Adult, Senior")
    age_months: int | None = Field(None, description="Exact age in months if provided")
    size_category: str | None = Field(
        None, description="Size category: small, medium, large, giant"
    )
    weight_kg: float | None = Field(None, description="Weight in kg")
    training_level: str | None = Field(None, description="Training skill level 1-5")
    temperament: str | None = Field(None, description="Temperament description")
    behavior_issues: str | None = Field(None, description="Known behavioral challenges")
    goal: str | None = Field(None, description="Primary training goal")
    energy_level: str | None = Field(None, description="Activity/energy level")
    health_notes: str | None = Field(None, description="Health notes or dietary restrictions")
    training_days: int = Field(0, description="Completed training streak for this pet")
    created_at: datetime | None = Field(None, description="Pet profile creation time")
    updated_at: datetime | None = Field(None, description="Last update time")


class PetCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="Pet name")
    breed: str | None = Field(None, max_length=60, description="Breed")
    sex: str | None = Field(None, max_length=20, description="Sex")
    age_category: str | None = Field(None, max_length=50, description="Age category")
    age_months: int | None = Field(None, ge=1, le=360, description="Age in months")
    size_category: str | None = Field(None, max_length=30, description="Size category")
    weight_kg: float | None = Field(None, ge=0.1, le=150.0, description="Weight in kg")
    training_level: str | None = Field(None, description="Skill level (1 to 5)")
    temperament: str | None = Field(None, max_length=100, description="Temperament")
    behavior_issues: str | None = Field(None, max_length=300, description="Behavior issues")
    goal: str | None = Field(None, max_length=200, description="Main training goal")
    energy_level: str | None = Field(None, max_length=50, description="Energy level")
    health_notes: str | None = Field(None, max_length=300, description="Health notes")


class PetUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=50)
    breed: str | None = Field(None, max_length=60)
    sex: str | None = Field(None, max_length=20)
    age_category: str | None = Field(None, max_length=50)
    age_months: int | None = Field(None, ge=1, le=360)
    size_category: str | None = Field(None, max_length=30)
    weight_kg: float | None = Field(None, ge=0.1, le=150.0)
    training_level: str | None = Field(None)
    temperament: str | None = Field(None, max_length=100)
    behavior_issues: str | None = Field(None, max_length=300)
    goal: str | None = Field(None, max_length=200)
    energy_level: str | None = Field(None, max_length=50)
    health_notes: str | None = Field(None, max_length=300)
