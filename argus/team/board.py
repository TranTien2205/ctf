"""The blackboard: shared, typed state every team member reads and writes.

This is the good kind of "shared context" - workers exchange ARTIFACTS
(leads, board notes, findings, agent status), never each other's raw
conversation. Anything the lead needs to decide (spawn requests, stalled
queues, new findings) is visible here as data.
"""
from __future__ import annotations

import threading
import time

from .leads import Lead, LeadQueue


class Board:
    def __init__(self, session):
        self.session = session                 # shared Session (evidence store)
        self.leads = LeadQueue()
        self.stop = threading.Event()          # hard stop: budgets/time
        self.engagement_done = threading.Event()  # lead called finish_engagement
        self._lock = threading.Lock()
        self._notes: list[dict] = []
        self._requests: list[dict] = []        # worker -> lead spawn requests
        self._agents: dict[str, dict] = {}
        self._spawn_cb = None                  # set by coordinator

    # ------------------------------------------------------------- agents
    def register(self, name: str, role: str, task: str) -> None:
        with self._lock:
            # bound the roster: sequential spawns would grow it forever -
            # drop finished entries past a generous history
            if len(self._agents) >= 200:
                self._agents = {n: a for n, a in self._agents.items()
                                if a.get("status") == "running"}
            self._agents[name] = {"role": role, "task": task,
                                  "status": "running",
                                  "started": round(time.time(), 1),
                                  "turns": 0, "requests": 0, "findings": 0}

    def update_agent(self, name: str, **kw) -> None:
        with self._lock:
            self._agents.get(name, {}).update(kw)

    def agents(self) -> dict:
        with self._lock:
            return {n: dict(a) for n, a in self._agents.items()}

    # ------------------------------------------------------------- notes
    def post_note(self, agent: str, text: str) -> None:
        with self._lock:
            self._notes.append({"agent": agent, "ts": round(time.time(), 1),
                                "text": text[:2000]})
            del self._notes[:-500]             # bound memory, keep a tail

    def notes(self) -> list[dict]:
        with self._lock:
            return list(self._notes)

    # -------------------------------------------------- spawn requests
    def request_worker(self, agent: str, role: str, task: str,
                       reason: str) -> None:
        """Worker asks the lead for help; lead decides on read_board."""
        with self._lock:
            self._requests.append({"agent": agent, "role": role,
                                   "task": task[:2000],
                                   "reason": reason[:1000],
                                   "ts": round(time.time(), 1)})
            del self._requests[:-200]          # a lead 200 behind is dead

    def take_requests(self) -> list[dict]:
        with self._lock:
            out, self._requests = self._requests, []
            return out

    def pending_requests(self) -> list[dict]:
        with self._lock:
            return list(self._requests)

    # ------------------------------------------------------------- spawn
    def set_spawner(self, cb) -> None:
        self._spawn_cb = cb

    def spawn(self, role: str, task: str) -> dict:
        if not self._spawn_cb:
            return {"error": "no spawner attached"}
        return self._spawn_cb(role, task)

    # ------------------------------------------------------------- views
    def snapshot(self, consume_requests: bool = False) -> dict:
        # Only the lead drains spawn requests; workers see them as pending
        # so a read_board by a worker cannot swallow a request meant for
        # the lead.
        requests = self.take_requests() if consume_requests \
            else self.pending_requests()
        return {
            "leads_pending": self.leads.pending,
            "leads_closed": self.leads.closed,
            "agents": self.agents(),
            "requests": requests,
            "notes": self.notes()[-15:],
            "findings": [{"id": f["id"], "severity": f["severity"],
                          "title": f["title"]} for f in self.session.findings],
            "stop": self.stop.is_set(),
        }
