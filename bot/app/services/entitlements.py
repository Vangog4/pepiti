"""Single source of truth for "does this user have Premium right now"."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


def has_premium(user: Any, now: datetime | None = None) -> bool:
    """True while ``subscription_expires_at`` is in the future (or lifetime grant).

    The ``is_premium`` column is a cache refreshed by the expire job; it can lag
    up to the job interval, so it must never be trusted on its own.
    """
    if user is None:
        return False
    exp = getattr(user, "subscription_expires_at", None)
    if exp is None:
        # Manually granted lifetime premium: flag set, no expiry. Every revoke/expire
        # path clears both fields together, so this state is never a stale leftover.
        return bool(getattr(user, "is_premium", False))
    if exp.tzinfo is not None:
        exp = exp.astimezone(UTC).replace(tzinfo=None)
    return exp > (now or datetime.utcnow())
