"""Unit tests for pdf_service.generate_training_pdf."""

import pytest
from app.services.pdf_service import generate_training_pdf


@pytest.fixture
def sample_tasks():
    return [
        {
            "day_of_week": 1,
            "title": "Сидеть",
            "description": "Команда 'сидеть' с подкреплением.",
            "duration_minutes": 10,
            "difficulty": "easy",
            "is_completed": True,
        },
        {
            "day_of_week": 1,
            "title": "Лежать",
            "description": None,
            "duration_minutes": None,
            "difficulty": None,
            "is_completed": False,
        },
        {
            "day_of_week": 3,
            "title": "Апорт",
            "description": "Бросить мяч, дождаться возврата.",
            "duration_minutes": 15,
            "difficulty": "medium",
            "is_completed": False,
        },
    ]


def test_returns_bytes(sample_tasks):
    result = generate_training_pdf("Бобик", "Базовый курс", "Освоить команды", sample_tasks)
    assert isinstance(result, bytes)
    assert len(result) > 0


def test_is_valid_pdf(sample_tasks):
    result = generate_training_pdf("Бобик", "Базовый курс", "Освоить команды", sample_tasks)
    assert result[:4] == b"%PDF"


def test_empty_tasks():
    result = generate_training_pdf("Рекс", "Пустой план", "", [])
    assert isinstance(result, bytes)
    assert result[:4] == b"%PDF"


def test_unicode_pet_name(sample_tasks):
    result = generate_training_pdf("Рыжик 🐾", "План", "Цель", sample_tasks)
    assert result[:4] == b"%PDF"


def test_missing_optional_fields():
    tasks = [
        {
            "day_of_week": None,
            "title": "Стоять",
            "description": None,
            "duration_minutes": None,
            "difficulty": None,
            "is_completed": False,
        }
    ]
    result = generate_training_pdf("Шарик", "Тест", "", tasks)
    assert result[:4] == b"%PDF"


@pytest.mark.parametrize("lang", ["en", "de", "fr", "es", "pt", "ru"])
def test_multilingual_pdf(sample_tasks, lang):
    result = generate_training_pdf("Buddy", "Plan", "Goal", sample_tasks, lang=lang)
    assert isinstance(result, bytes)
    assert result[:4] == b"%PDF"
    assert len(result) > 1000
