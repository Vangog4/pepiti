"""Pydantic contracts for structured AI outputs.

Validate → retry/escalate → fallback. LLM must not invent shapes.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

AGE_CATEGORIES = (
    "Щенок (до 4 мес)",
    "Щенок (4–12 мес)",
    "Молодой (1–3 года)",
    "Взрослый (3–7 лет)",
    "Пожилой (7+ лет)",
)

SIZE_CATEGORIES = (
    "Маленький (до 10 кг)",
    "Средний (10–25 кг)",
    "Крупный (25–45 кг)",
    "Гигант (45+ кг)",
)

Difficulty = Literal["easy", "medium", "hard"]
IntentAction = Literal["mark_done", "none"]


class TaskSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1, max_length=2000)
    duration_minutes: int = Field(default=5, ge=1, le=60)
    difficulty: Difficulty = "easy"

    @field_validator("difficulty", mode="before")
    @classmethod
    def normalize_difficulty(cls, v: Any) -> str:
        if v is None:
            return "easy"
        s = str(v).strip().lower()
        if s in ("easy", "medium", "hard"):
            return s
        # common LLM variants
        if s in ("лёгкий", "легкий", "просто", "simple"):
            return "easy"
        if s in ("средний", "норм", "normal"):
            return "medium"
        if s in ("сложный", "трудный", "hardcore"):
            return "hard"
        return "easy"

    @field_validator("title", "description", mode="before")
    @classmethod
    def strip_str(cls, v: Any) -> str:
        return str(v or "").strip()


class TrainingPlanSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: str = Field(min_length=1, max_length=80)
    goal: str | None = None
    tasks: list[TaskSchema] = Field(min_length=1, max_length=5)
    tip: str | None = None

    @field_validator("title", mode="before")
    @classmethod
    def strip_title(cls, v: Any) -> str:
        return str(v or "").strip()[:80]


class DayPlanSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    day: int = Field(ge=1, le=14)
    tasks: list[TaskSchema] = Field(min_length=1, max_length=5)


class WeekPlanSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: str = Field(min_length=1, max_length=80)
    goal: str | None = None
    days: list[DayPlanSchema] = Field(min_length=7, max_length=7)

    @field_validator("days")
    @classmethod
    def exactly_seven_days(cls, days: list[DayPlanSchema]) -> list[DayPlanSchema]:
        if len(days) != 7:
            raise ValueError("week plan must have exactly 7 days")
        return days


class PetProfileSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str | None = None
    breed: str | None = None
    age_category: str | None = None
    size_category: str | None = None
    behavior_issues: str | None = None
    goal: str | None = None
    missing_fields: list[str] = Field(default_factory=list)
    clarify_question: str | None = None

    @field_validator("missing_fields", mode="before")
    @classmethod
    def ensure_list(cls, v: Any) -> list[str]:
        if v is None:
            return []
        if isinstance(v, list):
            return [str(x) for x in v]
        return []

    @field_validator("age_category", mode="before")
    @classmethod
    def normalize_age(cls, v: Any) -> str | None:
        if v is None or v == "":
            return None
        s = str(v).strip()
        if s in AGE_CATEGORIES:
            return s
        # soft match
        low = s.lower()
        for cat in AGE_CATEGORIES:
            if cat.lower() in low or low in cat.lower():
                return cat
        return s  # keep model value; UI may still use it

    @field_validator("size_category", mode="before")
    @classmethod
    def normalize_size(cls, v: Any) -> str | None:
        if v is None or v == "":
            return None
        s = str(v).strip()
        if s in SIZE_CATEGORIES:
            return s
        low = s.lower()
        for cat in SIZE_CATEGORIES:
            if cat.lower() in low or low in cat.lower():
                return cat
        return s


class TrainingIntentSchema(BaseModel):
    model_config = ConfigDict(extra="ignore")

    action: IntentAction = "none"
    task_hint: str | None = None
    message: str = Field(min_length=1, max_length=2000)

    @field_validator("action", mode="before")
    @classmethod
    def normalize_action(cls, v: Any) -> str:
        s = str(v or "none").strip().lower()
        return "mark_done" if s == "mark_done" else "none"

    @field_validator("message", mode="before")
    @classmethod
    def strip_message(cls, v: Any) -> str:
        return str(v or "").strip()[:2000]
