"""A small MCP server, and the registry every tool in this system is declared in.

Why hand-rolled rather than the official SDK: the registry here has to do two
jobs at once. The same decorated function must be callable

* over stdio by any MCP client (Claude Code, opencode, an IDE), and
* in-process by our own harness, with no subprocess and no serialisation,

and every call, by either route, must pass the ledger gate. A thin protocol
layer over one registry gives that for about two hundred lines and no
dependency. The wire format is JSON-RPC 2.0, one object per line, which is what
the stdio transport specifies.

The gate is in `Server.call`, not in the tools. A tool author writes the tool;
scope, tier, budget, evidence and redaction are applied around it.
"""
from __future__ import annotations

import inspect
import json
import os
import sys
import traceback
from dataclasses import dataclass, field
from typing import Any, Callable

from .. import config
from ..ledger import hooks
from ..ledger.proof import nonce as make_nonce
from ..ledger.state import RECON, State
from ..util import bound, now_iso

PROTOCOL_VERSION = "2025-06-18"

# Errors that mean "this tool declined", as opposed to "this tool ran and
# failed". A decline is recorded in the refusal log and charges no probe; a
# failure is an observation and charges one.
TOOL_REFUSALS = frozenset({
    "bad-arguments", "unknown-tool", "no-engagement", "no-hypothesis", "out-of-scope",
    "tier-not-enabled", "class-mismatch", "budget-spent", "refused-class", "unknown-class",
    "unknown-skill", "unknown-script", "no-evidence", "missing-tool",
})
SUPPORTED_PROTOCOLS = (PROTOCOL_VERSION, "2025-03-26", "2024-11-05")


# --- context handed to every tool -------------------------------------------

@dataclass
class ToolContext:
    engagement: str | None
    tool: str
    tier: str
    actor: str = "broker"
    _state: State | None = field(default=None, repr=False)

    @property
    def state(self) -> State:
        if self._state is None:
            if not self.engagement:
                raise ValueError("this tool needs an engagement: pass engagement=<name> or set "
                                 "ARGUS_ENGAGEMENT")
            self._state = State.load(self.engagement)
        return self._state

    @property
    def paths(self):
        return self.state.paths

    @property
    def command_log(self):
        return self.state.paths.commands if self.engagement else None

    def nonce(self) -> str:
        return make_nonce()

    def emit_surface(self, target: str, kind: str, value: str, detail: dict | None = None) -> None:
        from ..ledger.lock import engagement_lock
        with engagement_lock(self.paths.dir):
            state = State.load(self.engagement)          # re-read under the lock
            state.add_surface(target, kind, value, source=self.tool, detail=detail)
            state.save()
            self._state = state

    def note_stack(self, target: str, stack: dict) -> None:
        from ..ledger.lock import engagement_lock
        with engagement_lock(self.paths.dir):
            state = State.load(self.engagement)
            entry = state.add_target(target)
            entry.setdefault("stack", {}).update(stack)
            state.save()
            self._state = state


# --- tool declaration --------------------------------------------------------

@dataclass
class ToolSpec:
    name: str
    description: str
    schema: dict
    handler: Callable[..., dict]
    tier: str = config.TIER_ACTIVE
    vuln_class: str | None = None          # "recon", or None = taken from arguments
    step: str = ""
    touches_target: bool = True
    requires: tuple[str, ...] = ()
    proves: str | None = None
    # Which of the gate's own argument names the handler also wants to receive.
    # `proof.requirement(vuln_class=...)` is a tool *about* a class, not a probe
    # against one, so the gate must read that argument without consuming it.
    handler_params: frozenset = frozenset()

    def to_mcp(self) -> dict:
        extra = []
        if self.touches_target:
            extra.append(f"Risk tier: {self.tier}.")
        if self.requires:
            extra.append("Needs: " + ", ".join(self.requires) + ".")
        if self.proves:
            extra.append(f"Can satisfy the {self.proves} proof requirement.")
        if self.touches_target and self.vuln_class is None:
            extra.append("Needs an open hypothesis: pass hypothesis_id and vuln_class.")
        return {
            "name": self.name,
            "description": (self.description.strip() + ("\n" + " ".join(extra) if extra else "")),
            "inputSchema": self.schema,
        }


class ToolError(RuntimeError):
    """A tool failed in a way the model should read and act on."""


