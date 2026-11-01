import os
import time

import pytest

from app.scheduler.jobs import heartbeat as hb


@pytest.mark.asyncio
async def test_beat_creates_fresh_file(tmp_path, monkeypatch):
    f = tmp_path / "hb"
    monkeypatch.setattr(hb, "HEARTBEAT_PATH", f)
    await hb.beat()
    assert f.exists() and hb.is_alive(path=f)


def test_missing_file_is_dead(tmp_path):
    assert hb.is_alive(path=tmp_path / "nope") is False


def test_stale_file_is_dead(tmp_path):
    f = tmp_path / "hb"
    f.touch()
    old = time.time() - 600
    os.utime(f, (old, old))
    assert hb.is_alive(path=f) is False
    assert hb.is_alive(max_age=1000, path=f) is True


def test_scheduler_registers_heartbeat_job():
    from unittest.mock import MagicMock

    from app.scheduler.setup import create_scheduler

    sched = create_scheduler(MagicMock(), MagicMock())
    assert sched.get_job("heartbeat") is not None
