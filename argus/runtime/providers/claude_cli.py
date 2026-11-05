"""Claude Code as a completion backend, for the subscription rather than a key.

`claude -p --output-format json` returns one JSON object with the final text, so
it works as a stateless text-dialect model exactly like opencode. Two caveats
worth stating because they change how the orchestrator should route to it:

* Claude Code brings its own tools. Here they are turned off (`--allowed-tools`
  empty) so the loop stays ours and every target-touching call still goes
  through the broker and the ledger.
* For a whole task rather than one step, the better route is delegation — let
  Claude Code run its own loop against our MCP server. That is
  `orchestrator/runner.py`, not this file.
"""
from __future__ import annotations

import json
import sys

from ...broker import exec as ex
from .base import (TEXT_PROTOCOL, Completion, Message, Provider, parse_text_call,
                   render_tools_for_text)
from .opencode_cli import render_prompt


class ClaudeCliProvider(Provider):
    name = "claude_cli"

    def __init__(self, timeout: int = 600, cwd: str | None = None, **_kwargs):
        self.timeout = timeout
        self.cwd = cwd

    def available(self) -> tuple[bool, str]:
        if ex.which("claude") is None:
            return False, "the claude CLI is not on PATH"
        return True, "claude code cli"

    def complete(self, system: str, messages: list[Message], tools: list[dict],
                 profile) -> Completion:
        ok, reason = self.available()
        if not ok:
            return Completion(error=reason)
        prompt = render_prompt(system, messages, tools)
        argv = ["claude", "-p", "--output-format", "json", "--model", profile.model,
                "--allowed-tools", ""]
        result = ex.run(argv, timeout=self.timeout, stdin=prompt, cwd=self.cwd)
        text, usage = _parse(result.stdout)
        if not text:
            return Completion(error=f"claude cli returned nothing usable (exit "
                                    f"{result.exit_code}): {result.stderr[:300]}")
        calls, done = parse_text_call(text)
        safeguard = usage.get("safeguard") or []
        for note in safeguard:
            print(f"claude cli answered {profile.model} with "
                  f"{note.get('fallback_model') or 'another model'}: "
                  f"{note.get('trigger', 'refusal')}/{note.get('category', '?')} "
                  f"(scope {note.get('scope', '?')})", file=sys.stderr)
        return Completion(text=text if not calls else "", tool_calls=calls,
                          input_tokens=usage.get("input_tokens", len(prompt) // 4),
                          output_tokens=usage.get("output_tokens", len(text) // 4),
                          stop_reason="end" if done or not calls else "tool_use",
                          raw={"done": done, "safeguard": safeguard})


def _parse(stdout: str) -> tuple[str, dict]:
    """Pull the final text out of whatever shape `claude -p --output-format json` used.

    Measured 2026-11-05: the CLI answered with a JSON *array* of transcript
    events rather than one object, so reading `data["result"]` found nothing and
    the planner reported "did not return a JSON object" even though the model had
    answered in full. The last `type == "result"` event carries the text, and the
    array also carries the safeguard record this provider must surface, so both
    shapes are handled here rather than at the call site.
    """
    stdout = stdout.strip()
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
    if isinstance(data, list):
        results = [event for event in data
                   if isinstance(event, dict) and event.get("type") == "result"]
        if not results:
            return stdout, {}
        final = results[-1]
        usage = dict(final.get("usage") or {})
        notes = _safeguard_notes(data)
        if notes:
            usage["safeguard"] = notes
        return str(final.get("result") or final.get("text") or ""), usage
    if isinstance(data, dict):
        return str(data.get("result") or data.get("text") or ""), (data.get("usage") or {})
    return stdout, {}


def _safeguard_notes(events: list) -> list[dict]:
    """Which model actually answered, when the CLI swapped it mid-session.

    `claude -p` can retry a flagged request on a weaker model and say so in a
    `model_refusal_fallback` event. The orchestrator pinned a model and must not
    report work as that model's when another one did it, so the swap travels back
    with the completion instead of staying in the CLI's transcript.
    """
    notes = []
    for event in events:
        if not isinstance(event, dict) or event.get("subtype") != "model_refusal_fallback":
            continue
        notes.append({"trigger": event.get("trigger", ""),
                      "category": event.get("api_refusal_category", ""),
                      "original_model": event.get("original_model", ""),
                      "fallback_model": event.get("fallback_model", ""),
                      "scope": event.get("scope", "")})
    return notes
