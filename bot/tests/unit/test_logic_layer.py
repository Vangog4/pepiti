"""Unit tests for app.logic — rules, schemas, cascade (no Gemini/Redis)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.logic.cascade import ModelCascade
from app.logic.rules import contains_forbidden, get_rules, reload_rules, rule
from app.logic.schemas import (
    PetProfileSchema,
    TrainingIntentSchema,
    TrainingPlanSchema,
    WeekPlanSchema,
)
from app.services.coach_service import CoachService
from app.services.referral_service import REFERRAL_BONUS_DAYS, REFERRAL_MILESTONES
from app.services.subscription_service import PREMIUM_1M_STARS, PREMIUM_DURATION_DAYS
from app.infrastructure.redis.ai_rate_limit import FREE_DAILY_LIMIT


# ── rules.json ───────────────────────────────────────────────────────────────


def test_rules_json_loads():
    rules = reload_rules()
    assert "ai" in rules
    assert "premium" in rules
    assert "referral" in rules
    assert rules["ai"]["free_daily_limit"] == 5


def test_rule_dotted_path():
    reload_rules()
    assert rule("premium.stars_1m") == 299
    assert rule("missing.path", default=42) == 42


def test_constants_match_rules():
    reload_rules()
    assert FREE_DAILY_LIMIT == rule("ai.free_daily_limit")
    assert PREMIUM_1M_STARS == rule("premium.stars_1m")
    assert PREMIUM_DURATION_DAYS == rule("premium.duration_days")
    assert REFERRAL_BONUS_DAYS == rule("referral.bonus_days")
    assert len(REFERRAL_MILESTONES) == 4
    assert REFERRAL_MILESTONES[0]["count"] == 3
    assert CoachService.CONTEXT_MESSAGES_FREE == rule("coach.context_messages_free")


def test_contains_forbidden():
    reload_rules()
    assert contains_forbidden("Это ветеринарный диагноз: артрит") is not None
    assert contains_forbidden("Учите команду сидеть") is None


# ── cascade ──────────────────────────────────────────────────────────────────


def test_cascade_default_and_ladder():
    c = ModelCascade(
        {
            "models": {
                "default": "gemini-2.5-flash-lite",
                "escalate": "gemini-2.5-flash",
                "media": "gemini-2.5-flash",
                "premium": "gemini-2.5-flash",
            },
            "schema_retries": 1,
            "kinds": {
                "training_plan": "default",
                "media_analysis": "media",
                "premium_deep": "premium",
            },
        }
    )
    assert c.model_for("training_plan") == "gemini-2.5-flash-lite"
    assert c.model_for("media_analysis") == "gemini-2.5-flash"
    assert c.model_for("premium_deep") == "gemini-2.5-flash"
    ladder = c.ladder_for("training_plan")
    assert ladder[0] == "gemini-2.5-flash-lite"
    assert "gemini-2.5-flash" in ladder
    assert len(ladder) == len(set(ladder))


def test_cascade_no_duplicate_when_same_model():
    c = ModelCascade(
        {
            "models": {"default": "m1", "escalate": "m1"},
            "schema_retries": 1,
            "kinds": {"x": "default"},
        }
    )
    assert c.ladder_for("x") == ["m1"]


# ── schemas ──────────────────────────────────────────────────────────────────


def test_training_plan_schema_ok():
    data = {
        "title": "День 1",
        "goal": "Контакт",
        "tasks": [
            {
                "title": "Сидеть",
                "description": "1. Встать\n2. Ждать",
                "duration_minutes": 5,
                "difficulty": "easy",
            }
        ],
        "tip": "Коротко",
    }
    plan = TrainingPlanSchema.model_validate(data)
    assert plan.tasks[0].difficulty == "easy"


def test_training_plan_normalizes_difficulty():
    plan = TrainingPlanSchema.model_validate(
        {
            "title": "T",
            "tasks": [
                {
                    "title": "A",
                    "description": "steps",
                    "duration_minutes": 5,
                    "difficulty": "лёгкий",
                }
            ],
        }
    )
    assert plan.tasks[0].difficulty == "easy"


def test_training_plan_rejects_empty_tasks():
    with pytest.raises(ValidationError):
        TrainingPlanSchema.model_validate({"title": "T", "tasks": []})


def test_week_plan_requires_seven_days():
    day = {
        "day": 1,
        "tasks": [{"title": "A", "description": "d", "duration_minutes": 5, "difficulty": "easy"}],
    }
    with pytest.raises(ValidationError):
        WeekPlanSchema.model_validate({"title": "W", "days": [day] * 3})

    days = []
    for i in range(1, 8):
        days.append(
            {
                "day": i,
                "tasks": [
                    {
                        "title": "A",
                        "description": "d",
                        "duration_minutes": 5,
                        "difficulty": "easy",
                    }
                ],
            }
        )
    plan = WeekPlanSchema.model_validate({"title": "W", "days": days})
    assert len(plan.days) == 7


def test_pet_profile_schema():
    p = PetProfileSchema.model_validate(
        {
            "name": "Чарли",
            "breed": "Бигль",
            "age_category": "Молодой (1–3 года)",
            "size_category": "Средний (10–25 кг)",
            "missing_fields": [],
            "clarify_question": None,
        }
    )
    assert p.name == "Чарли"
    assert p.missing_fields == []


def test_intent_schema_normalizes_action():
    i = TrainingIntentSchema.model_validate(
        {"action": "MARK_DONE", "task_hint": "сидеть", "message": "Молодец!"}
    )
    assert i.action == "mark_done"
    j = TrainingIntentSchema.model_validate({"action": "ask", "message": "Как?"})
    assert j.action == "none"


def test_rules_json_is_valid_json_file():
    path = Path(__file__).resolve().parents[2] / "app" / "logic" / "rules.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["ai"]["models"]["default"]
