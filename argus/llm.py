"""Anthropic Messages API client - tool_use loop, stdlib-thin.

Uses httpx directly instead of the anthropic SDK so the dependency surface
stays at one package. Honors ANTHROPIC_BASE_URL for gateways/proxies.
"""
from __future__ import annotations

import time
from typing import Callable

import httpx

from .config import API_VERSION

RETRYABLE = (429, 500, 502, 503, 529)


class LLMError(RuntimeError):
    pass


class ClaudeClient:
    def __init__(self, api_key: str, api_base: str, model: str,
                 max_tokens: int = 4096, timeout: float = 120.0):
        self.api_key = api_key
        self.api_base = api_base
        self.model = model
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.calls = 0
        self.input_tokens = 0
        self.output_tokens = 0

    def chat(self, messages: list[dict], tools: list[dict], system: str) -> dict:
        if not self.api_key:
            raise LLMError(
                "ANTHROPIC_API_KEY is not set; export it or pass --api-key"
            )
        payload = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "system": system,
            "tools": tools,
            "messages": messages,
        }
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": API_VERSION,
            "content-type": "application/json",
        }
        delay = 2.0
        last_error = ""
        for attempt in range(5):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    resp = client.post(self.api_base, json=payload, headers=headers)
            except httpx.HTTPError as exc:
                last_error = f"{type(exc).__name__}: {exc}"
                time.sleep(delay)
                delay = min(delay * 2, 30)
                continue
            if resp.status_code == 200:
                data = resp.json()
                self.calls += 1
                usage = data.get("usage") or {}
                self.input_tokens += usage.get("input_tokens", 0)
                self.output_tokens += usage.get("output_tokens", 0)
                return data
            body = resp.text[:500]
            last_error = f"HTTP {resp.status_code}: {body}"
            if resp.status_code not in RETRYABLE:
                raise LLMError(f"Anthropic API error {resp.status_code}: {body}")
            time.sleep(delay)
            delay = min(delay * 2, 30)
        raise LLMError(f"Anthropic API unreachable after retries: {last_error}")


class ScriptedClient:
    """Deterministic stand-in for tests: replays canned tool_use turns."""

    def __init__(self, script: list[dict]):
        self.script = list(script)
        self.calls = 0
        self.input_tokens = 0
        self.output_tokens = 0
        self.seen_messages: list[list[dict]] = []

    def chat(self, messages: list[dict], tools: list[dict], system: str) -> dict:
        self.calls += 1
        self.seen_messages.append(messages)
        if not self.script:
            return {"stop_reason": "end_turn",
                    "content": [{"type": "text", "text": "script exhausted"}]}
        step = self.script.pop(0)
        content = []
        if step.get("text"):
            content.append({"type": "text", "text": step["text"]})
        for call in step.get("tool_calls", []):
            content.append({"type": "tool_use", **call})
        if isinstance(step.get("raw_content"), list):
            content = step["raw_content"]
        return {"stop_reason": step.get("stop_reason", "tool_use" if content else "end_turn"),
                "content": content}
