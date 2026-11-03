"""The agent loop: one shape of loop, one profile per model.

    while there is a next action and the budget holds:
        ask the controller what shape the next move is
        show the model the ledger, the action and the working set
        execute whatever tool it calls, through the broker and the ledger
        record the observation, the tokens and the cost

Three stop conditions, all of them recorded rather than inferred: the controller
says report, the step budget runs out, or the model stops calling tools. The
third one is the interesting failure — a model that has lost the thread starts
writing summaries instead of calling tools, so the loop counts those and ends
the run rather than paying for a conversation with itself.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field

from .. import config
from ..broker.serve import merge
from ..ledger import decide as decide_mod
from ..ledger.state import State
from ..util import append_jsonl, bound, new_id, now_iso
from . import context as context_mod
from . import profile as profile_mod
from . import prompts, providers
from .providers.base import Message

STOP_REASONS = ("controller-report", "step-budget", "no-tool-calls", "provider-error",
                "engagement-budget", "operator-stop", "objective-met")


@dataclass
class RunResult:
    run_id: str
    engagement: str
    model: str
    steps: int = 0
    tool_calls: int = 0
    refusals: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    stop_reason: str = ""
    findings_before: int = 0
    findings_after: int = 0
    last_action: dict = field(default_factory=dict)
    final_text: str = ""
    errors: list = field(default_factory=list)

    @property
    def findings_added(self) -> int:
        return self.findings_after - self.findings_before

    def to_dict(self) -> dict:
        data = {k: v for k, v in self.__dict__.items()}
        data["findings_added"] = self.findings_added
        return data

    def render(self) -> str:
        return (f"run {self.run_id} [{self.model}] {self.steps} step(s), "
                f"{self.tool_calls} tool call(s), {self.refusals} refusal(s), "
                f"{self.findings_added:+d} finding(s), "
                f"{self.input_tokens + self.output_tokens} tokens, "
                f"${self.cost_usd:.4f} — stopped: {self.stop_reason}")


class Harness:
    def __init__(self, engagement: str, model: str, provider: str | None = None,
                 server=None, profile=None, actor: str | None = None,
                 provider_kwargs: dict | None = None, tool_filter=None):
        self.engagement = engagement
        self.profile = profile or profile_mod.load(model)
        # `provider` is either a name to construct or an already-built adapter
        # (which is how the mock is injected). Keep the two apart: an earlier
        # version stored the adapter object as the name and the first event that
        # logged it failed to serialise.
        if provider is not None and hasattr(provider, "complete"):
            self.provider = provider
            self.provider_name = getattr(provider, "name", type(provider).__name__)
        else:
            self.provider_name = provider or self.profile.provider
            self.provider = providers.get(self.provider_name, **(provider_kwargs or {}))
        self.server = server or merge(list(_default_servers()))
        self.actor = actor or f"{self.provider_name}:{model}"
        self.tool_filter = tool_filter

    # --- tool surface --------------------------------------------------------

    def tools(self) -> list[dict]:
        specs = self.server.list_tools()
        if self.tool_filter:
            specs = [spec for spec in specs if self.tool_filter(spec["name"])]
        return specs

    # --- the loop ------------------------------------------------------------

    def run(self, task: str = "", max_steps: int | None = None) -> RunResult:
        state = State.load(self.engagement)
        run_id = new_id("run")
        transcript = state.paths.transcripts / f"{run_id}.jsonl"
        limit = max_steps or self.profile.max_steps
        result = RunResult(run_id, self.engagement, self.profile.model,
                           findings_before=len(state.data["findings"]))
        ok, reason = self.provider.available()
        if not ok:
            result.stop_reason = "provider-error"
            result.errors.append(reason)
            return result

        messages: list[Message] = []
        if task:
            messages.append(Message("user", f"TASK: {task}"))
        wasted = 0
        state.event("run.started", {"run": run_id, "model": self.profile.model,
                                    "provider": self.provider_name, "task": bound(task, 300)},
                    actor=self.actor)

        for step in range(1, limit + 1):
            state = State.load(self.engagement)
            action = decide_mod.decide(self.engagement).to_dict()
            result.last_action = action
            if action["action"] == "report":
                result.stop_reason = "controller-report"
                break
            if state.budget().spent:
                result.stop_reason = "engagement-budget"
                break

            extra = prompts.SHORT_CONTRACT if (
                step > 1 and step % max(1, self.profile.restate_contract_every) == 0) else ""
            system = prompts.system_prompt(state.digest(), action, self.profile, extra)
            messages, collapsed = context_mod.compact(messages, self.profile)
            if not messages:
                messages = [Message("user", "Begin. Follow the controller's next action.")]

            started = time.monotonic()
            completion = self.provider.complete(system, messages, self.tools(), self.profile)
            elapsed = int((time.monotonic() - started) * 1000)
            result.steps = step
            result.input_tokens += completion.input_tokens
            result.output_tokens += completion.output_tokens
            result.cost_usd += self.profile.cost(completion.input_tokens, completion.output_tokens)

            if not completion.ok:
                result.errors.append(f"step {step}: {completion.error}")
                _log(transcript, {"step": step, "kind": "provider-error",
                                  "error": completion.error, "ms": elapsed})
                if _terminal_provider_error(completion.error):
                    # An exhausted balance, a rejected key or a model the account
                    # cannot reach will not fix itself on the next call. Retrying
                    # a 402 three times spends three round trips to learn what the
                    # first one said: measured 2026-11-03 against a DeepSeek
                    # account with no balance.
                    result.stop_reason = "provider-error"
                    break
                if len(result.errors) >= self.profile.retry + 1:
                    result.stop_reason = "provider-error"
                    break
                continue

            _log(transcript, {"step": step, "kind": "assistant", "ms": elapsed,
                              "text": bound(completion.text, 4000),
                              "tool_calls": [{"name": c.name, "arguments": c.arguments}
                                             for c in completion.tool_calls],
                              "collapsed_results": collapsed,
                              "input_tokens": completion.input_tokens,
                              "output_tokens": completion.output_tokens})

            if not completion.tool_calls:
                result.final_text = completion.text
                from .providers.base import parse_text_call
                _calls, done = parse_text_call(completion.text or "")
                raw_done = (bool((completion.raw or {}).get("done"))
                            if isinstance(completion.raw, dict) else False)
                if done or raw_done:
                    result.stop_reason = "objective-met"
                    break
                wasted += 1
                if wasted >= 3:
                    result.stop_reason = "no-tool-calls"
                    break
                messages.append(Message("assistant", completion.text or "(no content)"))
                messages.append(Message("user", prompts.nudge(action, wasted)))
                continue

            wasted = 0
            calls = completion.tool_calls
            if self.profile.one_tool_per_step and len(calls) > 1:
                calls = calls[:1]
                result.errors.append(f"step {step}: {len(completion.tool_calls)} calls offered, "
                                     f"one executed (profile says one tool per step)")
            messages.append(Message("assistant", completion.text, tool_calls=calls))

            for call in calls:
                outcome = self.server.call(call.name, call.arguments,
                                           engagement=self.engagement, actor=self.actor)
                result.tool_calls += 1
                if not outcome.get("ok", True):
                    result.refusals += 1
                rendered = _render_for_model(outcome)
                messages.append(Message("tool", context_mod.observation(rendered, self.profile),
                                        tool_call_id=call.id, name=call.name))
                _log(transcript, {"step": step, "kind": "tool", "name": call.name,
                                  "arguments": call.arguments, "ok": outcome.get("ok"),
                                  "error": outcome.get("error"),
                                  "summary": bound(str(outcome.get("summary") or ""), 500),
                                  "probe_id": outcome.get("probe_id"),
                                  "evidence_id": outcome.get("evidence_id")})
                append_jsonl(state.paths.cost, {
                    "ts": now_iso(), "run": run_id, "model": self.profile.model,
                    "tool": call.name, "ok": outcome.get("ok"),
                    "input_tokens": completion.input_tokens,
                    "output_tokens": completion.output_tokens,
                    "cost_usd": round(self.profile.cost(completion.input_tokens,
                                                        completion.output_tokens), 6)})
        else:
            result.stop_reason = "step-budget"

        final_state = State.load(self.engagement)
        result.findings_after = len(final_state.data["findings"])
        result.stop_reason = result.stop_reason or "step-budget"
        final_state.event("run.finished", result.to_dict(), actor=self.actor)
        _log(transcript, {"kind": "result", **result.to_dict()})
        return result


_TERMINAL_ERRORS = ("insufficient balance", "insufficient_quota", "quota exceeded",
                    "invalid api key", "invalid_api_key", "authentication", "unauthorized",
                    "http 401", "http 402", "http 403", "no anthropic key", "no openai key",
                    "no deepseek key", "no google key", "is not on path", "not installed",
                    "model not found", "does not exist or you do not have access")


def _terminal_provider_error(message: str | None) -> bool:
    """Is this the kind of failure another attempt cannot clear?"""
    text = (message or "").lower()
    return any(marker in text for marker in _TERMINAL_ERRORS)


def _default_servers():
    from ..broker.servers import SERVER_NAMES
    return SERVER_NAMES


def _render_for_model(outcome: dict) -> str:
    from ..broker.mcp import _render
    return _render(outcome)


def _log(path, record: dict) -> None:
    append_jsonl(path, {"ts": now_iso(), **record})


def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(prog="argus-run", description=__doc__.splitlines()[0])
    parser.add_argument("engagement")
    parser.add_argument("--model", default="mock")
    parser.add_argument("--provider", default=None)
    parser.add_argument("--task", default="")
    parser.add_argument("--max-steps", type=int, default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    harness = Harness(args.engagement, args.model, provider=args.provider)
    result = harness.run(task=args.task, max_steps=args.max_steps)
    print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2) if args.json
          else result.render())
    return 0 if result.stop_reason not in ("provider-error",) else 1


if __name__ == "__main__":
    raise SystemExit(main())
