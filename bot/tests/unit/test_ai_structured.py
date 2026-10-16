"""Structured generate: schema validate + cascade retry (mocked Gemini)."""

from __future__ import annotations

import sys
from unittest.mock import AsyncMock, MagicMock

import pytest

sys.path.insert(0, ".")

from app.services.ai_service import AiService
from app.logic.cascade import ModelCascade


def _make_service(cascade: ModelCascade | None = None) -> AiService:
    svc = AiService.__new__(AiService)
    svc.client = MagicMock()
    svc._cascade = cascade or ModelCascade(
        {
            "models": {
                "default": "lite",
                "escalate": "flash",
                "media": "flash",
                "premium": "flash",
            },
            "schema_retries": 1,
            "kinds": {"training_plan": "default", "extract_profile": "default"},
        }
    )
    return svc


def _mock_responses(svc: AiService, texts: list[str]) -> None:
    results = []
    for t in texts:
        m = MagicMock()
        m.text = t
        results.append(m)
    svc.client.aio.models.generate_content = AsyncMock(side_effect=results)


def _pet() -> MagicMock:
    pet = MagicMock()
    pet.name = "Чарли"
    pet.breed = "Бигль"
    pet.age_category = "Молодой (1–3 года)"
    pet.goal = "Не тянуть"
    pet.training_level = "3"
    pet.behavior_issues = "тянет поводок"
    return pet


@pytest.mark.asyncio
async def test_training_plan_valid_on_first_try():
    svc = _make_service()
    good = """{
      "title": "Поводок",
      "goal": "Не тянуть",
      "tasks": [
        {"title": "Стоп", "description": "1. Стоп\\n2. Ждать", "duration_minutes": 5, "difficulty": "easy"},
        {"title": "Имя", "description": "1. Позвать", "duration_minutes": 5, "difficulty": "easy"}
      ],
      "tip": "Коротко"
    }"""
    _mock_responses(svc, [good])
    plan = await svc.generate_training_plan(_pet(), lang="ru")
    assert plan["title"] == "Поводок"
    assert len(plan["tasks"]) == 2
    assert svc.client.aio.models.generate_content.await_count == 1


@pytest.mark.asyncio
async def test_training_plan_escalates_after_bad_json():
    svc = _make_service()
    bad = "not json at all"
    good = """{
      "title": "Retry plan",
      "tasks": [
        {"title": "A", "description": "steps here", "duration_minutes": 5, "difficulty": "medium"}
      ],
      "tip": "ok"
    }"""
    _mock_responses(svc, [bad, good])
    plan = await svc.generate_training_plan(_pet(), lang="ru")
    assert plan["title"] == "Retry plan"
    assert svc.client.aio.models.generate_content.await_count == 2
    # second call used escalate model
    second_kwargs = svc.client.aio.models.generate_content.await_args_list[1].kwargs
    assert second_kwargs["model"] == "flash"


@pytest.mark.asyncio
async def test_training_plan_fallback_when_all_fail():
    svc = _make_service()
    _mock_responses(svc, ["{}", "still bad"])
    plan = await svc.generate_training_plan(_pet(), lang="ru")
    assert plan["title"] == "Базовая тренировка"
    assert "tasks" in plan


@pytest.mark.asyncio
async def test_extract_profile_schema():
    svc = _make_service()
    _mock_responses(
        svc,
        [
            """{
        "name": "Чарли",
        "breed": "Бигль",
        "age_category": "Молодой (1–3 года)",
        "size_category": "Средний (10–25 кг)",
        "behavior_issues": "Тянет",
        "goal": "Не тянуть",
        "missing_fields": [],
        "clarify_question": null
    }"""
        ],
    )
    result = await svc.extract_pet_profile(language_code="ru", text="Бигль Чарли 2 года")
    assert result["name"] == "Чарли"
    assert result["missing_fields"] == []
