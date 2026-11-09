"""Minimal MCP (Model Context Protocol) stdio client.

Lets the agent call tools hosted by external MCP servers (web search,
fetchers, CVE lookups) as first-class Argus tools. Speaks newline-delimited
JSON-RPC 2.0 over the server subprocess's stdio, lazily spawned on first use
and shared - one MCPClient per configured server per run.

Config file (JSON), discovered via --mcp-config / ARGUS_MCP_CONFIG / mcp.json:

    {"servers": {
        "search": {"command": ["npx", "-y", "some-mcp-server"],
                   "env": {"API_KEY": "..."}},
        "cvelist": {"command": ["python", "server.py"]}
    }}

Server output is untrusted external data: tools mark it as such so the model
treats it as data, not instructions. Every call is recorded in the transcript
as an mcp_call event.
"""
from __future__ import annotations

import json
import os
import queue
import subprocess
import sys
import threading
from pathlib import Path

PROTOCOL_VERSION = "2024-11-05"
CLIENT_INFO = {"name": "argus", "version": "1.0"}


def discover_config_path(explicit: str = "") -> Path | None:
    if explicit:
        p = Path(explicit)
        if not p.exists():
            # a declared-but-missing config must fail loud: silently
            # running without the servers the operator wired is worse
            raise SystemExit(f"--mcp-config not found: {explicit}")
        return p
    env = os.environ.get("ARGUS_MCP_CONFIG", "")
    if env:
        if not Path(env).exists():
            raise SystemExit(f"ARGUS_MCP_CONFIG not found: {env}")
        return Path(env)
    # cwd auto-discovery is opt-in: mcp.json names subprocesses to run,
    # so a planted file inside an untrusted working directory would hand
    # the model commands to execute. Operators declare it explicitly with
    # --mcp-config, ARGUS_MCP_CONFIG, or ARGUS_MCP_CWD=1.
    cwd_found = next(
        (Path(name) for name in
         ("mcp.json", ".argus-mcp.json", ".mcp.json")
         if Path(name).exists()), None)
    if cwd_found is not None:
        if os.environ.get("ARGUS_MCP_CWD") == "1":
            return cwd_found
        print(f"[argus] ignoring {cwd_found} in cwd - MCP configs name "
              "subprocesses; use --mcp-config or set ARGUS_MCP_CWD=1 to "
              "opt in", file=sys.stderr)
    return None


class MCPError(RuntimeError):
    pass


