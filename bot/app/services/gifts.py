"""Invoice payloads: a plain product code, or ``gift:<product>:<recipient_telegram_id>``.

Only one-time packs can be gifted (a recurring Stars subscription cannot be bought for
someone else). Anything malformed parses to None and is NEVER granted.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.services.products import Product, get_product

GIFT_PREFIX = "gift"
MAX_PAYLOAD_BYTES = 128  # Telegram's limit for invoice_payload


@dataclass(frozen=True)
class ParsedPayload:
    product: Product
    recipient_tg_id: int | None = None

    @property
    def is_gift(self) -> bool:
        return self.recipient_tg_id is not None


def make_gift_payload(product_code: str, recipient_tg_id: int) -> str:
    payload = f"{GIFT_PREFIX}:{product_code}:{int(recipient_tg_id)}"
    if len(payload.encode()) > MAX_PAYLOAD_BYTES:
        raise ValueError("payload too long")
    return payload


def parse_payload(payload: str | None) -> ParsedPayload | None:
    if not payload or len(payload.encode()) > MAX_PAYLOAD_BYTES:
        return None
    parts = payload.split(":")
    if len(parts) == 1:
        product = get_product(payload)
        return ParsedPayload(product) if product else None
    if len(parts) != 3 or parts[0] != GIFT_PREFIX:
        return None
    product = get_product(parts[1])
    if product is None or product.recurring:
        return None
    try:
        recipient = int(parts[2])
    except ValueError:
        return None
    return ParsedPayload(product, recipient) if recipient > 0 else None


def target_telegram_id(parsed: ParsedPayload, payer_tg_id: int) -> int:
    """Who receives the Premium days."""
    return parsed.recipient_tg_id if parsed.is_gift else payer_tg_id
