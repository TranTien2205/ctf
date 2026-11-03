"""A scripted provider, so the loop can be tested without a model or a key."""
from __future__ import annotations

from .base import Completion, Message, Provider, ToolCall


class MockProvider(Provider):
    name = "mock"

    def __init__(self, script: list | None = None, **_kwargs):
        # Each entry is either {"tool": name, "arguments": {...}} or {"text": "..."}
        self.script = list(script or [])
        self.calls = 0

    def available(self) -> tuple[bool, str]:
        return True, "scripted"

    def complete(self, system: str, messages: list[Message], tools: list[dict],
                 profile) -> Completion:
        self.calls += 1
        if not self.script:
            return Completion(text="done: the script is empty", stop_reason="end",
                              input_tokens=len(system) // 4, output_tokens=8)
        step = self.script.pop(0)
        if "tool" in step:
            known = {tool["name"] for tool in tools}
            if step["tool"] not in known:
                return Completion(text=f"the script asked for {step['tool']}, which is not offered",
                                  stop_reason="error", error=None)
            return Completion(
                tool_calls=[ToolCall(id=f"mock-{self.calls}", name=step["tool"],
                                     arguments=step.get("arguments") or {})],
                stop_reason="tool_use", input_tokens=len(system) // 4, output_tokens=24)
        return Completion(text=step.get("text", ""), stop_reason="end",
                          input_tokens=len(system) // 4, output_tokens=len(step.get("text", "")) // 4)
