"""Leads: the typed artifacts recon produces and exploit consumes.

A lead is NOT a chat message - it is a structured, deduped, prioritized unit
of work that always traces back to the request that produced it. Workers
communicate through these, so nothing is re-interpreted between agents and
the evidence chain stays intact.
"""
from __future__ import annotations

import heapq
import itertools
import threading
import time
import urllib.parse
from dataclasses import dataclass, field

LEAD_KINDS = ("endpoint", "param", "credential", "note")


def _canon(url: str) -> str:
    p = urllib.parse.urlparse(url if "://" in url else "http://" + url)
    qs = tuple(sorted(urllib.parse.parse_qsl(p.query)))
    return urllib.parse.urlunparse((p.scheme.lower(), p.netloc.lower(),
                                    p.path or "/", "", "", "")) + "|" + "&".join(
        f"{k}={v}" for k, v in qs)


@dataclass(frozen=True)
class Lead:
    """One unit of attackable surface, passed recon -> exploit."""
    kind: str                     # endpoint | param | credential | note
    url: str
    params: tuple = ()            # sorted param names
    method: str = "GET"
    tech: str = ""                # observed stack hints, e.g. "express, json"
    note: str = ""                # why this looks interesting
    source: str = ""              # request_id or agent that produced it
    priority: int = 5             # 0 (highest) .. 9
    ts: float = field(default_factory=time.time)

    def key(self) -> tuple:
        return (self.kind, _canon(self.url), self.params, self.method.upper())

    def to_dict(self) -> dict:
        return {"kind": self.kind, "url": self.url, "params": list(self.params),
                "method": self.method, "tech": self.tech, "note": self.note,
                "source": self.source, "priority": self.priority}


class LeadQueue:
    """Thread-safe priority queue with dedup and close semantics.

    Producers push leads; consumers pull with a timeout so a worker can block
    while recon is still running, then exit cleanly once the queue is closed
    AND drained.
    """

    def __init__(self):
        self._heap: list[tuple] = []
        self._seen: set[tuple] = set()
        self._closed = False
        self._cond = threading.Condition()
        self._counter = itertools.count()

    def offer(self, lead: Lead) -> str:
        """Add a lead. Returns "" when queued, else WHICH refusal applied.

        Named `offer`, not `push`, because it reports a reason rather than a
        bool: a caller still written against the bool would read a non-empty
        reason as success, and a rename fails loudly instead.

        The three refusals need three different actions from the producer,
        which is the whole point of distinguishing them:

          "closed"    - the pipeline is shut; every further lead is wasted
                        work, so stop producing, do not go looking for
                        different surface.
          "duplicate" - this exact lead is already queued or worked; go find
                        different surface.
          "capacity"  - the unique-lead bound is spent. Nothing is wrong with
                        THIS lead, and the surface is not covered; the queue
                        simply stopped accepting.

        Collapsing them into one `False` told a recon worker "duplicate" when
        the pipeline had closed, so it burned its remaining turns producing
        leads nobody would ever pull - and left an operator reading
        "duplicate of an existing lead" in the transcript to conclude recon
        had been thorough.
        """
        with self._cond:
            if self._closed:
                return "closed"
            if lead.key() in self._seen:
                return "duplicate"
            # bound total unique leads - a runaway producer must not grow
            # the heap/seen-set without limit
            if len(self._seen) >= 10_000:
                return "capacity"
            self._seen.add(lead.key())
            heapq.heappush(self._heap,
                           (lead.priority, next(self._counter), lead))
            self._cond.notify()
            return ""

    def pull(self, max_n: int = 5, wait_s: float = 20.0) -> tuple[list[Lead], bool]:
        """Return up to max_n leads. Blocks up to wait_s for the first one.

        Second element of the result is True when the queue is closed and
        drained - the consumer should finish, not wait again.
        """
        deadline = time.monotonic() + max(0.0, wait_s)
        with self._cond:
            while True:
                if self._heap:
                    out = []
                    while self._heap and len(out) < max(1, max_n):
                        out.append(heapq.heappop(self._heap)[2])
                    return out, False
                if self._closed:
                    return [], True
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return [], False
                self._cond.wait(timeout=min(remaining, 1.0))

    def close(self) -> None:
        with self._cond:
            self._closed = True
            self._cond.notify_all()

    @property
    def closed(self) -> bool:
        return self._closed

    @property
    def pending(self) -> int:
        return len(self._heap)

    @property
    def drained(self) -> bool:
        return self._closed and not self._heap
