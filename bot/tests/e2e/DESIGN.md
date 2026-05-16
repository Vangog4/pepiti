# E2E Telegram Testing — Design Note

**Статус**: scaffold / design only. Полная реализация — в backlog.

---

## Цель

Автоматически проверять ключевые user flows Telegram-бота без ручного кликанья:
- онбординг (10 шагов FSM)
- главное меню (все кнопки открываются)
- тренировка (toggle задач, AI-ответ)
- premium flow (invoice, активация)

---

## Вариант A: Telethon user simulation ✅ РЕКОМЕНДУЕТСЯ

**Суть**: второй аккаунт Telegram (test account) управляется через Telethon MTProto API.
Скрипт отправляет команды боту и проверяет ответы.

**Почему рекомендуется для VDS:**
- Работает headless, без браузера
- Не требует X11/Xvfb
- Telethon стабилен, хорошо документирован
- Можно запускать из CI/CD или из cron

**Что нужно:**
- `TELETHON_API_ID`, `TELETHON_API_HASH` — из my.telegram.org
- `TELETHON_SESSION` — файл сессии тестового аккаунта (не основного!)
- `TEST_BOT_USERNAME` — username бота (из .env)
- Тестовый Telegram-аккаунт (отдельный номер телефона)

**Пример теста:**
```python
# tests/e2e/test_onboarding.py (TODO)
from telethon.sync import TelegramClient

async def test_start_command(client, bot_username):
    await client.send_message(bot_username, "/start")
    response = await client.get_messages(bot_username, limit=1)
    assert "Привет" in response[0].text or response[0].reply_markup is not None
```

**Ограничения:**
- Требует живой бот (не unit-тест)
- Не проверяет визуальный вид — только текст и кнопки
- Нужен второй Telegram-аккаунт для теста

---

## Вариант B: Playwright + Telegram Web

**Суть**: управление браузером через Playwright, логин в web.telegram.org, взаимодействие с ботом через UI.

**Почему НЕ рекомендуется для VDS:**
- Требует Chromium/Firefox + X11 или xvfb
- Авторизация через QR/SMS — неудобно автоматизировать
- Хрупкость: верстка Telegram Web меняется
- Высокий overhead на VDS с ограниченными ресурсами

---

## Текущее состояние

- [ ] Выбран подход: **Telethon (вариант A)**
- [ ] `tests/e2e/conftest.py` — TODO: настройка Telethon client fixture
- [ ] `tests/e2e/test_onboarding.py` — TODO
- [ ] `tests/e2e/test_menu.py` — TODO
- [ ] `.env.test` — TODO: отдельные переменные для тестового окружения

## Следующий шаг

Добавить в requirements.txt:
```
telethon>=1.36
pytest-asyncio>=0.23
```

Создать `tests/e2e/conftest.py` с Telethon-клиентом и добавить тесты онбординга.
Обновить judge.sh: запускать e2e только если `E2E_ENABLED=1` в env.

---

## Переменные окружения для e2e

```env
TELETHON_API_ID=...
TELETHON_API_HASH=...
TELETHON_SESSION=./artifacts/test_session
TEST_BOT_USERNAME=@pepito_bot
E2E_ENABLED=0   # 1 только в staging
```
