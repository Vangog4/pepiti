# Pepito Odoo Constitution

## Core Principles

### I. Web-Interface First
Все изменения в данных Odoo (вложения, записи, виды) производятся через официальный JSON-RPC API или MCP-инструменты (`odoo-pepito`). Прямые SQL-запросы допустимы только для чтения (диагностика). Запись в БД напрямую — запрещена.

### II. Visual QA After Every Change
После каждого изменения дизайна или контента — скриншот через `visual-qa-pepito`. Изменение считается принятым только после визуальной проверки. Скриншоты не сохраняются в /tmp дольше одной сессии.

### III. Judge Before Commit
Любое изменение в `addons/` проходит через `./judge.sh` (exit 0) до коммита. SCSS и XML валидируются. Нет зелёного судьи — нет коммита.

### IV. Brand Consistency (NON-NEGOTIABLE)
Цвета: `$color-rust:#C8411A`, `$color-gold:#F0A500`, `$color-dark:#1A0A00`, `$color-cream:#FDF6EE`.
Шрифт заголовков: `Playfair Display, serif`. Стиль: мексиканская фиеста, тепло, натуральность.
Отклонение от палитры требует явного одобрения пользователя.

### V. No Clutter
Временные файлы удаляются в конце каждой сессии. Скрипты не пишутся для одноразовых задач — используются MCP-инструменты и API.

## Стек и зоны ответственности

**Agent-owned**: `addons/pepito_design/` (SCSS, QWeb, XML), данные товаров, вложения, виды homepage/shop/product.
**Human-owned**: `config/odoo.conf`, `podman-compose.yml`, учётные данные.

**Инструменты**:
- `odoo-pepito` MCP → все операции чтения/записи в Odoo API
- `visual-qa-pepito` MCP → скриншоты и DOM-геометрия
- `./judge.sh` → валидация перед каждым коммитом

## Development Workflow

1. `/speckit-specify` → зафиксировать требования
2. `/speckit-plan` → декомпозиция на задачи
3. `/speckit-implement` → реализация с визуальной проверкой
4. `./judge.sh` → gate перед коммитом

## Governance

Конституция имеет приоритет над любыми другими практиками. Изменения дизайна без визуальной проверки и изменения данных без API — нарушения конституции.

**Version**: 1.0.0 | **Ratified**: 2026-05-14 | **Last Amended**: 2026-05-14
