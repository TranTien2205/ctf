"""Run the plan: dependencies, parallelism, and never spawning then waiting.

The scheduling rule that matters is not the wave structure — it is that a free
slot is filled the moment one opens. A fleet that launches five agents, waits for
all five, reads all five reports and then thinks about the next five has
converted parallel time back into serial time twice per round.

So: a ready queue, a fixed number of slots, and a completion handler that
expands the plan from whatever the finished task put in the ledger and
immediately starts the next thing. `after_all` tasks — review, report — are held
back until nothing else can be produced.
"""
from __future__ import annotations

import json
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from dataclasses import dataclass, field

from ..ledger.state import State
from ..util import now_iso
from . import planner as planner_mod
from .bus import Bus
from .router import Router
from .runner import Runner


@dataclass
class Summary:
    engagement: str
    policy: str
    parallelism: int
    tasks_run: int = 0
    tasks_failed: int = 0
    tasks_unroutable: int = 0
    tool_calls: int = 0
    refusals: int = 0
    findings_before: int = 0
    findings_after: int = 0
    cost_usd: float = 0.0
    input_tokens: int = 0
    output_tokens: int = 0
    by_model: dict = field(default_factory=dict)
    started: str = field(default_factory=now_iso)
    finished: str = ""
    stopped_because: str = ""

    def to_dict(self) -> dict:
        data = {k: v for k, v in self.__dict__.items()}
        data["findings_added"] = self.findings_after - self.findings_before
        return data

    def render(self) -> str:
        lines = [f"engagement {self.engagement} — policy {self.policy}, {self.parallelism} slot(s)",
                 f"{self.tasks_run} task(s) run, {self.tasks_failed} failed, "
                 f"{self.tasks_unroutable} unroutable",
                 f"{self.tool_calls} tool call(s), {self.refusals} refusal(s), "
                 f"{self.findings_after - self.findings_before:+d} finding(s)",
                 f"${self.cost_usd:.4f} across {self.input_tokens + self.output_tokens} tokens",
                 f"stopped: {self.stopped_because}"]
        if self.by_model:
            lines.append("per model:")
            for model, stats in sorted(self.by_model.items()):
                lines.append(f"  {model:26} {stats['tasks']} task(s)  "
                             f"{stats['tool_calls']:3} call(s)  ${stats['cost_usd']:.4f}  "
                             f"{stats['findings']:+d} finding(s)")
        return "\n".join(lines)