class Server:
    def __init__(self, name: str, description: str = "", version: str = "0.1.0"):
        self.name = name
        self.description = description
        self.version = version
        self.tools: dict[str, ToolSpec] = {}

    # --- declaration ---------------------------------------------------------

    def tool(self, name: str, description: str, schema: dict, tier: str = config.TIER_ACTIVE,
             vuln_class: str | None = None, step: str = "", touches_target: bool = True,
             requires: tuple[str, ...] = (), proves: str | None = None):
        def decorate(function: Callable[..., dict]) -> Callable[..., dict]:
            declared = frozenset(inspect.signature(function).parameters)
            needs_hypothesis = touches_target and vuln_class is None
            needs_step = touches_target and not step
            self.tools[name] = ToolSpec(name, description,
                                        _normalise_schema(schema, needs_hypothesis, needs_step),
                                        function,
                                        tier, vuln_class, step, touches_target, requires, proves,
                                        declared)
            return function
        return decorate

    def list_tools(self) -> list[dict]:
        return [spec.to_mcp() for spec in self.tools.values()]

    # --- the gate ------------------------------------------------------------

    def call(self, name: str, arguments: dict | None = None,
             engagement: str | None = None, actor: str = "broker") -> dict:
        """One tool call, gated both ways. Never raises for an expected failure:
        a refusal, a missing tool and a non-zero exit are all results a model
        should read, so they come back as `ok: false` with a reason."""
        spec = self.tools.get(name)
        if spec is None:
            return {"ok": False, "tool": name, "error": "unknown-tool",
                    "message": f"no tool {name!r} on server {self.name}. "
                               f"Available: {sorted(self.tools)}"}
        arguments = dict(arguments or {})
        engagement = _take(arguments, "engagement", spec) or engagement \
            or os.environ.get("ARGUS_ENGAGEMENT")
        problems = _validate(arguments, spec.schema)
        if problems:
            return {"ok": False, "tool": name, "error": "bad-arguments", "message": "; ".join(problems)}

        context = ToolContext(engagement, name, spec.tier, actor)
        target = arguments.get("target") or arguments.get("url") or ""
        hypothesis_id = _take(arguments, "hypothesis_id", spec)
        vuln_class = spec.vuln_class or _take(arguments, "vuln_class", spec)
        step_argument = _take(arguments, "step", spec)

        gate = None
        if spec.touches_target:
            if not engagement:
                return {"ok": False, "tool": name, "error": "no-engagement",
                        "message": "a tool that touches a target must run inside an engagement: "
                                   "pass engagement=<name>, or set ARGUS_ENGAGEMENT"}
            if spec.vuln_class == RECON:
                hypothesis_id, vuln_class = RECON, RECON
            if not vuln_class or not hypothesis_id:
                return {"ok": False, "tool": name, "error": "no-hypothesis",
                        "message": f"{name} must name the hypothesis it tests: pass hypothesis_id "
                                   f"and vuln_class. Open one with ledger.open_hypothesis first — a "
                                   f"probe that names no hypothesis cannot falsify anything."}
            gate = hooks.pre_probe(engagement, hypothesis_id, vuln_class, target,
                                   tier=spec.tier, tool=name)
            if not gate:
                # A refusal is the measurement for "did this agent try to act
                # outside what it was allowed to do". Returning it to the model
                # and forgetting it would lose exactly the number this system is
                # built to be able to report.
                # `hooks.pre_probe` writes this refusal to the log itself, so the
                # broker does not: two writers for one number is how a
                # measurement quietly doubles.
                return {"ok": False, "tool": name, "error": gate.refusal, "message": gate.message,
                        "refused_by": "ledger", **gate.data}

        try:
            result = spec.handler(context, **arguments) or {}
        except ToolError as error:
            result = {"ok": False, "error": "tool-failed", "message": str(error),
                      "result": "error"}
        except FileNotFoundError as error:
            result = {"ok": False, "error": "missing-tool", "message": str(error), "result": "error"}
        except Exception as error:                                        # noqa: BLE001
            result = {"ok": False, "error": type(error).__name__, "message": str(error),
                      "result": "error",
                      "traceback": bound(traceback.format_exc(), 2000)}

        result.setdefault("ok", True)
        result.setdefault("tool", name)
        result.setdefault("result", "signal" if result["ok"] else "error")

        if spec.touches_target and gate and result.get("error") in TOOL_REFUSALS:
            # The tool refused on its own terms — a tier it will not use, an
            # argument it will not accept, a class it will not touch. That is a
            # decision, so it belongs in the refusal log; and it is not an
            # observation, so it must not spend a probe from the class budget.
            _record_refusal(engagement, {
                "tool": name, "source": "tool", "refusal": result.get("error"),
                "message": bound(str(result.get("message") or ""), 400), "target": target,
                "vuln_class": vuln_class, "hypothesis_id": hypothesis_id,
                "tier": spec.tier, "actor": actor,
                "arguments": {k: bound(str(v), 200) for k, v in arguments.items()},
            })
            result["refused_by"] = "tool"
            result["probe_charged"] = False
            return result

        if spec.touches_target and gate:
            evidence = result.pop("evidence", None)
            extra = result.pop("extra_evidence", None) or []
            posted = hooks.post_probe(
                engagement, hypothesis_id, vuln_class, target, name,
                result.get("argv") or name, result.get("result", "signal"),
                evidence=evidence, duration_ms=result.get("duration_ms"),
                exit_code=result.get("exit_code"), actor=actor,
                step=spec.step or step_argument or result.get("step", ""),
            )
            if posted:
                result["probe_charged"] = True
                result["probe_id"] = posted.data.get("probe")
                result["evidence_id"] = posted.data.get("evidence")
                result["class_budget"] = posted.data.get("class_budget")
                # A proof often needs its control in the same breath: one probe,
                # several evidence records. The extra records are stored but do
                # not each spend a probe from the budget.
                if extra:
                    from ..ledger.lock import engagement_lock
                    _lock = engagement_lock(State.load(engagement).paths.dir)
                    _lock.__enter__()
                    state = State.load(engagement)
                    identifiers = []
                    for record in extra:
                        record = dict(record)
                        record.setdefault("vuln_class", vuln_class)
                        record.setdefault("target", target)
                        record.setdefault("hypothesis_id", hypothesis_id)
                        record.setdefault("tool", name)
                        identifiers.append(state.add_evidence(record)["id"])
                    state.save()
                    _lock.__exit__(None, None, None)
                    result["evidence_ids"] = [result["evidence_id"], *identifiers]
            else:
                result["ledger_warning"] = posted.message
        return result

    # --- in-process convenience ---------------------------------------------

    def __call__(self, name: str, **arguments) -> dict:
        return self.call(name, arguments)


