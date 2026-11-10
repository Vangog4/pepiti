# DECISIONS — pepito

## Retrospective — 2026-11-01 12:32 [pepito]

### Изменения
```
bot/podman-compose.yml | 4 ----
 1 file changed, 4 deletions(-)
```

### Gemini Review
_Gemini недоступен_

---

## Retrospective — 2026-11-01 14:06 [pepito]

### Изменения
```
bot/podman-compose.yml | 12 +++++-------
 1 file changed, 5 insertions(+), 7 deletions(-)
```

### Gemini Review
_Gemini недоступен_

---

## Retrospective — 2026-11-01 14:20 [pepito]

### Изменения
```
bot/podman-compose.yml | 12 +++++-------
 1 file changed, 5 insertions(+), 7 deletions(-)
```

### Gemini Review
_Gemini недоступен_

---

## Retrospective — 2026-11-01 15:21 [pepito]

### Изменения
```
bot/podman-compose.yml | 12 +++++-------
 1 file changed, 5 insertions(+), 7 deletions(-)
```

### Gemini Review
_Gemini недоступен_

---

## Retrospective — 2026-11-01 15:51 [pepito]

### Изменения
```
bot/app/api/routes.py                            |  11 +++++---
 bot/app/api/v1/routers/coach.py                  |  22 ++++++++-------
 bot/app/api/v1/routers/profile.py                |   5 ++--
 bot/app/api/v1/routers/subscription.py           |   3 ++-
 bot/app/api/v1/routers/training.py               |   4 ++-
 bot/app/bot/handlers/admin.py                    |   9 ++++---
 bot/app/bot/handlers/menu.py                     | 132 +++++++++++++++++++++++++++++++++++++++++++++++++++++++-----------------------------------
 bot/app/bot/handlers/start.py                    |   7 ++---
 bot/app/bot/handlers/subscription.py             |  24 ++++++++++++++++-
 bot/app/core/config.py                           |   1 +
 bot/app/core/tz_utils.py                         |  16 ++++++++++-
 bot/app/i18n/locales/de.py                       |   2 ++
 bot/app/i18n/locales/en.py                       |   2 ++
 bot/app/i18n/locales/es.py                       |   2 ++
 bot/app/i18n/locales/fr.py                       |   2 ++
 bot/app/i18n/locales/pt.py                       |   2 ++
 bot/app/i18n/locales/ru.py                       |   2 ++
 bot/app/infrastructure/db/models/subscription.py |  11 +++++++-
 bot/app/infrastructure/redis/ai_rate_limit.py    |  52 ++++++++++++++++++++++++++----------
 bot/app/main.py                                  |   4 +--
 bot/app/scheduler/jobs/reminders.py              |  49 +++++++++++++---------------------
 bot/app/scheduler/jobs/reports.py                |   3 ++-
 bot/app/scheduler/setup.py                       |   4 +--
 bot/app/services/ai_service.py                   |  31 ++++++++++++++-------
 bot/app/services/subscription_service.py         |  22 ++++++++++-----
 bot/podman-compose.yml                           |  12 ++++-----
 26 files changed, 284 insertions(+), 150 deletions(-)
```

### Gemini Review
_Gemini недоступен_

---
