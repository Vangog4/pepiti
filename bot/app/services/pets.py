"""Several dogs per owner: limits and which dog is active. Pure functions."""

from __future__ import annotations

from typing import Any

from app.logic.rules import rule


def pet_limit(premium: bool) -> int:
    key = "pets.premium_max" if premium else "pets.free_max"
    return int(rule(key, 3 if premium else 1))


def allowed_pets(pets: list[Any], premium: bool) -> list[Any]:
    """The dogs the owner may use now: the oldest ``limit`` ones. After Premium lapses the
    newer dogs stay stored and visible but locked (read-only); nothing is deleted."""
    return sorted(pets, key=lambda p: p.id)[: pet_limit(premium)]


def resolve_active(pets: list[Any], active_id: int | None, premium: bool) -> Any | None:
    allowed = allowed_pets(pets, premium)
    if not allowed:
        return None
    return next((p for p in allowed if p.id == active_id), allowed[0])


def can_add(count: int, premium: bool) -> str:
    """ok | need_premium | max"""
    if count < pet_limit(premium):
        return "ok"
    if not premium and count < pet_limit(True):
        return "need_premium"
    return "max"
