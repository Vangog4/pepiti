import asyncio
import logging
from datetime import datetime, timedelta

from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from dependency_injector.wiring import Provide, inject

from app.bot.filters.admin import IsAdmin
from app.core.container import AppContainer
from app.infrastructure.db.models.pet import PetModel
from app.infrastructure.db.models.subscription import SubscriptionModel
from app.infrastructure.db.repositories.user_repo import UserRepository
from app.infrastructure.redis.admin_log import AdminLog
from app.infrastructure.redis.ai_rate_limit import AiRateLimiter
from app.infrastructure.redis.metrics import BotMetrics
from app.logic.cascade import ModelCascade
from app.logic.rules import rule
from app.services.broadcast_service import run_broadcast

logger = logging.getLogger(__name__)
router = Router(name="admin_router")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


class BroadcastState(StatesGroup):
    waiting_for_text = State()
    waiting_for_confirm = State()


def _admin_keyboard() -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast")],
            [types.InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
            [types.InlineKeyboardButton(text="🧠 AI logic", callback_data="admin_ai_stats")],
            [types.InlineKeyboardButton(text="🔗 Рефералы", callback_data="admin_ref_stats")],
        ]
    )


@router.message(Command("admin"))
@inject
async def admin_menu(
    msg: types.Message,
    state: FSMContext,
    user_repo: UserRepository = Provide[AppContainer.user_repo],
) -> None:
    await state.clear()
    stats = await user_repo.get_rich_stats()
    conv = stats["conversion_pct"]
    text = (
        "🛠 <b>Admin-панель Pepito</b>\n\n"
        f"👥 Всего: <b>{stats['total']}</b>  |  "
        f"✅ Онбординг: <b>{stats['onboarded']}</b>  |  "
        f"⭐ Premium: <b>{stats['premium']}</b>\n"
        f"🆕 Новых сегодня: <b>{stats['new_today']}</b>  |  "
        f"🔥 Активных: <b>{stats['active_today']}</b>  |  "
        f"📈 Конверсия: <b>{conv}%</b>"
    )
    await msg.answer(text, reply_markup=_admin_keyboard(), parse_mode="HTML")


@router.callback_query(F.data == "admin_stats")
@inject
async def admin_stats(
    cb: types.CallbackQuery,
    user_repo: UserRepository = Provide[AppContainer.user_repo],
) -> None:
    await cb.answer()
    stats = await user_repo.get_rich_stats()
    conv = stats["conversion_pct"]
    text = (
        "📊 <b>Статистика</b>\n\n"
        f"👥 Всего: <b>{stats['total']}</b>  |  "
        f"✅ Онбординг: <b>{stats['onboarded']}</b>  |  "
        f"⭐ Premium: <b>{stats['premium']}</b>\n"
        f"🆕 Новых сегодня: <b>{stats['new_today']}</b>  |  "
        f"🔥 Активных: <b>{stats['active_today']}</b>  |  "
        f"📈 Конверсия: <b>{conv}%</b>"
    )
    await cb.message.edit_text(text, reply_markup=_admin_keyboard(), parse_mode="HTML")


@router.callback_query(F.data == "admin_ref_stats")
@inject
async def admin_referral_stats(
    cb: types.CallbackQuery,
    user_repo: UserRepository = Provide[AppContainer.user_repo],
) -> None:
    await cb.answer()
    stats = await user_repo.get_referral_stats()
    total = stats["total_referred"]
    top = stats["top"]

    lines = [f"🔗 <b>Реферальная статистика</b>\n\nВсего засчитанных рефералов: <b>{total}</b>"]
    if top:
        lines.append("\n<b>Топ рефереров:</b>")
        for i, row in enumerate(top, 1):
            lines.append(f"{i}. <code>{row[0]}</code> — {row[1]} приглаш.")
    else:
        lines.append("\nПока нет засчитанных рефералов.")

    await cb.message.edit_text("\n".join(lines), reply_markup=_admin_keyboard(), parse_mode="HTML")