class MCPClient:
    """One MCP server subprocess. Calls are serialized under a lock; a
    persistent reader thread dispatches responses to pending callers."""

    def __init__(self, name: str, command: list[str], env: dict | None = None,
                 timeout_s: float = 30.0):
        self.name = name
        self.command = command
        self.env_extra = env or {}
        self.timeout_s = timeout_s
        self._proc: subprocess.Popen | None = None
        self._lock = threading.Lock()
        self._next_id = 0
        self._pending: dict[int, queue.Queue] = {}
        self._tools: list[dict] | None = None

    # ------------------------------------------------------------ plumbing
    # the base environment handed to a server is scrubbed of secrets -
    # an MCP subprocess must not inherit ANTHROPIC_API_KEY and friends;
    # servers get credentials only via their own 'env' spec.
    _SECRET_RE = ("KEY", "TOKEN", "SECRET", "PASSWORD", "CREDENTIAL",
                  "CREDS")

    def _start(self) -> None:
        if self._proc is not None and self._proc.poll() is None:
            return
        self._proc = None
        self._pending.clear()
        env = {k: v for k, v in os.environ.items()
               if not any(s in k.upper() for s in self._SECRET_RE)}
        env.update(self.env_extra)
        try:
            self._proc = subprocess.Popen(
                self.command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL, env=env, bufsize=0)
            threading.Thread(target=self._reader_loop, daemon=True).start()
            self._initialize()
        except Exception:
            # never leave a half-started server around - next call retries
            try:
                if self._proc:
                    self._proc.kill()
            except Exception:
                pass
            self._proc = None
            self._tools = None
            raise

    def _reader_loop(self) -> None:
        proc = self._proc
        # bound each readline: a hostile server writing a newline-free
        # stream would otherwise exhaust memory - the cap splits oversized
        # output into pieces that fail json.loads and are dropped
        while proc and proc.poll() is None:
            line = proc.stdout.readline(4 * 1024 * 1024)
            if not line:
                break
            try:
                msg = json.loads(line.decode("utf-8", "replace"))
            except ValueError:
                continue
            if not isinstance(msg, dict):
                continue    # a list/str frame would kill the reader on .get
            rid = msg.get("id")
            q = self._pending.get(rid)
            if q is not None:
                q.put(msg)
            # notifications and orphaned responses are dropped

    def _write(self, msg: dict) -> None:
        assert self._proc and self._proc.stdin
        self._proc.stdin.write(json.dumps(msg).encode() + b"\n")
        self._proc.stdin.flush()

    def _rpc(self, method: str, params: dict, timeout: float) -> dict:
        self._next_id += 1
        rid = self._next_id
        q: queue.Queue = queue.Queue()
        self._pending[rid] = q
        try:
            self._write({"jsonrpc": "2.0", "id": rid, "method": method,
                         "params": params})
            resp = q.get(timeout=timeout)
        except queue.Empty:
            raise MCPError(f"{method}: timed out after {timeout}s")
        except (BrokenPipeError, OSError) as exc:
            raise MCPError(f"{method}: {exc}")
        finally:
            self._pending.pop(rid, None)
        if "error" in resp:
            raise MCPError(f"{method}: {resp['error']}")
        result = resp.get("result")
        return result if isinstance(result, dict) else {}

    def _initialize(self) -> None:
        self._rpc("initialize", {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": CLIENT_INFO,
        }, timeout=self.timeout_s)
        self._write({"jsonrpc": "2.0", "method": "notifications/initialized"})

    # ------------------------------------------------------------ interface
    def tools(self) -> list[dict]:
        with self._lock:
            if self._tools is not None:
                return self._tools
            self._start()
            result = self._rpc("tools/list", {}, timeout=self.timeout_s)
            tools = result.get("tools")
            self._tools = [t for t in tools if isinstance(t, dict)] \
                if isinstance(tools, list) else []
            return self._tools

    def call(self, tool: str, arguments: dict, timeout_s: float) -> dict:
        with self._lock:
            self._start()
            return self._rpc("tools/call", {
                "name": tool, "arguments": arguments or {},
            }, timeout=timeout_s)

    def close(self) -> None:
        with self._lock:
            if self._proc and self._proc.poll() is None:
                try:
                    self._proc.terminate()
                    self._proc.wait(timeout=3)
                except Exception:
                    try:
                        self._proc.kill()
                    except Exception:
                        pass
            self._proc = None


class MCPManager:
    """All configured servers for one run; lazy, shared across agents."""

    def __init__(self, config_path: Path | None):
        self._clients: dict[str, MCPClient] = {}
        self._errors: dict[str, str] = {}
        if config_path is None:
            return
        try:
            data = json.loads(Path(config_path).read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            self._errors["<config>"] = f"unreadable MCP config: {exc}"
            return
        if not isinstance(data, dict):
            self._errors["<config>"] = "MCP config root is not an object"
            return
        servers = data.get("servers")
        if not isinstance(servers, dict):
            self._errors["<config>"] = "MCP config 'servers' is not an object"
            return
        for name, spec in servers.items():
            if not isinstance(spec, dict):
                self._errors[str(name)] = "server entry is not an object"
                continue
            cmd = spec.get("command")
            if not cmd:
                self._errors[str(name)] = "server entry has no 'command'"
                continue
            if isinstance(cmd, str):
                import shlex
                try:
                    cmd = shlex.split(cmd, posix=(os.name != "nt"))
                except ValueError:
                    cmd = []
            if not isinstance(cmd, list) or not cmd:
                self._errors[str(name)] = "server 'command' is not a list"
                continue
            try:
                timeout_s = float(spec.get("timeout_s", 30))
            except (TypeError, ValueError):
                timeout_s = 30.0
            env = spec.get("env")
            self._clients[str(name)] = MCPClient(
                str(name), [str(c) for c in cmd],
                env=env if isinstance(env, dict) else None,
                timeout_s=max(1.0, min(timeout_s, 600.0)))

    def servers(self) -> list[str]:
        return sorted(self._clients)

    def errors(self) -> dict:
        return dict(self._errors)

    def client(self, name: str) -> MCPClient | None:
        return self._clients.get(name)

    def configured(self) -> bool:
        return bool(self._clients or self._errors)

    def close(self) -> None:
        for c in self._clients.values():
            try:
                c.close()
            except Exception:
                pass
