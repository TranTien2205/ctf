"""Turning an objective into tasks, with or without a model.

Two planners, and the deterministic one is not a fallback — it is the baseline
the model-made plan has to beat. Being able to run the same engagement both ways
is what makes "the planner is worth its cost" a measurement rather than a claim.

What a plan is: a list of tasks on disk, each one carrying its own goal, target,
class, acceptance criteria, risk tier and — optionally — a pinned runner and
model. The plan is an artifact, not a conversation, so an agent that joins at
task nine reads it instead of being told about it.

What a planner may not do: probe anything, or write a finding. It reads the
ledger and writes tasks. A planner that starts testing produces a diffuse plan
and spends the most expensive tokens in the engagement on the cheapest work.
"""
from __future__ import annotations

import json
from dataclasses import dataclass

from .. import config
from ..knowledge import playbook
from ..ledger import proof as matrix
from ..ledger.state import State
from ..runtime import profile as profile_mod, prompts
from ..runtime.providers.base import Message
from ..util import new_id, now_iso, read_json, write_json
from .bus import Bus

KINDS = ("recon", "triage", "classify", "probe", "exploit", "prove", "research", "review",
         "report", "tooling")
DEFAULT_SWEEP = ("sqli", "rce", "lfi", "idor", "auth-bypass", "ssrf", "xss", "secret-exposure")


def blank_task(**fields) -> dict:
    task = {
        "id": fields.get("id") or new_id("task"),
        "title": "", "goal": "", "kind": "probe", "target": "", "vuln_class": "",
        "hypothesis_id": "", "inputs": [], "done_when": [], "mode": "active",
        "runner": "", "model": "", "role": "", "max_steps": None,
        "after_all": False, "status": "pending", "result": None, "created": now_iso(),
    }
    task.update({k: v for k, v in fields.items() if k in task})
    return task


# --- the deterministic baseline ---------------------------------------------

def deterministic_plan(engagement: str, note: str = "") -> dict:
    """Recon every target, classify its surface, then expand per hypothesis.

    No model is consulted. This plan is correct rather than clever: it never
    skips a step, it never speculates, and it is the control condition for
    measuring whether a planner model earned its tokens.
    """
    state = State.load(engagement)
    targets = list(state.data["targets"]) or []
    tasks: list[dict] = []
    for target in targets:
        recon = blank_task(kind="recon", target=target, mode="active",
                           title=f"Map the surface of {target}",
                           goal=("Walk the recon ladder: ports, service fingerprint, content "
                                 "discovery, parameter discovery, template scan. Record every "
                                 "input as surface. Open no hypotheses."),
                           done_when=["every recon ladder step has a recorded probe",
                                      "every parameter and endpoint found is in the ledger"])
        classify = blank_task(kind="classify", target=target, inputs=[recon["id"]],
                              mode="passive",
                              title=f"Name a class and a falsifier for each input on {target}",
                              goal=("For each surface item worth testing, open ONE falsifiable "
                                    "hypothesis with a class from the proof matrix and the "
                                    "observation that would kill it. Park the rest by name. "
                                    "Probe nothing."),
                              done_when=["every surface item is either a hypothesis or parked",
                                         "each hypothesis names a class and a falsifier"])
        tasks += [recon, classify]
    review = blank_task(kind="review", after_all=True, mode="passive",
                        title="Adversarial review of every confirmed finding",
                        goal=("Re-read the evidence behind each confirmed finding and say, for "
                              "each, whether it carries the claim. Record agreement or "
                              "disagreement with ledger.cross_verify. Disagreement is a valid "
                              "and useful outcome."),
                        done_when=["every confirmed finding has a cross-verification record"])
    report = blank_task(kind="report", after_all=True, mode="passive",
                        inputs=[review["id"]],
                        title="Write the report",
                        goal=("Render the report, then state plainly what was proven, what is a "
                              "candidate and the exact check each candidate is missing, and what "
                              "was never tested."),
                        done_when=["report.md written", "coverage section names what was not tested"])
    plan = {
        "engagement": engagement,
        "objective": state.data["objective"],
        "created": now_iso(),
        "created_by": "deterministic",
        "note": note or "baseline plan: no model consulted",
        "tasks": tasks + [review, report],
    }
    _write(engagement, plan)
    return plan


# --- the model planner -------------------------------------------------------

