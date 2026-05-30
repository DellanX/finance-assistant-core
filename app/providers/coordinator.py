"""Coordinator helpers for providers.

`BaseCoordinator.start()` will only schedule its background loop when an
asyncio event loop is already running. This avoids creating orphaned tasks in
synchronous test contexts (for example, when test suites import provider
modules but do not run an event loop). Test code should use the `coordinator_factory`
fixture to attach `TestCoordinator` instances to providers when tests need a
coordinator without running real background loops.
"""

from typing import Any, Callable, Optional


class CoordinatorInterface:
    """Minimal coordinator interface used by the registry and tests.

    Implementations should provide `start()`, `stop()` and optional `refresh()`.
    Methods may be sync or async; callers should handle coroutines.
    """

    def start(self) -> Any:
        raise NotImplementedError()

    async def stop(self) -> Any:
        raise NotImplementedError()

    def refresh(self) -> Any:
        raise NotImplementedError()


class TestCoordinator(CoordinatorInterface):
    """A simple synchronous coordinator useful for tests.

    It records whether it's running and provides sync wrappers for lifecycle.
    """

    def __init__(self):
        self.is_running = False

    def start(self):
        self.is_running = True

    async def stop(self):
        self.is_running = False

    def refresh(self):
        # no-op; tests may override this attribute
        return None


def ensure_coordinator(provider: Any, factory: Optional[Callable[[Any], CoordinatorInterface]] = None) -> CoordinatorInterface:
    """Ensure `provider.coordinator` exists.

    If `factory` is provided, it will be called with the provider to produce a coordinator.
    If provider already has a coordinator, it's returned as-is.
    """
    coord = getattr(provider, "coordinator", None)
    if coord is not None:
        return coord
    if factory is not None:
        coord = factory(provider)
        provider.coordinator = coord
        return coord
    # default: attach a TestCoordinator so tests don't start background tasks
    coord = TestCoordinator()
    provider.coordinator = coord
    return coord

import asyncio
import logging
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class BaseCoordinator:
    """Simple coordinator for polling/updating provider state.

    Providers/integrations can subclass this to implement periodic updates and
    to expose current data to platform modules.

    Features added:
    - Logging on `start`/`stop`/`refresh` so lifecycle events are visible.
    - `is_running` property to inspect runtime state.
    """

    def __init__(self, update_fn: Callable[[], None], update_interval: int = 30, name: Optional[str] = None, shutdown_timeout: float = 5.0):
        self.update_fn = update_fn
        self.update_interval = update_interval
        self._task: Optional[asyncio.Task] = None
        self._stopping = False
        self.name = name or "coordinator"
        # how long to wait (seconds) for the task to finish after cancel
        self.shutdown_timeout = float(shutdown_timeout)

    @property
    def is_running(self) -> bool:
        return self._task is not None and not self._task.done()

    async def _loop(self):
        try:
            while not self._stopping:
                try:
                    logger.debug("%s: running update function", self.name)
                    await self.update_fn()
                except asyncio.CancelledError:
                    # Propagate cancellation to allow immediate shutdown
                    raise
                except Exception:
                    logger.exception("%s: update function crashed", self.name)
                # Sleep in cancellable way
                try:
                    await asyncio.sleep(self.update_interval)
                except asyncio.CancelledError:
                    raise
        except asyncio.CancelledError:
            logger.debug("%s: coordinator loop cancelled", self.name)
            # exit silently on cancellation
            return

    def start(self):
        if self._task is None:
            logger.info("%s: starting coordinator", self.name)
            self._stopping = False
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                # No running loop in this thread/context — do not start background task.
                logger.debug("%s: no running event loop, deferring start", self.name)
                return
            # schedule the coordinator loop on the running event loop
            self._task = loop.create_task(self._loop())

    async def stop(self):
        logger.info("%s: stopping coordinator", self.name)
        self._stopping = True
        if self._task:
            try:
                # Cancel the running task to speed up shutdown (interrupt sleeps)
                self._task.cancel()
                # Wait up to shutdown_timeout seconds for the task to finish
                try:
                    await asyncio.wait_for(self._task, timeout=self.shutdown_timeout)
                except asyncio.TimeoutError:
                    logger.warning("%s: coordinator did not stop within %s seconds", self.name, self.shutdown_timeout)
                except asyncio.CancelledError:
                    logger.debug("%s: coordinator task cancelled during stop", self.name)
            except Exception:
                logger.exception("%s: error while stopping coordinator", self.name)
            finally:
                self._task = None

    async def refresh(self):
        """Trigger an immediate update."""
        logger.info("%s: refreshing coordinator", self.name)
        await self.update_fn()
