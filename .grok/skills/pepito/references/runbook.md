# Pepito runbook — copy-paste commands

## Health

```bash
python3 /root/agents/tools/agent_health.py
python3 /root/agents/tools/agent_health.py --json

podman ps --filter name=pepito --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
podman ps --filter name=odoo_pepito --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

curl -sI https://pepitopet.ru/shop | head -5
curl -sI https://bot.pepitopet.ru/ | head -5
curl -sI https://pepitopet.ru/payment/tinkoff/notification | head -5   # expect 405
```

## Bot

```bash
# Logs
podman logs --tail 100 pepito-bot_bot_1
podman logs --since 30m pepito-bot_bot_1 2>&1 | grep -iE 'error|traceback' | tail

# Tests (host)
cd /root/pepito/bot
./judge.sh
uv run pytest tests/unit -q --tb=line
uv run pytest tests/unit/test_logic_layer.py tests/unit/test_subscription_logic.py -q

# Real-DB QA (container has deps + network to db/redis)
podman exec pepito-bot_bot_1 python /app/scripts/qa_subscription_logic.py
podman exec pepito-bot_bot_1 python /app/scripts/qa_user_journey.py

# Deploy (image rebuild required)
cd /root/pepito/bot
podman-compose build bot
podman rm -f pepito-bot_bot_1
podman-compose up -d bot
# wait ~10s for alembic + polling
podman logs --tail 30 pepito-bot_bot_1
```

### Bot env (do not print secrets)

Required keys live in `bot/.env` (GEMINI_API_KEY, BOT_TOKEN, DB/REDIS URLs, …).  
Config references: `bot/app/core/config.py`.

### Enter bot DB

```bash
podman exec -it pepito-bot_db_1 psql -U pepito -d pepito_db
```

## Odoo

```bash
# Logs
podman logs --tail 100 odoo_pepito_app
podman logs odoo_pepito_app 2>&1 | grep -iE 'ERROR|FileNotFoundError' | tail

# Restart web only
podman restart odoo_pepito_app

# Stack up
cd /root/pepito/odoo && podman-compose up -d

# Shell ORM (no HTTP bind conflict)
podman exec odoo_pepito_app python3 -c '
import sys; sys.path.insert(0,"/usr/lib/python3/dist-packages")
import odoo, odoo.api, odoo.modules.registry
from odoo.tools import config
config.parse_config(["--config","/etc/odoo/odoo.conf","--database","odoo_user_pepito","--no-http"])
reg=odoo.modules.registry.Registry.new("odoo_user_pepito")
print("registry ok")
'

# SQL
podman exec odoo_pepito_db psql -U odoo_user_pepito -d odoo_user_pepito -c "SELECT name,state FROM ir_module_module WHERE name IN ('pepito_design','payment_tinkoff','website_blog');"

# Clear CSS assets after SCSS change
podman exec odoo_pepito_db psql -U odoo_user_pepito -d odoo_user_pepito -c \
  "DELETE FROM ir_attachment WHERE name LIKE '%web.assets_frontend%' OR url LIKE '%web.assets_frontend%';"
podman restart odoo_pepito_app
```

### Blog tooling

```bash
podman cp /root/pepito/odoo/tools/seed_blog_articles.py odoo_pepito_app:/tmp/
podman exec odoo_pepito_app python3 /tmp/seed_blog_articles.py

podman cp /root/pepito/odoo/tools/fix_blog_i18n.py odoo_pepito_app:/tmp/
podman cp /root/pepito/odoo/tools/seed_blog_articles.py odoo_pepito_app:/tmp/
podman exec odoo_pepito_app python3 /tmp/fix_blog_i18n.py

podman cp /root/pepito/odoo/tools/blog_covers odoo_pepito_app:/tmp/blog_covers
podman cp /root/pepito/odoo/tools/upload_blog_covers.py odoo_pepito_app:/tmp/
podman exec odoo_pepito_app python3 /tmp/upload_blog_covers.py
```

### Mobile menu QA

```bash
bash /root/pepito/odoo/tools/mobile_menu_smoke.sh
# artifacts: odoo/artifacts/mobile-menu-qa/
```

## Shared regression / cost

```bash
bash /root/agents/tools/agent_regression.sh pepito
bash /root/agents/tools/agent_regression.sh          # all projects offline

python3 /root/agents/hooks/llm_tracker.py log \
  --project pepito --model gemini-2.5-flash --tokens-in 800 --tokens-out 400
python3 /root/agents/tools/unit_economics.py --days 7
```

## Promptfoo (live Gemini)

```bash
export PATH="/root/.nvm/versions/node/v22.22.2/bin:$PATH"
set -a; source /root/pepito/bot/.env; set +a
cd /root/pepito/bot/eval && promptfoo eval
REGRESSION_LIVE=1 bash /root/agents/tools/agent_regression.sh pepito
```

## Recovery playbooks

### Shop 502
1. `podman ps | grep odoo_pepito` — both app+db Up?
2. `podman start odoo_pepito_db odoo_pepito_app`
3. NPM proxy host must resolve **hostname** `odoo_pepito_app`, not stale IP
4. `curl -sI https://pepitopet.ru/shop`

### Bot not polling
1. `podman logs pepito-bot_bot_1` — migrations hang? GEMINI/TOKEN errors?
2. Rebuild deploy sequence above
3. Telegram Bad Gateway spikes are usually transient

### WebApp 502 after bot recreate
Wait for `Web server listening on 0.0.0.0:8080` + NPM network `npm_network` attached.

### Odoo won't start / port in use
Do not run second `odoo` bind on 8069 inside host. Use `--no-http` for one-shot scripts or restart the existing container.
