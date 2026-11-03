"""Anthropic Messages API, with native tool use."""
from __future__ import annotations

import json

from .. import credentials
from .base import Completion, Message, Provider, ToolCall
from .http_json import post

API = "https://api.anthropic.com/v1/messages"
VERSION = "2023-06-01"


class AnthropicProvider(Provider):
    name = "anthropic"
    needs_key = "anthropic"

    def __init__(self, api_key: str | None = None, base_url: str = API, **_kwargs):
        self.api_key = api_key or credentials.get("anthropic")
        self.base_url = base_url

    def available(self) -> tuple[bool, str]:
        if not self.api_key:
            return False, ("no anthropic key: set ANTHROPIC_API_KEY, or put it in "
                           f"{credentials.CREDENTIALS_FILE}")
        return True, "key present"

    def complete(self, system: str, messages: list[Message], tools: list[dict],
                 profile) -> Completion:
        ok, reason = self.available()
        if not ok:
            return Completion(error=reason)
        payload = {
            "model": profile.model,
            "max_tokens": profile.max_output_tokens,
            "system": system,
            "messages": _to_anthropic(messages),
            "temperature": profile.temperature,
        }
        if tools:
            payload["tools"] = [{"name": t["name"], "description": t.get("description", ""),
                                 "input_schema": t.get("inputSchema") or {"type": "object"}}
                                for t in tools]
        status, data, error = post(self.base_url,
                                   {"x-api-key": self.api_key, "anthropic-version": VERSION},
                                   payload, retries=profile.retry)
        if error:
            return Completion(error=error, raw=data)
        text_parts, calls = [], []
        for block in data.get("content") or []:
            if block.get("type") == "text":
                text_parts.append(block.get("text", ""))
            elif block.get("type") == "tool_use":
                calls.append(ToolCall(id=block.get("id", ""), name=block.get("name", ""),
                                      arguments=block.get("input") or {}))
        usage = data.get("usage") or {}
        return Completion("\n".join(text_parts), calls, usage.get("input_tokens", 0),
                          usage.get("output_tokens", 0), data.get("stop_reason", ""), None, data)


def _to_anthropic(messages: list[Message]) -> list[dict]:
    out: list[dict] = []
    for message in messages:
        if message.role == "tool":
            block = {"type": "tool_result", "tool_use_id": message.tool_call_id,
                     "content": message.content}
            if out and out[-1]["role"] == "user" and isinstance(out[-1]["content"], list):
                out[-1]["content"].append(block)
            else:
                out.append({"role": "user", "content": [block]})
            continue
        if message.role == "assistant" and message.tool_calls:
            content: list[dict] = []
            if message.content:
                content.append({"type": "text", "text": message.content})
            for call in message.tool_calls:
                content.append({"type": "tool_use", "id": call.id, "name": call.name,
                                "input": call.arguments})
            out.append({"role": "assistant", "content": content})
            continue
        out.append({"role": message.role, "content": message.content or "(no content)"})
    return out
