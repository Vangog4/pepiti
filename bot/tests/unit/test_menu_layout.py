"""P1.9: six-button main menu, short labels, and a ratchet on over-long button text."""

import re

from app.bot.keyboards.main_menu import get_main_menu, get_more_menu
from app.i18n.core import _load_locale

LOCALES = ("ru", "en", "de", "es", "fr", "pt")
MAX_LEN = 14
# Over-long labels still to shorten (P1.10 text pass). This number may only go DOWN.
OVERLONG_BASELINE = 111


def _buttons(kb):
    return [b for r in kb.inline_keyboard for b in r]


def test_main_menu_has_at_most_six_buttons_and_fits():
    for lg in LOCALES:
        for premium in (False, True):
            btns = _buttons(get_main_menu(premium, "https://x.example", lg))
            assert len(btns) <= 6
            assert all(len(b.text) <= MAX_LEN for b in btns), (lg, [b.text for b in btns])


def test_more_menu_labels_fit_and_everything_is_reachable():
    for lg in LOCALES:
        kb = get_more_menu(False, "https://x.example", lg)
        assert all(len(b.text) <= MAX_LEN for b in _buttons(kb)), lg
    reach = {b.callback_data for b in _buttons(get_main_menu(False, "", "ru"))}
    reach |= {b.callback_data for b in _buttons(get_more_menu(False, "", "ru"))}
    for needed in (
        "menu_training",
        "menu_coach",
        "menu_health",
        "menu_tracker",
        "menu_profile",
        "menu_week_plan",
        "menu_stats",
        "menu_premium",
        "menu_settings",
        "menu_shop",
        "menu_invite",
        "menu_main",
    ):
        assert needed in reach, needed


def _overlong() -> int:
    n = 0
    for lg in LOCALES:
        for k, v in _load_locale(lg).items():
            if isinstance(v, str) and (k.endswith(".btn") or ".btn." in k):
                if len(re.sub(r"\{[^}]*\}", "00", v)) > MAX_LEN:
                    n += 1
    return n


def test_overlong_button_labels_never_grow():
    assert _overlong() <= OVERLONG_BASELINE, _overlong()


def test_user_messages_are_never_deleted_in_menu_handlers():
    """Owner decision: keep the owner's questions in the chat (context is not lost)."""
    import pathlib

    src = pathlib.Path("app/bot/handlers/menu.py").read_text()
    assert "msg.delete()" not in src
    assert "msg.delete()" not in pathlib.Path("app/bot/handlers/edit_profile.py").read_text()
