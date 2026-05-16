import asyncio
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter

logger = logging.getLogger(__name__)


async def run_broadcast(
    bot: Bot,
    telegram_ids: list[int],
    text: str,
    admin_telegram_id: int,
    reply_markup=None,
) -> None:
    """Send text (+ optional inline keyboard) to all telegram_ids and notify admin.

    Respects Telegram rate limits: 0.05 s delay between sends (~20 msg/s).
    Blocked users are silently skipped. RetryAfter is respected with one retry.
    """
    sent = 0
    failed = 0

    for tid in telegram_ids:
        try:
            await bot.send_message(
                chat_id=tid, text=text, parse_mode="HTML", reply_markup=reply_markup
            )
            sent += 1
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
            try:
                await bot.send_message(
                    chat_id=tid, text=text, parse_mode="HTML", reply_markup=reply_markup
                )
                sent += 1
            except Exception:
                failed += 1
        except TelegramForbiddenError:
            failed += 1
        except Exception as exc:
            logger.warning("Broadcast: failed for %s: %s", tid, exc)
            failed += 1
        await asyncio.sleep(0.05)

    logger.info("Broadcast done: sent=%d failed=%d total=%d", sent, failed, len(telegram_ids))

    try:
        await bot.send_message(
            chat_id=admin_telegram_id,
            text=(
                f"📣 Рассылка завершена!\n"
                f"Успешно отправлено: {sent}\n"
                f"Заблокировали бота / Ошибки: {failed}"
            ),
        )
    except Exception as exc:
        logger.warning("Failed to notify admin about broadcast: %s", exc)