PLANNER_INSTRUCTIONS = """\
You are the planner for an authorized penetration test. You are the most capable
model in this fleet and the most expensive, so you do exactly one thing: turn the
objective and the ledger below into a list of tasks other agents will execute.

You do not probe. You do not record findings. You read and you plan.

Return ONE JSON object and nothing else:

{"tasks": [
  {"id": "task-01",
   "title": "<one line>",
   "goal": "<what this agent must establish, specifically>",
   "kind": "recon|triage|classify|probe|exploit|prove|research|review|report|tooling",
   "target": "<url or host, in scope>",
   "vuln_class": "<a class from the proof matrix, or empty>",
   "inputs": ["<ids of tasks whose output this needs>"],
   "done_when": ["<acceptance criterion>", "..."],
   "mode": "passive|active|intrusive",
   "role": "planner|executor|breadth|long_context|reviewer|report",
   "max_steps": 20,
   "after_all": false},
  ...
]}

Rules the plan must obey:

- Breadth before depth: the surface is mapped before any class is probed, and a
  class is probed only where the surface says the input exists.
- One class per probe task, with the proof requirement in mind: a task whose
  class cannot be proven is a task that will be refused.
- A task is independent unless it genuinely needs another's answer. Independent
  tasks run at the same time, so a plan where everything depends on the previous
  task wastes the fleet.
- `mode` is the smallest tier that can do the job. Only code execution needs
  `intrusive`.
- Use `role` to say what the task needs, not which model you want: breadth for
  volume, executor for probing, long_context for reading large artifacts,
  reviewer for checking another model's evidence.
- Review and report tasks set `after_all: true`.
- Six to fourteen tasks. A plan longer than that is a plan that has started
  guessing."""


@dataclass
class PlanOutcome:
    plan: dict
    problems: list
    raw: str = ""
    model: str = ""
    cost_usd: float = 0.0

    @property
    def ok(self) -> bool:
        return bool(self.plan.get("tasks")) and not [p for p in self.problems
                                                     if p.startswith("fatal")]


def plan_with_model(engagement: str, provider, model: str, profile=None,
                    extra: str = "") -> PlanOutcome:
    state = State.load(engagement)
    profile = profile or profile_mod.load(model)
    bus = Bus(engagement)
    system = "\n\n".join([
        PLANNER_INSTRUCTIONS,
        "## The contract every executing agent works under\n\n" + prompts.CONTRACT,
        "## Proof requirements\n\n" + "\n".join(
            f"- {name}: {matrix.spec_for(name).requirement}" for name in matrix.classes()),
        "## Probe ladders available\n\n" + json.dumps(
            {klass: [step["step"] for step in playbook.ladder(klass)]
             for klass in playbook.known_classes()}, ensure_ascii=False),
        "## The engagement\n\n" + bus.digest_markdown(),
        "## Scope\n\n" + json.dumps(state.scope.to_dict(), ensure_ascii=False),
    ])
    if extra:
        system += "\n\n## Operator notes\n\n" + extra
    completion = provider.complete(system, [Message("user", "Produce the plan now.")], [], profile)
    if not completion.ok:
        return PlanOutcome({}, [f"fatal: planner provider failed: {completion.error}"], "", model)
    plan, problems = parse_and_validate(completion.text, engagement)
    plan.update({"engagement": engagement, "objective": state.data["objective"],
                 "created": now_iso(), "created_by": f"model:{model}",
                 "note": "planned by a model; validated against scope and the proof matrix"})
    cost = profile.cost(completion.input_tokens, completion.output_tokens)
    if plan.get("tasks"):
        _write(engagement, plan)
        bus.emit("plan.created", {"by": model, "tasks": len(plan["tasks"]),
                                  "problems": problems, "cost_usd": round(cost, 4)})
    return PlanOutcome(plan, problems, completion.text, model, cost)


def parse_and_validate(text: str, engagement: str) -> tuple[dict, list]:
    problems: list[str] = []
    data = _extract_json(text)
    if data is None:
        return {}, ["fatal: the planner did not return a JSON object"]
    raw_tasks = data.get("tasks") if isinstance(data, dict) else data
    if not isinstance(raw_tasks, list) or not raw_tasks:
        return {}, ["fatal: the plan has no tasks array"]
    state = State.load(engagement)
    scope = state.scope
    seen: set[str] = set()
    tasks: list[dict] = []
    for index, entry in enumerate(raw_tasks, start=1):
        if not isinstance(entry, dict):
            problems.append(f"task {index}: not an object, dropped")
            continue
        task = blank_task(**{k: v for k, v in entry.items()})
        if not task["id"] or task["id"] in seen:
            task["id"] = f"task-{index:02d}"
        seen.add(task["id"])
        if task["kind"] not in KINDS:
            problems.append(f"{task['id']}: unknown kind {task['kind']!r}, treated as probe")
            task["kind"] = "probe"
        if task["mode"] not in config.TIERS:
            problems.append(f"{task['id']}: unknown mode {task['mode']!r}, treated as active")
            task["mode"] = config.TIER_ACTIVE
        if task["mode"] not in state.tiers:
            problems.append(f"{task['id']}: mode {task['mode']} is not enabled for this "
                            f"engagement; the broker will refuse those calls")
        if task["vuln_class"]:
            spec = matrix.spec_for(task["vuln_class"])
            if spec is None:
                problems.append(f"{task['id']}: class {task['vuln_class']!r} is not in the proof "
                                f"matrix, cleared")
                task["vuln_class"] = ""
            elif spec.verifier is matrix.verify_refused:
                problems.append(f"{task['id']}: class {task['vuln_class']} is refused by this "
                                f"system, task dropped")
                continue
            else:
                task["vuln_class"] = spec.vuln_class
        if task["target"] and not scope.check(task["target"]):
            problems.append(f"{task['id']}: target {task['target']} is out of scope, task dropped")
            continue
        tasks.append(task)
    known = {task["id"] for task in tasks}
    for task in tasks:
        missing = [dep for dep in task["inputs"] if dep not in known]
        if missing:
            problems.append(f"{task['id']}: dropped unknown dependencies {missing}")
            task["inputs"] = [dep for dep in task["inputs"] if dep in known]
    if _has_cycle(tasks):
        problems.append("fatal: the plan's dependencies contain a cycle")
    if not tasks:
        problems.append("fatal: every task was dropped by validation")
    return {"tasks": tasks}, problems


