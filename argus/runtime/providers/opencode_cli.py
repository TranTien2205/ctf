"""opencode as a completion backend.

opencode is itself an agent harness, so there are two honest ways to use it and
this file is only the first:

* **as a model** (here): one `opencode run` per step with the rendered prompt,
  the text dialect for tool calls, and our loop keeping the state. Stateless per
  call, which costs input tokens but keeps every decision inside our ledger.
* **as an agent** (`orchestrator/runner.py`): hand it a task brief and our MCP
  server and let its own loop run. Cheaper per task, and the ledger still sees
  every tool call because the tools are ours.

Two flags matter. `--pure` keeps the user's own plugins and MCP servers out of
the session: without it a crowded global config sends more than a hundred tool
definitions upstream and the provider rejects the request outright — measured on
this machine, `Invalid value for 'tools': maximum number of items is 128`.
`--format json` gives newline-delimited events instead of a rendered TUI, which
is the only output worth parsing.
"""
from __future__ import annotations

import json
import re

from ...broker import exec as ex
from .base import (TEXT_PROTOCOL, Completion, Message, Provider, parse_text_call,
                   render_tools_for_text)

ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
_TEXT_KEYS = ("text", "content", "message")


class OpenCodeProvider(Provider):
    name = "opencode"

    def __init__(self, model_prefix: str = "", timeout: int = 600, pure: bool = True,
                 cwd: str | None = None, **_kwargs):
        # opencode names a model `provider/model`; a profile only carries the
        # model, so the prefix says which of the user's credentials to spend.
        self.model_prefix = model_prefix
        self.timeout = timeout
        self.pure = pure
        self.cwd = cwd

    def available(self) -> tuple[bool, str]:
        if ex.which("opencode") is None:
            return False, "opencode is not on PATH"
        return True, "opencode cli"

    def _model(self, model: str) -> str:
        if "/" in model:
            return model
        return f"{self.model_prefix}/{model}" if self.model_prefix else model

    def complete(self, system: str, messages: list[Message], tools: list[dict],
                 profile) -> Completion:
        ok, reason = self.available()
        if not ok:
            return Completion(error=reason)
        prompt = render_prompt(system, messages, tools)
        argv = ["opencode", "run", "--format", "json", "-m", self._model(profile.model)]
        if self.pure:
            argv.append("--pure")
        if profile.reasoning:
            argv += ["--variant", profile.reasoning]
        argv.append(prompt)
        result = ex.run(argv, timeout=self.timeout, cwd=self.cwd)
        text, error = _collect(result.stdout)
        if error:
            return Completion(error=f"opencode: {error}", raw=result.stdout[:2000])
        if not text.strip():
            return Completion(error=f"opencode produced no text (exit {result.exit_code}): "
                                    f"{result.stderr[:400] or result.stdout[:400]}")
        calls, done = parse_text_call(text)
        return Completion(text=text if not calls else "", tool_calls=calls,
                          input_tokens=len(prompt) // 4, output_tokens=len(text) // 4,
                          stop_reason="end" if done or not calls else "tool_use",
                          raw={"done": done})


def render_prompt(system: str, messages: list[Message], tools: list[dict]) -> str:
    """One self-contained prompt: contract, tools, transcript, and the ask.

    A stateless backend has to be handed the whole conversation each turn. That
    is the cost of using a subscription CLI as a model, and it is why the profile
    for such a model keeps `history_chars` low.
    """
    parts = [system, "", "## Tools", render_tools_for_text(tools), "", TEXT_PROTOCOL, "",
             "## Transcript so far"]
    for message in messages:
        if message.role == "tool":
            parts.append(f"TOOL RESULT [{message.name}]:\n{message.content}")
        elif message.role == "assistant":
            if message.tool_calls:
                for call in message.tool_calls:
                    parts.append(f"YOU CALLED {call.name} with "
                                 f"{json.dumps(call.arguments, ensure_ascii=False)}")
            if message.content:
                parts.append(f"YOU SAID: {message.content}")
        else:
            parts.append(f"OPERATOR: {message.content}")
    parts += ["", "## Your move", "Emit exactly one JSON block, as specified above."]
    return "\n".join(parts)


def _collect(stdout: str) -> tuple[str, str | None]:
    """Pull assistant text out of opencode's event stream, tolerantly."""
    chunks, error = [], None
    for line in stdout.splitlines():
        line = ANSI_RE.sub("", line).strip()
        if not line:
            continue
        if not line.startswith("{"):
            chunks.append(line)                      # default-format fallback
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            chunks.append(line)
            continue
        if event.get("type") == "error":
            detail = ((event.get("error") or {}).get("data") or {}).get("message")
            error = detail or json.dumps(event.get("error"))[:400]
            continue
        chunks.extend(_strings(event))
    return "\n".join(c for c in chunks if c), error


def _strings(event, depth: int = 0) -> list[str]:
    """Collect the text-bearing leaves of one event, whatever the schema calls them."""
    if depth > 6:
        return []
    out = []
    if isinstance(event, dict):
        for key, value in event.items():
            if key in _TEXT_KEYS and isinstance(value, str) and value.strip():
                out.append(value)
            else:
                out.extend(_strings(value, depth + 1))
    elif isinstance(event, list):
        for item in event:
            out.extend(_strings(item, depth + 1))
    return out
