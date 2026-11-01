# Pepito: always-on service (Podman Quadlet + systemd)

Replaces `podman-compose` + `restart: always`. Gains: start on boot, restart on a
**failed healthcheck** (not just on exit), ordered startup, journald logs, no published
DB/Redis ports, daily `pg_dump` with 7-day rotation.

## Install (run as root, once)

```sh
cd /root/pepito/bot
podman-compose build bot api                    # images pepito-bot_bot / pepito-bot_api
podman-compose down                             # stop the compose stack (volumes are kept)
install -m 0644 ../deploy/quadlet/*.network ../deploy/quadlet/*.container /etc/containers/systemd/
install -m 0644 ../deploy/quadlet/pepito-backup.* /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now pepito-db pepito-redis pepito-bot pepito-api
systemctl enable --now pepito-backup.timer
systemctl --no-pager status pepito-db pepito-redis pepito-bot pepito-api
```

`bot/.env` must be `chmod 600` and contain `POSTGRES_PASSWORD`, `REDIS_PASSWORD`,
`DATABASE_URL`, `REDIS_URL`, `BOT_TOKEN`.

## Update the app

```sh
cd /root/pepito/bot && podman-compose build bot api && systemctl restart pepito-bot pepito-api
```

## Roll back to compose

```sh
systemctl disable --now pepito-api pepito-bot pepito-redis pepito-db
rm /etc/containers/systemd/pepito*.{container,network}; systemctl daemon-reload
cd /root/pepito/bot && podman-compose up -d
```

## Checks

`journalctl -u pepito-bot -f` · `podman healthcheck run pepito-bot` ·
`ss -tlnp | grep -E ':5432|:6379'` must print nothing.
