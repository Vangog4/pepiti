"""Timezone utilities for UTC±N offset strings (e.g. 'UTC', 'UTC+3', 'UTC-5')."""


def _parse_offset(tz: str | None) -> int:
    """Return integer hour offset from a 'UTC±N' string. Returns 0 for invalid/None."""
    if not tz or tz == "UTC":
        return 0
    tz = tz.strip()
    if not tz.startswith("UTC"):
        return 0
    sign_and_num = tz[3:]  # "+3", "-5", ""
    if not sign_and_num:
        return 0
    try:
        return int(sign_and_num)
    except ValueError:
        return 0


def local_to_utc(local_time: str, tz: str | None) -> str:
    """Convert 'HH:MM' local time to UTC string given a 'UTC±N' offset."""
    offset = _parse_offset(tz)
    h, m = int(local_time[:2]), int(local_time[3:])
    total = (h * 60 + m - offset * 60) % (24 * 60)
    return f"{total // 60:02d}:{total % 60:02d}"


def utc_to_local(utc_time: str, tz: str | None) -> str:
    """Convert 'HH:MM' UTC to local time string given a 'UTC±N' offset."""
    offset = _parse_offset(tz)
    h, m = int(utc_time[:2]), int(utc_time[3:])
    total = (h * 60 + m + offset * 60) % (24 * 60)
    return f"{total // 60:02d}:{total % 60:02d}"
