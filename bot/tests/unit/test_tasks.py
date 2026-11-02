import asyncio
import gc
import logging

import pytest

from app.core import tasks


@pytest.mark.asyncio
async def test_spawn_keeps_reference_and_finishes():
    done = asyncio.Event()

    async def work():
        await asyncio.sleep(0.01)
        done.set()

    t = tasks.spawn(work())
    assert t in tasks._tasks
    del t
    gc.collect()
    await asyncio.wait_for(done.wait(), 1)
    await asyncio.sleep(0)
    assert not tasks._tasks


@pytest.mark.asyncio
async def test_spawn_logs_failures(caplog):
    async def boom():
        raise RuntimeError("bg-fail")

    with caplog.at_level(logging.ERROR):
        tasks.spawn(boom(), name="boom")
        await asyncio.sleep(0.05)
    assert "bg-fail" in caplog.text
