# CLAUDE.md — pepito/bot (@pepitopetbot)

## Sandbox Rules (ОБЯЗАТЕЛЬНО)
- Runtime: **podman** и **podman-compose** ТОЛЬКО
- Python: **uv** ТОЛЬКО (`uv run`, `uv add`)
- **НИКОГДА:** `apt install`, `pip install` (глобально), `docker`
- Scope: только `/root/pepito/` — не трогать другие проекты

## Mode Declarations (объявлять в каждом ответе)
- `[REVIEW MODE]` / `[DESIGN MODE]` / `[BUILD MODE]` / `[PATCH MODE]`

## Hook Pipeline (глобальный, всегда активен)
- PreToolUse:Bash → `safety_guard.py` (блокирует деструктивные команды)
- PreToolUse:Write/Edit → `skill_vetter.py` (аудит кода)
- PostToolUse → `run_pytest.sh` + `stuck_detector.py`

---

## Autoresearch Workflow

Подробная документация — в `autoresearch.md`. Здесь — краткая операционная памятка.

### Цикл изменений

```
propose → patch → ./judge.sh → keep (commit) / discard (git checkout)
```

### Запуск judge

```bash
./judge.sh                    # лог → artifacts/judge-<timestamp>.log
./judge.sh my-artifacts-dir   # кастомный каталог логов
```

Judge проверяет:
1. Синтаксис Python (`py_compile` всех `app/**/*.py`)
2. Import smoke-check ключевых модулей (без DB/Redis)
3. Наличие обязательных env-var в `config.py`
4. Pytest unit/smoke-тесты (`tests/` без `tests/e2e/`)
5. Наличие критических файлов проекта

**Exit 0** — изменение принято, можно коммитить.
**Exit != 0** — откатить: `git checkout -- <changed files>`, причину записать в `artifacts/`.

### Зоны ответственности

**Human-owned** (агент не трогает без явного разрешения):
- `alembic/`, `alembic.ini` — миграции необратимы
- `podman-compose.yml`, `Containerfile` — инфраструктура
- `.env` — секреты
- `app/infrastructure/db/` — модели связаны с миграциями

**Agent-owned** (агент предлагает и применяет):
- `app/bot/handlers/`, `app/bot/keyboards/` — UX
- `app/services/` — бизнес-логика
- `app/core/shop.py`, `app/core/shop_recommendations.py`
- `tests/`, `artifacts/`, `autoresearch.md`, `judge.sh`

### Rollout-сценарий

```
1. Baseline → ветка stable-YYYY-MM-DD (уже есть: stable-2026-04-20)
2. Рабочая ветка от master (например instructions-v2, feature/*)
3. Изменить только agent-owned файлы
4. ./judge.sh                      # должен дать exit 0
5. exit 0 → git commit → PR в master
6. exit != 0 → git checkout -- .   → artifacts/FAILED-<date>.md
```

### E2E Telegram тесты

Scaffold готов в `tests/e2e/DESIGN.md`.
Рекомендуемый подход: **Telethon user simulation** (headless, без браузера, подходит для VDS).
Статус: design only, полная реализация — в backlog.

---

## Running the Bot (локальная разработка)

```bash
podman-compose up -d --build   # первый запуск: поднять PostgreSQL, Redis, bot
podman logs -f pepito-bot_bot_1
python -m app.main             # запустить бота напрямую (сервисы должны быть запущены)
```

Migrations (Alembic):
```bash
alembic upgrade head                            # применить все миграции
alembic revision --autogenerate -m "description"  # создать новую миграцию
```

---

## Deployment

### Рекомендуемый сценарий деплоя (каждый раз при изменении кода)

```bash
# 1. Остановить и удалить старый контейнер бота (БД и Redis не трогать)
podman rm -f pepito-bot_bot_1

# 2. Применить миграции вручную, пока контейнер не запущен
#    (избегает гонки между стартом и alembic upgrade head внутри start.sh)
podman run --rm \
  --env-file /root/pepito/bot/.env \
  --net pepito-bot_default \
  localhost/pepito-bot_bot:latest \
  alembic upgrade head

# 3. Пересобрать образ и поднять контейнер
podman-compose up -d --build

# 4. Убедиться, что бот стартовал
podman logs -f pepito-bot_bot_1
```

> **Почему именно так:** `podman-compose up -d --build` при конфликте имён (`container name already in use`) может запустить **старый** контейнер вместо нового. `podman rm -f` перед `up` гарантирует, что поднимется именно новый образ.

