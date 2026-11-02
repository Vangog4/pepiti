"""One live main-menu window per chat.

The window is the message the owner navigates with (screens edit it in place). When the
owner asks for the menu again (/menu, /start) the previous window is removed so menus do not
pile up. Telegram refuses to delete messages older than 48 h or already gone: that is fine,
the new window is sent regardless.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


async def replace_window(
    msg: Any, usr: Any, session: Any, text: str, markup: Any, parse_mode: str | None = "HTML"
) -> Any:
    old = getattr(usr, "ui_message_id", None)
    if old:
        try:
            await msg.bot.delete_message(msg.chat.id, old)
        except Exception:
            logger.debug("old window %s could not be deleted", old)
    sent = await msg.answer(text, reply_markup=markup, parse_mode=parse_mode)
    usr.ui_message_id = sent.message_id
    await session.commit()
    return sent
