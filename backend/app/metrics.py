import time
import asyncio
from dataclasses import dataclass

@dataclass
class Counters:
    uploads_total: int = 0
    upload_bytes_sum: int = 0

@dataclass
class Gauges:
    requests_in_progress: int = 0
    queue_len: int = 0

class Metrics:
    """
    Thread-safe asynchronous metrics tracker for upload system.
    Tracks counts, gauges, and uptime.
    """
    def __init__(self):
        self._lock = asyncio.Lock()
        self.counters = Counters()
        self.gauges = Gauges()
        self.start_time = time.monotonic()

    async def inc_uploads(self, bytes_: int):
        """
        Increment uploads_total and upload_bytes_sum.
        :param bytes_: Size of uploaded file in bytes.
        """
        async with self._lock:
            self.counters.uploads_total += 1
            self.counters.upload_bytes_sum += bytes_

    async def inc_in_progress(self):
        """Increment number of in-progress requests."""
        async with self._lock:
            self.gauges.requests_in_progress += 1

    async def dec_in_progress(self):
        """Decrement number of in-progress requests."""
        async with self._lock:
            self.gauges.requests_in_progress -= 1

    async def set_queue_len(self, n: int):
        """Set the queue length gauge."""
        async with self._lock:
            self.gauges.queue_len = n

    def uptime_s(self) -> float:
        """
        Return uptime of the Metrics instance in seconds.
        :return: Float seconds since instantiation.
        """
        return time.monotonic() - self.start_time

metrics = Metrics()