class Scheduler:
    def __init__(self, engagement: str, policy: str = "balanced", parallelism: int = 3,
                 dry_run: bool = False, max_tasks: int = 40, task_timeout: int = 1800,
                 router: Router | None = None):
        self.engagement = engagement
        self.bus = Bus(engagement)
        self.policy = policy
        self.parallelism = max(1, min(int(parallelism), 8))
        self.dry_run = dry_run
        self.max_tasks = max_tasks
        self.router = router or Router(policy=policy)
        self.runner = Runner(engagement, self.bus, dry_run=dry_run, timeout=task_timeout)

    # --- readiness -----------------------------------------------------------

    @staticmethod
    def _ready(plan: dict, running: set[str]) -> list[dict]:
        done = {task["id"] for task in plan["tasks"] if task["status"] in ("done", "failed")}
        out = []
        for task in plan["tasks"]:
            if task["status"] != "pending" or task["id"] in running or task.get("after_all"):
                continue
            if all(dependency in done for dependency in task.get("inputs") or []):
                out.append(task)
        return out

    @staticmethod
    def _after_all(plan: dict, running: set[str]) -> list[dict]:
        done = {task["id"] for task in plan["tasks"] if task["status"] in ("done", "failed")}
        pending_regular = [task for task in plan["tasks"]
                           if task["status"] == "pending" and not task.get("after_all")]
        if pending_regular or running:
            return []
        out = []
        for task in plan["tasks"]:
            if task["status"] != "pending" or not task.get("after_all"):
                continue
            if all(dependency in done for dependency in task.get("inputs") or []):
                out.append(task)
        return out

    # --- the loop ------------------------------------------------------------

    def run(self, expand: bool = True) -> Summary:
        state = State.load(self.engagement)
        plan = planner_mod.load(self.engagement) or planner_mod.deterministic_plan(self.engagement)
        summary = Summary(self.engagement, self.policy, self.parallelism,
                          findings_before=len(state.data["findings"]))
        self.bus.emit("schedule.started", {"policy": self.policy,
                                           "parallelism": self.parallelism,
                                           "tasks": len(plan["tasks"]),
                                           "dry_run": self.dry_run})
        running: dict = {}
        with ThreadPoolExecutor(max_workers=self.parallelism) as pool:
            while True:
                plan = planner_mod.load(self.engagement)
                ready = self._ready(plan, set(running.values()))
                while ready and len(running) < self.parallelism and summary.tasks_run < self.max_tasks:
                    task = ready.pop(0)
                    planner_mod.update_task(self.engagement, task["id"], status="running")
                    route = self._route_for(task)
                    future = pool.submit(self.runner.execute, task, route)
                    running[future] = task["id"]
                    summary.tasks_run += 1
                if not running:
                    if expand and summary.tasks_run < self.max_tasks and planner_mod.expand(self.engagement):
                        continue
                    final = self._after_all(planner_mod.load(self.engagement), set())
                    if final and summary.tasks_run < self.max_tasks:
                        for task in final:
                            planner_mod.update_task(self.engagement, task["id"], status="running")
                            route = self._route_for(task)
                            future = pool.submit(self.runner.execute, task, route)
                            running[future] = task["id"]
                            summary.tasks_run += 1
                        continue
                    summary.stopped_because = ("task cap reached"
                                               if summary.tasks_run >= self.max_tasks
                                               else "nothing left that is ready")
                    break
                # Fill the slot the instant one frees, rather than draining the wave.
                finished, _pending = wait(list(running), return_when=FIRST_COMPLETED)
                for future in finished:
                    task_id = running.pop(future)
                    try:
                        result = future.result()
                    except Exception as error:                          # noqa: BLE001
                        planner_mod.update_task(self.engagement, task_id, status="failed",
                                                result={"summary": f"{type(error).__name__}: {error}"})
                        summary.tasks_failed += 1
                        self.bus.emit("task.crashed", {"task": task_id, "error": str(error)})
                        continue
                    self._absorb(summary, task_id, result)
                if expand:
                    planner_mod.expand(self.engagement)

        final_state = State.load(self.engagement)
        summary.findings_after = len(final_state.data["findings"])
        summary.finished = now_iso()
        self.bus.emit("schedule.finished", summary.to_dict())
        return summary

    # --- helpers -------------------------------------------------------------

    def _route_for(self, task: dict):
        exclude: tuple[str, ...] = ()
        if task.get("kind") == "review":
            exclude = tuple(sorted(self._families_that_produced_findings()))
        route = self.router.route(task, exclude_families=exclude)
        planner_mod.update_task(self.engagement, task["id"], route=route.to_dict())
        self.bus.emit("task.routed", route.to_dict())
        return route

    def _families_that_produced_findings(self) -> set[str]:
        """A review must not come from the family that wrote the finding."""
        from ..runtime import profile as profile_mod
        state = State.load(self.engagement)
        families = set()
        for finding in state.data["findings"]:
            author = str(finding.get("recorded_by") or "")
            model = author.split(":")[-1]
            if model:
                families.add(profile_mod.load(model).family)
        return {family for family in families if family and family != "unknown"}

    def _absorb(self, summary: Summary, task_id: str, result) -> None:
        planner_mod.update_task(self.engagement, task_id,
                                status="done" if result.ok else "failed",
                                result=result.to_dict())
        if not result.ok:
            summary.tasks_failed += 1
        if result.runner == "none":
            summary.tasks_unroutable += 1
        summary.tool_calls += result.tool_calls
        summary.refusals += result.refusals
        summary.cost_usd += result.cost_usd
        summary.input_tokens += result.input_tokens
        summary.output_tokens += result.output_tokens
        stats = summary.by_model.setdefault(result.model or "(unrouted)",
                                            {"tasks": 0, "tool_calls": 0, "cost_usd": 0.0,
                                             "findings": 0})
        stats["tasks"] += 1
        stats["tool_calls"] += result.tool_calls
        stats["cost_usd"] += result.cost_usd
        stats["findings"] += result.findings_added


def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(prog="argus-schedule", description=__doc__.splitlines()[0])
    parser.add_argument("engagement")
    parser.add_argument("--policy", default="balanced", choices=("quality", "balanced", "cheap"))
    parser.add_argument("--parallelism", type=int, default=3)
    parser.add_argument("--max-tasks", type=int, default=40)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--no-expand", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    scheduler = Scheduler(args.engagement, policy=args.policy, parallelism=args.parallelism,
                          dry_run=args.dry_run, max_tasks=args.max_tasks)
    summary = scheduler.run(expand=not args.no_expand)
    print(json.dumps(summary.to_dict(), ensure_ascii=False, indent=2) if args.json
          else summary.render())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
