import asyncio
import time

from app.providers.coordinator import BaseCoordinator


def test_coordinator_refresh_calls_update_fn():
    called = {"count": 0}

    async def upd():
        called["count"] += 1

    coord = BaseCoordinator(update_fn=upd)
    asyncio.run(coord.refresh())
    assert called["count"] == 1


def test_coordinator_start_and_stop():
    called = {"count": 0}

    async def upd():
        called["count"] += 1
        # small sleep to allow loop scheduling
        await asyncio.sleep(0.001)

    coord = BaseCoordinator(update_fn=upd, update_interval=0.01, name="test-coord", shutdown_timeout=1.0)

    async def runner():
        coord.start()
        # allow loop to run a bit
        await asyncio.sleep(0.02)
        assert coord.is_running
        await coord.stop()
        assert not coord.is_running

    asyncio.run(runner())
    assert called["count"] >= 1


def test_coordinator_stop_without_start_is_noop():
    async def runner():
        coord = BaseCoordinator(update_fn=lambda: None)
        # stopping when not started should be fine
        await coord.stop()

    asyncio.run(runner())
