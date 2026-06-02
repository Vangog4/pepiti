#!/usr/bin/env bash
# judge.sh — MVP validation script for pepito-bot
# Exit 0 = passed, non-zero = failed
# Usage: ./judge.sh [log-dir] ["task name"]
#
# Run modes:
#   ./judge.sh                              — local, logs → artifacts/
#   ./judge.sh artifacts                    — explicit log dir
#   ./judge.sh artifacts "feat: add button" — with task name → journal entry
#   Inside container:                       — full import checks with real deps

set -euo pipefail

LOG_DIR="${1:-artifacts}"
TASK_NAME="${2:-}"
mkdir -p "$LOG_DIR"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LOG_FILE="$LOG_DIR/judge-${TIMESTAMP}.log"

PASS=0
FAIL=0
SKIP=0

log() {
    echo "$@" | tee -a "$LOG_FILE"
}

check() {
    local name="$1"
    local result="$2"   # 0 = ok, non-zero = fail
    local detail="${3:-}"
    if [ "$result" -eq 0 ]; then
        log "  [PASS] $name"
        PASS=$((PASS + 1))
    else
        log "  [FAIL] $name${detail:+ — $detail}"
        FAIL=$((FAIL + 1))
    fi
}

skip() {
    log "  [SKIP] $1"
    SKIP=$((SKIP + 1))
}

log "========================================="
log "  Pepito Bot — Judge Run: $TIMESTAMP"
log "========================================="
log ""

# ------------------------------------------------------------------
# 1. Python syntax check (always runs — no external deps needed)
# ------------------------------------------------------------------
log "=== 1. Python syntax check ==="
SYNTAX_ERRORS=0
while IFS= read -r -d '' pyfile; do
    if ! python3 -m py_compile "$pyfile" 2>>"$LOG_FILE"; then
        log "  [FAIL] syntax error: $pyfile"
        SYNTAX_ERRORS=$((SYNTAX_ERRORS + 1))
    fi
done < <(find app -name "*.py" -print0)
check "Python syntax (app/)" "$SYNTAX_ERRORS" "$SYNTAX_ERRORS error(s)"

# ------------------------------------------------------------------
# 1b. Ruff lint + format check
# ------------------------------------------------------------------
log ""
log "=== 1b. Ruff lint ==="
if command -v uvx &>/dev/null; then
    RUFF_LINT_EXIT=0
    uvx ruff check app/ --config pyproject.toml --output-format concise >>"$LOG_FILE" 2>&1 || RUFF_LINT_EXIT=$?
    check "ruff lint" "$RUFF_LINT_EXIT" ""
    RUFF_FMT_EXIT=0
    uvx ruff format app/ --check >>"$LOG_FILE" 2>&1 || RUFF_FMT_EXIT=$?
    check "ruff format" "$RUFF_FMT_EXIT" ""
else
    skip "uvx not found — skipping ruff"
fi

# ------------------------------------------------------------------
# 2. Import smoke-check — requires installed deps (aiogram, pydantic-settings…)
#    Skipped gracefully if deps are missing (e.g. host run outside container)
# ------------------------------------------------------------------
log ""
log "=== 2. Import smoke-check ==="
if python3 -c "import aiogram, pydantic_settings" 2>/dev/null; then
    python3 - 2>>"$LOG_FILE" <<'PYCHECK'
import sys
sys.path.insert(0, ".")

failures = []

modules = [
    "app.core.config",
    "app.domain",
    "app.bot.states",
    "app.bot.keyboards.main_menu",
    "app.bot.keyboards.training",
    "app.core.shop",
    "app.core.shop_recommendations",
]

for m in modules:
    try:
        __import__(m)
        print(f"  [PASS] import {m}")
    except Exception as e:
        print(f"  [FAIL] import {m}: {e}")
        failures.append(m)

if failures:
    print(f"\nFailed imports: {failures}")
    sys.exit(1)
sys.exit(0)
PYCHECK
    check "Core module imports" $? ""
else
    skip "Core module imports (deps not installed — run inside container for full check)"
    log "    Hint: podman exec pepito-bot_bot_1 bash /app/judge.sh"
