"""Shop recommendation button labels follow locale."""

from types import SimpleNamespace

from app.core.shop_recommendations import AFTER_COMPLETION, AFTER_EXERCISE, get_shop_button


def _pet(**kwargs):
    defaults = {
        "name": "Balu",
        "age_category": "Щенок (4–12 мес)",
        "size_category": "Средний (10–25 кг)",
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_puppy_free_button_is_localized():
    btn_ru = get_shop_button(_pet(), False, AFTER_EXERCISE, lang="ru")
    btn_en = get_shop_button(_pet(), False, AFTER_EXERCISE, lang="en")
    assert "Лакомства" in btn_ru.text
    assert "Treats" in btn_en.text
    assert "Лакомства" not in btn_en.text
    assert "pepitopet.ru/shop" in btn_en.url


def test_completion_adult_free_uses_longplay():
    adult = _pet(age_category="Взрослый (3–7 лет)", size_category="Крупный (25–45 кг)", name="Rex")
    btn = get_shop_button(adult, False, AFTER_COMPLETION, lang="en")
    assert "Long-lasting" in btn.text
    assert "tags=3" in btn.url


def test_premium_named_puppy():
    btn = get_shop_button(_pet(name="Чарли"), True, AFTER_EXERCISE, lang="ru")
    assert "Чарли" in btn.text
