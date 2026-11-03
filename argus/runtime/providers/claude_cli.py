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
        return Completion(text=text if not calls else "", tool_calls=calls,
                          input_tokens=usage.get("input_tokens", len(prompt) // 4),
                          output_tokens=usage.get("output_tokens", len(text) // 4),
                          stop_reason="end" if done or not calls else "tool_use",
                          raw={"done": done})


def _parse(stdout: str) -> tuple[str, dict]:
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
    if isinstance(data, dict):
        return str(data.get("result") or data.get("text") or ""), (data.get("usage") or {})
    return stdout, {}
