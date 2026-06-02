"""
Russian (ru) — source-of-truth locale.
All keys that exist in the system MUST be present here.
Other locales may omit keys; the fallback chain will reach ru.
"""

STRINGS: dict[str, str] = {
    # ── Main menu ──────────────────────────────────────────────────────────────
    "menu.main.greeting": "🐾 <b>Главное меню Pepito</b>",
    "menu.main.choose": "Выбери нужный раздел:",
    "menu.btn.training": "🏋️ Тренировка на сегодня",
    "menu.btn.week_plan": "📅 Недельный план",
    "menu.btn.stats": "📊 Статистика",
    "menu.btn.coach": "💬 Вопрос кинологу",
    "menu.btn.profile": "🐶 Мой питомец",
    "menu.btn.premium": "⭐ Получить Premium",
    "menu.btn.premium.active": "⭐ Premium (активен)",
    "menu.btn.shop": "🛒 Магазин",
    "menu.btn.invite": "🐾 Позови друга",
    "menu.btn.webapp": "📊 Дашборд",
    "menu.main.streak": "{emoji} Тренировок выполнено: <b>{n}</b>\n\n",
    "menu.main.streak.days.one": "день",
    "menu.main.streak.days.few": "дня",
    "menu.main.streak.days.many": "дней",
    # ── Common buttons ─────────────────────────────────────────────────────────
    "common.back_menu.btn": "🔙 В главное меню",
    "common.back.btn": "🔙 Назад",
    "common.menu.btn": "🔙 Меню",
    # ── Errors / Guards ────────────────────────────────────────────────────────
    "error.no_pet": "Сначала пройди регистрацию /start",
    # ── Settings ───────────────────────────────────────────────────────────────
    "settings.main.title": "⚙️ <b>Настройки</b>",
    "settings.main.reminder_on": "⏰ Напоминания: <b>{time} ({tz})</b>",
    "settings.main.reminder_default": "⏰ Напоминания: <b>10:00 ({tz})</b>, по умолчанию",
    "settings.main.reminder_off": "⏰ Напоминания: <b>отключены</b>",
    "settings.language.title": "🌐 <b>Язык / Language</b>",
    "settings.language.choose": "Выбери язык интерфейса:",
    "settings.language.saved": "✅ Язык изменён на <b>{name}</b>.",
    "settings.language.btn": "🌐 Язык",
    "settings.btn": "⚙️ Настройки",
    "settings.reminder.btn": "⏰ Напоминания",
    # ── Onboarding (Stage 9: conversational AI) ────────────────────────────────
    "onboarding.start.returning": "С возвращением, {name}! 🐾\nЧто будем делать сегодня?",
    "onboarding.ai.welcome": (
        "🐾 Привет, <b>{name}</b>!\n"
        "──────────\n"
        "Я — твой AI-кинолог <b>Pepito</b>. 🐶\n\n"
        "Расскажи о своей собаке:\n"
        "• как зовут\n"
        "• порода и возраст\n"
        "• с какими трудностями сталкиваетесь\n\n"
        "<i>Текстом или голосовым сообщением.</i>\n\n"
        "<b>Например:</b> «Бигль Чарли, 2 года, тянет поводок и лает на других собак»"
    ),
    "onboarding.ai.thinking": "⏳ <i>Анализирую...</i>",
    "onboarding.ai.photo_prompt": (
        "📷 Красивый питомец! Расскажи о нём текстом или голосом:\n"
        "как зовут, порода, возраст и с чем нужна помощь?"
    ),
    "onboarding.ai.clarify": "Отлично, записал: <b>{summary}</b>\n\n{question}",
    "onboarding.ai.clarify.name": "Как зовут твоего питомца?",
    "onboarding.ai.clarify.breed": "Какая у него порода?",
    "onboarding.ai.clarify.age_category": "Сколько ему лет? (щенок, молодой или взрослый?)",
    # completion — interpolation: {name}, {pet}
    "onboarding.done.welcome": (
        "🎉 <b>Профиль создан!</b>\n"
        "──────────\n"
        "Добро пожаловать, {name}!\n\n"
        "🐾 Я готов помочь тебе с тренировками <b>{pet}</b>."
    ),
    "onboarding.done.referral_bonus": "\n\n🎁 <b>Бонус за приглашение:</b> +{days} дня Premium активированы!",
    "onboarding.done.milestone": "\n🏆 <b>Реферальный milestone:</b> {label} — {reward}!",
    "onboarding.done.plan_loading": "🐾 <i>Составляю первый план тренировки для {pet}...</i>",
    "onboarding.done.first_plan": "🏋️ <b>Вот твой первый план!</b>\n\n{plan}",
    "onboarding.done.fallback": "Выбери, с чего начнём 👇",
    # ── Training ───────────────────────────────────────────────────────────────
    "training.loading": "🐾 <i>Составляю план для {name}...</i>",
    "training.refresh.confirm": "🔄 <b>Сгенерировать новый план?</b>\n\nТекущий прогресс будет сброшен.",
    "training.refresh.confirm.yes": "✅ Да, новый план",
    "training.refresh.confirm.no": "❌ Нет",
    "training.refresh.loading": "🔄 <i>Генерирую новый план для {name}...</i>",
    "training.refresh.toast": "Генерирую новый план…",
    "training.week.loading": "📅 <i>Составляю недельный план для {name}...</i>",
    "training.week.refresh.confirm": (
        "🔄 <b>Сгенерировать новый недельный план?</b>\n\nТекущий прогресс недели будет сброшен."
    ),
    "training.week.refresh.loading": "🔄 <i>Генерирую новый недельный план для {name}...</i>",
    "training.week.empty": (
        "📅 <b>Недельный план</b>\n"
        "──────────\n"
        "🌱 <b>Пока нет задач</b>\n\n"
        "Начни с ежедневного плана — Pepito составит недельный, "
        "когда накопится немного прогресса!"
    ),
    "training.week.empty.cta.btn": "🏋️ Тренировка на сегодня",
    "training.explain.btn": "📖 Объяснить",
    "training.refresh.btn": "🔄 Новый план",
    "training.explain.loading": "🔍 <i>Объясняю упражнение «{title}»...</i>",
    "training.explain.back_daily.btn": "🔙 К тренировке",
    "training.explain.back_weekly.btn": "🔙 К плану",
    "training.task.not_found": "Задача не найдена.",
    "training.plan.not_found": "План не найден.",
    "training.task.toggle.done": "✅ Выполнено!",
    "training.task.toggle.undone": "↩️ Отменено",
    "training.share.text": "Мы с {name} тренируемся {n} {days} подряд с Pepito! 🐾",
    "training.share.btn": "📤 Поделиться",
    "training.done": (
        "\n\n──────────\n"
        "🎉 <b>Тренировка завершена!</b>\n"
        "Отличная работа!\n\n"
        "{emoji} Тренировок всего: <b>{n}</b>"
    ),
    "training.week_done": (
        "\n\n──────────\n"
        "🎉 <b>{day} выполнен!</b>\n"
        "Отличная работа!\n\n"
        "{emoji} Тренировок всего: <b>{n}</b>"
    ),
    "training.stats.empty": (
        "🌱 <b>Ты только начинаешь!</b>\n\n"
        "Первая тренировка — самая важная.\n"
        "Открой план на сегодня и отметь первое упражнение выполненным — "
        "счётчик тренировок начнёт расти!"
    ),
    "training.stats.empty.cta": "🏋️ Начать тренировку",
    "training.minutes.abbr": "мин",
    "training.goal.label": "Цель",
    "training.day.1": "Понедельник",
    "training.day.2": "Вторник",
    "training.day.3": "Среда",
    "training.day.4": "Четверг",
    "training.day.5": "Пятница",
    "training.day.6": "Суббота",
    "training.day.7": "Воскресенье",
    "training.day.short.1": "Пн",
    "training.day.short.2": "Вт",
    "training.day.short.3": "Ср",
    "training.day.short.4": "Чт",
    "training.day.short.5": "Пт",
    "training.day.short.6": "Сб",
    "training.day.short.7": "Вс",
    "coach.display.photo": "[📷 Фото]",
    "coach.display.voice": "[🎤 Голосовое]",
    "coach.display.video": "[🎥 Видео]",
    "defaults.pet_name": "Питомец",
    # ── AI / Coach ─────────────────────────────────────────────────────────────
    "ai.fallback": (
        "🧠 <b>Кинолог сейчас занят</b>\n"
        "──────────\n"
        "Слишком много запросов одновременно.\n\n"
        "Попробуй через минуту — обычно это проходит быстро.\n"
        "<i>Если проблема повторяется — введи /menu и попробуй снова.</i>"
    ),
    "ai.rate_limit": (
        "💬 <b>Дневной лимит исчерпан</b>\n"
        "──────────\n"
        "Free-план: <b>5 AI-запросов в день</b>\n"
        "Лимит обновится в полночь по UTC.\n\n"
        "⭐ <b>Premium — без ограничений:</b>\n"
        "💬 Безлимитные вопросы кинологу\n"
        "🧠 Глубокий анализ прогресса\n"
        "🎁 Персональные рекомендации\n"
        "──────────"
    ),
    "ai.rate_limit.btn": "⭐ Попробовать Premium",
    "ai.analyzing.premium": "🧠 <i>Провожу глубокий анализ...</i>",
    "ai.analyzing.free": "🧠 <i>Анализирую прогресс...</i>",
    "ai.progress.premium.header": "⭐ <b>Глубокий анализ прогресса {name}</b>\n\n",
    "ai.progress.free.header": "📈 <b>Анализ прогресса {name}</b>\n\n",
    "ai.progress.back.btn": "🔙 К статистике",
    "ai.retry.btn": "🔄 Попробовать снова",
    "ai.back_menu.btn": "🔙 Меню",
    "coach.entry": (
        "💬 <b>Вопрос кинологу</b>\n\n"
        "Напиши любой вопрос о дрессировке или поведении питомца — или пришли <b>📷 фото</b>.\n"
        "<i>Например: «Как отучить тянуть поводок?» или «Почему игнорирует команду “Лежать”?»</i>\n\n"
        "Бесплатно: текст + фото\n"
        "⭐ Premium: + 🎤 голосовые сообщения и 🎥 видео"
    ),
    "coach.thinking": "🧠 <i>Анализирую вопрос...</i>",
    "coach.media.thinking": "🔍 <i>Анализирую медиа...</i>",
    "coach.media.voice.premium": (
        "🎤 <b>Анализ голосовых — только для Premium</b>\n\n"
        "Отправь <b>📷 фото</b> питомца — это бесплатно.\n\n"
        "⭐ Premium открывает анализ голосовых и видео без ограничений."
    ),
    "coach.media.video.premium": (
        "🎥 <b>Анализ видео — только для Premium</b>\n\n"
        "Отправь <b>📷 фото</b> питомца — это бесплатно.\n\n"
        "⭐ Premium открывает анализ видео и голосовых без ограничений."
    ),
    "coach.media.too_large": "⚠️ Файл слишком большой (максимум 20 МБ). Попробуй отправить покороче.",
    "coach.hub.active_thread": (
        "💬 <b>Кинолог</b> · <i>{title}</i>\n\n"
        "{count} сообщ. · продолжается\n\n"
        "Напиши вопрос или отправь фото."
    ),
    "coach.hub.archive_btn": "📁 Завершить консультацию",
    "coach.new_thread.btn": "🆕 Новая консультация",
    "coach.thread.archived": "✔ Консультация завершена.",
    "coach.thread.title_default": "Консультация",
    "coach.role.owner": "Хозяин",
    "coach.role.trainer": "Кинолог",
    "coach.summary.header": "Краткое резюме предыдущей беседы:",
    # ── Voice-action (hands-free task reporting) ───────────────────────────────
    "voice_action.thinking": "🐾 <i>Анализирую...</i>",
    "voice_action.marked": "✅ Я отметил задачу <b>{task}</b> как выполненную!\n\n",
    "voice_action.all_done": "🎉 Все задачи дня выполнены! Отличная тренировка!",
    # ── Stats ──────────────────────────────────────────────────────────────────
    "stats.header": "📊 <b>Статистика {name}</b>\n──────────\n",
    "stats.days_with_us": "🗓 Дней с Pepito: <b>{n}</b>\n",
    "stats.completed": "{emoji} Тренировок выполнено: <b>{n}</b>\n",
    "stats.level": "🏆 Уровень послушания: <b>{level}</b>\n\n──────────\n",
    "stats.motivate": "<i>Каждая тренировка делает {name} лучше!</i> 🚀",
    "stats.analysis.premium.btn": "🧠 Глубокий анализ AI ⭐",
    "stats.analysis.free.btn": "🧠 Анализ прогресса AI",
    # ── Profile ────────────────────────────────────────────────────────────────
    "profile.header": "🐾 <b>{name}</b>\n──────────\n",
    "profile.breed": "🐕 Порода: {val}\n",
    "profile.sex": "⚥ Пол: {val}\n",
    "profile.age": "🎂 Возраст: {val}\n",
    "profile.size": "📏 Размер: {val}\n",
    "profile.weight": "⚖️ Вес: {val}\n\n",
    "profile.level": "🎓 Уровень: {val}/5\n",
    "profile.goal": "🎯 Цель: {val}\n",
    "profile.issues": "📋 Проблемы: {val}\n",
    "profile.schedule": "🗓 Расписание: {val}\n\n──────────\n",
    "profile.training_count": "🔥 Тренировок выполнено: <b>{n}</b>",
    "profile.weight.unit": "кг",
    "profile.weight.unknown": "не указан",
    "profile.issues.none": "нет",
    "profile.schedule.unknown": "не указано",
    "profile.edit.btn": "✏️ Изменить профиль",
    # ── Shop ───────────────────────────────────────────────────────────────────
    "shop.title": "🛒 <b>Магазин PepitoPet</b>",
    "shop.body": (
        "Натуральные лакомства собственного производства — "
        "без химии и консервантов, из настоящего мяса.\n\n"
        "Выбери категорию:"
    ),
    "shop.cat.training.btn": "🎯 Для дрессировки",
    "shop.cat.longplay.btn": "🦴 Долгоиграющие",
    "shop.cat.by_size.btn": "🐶 Для щенков и по размеру",
    "shop.cat.all.btn": "🛒 Весь магазин",
    # ── Invite / Referral ──────────────────────────────────────────────────────
    "invite.title": "🐾 <b>Позови друга — бонус обоим!</b>",
    "invite.link_label": "🔗 Твоя ссылка:",
    "invite.bonus": "🎁 Каждый друг даёт <b>+{days} дня Premium</b> — тебе <i>и</i> ему.",
    "invite.ladder.title": "🏆 <b>Путь наград:</b>",
    "invite.count": "👥 Приглашено: <b>{n}</b>",
    "invite.next": "🎯 До следующей награды: ещё <b>{n}</b>",
    "invite.all_done": "👑 <b>Все награды получены! Ты легенда!</b>",
    "invite.share.btn": "📤 Поделиться ссылкой",
    "invite.share.text": "Тренирую питомца с AI-кинологом Pepito 🐾",
    "invite.base_tier": "1 друг    — +{days} дней Premium (обоим)",
    "invite.goal": "🎯 Ещё {needed} до {next_label} ({reward})",
    "invite.current_goal": "← следующая цель",
    "invite.how.title": "❓ <b>Как это работает:</b>",
    "invite.how.1": "1. Поделись ссылкой",
    "invite.how.2": "2. Друг запускает бота и заполняет профиль",
    "invite.how.3": "3. Вы оба получаете +{days} дней Premium",
    # ── Referral push-notifications ────────────────────────────────────────────
    "referral.notify.base": (
        "🎉 По твоей ссылке пришёл новый друг!\n"
        "+{days} дней Premium начислено. Приглашено: <b>{count}</b>\n{ladder_hint}"
    ),
    "referral.notify.milestone": (
        "🏆 <b>{label}!</b>\n\n"
        "Ты пригласил {count} друзей и получаешь <b>{reward}</b>!\n{next_hint}"
    ),
    "referral.notify.next_hint": "🎯 Следующая цель: {next_label} → {next_reward}",
    "referral.notify.all_done": "👑 Все награды получены!",
    "referral.milestone.label.3": "3 друга",
    "referral.milestone.label.5": "5 друзей",
    "referral.milestone.label.10": "10 друзей",
    "referral.milestone.label.25": "25 друзей",
    "referral.reward.days": "+{days} дней",
    # ── Premium / Subscription ─────────────────────────────────────────────────
    "premium.active.title": "⭐ <b>Premium активен</b>",
    "premium.active.expires": "Действует до: <b>{date}</b>",
    "premium.active.features": (
        "\n──────────\n"
        "Доступно:\n"
        "💬 Безлимитные вопросы кинологу\n"
        "🧠 Глубокий AI-анализ прогресса\n"
        "🎁 Персональные рекомендации лакомств"
    ),
    "premium.upsell.body": (
        "⭐ <b>Pepito Premium</b>\n\n"
        "💬 Вопросы кинологу — без лимитов\n"
        "🧠 Глубокий AI-анализ прогресса\n"
        "🎁 Персональные рекомендации лакомств\n\n"
        "<b>{price} Stars</b> / месяц · или пригласи 3 друзей — бесплатно"
    ),
    "premium.upsell.btn": "⭐ Получить Premium за {price} Stars",
    "premium.invoice.title": "Pepito Premium — 1 месяц",
    "premium.invoice.description": "AI-кинолог без ограничений, детальные отчёты и расширенный анализ поведения питомца.",
    "premium.invoice.label": "Premium 1 месяц",
    "premium.activated": (
        "🎉 <b>Premium активирован!</b>\n"
        "──────────\n"
        "Теперь доступно:\n"
        "💬 Вопросы кинологу без ограничений\n"
        "🧠 Глубокий анализ прогресса питомца\n"
        "🎁 Персональные рекомендации лакомств\n\n"
        "Используй /menu чтобы начать."
    ),
    "premium.refunded": (
        "✔ Возврат средств обработан. Подписка Premium деактивирована.\n"
        "Если это ошибка — обратись в поддержку."
    ),
    # ── Reminders ─────────────────────────────────────────────────────────────
    "reminder.title": "⏰ <b>Напоминания</b>",
    "reminder.status.off": "🔕 <b>Отключены</b>",
    "reminder.status.off.desc": "Ежедневные напоминания не приходят.",
    "reminder.status.on": "🔔 <b>Включены</b> — {time} ({tz}) каждый день",
    "reminder.status.default": "🔔 <b>Включены</b> — 10:00 ({tz}, по умолчанию)",
    "reminder.status.on.desc": "Pepito напомнит тебе потренировать питомца.",
    "reminder.input.prompt": (
        "⏰ <b>Напоминания</b>\n\n"
        "Напиши время в формате <code>ЧЧ:ММ</code> в твоём часовом поясе (<b>{tz}</b>).\n"
        "Например: <code>09:00</code>, <code>18:30</code>\n\n"
        "<i>Часовой пояс можно изменить в ✏️ Редактировать профиль → 🌍 Часовой пояс.</i>"
    ),
    "reminder.disabled": (
        "🔕 <b>Отключены</b>\nТы больше не будешь получать ежедневные напоминания."
    ),
    "reminder.saved": "✅ <b>Готово!</b> Напоминание каждый день в <b>{time} ({tz})</b>.",
    "reminder.error.format": (
        "⚠️ Неверный формат. Введи время как <code>ЧЧ:ММ</code>, например <code>09:30</code>."
    ),
    "reminder.enable.btn": "🔔 Включить напоминания",
    "reminder.change.btn": "✏️ Изменить время",
    "reminder.disable.btn": "🔕 Отключить",
    "reminder.back.btn": "🔙 Назад к напоминаниям",
    "reminder.back_settings.btn": "🔙 Назад",
    "reminder.settings.btn": "⏰ К настройкам",
    "reminder.menu.btn": "🔙 В меню",
    "reminder.tz_missing": "⚠️ <b>Часовой пояс не задан</b> — используется UTC+0. Задай его, чтобы напоминания приходили в нужное время.",
    "reminder.tz_change.btn": "🌍 Задать часовой пояс",
    "reminder.push.friend": "друг",
    "reminder.push.text": "🐾 Привет, {name}!\n\nНе забудь про тренировку с питомцем сегодня. Открой /menu, чтобы посмотреть план.",
    "report.weekly.premium": (
        "📊 Еженедельный отчёт, {name}!\n\n"
        "Всего тренировочных дней: <b>{days}</b>\n"
        "Продолжай в том же духе! Открой /menu для деталей."
    ),
    "report.weekly.free": (
        "📊 Итоги недели, {name}!\n\n"
        "Тренировочных дней: <b>{days}</b>\n"
        "Для детальной аналитики оформи Premium — /menu."
    ),
    # ── Help / Support ─────────────────────────────────────────────────────────
    "help.guide.title": "❓ <b>Инструкция Pepito</b>\n\n",
    "help.guide.plan.header": "🧠 <b>Как работает план тренировок</b>\n",
    "help.guide.plan.text": (
        "Pepito генерирует план каждый день на основе профиля питомца. "
        "Нажми «🏋️ Тренировка на сегодня» — и получишь список задач.\n\n"
    ),
    "help.guide.streak.header": "✅ <b>Галочки и прогресс</b>\n",
    "help.guide.streak.text": (
        "Отмечай ○ → ✅ каждое упражнение. Когда выполнишь все — "
        "день засчитывается и счётчик тренировок растёт.\n\n"
    ),
    "help.guide.shop.header": "🛍️ <b>Магазин и награды</b>\n",
    "help.guide.shop.text": (
        "После тренировок Pepito рекомендует натуральные лакомства PepitoPet. "
        "Приглашай друзей — получай бонусы: +30, +60, +90 и +180 дней Premium за milestones.\n\n"
    ),
    "help.guide.premium.header": "⭐ <b>Что даёт Premium</b>\n",
    "help.guide.premium.text": (
        "💬 Безлимитные вопросы кинологу\n"
        "🧠 Глубокий AI-анализ прогресса\n"
        "🎁 Персональные рекомендации лакомств с именем питомца\n\n"
    ),
    "help.guide.commands": "<b>Команды:</b> /menu · /start · /reset",
    "help.support.btn": "💬 Написать в поддержку",
    "help.btn": "❓ Помощь",
    "help.back_settings.btn": "🔙 К настройкам",
    # ── Edit Profile ───────────────────────────────────────────────────────────
    "edit_profile.title": "✏️ <b>Редактирование профиля</b>\n\nЧто хочешь изменить?",
    "edit_profile.field.name.prompt": "Введи новое имя питомца прямо в чат:",
    "edit_profile.field.breed.prompt": "Введи новую породу прямо в чат:",
    "edit_profile.field.goal.prompt": "Напиши новую цель тренировок прямо в чат:",
    "edit_profile.field.level.prompt": "Выбери новый уровень послушания:",
    "edit_profile.field.age.prompt": "Выбери новую возрастную категорию:",
    "edit_profile.field.size.prompt": "Выбери новый размер питомца:",
    "edit_profile.field.timezone.prompt": "🌍 Выбери свой часовой пояс:",
    "edit_profile.saved": "✅ Обновлено: <b>{value}</b>",
    "edit_profile.edit_more.btn": "✏️ Изменить ещё",
    "edit_profile.error.empty": "⚠️ Поле не может быть пустым. Попробуй ещё раз.",
    "edit_profile.error.too_long": "⚠️ Слишком длинное значение — максимум 50 символов (у тебя {n}).",
    "edit_profile.btn.name": "🐾 Имя",
    "edit_profile.btn.breed": "🐕 Порода",
    "edit_profile.btn.goal": "🎯 Цель",
    "edit_profile.btn.level": "🎓 Уровень",
    "edit_profile.btn.age": "🎂 Возраст",
    "edit_profile.btn.size": "📏 Размер",
    "edit_profile.btn.timezone": "🌍 Часовой пояс",
    "edit_profile.cancel.btn": "🔙 Отмена",
    "edit_profile.level.1": "1 — Не знает команд",
    "edit_profile.level.2": "2 — Знает базовые (сесть, стоять)",
    "edit_profile.level.3": "3 — Слушается дома",
    "edit_profile.level.4": "4 — Слушается при отвлечениях",
    "edit_profile.level.5": "5 — Отлично обучен",
    "edit_profile.size.small": "Маленький (до 10 кг)",
    "edit_profile.size.medium": "Средний (10–25 кг)",
    "edit_profile.size.large": "Крупный (25–45 кг)",
    "edit_profile.size.giant": "Гигант (45+ кг)",
    "edit_profile.age.1": "Щенок (до 4 мес)",
    "edit_profile.age.2": "Щенок (4–12 мес)",
    "edit_profile.age.3": "Молодой (1–3 года)",
    "edit_profile.age.4": "Взрослый (3–7 лет)",
    "edit_profile.age.5": "Пожилой (7+ лет)",
}