### Быстрый hot-restart (без смены образа)

```bash
podman restart pepito-bot_bot_1
podman logs -f pepito-bot_bot_1
```

### Как понять, что бот успешно стартовал

В логах должно появиться (в таком порядке):

```
Waiting for databases to boot...
Running migrations...
INFO  [alembic.runtime.migration] ...   ← миграции применяются или пропускаются
Starting bot...
INFO - Starting bot...
INFO - Start polling
INFO - Run polling for bot @<username> id=<id> - '<name>'
```

Если последняя строка есть — бот принимает апдейты. Проверить статус контейнера:

```bash
podman ps --filter name=pepito-bot
# ожидаемый статус: Up X minutes (не Restarting)
```

### Дрейф alembic_version (DuplicateColumn и аналогичные ошибки)

**Симптом:** бот уходит в cyclic restart, в логах:
```
sqlalchemy.exc.ProgrammingError: column "X" of relation "Y" already exists
```

**Причина:** колонка уже есть в БД, но `alembic_version` отстаёт — миграция пытается добавить её повторно.

**Диагностика:**
```bash
# посмотреть текущую версию в БД
podman exec pepito-bot_db_1 psql -U pepito -d pepito_db \
  -c "SELECT version_num FROM alembic_version;"

# посмотреть head в файлах
podman exec pepito-bot_bot_1 alembic heads
```

**Лечение** (если структура БД уже соответствует моделям):
```bash
# пометить БД как актуальную без выполнения миграций
podman exec pepito-bot_bot_1 alembic stamp head

# перезапустить бота
podman restart pepito-bot_bot_1
podman logs -f pepito-bot_bot_1
```

**Профилактика:** всегда деплоить через `podman rm -f` → `alembic upgrade head` → `podman-compose up -d --build`, а не через `podman restart` после смены образа.

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `BOT_TOKEN` | ✅ | Telegram bot token |
| `GEMINI_API_KEY` | ✅ | Google AI API key |
| `DATABASE_URL` | ✅ | `postgresql+asyncpg://...` |
| `REDIS_URL` | ✅ | Redis URL for FSM state |
| `ADMIN_TELEGRAM_IDS` | ✅ | Comma-separated telegram_id of admins |
| `APP_ENV` | — | `development` / `production` |
| `LOG_LEVEL` | — | `INFO` / `DEBUG` |

## Architecture

```
Telegram (aiogram handlers + FSM)
         ↓
   Middlewares (DbSessionMiddleware)
         ↓
   Services Layer (UserService, PetService, AiService)
         ↓
   Repositories (SQLAlchemy async)
         ↓
   PostgreSQL + Redis (FSM state)
         ↑
   Scheduler (APScheduler — reminders, reports)
```

**DI**: `dependency-injector` — handlers use `@inject` + `Provide[AppContainer.x]`. Container wired in `main.py`.

**FSM**: aiogram + Redis backend. States in `app/bot/states/`. Use `state.set_state()` / `state.update_data()` / `state.get_data()`.

**Sessions**: `DbSessionMiddleware` (`app/bot/middlewares/db.py`) opens one `AsyncSession` per update via ContextVar and closes it after. Repos share the same session within a request.

## Project Structure

```
app/
  core/          — config.py, container.py, shop.py, shop_recommendations.py
  domain/        — enums, value objects
  services/      — UserService, PetService, AiService, SubscriptionService, ReferralService
  infrastructure/
    db/          — SQLAlchemy models + repositories
    redis/       — FSM / cache helpers, AiRateLimiter
    payments/    — Telegram Stars / invoices
  bot/
    handlers/    — aiogram routers (menu, onboarding, edit_profile, subscription, admin)
    keyboards/   — inline keyboards (main_menu, training, edit_profile)
    states/      — FSM state groups
    middlewares/ — DbSessionMiddleware
  scheduler/     — APScheduler jobs (reminders, weekly reports, expire_subscriptions)
  main.py        — entry point
```

## Data Model

**User**: `id`, `telegram_id`, `username`, `first_name`, `language_code`, `timezone`, `is_premium`, `subscription_expires_at`, `onboarding_completed_at`, `current_stage`, `reminder_time`, `referrer_telegram_id`, `referral_bonus_given`, `created_at`, `updated_at`

