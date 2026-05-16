# Experiment Log Template

Используй этот шаблон когда judge.sh не запускался (чистый diff, документация,
изменения только в конфиге) или для ручного дополнения авто-записи.

Скопируй блок ниже в `docs/journal/YYYY-MM-DD.md`.

---

## HH:MM — <task name>

- **Verdict:** PASSED / FAILED / N/A
- **Commit:** `git rev-parse --short HEAD` → заменить на SHA
- **Judge:** PASS=? FAIL=? SKIP=? / N/A (doc-only change)
- **Log:** artifacts/judge-YYYY-MM-DD_HH-MM-SS.log / N/A
- **Changed files:**
  - `app/bot/handlers/menu.py`
  - `app/bot/keyboards/main_menu.py`
- **Notes:** почему KEEP или DISCARD; что было неожиданным

---

## Когда использовать

| Ситуация | Что заполнять |
|---|---|
| Обычный pilot task | judge.sh заполняет автоматически; добавить Commit SHA вручную |
| Doc-only / template change | Judge = N/A; остальное вручную |
| DISCARD — откат | Verdict = DISCARD; Notes = причина отката |
| Hotfix без judge | Judge = SKIP (объяснить почему); Notes = обоснование |

## Пример заполненной записи

## 09:15 — feat(menu): add weekly plan button

- **Verdict:** PASSED
- **Commit:** `58f13a1`
- **Judge:** PASS=3 FAIL=0 SKIP=2
- **Log:** artifacts/judge-2026-04-20_07-36-21.log
- **Changed files:**
  - `app/bot/keyboards/main_menu.py`
- **Notes:** SKIP=2 ожидаемы (deps вне контейнера). Кнопка добавлена в строку 1 рядом с тренировкой.
