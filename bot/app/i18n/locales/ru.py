"""
Russian (ru) — source-of-truth locale.
All keys that exist in the system MUST be present here.
Other locales may omit keys; the fallback chain will reach ru.
"""

STRINGS: dict[str, str] = {
    # ── Main menu ──────────────────────────────────────────────────────────────
    "menu.main.greeting": "🐾 <b>Главное меню Pepito</b>",
    "menu.main.choose": "Выбери нужный раздел:",
    "menu.btn.training": "🏋️ Занятие",
    "menu.btn.week_plan": "📅 Неделя",
    "menu.btn.stats": "📊 Статистика",
    "menu.btn.coach": "💬 Кинолог",
    "menu.btn.profile": "🐶 Паспорт",
    "menu.btn.premium": "⭐ Premium",
    "menu.btn.premium.active": "⭐ Premium ✓",
    "menu.btn.shop": "🛒 Магазин",
    "menu.btn.invite": "🎁 Друзья",
    "menu.btn.webapp": "📱 Приложение",
    "menu.main.streak": "{emoji} Тренировок выполнено: <b>{n}</b>\n\n",
    "menu.main.streak.days.one": "день",
    "menu.main.streak.days.few": "дня",
    "menu.main.streak.days.many": "дней",
    # ── Common buttons ─────────────────────────────────────────────────────────
    "common.back_menu.btn": "🔙 В меню",
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
    "training.week.empty.cta.btn": "🏋️ Занятие",
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
        "Free-план: <b>{limit} AI-запроса в день</b>\n"
        "Лимит обновится в полночь по твоему времени.\n\n"
        "⭐ <b>Premium — без ограничений:</b>\n"
        "💬 Безлимитные вопросы кинологу\n"
        "🧠 Глубокий анализ прогресса\n"
        "🎁 Персональные рекомендации\n"
        "──────────"
    ),
    "ai.rate_limit.btn": "⭐ Premium",
    "ai.analyzing.premium": "🧠 <i>Провожу глубокий анализ...</i>",
    "ai.analyzing.free": "🧠 <i>Анализирую прогресс...</i>",
    "ai.progress.premium.header": "⭐ <b>Глубокий анализ прогресса {name}</b>\n\n",
    "ai.progress.free.header": "📈 <b>Анализ прогресса {name}</b>\n\n",
    "ai.progress.back.btn": "🔙 К статистике",
    "ai.retry.btn": "🔄 Ещё раз",
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
    "coach.new_thread.btn": "🆕 Новая тема",
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
    "stats.analysis.premium.btn": "🧠 AI Pro ⭐",
    "stats.analysis.free.btn": "🧠 Анализ AI",
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
    "profile.edit.btn": "✏️ Изменить",
    # ── Shop ───────────────────────────────────────────────────────────────────
    "shop.title": "🛒 <b>Магазин PepitoPet</b>",
    "shop.body": (
        "Натуральные лакомства собственного производства — "
        "без химии и консервантов, из настоящего мяса.\n\n"
        "Выбери категорию:"
    ),
    "shop.cat.training.btn": "🎯 Дрессировка",
    "shop.cat.longplay.btn": "🦴 Надолго",
    "shop.cat.by_size.btn": "🐶 По размеру",
    "shop.cat.all.btn": "🛒 Весь магазин",
    "shop.rec.puppy_named": "🐶 Лакомства для щенков — для {name}",
    "shop.rec.small_named": "🐶 Лакомства для маленьких пород — для {name}",
    "shop.rec.puppy_small_free": "🐶 Лакомства для щенков и малышей",
    "shop.rec.longplay_named": "🎁 Долгоиграющие лакомства — награда для {name}",
    "shop.rec.longplay_free": "🦴 Долгоиграющие лакомства",
    "shop.rec.exercise_named": "🦴 Лакомства для упражнений {name}",
    "shop.rec.training_named": "🦴 Лакомства для тренировок {name}",
    "shop.rec.training_free": "🦴 Лакомства для дрессировки",
    # ── Invite / Referral ──────────────────────────────────────────────────────
    "invite.title": "🐾 <b>Позови друга — бонус обоим!</b>",
    "invite.link_label": "🔗 Твоя ссылка:",
    "invite.bonus": "🎁 Каждый друг даёт <b>+{days} дня Premium</b> — тебе <i>и</i> ему.",
    "invite.ladder.title": "🏆 <b>Путь наград:</b>",
    "invite.count": "👥 Приглашено: <b>{n}</b>",
    "invite.next": "🎯 До следующей награды: ещё <b>{n}</b>",
    "invite.all_done": "👑 <b>Все награды получены! Ты легенда!</b>",
    "invite.share.btn": "📤 Поделиться",
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
    "premium.upsell.btn": "⭐ {price} Stars",
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
    "premium.paysupport": "💬 <b>Поддержка по оплате</b>\n\nОплатил, а Premium не пришёл? Или нужен возврат? Напиши в поддержку и приложи номер платежа из чата с Telegram. Ответим в течение суток.",
    "premium.terms": "📄 <b>Условия</b>\n\nPremium — это цифровая подписка на ИИ-кинолога Pepito. Оплата в Telegram Stars. Подписка продлевается сама, отменить можно в любой момент в настройках Telegram. Возврат — через /paysupport. Бот не заменяет ветеринара.",
    "premium.plan.premium_1m.btn": "1 мес · {stars}⭐",
    "premium.plan.premium_3m.btn": "3 мес · {stars}⭐",
    "premium.plan.premium_12m.btn": "12 мес · {stars}⭐",
    "premium.plans.btn": "Тарифы",
    "ai.remaining": "Осталось {n} из {limit} сегодня",
    "onboarding.q.name": "🐶 Привет! Я Pepito, твой кинолог. Как зовут собаку?",
    "onboarding.q.age": "Сколько <b>{name}</b> лет?",
    "onboarding.q.breed": "Какая порода? Выбери или пришли фото.",
    "onboarding.q.breed_text": "Напиши породу или пришли фото собаки 📷",
    "onboarding.q.goal": "Что хочешь прокачать?",
    "onboarding.photo.fail": "Не разглядел породу 🤔 Напиши её текстом.",
    "onboarding.photo.guess": "Похоже на: <b>{breed}</b>. Верно?",
    "onboarding.btn.other": "Другая",
    "onboarding.btn.photo": "📷 Фото",
    "onboarding.age.1": "До 4 мес",
    "onboarding.age.2": "4–12 мес",
    "onboarding.age.3": "1–3 года",
    "onboarding.age.4": "3–7 лет",
    "onboarding.age.5": "7+ лет",
    "onboarding.goal.1": "Послушание",
    "onboarding.goal.2": "Поведение",
    "onboarding.goal.3": "Щенок",
    "onboarding.goal.4": "Активность",
    "onboarding.name.need_text": "Напиши кличку текстом 🙂",
    "memory.btn": "🧠 Память",
    "memory.title": "🧠 <b>Что я помню о {name}</b>\n──────────",
    "memory.empty": "🧠 Пока ничего не помню о <b>{name}</b>. Расскажи в чате про собаку или добавь факт сам.",
    "memory.add.btn": "➕ Добавить",
    "memory.add.prompt": "Напиши факт о собаке одной фразой, например: «боится грома».",
    "memory.add.invalid": "Нужна фраза от 3 до 160 символов 🙂",
    "memory.deleted": "Удалил",
    "edit_profile.btn.weight": "⚖️ Вес",
    "edit_profile.btn.birth": "🎂 Рождение",
    "edit_profile.btn.allergies": "🚫 Аллергии",
    "edit_profile.btn.chronic": "🩺 Хроника",
    "edit_profile.field.weight.prompt": "Напиши вес в кг, например: 12,5",
    "edit_profile.field.birth.prompt": "Напиши дату рождения: 31.12.2023",
    "edit_profile.field.allergies.prompt": "Перечисли аллергии через запятую или напиши «нет»",
    "edit_profile.field.chronic.prompt": "Перечисли хронические состояния через запятую или напиши «нет»",
    "edit_profile.error.invalid": "Не получилось разобрать. Проверь формат и попробуй ещё раз.",
    "profile.allergies": "🚫 Аллергии: {val}\n",
    "profile.chronic": "🩺 Хроника: {val}\n",
    "menu.btn.health": "🩺 Здоровье",
    "health.title": "🩺 <b>Здоровье {name}</b>\n──────────",
    "health.kind.vaccine": "Прививка",
    "health.kind.ticks": "Клещи",
    "health.kind.worms": "Глисты",
    "health.row.none": "{kind}: не отмечено",
    "health.row.overdue": "{kind}: ⚠️ просрочено на {n} дн.",
    "health.row.today": "{kind}: ❗ сегодня",
    "health.row.soon": "{kind}: ⏳ через {n} дн. ({date})",
    "health.row.later": "{kind}: ✅ до {date}",
    "health.add.prompt": "Когда делали: {kind}?",
    "health.btn.today": "Сегодня",
    "health.btn.date": "Дата",
    "health.btn.back": "🔙 Назад",
    "health.date.prompt": "Напиши дату в формате 31.10.2026",
    "health.date.invalid": "Не разобрал дату. Нужна прошедшая дата вида 31.10.2026.",
    "health.saved": "✅ Записал: {kind}. Следующий раз — {date}.",
    "health.push.soon": "🔔 {name}: {kind} — через {n} дн. ({date})",
    "health.push.today": "🔔 {name}: сегодня срок — {kind}",
    "health.btn.done": "✅ Сделано",
    "health.btn.snooze": "⏰ +3 дня",
    "health.snoozed": "Ок, напомню {date}.",
    "menu.btn.tracker": "🔥 Трекер",
    "tracker.title": "🔥 <b>Трекер {name}</b>\n──────────",
    "tracker.streak": "Стрик: <b>{n}</b> дн. подряд",
    "tracker.streak.zero": "Стрик: пока 0. Займись сегодня — и он пойдёт!",
    "tracker.today.done": "Сегодня: ✅ уже есть",
    "tracker.today.todo": "Сегодня: ещё не занимались",
    "tracker.freezes": "🧊 Заморозок на неделе: {n}",
    "tracker.week": "Неделя: тренировок {days}, прогулок {walks} ({minutes} мин)",
    "tracker.badges": "Ачивки: {list}",
    "tracker.walk.btn": "🚶 {m} мин",
    "tracker.walk.saved": "Записал прогулку: {m} мин",
    "tracker.badge.new": "🎉 Новая ачивка: {badge}",
    "tracker.badge.streak_7": "🔥7 дней",
    "tracker.badge.streak_30": "⚡30 дней",
    "tracker.badge.streak_100": "🏆100 дней",
    "tracker.badge.walks_10": "🚶10 прогулок",
    "report.weekly.stats": "📊 <b>Итоги недели, {name}</b>\n\n🐶 {pet}\n🏋️ Тренировок: {days}\n🚶 Прогулок: {walks} ({minutes} мин)\n🔥 Стрик: {streak} дн.\n\nОтличная работа! В понедельник новый план.",
    "menu.btn.more": "⚙️ Ещё",
    "menu.more.title": "Выбери раздел 👇",
    "media.verdict.vet_now": "🚨 <b>К ветеринару сегодня</b>",
    "media.verdict.vet_soon": "⚠️ <b>Покажи ветеринару в ближайшие дни</b>",
    "media.verdict.see": "🎯 <b>Что вижу:</b>",
    "media.verdict.steps": "🛠 <b>Что делать:</b>",
    "media.verdict.disclaimer": "<i>Это не диагноз и не замена ветеринара.</i>",
    "card.unit.streak": "дней подряд",
    "card.headline.streak": "{pet} не пропускает тренировки",
    "card.badge.caption": "Новая ачивка",
    "card.week.caption": "тренировок за неделю",
    "card.row.walks": "Прогулок",
    "card.row.minutes": "Минут на прогулках",
    "card.row.streak": "Стрик, дней",
    "card.row.age": "Возраст",
    "card.row.weight": "Вес",
    "card.row.allergies": "Аллергии",
    "card.unit.kg": "кг",
    "card.passport.caption": "Паспорт собаки",
    "card.nothing": "Пока нечем поделиться. Позанимайся сегодня — и карточка появится!",
    "card.drawing": "Рисую карточку…",
    "card.error": "Не получилось нарисовать карточку. Попробуй чуть позже.",
    "card.caption": "Держи! Выкладывай в Stories 🐶",
    "tracker.card.streak.btn": "📤 Стрик",
    "tracker.card.week.btn": "📤 Неделя",
    "tracker.card.badge.btn": "📤 Ачивка",
    "profile.card.btn": "📤 Карточка",
    "nudge.renew.soon": "⏳ Premium закончится через {n} дн. ({date}). Продлить, чтобы у {pet} не пропали безлимит и память?",
    "nudge.renew.last": "⏳ Завтра ({date}) заканчивается Premium. Продли, чтобы не терять безлимит и память о {pet}.",
    "nudge.renew.btn": "⭐ Продлить",
    "nudge.evening": "🔥 Стрик {n} дн. — сегодня с {pet} ещё не занимались. 5 минут, и он живёт!",
    "nudge.season.ticks": "🕷 {pet}: начался сезон клещей. Осматривай после каждой прогулки и не забудь про обработку — отметь её в «Здоровье».",
    "nudge.season.heat": "☀️ Жара! Гуляй с {pet} утром и вечером, давай больше воды, а асфальт проверяй ладонью — лапы горят быстро.",
    "nudge.season.reagents": "🧂 Зима и реагенты: мой лапы {pet} после прогулки и смазывай защитным воском.",
    "nudge.winback": "👋 {pet} скучает по занятиям. С Premium снова будут безлимитные вопросы, память о собаке и карточки. Вернёшься?",
    "nudge.winback.btn": "⭐ Вернуться",
    "settings.seasonal.on": "🌦 Сезон: вкл",
    "settings.seasonal.off": "🌦 Сезон: выкл",
    "settings.seasonal.toast.on": "Сезонные советы включены",
    "settings.seasonal.toast.off": "Сезонные советы выключены",
    "profile.pdf.btn": "📄 Ветеринару",
    "pdf.drawing": "Собираю PDF…",
    "pdf.caption": "Паспорт для ветеринара. Данные со слов владельца — покажи врачу на приёме.",
    "pdf.passport.title": "Pepito — паспорт собаки",
    "pdf.passport.profile": "Профиль",
    "pdf.passport.breed": "Порода",
    "pdf.passport.sex": "Пол",
    "pdf.passport.age": "Возраст",
    "pdf.passport.birth": "Дата рождения",
    "pdf.passport.weight": "Вес",
    "pdf.passport.kg": "кг",
    "pdf.passport.health": "Здоровье",
    "pdf.passport.allergies": "Аллергии",
    "pdf.passport.chronic": "Хронические состояния",
    "pdf.passport.notes": "Заметки",
    "pdf.passport.schedule": "Прививки и обработки",
    "pdf.passport.last": "сделано",
    "pdf.passport.next": "следующее",
    "pdf.passport.history": "История",
    "pdf.passport.facts": "Что известно о собаке",
    "pdf.passport.disclaimer": "Составлено {date} в Pepito (@pepitopetbot) по данным владельца. Это не медицинский документ.",
    "voice_action.walk": "🚶 Записал прогулку: {m} мин. Стрик: {n} дн.",
    "pets.add.btn": "➕ Собака",
    "pets.limit.free": "🐶 На Free одна собака. В Premium можно до {n} — у каждой свой паспорт, план и память.",
    "pets.limit.max": "Максимум {n} собаки.",
    "pets.switched": "Теперь работаем с {name}",
    "pets.added": "🐶 {name} добавлена! Составляю первый план…",
    "pets.locked": "Эта собака доступна в Premium (до {n} собак). Данные сохранены.",
    "gift.btn": "🎁 Подарить",
    "gift.choose": "🎁 Подари Premium другу. Выбери срок:",
    "gift.ask_username": "Напиши @username друга. Он уже должен пользоваться ботом.",
    "gift.notfound": "Не нашёл такого пользователя. Друг должен сначала запустить бота, потом пришли @username ещё раз.",
    "gift.self": "Себе подарок не получится 🙂 Пришли @username друга.",
    "gift.invoice.title": "Подарок: Premium",
    "gift.invoice.description": "Premium для {name} на {days} дн.",
    "gift.sent": "🎁 Готово! {name} получил(а) Premium на {days} дн.",
    "gift.received": "🎁 Тебе подарили Premium на {days} дн.! Безлимит вопросов, память и карточки уже работают.",
    "weight.btn": "⚖️ Вес",
    "weight.empty": "⚖️ Веса <b>{name}</b> пока нет в журнале.",
    "weight.title": "⚖️ <b>{name}</b>: {kg} кг",
    "weight.change": "За месяц: {delta} кг ({pct}%), было {prev} кг",
    "weight.alert.gain": "⚠️ Вес вырос больше чем на 10% за месяц. Покажи собаку ветеринару.",
    "weight.alert.loss": "⚠️ Вес упал больше чем на 10% за месяц. Покажи собаку ветеринару.",
    "weight.ask": "Пришли новый вес в кг, например 12,5",
    "weight.saved": "✅ Записал: {kg} кг",
    "weight.nudge": "⚖️ Пора взвесить {pet}: раз в месяц достаточно. Это 10 секунд.",
    "premium.refunded": (
        "✔ Возврат средств обработан. Подписка Premium деактивирована.\n"
        "Если это ошибка — обратись в поддержку."
    ),
    "webapp.validation.name_empty": "Имя не может быть пустым",
    "webapp.validation.name_long": "Имя не более 30 символов",
    "webapp.validation.breed_long": "Порода не более 40 символов",
    "webapp.validation.goal_long": "Цель не более 150 символов",
    "webapp.validation.level": "Недопустимый уровень",
    "webapp.validation.age": "Недопустимый возраст",
    "webapp.validation.reminder": "Формат: ЧЧ:ММ, например 09:30",
    "webapp.validation.timezone": "Недопустимый часовой пояс",
    "webapp.validation.language": "Недопустимый язык",
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
    "reminder.enable.btn": "🔔 Включить",
    "reminder.change.btn": "✏️ Время",
    "reminder.disable.btn": "🔕 Отключить",
    "reminder.back.btn": "🔙 Назад",
    "reminder.back_settings.btn": "🔙 Назад",
    "reminder.settings.btn": "⏰ К настройкам",
    "reminder.menu.btn": "🔙 В меню",
    "reminder.tz_missing": "⚠️ <b>Часовой пояс не задан</b> — используется UTC+0. Задай его, чтобы напоминания приходили в нужное время.",
    "reminder.tz_change.btn": "🌍 Пояс",
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
    "help.support.btn": "💬 Поддержка",
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
    "edit_profile.edit_more.btn": "✏️ Ещё",
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
