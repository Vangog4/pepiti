"""Rubles via Telegram Payments (T-Bank). DORMANT unless configured.

Enabled only when BOTH are set in bot/.env:
  TBANK_PROVIDER_TOKEN  provider token from BotFather (Payments -> T-Bank)
  TBANK_PROVIDER_DATA   the receipt (54-FZ) ``provider_data`` JSON, as the provider documents it,
                        with placeholders %TITLE% (JSON string, quoted), %KOP% (amount in
                        kopecks), %RUB% (whole rubles), %CODE% (product code, JSON string).

We deliberately do NOT invent the fiscal receipt schema: it is defined by the provider and a
wrong receipt means rejected payments or an incorrect tax document.
"""

from __future__ import annotations

import json
import logging

from app.core.config import settings
from app.services.products import Product

logger = logging.getLogger(__name__)
CURRENCY = "RUB"
PROVIDER = "tbank"
RUB_PLAN_SUFFIX = "_rub"


def rub_enabled() -> bool:
    return bool(
        (settings.TBANK_PROVIDER_TOKEN or "").strip()
        and (settings.TBANK_PROVIDER_DATA or "").strip()
    )


def kopecks(product: Product) -> int:
    return int(product.rub) * 100


def rub_plan_code(product: Product) -> str:
    return f"{product.code}{RUB_PLAN_SUFFIX}"


def render_provider_data(product: Product, title: str) -> str | None:
    """Fill the owner's template. Returns None (never a half-valid receipt) on any problem."""
    template = settings.TBANK_PROVIDER_DATA or ""
    rendered = (
        template.replace("%TITLE%", json.dumps(title, ensure_ascii=False))
        .replace("%CODE%", json.dumps(product.code))
        .replace("%KOP%", str(kopecks(product)))
        .replace("%RUB%", str(int(product.rub)))
    )
    try:
        json.loads(rendered)
    except ValueError:
        logger.error("TBANK_PROVIDER_DATA is not valid JSON after substitution; rubles disabled")
        return None
    return rendered
