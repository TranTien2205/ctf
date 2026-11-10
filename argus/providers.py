"""Providers other than Anthropic, speaking the loop's existing interface.

`AgentLoop` does not change for this. It calls `chat(messages, tools, system)`
and reads an Anthropic-shaped response - `ScriptedClient` has always proved
that interface is duck-typed - so a provider is an adapter that translates in
both directions and counts its own tokens.

The translation is the whole file. Anthropic puts tool calls and tool results
in content BLOCKS; OpenAI puts them in `tool_calls` on the assistant message
and in separate `role: "tool"` messages. Getting that wrong does not fail
loudly: the model simply stops calling tools and the run ends with no
findings, which is why the round trip is tested rather than inspected.
"""
from __future__ import annotations

import json
import time

import httpx

from .llm import LLMError, RETRYABLE


def _anthropic_to_openai(messages: list[dict], system) -> list[dict]:
    """Anthropic content blocks -> OpenAI chat messages."""
    out: list[dict] = []
    if system:
        text = system if isinstance(system, str) else "\n\n".join(
            str(b.get("text") or "") for b in system
            if isinstance(b, dict))
        if text:
            out.append({"role": "system", "content": text})
    for msg in messages or []:
        role = msg.get("role")
        content = msg.get("content")
        if isinstance(content, str):
            out.append({"role": role, "content": content})
            continue
        blocks = content if isinstance(content, list) else []
        if role == "assistant":
            text = "".join(str(b.get("text") or "") for b in blocks
                           if isinstance(b, dict) and b.get("type") == "text")
            calls = [{
                "id": str(b.get("id") or ""),
                "type": "function",
                "function": {"name": str(b.get("name") or ""),
                             "arguments": json.dumps(b.get("input") or {},
                                                     default=str)},
            } for b in blocks
                if isinstance(b, dict) and b.get("type") == "tool_use"]
            entry: dict = {"role": "assistant", "content": text or None}
            if calls:
                entry["tool_calls"] = calls
            out.append(entry)
            continue
        # a user turn: tool results become their own messages, in order
        texts = []
        for b in blocks:
            if not isinstance(b, dict):
                continue
            if b.get("type") == "tool_result":
                body = b.get("content")
                if isinstance(body, list):
                    body = "".join(str(x.get("text") or "") for x in body
                                   if isinstance(x, dict))
                out.append({"role": "tool",
                            "tool_call_id": str(b.get("tool_use_id") or ""),
                            "content": str(body or "")})
            elif b.get("type") == "text":
                texts.append(str(b.get("text") or ""))
        if texts:
            out.append({"role": "user", "content": "\n".join(texts)})
    return out


def _tools_to_openai(tools: list[dict]) -> list[dict]:
    out = []
    for t in tools or []:
        if not isinstance(t, dict):
            continue
        out.append({"type": "function", "function": {
            "name": t.get("name"),
            "description": t.get("description") or "",
            "parameters": t.get("input_schema")
                          or {"type": "object", "properties": {}},
        }})
    return out


def _openai_to_anthropic(data: dict) -> dict:
    """An OpenAI completion -> the response shape the loop reads."""
    choices = data.get("choices")
    choice = choices[0] if isinstance(choices, list) and choices else {}
    choice = choice if isinstance(choice, dict) else {}
    message = choice.get("message")
    message = message if isinstance(message, dict) else {}
    content: list[dict] = []
    text = message.get("content")
    if isinstance(text, str) and text.strip():
        content.append({"type": "text", "text": text})
    for call in message.get("tool_calls") or []:
        if not isinstance(call, dict):
            continue
        fn = call.get("function") if isinstance(call.get("function"), dict) else {}
        raw = fn.get("arguments")
        try:
            args = json.loads(raw) if isinstance(raw, str) and raw.strip() else {}
        except ValueError:
            # a model that emits malformed JSON arguments is a fact of life;
            # the dispatcher reports a bad-arguments error, which is a turn
            # the model can recover from - dropping the call silently is not
            args = {"__unparsed__": str(raw)[:2000]}
        if not isinstance(args, dict):
            args = {"__unparsed__": str(args)[:2000]}
        content.append({"type": "tool_use",
                        "id": str(call.get("id") or ""),
                        "name": str(fn.get("name") or ""),
                        "input": args})
    finish = str(choice.get("finish_reason") or "")
    stop = ("tool_use" if any(b["type"] == "tool_use" for b in content)
            else "max_tokens" if finish == "length" else "end_turn")
    usage = data.get("usage") if isinstance(data.get("usage"), dict) else {}
    details = usage.get("prompt_tokens_details")
    cached = (details.get("cached_tokens")
              if isinstance(details, dict) else 0) or 0
    # The two providers do not mean the same thing by "input tokens". OpenAI's
    # `prompt_tokens` INCLUDES the cached ones; Anthropic's `input_tokens`
    # excludes them and reports cache reads separately. Passing the raw number
    # through would bill every cached token twice - once at full input price
    # and again at the cache rate - so the cost report would be wrong in the
    # direction that flatters caching's cost, not its benefit.
    prompt = max(int(usage.get("prompt_tokens") or 0), 0)
    cached = max(min(int(cached), prompt), 0)
    return {"stop_reason": stop, "content": content,
            "usage": {"input_tokens": prompt - cached,
                      "output_tokens": usage.get("completion_tokens") or 0,
                      "cache_read_input_tokens": cached}}