**Pet**: `id`, `user_id`, `name`, `breed`, `sex`, `age_category`, `age_months`, `size_category`, `weight_kg`, `training_level`, `temperament`, `behavior_issues`, `goal`, `energy_level`, `health_notes`, `training_days`, `training_schedule`, `created_at`, `updated_at`

**TrainingPlan**: `id`, `user_id`, `pet_id`, `title`, `goal`, `week_number`, `plan_json`, `is_active`, `created_at`

**TrainingTask**: `id`, `plan_id`, `day_of_week`, `title`, `description`, `duration_minutes`, `difficulty`, `is_completed`, `completed_at`

**AiConversation**: `id`, `user_id`, `pet_id`, `question`, `answer`, `topic`, `created_at`

**Subscription**: `id`, `user_id`, `plan_code`, `status`, `provider`, `telegram_payment_charge_id`, `starts_at`, `expires_at`

## AI Layer

**Model**: `gemini-2.5-flash-lite` — задан в `_MODEL` в `app/services/ai_service.py`.

⚠️ Модели семейства `gemini-2.0-*` на текущем API-ключе исчерпали free-tier квоту (429). Если ключ заменить — можно вернуться к `gemini-2.0-flash-lite` (дешевле). Текущий ключ имеет доступ к preview-моделям (`gemini-3.x`) и `gemini-2.5-*`.

**Use cases**: `generate_training_plan`, `generate_week_plan`, `answer_coach_question`, `explain_exercise`, `summarize_progress`, `premium_deep_analysis`.

**Rate limiting**: `AiRateLimiter` в `app/infrastructure/redis/ai_rate_limit.py`. Free: 5 запросов/день, сброс в полночь UTC. Premium: безлимит. Guard применён во всех AI-хэндлерах в `menu.py`.

**Guardrails**: не давать ветеринарных диагнозов; ограничить длину входящих сообщений (1000 символов); не хранить токены в логах.

## Main Menu Structure

Текущая структура `get_main_menu()` (`app/bot/keyboards/main_menu.py`):

```
[ 🏋️ Тренировка на сегодня          ]  ← главный CTA, полная ширина
[ 📊 Статистика    ][ 💬 Вопрос кинологу ]
[ 🐶 Мой питомец  ][ ⏰ Напоминания      ]
[ ⭐ Premium       ][ 🛒 Магазин          ]
[ 🐾 Позови друга — бонус!            ]  ← полная ширина
```

**Редактирование профиля** — кнопка "✏️ Изменить профиль" находится внутри экрана "🐶 Мой питомец", не в главном меню.

⚠️ **Недельный план** — хэндлер `menu_week_plan` реализован и работает, но кнопки входа в него из главного меню нет. Доступен только если добавить кнопку вручную.

## User Roles

- **User** — обычный пользователь
- **Premium** — расширенные AI-функции, персональные рекомендации магазина, безлимитный AI
- **Admin** — `ADMIN_TELEGRAM_IDS`; рассылки, `/grant_premium`, статистика пользователей

---

## Roadmap

### Реализовано (полный список)

**Онбординг и профиль**
- [x] Онбординг (FSM, 10 шагов, профиль питомца)
- [x] После онбординга — автоматическая генерация первого плана
- [x] Редактирование профиля питомца (FSM, 6 полей, кнопка внутри "Мой питомец")

**Тренировки**
- [x] Ежедневные планы (AI-генерация, toggle-задачи, streak, кнопка 🔄 Новый план)
- [x] Недельный план 7 дней (навигация ◀/▶ по дням, toggle-задачи) — ⚠️ нет кнопки входа в главном меню
- [x] Объяснение упражнения — кнопка ℹ️ у каждой задачи → `explain_exercise` через AI

**AI-кинолог**
- [x] Вопросы кинологу с историей диалога, сохранение в `AiConversation`
- [x] Rate limiting: free 5/день, premium безлимит (Redis, сброс в полночь UTC)
- [x] Мультимодальность: 📷 фото бесплатно (−1 запрос), 🎤 голос + 🎥 видео — только Premium; inline bytes → Gemini `types.Part.from_bytes()`
- [x] Статистика + AI-анализ прогресса (free / premium-версии с разной глубиной)

**Подписка и монетизация**
- [x] Подписка Telegram Stars (UI, инвойс, активация, `is_premium`)
- [x] Автоматическое истечение подписки — scheduler-job `expire_subscriptions` (00:05 UTC)
- [x] Возврат средств (refund) — обработчик `F.refunded_payment`, снятие premium

