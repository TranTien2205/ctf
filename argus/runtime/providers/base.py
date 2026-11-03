"""The provider-neutral shapes the loop speaks.

The loop never sees a provider's wire format. It builds `Message` objects and
gets a `Completion` back, and each adapter owns the translation — including the
`text` dialect, which is how a model with no native tool calling takes part in
exactly the same loop.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict = field(default_factory=dict)


@dataclass
class Message:
    role: str                                   # user | assistant | tool
    content: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_call_id: str = ""
    name: str = ""

    def chars(self) -> int:
        return len(self.content) + sum(len(json.dumps(c.arguments, default=str))
                                       for c in self.tool_calls)


@dataclass
class Completion:
    text: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    stop_reason: str = ""
    error: str | None = None
    raw: Any = None

    @property
    def ok(self) -> bool:
        return self.error is None


class Provider:
    """Subclasses implement `complete`. `available` says whether to even try."""

    name = "base"
    needs_key: str | None = None

    def available(self) -> tuple[bool, str]:
        return True, ""

    def complete(self, system: str, messages: list[Message], tools: list[dict],
                 profile) -> Completion:
        raise NotImplementedError


# --- the text dialect -------------------------------------------------------

TEXT_PROTOCOL = """\
You have no native tool-calling in this session, so a tool call is a JSON object
in a fenced block and nothing else in the message:

```json
{"tool": "<tool name>", "arguments": {...}, "why": "<one line: what this would show>"}
```

To finish, emit instead:

```json
{"done": true, "summary": "<what was established, and what was not>"}
```

Exactly one block per message. No prose outside it."""

_BLOCK_RE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)
_BARE_RE = re.compile(r"(\{(?:[^{}]|\{[^{}]*\})*\})", re.DOTALL)


def parse_text_call(text: str) -> tuple[list[ToolCall], dict | None]:
    """Pull the tool call out of a text answer, tolerantly.

    A model that was told to emit one fenced JSON object will sometimes emit two,
    or wrap it in an apology, or forget the fence. All three are recoverable and
    none of them is worth an extra round trip, so the last valid object wins.
    """
    candidates = _BLOCK_RE.findall(text) or _BARE_RE.findall(text)
    for raw in reversed(candidates):
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if not isinstance(parsed, dict):
            continue
        if parsed.get("done"):
            return [], parsed
        if parsed.get("tool"):
            return [ToolCall(id=f"text-{abs(hash(raw)) % 10**8}", name=str(parsed["tool"]),
                             arguments=parsed.get("arguments") or {})], None
    return [], None


def render_tools_for_text(tools: list[dict]) -> str:
    lines = []
    for tool in tools:
        schema = tool.get("inputSchema") or {}
        properties = schema.get("properties") or {}
        required = set(schema.get("required") or [])
        arguments = ", ".join(
            f"{name}{'*' if name in required else ''}:{spec.get('type', 'any')}"
            for name, spec in properties.items() if name not in ("engagement",))
        first_line = (tool.get("description") or "").strip().splitlines()[0]
        lines.append(f"- {tool['name']}({arguments})\n    {first_line}")
    return "\n".join(lines)
