#!/usr/bin/env python3
"""Visual QA MCP server for pepitopet.ru.

Uses shared browserless (amanita :3001) by default to save VDS RAM —
a second chromium on :3002 is optional if CONCURRENT load requires it.
"""

from __future__ import annotations

import base64
import json
import os

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("visual-qa-pepito")

# Prefer shared browserless on 3001; override with BROWSERLESS_URL if needed.
BROWSERLESS = os.getenv("BROWSERLESS_URL", "http://127.0.0.1:3001")
TOKEN = os.getenv("BROWSERLESS_TOKEN", "localdev")

# Defaults: public URL works from any browserless network.
# Internal host only works if browserless is on pepito_internal network.
ODOO_PUBLIC = "https://pepitopet.ru"
ODOO_HOST = "http://127.0.0.1:8071"
ODOO_INTERNAL = "http://web_pepito:8069"


def _bl_url(path: str) -> str:
    return f"{BROWSERLESS.rstrip('/')}{path}"


@mcp.tool()
async def screenshot(
    url: str = ODOO_PUBLIC,
    full_page: bool = True,
    width: int = 1280,
    height: int = 900,
    is_mobile: bool = False,
) -> str:
    """
    Render a page via headless Chromium and return a base64-encoded PNG.

    Defaults to https://pepitopet.ru (reachable from shared browserless).
    Set is_mobile=true for iPhone-like viewport (390x844).
    """
    if is_mobile:
        width, height = 390, 844
    viewport: dict = {"width": width, "height": height}
    if is_mobile:
        viewport.update({"isMobile": True, "hasTouch": True, "deviceScaleFactor": 2})

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            _bl_url("/chromium/screenshot"),
            params={"token": TOKEN},
            json={
                "url": url,
                "options": {"fullPage": full_page, "type": "png"},
                "viewport": viewport,
                "gotoOptions": {"waitUntil": "networkidle2", "timeout": 45000},
            },
        )
        resp.raise_for_status()
        return base64.b64encode(resp.content).decode()


@mcp.tool()
async def dom_geometry(
    url: str = ODOO_PUBLIC,
    selector: str = "header, footer, main, .o_website_main_content, section",
    max_elements: int = 40,
) -> str:
    """Bounding boxes for CSS selector matches (layout QA)."""
    safe_sel = selector.replace("\\", "\\\\").replace("'", "\\'")
    safe_url = url.replace("\\", "\\\\").replace("'", "\\'")
    code = f"""
export default async function({{ page }}) {{
  await page.goto('{safe_url}', {{ waitUntil: 'domcontentloaded', timeout: 25000 }});
  await new Promise(r => setTimeout(r, 800));
  return page.evaluate((sel, max) => {{
    const els = [...document.querySelectorAll(sel)].slice(0, max);
    return JSON.stringify(els.map(el => {{
      const r = el.getBoundingClientRect();
      return {{
        tag: el.tagName,
        id:  el.id   || null,
        cls: (el.className || '').toString().slice(0, 60),
        top:    Math.round(r.top),
        left:   Math.round(r.left),
        width:  Math.round(r.width),
        height: Math.round(r.height),
      }};
    }}));
  }}, '{safe_sel}', {max_elements});
}}
"""
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            _bl_url("/chromium/function"),
            params={"token": TOKEN},
            headers={"Content-Type": "application/javascript"},
            content=code,
        )
        resp.raise_for_status()
        try:
            return json.dumps(json.loads(resp.text), indent=2, ensure_ascii=False)
        except Exception:
            return resp.text


@mcp.tool()
async def mobile_menu_check(url: str = ODOO_PUBLIC) -> str:
    """
    Mobile smoke: open homepage at 390px, tap hamburger, report whether
    offcanvas menu shows links (Главная/Магазин/Блог).
    """
    code = """
export default async function ({ page }) {
  await page.setViewport({
    width: 390, height: 844, isMobile: true, hasTouch: true, deviceScaleFactor: 2,
  });
  await page.goto(%URL%, { waitUntil: 'networkidle2', timeout: 45000 });
  await new Promise(r => setTimeout(r, 800));
  const btn = await page.$('button[data-bs-toggle="offcanvas"]');
  if (!btn) return JSON.stringify({ ok: false, error: 'no hamburger button' });
  await btn.tap().catch(() => btn.click({ force: true }));
  await new Promise(r => setTimeout(r, 1000));
  return page.evaluate(() => {
    const off = document.querySelector('#top_menu_collapse_mobile');
    const cs = off ? getComputedStyle(off) : null;
    const r = off ? off.getBoundingClientRect() : null;
    const links = [...document.querySelectorAll('#top_menu_collapse_mobile a.nav-link')]
      .map(a => (a.textContent || '').trim()).filter(Boolean);
    const ok = !!(off && cs && cs.visibility === 'visible' && r && r.width > 100 && links.length >= 2);
    return JSON.stringify({
      ok,
      visibility: cs && cs.visibility,
      display: cs && cs.display,
      position: cs && cs.position,
      zIndex: cs && cs.zIndex,
      rect: r && { x: r.x, y: r.y, w: r.width, h: r.height },
      links,
      backdrop: !!document.querySelector('.offcanvas-backdrop'),
      iconFilter: (document.querySelector('.navbar-toggler-icon')
        && getComputedStyle(document.querySelector('.navbar-toggler-icon')).filter) || null,
    });
  });
}
""".replace("%URL%", json.dumps(url))

    async with httpx.AsyncClient(timeout=90) as client:
        resp = await client.post(
            _bl_url("/chromium/function"),
            params={"token": TOKEN},
            headers={"Content-Type": "application/javascript"},
            content=code,
        )
        resp.raise_for_status()
        try:
            data = json.loads(resp.text)
            # function may return a JSON string
            if isinstance(data, str):
                data = json.loads(data)
            return json.dumps(data, indent=2, ensure_ascii=False)
        except Exception:
            return resp.text


@mcp.tool()
async def browserless_health() -> str:
    """Check whether browserless is reachable."""
    async with httpx.AsyncClient(timeout=5) as client:
        try:
            resp = await client.get(
                _bl_url("/json/version"),
                params={"token": TOKEN},
            )
            return f"OK — {BROWSERLESS} — {resp.status_code}: {resp.text[:200]}"
        except Exception as exc:
            return f"UNREACHABLE ({BROWSERLESS}): {exc}"


if __name__ == "__main__":
    mcp.run()
