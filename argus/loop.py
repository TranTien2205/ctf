"""The agent loop: messages -> Claude tool_use -> tool_result -> repeat.

Fully autonomous within scope. The loop ends on the finish tool, on budget
exhaustion, or when the model stops calling tools after a nudge.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from .config import Config
from .httpclient import GuardedClient
from .llm import ClaudeClient
from .scope import ScopeGuard
from .session import Session
from .system import build_seed, build_system
from .tools import TOOL_SCHEMAS, Context, dispatch

_MAX_RESULT_CHARS = 16_000


def _truncate_result(result: dict) -> str:
    text = json.dumps(result, ensure_ascii=False)
    if len(text) > _MAX_RESULT_CHARS:
        text = text[:_MAX_RESULT_CHARS] + "...[truncated]"
    return text


class AgentLoop:
    def __init__(self, cfg: Config, llm=None, quiet: bool = False):
        self.cfg = cfg
        self.quiet = quiet
        self.scope = ScopeGuard(
            cfg.target, extra_hosts=cfg.scope_hosts,
            exclude_paths=cfg.exclude_paths, allow_private=cfg.allow_private,
        )
        self.session = Session(cfg.session_dir, cfg.target, meta={
            "model": cfg.model, "goal": cfg.goal,
            "scope": cfg.scope_hosts, "max_turns": cfg.max_turns,
        })
        skills_dir = Path(__file__).parent / "skills"
        from .ratelimit import RateLimiter
        self.ctx = Context(
            cfg=cfg, scope=self.scope, session=self.session,
            client=GuardedClient(
                self.scope, self.session, RateLimiter(cfg.rate_rps),
                default_headers=cfg.resolved_headers(),
                tls_verify=cfg.tls_verify, max_requests=cfg.max_requests,
            ),
            skills_dir=skills_dir,
        )
        self.llm = llm or ClaudeClient(cfg.api_key, cfg.api_base, cfg.model,
                                       max_tokens=cfg.llm_max_tokens)
        self.system = build_system(cfg, self.scope)
        self._last_error = ""

    def _log(self, msg: str) -> None:
        if not self.quiet:
            print(msg, flush=True)
        with (self.session.dir / "agent.log").open("a", encoding="utf-8") as fh:
            fh.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")

    def run(self) -> dict:
        messages: list[dict] = [{"role": "user", "content": build_seed(self.cfg)}]
        started = time.monotonic()
        turns = 0
        nudges = 0
        self._log(f"session {self.session.id} -> {self.cfg.target}")

        while True:
            if self.ctx.finished:
                break
            if turns >= self.cfg.max_turns or \
                    time.monotonic() - started >= self.cfg.max_time_s:
                if nudges >= 1:
                    self._log("budget exhausted; forcing finish")
                    break
                messages.append({"role": "user", "content":
                    "Budget nearly exhausted. Record any confirmed findings now, "
                    "then call finish() with your summary. Do not start new work."})
                nudges += 1

            try:
                response = self.llm.chat(messages, TOOL_SCHEMAS, self.system)
            except Exception as exc:
                self._log(f"LLM error: {exc}")
                self._last_error = str(exc)
                break
            turns += 1

            content = response.get("content") or []
            messages.append({"role": "assistant", "content": content})

            tool_uses = [b for b in content if b.get("type") == "tool_use"]
            for b in content:
                if b.get("type") == "text" and b.get("text", "").strip():
                    self._log(f"agent: {b['text'].strip()[:400]}")

            if not tool_uses:
                if response.get("stop_reason") == "end_turn":
                    if nudges >= 2:
                        break
                    messages.append({"role": "user", "content":
                        "You stopped without calling a tool. If assessment is "
                        "complete, call finish(). Otherwise continue: what is "
                        "the next most valuable test?"})
                    nudges += 1
                    continue
                break

            results = []
            for call in tool_uses:
                name = call.get("name", "?")
                args = call.get("input") or {}
                self._log(f"tool {name} {json.dumps(args)[:200]}")
                out = dispatch(self.ctx, name, args)
                is_error = "error" in out
                self._log(f"  -> {'ERROR ' if is_error else ''}{_truncate_result(out)[:300]}")
                results.append({
                    "type": "tool_result",
                    "tool_use_id": call.get("id"),
                    "content": _truncate_result(out),
                    "is_error": is_error,
                })
            messages.append({"role": "user", "content": results})

        self._log(f"done in {turns} turns; findings={len(self.session.findings)}")
        self.ctx.client.close()
        from .report.markdown import render_report
        report_path = render_report(self.session, self.cfg, self.ctx.finish_summary)
        return {
            "session_dir": str(self.session.dir),
            "turns": turns,
            "requests": self.session._seq,
            "findings": len(self.session.findings),
            "report": str(report_path),
            "llm_tokens": {"in": self.llm.input_tokens, "out": self.llm.output_tokens},
            "summary": self.ctx.finish_summary,
            "error": self._last_error or None,
        }
