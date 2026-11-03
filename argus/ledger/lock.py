"""One writer at a time per engagement.

The ledger writes atomically, so a reader never sees half a file. That is not
enough once several agents work the same engagement: load, mutate, save is a
read-modify-write, and two of them interleaved lose whichever finished first.
The failure is quiet and it costs exactly the thing this system exists to
protect — a recorded observation.

So every mutation holds an advisory lock on `<engagement>/.lock`. It is held for
the microseconds of a JSON rewrite, never across a tool call, so three agents
probing in parallel do not serialise on it.
"""
from __future__ import annotations

import contextlib
import errno
import fcntl
import os
import time
from pathlib import Path

TIMEOUT_SECONDS = 30


@contextlib.contextmanager
def engagement_lock(directory: str | os.PathLike[str], timeout: float = TIMEOUT_SECONDS):
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    lock_path = path / ".lock"
    handle = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
    deadline = time.monotonic() + timeout
    try:
        while True:
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError as error:
                if error.errno not in (errno.EACCES, errno.EAGAIN):
                    raise
                if time.monotonic() >= deadline:
                    raise TimeoutError(
                        f"another agent has held the ledger lock on {path.name} for "
                        f"{timeout:.0f}s; it is held only across a JSON rewrite, so this means a "
                        f"crashed writer rather than contention") from error
                time.sleep(0.02)
        yield
    finally:
        try:
            fcntl.flock(handle, fcntl.LOCK_UN)
        finally:
            os.close(handle)