class OpenAICompatClient:
    """Any server that speaks OpenAI chat-completions.

    One adapter covers OpenAI, DeepSeek, Groq, OpenRouter, Together and every
    local runtime (ollama, vLLM, llama.cpp, LM Studio) - the difference is a
    base URL and a key, which live in `models.json`.
    """

    def __init__(self, api_key: str, api_base: str, model: str,
                 max_tokens: int = 4096, timeout: float = 120.0,
                 allow_insecure_base: bool = False, temperature: float = 0.2):
        if not api_base:
            raise LLMError(f"model {model!r} has no api_base in models.json")
        if not api_base.startswith("https://") and not allow_insecure_base:
            # a key over plaintext is a leaked key; a loopback dev server
            # declares itself in the table instead of being guessed at here
            raise LLMError(
                f"refusing to send a credential to {api_base} over plaintext; "
                "set allow_insecure_base on the model in models.json if it is "
                "a local server")
        self.api_key = api_key
        self.api_base = api_base
        self.model = model
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.temperature = temperature
        self.calls = 0
        self.input_tokens = 0
        self.output_tokens = 0
        self.cache_read_tokens = 0
        self.cache_write_tokens = 0

    def chat(self, messages: list[dict], tools: list[dict], system) -> dict:
        if not self.api_key:
            raise LLMError(
                f"no credential for {self.model}: set the environment variable "
                "named in models.json for this model")
        payload = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "messages": _anthropic_to_openai(messages, system),
        }
        tls = _tools_to_openai(tools)
        if tls:
            payload["tools"] = tls
            payload["tool_choice"] = "auto"
        headers = {"authorization": f"Bearer {self.api_key}",
                   "content-type": "application/json"}
        delay, last = 2.0, ""
        for _ in range(5):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    resp = client.post(self.api_base, json=payload,
                                       headers=headers)
            except httpx.HTTPError as exc:
                last = f"{type(exc).__name__}: {exc}"
                time.sleep(delay)
                delay = min(delay * 2, 30)
                continue
            if resp.status_code == 200:
                try:
                    data = resp.json()
                except ValueError:
                    last = f"HTTP 200 with non-JSON body: {resp.text[:200]}"
                    time.sleep(delay)
                    delay = min(delay * 2, 30)
                    continue
                if not isinstance(data, dict):
                    last = "HTTP 200 with non-object JSON body"
                    time.sleep(delay)
                    delay = min(delay * 2, 30)
                    continue
                out = _openai_to_anthropic(data)
                self.calls += 1
                usage = out["usage"]
                self.input_tokens += int(usage.get("input_tokens") or 0)
                self.output_tokens += int(usage.get("output_tokens") or 0)
                self.cache_read_tokens += int(
                    usage.get("cache_read_input_tokens") or 0)
                return out
            body = resp.text[:500]
            last = f"HTTP {resp.status_code}: {body}"
            if resp.status_code not in RETRYABLE:
                raise LLMError(
                    f"{self.model} provider error {resp.status_code}: {body}")
            time.sleep(delay)
            delay = min(delay * 2, 30)
        raise LLMError(f"{self.model} provider unreachable after retries: {last}")
