"""Unit tests for AiService.extract_pet_profile (Stage 9: conversational onboarding)."""
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, ".")

from app.services.ai_service import AiService


def _make_service() -> AiService:
    svc = AiService.__new__(AiService)
    svc.client = MagicMock()
    return svc


def _mock_gemini(svc: AiService, response_text: str) -> None:
    result = MagicMock()
    result.text = response_text
    svc.client.aio.models.generate_content = AsyncMock(return_value=result)


@pytest.mark.asyncio
async def test_full_message_no_missing_fields():
    """Complete message → missing_fields empty, profile filled."""
    svc = _make_service()
    _mock_gemini(svc, """{
        "name": "Чарли",
        "breed": "Бигль",
        "age_category": "Молодой (1–3 года)",
        "size_category": "Средний (10–25 кг)",
        "behavior_issues": "Тянет поводок",
        "goal": "Перестать тянуть поводок",
        "missing_fields": [],
        "clarify_question": null
    }""")

    result = await svc.extract_pet_profile(language_code="ru", text="Бигль Чарли, 2 года, тянет поводок")

    assert result["name"] == "Чарли"
    assert result["breed"] == "Бигль"
    assert result["age_category"] == "Молодой (1–3 года)"
    assert result["size_category"] == "Средний (10–25 кг)"
    assert result["missing_fields"] == []
    assert result["clarify_question"] is None


@pytest.mark.asyncio
async def test_partial_message_missing_age():
    """Message without age → missing_fields contains age_category, size inferred from breed."""
    svc = _make_service()
    _mock_gemini(svc, """{
        "name": "Вейк",
        "breed": "Ксолоитцкуинтли",
        "age_category": null,
        "size_category": "Средний (10–25 кг)",
        "behavior_issues": "Суетится в машине",
        "goal": "Спокойствие в транспорте",
        "missing_fields": ["age_category"],
        "clarify_question": "Сколько лет Вейку?"
    }""")

    result = await svc.extract_pet_profile(language_code="ru", text="Ксолоитцкуинтли Вейк, суетится в машине")

    assert result["name"] == "Вейк"
    assert result["size_category"] == "Средний (10–25 кг)"
    assert result["missing_fields"] == ["age_category"]
    assert result["clarify_question"] == "Сколько лет Вейку?"


@pytest.mark.asyncio
async def test_clarification_merge_with_partial():
    """Second turn with partial data → Gemini merges, missing_fields becomes empty."""
    svc = _make_service()
    _mock_gemini(svc, """{
        "name": "Вейк",
        "breed": "Ксолоитцкуинтли",
        "age_category": "Взрослый (3–7 лет)",
        "size_category": "Средний (10–25 кг)",
        "behavior_issues": "Суетится в машине",
        "goal": "Спокойствие в транспорте",
        "missing_fields": [],
        "clarify_question": null
    }""")

    partial = {
        "name": "Вейк",
        "breed": "Ксолоитцкуинтли",
        "size_category": "Средний (10–25 кг)",
        "behavior_issues": "Суетится в машине",
        "missing_fields": ["age_category"],
    }
    result = await svc.extract_pet_profile(language_code="ru", text="3 года", partial=partial)

    assert result["age_category"] == "Взрослый (3–7 лет)"
    assert result["missing_fields"] == []
    assert result["clarify_question"] is None


@pytest.mark.asyncio
async def test_gemini_error_safe_fallback():
    """Gemini exception → safe fallback preserving partial, flags missing core fields."""
    svc = _make_service()
    svc.client.aio.models.generate_content = AsyncMock(side_effect=Exception("timeout"))

    partial = {"name": "Рекс", "breed": "Овчарка"}
    result = await svc.extract_pet_profile(language_code="en", text="hello", partial=partial)

    assert result.get("name") == "Рекс"
    assert result.get("breed") == "Овчарка"
    assert "age_category" in result["missing_fields"]
    assert "name" not in result["missing_fields"]
    assert "breed" not in result["missing_fields"]


@pytest.mark.asyncio
async def test_clarify_question_language_ru():
    """clarify_question passes language to prompt — response in user's language."""
    svc = _make_service()
    captured_prompt: list[str] = []

    async def _capture(model, contents):
        if isinstance(contents, str):
            captured_prompt.append(contents)
        result = MagicMock()
        result.text = '{"name":null,"breed":null,"age_category":null,"size_category":null,"behavior_issues":null,"goal":null,"missing_fields":["name","breed","age_category"],"clarify_question":"Как зовут вашу собаку?"}'
        return result

    svc.client.aio.models.generate_content = _capture

    await svc.extract_pet_profile(language_code="ru", text="У меня собака")

    assert captured_prompt, "prompt was not captured"
    assert "Russian" in captured_prompt[0]


@pytest.mark.asyncio
async def test_clarify_question_language_de():
    """German language_code → prompt specifies German (Deutsch)."""
    svc = _make_service()
    captured_prompt: list[str] = []

    async def _capture(model, contents):
        if isinstance(contents, str):
            captured_prompt.append(contents)
        result = MagicMock()
        result.text = '{"name":null,"breed":null,"age_category":null,"size_category":null,"behavior_issues":null,"goal":null,"missing_fields":["name"],"clarify_question":"Wie heißt dein Hund?"}'
        return result

    svc.client.aio.models.generate_content = _capture

    await svc.extract_pet_profile(language_code="de", text="Ich habe einen Hund")

    assert captured_prompt
    assert "German" in captured_prompt[0] or "Deutsch" in captured_prompt[0]
