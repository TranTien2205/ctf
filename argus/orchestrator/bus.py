"""The shared context plane.

Context drift between agents is not solved by a bigger window; it is solved by
not keeping the context in a window. Three files do the work:

* `log/bus.jsonl` — every orchestration event, append-only, one line each.
* `decisions.json` — the small set of things later agents must not re-litigate:
  which parameter is the entry point, which class was ruled out and why, what
  the credentials are for, which host is out of bounds. Each has an author, a
  rationale and a history, so a later agent can disagree *with the reason* in
  front of it rather than by accident.
* `tasks/<id>/brief.md` and `report.md` — the handoff. A task that cannot be
  described in a brief is not a task yet.

`digest()` is what a new agent reads first: the ledger's state, the decisions,
the sibling tasks' one-line outcomes, and the last few events. It is deliberately
short — an agent that has to be told everything was given the wrong task.
"""
from __future__ import annotations

from dataclasses import dataclass

from .. import config
from ..ledger.state import State
from ..util import append_jsonl, bound, now_iso, read_json, read_jsonl, write_json


@dataclass
class Bus:
    engagement: str

    @property
    def paths(self) -> config.Paths:
        return config.Paths(self.engagement).ensure()

    @property
    def events_path(self):
        return self.paths.dir / "log" / "bus.jsonl"

    # --- events --------------------------------------------------------------

    def emit(self, kind: str, payload: dict | None = None, actor: str = "orchestrator") -> None:
        append_jsonl(self.events_path, {"ts": now_iso(), "kind": kind, "actor": actor,
                                        "payload": payload or {}})

    def events(self, limit: int = 40) -> list[dict]:
        return read_jsonl(self.events_path, limit=limit)

    # --- decisions -----------------------------------------------------------

    def decide(self, key: str, value, actor: str, rationale: str = "") -> dict:
        """Record a decision later agents must read before contradicting it."""
        store = read_json(self.paths.decisions, {}) or {}
        entry = store.get(key) or {"key": key, "history": []}
        if "value" in entry:
            entry["history"].append({"value": entry["value"], "actor": entry.get("actor"),
                                     "rationale": entry.get("rationale"), "ts": entry.get("ts")})
        entry.update({"value": value, "actor": actor, "rationale": rationale, "ts": now_iso()})
        store[key] = entry
        write_json(self.paths.decisions, store)
        self.emit("decision", {"key": key, "value": value, "rationale": rationale}, actor)
        return entry

    def decision(self, key: str):
        store = read_json(self.paths.decisions, {}) or {}
        return (store.get(key) or {}).get("value")

    def decisions(self) -> dict:
        store = read_json(self.paths.decisions, {}) or {}
        return {key: {"value": entry.get("value"), "by": entry.get("actor"),
                      "why": entry.get("rationale"), "ts": entry.get("ts"),
                      "revisions": len(entry.get("history") or [])}
                for key, entry in store.items()}

    # --- task handoff --------------------------------------------------------

    def task_dir(self, task_id: str):
        directory = self.paths.tasks / task_id
        directory.mkdir(parents=True, exist_ok=True)
        return directory

    def write_brief(self, task_id: str, text: str) -> str:
        path = self.task_dir(task_id) / "brief.md"
        path.write_text(text, encoding="utf-8")
        return str(path)

    def write_report(self, task_id: str, text: str) -> str:
        path = self.task_dir(task_id) / "report.md"
        path.write_text(text, encoding="utf-8")
        self.emit("task.report", {"task": task_id, "bytes": len(text)})
        return str(path)

    def read_report(self, task_id: str) -> str:
        path = self.paths.tasks / task_id / "report.md"
        try:
            return path.read_text(encoding="utf-8")
        except OSError:
            return ""

    # --- the digest every agent starts from ----------------------------------

    def digest(self, task_id: str | None = None, event_limit: int = 12) -> dict:
        state = State.load(self.engagement)
        plan = read_json(self.paths.plan, {}) or {}
        siblings = []
        for task in plan.get("tasks") or []:
            if task_id and task["id"] == task_id:
                continue
            if task.get("status") in ("done", "failed"):
                siblings.append({"id": task["id"], "title": bound(task.get("title", ""), 90),
                                 "status": task["status"],
                                 "outcome": bound(str((task.get("result") or {}).get("summary")
                                                      or ""), 200)})
        return {
            "engagement": state.digest(),
            "decisions": self.decisions(),
            "completed_tasks": siblings[-10:],
            "recent_events": [{"kind": event["kind"], "actor": event.get("actor"),
                               "payload": bound(str(event.get("payload")), 180)}
                              for event in self.events(event_limit)],
        }

    def digest_markdown(self, task_id: str | None = None) -> str:
        """The same thing as prose, for a CLI agent that gets one prompt."""
        data = self.digest(task_id)
        engagement = data["engagement"]
        lines = ["## What is already established", "",
                 f"Objective: {engagement.get('objective')}",
                 f"Targets: {', '.join(engagement.get('targets') or []) or 'none'}",
                 f"Risk tiers enabled: {', '.join(engagement.get('tiers') or [])}",
                 f"Surface: {engagement.get('surface_counts')}",
                 f"Probes so far: {engagement.get('probes', {}).get('total')} "
                 f"({engagement.get('probes', {}).get('by_class')})", ""]
        findings = engagement.get("findings") or []
        if findings:
            lines.append("Findings on record:")
            for finding in findings:
                lines.append(f"- {finding['id']} {finding.get('class')} "
                             f"[{finding.get('grade')}] {finding.get('title')}")
            lines.append("")
        open_hypotheses = (engagement.get("hypotheses") or {}).get("open") or []
        if open_hypotheses:
            lines.append("Open hypotheses:")
            for hypothesis in open_hypotheses:
                lines.append(f"- {hypothesis['id']} {hypothesis['class']} on "
                             f"{hypothesis['target']}: {hypothesis['statement']}")
            lines.append("")
        if data["decisions"]:
            lines.append("Decisions you must not silently contradict:")
            for key, entry in data["decisions"].items():
                lines.append(f"- **{key}** = {entry['value']}  (by {entry['by']}: {entry['why']})")
            lines.append("")
        if data["completed_tasks"]:
            lines.append("What other agents already finished:")
            for task in data["completed_tasks"]:
                lines.append(f"- [{task['status']}] {task['title']} — {task['outcome']}")
            lines.append("")
        return "\n".join(lines)