**Магазин PepitoPet**
- [x] Раздел /shop: экран с 4 кнопками (3 категории + весь магазин), UTM-трекинг
- [x] Контекстные рекомендации: после плана (AFTER_PLAN), после завершения дня (AFTER_COMPLETION), после explain_exercise (AFTER_EXERCISE)
- [x] Rule-based персонализация: щенок/маленький → by_size, завершение → longplay, остальное → training
- [x] Premium: персональный текст с именем питомца; Free: общий текст категории
- [x] `app/core/shop.py` — URL и UTM; `app/core/shop_recommendations.py` — логика
- ⚠️ Точные URL тег-фильтров pepitopet.ru не проверены — обновить в `shop.py` после уточнения

**Рефералы**
- [x] Deep link `/start ref_XXX` — сохранять referrer при первом запуске
- [x] Реферальный бонус +3 дня premium обоим после завершения онбординга (double-sided)
- [x] Антифрод: self-referral, повтор (флаг `referral_bonus_given`), дневной лимит 10
- [x] Экран "Позови друга": личная ссылка + счётчик + прогресс до следующего уровня
- [x] Milestone-награды за 3/5/10/25 рефералов (+7/14/30/90 дней), идемпотентность через `SubscriptionModel`

**Напоминания и scheduler**
- [x] APScheduler: ежедневные напоминания (каждую минуту, фильтр по `reminder_time`, дефолт 10:00 UTC)
- [x] APScheduler: еженедельные отчёты (вс 18:00 UTC)
- [x] Персональное время напоминаний — поле `reminder_time` HH:MM UTC, настройка через меню

**Admin**
- [x] Admin-панель `/admin`: рассылка, статистика пользователей
- [x] `/grant_premium <telegram_id> <days>` — выдать premium вручную

**UX / Меню**
- [x] Главное меню переработано: 5 строк, Premium и Магазин в одной строке, без кнопки "Изменить" на главном экране
- [x] Редактирование профиля перенесено внутрь экрана "Мой питомец"

### Следующие задачи

**Критично перед показом**
- [x] ✅ Вернуть доступ к недельному плану — кнопка добавлена в главное меню (Stage 4)
- [ ] ⚠️ Проверить и обновить URL тег-фильтров pepitopet.ru в `app/core/shop.py`

**Stage 5 — Production (выполнено 2026-04-23)**
- [x] ✅ Web App Dashboard (`app/webapp/`) — задеплоен на `https://bot.pepitopet.ru`
- [x] ✅ Nginx Proxy Manager + SSL, bridge-сеть `npm_network`, без открытых портов
- [x] ✅ Локализация (i18n) — RU, EN, DE 🇩🇪, FR 🇫🇷, ES 🇲🇽, PT 🇧🇷 (uk/et удалены)
- [x] ✅ Web App guard — защита от открытия вне Telegram (initData check)
- [x] ✅ DNS-конфликт `db` на npm_network — DATABASE_URL переведён на `pepito-bot_db_1`
- [x] ✅ Scheduler ошибки устранены — send_daily_reminders работает чисто

**Stage 6 — Secret Admin Dashboard (выполнено 2026-04-23)**
- [x] ✅ Секретный таб "👑 Админка" в Web App — виден только основателю (`ADMIN_TELEGRAM_IDS`)
- [x] ✅ Бэкенд: `is_admin` + `admin_stats` добавляются в `/api/dashboard` только для админа; ключ физически отсутствует в ответах обычным пользователям
- [x] ✅ Фронтенд: весь HTML таба создаётся через `createElement` после проверки `is_admin === true`; в исходнике `index.html` нет ни одного admin-тега
- [x] ✅ Метрики: Total Users, Premium Users, Referrals Given (SQL COUNT)
- [x] ✅ UI: тёмный фон, gold + neon-purple акценты, пульсирующая корона, кнопка "📣 Broadcast" (активирована в Stage 8)

**Stage 7 — Hands-Free Voice-to-Action (выполнено 2026-04-23)**
- [x] ✅ Хэндлер `handle_voice_action` — `StateFilter(default_state)`, перехватывает TEXT/VOICE/PHOTO вне FSM
- [x] ✅ Gemini structured JSON: `detect_training_intent` определяет намерение — отчёт о выполнении (`mark_done`) или вопрос кинологу (`none`)
- [x] ✅ Промпт с `language_code` — AI отвечает строго на языке пользователя (RU/EN/DE/FR/ES/PT)
- [x] ✅ `mark_task_by_hint` — fuzzy-матч по названию задачи, fallback на первую невыполненную
- [x] ✅ Premium gating: voice/photo отчёты — бесплатно; voice/photo вопросы кинологу — только Premium
- [x] ✅ Фото без подписи → AI хвалит питомца, `action: none`
- [x] ✅ `_is_fallback: True` сигнал когда JSON от AI не распарсился

