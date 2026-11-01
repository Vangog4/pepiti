"""Pet passport + long-term memory: pure prompt block, strict fact extraction, dedup."""

from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from pydantic import ValidationError

from app.logic.schemas import FactExtraction
from app.services.pet_memory import MAX_FACTS_IN_PROMPT, merge_new_facts, pet_memory_block


def _pet(**kw):
    base = dict(
        name="Рекс",
        breed="Лабрадор",
        age_category="Молодой (1–3 года)",
        weight_kg=28.5,
        birth_date=None,
        allergies=None,
        chronic_conditions=None,
        health_notes=None,
    )
    base.update(kw)
    return SimpleNamespace(**base)


def test_block_contains_passport_and_facts():
    pet = _pet(allergies=["курица"], chronic_conditions=["дисплазия"], birth_date=date(2024, 1, 10))
    out = pet_memory_block(pet, ["боится пылесоса", "ест сухой корм"], today=date(2026, 11, 1))
    assert "Рекс" in out and "28.5" in out
    assert "курица" in out and "дисплазия" in out
    assert "2 г" in out or "2 y" in out or "26 мес" in out
    assert "боится пылесоса" in out


def test_block_limits_facts_and_handles_empty():
    facts = [f"факт {i} длинный" for i in range(MAX_FACTS_IN_PROMPT + 10)]
    out = pet_memory_block(_pet(), facts)
    assert out.count("факт ") == MAX_FACTS_IN_PROMPT
    assert pet_memory_block(_pet(weight_kg=None), []) != ""


def test_schema_is_strict():
    ok = FactExtraction(facts=[{"text": "  боится грома  "}])
    assert ok.facts[0].text == "боится грома"
    with pytest.raises(ValidationError):
        FactExtraction(facts=[{"text": "ab"}])
    with pytest.raises(ValidationError):
        FactExtraction(facts=[{"text": "x" * 400}])
    assert len(FactExtraction(facts=[{"text": f"факт номер {i}"} for i in range(5)]).facts) == 5
    with pytest.raises(ValidationError):
        FactExtraction(facts=[{"text": f"факт номер {i}"} for i in range(9)])


def test_merge_dedups_case_insensitive_and_caps():
    known = ["Боится грома"]
    new = ["боится ГРОМА ", "аллергия на курицу", "аллергия на курицу"]
    assert merge_new_facts(known, new) == ["аллергия на курицу"]


@pytest.mark.asyncio
async def test_extract_facts_returns_empty_on_ai_failure():
    from app.services.ai_service import AiService

    svc = AiService.__new__(AiService)
    svc._generate_structured = AsyncMock(return_value=None)
    assert await svc.extract_facts("вопрос", "ответ", []) == []
    svc._generate_structured = AsyncMock(
        return_value=FactExtraction(facts=[{"text": "боится грома"}])
    )
    assert await svc.extract_facts("вопрос", "ответ", []) == ["боится грома"]
