# CLAUDE.md — pepito_odoo

Интернет-магазин pepitopet.ru — натуральные говяжьи лакомства для собак, 34 товара.

## Stack

- **Odoo 19** — `odoo_pepito_app`, хостовый порт `127.0.0.1:8071:8069`
- **PostgreSQL 17** — `odoo_pepito_db`
- **Browserless/Chromium** — `odoo_pepito_browserless`, хостовый порт `127.0.0.1:3002:3000`
- Сеть: `pepito_net` (internal bridge) + `npm_network` (external, reverse proxy)
- Compose-файл: `podman-compose.yml`
- Кастомные модули: `./addons/`
- Публичный домен: `pepitopet.ru`

---

## Workflow изменений (judge-цикл)

```
propose → patch → ./judge.sh → keep (commit) / discard (git checkout)
```

```bash
./judge.sh                   # лог → artifacts/judge-<timestamp>.log
./judge.sh my-artifacts-dir  # кастомный каталог логов
```

Judge проверяет:
1. Синтаксис Python во всех `addons/**/*.py`
2. Наличие `__manifest__.py` в каждом аддоне
3. XML валидность (`xmllint`) во всех `addons/**/*.xml`
4. Odoo health-endpoint (`/web/health` через хостовый порт)
5. Наличие критических файлов проекта

**Exit 0** → изменение принято, можно коммитить.
**Exit != 0** → откатить: `git checkout -- <changed files>`, причину записать в `artifacts/`.

---

## Деплой

### Рекомендуемый сценарий

```bash
cd /root/pepito/odoo

# Обновить модуль после правки (без рестарта Odoo):
podman exec odoo_pepito_app odoo -u <module_name> --stop-after-init

# Полный рестарт (редко нужен):
podman-compose down
podman-compose up -d
podman logs -f odoo_pepito_app
```

### Запуск с нуля (после перезагрузки сервера)

```bash
cd /root/pepito/odoo
podman-compose up -d
podman logs -f odoo_pepito_app
```

### Browserless (для Visual QA)

```bash
# Запустить отдельно если упал:
podman-compose up -d browserless_pepito
```

---

## Visual QA Workflow

**Триггеры:** слова "кривой", "поехала верстка", "визуальный баг", "посмотри сайт",
"не так выглядит", "расположение", "отступы", "блок", "секция".

### Шаги

1. **Проверь browserless:** вызови `browserless_health()` (MCP-сервер `visual-qa-pepito`).
   - Если `UNREACHABLE` → попроси пользователя выполнить:
     `podman-compose -f /root/pepito/odoo/podman-compose.yml up -d browserless_pepito`

2. **Сделай скриншот:** вызови `screenshot(url="http://web_pepito:8069/")`.
   - `url` передаётся внутри сети podman → browserless разрешает `web_pepito` по имени.
   - Для конкретной страницы: `screenshot(url="http://web_pepito:8069/shop")`.
   - Результат — base64 PNG; передай его в сообщение как изображение для анализа.

3. **Диагностика блоков:** при подозрении на поехавшие отступы/высоты вызови:
   `dom_geometry(url="http://web_pepito:8069/", selector="header, .o_home_menu, section, footer")`

4. **Исправляй** в `./addons/<module>/static/src/scss/` или в шаблонах QWeb.
   После правки — повтори скриншот для верификации.

### URL-справочник

| Откуда         | URL Odoo                       | URL Browserless          |
|----------------|--------------------------------|--------------------------|
| Внутри сети    | `http://web_pepito:8069`       | `http://browserless_pepito:3000` |
| С хоста        | `http://127.0.0.1:8071`        | `http://127.0.0.1:3002`  |
| Публичный      | `https://pepitopet.ru`         | —                        |

### MCP-инструменты (сервер `visual-qa-pepito`)

| Инструмент          | Назначение                                    |
|---------------------|-----------------------------------------------|
| `screenshot`        | Полностраничный PNG, возвращает base64        |
| `dom_geometry`      | BBox всех элементов по CSS-селектору          |
| `browserless_health`| Проверка доступности контейнера               |

---

## Разработка модулей

```bash
# Перезагрузка модуля без рестарта Odoo:
podman exec odoo_pepito_app odoo -u <module> --stop-after-init

# Логи Odoo:
podman logs -f odoo_pepito_app

# Права на addons (если нужны):
chown -R root:root /root/pepito/odoo/addons/
```

---

## Зоны ответственности

**Agent-owned** (агент предлагает и применяет):
- `addons/` — кастомные модули (SCSS, QWeb, Python контроллеры)
- `judge.sh`, `CLAUDE.md`

**Human-owned** (не трогать без явного разрешения):
- `config/odoo.conf` — настройки сервера и БД
- `podman-compose.yml` — только по согласованию

---

## Установленные модули (prod)

account, base_setup, bus, delivery, ecommerce, mail, mrp, payment, payment_custom,
portal, product, sale, sale_management, website, auth_signup, google_recaptcha,
stock, utm, web.

---

## Rollout-сценарий

```
1. Изменить только agent-owned файлы
2. ./judge.sh                      # должен дать exit 0
3. exit 0 → git commit → готово
4. exit != 0 → git checkout -- .   → artifacts/FAILED-<date>.md
```