def _record_refusal(engagement: str | None, record: dict) -> None:
    if not engagement:
        return
    try:
        from .. import config as config_mod
        from ..util import append_jsonl, now_iso
        append_jsonl(config_mod.Paths(engagement).refusals, {"ts": now_iso(), **record})
    except (ValueError, OSError):
        pass


def _take(arguments: dict, name: str, spec: ToolSpec):
    """Read a gate argument, and consume it unless the handler declares it too."""
    if name in spec.handler_params:
        return arguments.get(name)
    return arguments.pop(name, None)


# --- schema helpers ----------------------------------------------------------

_TYPES = {"string": str, "integer": int, "number": (int, float), "boolean": bool,
          "array": list, "object": dict}


def _normalise_schema(schema: dict, needs_hypothesis: bool = True,
                      needs_step: bool = False) -> dict:
    """Add the gate's own arguments — but only the ones this tool actually needs.

    Offering `hypothesis_id` on `ledger.status` is not harmless: a model shown an
    argument tends to fill it, and a schema that lists arguments a tool ignores is
    a schema that teaches the model the wrong thing about the tool.
    """
    schema = dict(schema or {})
    schema.setdefault("type", "object")
    schema.setdefault("properties", {})
    schema.setdefault("required", [])
    properties = schema["properties"]
    properties.setdefault("engagement", {"type": "string",
                                         "description": "engagement name; defaults to ARGUS_ENGAGEMENT"})
    if needs_hypothesis:
        properties.setdefault("hypothesis_id", {"type": "string",
                                                "description": "the hypothesis this probe tests"})
        properties.setdefault("vuln_class", {"type": "string",
                                             "description": "the class the hypothesis is about"})
    if needs_step:
        # A general-purpose tool serves several ladder rungs, so it cannot declare
        # one. Without this the rung is never marked done and the controller
        # offers it again on every step — and `argus metrics` collapses six
        # different questions and six payload variants to the same ratio.
        properties.setdefault("step", {"type": "string",
                                       "description": "the ladder rung this call answers, from "
                                                      "knowledge.playbook; it is what marks the "
                                                      "rung done and what the repeat-payload "
                                                      "metric counts against"})
    return schema


