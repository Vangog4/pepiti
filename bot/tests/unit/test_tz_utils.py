"""Unit tests for app/core/tz_utils.py — 8 cases."""

import sys

sys.path.insert(0, ".")

import pytest
from app.core.tz_utils import _parse_offset, local_to_utc, utc_to_local


def test_parse_offset_none():
    assert _parse_offset(None) == 0


def test_parse_offset_utc():
    assert _parse_offset("UTC") == 0


def test_parse_offset_positive():
    assert _parse_offset("UTC+3") == 3


def test_parse_offset_negative():
    assert _parse_offset("UTC-5") == -5


def test_local_to_utc_moscow():
    # Moscow UTC+3: 10:00 local → 07:00 UTC
    assert local_to_utc("10:00", "UTC+3") == "07:00"


def test_local_to_utc_negative_offset():
    # UTC-5: 02:00 local → 07:00 UTC
    assert local_to_utc("02:00", "UTC-5") == "07:00"


def test_utc_to_local_round_trip():
    # UTC+3: 07:00 UTC → 10:00 local
    assert utc_to_local("07:00", "UTC+3") == "10:00"


def test_local_to_utc_day_wrap():
    # UTC+12: 02:00 local − 12h = 14:00 previous UTC day (wraps to 14:00)
    assert local_to_utc("02:00", "UTC+12") == "14:00"
