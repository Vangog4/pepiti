#!/usr/bin/env python3
"""Visual QA MCP server — proxies screenshot/DOM requests to browserless/chromium (pepito_odoo)."""

import base64
import json

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("visual-qa-pepito")

BROWSERLESS = "http://127.0.0.1:3002"
TOKEN = "localdev"
# Internal hostname: use when browserless and Odoo are on the same podman network.
ODOO_INTERNAL = "http://web_pepito:8069"
# Host-side URL: use from scripts running outside containers.
ODOO_HOST = "http://127.0.0.1:8071"


@mcp.tool()
async def screenshot(
    url: str = ODOO_INTERNAL,
    full_page: bool = True,
    width: int = 1280,
    height: int = 900,
) -> str:
    """
    Render a page via headless Chromium and return a base64-encoded PNG.

    Default URL targets Odoo through the internal podman network so browserless
    can resolve 'web_pepito' by hostname. Pass url='http://127.0.0.1:8071' to
    use the host-facing port instead.
    """
    async with httpx.AsyncClient(timeout=40) as client:
        resp = await client.post(
            f"{BROWSERLESS}/chromium/screenshot",
            params={"token": TOKEN},
            json={
                "url": url,
                "options": {"fullPage": full_page, "type": "png"},
                "viewport": {"width": width, "height": height},
            },
        )
        resp.raise_for_status()
        return base64.b64encode(resp.content).decode()


@mcp.tool()
async def dom_geometry(
    url: str = ODOO_INTERNAL,
    selector: str = "header, footer, main, .o_website_main_content, section",
    max_elements: int = 40,
) -> str:
    """
    Return bounding-box geometry (top/left/width/height) for all elements
    matching a CSS selector. Useful for diagnosing misaligned/collapsed blocks.
    """
    safe_sel = selector.replace("'", "\\'")
    safe_url = url.replace("'", "\\'")
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
    async with httpx.AsyncClient(timeout=40) as client:
        resp = await client.post(
            f"{BROWSERLESS}/chromium/function",
            params={"token": TOKEN},
            json={"code": code},
        )
        resp.raise_for_status()
        try:
            return json.dumps(json.loads(resp.text), indent=2, ensure_ascii=False)
        except Exception:
            return resp.text


@mcp.tool()
async def browserless_health() -> str:
    """Check whether the pepito browserless container is reachable and healthy."""
    async with httpx.AsyncClient(timeout=5) as client:
        try:
            resp = await client.get(f"{BROWSERLESS}/json/version")
            return f"OK — {resp.status_code}: {resp.text[:200]}"
        except Exception as exc:
            return f"UNREACHABLE: {exc}"


if __name__ == "__main__":
    mcp.run()