**Stage 7.1 — Observability Metrics (выполнено 2026-04-23)**
- [x] ✅ `BotMetrics` — новый Redis-класс, ключи `pepito:metrics:va_*` (не пересекаются с FSM)
- [x] ✅ Три счётчика: `va_mark_done`, `va_premium_gate`, `va_fallback` — кумулятивные, без TTL
- [x] ✅ Singleton в DI-контейнере, проброшен в aiohttp через `request.app["metrics"]`
- [x] ✅ Admin dashboard расширен: вторая строка карточек "🎤 Voice-to-Action" в секретной админке

**Stage 7.2 — Timezone-Aware Reminders (выполнено 2026-04-23)**
- [x] ✅ `app/core/tz_utils.py` — `local_to_utc`, `utc_to_local`, `_parse_offset`; 8 unit-тестов
- [x] ✅ Scheduler rewrite: SQL OR по всем UTC-12…UTC+14 смещениям вместо Python-цикла (O(N) → SQL WHERE)
- [x] ✅ `_VALID_TIMEZONES` расширен до UTC-12…UTC+14 в `routes.py`; Webapp: дропдаун из 27 пунктов с городами
- [x] ✅ `reminder_time` в БД хранит **местное** время пользователя (исправлен комментарий в `user.py`)
- [x] ✅ Webapp: убран "(UTC)" из лейбла, подсказка "Местное время — в выбранном часовом поясе ниже"

**Stage 8 — Admin Broadcast (выполнено 2026-04-23)**
- [x] ✅ `app/services/broadcast_service.py` — `run_broadcast()`: 0.05 с задержка между отправками (~20 msg/s)
- [x] ✅ `TelegramForbiddenError` → тихий skip; `TelegramRetryAfter` → `sleep(retry_after)` + один повтор
- [x] ✅ По завершении рассылки — отчёт администратору в личку: sent / failed
- [x] ✅ `POST /api/broadcast`: admin-only, DB-сессия закрыта до `asyncio.create_task` (нет утечки)
- [x] ✅ Webapp: кнопка активна — `prompt()` → `confirm()` → POST → `showAlert` с числом получателей
- [x] ✅ 4 unit-теста: all-success, forbidden-skip, retry-after, empty-list

**Backlog — приоритизировано**

*P1 — влияет на retention*
- [x] ✅ **Onboarding progress bar** — N/A: онбординг переведён на AI-driven flow (2 состояния, не 10 шагов). "Шаг N из M" не применимо.

*P2 — продуктовые улучшения*
- [x] ✅ **Статистика рефералов в /admin** — кнопка "🔗 Рефералы" в /admin, топ-5 рефереров + итого.
- [ ] **Shop URL тег-фильтров pepitopet.ru** — уточнить точные URL у команды и обновить `app/core/shop.py`

*P3 — UX-полировка*
- [x] ✅ **Подтверждение "🔄 Новый план"** — `refresh_confirm` callback, inline [Да]/[Нет].
- [ ] **Кулдаун на shop-кнопку** — показывается повторно при каждом открытии плана. Redis TTL 1ч.
- [x] ✅ **Кнопка "Новый вопрос" в кинологе** — `_coach_reply_keyboard()`: кнопка "🆕 Новая консультация" после каждого ответа AI.

---

## Shop Integration

**Магазин**: pepitopet.ru — тот же бренд что и бот. Только лакомства (говядина), нет аксессуаров.

**UTM-схема**:
```
utm_source=pepito_bot&utm_medium=telegram&utm_campaign=<context>
```

**Правила рекомендаций** (`app/core/shop_recommendations.py`):
- Щенок или маленькая порода → `SHOP_URL_BY_SIZE`
- Завершение дня/плана → `SHOP_URL_LONGPLAY`
- Всё остальное → `SHOP_URL_TRAINING`
- Premium: персональный текст с именем питомца
- Максимум 1 рекомендация за сценарий, не блокирует основной флоу

---

