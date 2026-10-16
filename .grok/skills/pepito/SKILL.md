---
name: pepito
description: >
  Work on the Pepito brand monorepo: Telegram AI dog-trainer bot (@pepitopetbot)
  and Odoo 19 shop (pepitopet.ru). Covers deploy (podman), logic layer (rules.json),
  subscriptions/Stars/referrals, Gemini AI, shop UTM, Tinkoff acquiring, blog,
  mobile menu/design, QA (judge/regression/promptfoo). Use when the user mentions
  pepito, pepitopet, pepitopetbot, AI-кинолог, магазин pepito, tinkoff/stars for
  pepito, or runs /pepito. Not for other bots (motormind, dogsensei, subarist).
metadata:
  short-description: "Pepito bot + Odoo shop monorepo"
---

# Pepito skill

Monorepo brand stack: **AI-кинолог bot + natural dog-treat shop**.

| Piece | Path | Public |
|-------|------|--------|
| Bot | `/root/pepito/bot` | Telegram `@pepitopetbot`, WebApp `https://bot.pepitopet.ru` |
| Shop | `/root/pepito/odoo` | `https://pepitopet.ru` |
| Android (separate) | `/root/pepito_android` | RuStore; only if user asks |
| Shared toolkit | `/root/agents` | health / regression / economics |

**Scope default:** only `/root/pepito/` (+ toolkit reads). Do not touch other VDS projects unless asked.

**Session start:**
```bash
cat /root/pepito/SESSION_NOTES.md
python3 /root/agents/tools/agent_health.py
```
Update `SESSION_NOTES.md` after material steps. **No git commit/push without explicit user OK.**

---

## Architecture (mental model)

```
Owner (Telegram) ──► pepito-bot (aiogram3 + Gemini)
                         │
         PostgreSQL ◄────┤ rate limit / metrics / FSM ──► Redis
                         │
                         └── UTM links ──► Odoo 19 shop (pepitopet.ru)
                                              │
                         Tinkoff webhook ◄────┘  payment_tinkoff
                         NPM proxy ──► bot.pepitopet.ru :8080 in bot container
```

**Business SSOT (bot):** `bot/app/logic/rules.json`  
— free AI limit (5), Stars (299 / 30d), referral tiers, model cascade, forbidden medical phrases, shop age tokens.

**Never invent vet diagnoses.** Soft-block via `forbidden_phrases` + product tone.

Deep map: [references/architecture.md](references/architecture.md)  
Commands: [references/runbook.md](references/runbook.md)

---

## Guardrails (hard)

### Runtime
- **podman / podman-compose only** — never docker
- **uv** for Python deps in bot (`uv run`, `uv add`) — no global `pip install` / `apt`
- VDS RAM ~3GB: do **not** start a second Browserless; reuse `:3001` (amanita) or existing pepito `:3002` if already up

### Human-owned (ask first)
| Area | Paths |
|------|--------|
| Secrets | `bot/.env`, Odoo admin passwords, Tinkoff TerminalKey/Password |
| Migrations / DB models | `bot/alembic/`, `bot/app/infrastructure/db/` |
| Infra compose | `bot/podman-compose.yml`, `bot/Containerfile`, `odoo/podman-compose.yml`, `odoo/config/odoo.conf` |
| Legal / company data | Odoo company, оферта — needed for Tinkoff moderation |

### Agent-owned (edit freely with tests)
- Bot: `app/bot/handlers|keyboards|states`, `app/services/`, `app/logic/`, `app/i18n/`, `app/core/shop*.py`, `tests/`, `scripts/`, `eval/`
- Odoo: `addons/pepito_design`, `addons/payment_tinkoff`, `tools/`, blog content via scripts

### Critical business rules (already fixed once — do not regress)
1. **Subscription stacking** — new paid/referral expiry = `max(now, current_end) + days`; never reset to only +30d
2. **Expire job** — expire **rows** past due only; recompute `is_premium` if any active remains
3. **Refund** — same recompute; do not wipe stacked referral days
4. **mark_task_by_hint** — substring match or single incomplete task; **no guessing** among many
5. **mark_done miss UX** — use `training.task.not_found`, not `voice_action.all_done`
6. **Mobile header CSS** — never `backdrop-filter` / `filter` / `transform` on `<header>` (breaks offcanvas)

---

## Workflows

### 0) Health (always before long work)
```bash
python3 /root/agents/tools/agent_health.py
podman ps --filter name=pepito --format 'table {{.Names}}\t{{.Status}}'
podman ps --filter name=odoo_pepito --format 'table {{.Names}}\t{{.Status}}'
```

### 1) Bot code change
```
edit agent-owned files
  → cd /root/pepito/bot && ./judge.sh          # must exit 0
  → uv run pytest tests/unit -q                # if logic touched
  → deploy (rebuild — code is NOT volume-mounted)
```

Deploy bot (no bind-mount):
```bash
cd /root/pepito/bot
podman-compose build bot
podman rm -f pepito-bot_bot_1
podman-compose up -d bot
podman logs --tail 40 pepito-bot_bot_1   # expect: Start polling, Web server :8080
```

