#!/usr/bin/env bash
# Install payment_tinkoff on pepito Odoo and restart.
set -euo pipefail

DB="${ODOO_DB:-odoo_user_pepito}"
CONTAINER="${ODOO_CONTAINER:-odoo_pepito_app}"

echo "== Install payment_tinkoff on $CONTAINER / $DB =="
podman exec "$CONTAINER" odoo -d "$DB" \
  -i payment_tinkoff \
  --stop-after-init \
  --http-port=8099 \
  --gevent-port=8098

echo "== Restart Odoo =="
podman restart "$CONTAINER"
sleep 8
curl -sf --max-time 15 "http://127.0.0.1:8071/web/health" && echo " health OK" || echo " health wait..."

echo "== Provider row =="
podman exec odoo_pepito_db psql -U odoo_user_pepito -d "$DB" -c \
  "SELECT id, code, state, is_published, tinkoff_terminal_key IS NOT NULL AS has_key
   FROM payment_provider WHERE code='tinkoff';" 2>/dev/null \
  || podman exec odoo_pepito_db psql -U odoo_user_pepito -d "$DB" -c \
  "SELECT id, code, state, is_published FROM payment_provider WHERE code='tinkoff';"

echo "Done. Open Website → Payment Providers → Т-Банк and enter TerminalKey/Password."
echo "Notification URL: https://pepitopet.ru/payment/tinkoff/notification"