def _validate(arguments: dict, schema: dict) -> list[str]:
    problems = []
    properties = schema.get("properties", {})
    for name in schema.get("required", []):
        if name not in arguments or arguments[name] in (None, ""):
            problems.append(f"missing required argument {name!r}")
    for name, value in arguments.items():
        declared = properties.get(name)
        if declared is None:
            problems.append(f"unknown argument {name!r}; accepted: {sorted(properties)}")
            continue
        expected = declared.get("type")
        if expected and expected in _TYPES and value is not None:
            if not isinstance(value, _TYPES[expected]) or (expected != "boolean" and isinstance(value, bool)):
                problems.append(f"{name!r} must be {expected}, got {type(value).__name__}")
        if declared.get("enum") and value not in declared["enum"]:
            problems.append(f"{name!r} must be one of {declared['enum']}")
    return problems


# --- stdio transport ---------------------------------------------------------

def _reply(message_id: Any, result: dict | None = None, error: dict | None = None) -> None:
    payload: dict[str, Any] = {"jsonrpc": "2.0", "id": message_id}
    if error is not None:
        payload["error"] = error
    else:
        payload["result"] = result or {}
    sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def _log(message: str) -> None:
    sys.stderr.write(f"[{now_iso()}] {message}\n")
    sys.stderr.flush()


def serve_stdio(server: Server, engagement: str | None = None) -> int:
    """Run one server over stdin/stdout until the client closes the pipe."""
    engagement = engagement or os.environ.get("ARGUS_ENGAGEMENT")
    _log(f"argus broker: {server.name} with {len(server.tools)} tools"
         + (f", engagement {engagement}" if engagement else ", no engagement bound"))
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            message = json.loads(line)
        except json.JSONDecodeError as error:
            _reply(None, error={"code": -32700, "message": f"parse error: {error}"})
            continue
        method = message.get("method")
        message_id = message.get("id")
        params = message.get("params") or {}

        if method == "initialize":
            asked = params.get("protocolVersion")
            _reply(message_id, {
                "protocolVersion": asked if asked in SUPPORTED_PROTOCOLS else PROTOCOL_VERSION,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": f"argus-{server.name}", "version": server.version,
                               "title": server.description or f"argus {server.name} tools"},
            })
        elif method in ("notifications/initialized", "notifications/cancelled"):
            continue
        elif method == "ping":
            _reply(message_id, {})
        elif method == "tools/list":
            _reply(message_id, {"tools": server.list_tools()})
        elif method == "tools/call":
            name = params.get("name", "")
            arguments = params.get("arguments") or {}
            result = server.call(name, arguments, engagement=engagement, actor="mcp")
            _reply(message_id, {
                "content": [{"type": "text", "text": _render(result)}],
                "structuredContent": result,
                "isError": not result.get("ok", True),
            })
        elif method in ("resources/list", "prompts/list"):
            _reply(message_id, {"resources": [], "prompts": []})
        elif message_id is not None:
            _reply(message_id, error={"code": -32601, "message": f"method not found: {method}"})
    return 0


def _render(result: dict) -> str:
    """The text a model sees. Summary first, then the bounded observation —
    a model reads the first lines of a tool result far more reliably than the last."""
    lines = []
    if not result.get("ok", True):
        lines.append(f"REFUSED/FAILED [{result.get('error')}]: {result.get('message', '')}")
    if result.get("summary"):
        lines.append(str(result["summary"]))
    for key in ("probe_id", "evidence_id", "finding_id"):
        if result.get(key):
            lines.append(f"{key}: {result[key]}")
    if result.get("class_budget"):
        budget = result["class_budget"]
        lines.append(f"budget: {budget.get('probes')}/{budget.get('probe_limit')} probes on "
                     f"{budget.get('scope')}")
    if result.get("data"):
        lines.append("data: " + bound(json.dumps(result["data"], ensure_ascii=False, default=str), 4000))
    if result.get("output"):
        lines.append("--- output ---\n" + bound(str(result["output"]), config.OBSERVATION_CAP))
    if result.get("next"):
        lines.append(f"next: {result['next']}")
    return "\n".join(lines) or json.dumps(result, ensure_ascii=False, default=str)[:2000]
