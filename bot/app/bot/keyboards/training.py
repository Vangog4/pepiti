from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.i18n import t
from app.infrastructure.db.models.training import TrainingTaskModel


def get_task_keyboard(
    tasks: list[TrainingTaskModel],
    shop_btn: InlineKeyboardButton | None = None,
    extra_btns: list[InlineKeyboardButton] | None = None,
    lang: str = "ru",
) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    sorted_tasks = sorted(tasks, key=lambda task: task.day_of_week or 0)
    for task in sorted_tasks:
        icon = "✅" if task.is_completed else "⬜"
        title = task.title[:22] + "…" if len(task.title) > 24 else task.title
        state = 1 if task.is_completed else 0
        b.row(
            InlineKeyboardButton(text=f"{icon} {title}", callback_data=f"task_done:{task.id}:{state}"),
            InlineKeyboardButton(text=t("training.explain.btn", lang), callback_data=f"expl_d:{task.id}"),
        )
    # extra_btns takes precedence over legacy shop_btn
    buttons = extra_btns if extra_btns is not None else ([shop_btn] if shop_btn else [])
    for btn in buttons:
        b.row(btn)
    b.row(
        InlineKeyboardButton(text=t("training.refresh.btn", lang), callback_data="refresh_confirm"),
        InlineKeyboardButton(text=t("common.menu.btn", lang), callback_data="menu_main"),
    )
    return b.as_markup()


def get_week_day_keyboard(
    tasks: list[TrainingTaskModel],
    plan_id: int,
    day: int,
    shop_btn: InlineKeyboardButton | None = None,
    lang: str = "ru",
) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    day_tasks = sorted([task for task in tasks if task.day_of_week == day], key=lambda task: task.id)
    for task in day_tasks:
        icon = "✅" if task.is_completed else "⬜"
        title = task.title[:22] + "…" if len(task.title) > 24 else task.title
        state = 1 if task.is_completed else 0
        b.row(
            InlineKeyboardButton(
                text=f"{icon} {title}",
                callback_data=f"week_task:{task.id}:{plan_id}:{day}:{state}",
            ),
            InlineKeyboardButton(
                text=t("training.explain.btn", lang),
                callback_data=f"expl_w:{task.id}:{plan_id}:{day}",
            ),
        )
    nav: list[InlineKeyboardButton] = []
    if day > 1:
        nav.append(InlineKeyboardButton(
            text=f"◀ {t(f'training.day.short.{day - 1}', lang)}",
            callback_data=f"week_day:{plan_id}:{day - 1}",
        ))
    if day < 7:
        nav.append(InlineKeyboardButton(
            text=f"{t(f'training.day.short.{day + 1}', lang)} ▶",
            callback_data=f"week_day:{plan_id}:{day + 1}",
        ))
    if nav:
        b.row(*nav)
    if shop_btn:
        b.row(shop_btn)
    b.row(
        InlineKeyboardButton(text=t("training.refresh.btn", lang), callback_data="refresh_week_confirm"),
        InlineKeyboardButton(text=t("common.menu.btn", lang), callback_data="menu_main"),
    )
    return b.as_markup()
