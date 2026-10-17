from aiogram import Router, types
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from dependency_injector.wiring import Provide, inject

from app.bot.keyboards.main_menu import get_main_menu
from app.bot.states.onboarding import OnboardingStates
from app.core.config import settings
from app.core.container import AppContainer
from app.i18n import normalize_locale, t
from app.services.user_service import UserService

router = Router(name="start_router")


@router.message(CommandStart())
@inject
async def cmd_start(
    message: types.Message,
    state: FSMContext,
    user_service: UserService = Provide[AppContainer.user_service],
) -> None:
    if not message.from_user:
        return

    await state.clear()

    # Parse deep links before creating the user
    parts = (message.text or "").split(maxsplit=1)
    payload = parts[1].strip() if len(parts) > 1 else ""
    if payload.startswith("ref_"):
        try:
            referrer_tid = int(payload[4:])
            if referrer_tid != message.from_user.id:
                await state.update_data(referrer_telegram_id=referrer_tid)
        except ValueError:
            pass

    user = await user_service.get_or_create_telegram_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        language_code=message.from_user.language_code,
    )

    lang = normalize_locale(user.language_code)

    if payload.startswith("auth_"):
        import json

        from redis.asyncio import Redis

        session_token = payload[5:]
        redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
        try:
            raw = await redis.get(f"tg_session:{session_token}")
            if raw:
                await redis.set(
                    f"tg_session:{session_token}",
                    json.dumps({"status": "authenticated", "user_id": user.id}),
                    ex=600,
                )
                await message.answer(
                    "🐾 <b>Вход в мобильное приложение Pepito подтвержден!</b>\n\n"
                    "Вы можете вернуться в приложение — данные синхронизированы.",
                    reply_markup=get_main_menu(
                        user.is_premium, webapp_url=settings.WEBAPP_PUBLIC_URL, lang=lang
                    ),
                    parse_mode="HTML",
                )
                return
        finally:
            await redis.aclose()

    if user.onboarding_completed_at:
        tmp = await message.answer("⌛️", reply_markup=ReplyKeyboardRemove())
        await tmp.delete()
        if payload in {"premium", "buy_premium"}:
            from app.bot.handlers.subscription import send_premium_invoice

            await send_premium_invoice(message, lang)
            return
        if payload == "coach":
            from app.bot.handlers.menu import CoachState

            await state.set_state(CoachState.waiting_for_question)
            await message.answer(
                t("coach.entry", lang),
                reply_markup=get_main_menu(
                    user.is_premium, webapp_url=settings.WEBAPP_PUBLIC_URL, lang=lang
                ),
                parse_mode="HTML",
            )
            return
        await message.answer(
            t("onboarding.start.returning", lang, name=user.first_name),
            reply_markup=get_main_menu(
                user.is_premium, webapp_url=settings.WEBAPP_PUBLIC_URL, lang=lang
            ),
        )
        return

    await message.answer(
        t("onboarding.ai.welcome", lang, name=message.from_user.first_name),
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(OnboardingStates.collecting)


@router.message(Command("connect"))
@inject
async def cmd_connect(
    message: types.Message,
    user_service: UserService = Provide[AppContainer.user_service],
) -> None:
    if not message.from_user:
        return

    import secrets

    from redis.asyncio import Redis

    user = await user_service.get_or_create_telegram_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        language_code=message.from_user.language_code,
    )

    redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        code = None
        for _ in range(5):
            candidate = f"{secrets.randbelow(900000) + 100000}"
            if await redis.set(f"tg_connect_code:{candidate}", str(user.id), ex=600, nx=True):
                code = candidate
                break
    finally:
        await redis.aclose()

    if not code:
        await message.answer("⚠️ Не удалось сгенерировать код. Попробуйте еще раз через минуту.")
        return

    await message.answer(
        f"📱 <b>Код для подключения мобильного приложения:</b>\n\n"
        f"<code>{code}</code>\n\n"
        "Код действителен 10 минут. Введите его в приложении Pepito на телефоне, чтобы синхронизировать данные с этим аккаунтом.",
        parse_mode="HTML",
    )
