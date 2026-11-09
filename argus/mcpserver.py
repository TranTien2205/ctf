"""argus as an MCP server: `user -> LLM -> MCP -> tool`.

`argus run` owns the loop: it talks to Claude itself and calls its own tools.
That is one shape of the chain and not the only one. This module is the other:
argus exposes its 55 tools over stdio JSON-RPC, and whichever LLM the operator
already has - Claude Code, an MCP-speaking IDE, an agent host - drives the
assessment through them.

What does NOT change when the driver moves outside: the scope guard, the rate
limiter, the transcript, the finding dedup, and the proof grading. The host
LLM gets argus's hands, not argus's permissions - it cannot widen scope, it
cannot send a byte that is not recorded, and a finding it records is graded
against the requirement for its class exactly as `argus run` would grade it.

Framing is newline-delimited JSON-RPC, symmetric with `argus/mcp.py` - the
client in this same package, so the two halves are testable against each
other.

Tools withheld from the MCP surface, and why:

    spawn_worker, request_worker, list_workers, finish_engagement
        team-mode orchestration. The host LLM is the orchestrator here; a
        second one inside argus would re-interpret the same intent.
    mcp_list, mcp_call
        argus calling out to other MCP servers while serving as one invites a
        loop the operator cannot see. Register those servers with the host.
"""
from __future__ import annotations

import json
import sys
import threading
from pathlib import Path
from typing import TextIO

from .config import Config
from .httpclient import GuardedClient
from .mcp import PROTOCOL_VERSION
from .ratelimit import RateLimiter
from .scope import ScopeGuard
from .session import Session
from .tools import Context, dispatch
from .tools.registry import TOOL_SCHEMAS

SERVER_INFO = {"name": "argus", "version": "1.0"}

# Every board tool, not four of them: `read_board`, `post_board_note`,
# `emit_lead` and `pull_leads` were advertised in the manifest and can only
# ever raise outside team mode, because there is no Board. A manifest entry a
# host can never call successfully is a lie in the catalogue.
from .tools.registry import BOARD_TOOLS                    # noqa: E402

WITHHELD = frozenset(BOARD_TOOLS) | frozenset({"mcp_list", "mcp_call"})

# JSON-RPC 2.0
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INTERNAL_ERROR = -32603


def tool_manifest(allowed: frozenset[str] | None = None) -> list[dict]:
    """TOOL_SCHEMAS in MCP shape. Anthropic calls it `input_schema`, MCP calls
    it `inputSchema`; the schema itself is identical."""
    out = []
    for schema in TOOL_SCHEMAS:
        name = schema["name"]
        if name in WITHHELD or (allowed is not None and name not in allowed):
            continue
        out.append({"name": name,
                    "description": schema.get("description", ""),
                    "inputSchema": schema.get("input_schema")
                    or {"type": "object", "properties": {}}})
    return out


