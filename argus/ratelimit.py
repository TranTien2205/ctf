"""Token-bucket rate limiter shared by all request-emitting tools."""
from __future__ import annotations

import threading
import time


class RateLimiter:
    def __init__(self, rps: float):
        import math
        # nan/inf slip past 'rps > 0' (nan comparisons are False; 1/inf
        # is 0) into an effectively unlimited limiter - treat any
        # non-finite input as "no cap" only when it is exactly 0, else
        # fail loud
        if not math.isfinite(rps):
            raise ValueError(f"rps must be finite, got {rps!r}")
        if rps < 0:
            # a negative rate meaning 'unlimited' is never stated anywhere
            # - only exact 0 is the documented opt-out
            raise ValueError(f"rps must be >= 0, got {rps!r}")
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
