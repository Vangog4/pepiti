"""Regression test: /reset must leave the user in OnboardingStates.collecting.

Root cause of original bug:
  reset.py used OnboardingStates.pet_name (non-existent attribute) → AttributeError
  was swallowed by aiogram → state remained None (default_state) → handle_voice_action
  intercepted the next message → found no pet → silent exit.
"""

import sys
from unittest.mock import AsyncMock, MagicMock, patch, call

import pytest

sys.path.insert(0, ".")

from app.bot.states.onboarding import OnboardingStates


# ── 1. State attribute guard ─────────────────────────────────────────────────


def test_onboarding_states_has_collecting():
    """OnboardingStates.collecting must exist — it is the entry point for onboarding."""
    assert hasattr(OnboardingStates, "collecting"), (
        "OnboardingStates.collecting is missing; reset and /start both depend on it"
    )


def test_onboarding_states_has_no_pet_name():
    """OnboardingStates.pet_name must NOT exist — it caused the original silent-bot bug."""
    assert not hasattr(OnboardingStates, "pet_name"), (
        "OnboardingStates.pet_name should not exist; use OnboardingStates.collecting instead"
    )


# ── 2. Handler calls set_state with the correct state ────────────────────────


@pytest.mark.asyncio
async def test_reset_sets_collecting_state():
    """/reset handler must call state.set_state(OnboardingStates.collecting)."""
    from app.bot.handlers.reset import reset_profile

    # Mock message
    msg = MagicMock()
    msg.from_user.id = 12345
    msg.answer = AsyncMock()

    # Mock FSM state
    state = MagicMock()
    state.clear = AsyncMock()
    state.set_state = AsyncMock()

    # Mock user
    fake_user = MagicMock()
    fake_user.id = 1
    fake_user.onboarding_completed_at = None
    fake_user.language_code = "ru"

    # Mock session — no pets
    mock_result = MagicMock()
    mock_result.fetchall.return_value = []
    mock_session = MagicMock()
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.commit = AsyncMock()

    mock_u_svc = MagicMock()
    mock_u_svc.get_or_create_telegram_user = AsyncMock(return_value=fake_user)
    mock_u_svc.repo.session = mock_session

    msg.from_user.first_name = "Test"

    await reset_profile(msg, state, u_svc=mock_u_svc)

    # Verify state.clear() was called first
    state.clear.assert_called_once()

    # Verify state.set_state was called with OnboardingStates.collecting
    state.set_state.assert_called_once_with(OnboardingStates.collecting)


@pytest.mark.asyncio
async def test_reset_sends_name_prompt():
    """/reset handler must send a message asking for the pet's name."""
    from app.bot.handlers.reset import reset_profile

    msg = MagicMock()
    msg.from_user.id = 12345
    msg.answer = AsyncMock()

    state = MagicMock()
    state.clear = AsyncMock()
    state.set_state = AsyncMock()

    fake_user = MagicMock()
    fake_user.id = 1
    fake_user.onboarding_completed_at = None
    fake_user.language_code = "ru"

    mock_result = MagicMock()
    mock_result.fetchall.return_value = []
    mock_session = MagicMock()
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.commit = AsyncMock()

    mock_u_svc = MagicMock()
    mock_u_svc.get_or_create_telegram_user = AsyncMock(return_value=fake_user)
    mock_u_svc.repo.session = mock_session

    msg.from_user.first_name = "Test"

    await reset_profile(msg, state, u_svc=mock_u_svc)

    msg.answer.assert_called_once()
    call_text = msg.answer.call_args[0][0]
    assert "кинолог" in call_text.lower() or "собак" in call_text.lower(), (
        f"Expected AI-onboarding welcome prompt, got: {call_text!r}"
    )
