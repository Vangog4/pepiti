# [[pepito-bot]] — Project Page

> AI-кинолог Telegram-бот. Персональные тренировки для питомцев через Gemini AI.
> Bot: `@pepitopetbot` · Webapp: `https://bot.pepitopet.ru`

---

## Status: PRODUCTION READY (2026-04-29)

**Release Candidate закрыт**: все user-facing баги исправлены, smoke test пройден, judge.sh PASS=5.

---

## Stack

| Layer | Tech |
|---|---|
| Bot | aiogram 3.x, FSM (Redis backend) |
| AI | Google Gemini `gemini-2.5-flash-lite` |
| DB | PostgreSQL 16 + SQLAlchemy async |
| DI | dependency-injector |
| Scheduler | APScheduler (reminders, reports, expiry) |
| Webapp | aiohttp + Telegram WebApp Mini App |
| i18n | Custom pure-Python, 6 locales: ru/en/de/fr/es/pt |
| Infra | podman-compose, Nginx Proxy Manager, SSL |

---

## Architecture

```
Telegram (aiogram polling)
  ↓ handlers (menu, onboarding, edit_profile, subscription, admin)
  ↓ FSM states (OnboardingStates, CoachState, EditProfileStates, ...)
  ↓ Services (UserService, PetService, AiService, TrainingService, ...)
  ↓ Repositories → PostgreSQL
  ↓ Redis (FSM state, AiRateLimiter, BotMetrics)

WebApp (aiohttp :8080)
  ↓ /api/dashboard → JSON payload (user, pet, tasks, growth, settings)
  ↓ /api/tasks/{id}/toggle, /api/profile/pet|settings
  ↓ /api/coach/threads, /api/broadcast, /api/admin/*
  ↓ Served via Nginx Proxy Manager → https://bot.pepitopet.ru
```

---

## Implemented Features

### Onboarding & Profile
- [x] AI-онбординг (FSM, free-form text/voice/photo → structured profile)
- [x] Первый план автогенерируется после онбординга
- [x] Редактирование профиля питомца (7 полей, FSM, inline keyboards)
- [x] Translate_option: хранимые RU-значения → i18n display

### Training
- [x] Ежедневные планы (AI, toggle ✅/⬜, streak, 🔄 Новый план с подтверждением)
- [x] Недельный план (◀/▶ навигация, toggle, day-complete CTA)
- [x] Объяснение упражнения (explain_exercise → AI + shop CTA)

### AI Coach
- [x] Вопросы с историей диалога (CoachThread model)
- [x] Rate limiting: free 5/день, premium безлимит
- [x] Мультимодальность: фото (free), голос/видео (premium)
- [x] Архивирование тредов в WebApp

### Subscription & Monetization
- [x] Telegram Stars (invoice, активация, автоистечение scheduler)
- [x] Refund handler
- [x] `/grant_premium` (admin)

### Referral & Growth
- [x] Deep link `?start=ref_<id>` → double-sided +3 дня premium
- [x] Антифрод: self-referral, dedup, дневной лимит 10
- [x] Milestone награды: 3/5/10/25 рефералов → +7/14/30/90 дней
- [x] Экран "Позови друга" с live link через `bot.get_me()`

### Reminders & Scheduler
- [x] Timezone-aware напоминания (local_to_utc конвертация)
- [x] Еженедельные отчёты (Вс 18:00 UTC)
- [x] expire_subscriptions (00:05 UTC)

### Admin
- [x] `/admin`: broadcast, статистика пользователей
- [x] Secret WebApp admin tab (founder-only): metrics, growth funnel, referral stats, broadcast

### WebApp Dashboard (`https://bot.pepitopet.ru`)
- [x] 4 таба: Питомец / Настройки / Награды / Кинолог
- [x] Полная i18n: 51 ключ × 6 локалей в WEBAPP_I18N
- [x] `applyI18n()` покрывает все статичные HTML-элементы
- [x] Referral link через `settings.BOT_USERNAME` (`pepitopetbot`)
- [x] Coach threads: список, архивирование, relative dates
- [x] Milestone track, premium card, shop cards

### Shop
- [x] 4 кнопки: 3 категории + весь магазин, UTM-трекинг
- [x] Контекстные рекомендации (AFTER_PLAN, AFTER_EXERCISE, AFTER_COMPLETION)

---

## Config (.env)

| Variable | Value | Notes |
|---|---|---|
| `BOT_TOKEN` | set | Telegram bot token |
| `GEMINI_API_KEY` | set | Google AI key |
| `DATABASE_URL` | `postgresql+asyncpg://...@pepito-bot_db_1:5432/pepito_db` | |
| `REDIS_URL` | `redis://redis:6379/0` | |
| `ADMIN_TELEGRAM_IDS` | set | Comma-separated |
| `WEBAPP_PUBLIC_URL` | `https://bot.pepitopet.ru` | |
| `BOT_USERNAME` | `pepitopetbot` | Added 2026-04-29 (Stage 40) |

---

## Known Limitations (non-user-facing)

1. **Timezone picker**: DE/FR/ES/PT users see English city names (geographic names, bilingual is standard).
2. **DB storage for size/age**: stored as Russian strings (data model constraint), display via `translate_option()` — transparent to user.
3. **Shop URLs**: exact tag-filter URLs on pepitopet.ru not team-verified — placeholders in `app/core/shop.py`.
4. **Admin UI**: hardcoded Russian — intentional (admin-only tooling).
5. **Weekly plan entry**: no button in main menu historically; button added (Stage 4). Verified accessible.

---

## Definition of Done ✅

- All user-facing strings via `t()` (bot) or `_ui()` (webapp)
- 6 locales (ru/en/de/fr/es/pt) with full key parity (157 bot keys, 51 webapp keys)
- `applyI18n()` covers all static HTML elements with ids
- `referral_link` non-null when `BOT_USERNAME` set
- `judge.sh` PASS=5 FAIL=0
- Container: Up, scheduler running, 0 ERROR in logs

---

## Deployment

```bash
# Full deploy from scratch:
podman rm -f pepito-bot_bot_1
podman run --rm --env-file .env --net pepito-bot_pepito_net \
  localhost/pepito-bot_bot:latest alembic upgrade head
podman-compose up -d --build

# Hot restart (no image change):
podman restart pepito-bot_bot_1
podman logs -f pepito-bot_bot_1
```

Success indicator in logs:
```
Run polling for bot @pepitopetbot id=8705109498 - 'Pepito | AI-кинолог'
```

---

## Release History

| Date | Stage | Summary |
|---|---|---|
| 2026-04-20 | 1–3 | Core bot, FSM, AI, subscriptions |
| 2026-04-21 | 4 | Weekly plan, web app scaffold |
| 2026-04-23 | 5–8 | WebApp deploy, i18n (6 langs), admin tab, voice-to-action, broadcast |
| 2026-04-25 | 25–28 | i18n fixes across all flows |
| 2026-04-26 | 29–30 | Full i18n pass, language-aware AI output |
| 2026-04-29 | 38–42 | **RC Lock**: webapp i18n complete, BOT_USERNAME, all UX bugs closed |
