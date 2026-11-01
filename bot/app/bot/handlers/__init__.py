from aiogram import Dispatcher

from app.bot.handlers.admin import router as admin_router
from app.bot.handlers.cards import router as cards_router
from app.bot.handlers.edit_profile import router as edit_profile_router
from app.bot.handlers.gift import router as gift_router
from app.bot.handlers.health import router as health_router
from app.bot.handlers.help import router as help_router
from app.bot.handlers.memory import router as memory_router
from app.bot.handlers.menu import router as menu_router
from app.bot.handlers.onboarding import router as onboarding_router
from app.bot.handlers.pets import router as pets_router
from app.bot.handlers.reset import router as reset_router
from app.bot.handlers.start import router as start_router
from app.bot.handlers.subscription import router as subscription_router
from app.bot.handlers.tracker import router as tracker_router


def setup_routers(dp: Dispatcher) -> None:
    dp.include_router(admin_router)  # первым — фильтр IsAdmin на всём роутере
    dp.include_router(start_router)
    dp.include_router(onboarding_router)
    dp.include_router(health_router)
    dp.include_router(tracker_router)
    dp.include_router(cards_router)
    dp.include_router(pets_router)
    dp.include_router(gift_router)
    dp.include_router(memory_router)  # before menu: its FSM catch-alls must not shadow it
    dp.include_router(menu_router)
    dp.include_router(edit_profile_router)
    dp.include_router(reset_router)
    dp.include_router(help_router)
    dp.include_router(subscription_router)
