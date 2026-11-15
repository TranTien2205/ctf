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
        # An uppercase scheme is the same URL. `_url_args` tested
        # `value.startswith(("http://", "https://"))`, so `HTTP://` was
        # collected by nobody and checked by nobody, while the server would
        # fetch it exactly as it fetches the lowercase form - this gate is
        # the only thing between an MCP argument and that server's own
        # socket. The scope guard refuses it when asked; it was not asked.
        for spelling in ("HTTP://evil.example/fetch",
                         "HTTPS://evil.example/fetch",
                         "HtTpS://evil.example/fetch"):
            blocked = mcp_tools.mcp_call(ctx, "fake", "echo",
                                         {"url": spelling})
            assert "error" in blocked and "scope" in blocked["error"], \
                f"{spelling} crossed into the server process: {blocked}"
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


def test_close_does_not_wait_for_a_lock_an_in_flight_call_holds():
    """The bounded shutdown was bounded everywhere except its last line.

    `call()` takes `self._lock` and holds it across `_rpc`'s blocking
    `q.get(timeout=...)`, a per-server timeout clamped at 600s. `close()`
    took the same lock unconditionally. The manager is shared by every
    worker thread, so `Coordinator.run()` - which bounds its join to 30s
    because "workers are daemon threads so a straggler can't hang" - then
    called `close()` and blocked on the lock the straggler was holding.

    Terminating the subprocess is what unblocks that waiter: the server's
    stdout closes, the reader thread ends, and `_rpc` returns its
    dead-reader error rather than waiting out the timeout. So `close()`
    tries briefly for the lock and proceeds without it, and this asserts
    the bound by actually holding the lock while calling it.
    """
    import threading
    import time

    from argus.mcp import MCPClient

    client = MCPClient.__new__(MCPClient)
    client._lock = threading.Lock()
    client._proc = None

    held = threading.Event()
    release = threading.Event()

    def hog():
        with client._lock:
            held.set()
            release.wait(30)

    t = threading.Thread(target=hog, daemon=True)
    t.start()
    assert held.wait(5), "the holder thread never took the lock"

    started = time.monotonic()
    client.close()                      # must not wait for the holder
    elapsed = time.monotonic() - started
    release.set()
    t.join(timeout=5)

    assert elapsed < 10, (
        f"close() waited {elapsed:.1f}s for a lock an in-flight call was "
        "holding - the shutdown is only bounded if this returns")


def test_closing_a_server_kills_what_it_spawned_not_just_what_it_started():
    """The `run_capped` orphan, one plane over.

    `MCPClient.close` sent `terminate()` to the direct child and waited for
    it. Anything that child spawned was reparented to init and kept
    running - and an MCP server makes its own network requests outside
    GuardedClient by design, which this module's docstring states as the
    reason `mcp_call` scope-checks URL arguments at all. So an orphaned one
    is a client with no scope guard, no rate limiter and no request budget,
    whose traffic reaches no transcript, while the engagement's record says
    the server was shut down.

    Two things were wrong and the second is the subtle one. The server was
    not started with `start_new_session=True`, so there was no group to
    signal; and `close()` reaped the leader with `wait()` BEFORE asking for
    its group, so even with a group `os.getpgid` would raise and signal
    nobody. A graceful, successful shutdown left the whole tree running.

    Measured before the fix with a stub that spawns a sleeper: the
    grandchild survived `close()` and reported `PPid: 1`.
    """
    import os
    import subprocess
    import sys
    import tempfile
    import time
    from pathlib import Path

    import pytest

    from argus.mcp import MCPClient

    if os.name != "posix":
        pytest.skip("process groups are POSIX; CI covers nt through the "
                    "taskkill branch, which needs a real Windows runner")

    marker = Path(tempfile.mkdtemp()) / "orphan-was-alive"
    server = Path(__file__).parent / "orphan_mcp_server.py"
    c = MCPClient("orphan", [sys.executable, str(server)],
                  env={"ORPHAN_MARKER": str(marker)})
    assert c.tools() == [], "the stub server did not complete a handshake"
    c.close()

    time.sleep(3.0)
    assert not marker.exists(), (
        "a process the MCP server spawned outlived close(): it still has "
        "the target and no place in the transcript, while the run's record "
        "says the server was shut down")
