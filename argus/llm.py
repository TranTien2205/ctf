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


NO_CREDENTIAL_MSG = (
    "no Anthropic credential: set ANTHROPIC_API_KEY or pass --api-key, "
    "set ANTHROPIC_AUTH_TOKEN / CLAUDE_CODE_OAUTH_TOKEN, or sign in with "
    "Claude Code (Pro/Max) so ~/.claude/.credentials.json exists"
)


class ClaudeClient:
    def __init__(self, api_key: str, api_base: str, model: str,
                 max_tokens: int = 4096, timeout: float = 120.0,
                 auth_token: str = "", prompt_cache: bool = True):
        self.api_key = api_key
        self.auth_token = auth_token
        self.api_base = api_base
        self.model = model
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.calls = 0
        self.input_tokens = 0
        self.output_tokens = 0
        self.cache_read_tokens = 0
        self.cache_write_tokens = 0
        # prompt caching: the system+tools prefix (~30KB) is identical every
        # turn and the conversation tail is a stable prefix for the NEXT
        # turn - ephemeral breakpoints cut billed input by ~90% on reads.
        # Some auth paths (metered OAuth tiers) reject cache_control, so a
        # 400 mentioning cache disables it permanently for the client.
        self._cache = prompt_cache

    def _build(self, messages: list[dict], tools: list[dict],
               system, with_cache: bool) -> dict:
        sys_field = system
        tls = tools
        msgs = messages
        if with_cache:
            if sys_field and isinstance(sys_field, str):
                sys_field = [{"type": "text", "text": sys_field}]
            if tls:
                tls = list(tls)
                tls[-1] = {**tls[-1],
                           "cache_control": {"type": "ephemeral"}}
            if msgs:
                msgs = list(msgs)
                last = msgs[-1]
                cont = last.get("content")
                cont = ([{"type": "text", "text": cont}]
                        if isinstance(cont, str) else list(cont or []))
                if cont:
                    cont[-1] = {**cont[-1],
                                "cache_control": {"type": "ephemeral"}}
                    msgs[-1] = {**last, "content": cont}
        return {"model": self.model, "max_tokens": self.max_tokens,
                "system": sys_field, "tools": tls, "messages": msgs}

    def chat(self, messages: list[dict], tools: list[dict], system: str) -> dict:
        if not (self.api_key or self.auth_token):
            raise LLMError(NO_CREDENTIAL_MSG)
        if self.auth_token:
            headers = {
                "authorization": f"Bearer {self.auth_token}",
                "anthropic-version": API_VERSION,
                "anthropic-beta": "oauth-2025-04-20",
                "content-type": "application/json",
                "user-agent": "claude-cli/2.0.0 (external, cli)",
            }
            # Subscription OAuth tokens are only accepted for requests that
            # identify as Claude Code, which includes this system prefix.
            system_blocks = [
                {"type": "text",
                 "text": "You are Claude Code, Anthropic's official CLI for Claude."},
            ]
            if system:
                system_blocks.append({"type": "text", "text": system})
            system = system_blocks
        else:
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": API_VERSION,
                "anthropic-beta": "prompt-caching-2024-07-31",
                "content-type": "application/json",
            }
        delay = 2.0
        last_error = ""
        for attempt in range(5):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    resp = client.post(
                        self.api_base,
                        json=self._build(messages, tools, system, self._cache),
                        headers=headers)
            except httpx.HTTPError as exc:
                last_error = f"{type(exc).__name__}: {exc}"
                time.sleep(delay)
                delay = min(delay * 2, 30)
                continue
            if resp.status_code == 200:
                try:
                    data = resp.json()
                except ValueError:
                    # a proxy/gateway answered 200 with a non-JSON body -
                    # retry like any transient upstream failure rather
                    # than killing the whole run on a parse error
                    last_error = f"HTTP 200 with non-JSON body: {resp.text[:200]}"
                    time.sleep(delay)
                    delay = min(delay * 2, 30)
                    continue
                if not isinstance(data, dict):
                    # valid JSON, wrong shape - same transient-gateway class
                    last_error = f"HTTP 200 with non-object JSON body"
                    time.sleep(delay)
                    delay = min(delay * 2, 30)
                    continue
                self.calls += 1
                usage = data.get("usage")
                usage = usage if isinstance(usage, dict) else {}
                def _tok(key):
                    v = usage.get(key, 0)
                    return v if isinstance(v, int) and not isinstance(v, bool) else 0
                self.input_tokens += _tok("input_tokens")
                self.output_tokens += _tok("output_tokens")
                self.cache_read_tokens += _tok("cache_read_input_tokens")
                self.cache_write_tokens += _tok("cache_creation_input_tokens")
                return data
            body = resp.text[:500]
            # cache_control rejected (e.g. a plan that forbids it): drop the
            # feature once and resend the identical request without it
            if resp.status_code == 400 and self._cache \
                    and "cache" in body.lower():
                self._cache = False
                continue
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
        self.cache_read_tokens = 0
        self.cache_write_tokens = 0
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
