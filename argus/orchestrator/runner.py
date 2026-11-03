"""Three ways to execute one task, and one brief that works for all of them.

    harness   our own loop (argus.runtime.loop) over the provider directly.
              Tightest control: every step is ours, the ledger gate is in-process.
    claude     Claude Code's own loop, with our MCP server as its only tools.
              Best for open-ended work and for spending a subscription instead of
              a key. Its builtin Bash/Write/WebFetch tools are refused, so the
              rule that every target-touching command goes through the broker
              still holds.
    opencode   the same arrangement with opencode, which reaches a different set
              of credentials.

The brief is the handoff, and it is the same text in all three cases: the
contract, what is already established, the task, the acceptance criteria, and
what to write at the end. An agent that needs more than that was given a task
that is not yet a task.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from .. import config
from ..broker import exec as ex
from ..ledger.state import State
from ..runtime.loop import Harness
from ..util import bound, now_iso, write_json
from .bus import Bus

TOOL_SETS = {
    # Which part of the tool surface a task kind is allowed to see. Narrowing the
    # surface measurably improves tool choice, and it is also the cheapest
    # safety control available: a tool that is not offered cannot be called.
    "recon": ("recon.", "http.", "fuzz.", "scan.", "ledger.", "knowledge."),
    "triage": ("recon.", "http.", "ledger.", "knowledge.", "proof.requirement", "session.list"),
    "classify": ("ledger.", "knowledge.", "http.probe", "proof.requirement", "session.list"),
    # sqlmap belongs in a probe set as well as an exploit one: confirming a SQL
    # injection is how you probe it, and the row cap is enforced by the tool.
    "probe": ("http.", "proof.", "exploit.", "web.", "session.", "ledger.", "knowledge.",
              "recon.fingerprint"),
    "exploit": ("http.", "exploit.", "proof.", "web.", "session.", "ledger.", "knowledge."),
    "prove": ("proof.", "http.", "exploit.", "web.", "session.", "ledger.", "knowledge."),
    "research": ("knowledge.", "ledger.status", "ledger.add_evidence", "ledger.add_surface"),
    "review": ("ledger.", "proof.verify", "proof.requirement", "knowledge."),
    "report": ("ledger.", "knowledge."),
    "tooling": ("knowledge.", "ledger.status", "ledger.add_evidence"),
}


@dataclass
class TaskResult:
    task_id: str
    runner: str
    model: str
    ok: bool = False
    summary: str = ""
    stop_reason: str = ""
    tool_calls: int = 0
    refusals: int = 0
    findings_added: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    report_path: str = ""
    errors: list = field(default_factory=list)
    started: str = field(default_factory=now_iso)
    finished: str = ""

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}


def tool_filter_for(kind: str):
    prefixes = TOOL_SETS.get(kind)
    if not prefixes:
        return None
    return lambda name: name.startswith(tuple(prefixes))


def brief_for(task: dict, bus: Bus, route, extra: str = "") -> str:
    from ..runtime.prompts import CONTRACT
    state = State.load(bus.engagement)
    lines = [f"# Task {task['id']}: {task.get('title') or task.get('goal', '')}", "",
             CONTRACT, "", bus.digest_markdown(task["id"]), "", "## Your task", "",
             f"**Goal.** {task.get('goal', '')}", ""]
    if task.get("target"):
        lines += [f"**Target.** {task['target']}", ""]
    if task.get("vuln_class"):
        lines += [f"**Class.** {task['vuln_class']} — call proof.requirement for it before you "
                  f"probe, and collect exactly what it asks for.", ""]
    if task.get("hypothesis_id"):
        lines += [f"**Hypothesis.** {task['hypothesis_id']} — every probe names it.", ""]
    done = task.get("done_when") or []
    if done:
        lines += ["**Done when.**"] + [f"- {item}" for item in done] + [""]
    lines += [f"**Risk tier for this task.** {task.get('mode') or 'active'}. "
              f"The engagement enables {', '.join(state.tiers)}; anything above that is refused "
              f"at the broker, and that refusal is correct.", ""]
    if task.get("inputs"):
        lines += ["**What produced your inputs.**"]
        for dependency in task["inputs"]:
            report = bus.read_report(dependency)
            lines.append(f"- {dependency}: {bound(report.strip().splitlines()[0] if report.strip() else 'no report', 200)}")
        lines.append("")
    lines += ["## What to write at the end", "",
              "Four short sections, in this order:", "",
              "1. **Established** — what you proved, naming the evidence ids.",
              "2. **Candidate** — what has a signal and the exact check it is missing.",
              "3. **Closed** — which hypotheses you falsified, and on what observation.",
              "4. **Next** — the single cheapest thing the next agent should do, and why.", "",
              "Do not restate the contract. Do not claim anything the ledger would refuse."]
    if extra:
        lines += ["", extra]
    return "\n".join(lines)


class Runner:
    def __init__(self, engagement: str, bus: Bus | None = None, dry_run: bool = False,
                 timeout: int = 1800):
        self.engagement = engagement
        self.bus = bus or Bus(engagement)
        self.dry_run = dry_run
        self.timeout = timeout

    # --- entry point ---------------------------------------------------------

    def execute(self, task: dict, route) -> TaskResult:
        result = TaskResult(task["id"], route.runner, route.model)
        brief = brief_for(task, self.bus, route)
        self.bus.write_brief(task["id"], brief)
        self.bus.emit("task.started", {"task": task["id"], "runner": route.runner,
                                       "model": route.model, "reason": route.reason})
        if self.dry_run:
            result.ok = True
            result.summary = f"dry run: would execute on {route.runner}/{route.model}"
            result.stop_reason = "dry-run"
            result.report_path = self.bus.write_report(task["id"],
                                                       f"# {task['id']} (dry run)\n\n{result.summary}\n")
            result.finished = now_iso()
            self.bus.emit("task.finished", result.to_dict())
            return result
        if route.runner == "none" or not route.model:
            result.errors.append(route.reason)
            result.summary = "no model available for this task"
            result.finished = now_iso()
            self.bus.emit("task.unroutable", {"task": task["id"], "reason": route.reason})
            return result

        before = len(State.load(self.engagement).data["findings"])
        try:
            if route.runner == "harness":
                self._harness(task, route, brief, result)
            elif route.runner == "claude":
                self._cli_claude(task, route, brief, result)
            elif route.runner == "opencode":
                self._cli_opencode(task, route, brief, result)
            else:
                result.errors.append(f"unknown runner {route.runner!r}")
        except Exception as error:                                     # noqa: BLE001
            result.errors.append(f"{type(error).__name__}: {error}")
            result.stop_reason = "runner-exception"
        after = len(State.load(self.engagement).data["findings"])
        result.findings_added = after - before
        result.ok = result.ok and not result.errors
        result.finished = now_iso()
        self.bus.emit("task.finished", result.to_dict())
        return result

    # --- our own loop --------------------------------------------------------

    def _harness(self, task: dict, route, brief: str, result: TaskResult) -> None:
        provider = route.profile.provider if route.profile else None
        kwargs: dict = {}
        if provider == "opencode":
            prefix = (route.profile.opencode_name or "").split("/")[0]
            kwargs = {"model_prefix": prefix, "timeout": min(self.timeout, 900)}
        elif route.profile and route.profile.family == "claude" and provider == "anthropic":
            from ..runtime import credentials
            if not credentials.get("anthropic"):
                provider = "claude_cli"                 # the subscription, not a key
                kwargs = {"timeout": min(self.timeout, 900)}
        harness = Harness(self.engagement, route.model, provider=provider,
                          profile=route.profile, actor=f"{route.runner}:{route.model}",
                          provider_kwargs=kwargs, tool_filter=tool_filter_for(task.get("kind", "")))
        run = harness.run(task=brief, max_steps=task.get("max_steps"))
        result.ok = run.stop_reason not in ("provider-error",)
        result.stop_reason = run.stop_reason
        result.tool_calls = run.tool_calls
        result.refusals = run.refusals
        result.input_tokens = run.input_tokens
        result.output_tokens = run.output_tokens
        result.cost_usd = run.cost_usd
        result.errors.extend(run.errors[:4] if run.stop_reason == "provider-error" else [])
        result.summary = bound(run.final_text or run.render(), 1200)
        result.report_path = self.bus.write_report(
            task["id"], f"# {task['id']} — {route.model} via our harness\n\n"
                        f"{run.render()}\n\n## Final statement\n\n{run.final_text or '(none)'}\n")

    # --- delegation ----------------------------------------------------------

    def mcp_config_claude(self) -> str:
        path = config.Paths(self.engagement).dir / "mcp-claude.json"
        write_json(path, {"mcpServers": {"argus": {
            "command": "python3",
            "args": ["-m", "argus.broker.serve", "all", "--engagement", self.engagement],
            "env": {"PYTHONPATH": str(config.ROOT), "ARGUS_ENGAGEMENT": self.engagement},
        }}})
        return str(path)

    def mcp_config_opencode(self) -> str:
        path = config.Paths(self.engagement).dir / "opencode.json"
        write_json(path, {
            "$schema": "https://opencode.ai/config.json",
            "mcp": {"argus": {
                "type": "local",
                "command": ["python3", "-m", "argus.broker.serve", "all",
                            "--engagement", self.engagement],
                "environment": {"PYTHONPATH": str(config.ROOT),
                                "ARGUS_ENGAGEMENT": self.engagement},
                "enabled": True}},
        })
        return str(path)

    def _cli_claude(self, task: dict, route, brief: str, result: TaskResult) -> None:
        mcp_config = self.mcp_config_claude()
        argv = ["claude", "-p", "--output-format", "json", "--model", route.model,
                "--mcp-config", mcp_config,
                "--allowed-tools", "mcp__argus",
                "--disallowed-tools", "Bash,Write,Edit,NotebookEdit,WebFetch,WebSearch",
                "--append-system-prompt",
                "Every command that touches a target goes through the argus MCP tools. You have no "
                "shell here, and that is deliberate: the broker records each call in the ledger and "
                "refuses anything out of scope, above the risk tier, or unproven. Start with "
                "mcp__argus__ledger_next_action."]
        result_run = ex.run(argv, timeout=self.timeout, stdin=brief, cwd=str(config.ROOT),
                            log_path=config.Paths(self.engagement).commands)
        text, usage = _claude_json(result_run.stdout)
        result.ok = result_run.exit_code == 0 and bool(text)
        result.stop_reason = "cli-exit-0" if result_run.exit_code == 0 else f"cli-exit-{result_run.exit_code}"
        result.input_tokens = usage.get("input_tokens", 0)
        result.output_tokens = usage.get("output_tokens", 0)
        result.cost_usd = usage.get("total_cost_usd", 0.0) or (
            route.profile.cost(result.input_tokens, result.output_tokens) if route.profile else 0.0)
        result.summary = bound(text or result_run.stderr, 1200)
        if not result.ok:
            result.errors.append(bound(result_run.stderr or result_run.stdout, 600))
        result.report_path = self.bus.write_report(
            task["id"], f"# {task['id']} — {route.model} via claude code\n\n{text or '(no output)'}\n")

    def _cli_opencode(self, task: dict, route, brief: str, result: TaskResult) -> None:
        mcp_config = self.mcp_config_opencode()
        model = route.profile.opencode_name if route.profile and route.profile.opencode_name \
            else route.model
        argv = ["opencode", "run", "--format", "json", "--pure", "--auto", "-m", model, brief]
        result_run = ex.run(argv, timeout=self.timeout, cwd=str(config.ROOT),
                            env_extra={"OPENCODE_CONFIG": mcp_config,
                                       "PYTHONPATH": str(config.ROOT),
                                       "ARGUS_ENGAGEMENT": self.engagement},
                            log_path=config.Paths(self.engagement).commands)
        from ..runtime.providers.opencode_cli import _collect
        text, error = _collect(result_run.stdout)
        result.ok = not error and bool(text.strip())
        result.stop_reason = "cli-exit-0" if result_run.exit_code == 0 else f"cli-exit-{result_run.exit_code}"
        if error:
            result.errors.append(bound(error, 600))
        result.summary = bound(text or error or result_run.stderr, 1200)
        result.input_tokens = len(brief) // 4
        result.output_tokens = len(text) // 4
        result.cost_usd = route.profile.cost(result.input_tokens, result.output_tokens) \
            if route.profile else 0.0
        result.report_path = self.bus.write_report(
            task["id"], f"# {task['id']} — {model} via opencode\n\n{text or error or '(no output)'}\n")


def _claude_json(stdout: str) -> tuple[str, dict]:
    stdout = (stdout or "").strip()
    if not stdout:
        return "", {}
    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        for line in reversed(stdout.splitlines()):
            try:
                data = json.loads(line)
                break
            except json.JSONDecodeError:
                continue
        else:
            return stdout, {}
    if isinstance(data, dict):
        usage = dict(data.get("usage") or {})
        if data.get("total_cost_usd") is not None:
            usage["total_cost_usd"] = data["total_cost_usd"]
        return str(data.get("result") or data.get("text") or ""), usage
    return stdout, {}
