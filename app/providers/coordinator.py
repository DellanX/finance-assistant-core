
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
            loop = asyncio.get_event_loop()
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