fi

# ------------------------------------------------------------------
# 3. Config completeness check — static grep, no import needed
# ------------------------------------------------------------------
log ""
log "=== 3. Config env-var presence ==="
python3 - 2>>"$LOG_FILE" <<'PYCHECK'
import sys

with open("app/core/config.py") as f:
    content = f.read()

required = ["BOT_TOKEN", "GEMINI_API_KEY", "DATABASE_URL", "REDIS_URL", "ADMIN_TELEGRAM_IDS"]
missing = [v for v in required if v not in content]

if missing:
    print(f"  [FAIL] Missing env vars in config.py: {missing}")
    sys.exit(1)
print("  [PASS] All required env vars referenced in config.py")
sys.exit(0)
PYCHECK
check "Config env vars" $? ""

# ------------------------------------------------------------------
# 4. Unit/smoke tests — skipped if pytest or deps absent
# ------------------------------------------------------------------
log ""
log "=== 4. Unit tests ==="
if ! python3 -m pytest --version &>/dev/null; then
    skip "pytest not available — install: pip install pytest"
elif ! find tests -name "test_*.py" -not -path "tests/e2e/*" 2>/dev/null | grep -q .; then
    skip "No unit tests found yet (tests/e2e excluded)"
else
    python3 -m pytest tests/ --ignore=tests/e2e -q --tb=short >>"$LOG_FILE" 2>&1
    check "pytest (unit/smoke)" $? ""
fi

# ------------------------------------------------------------------
# 5. Critical file presence check
# ------------------------------------------------------------------
log ""
log "=== 5. Critical file presence ==="
CRITICAL_FILES=(
    "app/main.py"
    "app/core/config.py"
    "app/core/container.py"
    "app/services/ai_service.py"
    "app/bot/handlers/menu.py"
    "alembic.ini"
    "podman-compose.yml"
    "requirements.txt"
    "judge.sh"
)
FILE_ERRORS=0
for f in "${CRITICAL_FILES[@]}"; do
    if [ ! -f "$f" ]; then
        log "  [FAIL] Missing: $f"
        FILE_ERRORS=$((FILE_ERRORS + 1))
    fi
done
check "Critical files present" "$FILE_ERRORS" "$FILE_ERRORS missing"

# ------------------------------------------------------------------
# Summary
# ------------------------------------------------------------------
log ""
log "========================================="
log "  Results: PASS=$PASS  FAIL=$FAIL  SKIP=$SKIP"
log "  Log: $LOG_FILE"
log "========================================="

if [ "$FAIL" -gt 0 ]; then
    VERDICT="FAILED"
    log "  STATUS: FAILED — roll back changes (git checkout -- <files>)"
else
    VERDICT="PASSED"
    log "  STATUS: PASSED — safe to commit"
fi

# ------------------------------------------------------------------
# Journal entry — append to docs/journal/YYYY-MM-DD.md
# ------------------------------------------------------------------
JOURNAL_DIR="docs/journal"
mkdir -p "$JOURNAL_DIR"
JOURNAL_FILE="$JOURNAL_DIR/$(date +%Y-%m-%d).md"
RUN_TIME=$(date +"%H:%M")
CHANGED_FILES=$(git diff --name-only HEAD 2>/dev/null || echo "(no git diff available)")

{
    echo ""
    echo "## ${RUN_TIME} — ${TASK_NAME:-<no task name>}"
    echo ""
    echo "- **Verdict:** ${VERDICT}"
    echo "- **Commit:** (fill after git commit)"
    echo "- **Judge:** PASS=${PASS} FAIL=${FAIL} SKIP=${SKIP}"
    echo "- **Log:** ${LOG_FILE}"
    echo "- **Changed files:**"
    if [ -n "$CHANGED_FILES" ]; then
        while IFS= read -r f; do
            echo "  - \`${f}\`"
        done <<< "$CHANGED_FILES"
    else
        echo "  - (none)"
    fi
} >> "$JOURNAL_FILE"

log ""
log "  Journal: $JOURNAL_FILE"

if [ "$VERDICT" = "FAILED" ]; then
    exit 1
else
    exit 0
fi
