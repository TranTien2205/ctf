"""Google Generative Language API, with function declarations."""
from __future__ import annotations

from .. import credentials
from .base import Completion, Message, Provider, ToolCall
from .http_json import post

BASE = "https://generativelanguage.googleapis.com/v1beta"
# The API rejects the JSON-Schema keywords it does not implement.
_DROP = {"additionalProperties", "$schema", "examples", "default"}


class GoogleProvider(Provider):
    name = "google"
    needs_key = "google"

    def __init__(self, api_key: str | None = None, base_url: str = BASE, **_kwargs):
        self.api_key = api_key or credentials.get("google")
        self.base_url = base_url

    def available(self) -> tuple[bool, str]:
        if not self.api_key:
            return False, "no google key: set GEMINI_API_KEY or GOOGLE_API_KEY"
        return True, "key present"

    def complete(self, system: str, messages: list[Message], tools: list[dict],
                 profile) -> Completion:
        ok, reason = self.available()
        if not ok:
            return Completion(error=reason)
        payload = {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": _to_google(messages),
            "generationConfig": {"temperature": profile.temperature,
                                 "maxOutputTokens": profile.max_output_tokens},
        }
        if tools:
            payload["tools"] = [{"functionDeclarations": [
                {"name": t["name"], "description": (t.get("description") or "")[:1000],
                 "parameters": _clean(t.get("inputSchema") or {"type": "object"})}
                for t in tools]}]
        url = f"{self.base_url}/models/{profile.model}:generateContent?key={self.api_key}"
        status, data, error = post(url, {}, payload, retries=profile.retry)
        if error:
            return Completion(error=error, raw=data)
        candidates = data.get("candidates") or [{}]
        parts = ((candidates[0].get("content") or {}).get("parts")) or []
        text_parts, calls = [], []
        for index, part in enumerate(parts):
            if "text" in part:
                text_parts.append(part["text"])
            elif "functionCall" in part:
                call = part["functionCall"]
                calls.append(ToolCall(id=f"g-{index}", name=call.get("name", ""),
                                      arguments=call.get("args") or {}))
        usage = data.get("usageMetadata") or {}
        return Completion("\n".join(text_parts), calls, usage.get("promptTokenCount", 0),
                          usage.get("candidatesTokenCount", 0),
                          candidates[0].get("finishReason", ""), None, data)


def _clean(schema: dict) -> dict:
    if not isinstance(schema, dict):
        return schema
    out = {}
    for key, value in schema.items():
        if key in _DROP:
            continue
        if key == "properties" and isinstance(value, dict):
            out[key] = {k: _clean(v) for k, v in value.items()}
        elif isinstance(value, dict):
            out[key] = _clean(value)
        else:
            out[key] = value
    return out


def _to_google(messages: list[Message]) -> list[dict]:
    out = []
    for message in messages:
        if message.role == "tool":
            out.append({"role": "user", "parts": [{"functionResponse": {
                "name": message.name or "tool", "response": {"result": message.content}}}]})
        elif message.role == "assistant" and message.tool_calls:
            parts = ([{"text": message.content}] if message.content else []) + [
                {"functionCall": {"name": c.name, "args": c.arguments}}
                for c in message.tool_calls]
            out.append({"role": "model", "parts": parts})
        else:
            out.append({"role": "model" if message.role == "assistant" else "user",
                        "parts": [{"text": message.content or "(no content)"}]})
    return out
