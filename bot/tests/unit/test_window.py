"""P1.9: one live main-menu window; /menu and /start replace it instead of stacking menus."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.bot.window import replace_window


def _msg(new_id=200):
    msg = MagicMock()
    msg.chat.id = 55
    msg.bot.delete_message = AsyncMock()
    msg.answer = AsyncMock(return_value=SimpleNamespace(message_id=new_id))
    return msg


@pytest.mark.asyncio
async def test_old_window_is_deleted_and_the_new_id_remembered():
    msg, usr, session = _msg(200), SimpleNamespace(ui_message_id=100), MagicMock(commit=AsyncMock())
    sent = await replace_window(msg, usr, session, "menu", MagicMock())
    msg.bot.delete_message.assert_awaited_once_with(55, 100)
    assert usr.ui_message_id == 200 and sent.message_id == 200
    session.commit.assert_awaited()


@pytest.mark.asyncio
async def test_first_window_has_nothing_to_delete():
    msg, usr = _msg(), SimpleNamespace(ui_message_id=None)
    await replace_window(msg, usr, MagicMock(commit=AsyncMock()), "menu", MagicMock())
    msg.bot.delete_message.assert_not_awaited()


@pytest.mark.asyncio
async def test_failure_to_delete_an_old_window_never_blocks_the_new_one():
    """Telegram refuses to delete messages older than 48 h or already removed."""
    msg, usr = _msg(300), SimpleNamespace(ui_message_id=1)
    msg.bot.delete_message = AsyncMock(side_effect=RuntimeError("message can't be deleted"))
    await replace_window(msg, usr, MagicMock(commit=AsyncMock()), "menu", MagicMock())
    assert usr.ui_message_id == 300


@pytest.mark.asyncio
async def test_menu_command_uses_the_window():
    from app.bot.handlers import menu as mh

    usr = SimpleNamespace(
        id=1,
        language_code="ru",
        timezone="UTC",
        is_premium=False,
        subscription_expires_at=None,
        ui_message_id=10,
    )
    u_svc = MagicMock(get_or_create_telegram_user=AsyncMock(return_value=usr))
    u_svc.repo.session.commit = AsyncMock()
    p_svc = MagicMock(get_pet=AsyncMock(return_value=None))
    msg = _msg(500)
    msg.answer = AsyncMock(return_value=SimpleNamespace(message_id=500, delete=AsyncMock()))
    state = MagicMock(clear=AsyncMock())
    await mh.show_menu.__wrapped__(msg, state, u_svc, p_svc, MagicMock())
    msg.bot.delete_message.assert_awaited_once_with(55, 10)
    assert usr.ui_message_id == 500


@pytest.mark.asyncio
async def test_pressing_back_to_menu_tracks_the_edited_message_as_the_window():
    from app.bot.handlers import menu as mh

    usr = SimpleNamespace(
        id=1,
        language_code="ru",
        timezone="UTC",
        is_premium=False,
        subscription_expires_at=None,
        ui_message_id=None,
    )
    u_svc = MagicMock(get_or_create_telegram_user=AsyncMock(return_value=usr))
    u_svc.repo.session.commit = AsyncMock()
    p_svc = MagicMock(get_pet=AsyncMock(return_value=None))
    cb = MagicMock()
    cb.answer = AsyncMock()
    cb.from_user.id = 5
    cb.message.message_id = 777
    cb.message.edit_text = AsyncMock()
    await mh.back_to_main.__wrapped__(cb, MagicMock(clear=AsyncMock()), u_svc, p_svc, MagicMock())
    assert usr.ui_message_id == 777


@pytest.mark.asyncio
async def test_start_for_a_returning_user_replaces_the_window():
    """Regression: /start for an onboarded user must run end to end (a NameError hid here)."""
    from app.bot.handlers import start as sh

    user = SimpleNamespace(
        id=1,
        telegram_id=5,
        first_name="Аня",
        language_code="ru",
        timezone="UTC",
        is_premium=False,
        subscription_expires_at=None,
        ui_message_id=11,
        onboarding_completed_at="done",
        referrer_telegram_id=None,
    )
    user_service = MagicMock(get_or_create_telegram_user=AsyncMock(return_value=user))
    user_service.repo.session.commit = AsyncMock()
    message = _msg(900)
    message.text = "/start"
    message.from_user = SimpleNamespace(
        id=5, username="u", first_name="Аня", last_name=None, language_code="ru"
    )
    message.answer = AsyncMock(return_value=SimpleNamespace(message_id=900, delete=AsyncMock()))
    state = MagicMock(clear=AsyncMock())
    await sh.cmd_start.__wrapped__(message, state, user_service)
    message.bot.delete_message.assert_awaited_once_with(55, 11)
    assert user.ui_message_id == 900
