# CLAUDE.md — Pepito Project

## ⚡ СТАРТ СЕССИИ — читать ПЕРВЫМ
```bash
cat /root/pepito/SESSION_NOTES.md    # что было в работе
cat /root/logseq-graph/journals/$(date +%Y_%m_%d).md 2>/dev/null | tail -40
```
**В течение сессии:** обновляй `SESSION_NOTES.md` при каждом важном шаге.
**Без git commit/push без явного разрешения пользователя.**

Монорепо двух связанных проектов одного бренда: Telegram-бот + Odoo интернет-магазин.

```
/root/pepito/
  bot/    → Telegram-бот @pepitopetbot (Python/aiogram)
  odoo/   → Интернет-магазин pepitopet.ru (Odoo 19)
  docs/   → Общая документация, дорожная карта интеграции
```

---

## Проекты

### bot/ — Telegram-бот
Полная документация: `bot/CLAUDE.md`

Краткое:
- Python, aiogram 3, Gemini AI, PostgreSQL, Redis
- Запуск: `cd bot && podman-compose up -d --build`
- judge: `cd bot && ./judge.sh`
- Бот: @pepitopetbot, webapp: https://bot.pepitopet.ru

### odoo/ — Интернет-магазин
Полная документация: `odoo/CLAUDE.md` (создать)

Краткое:
- Odoo 19, PostgreSQL 17
- 34 товара (натуральные говяжьи лакомства для собак)
- Страницы: `/`, `/shop`, `/oferta`, `/contactus`, `/privacy`
- Запуск: `cd odoo && podman-compose up -d`
- Логи: `podman logs -f odoo_pepito_app`

---

## Интеграция бот ↔ магазин

Бот ссылается на магазин через UTM-ссылки в `bot/app/core/shop.py`:
```
utm_source=pepito_bot&utm_medium=telegram&utm_campaign=<context>
```

Контексты: `after_plan`, `after_exercise`, `after_completion`

---

## Деплой

### Бот
```bash
cd /root/pepito/bot
podman rm -f pepito-bot_bot_1
podman-compose up -d --build
podman logs -f pepito-bot_bot_1
```

### Odoo
```bash
cd /root/pepito/odoo
podman-compose up -d
podman logs -f odoo_pepito_app
```

---

## Зоны ответственности

**bot/** — Agent-owned (я предлагаю и применяю изменения):
- `app/bot/handlers/`, `app/bot/keyboards/`, `app/services/`, `app/i18n/`

**bot/** — Human-owned (не трогать без явного разрешения):
- `alembic/`, `.env`, `app/infrastructure/db/`

**odoo/** — Agent-owned:
- `addons/` — кастомные модули

**odoo/** — Human-owned:
- `config/odoo.conf` — только по согласованию
