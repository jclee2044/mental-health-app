"""Short optional wait; bounded actual workers, including after caller timeout."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from threading import BoundedSemaphore
from .service import Retrieval


class BoundedLookup:
    def __init__(self, service, *, timeout=2.0):
        self.service = service
        self.timeout = timeout
        self.slots = BoundedSemaphore(2)
        self.pool = ThreadPoolExecutor(max_workers=2, thread_name_prefix="reframing")
        self.closed = False

    async def prepare(self, message, *, allow_reference_lookup=True):
        if allow_reference_lookup is not True:
            return Retrieval("skipped")
        if getattr(self.service, "configuration_error", False):
            return Retrieval("unavailable")
        if self.service.embedder is None:
            return Retrieval("off")
        if self.closed or not self.slots.acquire(blocking=False):
            return Retrieval("unavailable")
        def work():
            try:
                return self.service.prepare(message, allow_reference_lookup=True, budget=6000)
            finally:
                self.slots.release()
        try:
            future = self.pool.submit(work)
        except RuntimeError:
            self.slots.release()
            return Retrieval("unavailable")
        try:
            # Shield actual work: a timed-out/cancelled waiter cannot free its slot.
            return await asyncio.wait_for(asyncio.shield(asyncio.wrap_future(future)), self.timeout)
        except TimeoutError:
            return Retrieval("unavailable")

    def close(self):
        self.closed = True
        self.pool.shutdown(wait=False, cancel_futures=False)
