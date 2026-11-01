"""4-tap onboarding: name -> age -> breed (button/photo/typed) -> goal."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import ValidationError

from app.bot.handlers import onboarding as ob
from app.bot.keyboards.onboarding import AGES, BREEDS, GOALS, age_kb, breed_kb, goal_kb
from app.bot.states.onboarding import OnboardingStates
from app.logic.schemas import BreedGuess
from app.services.ai_service import AiService


def _state(data=None):
    st = MagicMock()
    st._d = dict(data or {})
    st.update_data = AsyncMock(side_effect=lambda **kw: st._d.update(kw))
    st.get_data = AsyncMock(side_effect=lambda: dict(st._d))
    st.set_state = AsyncMock()
    return st


def _usr():
    return MagicMock(
        get_or_create_telegram_user=AsyncMock(
            return_value=SimpleNamespace(language_code="ru", id=1)
        )
    )


def _cb(data):
    cb = MagicMock(data=data)
    cb.answer = AsyncMock()
    cb.from_user.id = 5
    cb.message.edit_text = AsyncMock()
    cb.message.answer = AsyncMock()
    return cb


@pytest.mark.asyncio
async def test_name_then_age_then_breed_then_goal():
    st = _state()
    msg = MagicMock(text="  Рекс  ")
    msg.from_user.id = 5
    msg.answer = AsyncMock()
    await ob.step_name.__wrapped__(msg, st, _usr())
    assert st._d["name"] == "Рекс"
    st.set_state.assert_awaited_with(OnboardingStates.age)

    await ob.step_age.__wrapped__(_cb("ob_age:3"), st, _usr())
    assert st._d["age_category"] == AGES["3"]
    st.set_state.assert_awaited_with(OnboardingStates.breed)

    await ob.step_breed.__wrapped__(_cb("ob_breed:0"), st, _usr())
    assert st._d["breed"] == BREEDS[0][1]
    st.set_state.assert_awaited_with(OnboardingStates.goal)

    cb = _cb("ob_goal:2")
    fin = AsyncMock()
    with patch.object(ob, "_finish_onboarding", fin):
        await ob.step_goal.__wrapped__(cb, st, _usr(), MagicMock(), MagicMock(), MagicMock())
    profile = fin.await_args.args[3]
    assert profile == {
        "name": "Рекс",
        "age_category": AGES["3"],
        "breed": BREEDS[0][1],
        "goal": GOALS["2"],
    }


@pytest.mark.asyncio
async def test_slash_command_is_not_a_name():
    st = _state()
    msg = MagicMock(text="/menu")
    msg.from_user.id = 5
    msg.answer = AsyncMock()
    await ob.step_name.__wrapped__(msg, st, _usr())
    assert "name" not in st._d


@pytest.mark.asyncio
async def test_other_breed_switches_to_text_step():
    st = _state()
    await ob.step_breed.__wrapped__(_cb("ob_breed:other"), st, _usr())
    st.set_state.assert_awaited_with(OnboardingStates.breed_text)


@pytest.mark.asyncio
async def test_photo_guess_then_confirm():
    st = _state()
    msg = MagicMock()
    msg.from_user.id = 5
    msg.photo = [object()]
    msg.answer = AsyncMock()
    msg.bot.download = AsyncMock()
    ai = MagicMock(
        guess_breed=AsyncMock(return_value=BreedGuess(is_dog=True, breed="Корги", confidence=0.9))
    )
    await ob.step_breed_photo.__wrapped__(msg, st, _usr(), ai)
    assert st._d["guessed_breed"] == "Корги"
    await ob.step_breed.__wrapped__(_cb("ob_breed:yes"), st, _usr())
    assert st._d["breed"] == "Корги"


@pytest.mark.asyncio
async def test_photo_not_a_dog_asks_for_text():
    st = _state()
    msg = MagicMock()
    msg.from_user.id = 5
    msg.photo = [object()]
    msg.answer = AsyncMock()
    msg.bot.download = AsyncMock()
    ai = MagicMock(guess_breed=AsyncMock(return_value=None))
    await ob.step_breed_photo.__wrapped__(msg, st, _usr(), ai)
    assert "guessed_breed" not in st._d
    msg.answer.assert_awaited()


def test_breedguess_is_strict():
    with pytest.raises(ValidationError):
        BreedGuess(is_dog=True, breed="Лабрадор", confidence=1.5)
    with pytest.raises(ValidationError):
        BreedGuess(is_dog=True, breed="", confidence=0.5)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "is_dog,conf,ok", [(True, 0.9, True), (True, 0.3, False), (False, 0.9, False)]
)
async def test_guess_breed_threshold(is_dog, conf, ok):
    svc = AiService.__new__(AiService)
    svc._generate_structured = AsyncMock(
        return_value=BreedGuess(is_dog=is_dog, breed="Корги", confidence=conf)
    )
    assert (await svc.guess_breed(b"x") is not None) is ok


def test_keyboards_fit_limits_in_all_locales():
    for lg in ("ru", "en", "de", "es", "fr", "pt"):
        for kb in (age_kb(lg), breed_kb(lg), goal_kb(lg)):
            for row in kb.inline_keyboard:
                for b in row:
                    assert len(b.text) <= 14, (lg, b.text)
                    assert "{" not in b.text and "onboarding." not in b.text


@pytest.mark.asyncio
async def test_legacy_clarifying_state_restarts_flow():
    st = _state()
    st.clear = AsyncMock()
    msg = MagicMock()
    msg.from_user.id = 5
    msg.answer = AsyncMock()
    await ob.legacy_clarifying_restart.__wrapped__(msg, st, _usr())
    st.clear.assert_awaited()
    st.set_state.assert_awaited_with(OnboardingStates.collecting)
