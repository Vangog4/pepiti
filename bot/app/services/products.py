"""Premium product catalog. Prices/durations live only in ``rules.json`` -> ``products``."""

from __future__ import annotations

from dataclasses import dataclass

from app.logic.rules import rule

# Telegram Stars subscription period is fixed by the platform: 30 days in seconds.
STARS_SUBSCRIPTION_PERIOD = 2592000


@dataclass(frozen=True)
class Product:
    code: str
    stars: int
    rub: int
    days: int
    recurring: bool


def _load() -> dict[str, Product]:
    raw = rule("products", {}) or {}
    return {
        code: Product(
            code=code,
            stars=int(v["stars"]),
            rub=int(v["rub"]),
            days=int(v["days"]),
            recurring=bool(v.get("recurring", False)),
        )
        for code, v in raw.items()
    }


PRODUCTS: dict[str, Product] = _load()


def get_product(code: str | None) -> Product | None:
    return PRODUCTS.get(code or "")
