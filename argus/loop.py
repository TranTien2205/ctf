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
    """One agent's tool-use loop.

    Single-agent mode constructs its own scope/session/client (the defaults).
    Team mode injects the shared infra plus a role's tool subset, a role
    prompt, a custom seed and a stop event - the loop mechanics stay the same.
    """

    def __init__(self, cfg: Config, llm=None, quiet: bool = False, *,
                 scope: ScopeGuard | None = None,
                 session: Session | None = None,
                 client: GuardedClient | None = None,
                 board=None,
                 mcp=None,
                 agent_name: str = "agent",
                 role: str = "",
                 allowed=None,
                 system: str | None = None,
                 seed: str | None = None,
                 stop_event=None,
                 report: bool = True):
        self.cfg = cfg
        self.quiet = quiet
        self.agent_name = agent_name
        self.stop_event = stop_event
        self.report_enabled = report
        self.scope = scope or ScopeGuard(
            cfg.target, extra_hosts=cfg.scope_hosts,
            exclude_paths=cfg.exclude_paths, allow_private=cfg.allow_private,
        )
        self.session = session or Session(cfg.session_dir, cfg.target, meta={
            "model": cfg.model, "goal": cfg.goal,
            "scope": cfg.scope_hosts, "max_turns": cfg.max_turns,
        }, resume=Path(cfg.resume) if cfg.resume else None)
        skills_dir = Path(__file__).parent / "skills"
        if client is None:
            from .ratelimit import RateLimiter
            client = GuardedClient(
                self.scope, self.session, RateLimiter(cfg.rate_rps),
                default_headers=cfg.resolved_headers(),
                tls_verify=cfg.tls_verify, max_requests=cfg.max_requests,
                agent=agent_name,
            )
            self._owns_client = True
        else:
            self._owns_client = False
        if mcp is None:
            from .mcp import MCPManager, discover_config_path
            mcp = MCPManager(discover_config_path(cfg.mcp_config))
            self._owns_mcp = True
        else:
            self._owns_mcp = False
        self.ctx = Context(
            cfg=cfg, scope=self.scope, session=self.session,
            client=client, skills_dir=skills_dir,
            board=board, mcp=mcp, agent_name=agent_name, role=role,
            allowed=frozenset(allowed) if allowed else None,
        )
        self.llm = llm or ClaudeClient(cfg.api_key, cfg.api_base, cfg.model,
                                       max_tokens=cfg.llm_max_tokens,
                                       auth_token=cfg.auth_token)
        self.system = system or build_system(cfg, self.scope)
        self.seed = seed or build_seed(cfg)
        if getattr(self.session, "resumed", False) and seed is None \
                and self.session.findings:
            prior = "\n".join(
                f"- {f['id']} [{f['severity']}] {f['title']} ({f['url']})"
                for f in self.session.findings[:20])
            self.seed += (f"\n\nThis run RESUMES session {self.session.id}. "
                          f"Prior findings already recorded - do not re-verify "
                          f"them, build on them:\n{prior}")
        self.tools = TOOL_SCHEMAS if allowed is None else \
            [s for s in TOOL_SCHEMAS if s["name"] in allowed]
        self._last_error = ""

    def _log(self, msg: str) -> None:
        if not self.quiet:
            print(f"[{self.agent_name}] {msg}", flush=True)
        fname = "agent.log" if self.agent_name == "agent" else \
            f"agent-{self.agent_name}.log"
        try:
            with (self.session.dir / fname).open("a", encoding="utf-8") as fh:
                fh.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        except OSError:
            pass

    def run(self) -> dict:
        messages: list[dict] = [{"role": "user", "content": self.seed}]
        started = time.monotonic()
        turns = 0
        nudges = 0
        self._log(f"session {self.session.id} -> {self.cfg.target}")

        while True:
            if self.ctx.finished:
                break
            if self.stop_event is not None and self.stop_event.is_set():
                self._log("team stop event set; finishing")
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
                response = self.llm.chat(messages, self.tools, self.system)
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
        if self._owns_client:
            self.ctx.client.close()
        if self._owns_mcp and self.ctx.mcp is not None:
            self.ctx.mcp.close()
        report_path = ""
        if self.report_enabled:
            from .report.markdown import render_report
            report_path = str(render_report(
                self.session, self.cfg, self.ctx.finish_summary,
                extra={"mode": "team" if self.ctx.board is not None else "single",
                       "llm_calls": self.llm.calls,
                       "llm_tokens": {"in": self.llm.input_tokens,
                                      "out": self.llm.output_tokens}}))
        return {
            "session_dir": str(self.session.dir),
            "turns": turns,
            "requests": self.session._seq,
            "findings": len(self.session.findings),
            "report": report_path,
            "llm_calls": self.llm.calls,
            "llm_tokens": {"in": self.llm.input_tokens, "out": self.llm.output_tokens},
            "summary": self.ctx.finish_summary,
            "error": self._last_error or None,
        }
