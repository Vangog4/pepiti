"""AI metrics + HTML guard length caps."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.infrastructure.redis.metrics import BotMetrics
from app.logic.cascade import ModelCascade
from app.services.ai_service import AiService


def _svc_with_metrics() -> tuple[AiService, MagicMock]:
    metrics = MagicMock()
    metrics.inc = AsyncMock()
    svc = AiService.__new__(AiService)
    svc.client = MagicMock()
    svc._metrics = metrics
    svc._cascade = ModelCascade(
        {
            "models": {"default": "lite", "escalate": "flash"},
            "schema_retries": 1,
            "kinds": {"training_plan": "default"},
        }
    )
    return svc, metrics


def _pet() -> MagicMock:
    pet = MagicMock()
    pet.name = "Чарли"
    pet.breed = "Бигль"
    pet.age_category = "Молодой (1–3 года)"
    pet.goal = "Не тянуть"
    pet.training_level = "3"
    pet.behavior_issues = "тянет"
    return pet


@pytest.mark.asyncio
async def test_schema_ok_increments_metrics():
    svc, metrics = _svc_with_metrics()
    good = """{
      "title": "Plan",
      "tasks": [
        {"title": "A", "description": "steps", "duration_minutes": 5, "difficulty": "easy"}
      ],
      "tip": "t"
    }"""
    m = MagicMock()
    m.text = good
    svc.client.aio.models.generate_content = AsyncMock(return_value=m)

    await svc.generate_training_plan(_pet(), lang="ru")

    keys = [c.args[0] for c in metrics.inc.await_args_list]
    assert BotMetrics.AI_CALLS in keys
    assert BotMetrics.AI_SCHEMA_OK in keys


@pytest.mark.asyncio
async def test_fallback_increments_on_total_fail():
    svc, metrics = _svc_with_metrics()
    m = MagicMock()
    m.text = "not-json"
    svc.client.aio.models.generate_content = AsyncMock(return_value=m)

    plan = await svc.generate_training_plan(_pet(), lang="ru")
    assert plan["title"] == "Базовая тренировка"

    keys = [c.args[0] for c in metrics.inc.await_args_list]
    assert BotMetrics.AI_SCHEMA_FAIL in keys
    assert BotMetrics.AI_FALLBACK in keys
    assert BotMetrics.AI_ESCALATE in keys


def test_guard_html_truncates_by_rules():
    svc = AiService.__new__(AiService)
    svc._metrics = None
    long = "x" * 2000
    out = svc._guard_html(long, kind="progress_summary")
    # rules: progress_summary max 600
    assert len(out) <= 600
    assert out.endswith("…")


def test_guard_strips_forbidden():
    svc = AiService.__new__(AiService)
    svc._metrics = None
    text = "Нормальный совет. Это ветеринарный диагноз: воспаление. Дальше ок."
    out = svc._guard_html(text)
    assert "ветеринарный диагноз" not in out.lower()
