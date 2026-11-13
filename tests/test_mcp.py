"""MCP bridge: config discovery, stdio JSON-RPC roundtrip, tool gating."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from argus.mcp import MCPManager, discover_config_path
from argus.tools import mcp_tools

SERVER = str(Path(__file__).resolve().parent / "fake_mcp_server.py")


def _config(tmp_path) -> Path:
    path = tmp_path / "mcp.json"
    path.write_text(json.dumps({"servers": {
        "fake": {"command": [sys.executable, SERVER]},
    }}), encoding="utf-8")
    return path


def test_manager_roundtrip(tmp_path):
    mgr = MCPManager(_config(tmp_path))
    try:
        client = mgr.client("fake")
        tools = client.tools()
        assert [t["name"] for t in tools] == ["echo", "fail"]
        res = client.call("echo", {"a": 1, "b": "x"}, timeout_s=15)
        assert res["content"][0]["text"] == 'echo:{"a": 1, "b": "x"}'
    finally:
        mgr.close()


def test_mcp_call_tool_records_event(ctx, tmp_path):
    ctx.mcp = MCPManager(_config(tmp_path))
    try:
        out = mcp_tools.mcp_call(ctx, "fake", "echo", {"q": "test"})
        assert out["is_error"] is False
        assert 'echo:{"q": "test"}' in out["output"]
        assert out["untrusted"] is True
        entry = ctx.session.get_exchange(out["call_id"])
        assert entry["kind"] == "mcp_call"
        assert entry["server"] == "fake"
        assert entry["agent"] == "agent"
    finally:
        ctx.mcp.close()


def test_mcp_call_server_is_error(ctx, tmp_path):
    ctx.mcp = MCPManager(_config(tmp_path))
    try:
        out = mcp_tools.mcp_call(ctx, "fake", "fail", {})
        assert out["is_error"] is True
        assert "tool broke" in out["output"]
    finally:
        ctx.mcp.close()


def test_mcp_tools_without_config(ctx):
    ctx.mcp = None
    out = mcp_tools.mcp_call(ctx, "x", "y", {})
    assert "error" in out and "no MCP servers" in out["error"]
    listing = mcp_tools.mcp_list(ctx)
    assert listing["servers"] == []


def test_mcp_list_coerces_hostile_tool_entries(ctx, tmp_path, monkeypatch):
    """A buggy/hostile server returning non-str descriptions or non-dict
    tool entries must not crash the listing (0161307)."""
    class StubClient:
        def tools(self):
            # tools() itself filters non-dicts (mcp.py:178); descriptions
            # and names of any type get str()-coerced at mcp_list
            return [{"name": "ok", "description": 5},
                    {"name": ["x"], "description": None}, {}]

    mgr = MCPManager(_config(tmp_path))
    monkeypatch.setattr(mgr, "client", lambda name: StubClient())
    ctx.mcp = mgr
    try:
        out = mcp_tools.mcp_list(ctx)
        assert out["servers"][0]["server"] == "fake"
        assert out["servers"][0]["tools"][0]["description"] == "5"
        json.dumps(out)  # result must stay serializable
    finally:
        mgr.close()


def test_mcp_call_unknown_server(ctx, tmp_path):
    ctx.mcp = MCPManager(_config(tmp_path))
    try:
        out = mcp_tools.mcp_call(ctx, "nope", "x", {})
        assert "error" in out and "configured" in out["error"]
    finally:
        ctx.mcp.close()


def test_mcp_call_rejects_non_object_args(ctx, tmp_path):
    ctx.mcp = MCPManager(_config(tmp_path))
    try:
        out = mcp_tools.mcp_call(ctx, "fake", "echo", "not-a-dict")
        assert "error" in out
    finally:
        ctx.mcp.close()


def test_discover_config_path(tmp_path, monkeypatch):
    # a declared-but-missing config must fail loud, not silently drop the
    # servers the operator wired
    import pytest as _pt
    with _pt.raises(SystemExit):
        discover_config_path("/nonexistent/x.json")
    monkeypatch.setenv("ARGUS_MCP_CONFIG", "/nonexistent/y.json")
    with _pt.raises(SystemExit):
        discover_config_path("")
    monkeypatch.delenv("ARGUS_MCP_CONFIG")
    cfg = tmp_path / "mcp.json"
    cfg.write_text("{}")
    assert discover_config_path(str(cfg)) == cfg
    monkeypatch.setenv("ARGUS_MCP_CONFIG", str(cfg))
    assert discover_config_path("") == cfg


def test_cwd_mcp_config_is_opt_in(tmp_path, monkeypatch):
    """mcp.json names subprocesses to run - a planted file inside an
    untrusted working directory must not silently wire commands to the
    agent. cwd discovery requires ARGUS_MCP_CWD=1."""
    (tmp_path / "mcp.json").write_text(
        '{"servers": {"x": {"command": ["sh", "-c", "id"]}}}')
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("ARGUS_MCP_CONFIG", raising=False)
    monkeypatch.delenv("ARGUS_MCP_CWD", raising=False)
    assert discover_config_path("") is None
    monkeypatch.setenv("ARGUS_MCP_CWD", "1")
    assert discover_config_path("") == Path("mcp.json")


def test_mcp_call_scope_blocks_foreign_url(ctx, tmp_path):
    """A fetch-type MCP server runs its own network path - URL args must
    still be scope-checked, else mcp_call is a way around GuardedClient."""
    ctx.mcp = MCPManager(_config(tmp_path))
    try:
        out = mcp_tools.mcp_call(
            ctx, "fake", "echo", {"url": "https://evil.example/fetch"})
        assert "error" in out and "scope" in out["error"]
        # the block is recorded so the transcript shows what was attempted
        kinds = [e for e in ctx.session._transcript.values()
                 if e.get("scope_block")]
        assert kinds and "evil.example" in kinds[0]["scope_block"]
        # nested arguments are walked too
        out2 = mcp_tools.mcp_call(
            ctx, "fake", "echo",
            {"opts": {"url": "https://evil.example/"}})
        assert "error" in out2 and "scope" in out2["error"]
        # in-scope URL args pass the gate (the fake server doesn't fetch)
        out3 = mcp_tools.mcp_call(
            ctx, "fake", "echo", {"url": "http://127.0.0.1/x"})
        assert "scope" not in str(out3.get("error", ""))
    finally:
        ctx.mcp.close()


def test_a_hostile_frame_does_not_silently_kill_the_reader():
    """The mirror of the MCP *server* bug, on the client side.

    `_reader_loop` wrapped `json.loads` in `except ValueError`, and a deeply
    nested frame raises RecursionError - measured, `b"[" * 100000` does. The
    difference is the symptom: this runs in a thread, so the process lived
    on. The legitimate reply that followed was lost, and every later call
    waited out its full timeout and reported "timed out", pointing an
    operator at the server or the network instead of at a dead reader in
    this client.

    `tests/hostile_mcp_server.py` answers `initialize`, then emits the
    hostile frame followed by a valid reply - the exact sequence.
    """
    import sys
    import time
    from pathlib import Path

    from argus.mcp import MCPClient

    script = Path(__file__).resolve().parent / "hostile_mcp_server.py"
    client = MCPClient("hostile", [sys.executable, "-u", str(script)],
                       timeout_s=6.0)
    try:
        started = time.monotonic()
        tools = client.tools()
        elapsed = time.monotonic() - started
        # the reply after the hostile frame must arrive, and arrive fast -
        # a pass that took the full timeout would mean the reader died and
        # something else answered
        assert tools == [], tools
        assert elapsed < 5.0, elapsed
    finally:
        client.close()


def test_a_dead_reader_is_reported_as_such_not_as_a_timeout():
    """A dead reader and a slow server both show up as silence.

    They need different actions from the operator - one is this client's
    fault and the other is not - so `_rpc` checks whether the reader is
    still alive before blaming the server.
    """
    import queue
    import threading

    from argus.mcp import MCPClient, MCPError

    client = MCPClient.__new__(MCPClient)
    client.name = "stalled"
    client._pending = {}
    client._next_id = 0
    client.timeout_s = 0.2
    client._write = lambda msg: None
    dead = threading.Thread(target=lambda: None)
    dead.start()
    dead.join()
    client._reader = dead

    with pytest.raises(MCPError) as excinfo:
        client._rpc("tools/list", {}, 0.2)
    assert "no longer running" in str(excinfo.value)
    assert "not a timeout" in str(excinfo.value)