## Referral & Growth

**Механика**: `https://t.me/<bot>?start=ref_<telegram_id>` → бонус обоим после онбординга.

**Константы** в `referral_service.py`:
- `REFERRAL_BONUS_DAYS = 3`
- `REFERRAL_DAILY_LIMIT = 10`
- `REFERRAL_MILESTONES = [3→+7д, 5→+14д, 10→+30д, 25→+90д]`

**Антифрод**: self-referral игнорируется, флаг `referral_bonus_given`, дневной лимит через подсчёт записей в `SubscriptionModel`.

---

## Release Checklist

Перед показом живым пользователям пройти по всем пунктам:

### 1. Инфраструктура
- [ ] `.env` на проде содержит все 5 обязательных переменных (`BOT_TOKEN`, `GEMINI_API_KEY`, `DATABASE_URL`, `REDIS_URL`, `ADMIN_TELEGRAM_IDS`)
- [ ] Деплой выполнен по рекомендуемому сценарию: `podman rm -f` → `alembic upgrade head` → `podman-compose up -d --build`
- [ ] `podman ps` показывает три контейнера в статусе `Up` (db, redis, bot) — ни один не `Restarting`
- [ ] В логах бота есть строка `Run polling for bot @<username>` — нет ERROR/Traceback
- [ ] `alembic_version` в БД совпадает с `alembic heads` (нет дрейфа)

### 2. Конфигурация AI
- [ ] Модель в `app/services/ai_service.py` (`_MODEL`) отвечает на тестовый запрос (проверить через `podman exec ... python3 -c "..."`)
- [ ] При превышении квоты AI возвращает человекочитаемое сообщение, а не traceback
- [ ] Rate limiting работает: 6-й запрос у free-пользователя блокируется

### 3. Контент и ссылки
- [ ] URL в `app/core/shop.py` открываются в браузере (не 404, не редиректят на главную)
- [ ] ⚠️ Точные URL тег-фильтров pepitopet.ru уточнить у команды и обновить в `shop.py`
- [ ] Реферальная ссылка вида `https://t.me/<bot>?start=ref_<id>` ведёт на бота
- [ ] Нет текстов с "TODO", "заглушка", "PLACEHOLDER" в хэндлерах

### 4. Монетизация
- [ ] Telegram Stars invoice открывается корректно
- [ ] После оплаты `is_premium = True` (проверить: `/grant_premium <id> 1` → статус в меню)
- [ ] Кнопка Premium меняет label на "⭐ Premium (активен)" сразу после активации
- [ ] Scheduler `expire_subscriptions` настроен на 00:05 UTC (есть в логах APScheduler при старте)

### 5. Smoke test
- [ ] Пройден полностью smoke test checklist ниже (все пункты без блокеров)

### 6. Известные ограничения (не блокеры, но задокументировать)
- [x] ✅ Статистика рефералов в `/admin` — реализована (кнопка "🔗 Рефералы")
- [ ] Shop URL тег-фильтров pepitopet.ru — не верифицированы командой

---

## Smoke Test (Telegram, вручную)

Проверять на **двух аккаунтах**: основной (A) и второй (B) для реферального теста.

### Onboarding
- [ ] `/start` на новом аккаунте → запускается онбординг, не меню
- [ ] Все 10 шагов FSM проходятся без зависания
- [ ] После последнего шага → автоматически показывается первый план тренировки (не просто "готово")
- [ ] `/start ref_<id_A>` от аккаунта B → после онбординга B оба получают уведомление о +3 днях premium

### Меню
- [ ] `/menu` → 5 строк кнопок, нет кнопки "Изменить" на главном экране
- [ ] Все 8 кнопок открывают нужный экран, ни одна не даёт ошибку
- [ ] "🐶 Мой питомец" → анкета питомца + кнопки "✏️ Изменить профиль" и "🔙 В главное меню"
- [ ] "✏️ Изменить профиль" → выбор поля → изменить имя → сохранилось, видно в профиле
- [ ] "Отмена" внутри редактирования поля → возврат к выбору поля, не в меню и не в ошибку
- [ ] "🔙 В главное меню" с любого экрана → меню, FSM сброшен