class ArgusMCPServer:
    """One engagement, served over stdio. Single-threaded by design: the
    transcript is a sequence and a host that pipelines calls must still get a
    transcript it can read in order."""

    def __init__(self, cfg: Config, allowed: frozenset[str] | None = None,
                 stdin: TextIO | None = None, stdout: TextIO | None = None):
        self.cfg = cfg
        self.allowed = allowed
        self._in = stdin if stdin is not None else sys.stdin
        self._out = stdout if stdout is not None else sys.stdout
        self._lock = threading.Lock()
        self.scope = ScopeGuard(cfg.target, extra_hosts=cfg.scope_hosts,
                                exclude_paths=cfg.exclude_paths,
                                allow_private=cfg.allow_private)
        self.session = Session(
            cfg.session_dir, cfg.target,
            meta={"model": "mcp-host", "goal": cfg.goal,
                  "operator": cfg.operator, "mode": "mcp-serve",
                  "scope": cfg.scope_hosts, "max_turns": 0,
                  "max_requests": cfg.max_requests, "rate_rps": cfg.rate_rps,
                  "exclude_paths": cfg.exclude_paths, "proxy": bool(cfg.proxy),
                  "tls_verify": cfg.tls_verify,
                  "require_proof": cfg.require_proof,
                  "tools": sorted(allowed) if allowed else "all"},
            resume=Path(cfg.resume) if cfg.resume else None,
            secrets=cfg.secret_values, require_proof=cfg.require_proof)
        self.client = GuardedClient(
            self.scope, self.session, RateLimiter(cfg.rate_rps),
            default_headers=cfg.resolved_headers(), tls_verify=cfg.tls_verify,
            max_requests=cfg.max_requests, agent="mcp-host", proxy=cfg.proxy,
            secret_values=cfg.secret_values)
        self.ctx = Context(
            cfg=cfg, scope=self.scope, session=self.session,
            client=self.client,
            skills_dir=Path(__file__).parent / "skills",
            agent_name="mcp-host",
            allowed=None if allowed is None else frozenset(allowed) - WITHHELD)
        self._initialized = False

    # ------------------------------------------------------------- framing
    def _write(self, msg: dict) -> None:
        with self._lock:
            self._out.write(json.dumps(msg, ensure_ascii=False) + "\n")
            self._out.flush()

    def _reply(self, rid, result: dict) -> None:
        self._write({"jsonrpc": "2.0", "id": rid, "result": result})

    def _error(self, rid, code: int, message: str) -> None:
        self._write({"jsonrpc": "2.0", "id": rid,
                     "error": {"code": code, "message": message}})

    # ------------------------------------------------------------ handlers
    def handle(self, msg: dict) -> None:
        if not isinstance(msg, dict):
            self._error(None, INVALID_REQUEST, "frame is not an object")
            return
        method = msg.get("method")
        rid = msg.get("id")
        params = msg.get("params")
        params = params if isinstance(params, dict) else {}
        if not isinstance(method, str):
            self._error(rid, INVALID_REQUEST, "missing method")
            return
        # A JSON-RPC notification is any message with no id, whatever its
        # method. Replying to one - which this did for every method outside
        # the notifications/ namespace - is a protocol violation that some
        # hosts treat as a desync.
        if rid is None:
            if method == "notifications/initialized":
                self._initialized = True
            return
        if method == "initialize":
            self._reply(rid, {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": SERVER_INFO,
                "instructions": self._instructions(),
            })
            return
        if method in ("ping",):
            self._reply(rid, {})
            return
        if method == "tools/list":
            self._reply(rid, {"tools": tool_manifest(self.allowed)})
            return
        if method == "tools/call":
            self._call(rid, params)
            return
        if method in ("resources/list", "prompts/list"):
            # declared unsupported in capabilities; answer empty rather than
            # erroring, because several hosts probe both on connect
            key = "resources" if method.startswith("resources") else "prompts"
            self._reply(rid, {key: []})
            return
        self._error(rid, METHOD_NOT_FOUND, f"unknown method: {method}")

    def _call(self, rid, params: dict) -> None:
        name = params.get("name")
        arguments = params.get("arguments")
        arguments = arguments if isinstance(arguments, dict) else {}
        if not isinstance(name, str) or not name:
            self._error(rid, INVALID_REQUEST, "tools/call needs a name")
            return
        if name in WITHHELD:
            self._reply(rid, self._content(
                {"error": f"{name} is not served over MCP: the host LLM is "
                          "the orchestrator in this mode"}, is_error=True))
            return
        out = dispatch(self.ctx, name, arguments)
        # dispatch never raises; an error is data the host should read. The
        # envelope is only half of it: a tool that refuses internally - a scope
        # guard rejection, a finding the proof matrix will not accept - returns
        # {"result": {"error": ...}}, which reported isError=False and read to
        # the host as a success.
        inner = out.get("result")
        failed = "error" in out or (isinstance(inner, dict) and "error" in inner)
        self._reply(rid, self._content(out, is_error=failed))
        if name == "finish" and not failed:
            # A served engagement never sealed, so `argus verify` passed a
            # transcript with its tail deleted. finish() is the end of the
            # assessment in this mode too: render and seal.
            self._finalize()

    @staticmethod
    def _content(payload: dict, is_error: bool = False) -> dict:
        body = payload.get("result", payload) if "result" in payload else payload
        return {"content": [{"type": "text",
                             "text": json.dumps(body, ensure_ascii=False,
                                                default=str)}],
                "isError": bool(is_error)}

    def _instructions(self) -> str:
        from .system import build_system
        return build_system(self.cfg, self.scope)

    # --------------------------------------------------------------- loop
    def serve(self) -> int:
        """Read frames until stdin closes. Returns a process exit code."""
        for line in self._in:
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except ValueError:
                self._error(None, PARSE_ERROR, "invalid JSON frame")
                continue
            try:
                self.handle(msg)
            except Exception as exc:          # a crash must not kill the host
                self._error(msg.get("id") if isinstance(msg, dict) else None,
                            INTERNAL_ERROR, f"{type(exc).__name__}: {exc}")
        return 0

    def _finalize(self) -> None:
        """Render and seal, the way AgentLoop does at the end of a run."""
        try:
            from .report import render_report
            from .report.html import render_html
            from .report.sarif import render_sarif
            summary = getattr(self.ctx, "finish_summary", "") or ""
            render_report(self.session, self.cfg, summary=summary,
                          extra={"mode": "mcp-serve"})
            render_html(self.session, self.cfg, summary=summary)
            render_sarif(self.session)
            self.session.seal_artifacts()
        except Exception as exc:                            # pragma: no cover
            print(f"[argus] could not finalize session: "
                  f"{type(exc).__name__}: {exc}", file=sys.stderr, flush=True)

    def close(self) -> None:
        try:
            self.client.close()
        except Exception:
            pass


def serve(cfg: Config, allowed: frozenset[str] | None = None) -> int:
    server = ArgusMCPServer(cfg, allowed=allowed)
    print(f"[argus] mcp server on stdio - session {server.session.dir}",
          file=sys.stderr, flush=True)
    try:
        return server.serve()
    finally:
        server.close()
