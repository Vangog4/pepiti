"""Liveness signal for the container healthcheck.

The scheduler touches a file every 30 s. A hung event loop (polling stuck, deadlock)
stops the touches, the file goes stale, the healthcheck fails and systemd restarts the
container — a plain "process is running" check cannot catch that.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

HEARTBEAT_PATH = Path(os.getenv("PEPITO_HEARTBEAT_FILE", "/tmp/pepito.heartbeat"))  # noqa: S108
MAX_AGE_SEC = 180


async def beat() -> None:
    HEARTBEAT_PATH.touch()
    os.utime(HEARTBEAT_PATH, None)


def is_alive(
    max_age: float = MAX_AGE_SEC, path: Path | None = None, now: float | None = None
) -> bool:
    p = path or HEARTBEAT_PATH
    try:
        age = (now or time.time()) - p.stat().st_mtime
    except OSError:
        return False
    return age < max_age


if __name__ == "__main__":  # `python -m app.scheduler.jobs.heartbeat` = container HealthCmd
    sys.exit(0 if is_alive() else 1)
