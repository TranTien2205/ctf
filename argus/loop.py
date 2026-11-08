"""The agent loop: messages -> Claude tool_use -> tool_result -> repeat.

Fully autonomous within scope. The loop ends on the finish tool, on budget
exhaustion, or when the model stops calling tools after a nudge.
"""
from __future__ import annotations

import json
import re
import sys
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
# Older tool_results are compacted to stubs once this many newer result
# messages exist - 80 turns x 16KB otherwise overruns the context window
# mid-run and the API error kills the engagement. read_response(rid)
# always re-fetches the full exchange, so nothing is lost.
_KEEP_FULL_RESULTS = 8


def _truncate_result(result: dict) -> str:
    text = json.dumps(result, ensure_ascii=False)
    if len(text) > _MAX_RESULT_CHARS:
        text = text[:_MAX_RESULT_CHARS] + "...[truncated]"
    return text


def _compact_history(messages: list) -> None:
    """Shrink tool_result payloads older than the last _KEEP_FULL_RESULTS
    result-messages, keeping the cited request ids visible so the model
    can re-inspect via read_response."""
    result_msgs = [i for i, m in enumerate(messages)
                   if m.get("role") == "user"
                   and isinstance(m.get("content"), list)
                   and any(b.get("type") == "tool_result"
                           for b in m["content"])]
    for i in result_msgs[:-_KEEP_FULL_RESULTS] if len(
            result_msgs) > _KEEP_FULL_RESULTS else []:
        for b in messages[i]["content"]:
            if b.get("type") != "tool_result":
                continue
            c = b.get("content")
            if not isinstance(c, str) or len(c) < 400:
                continue
            rids = re.findall(r'"request_id"\s*:\s*"(r\d+)"', c)
            b["content"] = (f"[prior tool result cleared "
                            f"({len(c)} chars; rids: {', '.join(rids[:8]) or 'none'})"
                            " - call read_response(rid) to re-inspect]")


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
            "model": cfg.model, "goal": cfg.goal, "operator": cfg.operator,
            "scope": cfg.scope_hosts, "max_turns": cfg.max_turns,
            "max_requests": cfg.max_requests, "rate_rps": cfg.rate_rps,
            "exclude_paths": cfg.exclude_paths, "proxy": bool(cfg.proxy),
            "tls_verify": cfg.tls_verify,
            "tools": sorted(allowed) if allowed else "all",
        }, resume=Path(cfg.resume) if cfg.resume else None,
            secrets=cfg.secret_values)
        skills_dir = Path(__file__).parent / "skills"
        if client is None:
            from .ratelimit import RateLimiter
            client = GuardedClient(
                self.scope, self.session, RateLimiter(cfg.rate_rps),
                default_headers=cfg.resolved_headers(),
                tls_verify=cfg.tls_verify, max_requests=cfg.max_requests,
                agent=agent_name, proxy=cfg.proxy,
                secret_values=cfg.secret_values,
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
            from .session import sanitized_findings
            prior = "\n".join(
                f"- {f['id']} [{f['severity']}] {f['title']} ({f['url']})"
                for f in sanitized_findings(self.session.findings)[:20])
            self.seed += (f"\n\nThis run RESUMES session {self.session.id}. "
                          f"Prior findings already recorded - do not re-verify "
                          f"them, build on them:\n{prior}")
        self.tools = TOOL_SCHEMAS if allowed is None else \
            [s for s in TOOL_SCHEMAS if s["name"] in allowed]
        if board is None:
            from .tools.registry import BOARD_TOOLS
            self.tools = [s for s in self.tools
                          if s["name"] not in BOARD_TOOLS]
        self._last_error = ""

    def _log(self, msg: str) -> None:
        if not self.quiet:
            print(f"[{self.agent_name}] {msg}", flush=True)
        fname = "agent.log" if self.agent_name == "agent" else \
            f"agent-{self.agent_name}.log"
        try:
            from .session import _redact_obj
            msg = _redact_obj(msg, self.session.secret_values)
            with (self.session.dir / fname).open("a", encoding="utf-8", newline="") as fh:
                fh.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")
        except OSError:
            pass

    def run(self) -> dict:
        messages: list[dict] = [{"role": "user", "content": self.seed}]
        started = time.monotonic()
        turns = 0
        nudges = 0
        self._log(f"session {self.session.id} -> {self.cfg.target}")
        # a malformed MCP config or a server spec without 'command' must
        # be operator-visible, not silently absent for the whole run
        if self._owns_mcp and self.ctx.mcp is not None:
            for name, err in self.ctx.mcp.errors().items():
                self._log(f"mcp config error {name}: {err}")
                print(f"[argus] mcp config error {name}: {err}",
                      file=sys.stderr)

        while True:
            if self.ctx.finished:
                break
            if self.stop_event is not None and self.stop_event.is_set():
                self._log("team stop event set; finishing")
                break
            remaining_turns = self.cfg.max_turns - turns
            remaining_time = self.cfg.max_time_s - (time.monotonic() - started)
            if remaining_turns <= 0 or remaining_time <= 0:
                if nudges >= 2:
                    self._log("budget exhausted; forcing finish")
                    break
                messages.append({"role": "user", "content":
                    "Budget nearly exhausted. Record any confirmed findings now, "
                    "then call finish() with your summary. Do not start new work."})
                nudges += 1
            elif nudges == 0 and (remaining_turns <= max(3, self.cfg.max_turns // 5)
                                  or remaining_time <= self.cfg.max_time_s / 5):
                messages.append({"role": "user", "content":
                    f"Budget warning: ~{remaining_turns} turns and "
                    f"{int(remaining_time)}s remain. Record every confirmed "
                    "finding NOW (do not defer them), prioritize remaining "
                    "tests, then call finish()."})
                nudges += 1

            _compact_history(messages)
            try:
                response = self.llm.chat(messages, self.tools, self.system)
            except KeyboardInterrupt:
                self._log("interrupted by operator")
                self._last_error = "interrupted"
                break
            except Exception as exc:
                self._log(f"LLM error: {exc}")
                self._last_error = str(exc)
                break
            turns += 1

            # a non-Anthropic gateway can answer 200 with a shape that is
            # not {content: [blocks]} - coerce or an AttributeError would
            # kill the run outside the LLM try/except, artifacts unsealed
            content = [b for b in
                       (response.get("content") or [])
                       if isinstance(b, dict)] \
                if isinstance(response, dict) else []
            messages.append({"role": "assistant", "content": content})

            tool_uses = [b for b in content if b.get("type") == "tool_use"]
            for b in content:
                if b.get("type") == "text" and b.get("text", "").strip():
                    self._log(f"agent: {b['text'].strip()[:400]}")

            if not tool_uses:
                if isinstance(response, dict) and \
                        response.get("stop_reason") == "end_turn":
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
                if self.ctx.finished:
                    # finish() mid-batch: later calls must not fire -
                    # the run is done, and post-finish requests would
                    # pollute the transcript tail
                    results.append({
                        "type": "tool_result",
                        "tool_use_id": call.get("id"),
                        "content": '{"skipped": "engagement already finished"}',
                        "is_error": False,
                    })
                    continue
                name = call.get("name", "?")
                args = call.get("input") or {}
                self._log(f"tool {name} {json.dumps(args)[:200]}")
                try:
                    out = dispatch(self.ctx, name, args)
                except KeyboardInterrupt:
                    self._log("interrupted by operator")
                    self._last_error = "interrupted"
                    out = None
                    break
                # tools signal soft errors as {"error": ...} inside the
                # dispatch {"result": ...} wrapper - flag both layers so the
                # API marks the tool_result as an error for the model
                is_error = "error" in out or \
                    "error" in (out.get("result") or {})
                # the model sees real response headers (it needs them); the
                # persisted log gets the redacted copy, same as transcript
                logged = dict(out)
                if isinstance(out.get("result"), dict) and \
                        isinstance(out["result"].get("headers"), dict):
                    from .httpclient import _redact_headers
                    secrets = getattr(self.ctx.client, "_secret_values",
                                      set())
                    logged = {**out, "result": {
                        **out["result"], "headers": _redact_headers(
                            out["result"]["headers"], secrets)}}
                self._log(f"  -> {'ERROR ' if is_error else ''}{_truncate_result(logged)[:300]}")
                results.append({
                    "type": "tool_result",
                    "tool_use_id": call.get("id"),
                    "content": _truncate_result(out),
                    "is_error": is_error,
                })
            if self._last_error == "interrupted":
                break  # Ctrl-C during a tool must end the run, not retry
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
                       "llm_tokens": self._token_stats()}))
            # anchor every un-chained artifact (meta/findings/summary/
            # report.*) into the transcript so post-run edits are
            # detectable by verify - best-effort: a seal failure must not
            # kill a completed run
            try:
                self.session.seal_artifacts()
            except OSError as exc:
                self._log(f"warning: artifact seal failed: {exc}")
        return {
            "session_dir": str(self.session.dir),
            "turns": turns,
            "requests": self.session._seq,
            "findings": len(self.session.findings),
            "report": report_path,
            "llm_calls": self.llm.calls,
            "llm_tokens": self._token_stats(),
            "summary": self.ctx.finish_summary,
            "error": self._last_error or None,
        }

    def _token_stats(self) -> dict:
        return {"in": self.llm.input_tokens,
                "out": self.llm.output_tokens,
                "cache_read": getattr(self.llm, "cache_read_tokens", 0),
                "cache_write": getattr(self.llm, "cache_write_tokens", 0)}
