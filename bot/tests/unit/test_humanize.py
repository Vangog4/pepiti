import re

import pytest

from app.i18n.core import _load_locale
from app.logic.humanize import banned_ru, find_banned, strip_cliches
from app.logic.rules import rule


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("Отличный вопрос! Тянет — значит, мало занятий.", "Тянет — значит, мало занятий."),
        ("Тянет поводок. Надеюсь, это поможет!", "Тянет поводок."),
        ("<b>Хороший вопрос!</b> Начни с коротких шагов.", "Начни с коротких шагов."),
        ("Great question! Start with short sessions.", "Start with short sessions."),
        (
            "Тянет поводок. Остановись и жди.",
            "Тянет поводок. Остановись и жди.",
        ),  # nothing to strip
        (
            "Важно отметить, что собака устаёт от повторов и теряет интерес к занятию через десять минут",
            "Важно отметить, что собака устаёт от повторов и теряет интерес к занятию через десять минут",
        ),
    ],
)
def test_strip_cliches(raw, expected):
    assert strip_cliches(raw) == expected


def test_never_empties_a_pure_cliche_single_sentence_answer_to_nothing_useful():
    assert strip_cliches("") == ""
    assert strip_cliches("Остановись и жди.") == "Остановись и жди."


def test_find_banned_flags_bureaucratic_stems():
    assert find_banned("Необходимо осуществить действие") != []
    assert find_banned("Стой и жди, пока собака сядет.") == []


def test_russian_locale_is_free_of_bureaucratic_language():
    bad = {
        k: find_banned(v)
        for k, v in _load_locale("ru").items()
        if isinstance(v, str) and find_banned(v)
    }
    assert bad == {}, bad


def test_russian_locale_addresses_the_owner_as_ty():
    allowed = set(rule("copy.formal_you_allowed_keys", []))
    vy = re.compile(r"\b(вы|вас|вам|вами|ваш\w*)\b", re.IGNORECASE)
    bad = [
        k
        for k, v in _load_locale("ru").items()
        if isinstance(v, str) and k not in allowed and vy.search(v)
    ]
    assert bad == [], bad


def test_word_lists_are_configured():
    assert len(banned_ru()) >= 10 and len(rule("copy.ai_cliches", [])) >= 8


def test_ai_guard_strips_filler_and_prompt_asks_for_ty():
    from app.services.ai_service import AiService, _lang_instruction

    out = AiService.__new__(AiService)._guard_html("Отличный вопрос! Стой и жди.")
    assert "Отличный" not in out and "Стой и жди." in out
    assert "«ты»" in _lang_instruction("ru") and "«вы»" in _lang_instruction("ru")
    assert "du" in _lang_instruction("de") and "tu" in _lang_instruction("fr")
    assert "Respond strictly in" in _lang_instruction("en")
