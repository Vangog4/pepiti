"""A/B pricing. OFF unless ``ab.enabled`` is true in rules.json.

Config (rules.json):
  "ab": {"enabled": true, "salt": "...", "variants": {"B": {"weight": 30}}}
  "products": {"premium_1m": {..., "variants": {"B": {"stars": 800}}}}

``control`` gets the remaining weight and the catalog price. Assignment is a stable hash of
(salt, user id), so a user always sees the same price. Malformed config is ignored, never
raised: a typo must not take payments down.
"""

from __future__ import annotations

import hashlib
from typing import Any

from app.logic.rules import rule
from app.services.products import Product

CONTROL = "control"


def ab_enabled() -> bool:
    return bool(rule("ab.enabled", False))


def _weights() -> dict[str, int]:
    """Valid variant weights, capped so the total never exceeds 100."""
    raw = rule("ab.variants", {}) or {}
    out: dict[str, int] = {}
    total = 0
    for name in sorted(raw):
        try:
            w = int(raw[name]["weight"])
        except (KeyError, TypeError, ValueError):
            continue
        if name == CONTROL or w <= 0:
            continue
        w = min(w, 100 - total)
        if w <= 0:
            break
        out[name] = w
        total += w
    return out


def variant_for(user_id: int | None) -> str:
    if not ab_enabled() or not user_id:
        return CONTROL
    weights = _weights()
    if not weights:
        return CONTROL
    salt = str(rule("ab.salt", "pepito"))
    bucket = int(hashlib.sha256(f"{salt}:{user_id}".encode()).hexdigest(), 16) % 100
    edge = 100 - sum(weights.values())  # control owns [0, edge)
    if bucket < edge:
        return CONTROL
    for name in sorted(weights):
        edge += weights[name]
        if bucket < edge:
            return name
    return CONTROL


def _variant_stars(code: str, variant: str) -> int | None:
    cfg: Any = (rule(f"products.{code}.variants", {}) or {}).get(variant)
    try:
        stars = int(cfg["stars"])
    except (KeyError, TypeError, ValueError):
        return None
    # <= 4 digits keeps plan buttons within 14 characters in every locale
    return stars if 0 < stars <= 9999 else None


def stars_for(product: Product, variant: str) -> int:
    if variant == CONTROL or not ab_enabled():
        return product.stars
    return _variant_stars(product.code, variant) or product.stars


def allowed_stars(product: Product) -> set[int]:
    """Every price a legitimate invoice for this product can carry (for payment checks)."""
    prices = {product.stars}
    if ab_enabled():
        for name in _weights():
            price = _variant_stars(product.code, name)
            if price:
                prices.add(price)
    return prices