@router.callback_query(F.data == "admin_ai_stats")
@inject
async def admin_ai_stats(
    cb: types.CallbackQuery,
    metrics: BotMetrics = Provide[AppContainer.metrics],
) -> None:
    """Logic-layer counters + active model routing from rules.json."""
    await cb.answer()
    ai = await metrics.get_ai_stats()
    cascade = ModelCascade()
    default_m = cascade.default
    escalate_m = cascade.escalate
    free_limit = rule("ai.free_daily_limit", 5)
    stars = rule("premium.stars_1m", 299)

    text = (
        "🧠 <b>AI logic layer</b>\n\n"
        f"📞 Calls: <b>{ai['ai_calls']}</b>\n"
        f"✅ Schema OK: <b>{ai['ai_schema_ok']}</b>  |  "
        f"❌ Schema fail: <b>{ai['ai_schema_fail']}</b>\n"
        f"📈 Schema OK rate: <b>{ai['schema_ok_rate_pct']}%</b>\n"
        f"⬆ Escalate: <b>{ai['ai_escalate']}</b>  |  "
        f"🛟 Fallback: <b>{ai['ai_fallback']}</b>\n"
        f"🚫 Forbidden hits: <b>{ai['ai_forbidden']}</b>\n\n"
        f"<b>Routing</b>\n"
        f"default: <code>{default_m}</code>\n"
        f"escalate/media/premium: <code>{escalate_m}</code>\n\n"
        f"<b>Business rules</b>\n"
        f"free AI/day: <b>{free_limit}</b>  |  Stars 1m: <b>{stars}</b>\n"
        f"<i>Source: app/logic/rules.json</i>"
    )
    await cb.message.edit_text(text, reply_markup=_admin_keyboard(), parse_mode="HTML")


@router.message(Command("grant_premium"))
@inject
async def grant_premium(
    msg: types.Message,
    user_repo: UserRepository = Provide[AppContainer.user_repo],
    alog: AdminLog = Provide[AppContainer.admin_log],
) -> None:
    parts = (msg.text or "").split()
    if len(parts) != 3:
        await msg.answer(
            "Использование: /grant_premium &lt;telegram_id&gt; &lt;days&gt;", parse_mode="HTML"
        )
        return
    try:
        telegram_id = int(parts[1])
        days = int(parts[2])
        if days <= 0:
            raise ValueError
    except ValueError:
        await msg.answer("Неверный формат. Пример: /grant_premium 123456789 7")
        return

    user = await user_repo.get_by_telegram_id(telegram_id)
    if not user:
        await msg.answer(f"Пользователь <code>{telegram_id}</code> не найден.", parse_mode="HTML")
        return

    now = datetime.utcnow()
    expires_at = max(user.subscription_expires_at or now, now) + timedelta(days=days)
    user.is_premium = True
    user.subscription_expires_at = expires_at

    user_repo.session.add(
        SubscriptionModel(
            user_id=user.id,
            plan_code="admin_grant",
            status="active",
            provider="admin",
            expires_at=expires_at,
        )
    )
    await user_repo.session.commit()

    name = user.first_name or user.username or str(telegram_id)
    await alog.log(
        msg.from_user.id,
        "grant_premium",
        str(telegram_id),
        f"+{days} days, until {expires_at.strftime('%d.%m.%Y')}",
    )
    logger.info("Admin granted %d days premium to user %s (%s)", days, telegram_id, name)
    await msg.answer(
        f"✅ <b>Premium выдан</b>\n\n"
        f"Кому: <b>{name}</b> (<code>{telegram_id}</code>)\n"
        f"Срок: <b>+{days} дней</b>\n"
        f"Действует до: <b>{expires_at.strftime('%d.%m.%Y')}</b>",
        parse_mode="HTML",
    )


