"""OpenAI-shaped chat completions: OpenAI, DeepSeek and OpenRouter share it."""
from __future__ import annotations

import json

from .. import credentials
from .base import Completion, Message, Provider, ToolCall
from .http_json import post


class OpenAIProvider(Provider):
    name = "openai"
    needs_key = "openai"
    base_url = "https://api.openai.com/v1"

    def __init__(self, api_key: str | None = None, base_url: str | None = None, **_kwargs):
        self.api_key = api_key or credentials.get(self.needs_key)
        if base_url:
            self.base_url = base_url

    def available(self) -> tuple[bool, str]:
        if not self.api_key:
            return False, f"no {self.needs_key} key configured"
        return True, "key present"

    def complete(self, system: str, messages: list[Message], tools: list[dict],
                 profile) -> Completion:
        ok, reason = self.available()
        if not ok:
            return Completion(error=reason)
        payload = {
            "model": profile.model,
            "messages": [{"role": "system", "content": system}, *_to_openai(messages)],
            "temperature": profile.temperature,
            "max_tokens": profile.max_output_tokens,
        }
        if tools:
            payload["tools"] = [{"type": "function",
                                 "function": {"name": t["name"],
                                              "description": t.get("description", ""),
                                              "parameters": t.get("inputSchema")
                                              or {"type": "object"}}}
                                for t in tools]
        status, data, error = post(f"{self.base_url}/chat/completions",
                                   {"Authorization": f"Bearer {self.api_key}"},
                                   payload, retries=profile.retry)
        if error:
            return Completion(error=error, raw=data)
        choices = data.get("choices") or [{}]
        message = choices[0].get("message") or {}
        calls = []
        for call in message.get("tool_calls") or []:
            function = call.get("function") or {}
            try:
                arguments = json.loads(function.get("arguments") or "{}")
            except json.JSONDecodeError:
                arguments = {"_unparsable": function.get("arguments")}
            calls.append(ToolCall(id=call.get("id", ""), name=function.get("name", ""),
                                  arguments=arguments if isinstance(arguments, dict) else {}))
        usage = data.get("usage") or {}
        return Completion(message.get("content") or "", calls, usage.get("prompt_tokens", 0),
                          usage.get("completion_tokens", 0),
                          choices[0].get("finish_reason", ""), None, data)


class DeepSeekProvider(OpenAIProvider):
    name = "deepseek"
    needs_key = "deepseek"
    base_url = "https://api.deepseek.com/v1"


class OpenRouterProvider(OpenAIProvider):
    name = "openrouter"
    needs_key = "openrouter"
    base_url = "https://openrouter.ai/api/v1"


def _to_openai(messages: list[Message]) -> list[dict]:
    out = []
    for message in messages:
        if message.role == "tool":
            out.append({"role": "tool", "tool_call_id": message.tool_call_id,
                        "name": message.name or "tool", "content": message.content})
        elif message.role == "assistant" and message.tool_calls:
            out.append({"role": "assistant", "content": message.content or None,
                        "tool_calls": [{"id": c.id, "type": "function",
                                        "function": {"name": c.name,
                                                     "arguments": json.dumps(c.arguments)}}
                                       for c in message.tool_calls]})
        else:
            out.append({"role": message.role, "content": message.content})
    return out
