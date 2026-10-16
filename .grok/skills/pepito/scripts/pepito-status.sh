#!/usr/bin/env bash
# Quick Pepito status — used by skill / manual /pepito check
set -euo pipefail
export PATH="/root/.nvm/versions/node/v22.22.2/bin:${PATH:-}"

echo "=== Pepito status $(date '+%Y-%m-%d %H:%M') ==="
echo ""
echo "--- SESSION_NOTES (head) ---"
head -25 /root/pepito/SESSION_NOTES.md 2>/dev/null || echo "(missing)"
echo ""
echo "--- agent_health ---"
python3 /root/agents/tools/agent_health.py 2>/dev/null || echo "(agent_health failed)"
echo ""
echo "--- containers ---"
podman ps --filter name=pepito --format 'table {{.Names}}\t{{.Status}}' 2>/dev/null
podman ps --filter name=odoo_pepito --format 'table {{.Names}}\t{{.Status}}' 2>/dev/null
echo ""
echo "Tips:"
echo "  judge:      cd /root/pepito/bot && ./judge.sh"
echo "  regression: bash /root/agents/tools/agent_regression.sh pepito"
echo "  skill:      /pepito  or  read ~/.grok/skills/pepito/SKILL.md"
