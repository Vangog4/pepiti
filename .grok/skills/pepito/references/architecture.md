# Pepito architecture

## Monorepo layout

```
/root/pepito/
├── CLAUDE.md, DECISIONS.md, SESSION_NOTES.md
├── bot/                     # Telegram + WebApp + API
│   ├── app/
│   │   ├── bot/handlers/    # menu, onboarding, subscription, admin, …
│   │   ├── bot/keyboards/, states/, middlewares/
│   │   ├── services/        # Ai, User, Pet, Training, Subscription, Referral, Coach, PDF, Broadcast
│   │   ├── logic/           # rules.json SSOT, schemas, cascade, trace
│   │   ├── api/             # aiohttp for WebApp (bot.pepitopet.ru)
│   │   ├── webapp/          # static mini-app
│   │   ├── infrastructure/db|redis/
│   │   ├── scheduler/       # reminders */min, weekly, expire 00:05 UTC
│   │   ├── i18n/locales/    # ru en de fr es pt
│   │   └── core/            # config, DI container, shop*
│   ├── scripts/             # qa_subscription_logic, qa_user_journey
│   ├── eval/                # promptfoo
│   ├── tests/unit|smoke|e2e/
│   ├── judge.sh
│   └── podman-compose.yml   # db + redis + bot (no code volume)
└── odoo/
    ├── addons/
    │   ├── pepito_design/   # brand SCSS, mobile menu fixes
    │   └── payment_tinkoff/ # Init/Token/Notification acquiring
    ├── tools/               # blog seed, covers, visual QA, image upload
    ├── docs/TINKOFF_ACQUIRING.md
    ├── config/odoo.conf
    └── podman-compose.yml   # db + web (+ optional browserless :3002)
```

## Bot stack

| Layer | Tech |
|-------|------|
| Framework | aiogram 3, dependency-injector |
| AI | Google Gemini (`gemini-2.5-flash-lite` → escalate `flash`) |
| DB | PostgreSQL 16 + SQLAlchemy async + Alembic |
| Cache/FSM | Redis |
| Jobs | APScheduler (UTC) |
| HTTP | aiohttp API + static webapp on `:8080` |

### Logic layer

| File | Role |
|------|------|
| `logic/rules.json` | Product constants |
| `logic/rules.py` | `rule()`, `contains_forbidden()` |
| `logic/schemas.py` | Pydantic TrainingPlan, WeekPlan, Profile, Intent |
| `logic/cascade.py` | Model ladder default → escalate |
| `logic/trace.py` | Structured logs; optional Langfuse env |

### Premium & money (bot)

- Invoice currency **XTR** (Telegram Stars), plan `premium_1m`
- `SubscriptionService.activate` stacks days; idempotent on `charge_id`
- `expire_subscriptions` job: per-row expire + recompute user flag
- Refund handler recalculates remaining active subs

### Voice / training intent

- `detect_training_intent` → `mark_done` | `none`
- `TrainingService.mark_task_by_hint` strict matching
- Miss → `training.task.not_found` (not false “all done”)

## Odoo stack

| Layer | Tech |
|-------|------|
| Odoo | 19 Community |
| DB | PostgreSQL 17 (`odoo_user_pepito`) |
| Modules | website_sale, website_blog, pepito_design, payment_tinkoff |
| Proxy | Nginx Proxy Manager → container hostnames |

### Design constraints

- Brand: cream `#FBF3E8` / `#FDF6EE`, dark `#1A0A00`, gold `#F0A500`, rust `#C8411A`
- Header: no filter/backdrop-filter (mobile offcanvas)
- Blog: «Советы кинолога», homepage `s_pepito_blog`

### Filestore note

~600 missing binary files are mostly **payment.method** icons; product images are present. Prefer not bulk-deleting attachments.

## Integration bot ↔ shop

```
shop.py / shop_recommendations.py
  → https://pepitopet.ru/shop?…&utm_source=pepito_bot&utm_medium=telegram&utm_campaign=<ctx>
```

Contexts: after_plan, after_exercise, after_completion, blog articles use `utm_source=blog`.

## Related (out of monorepo)

| Path | Note |
|------|------|
| `/root/pepito_android` | Kotlin app / RuStore — separate CLAUDE |
| `/root/agents` | Shared health, regression, pricing, llm_tracker |
| Browserless | Prefer single instance; amenity often on `:3001` |