### 2) Logic / product constants
Edit **`app/logic/rules.json` only** for limits, Stars, referral, models.  
Wire reads via `app/logic/rules.py` (`rule("premium.stars_1m")`).  
Schemas: `app/logic/schemas.py`. Cascade: `app/logic/cascade.py`.  
AI entry: `app/services/ai_service.py` (`_generate_structured`, coach, plans).

### 3) Odoo design / shop UX
- SCSS: `odoo/addons/pepito_design/static/src/scss/pepito_design.scss` (volume-mounted)
- After SCSS: clear frontend assets + restart web if CSS stale  
  `DELETE FROM ir_attachment WHERE name LIKE '%web.assets_frontend%';` then `podman restart odoo_pepito_app`
- Mobile menu smoke: `bash /root/pepito/odoo/tools/mobile_menu_smoke.sh`

### 4) Odoo module code (payment_tinkoff, etc.)
- Edit under `addons/`; mount is live for Python, but registry may need:
  - Prefer restart: `podman restart odoo_pepito_app`
  - Full `-u module` only when needed; **port 8069 already bound** inside running container — use shell script pattern from `tools/` with `--no-http` or restart-based reload

### 5) Blog / articles
- Module: `website_blog` (installed). Blog name: **Советы кинолога**
- Seed/update: `odoo/tools/seed_blog_articles.py`, `fix_blog_i18n.py`, `upload_blog_covers.py`
- Run **inside** `odoo_pepito_app` via `podman cp` + `python3 /tmp/...`
- Translated fields: write **plain strings** with `with_context(lang='ru_RU')` — never nest dicts as string
- Public: `/blog`, homepage section `s_pepito_blog`

### 6) Payments
| Channel | Where | Notes |
|---------|--------|--------|
| Telegram Stars | bot `handlers/subscription.py` + `SubscriptionService` | payload `premium_1m`, charge_id idempotent |
| Tinkoff card | Odoo `payment_tinkoff` | notify `POST /payment/tinkoff/notification`; GET → 405 = route alive |
| Docs | `odoo/docs/TINKOFF_ACQUIRING.md` | TerminalKey/Password + legal entity for bank moderation |

### 7) QA matrix
```bash
# Offline multi-suite
bash /root/agents/tools/agent_regression.sh pepito

# Bot unit + judge
cd /root/pepito/bot && ./judge.sh

# Real DB + Redis (in bot container)
podman exec pepito-bot_bot_1 python /app/scripts/qa_subscription_logic.py
podman exec pepito-bot_bot_1 python /app/scripts/qa_user_journey.py   # spends Gemini

# Live prompt quality (optional)
export PATH="/root/.nvm/versions/node/v22.22.2/bin:$PATH"
set -a; source /root/pepito/bot/.env; set +a
cd /root/pepito/bot/eval && promptfoo eval
```

### 8) Shop ↔ bot links
- `bot/app/core/shop.py`, `shop_recommendations.py`
- UTM: `utm_source=pepito_bot` (or `blog`) + campaign context
- Categories e.g. treats `categ=4`, puppy tags

---

## Containers cheat sheet

| Name | Role |
|------|------|
| `pepito-bot_bot_1` | aiogram + aiohttp :8080 |
| `pepito-bot_db_1` | Postgres 16 (bot) — host :5432 |
| `pepito-bot_redis_1` | Redis — host :6379 |
| `odoo_pepito_app` | Odoo 19 — host 127.0.0.1:8071→8069 |
| `odoo_pepito_db` | Postgres 17 (shop) |
| `nginx_proxy_manager` | public TLS for pepitopet.ru / bot.pepitopet.ru |

If **shop 502**: Odoo down or NPM stale IP — prefer proxy hostname `odoo_pepito_app`, not raw IP.

---

## Decision defaults

1. Prefer small patches + `judge.sh` over rewrites.
2. Product numbers only in `rules.json`.
3. i18n: all 6 locales (ru/en/de/fr/es/pt) when adding user-facing strings.
4. DI: `@inject` + `Provide[AppContainer.…]` in handlers.
5. Ruff: do not “fix” E712 (`== True` on SQLAlchemy) or UP042.
6. Filestore: many missing `payment.method` icons — cosmetic; **product images OK** — don't bulk-delete attachments.
7. Log LLM cost for agents: `python3 /root/agents/hooks/llm_tracker.py log --project pepito …`

---

## Anti-patterns

- `docker` / global pip / second Chromium for visual QA
- Editing DB models without migration plan
- Force-recreating `pepito-bot_db_1` / wiping volumes
- Coach prompts that invent medical diagnoses
- `datetime.utcnow()` new code — prefer timezone-aware (legacy still present)
- Committing `.env` or Tinkoff secrets

---

## When stuck

1. `podman logs --tail 80 pepito-bot_bot_1` / `odoo_pepito_app`
2. `python3 /root/agents/tools/agent_health.py`
3. Read `bot/CLAUDE.md`, `odoo/CLAUDE.md`, `DECISIONS.md`, `SESSION_NOTES.md`
4. Regression: `bash /root/agents/tools/agent_regression.sh pepito`