### Тренировка
- [ ] "🏋️ Тренировка на сегодня" → план с задачами и кнопками ℹ️ у каждой
- [ ] ⬜ → ✅ при нажатии, ✅ → ⬜ при повторном нажатии
- [ ] После завершения ВСЕХ задач → "🎉 Тренировка завершена!" + shop-кнопка появляется
- [ ] ℹ️ → AI даёт объяснение (не заглушку) + shop-кнопка в клавиатуре
- [ ] "🔄 Новый план" → план меняется (AI отвечает)
- [ ] 6-й AI-запрос у free → "Лимит исчерпан" + кнопка Premium, не ошибка

### Недельный план
- [ ] Хэндлер доступен (временно: отправить callback `menu_week_plan` вручную или добавить кнопку)
- [ ] День 1 показывает задачи; ◀/▶ переключают дни 1–7
- [ ] Toggle задачи работает; завершение дня → "🎉 День выполнен!" + shop-кнопка

### AI-кинолог
- [ ] "💬 Вопрос кинологу" → предложение написать вопрос
- [ ] Вопрос "Как отучить тянуть поводок?" → структурированный ответ с именем питомца, не заглушка
- [ ] Второй вопрос подряд → ответ учитывает предыдущий (история работает)
- [ ] "📊 Статистика" → "🧠 Анализ прогресса AI" → ответ от AI (не заглушка)

### Premium
- [ ] "⭐ Получить Premium" → экран с описанием и кнопкой оплаты
- [ ] Кнопка оплаты → открывается Telegram Stars invoice
- [ ] `/grant_premium <id> 1` (admin) → в меню label меняется на "⭐ Premium (активен)"
- [ ] Premium-пользователь: AI-анализ прогресса длиннее и детальнее, чем у free

### Referral
- [ ] "🐾 Позови друга" → персональная ссылка + счётчик + прогресс до следующего milestone
- [ ] Аккаунт B приходит по ссылке A, проходит онбординг → оба получают +3 дня premium
- [ ] Self-referral (A приходит по своей же ссылке) → бонус не начисляется, нет ошибки
- [ ] Счётчик у A увеличивается на 1 после засчитанного реферала

### Shop
- [ ] "🛒 Магазин" → 4 кнопки (3 категории + "Весь магазин"), все открываются в браузере
- [ ] После показа дневного плана → shop-кнопка с лакомствами для дрессировки присутствует
- [ ] URL кнопки содержит `utm_source=pepito_bot` (проверить через "Копировать ссылку")

### Напоминания
- [ ] "⏰ Напоминания" → показывает текущее время и форму ввода
- [ ] Ввод `09:30` → "Готово! Напоминание в 09:30 (UTC+3)" (часовой пояс из профиля), значение сохранилось
- [ ] Ввод `9:5` или `25:00` → сообщение об ошибке формата, бот не падает
- [ ] Scheduler шлёт напоминание в настроенное **местное** время (конвертация UTC через tz_utils)

---

## UX-полировки (backlog, без реализации сейчас)

1. **Нет подтверждения после toggle задачи** — при нажатии ⬜/✅ нет тактильного feedback (cb.answer() пустой). Добавить `cb.answer("✅ Выполнено!")` / `cb.answer("↩️ Снято")` — одна строка кода.

2. ~~**Кнопка "🔄 Новый план" не предупреждает об удалении**~~ ✅ Реализовано: `refresh_confirm` inline [Да]/[Нет].

3. ~~**Кинолог не сбрасывает историю между сессиями**~~ ✅ Реализовано: `_coach_reply_keyboard()` с кнопкой "🆕 Новая консультация" после каждого ответа.

4. **Нет отображения streak в главном меню** — пользователь не видит свою серию, пока не зайдёт в статистику. Streak ("🔥 5 дней подряд") можно добавить в приветственный текст меню.

5. **Экран статистики статичный** — показывает только счётчик и предлагает AI-анализ. Добавить мини-прогресс-бар к следующей milestone-награде за рефералов прямо на экране статистики.

6. **AI-ответ кинолога не разбит на абзацы** — в Telegram длинный текст без отступов нечитабельный. Промпт уже задаёт структуру, но иногда модель игнорирует HTML-теги. Добавить постпроцессинг: заменять `\n\n` на разрывы и проверять наличие тегов.

7. ~~**Нет onboarding progress bar**~~ N/A: онбординг переведён на AI-driven flow (2 состояния, не 10 шагов).

8. **Shop-кнопка показывается повторно при navigation** — если пользователь зашёл в план, вышел и вернулся, shop-кнопка появится снова (AFTER_PLAN). Рассмотреть кулдаун через Redis (1 показ/час).