@router.message(Command("revoke_premium"))
@inject
async def revoke_premium(
    msg: types.Message,
    user_repo: UserRepository = Provide[AppContainer.user_repo],
    alog: AdminLog = Provide[AppContainer.admin_log],
) -> None:
    parts = (msg.text or "").split()
    if len(parts) != 2:
        await msg.answer("Использование: /revoke_premium &lt;telegram_id&gt;", parse_mode="HTML")
        return
    try:
        telegram_id = int(parts[1])
    except ValueError:
        await msg.answer("Неверный формат. Пример: /revoke_premium 123456789")
        return

    user = await user_repo.get_by_telegram_id(telegram_id)
    if not user:
        await msg.answer(f"Пользователь <code>{telegram_id}</code> не найден.", parse_mode="HTML")
        return

    user.is_premium = False
    user.subscription_expires_at = None
    await user_repo.session.commit()

    name = user.first_name or user.username or str(telegram_id)
    await alog.log(msg.from_user.id, "revoke_premium", str(telegram_id))
    await msg.answer(
        f"✅ <b>Premium снят</b>\n\nПользователь: <b>{name}</b> (<code>{telegram_id}</code>)",
        parse_mode="HTML",
    )


@router.message(Command("user"))
@inject
async def lookup_user(
    msg: types.Message,
    user_repo: UserRepository = Provide[AppContainer.user_repo],
) -> None:
    parts = (msg.text or "").split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        await msg.answer(
            "Использование:\n/user &lt;telegram_id&gt;\n/user @username",
            parse_mode="HTML",
        )
        return

    query = parts[1].strip()
    if query.lstrip("-").isdigit():
        user = await user_repo.get_by_telegram_id(int(query))
    else:
        user = await user_repo.get_by_username(query)

    if not user:
        await msg.answer(f"Пользователь <code>{query}</code> не найден.", parse_mode="HTML")
        return

    pet_result = await user_repo.session.execute(
        __import__("sqlalchemy", fromlist=["select"])
        .select(PetModel)
        .where(PetModel.user_id == user.id)
        .limit(1)
    )
    pet = pet_result.scalar_one_or_none()

    premium_status = "❌ нет"
    if user.is_premium and user.subscription_expires_at:
        premium_status = f"✅ до {user.subscription_expires_at.strftime('%d.%m.%Y')}"
    elif user.is_premium:
        premium_status = "✅ активен"

    onboard = (
        f"✅ {user.onboarding_completed_at.strftime('%d.%m.%Y')}"
        if user.onboarding_completed_at
        else "❌ не завершён"
    )
    pet_info = f"{pet.name} ({pet.breed or '—'})" if pet else "—"
    username_str = f"@{user.username}" if user.username else "—"

    await msg.answer(
        f"👤 <b>{user.first_name or '—'}</b> ({username_str})\n"
        f"ID: <code>{user.telegram_id}</code>\n"
        f"Premium: {premium_status}\n"
        f"Онбординг: {onboard}\n"
        f"Питомец: {pet_info}\n"
        f"Регистрация: {user.created_at.strftime('%d.%m.%Y') if user.created_at else '—'}",
        parse_mode="HTML",
    )


@router.message(Command("msg"))
@inject
async def send_to_user(
    msg: types.Message,
    user_repo: UserRepository = Provide[AppContainer.user_repo],
    alog: AdminLog = Provide[AppContainer.admin_log],
) -> None:
    parts = (msg.text or "").split(maxsplit=2)
    if len(parts) < 3:
        await msg.answer("Использование: /msg &lt;telegram_id&gt; &lt;текст&gt;", parse_mode="HTML")
        return
    try:
        telegram_id = int(parts[1])
    except ValueError:
        await msg.answer("telegram_id должен быть числом.")
        return

    text = parts[2].strip()
    if not text:
        await msg.answer("Текст не может быть пустым.")
        return

    user = await user_repo.get_by_telegram_id(telegram_id)
    name = (user.first_name or user.username or str(telegram_id)) if user else str(telegram_id)

    try:
        await msg.bot.send_message(chat_id=telegram_id, text=text, parse_mode="HTML")
        await alog.log(msg.from_user.id, "send_msg", str(telegram_id), text[:60])
        await msg.answer(f"✅ Сообщение отправлено <b>{name}</b>", parse_mode="HTML")
    except Exception as e:
        await msg.answer(f"❌ Ошибка: {e}")


