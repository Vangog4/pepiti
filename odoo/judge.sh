#!/usr/bin/env bash
# judge.sh — verifies the pepito_odoo project before committing changes
# Usage: ./judge.sh [artifacts-dir]
# Exit 0 → all checks passed. Exit != 0 → something broke.

set -euo pipefail
cd "$(dirname "$0")"

ARTIFACTS_DIR="${1:-artifacts}"
mkdir -p "$ARTIFACTS_DIR"
LOG="$ARTIFACTS_DIR/judge-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee "$LOG") 2>&1

PASS=0
FAIL=0

ok()   { echo "  [OK]  $*"; ((PASS++)) || true; }
fail() { echo "  [FAIL] $*"; ((FAIL++)) || true; }
sep()  { echo ""; echo "=== $* ==="; }

echo "judge.sh — pepito_odoo — $(date)"
echo "Log: $LOG"

# ──────────────────────────────────────────────
sep "1. Python syntax — addons/**/*.py"
PY_ERRORS=0
while IFS= read -r -d '' f; do
    if python3 -m py_compile "$f" 2>/dev/null; then
        :
    else
        fail "syntax error: $f"
        python3 -m py_compile "$f" 2>&1 || true
        ((PY_ERRORS++)) || true
    fi
done < <(find addons -name "*.py" -print0 2>/dev/null)

if [[ $PY_ERRORS -eq 0 ]]; then
    ok "All Python files compile clean"
fi

# ──────────────────────────────────────────────
sep "2. Ruff lint — addons/**/*.py"
if command -v uvx &>/dev/null && find addons -name "*.py" -quit 2>/dev/null; then
    uvx ruff check addons/ --select E,F,W,I --output-format concise 2>/dev/null && ok "ruff lint passed" || fail "ruff found issues"
else
    echo "  [SKIP] ruff/uvx not available or no Python files"
fi

# ──────────────────────────────────────────────
sep "3. __manifest__.py in each addon"
MANIFEST_ERRORS=0
for addon_dir in addons/*/; do
    [[ -d "$addon_dir" ]] || continue
    addon_name=$(basename "$addon_dir")
    if [[ -f "$addon_dir/__manifest__.py" ]]; then
        ok "$addon_name/__manifest__.py present"
    else
        fail "$addon_name missing __manifest__.py"
        ((MANIFEST_ERRORS++)) || true
    fi
done
if [[ $MANIFEST_ERRORS -eq 0 && -z "$(ls -A addons/ 2>/dev/null)" ]]; then
    ok "No addons yet — skipping manifest check"
fi

# ──────────────────────────────────────────────
sep "3. XML syntax — addons/**/*.xml"
XML_ERRORS=0
if command -v xmllint &>/dev/null; then
    while IFS= read -r -d '' f; do
        if xmllint --noout "$f" 2>/dev/null; then
            :
        else
            fail "XML error: $f"
            xmllint --noout "$f" 2>&1 || true
            ((XML_ERRORS++)) || true
        fi
    done < <(find addons -name "*.xml" -print0 2>/dev/null)
    if [[ $XML_ERRORS -eq 0 ]]; then
        ok "All XML files are well-formed"
    fi
else
    echo "  [SKIP] xmllint not installed — skipping XML check"
fi

# ──────────────────────────────────────────────
sep "4. Odoo container health"
if podman ps --filter name=odoo_pepito_app --format "{{.Status}}" 2>/dev/null | grep -q "Up"; then
    HEALTH=$(curl -sf http://127.0.0.1:8071/web/health 2>/dev/null || echo "unreachable")
    if echo "$HEALTH" | grep -qi "ok\|status.*200\|{"; then
        ok "Odoo responding at http://127.0.0.1:8071/web/health"
    else
        fail "Odoo health endpoint returned: $HEALTH"
    fi
else
    echo "  [SKIP] odoo_pepito_app not running — skipping live health check"
fi

# ──────────────────────────────────────────────
sep "5. Critical files present"
REQUIRED_FILES=(
    "podman-compose.yml"
    "config/odoo.conf"
    "judge.sh"
    "../AGENTS.md"
)
for f in "${REQUIRED_FILES[@]}"; do
    if [[ -f "$f" ]]; then
        ok "$f"
    else
        fail "$f missing"
    fi
done

# ──────────────────────────────────────────────
sep "Summary"
echo "Passed: $PASS  Failed: $FAIL"
echo ""

if [[ $FAIL -gt 0 ]]; then
    echo "EXIT 1 — fix failures above, then re-run judge.sh"
    exit 1
else
    echo "EXIT 0 — all checks passed, safe to commit"
    exit 0
fi
