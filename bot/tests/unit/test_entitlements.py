"""Premium must be decided by expiry date, never by the cached is_premium flag alone."""

from datetime import datetime, timedelta
from types import SimpleNamespace

from app.services.entitlements import has_premium


def _u(flag, exp):
    return SimpleNamespace(is_premium=flag, subscription_expires_at=exp)


def test_active_when_expiry_in_future():
    now = datetime(2026, 11, 1, 12)
    assert has_premium(_u(True, now + timedelta(hours=1)), now) is True


def test_expired_flag_still_true_is_not_premium():
    now = datetime(2026, 11, 1, 12)
    assert has_premium(_u(True, now - timedelta(seconds=1)), now) is False


def test_flag_without_expiry_is_lifetime():
    assert has_premium(_u(True, None)) is True


def test_no_flag_no_expiry_is_free():
    assert has_premium(_u(False, None)) is False


def test_future_expiry_with_stale_false_flag_is_premium():
    now = datetime(2026, 11, 1, 12)
    assert has_premium(_u(False, now + timedelta(days=1)), now) is True


def test_none_user():
    assert has_premium(None) is False