@router.message(Command("ai_reset"))
@inject
async def ai_reset(
    msg: types.Message,
    user_repo: UserRepository = Provide[AppContainer.user_repo],
    rate_limiter: AiRateLimiter = Provide[AppContainer.ai_rate_limiter],
    alog: AdminLog = Provide[AppContainer.admin_log],
) -> None:
    parts = (msg.text or "").split()
    if len(parts) != 2:
        await msg.answer("Использование: /ai_reset &lt;telegram_id&gt;", parse_mode="HTML")
        return
    try:
        telegram_id = int(parts[1])
    except ValueError:
        await msg.answer("telegram_id должен быть числом.")
        return

    user = await user_repo.get_by_telegram_id(telegram_id)
    name = (user.first_name or user.username or str(telegram_id)) if user else str(telegram_id)

    await rate_limiter.reset(telegram_id)
    await alog.log(msg.from_user.id, "ai_reset", str(telegram_id))
    await msg.answer(
        f"✅ AI-лимит сброшен для <b>{name}</b> (<code>{telegram_id}</code>)\n"
        f"Теперь у пользователя 5/5 запросов.",
        parse_mode="HTML",
    )


@router.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_start(cb: types.CallbackQuery, state: FSMContext) -> None:
    await cb.answer()
    await state.set_state(BroadcastState.waiting_for_text)
    await cb.message.edit_text(
        "📢 <b>Рассылка</b>\n\nНапиши текст сообщения (поддерживается HTML).\n\n"
        "Для отмены напиши /admin",
        parse_mode="HTML",
    )


@router.message(BroadcastState.waiting_for_text)
async def admin_broadcast_preview(msg: types.Message, state: FSMContext) -> None:
    text = msg.text or msg.caption or ""
    if not text.strip():
        await msg.answer("Текст не может быть пустым.")
        return

    await state.update_data(broadcast_text=text)
    await state.set_state(BroadcastState.waiting_for_confirm)
    await msg.answer(
        "📋 <b>Предпросмотр:</b>\n\n" + text + "\n\n<i>Отправить?</i>",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(text="✅ Всем", callback_data="bc_all"),
                    types.InlineKeyboardButton(text="⭐ Premium", callback_data="bc_premium"),
                    types.InlineKeyboardButton(text="🆓 Free", callback_data="bc_free"),
                    types.InlineKeyboardButton(text="❌ Отмена", callback_data="broadcast_cancel"),
                ]
            ]
        ),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "broadcast_cancel")
async def broadcast_cancel(cb: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await cb.answer("Отменено")
    await cb.message.edit_text("Рассылка отменена.", reply_markup=_admin_keyboard())


@router.callback_query(F.data.in_({"bc_all", "bc_premium", "bc_free"}))
@inject
async def broadcast_confirm(
    cb: types.CallbackQuery,
    state: FSMContext,
    user_repo: UserRepository = Provide[AppContainer.user_repo],
    alog: AdminLog = Provide[AppContainer.admin_log],
) -> None:
    await cb.answer()
    data = await state.get_data()
    text = data.get("broadcast_text", "")
    target = cb.data  # "bc_all" | "bc_premium" | "bc_free"
    await state.clear()

    from sqlalchemy import select as _select

    from app.infrastructure.db.models.user import UserModel

    q = _select(UserModel).where(UserModel.onboarding_completed_at.isnot(None))
    if target == "bc_premium":
        q = q.where(UserModel.is_premium == True)
    elif target == "bc_free":
        q = q.where(UserModel.is_premium == False)

    result = await user_repo.session.execute(q)
    users = result.scalars().all()
    target_label = {"bc_all": "всем", "bc_premium": "Premium", "bc_free": "Free"}[target]
    telegram_ids = [u.telegram_id for u in users]

    await cb.message.edit_text(
        f"⏳ <b>Рассылка запущена в фоне</b> ({target_label})\n\n"
        f"Получателей в очереди: <b>{len(telegram_ids)}</b>\n"
        f"По завершении бот пришлёт итоговый отчёт.",
        reply_markup=_admin_keyboard(),
        parse_mode="HTML",
    )

    await alog.log(cb.from_user.id, "broadcast", target_label, f"queued={len(telegram_ids)}")
    asyncio.create_task(run_broadcast(cb.bot, telegram_ids, text, cb.from_user.id))
