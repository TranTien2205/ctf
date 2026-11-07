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
    assert discover_config_path("/nonexistent/x.json") is None
    cfg = tmp_path / "mcp.json"
    cfg.write_text("{}")
    assert discover_config_path(str(cfg)) == cfg
    monkeypatch.setenv("ARGUS_MCP_CONFIG", str(cfg))
    assert discover_config_path("") == cfg
