"""Story cards: SVG templates -> PNG via resvg (no browser, ~3 MB wheel).

Canvas 1080x1920 rendered at 2x (2160x3840) so text stays crisp when shared to Stories.
All user-controlled text is sanitized (emoji stripped: the bundled font has no emoji glyphs),
fitted to the canvas, wrapped and XML-escaped. Rendering is CPU work: it runs in a thread and
at most ``MAX_PARALLEL`` renders run at once.
"""

from __future__ import annotations

import asyncio
import re
from html import escape
from pathlib import Path

CARD_W, CARD_H = 1080, 1920
SCALE = 2.0
MAX_PARALLEL = 2
HANDLE = "@pepitopetbot"

_ASSETS = Path(__file__).resolve().parents[1] / "assets"
FONT_FILES = [str(_ASSETS / "DejaVuSans.ttf"), str(_ASSETS / "DejaVuSans-Bold.ttf")]
_FONT = "DejaVu Sans"
_BOLD_CHAR_W = 0.72  # average glyph width / font size for DejaVu Sans Bold (conservative)
_REG_CHAR_W = 0.60

THEMES = {
    "streak": ("#FF9A3C", "#FF5E62"),
    "badge": ("#8E54E9", "#4776E6"),
    "week": ("#0B8A83", "#1E9E63"),
    "passport": ("#1B5E9B", "#2C93C9"),
}

_UNRENDERABLE = re.compile("[\U0001f000-\U0001faff←-⇿⌀-⏿☀-➿⬀-⯿︀-️​-‏⁠⃣]")

_semaphore: asyncio.Semaphore | None = None


def strip_unrenderable(text: str) -> str:
    """Drop emoji/variation selectors the font cannot draw; collapse spaces."""
    return " ".join(_UNRENDERABLE.sub("", text or "").split())


def wrap_text(text: str, max_chars: int, max_lines: int | None = None) -> list[str]:
    """Greedy word wrap; words longer than a line are hard-split; optional ellipsis cap."""
    words = (text or "").split()
    lines: list[str] = []
    cur = ""
    for word in words:
        while len(word) > max_chars:
            if cur:
                lines.append(cur)
                cur = ""
            lines.append(word[:max_chars])
            word = word[max_chars:]
        if not cur:
            cur = word
        elif len(cur) + 1 + len(word) <= max_chars:
            cur += " " + word
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1][: max_chars - 1].rstrip() + "…"
    return lines


def ellipsize(text: str, max_chars: int) -> str:
    """Shorten with an ellipsis (never a silent mid-word cut)."""
    text = text or ""
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1].rstrip(" ,;:-") + "…"


def fit_size(
    lines: list[str], max_width: float, base: int, min_size: int, bold: bool = True
) -> int:
    """Largest font size <= base so the longest line fits ``max_width``; never below min."""
    longest = max((len(line) for line in lines), default=0)
    if longest == 0:
        return base
    per_char = _BOLD_CHAR_W if bold else _REG_CHAR_W
    size = int(max_width / (longest * per_char))
    return max(min_size, min(base, size))


def _text(
    x: float,
    y: float,
    size: int,
    content: str,
    *,
    bold=False,
    fill="#fff",
    anchor="middle",
    opacity: float | None = None,
) -> str:
    weight = ' font-weight="700"' if bold else ""
    op = f' fill-opacity="{opacity}"' if opacity is not None else ""
    return (
        f'<text x="{x}" y="{y}" font-family="{_FONT}"{weight} font-size="{size}" '
        f'fill="{fill}" text-anchor="{anchor}"{op}>{escape(content, quote=True)}</text>'
    )


def build_svg(kind: str, data: dict) -> str:
    """One layout, four themes. ``data``: big, caption, headline, optional rows[(label, value)]."""
    if kind not in THEMES:
        raise ValueError(f"unknown card kind: {kind}")
    c1, c2 = THEMES[kind]
    cx, cy, r = CARD_W / 2, 560, 260
    inner = 2 * r * 0.78  # text must stay inside the circle

    big_text = strip_unrenderable(str(data.get("big", ""))) or "—"
    if len(big_text) <= 5:  # a number / short token: one huge line
        big_lines, big_base, big_min = [big_text], 340, 90
    else:  # a name: up to two fitted lines inside the circle
        big_lines = wrap_text(big_text, 12, max_lines=2)
        big_base, big_min = 150, 50
    big_size = fit_size(big_lines, inner, base=big_base, min_size=big_min)
    caption = wrap_text(strip_unrenderable(str(data.get("caption", ""))), 26, max_lines=2)
    headline = wrap_text(strip_unrenderable(str(data.get("headline", ""))), 18, max_lines=3)
    h_size = fit_size(headline, CARD_W - 160, base=84, min_size=52)
    rows = [
        (ellipsize(strip_unrenderable(str(a)), 20), ellipsize(strip_unrenderable(str(b)), 20))
        for a, b in (data.get("rows") or [])
    ][:5]

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CARD_W}" height="{CARD_H}" '
        f'viewBox="0 0 {CARD_W} {CARD_H}">',
        f'<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/>'
        "</linearGradient></defs>",
        f'<rect width="{CARD_W}" height="{CARD_H}" fill="url(#g)"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#fff" fill-opacity="0.18"/>',
    ]
    line_h = int(big_size * 1.12)
    first_y = cy + big_size * 0.36 - (len(big_lines) - 1) * line_h / 2
    for i, line in enumerate(big_lines):
        parts.append(_text(cx, first_y + i * line_h, big_size, line, bold=True))
    y = cy + r + 100
    for line in caption:
        parts.append(_text(cx, y, 56, line, opacity=0.95))
        y += 70
    y = max(y + 110, 1090)
    for line in headline:
        parts.append(_text(cx, y, h_size, line, bold=True))
        y += int(h_size * 1.18)
    if rows:
        y = max(y + 40, 1420)
        for label, value in rows:
            parts.append(_text(120, y, 46, label, opacity=0.95, anchor="start"))
            value_size = fit_size([value], 420, base=54, min_size=34)
            parts.append(_text(960, y, value_size, value, bold=True, anchor="end"))
            y += 84
    parts.append(
        '<rect x="290" y="1700" width="500" height="90" rx="45" fill="#fff" fill-opacity="0.92"/>'
    )
    parts.append(_text(cx, 1762, 40, HANDLE, bold=True, fill=c2))
    parts.append("</svg>")
    return "".join(parts)


def _render_sync(svg: str, scale: float) -> bytes:
    import resvg_py

    return resvg_py.svg_to_bytes(
        svg_string=svg, zoom=scale, skip_system_fonts=True, font_files=FONT_FILES
    )


async def render_card(kind: str, data: dict, scale: float = SCALE) -> bytes:
    """PNG bytes (2160x3840 at the default 2x). Raises ValueError for an unknown kind.

    Takes ~3-5 s at 2x on a busy box; callers must not await it on the hot path of a tap
    without a progress message. ``scale`` exists so tests can render small."""
    global _semaphore
    if _semaphore is None:
        _semaphore = asyncio.Semaphore(MAX_PARALLEL)
    svg = build_svg(kind, data)
    async with _semaphore:
        return await asyncio.to_thread(_render_sync, svg, scale)