def _extract_json(text: str):
    text = (text or "").strip()
    starts = [index for index, char in enumerate(text) if char == "{"]
    for start in starts:
        depth = 0
        for end in range(start, len(text)):
            if text[end] == "{":
                depth += 1
            elif text[end] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        parsed = json.loads(text[start:end + 1])
                    except json.JSONDecodeError:
                        break
                    if isinstance(parsed, dict) and ("tasks" in parsed):
                        return parsed
                    break
    return None


def _has_cycle(tasks: list[dict]) -> bool:
    graph = {task["id"]: list(task["inputs"]) for task in tasks}
    state: dict[str, int] = {}

    def walk(node: str) -> bool:
        if state.get(node) == 1:
            return True
        if state.get(node) == 2:
            return False
        state[node] = 1
        for dependency in graph.get(node, []):
            if walk(dependency):
                return True
        state[node] = 2
        return False

    return any(walk(node) for node in graph)


# --- dynamic expansion -------------------------------------------------------

def expand(engagement: str) -> list[dict]:
    """Add one probe task per open hypothesis that no task covers yet.

    This is what keeps the fleet busy. A plan written before recon ran cannot
    know which classes the surface will justify, so the scheduler calls this
    after every wave and the plan grows as the evidence does.
    """
    plan = load(engagement)
    if not plan:
        return []
    state = State.load(engagement)
    covered = {task.get("hypothesis_id") for task in plan["tasks"] if task.get("hypothesis_id")}
    added: list[dict] = []
    for hypothesis in state.open_hypotheses():
        if hypothesis["id"] in covered:
            continue
        spec = matrix.spec_for(hypothesis["vuln_class"])
        needs_intrusive = bool(spec and spec.kind == "command_output")
        proof_step = playbook.proof_step(hypothesis["vuln_class"]) or {}
        task = blank_task(
            kind="exploit" if needs_intrusive else "probe",
            target=hypothesis["target"], vuln_class=hypothesis["vuln_class"],
            hypothesis_id=hypothesis["id"],
            mode=proof_step.get("tier") or ("intrusive" if needs_intrusive else "active"),
            title=f"Prove or kill {hypothesis['vuln_class']} on {hypothesis['target']}",
            goal=(f"{hypothesis['statement']} Walk the ladder for this class, take the control, "
                  f"and either meet the proof requirement or record the observation that "
                  f"falsifies it. Falsifier on file: "
                  + (hypothesis.get("falsifier") or "none — write one before probing")),
            done_when=[f"either a finding recorded with grade proven, or {hypothesis['id']} "
                       f"falsified with an evidence id",
                       "no seventh probe on this class"],
        )
        plan["tasks"].insert(max(0, len(plan["tasks"]) - 2), task)
        added.append(task)
    if added:
        _write(engagement, plan)
        Bus(engagement).emit("plan.expanded", {"added": [task["id"] for task in added]})
    return added


# --- persistence -------------------------------------------------------------

def load(engagement: str) -> dict:
    return read_json(config.Paths(engagement).plan, {}) or {}


def _write(engagement: str, plan: dict) -> None:
    write_json(config.Paths(engagement).plan, plan)


def update_task(engagement: str, task_id: str, **fields) -> dict | None:
    plan = load(engagement)
    for task in plan.get("tasks") or []:
        if task["id"] == task_id:
            task.update(fields)
            _write(engagement, plan)
            return task
    return None


def render(plan: dict) -> str:
    lines = [f"plan for {plan.get('engagement')} by {plan.get('created_by')} "
             f"({len(plan.get('tasks') or [])} tasks)",
             f"{'id':14} {'kind':9} {'mode':10} {'class':14} {'status':9} deps"]
    for task in plan.get("tasks") or []:
        lines.append(f"{task['id']:14} {task['kind']:9} {task['mode']:10} "
                     f"{(task['vuln_class'] or '-'):14} {task['status']:9} "
                     f"{','.join(task['inputs']) or ('after-all' if task['after_all'] else '-')}")
        lines.append(f"{'':14} {task['title'][:100]}")
    return "\n".join(lines)
