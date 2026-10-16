#!/usr/bin/env bash
# Mobile menu smoke for pepitopet.ru via shared browserless (:3001).
set -euo pipefail

TOKEN="${BROWSERLESS_TOKEN:-localdev}"
BL="${BROWSERLESS_URL:-http://127.0.0.1:3001}"
URL="${PEITO_URL:-https://pepitopet.ru/}"
OUT_DIR="${1:-/root/pepito/odoo/artifacts/mobile-menu-qa}"
mkdir -p "$OUT_DIR"
JS="$OUT_DIR/menu_smoke.js"
RESULT="$OUT_DIR/menu_smoke_result.json"

# Escape URL for JS string
URL_JS=$(python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$URL")

cat >"$JS" <<EOF
export default async function ({ page }) {
  await page.setViewport({
    width: 390, height: 844, isMobile: true, hasTouch: true, deviceScaleFactor: 2,
  });
  await page.goto(${URL_JS}, {
    waitUntil: "networkidle2",
    timeout: 45000,
  });
  await new Promise((r) => setTimeout(r, 800));
  const btn = await page.\$('button[data-bs-toggle="offcanvas"]');
  if (!btn) return { ok: false, error: "no hamburger" };
  try { await btn.tap(); } catch { await btn.click({ force: true }); }
  await new Promise((r) => setTimeout(r, 1000));
  const after = await page.evaluate(() => {
    const off = document.querySelector("#top_menu_collapse_mobile");
    const cs = off ? getComputedStyle(off) : null;
    const r = off ? off.getBoundingClientRect() : null;
    const links = [...document.querySelectorAll("#top_menu_collapse_mobile a.nav-link")]
      .map((a) => (a.textContent || "").trim()).filter(Boolean);
    return {
      visibility: cs && cs.visibility,
      display: cs && cs.display,
      position: cs && cs.position,
      rect: r && { x: r.x, y: r.y, w: r.width, h: r.height },
      links,
      backdrop: !!document.querySelector(".offcanvas-backdrop"),
      iconFilter: document.querySelector(".navbar-toggler-icon")
        ? getComputedStyle(document.querySelector(".navbar-toggler-icon")).filter
        : null,
    };
  });
  const shot = await page.screenshot({ fullPage: false, encoding: "base64" });
  const ok =
    after.visibility === "visible" &&
    after.rect &&
    after.rect.w > 100 &&
    after.rect.h > 200 &&
    after.links.length >= 2;
  return { ok, after, screenshot_b64: shot };
}
EOF

echo "== browserless health =="
curl -sf --max-time 5 "${BL}/json/version?token=${TOKEN}" | head -c 160
echo

echo "== mobile menu click test =="
curl -sf --max-time 90 -X POST "${BL}/chromium/function?token=${TOKEN}" \
  -H 'Content-Type: application/javascript' \
  --data-binary @"$JS" \
  -o "$RESULT"

python3 - "$RESULT" "$OUT_DIR" <<'PY'
import json, base64, sys
from pathlib import Path
result_path, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
data = json.loads(result_path.read_text())
if "screenshot_b64" in data:
    (out_dir / "smoke_open.png").write_bytes(base64.b64decode(data["screenshot_b64"]))
    del data["screenshot_b64"]
print(json.dumps(data, ensure_ascii=False, indent=2))
ok = bool(data.get("ok"))
print("STATUS:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
PY
