# CLAUDE.md — pepito/odoo (Интернет-магазин pepitopet.ru)

## Sandbox Rules (ОБЯЗАТЕЛЬНО)
- Runtime: **podman** и **podman-compose** ТОЛЬКО
- **НИКОГДА:** `apt install`, `pip install` (глобально), `docker`
- Полный путь: `/root/pepito/odoo/`

## Stack

| Компонент | Детали |
|---|---|
| Odoo | 19 Community |
| PostgreSQL | 17 |
| Runtime | Podman |
| Публичный URL | `https://pepitopet.ru` |
| Каталог | 34 товара (натуральные говяжьи лакомства) |

```
pepito/odoo/
├── addons/        — кастомные модули (Agent-owned)
├── artifacts/     — артефакты CI/QA
├── config/        — odoo.conf (Human-owned)
├── judge.sh       — скрипт валидации
├── podman-compose.yml (Human-owned)
└── tools/         — MCP visual-qa server
```

## Mode Declarations
- `[REVIEW MODE]` / `[DESIGN MODE]` / `[BUILD MODE]` / `[PATCH MODE]`

## Управление стеком
```bash
# Запуск
cd /root/pepito/odoo && podman-compose up -d

# Рестарт Odoo (без БД)
podman-compose restart web

# Логи
podman logs -f odoo_pepito_app

# Апгрейд модуля
podman exec odoo_pepito_app odoo -u <module_name> --stop-after-init
```

## Pre-Session Checklist
```bash
podman ps --filter name=odoo_pepito      # все контейнеры running?
podman logs odoo_pepito_app --tail=20    # нет ERROR?
df -h /                                  # диск < 90%?
```

## Rollback Protocol
```bash
# 1. Перед изменением модуля:
git -C /root/pepito/odoo stash

# 2. Если Odoo не стартует:
git -C /root/pepito/odoo stash pop
podman exec odoo_pepito_app odoo -u <module> --stop-after-init

# 3. Проверка после изменений:
podman logs odoo_pepito_app --tail=30 | grep -E "^[0-9].*ERROR"
```

## Валидация (judge.sh)
```bash
cd /root/pepito/odoo && ./judge.sh
# exit 0 → принять изменения
# exit != 0 → git stash pop, разобрать ошибку
```

## Интеграция с Telegram-ботом
Бот ссылается на магазин через UTM в `../bot/app/core/shop.py`:
```
utm_source=pepito_bot&utm_medium=telegram&utm_campaign=<context>
```
Страницы: `/`, `/shop`, `/oferta`, `/contactus`, `/privacy`

## Guardrails
- Human-owned: `config/odoo.conf`, `.env`, `podman-compose.yml`
- Agent-owned: `addons/`, `static/`, QWeb-шаблоны
- **НИКОГДА** не делать SQL UPDATE/DELETE напрямую (только через ORM)
- **НИКОГДА** не удалять volume `pepito_odoo_odoo_pepito_db_data`

## SESSION_MEMORY
```
<STATE_MEMORY>
✅ Сделано: [список]
🔄 Открыто: [задачи]
➡️ Следующий шаг: [конкретное действие]
</STATE_MEMORY>
```
