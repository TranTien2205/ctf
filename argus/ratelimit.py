"""Token-bucket rate limiter shared by all request-emitting tools."""
from __future__ import annotations

import threading
import time


class RateLimiter:
    def __init__(self, rps: float):
        self.interval = 1.0 / rps if rps > 0 else 0.0
        self._lock = threading.Lock()
        self._next = 0.0

    def wait(self) -> None:
        if self.interval <= 0:
            return
        with self._lock:
            now = time.monotonic()
            if now < self._next:
                time.sleep(self._next - now)
                now = time.monotonic()
            self._next = now + self.interval
