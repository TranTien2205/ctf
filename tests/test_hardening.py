"""Regression tests for boundary-validation hardening added during the
robustness sweep: malformed inputs must fail fast (no budget burn, no
wire write) and persisted event payloads must stay bounded."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from argus.ratelimit import RateLimiter
from argus.scope import ScopeGuard
from argus.session import Session, _bound_value
from argus.httpclient import GuardedClient


@pytest.fixture()
def client(tmp_path, lab_url):
    scope = ScopeGuard(lab_url, allow_private=True)
    session = Session(tmp_path, lab_url, meta={"t": 1})
    c = GuardedClient(scope, session, RateLimiter(0), max_requests=50)
    yield c
    c.close()


def test_send_rejects_non_str_body(client, lab_url):
    for bad in ({"a": 1}, [1, 2], 5):
        with pytest.raises(TypeError, match="body must be"):
            client.send("POST", lab_url, body=bad)
    assert client.sent == 0  # no budget burned on malformed input


def test_send_rejects_list_headers(client, lab_url):
    with pytest.raises(TypeError, match="headers must be"):
        client.send("GET", lab_url, headers=["X: 1"])
    assert client.sent == 0


def test_send_rejects_control_char_method(client, lab_url):
    for bad in ("GET\r\nX-Inj: 1", "GET\nX: 1", "G\x00T", "", "  "):
        with pytest.raises(ValueError, match="invalid HTTP method"):
            client.send(bad, lab_url)
    assert client.sent == 0


def test_send_rejects_non_str_method(client, lab_url):
    with pytest.raises(ValueError, match="invalid HTTP method"):
        client.send(123, lab_url)
    assert client.sent == 0


def test_record_event_bounds_detail_values(tmp_path):
    s = Session(tmp_path, "http://t", meta={"t": 1})
    big = {"data": "x" * 300_000}
    rid = s.record_event("mcp_call", {"arguments": big})
    line = Path(s.transcript_path).read_text().splitlines()[-1]
    assert len(line) < 70_000
    assert "truncated" in line


def test_record_event_preserves_small_values(tmp_path):
    s = Session(tmp_path, "http://t", meta={"t": 1})
    rid = s.record_event("external_cmd", {
        "cmd": ["nmap", "-sV"], "n": 5, "ok": True})
    e = s._transcript[rid]
    assert e["cmd"] == ["nmap", "-sV"]
    assert e["n"] == 5 and e["ok"] is True


def test_dns_rebinding_blocked_at_connect(tmp_path, lab_url, monkeypatch):
    # the scope check resolved 'localhost' as public (rebound answer);
    # the real connection still lands on 127.0.0.1 and must be refused
    import argus.scope as scope_mod
    from argus.scope import ScopeError
    monkeypatch.setattr(scope_mod, "_is_private_host", lambda h: False)
    host = lab_url.split("://")[1].split(":")[0]
    scope = ScopeGuard(lab_url, allow_private=False)
    session = Session(tmp_path, lab_url, meta={"t": 1})
    c = GuardedClient(scope, session, RateLimiter(0))
    try:
        with pytest.raises(ScopeError, match="rebinding"):
            c.send("GET", lab_url)
    finally:
        c.close()


def test_crawl_survives_hostile_hrefs(ctx, lab_url):
    from argus.tools import web
    out = web.crawl(ctx, lab_url + "/weird-links", depth=1)
    # malformed links are skipped; the good /item?id=2 one is followed
    assert "error" not in out
    assert any("/item" in p["url"] for p in out["pages"])


def test_js_recon_survives_hostile_srcs(ctx, lab_url):
    from argus.tools import web
    out = web.js_recon(ctx, lab_url + "/weird-links")
    assert "error" not in out  # '//[bad/x.js' src skipped, good src fetched


def test_bound_value_handles_unserializable():
    class Weird:
        def __str__(self):
            return "weird"
    v = _bound_value(Weird())
    assert v == "weird" or isinstance(v, str)
    # a normal small dict passes through untouched
    assert _bound_value({"a": 1}) == {"a": 1}


def test_ival_falls_back_on_wrong_types():
    from argus.tools.registry import _ival
    assert _ival("x", 8, 1, 30) == 8      # str garbage -> default
    assert _ival([1], 5, 1, 10) == 5      # list -> default
    assert _ival(None, 7, 1, 10) == 7     # missing -> default
    assert _ival("", 3, 1, 10) == 3       # empty str -> default
    assert _ival(3.9, 5, 1, 10) == 3      # float truncates
    assert _ival(50, 5, 1, 10) == 10      # over-hi clamps
    assert _ival(-2, 5, 1, 10) == 1       # under-lo clamps
    assert _ival(6, 5, 1, 10) == 6        # good value passes


def test_tool_params_coerce_wrong_json_types(ctx):
    """JSON-legal wrong types on model params must degrade to an error
    dict or a safe default - not a stack trace the model can't parse."""
    from argus.tools import analysis, team
    from argus.session import Session

    # jwt_decode on an int token -> error dict, not AttributeError
    assert "error" in analysis.jwt_decode(ctx, 123)
    # load_skill int name -> falls back to the index, never crashes
    assert isinstance(analysis.load_skill(ctx, 123), dict)
    # _split_args int -> str'd, not a TypeError
    assert analysis._split_args(123) == ["123"]
    # add_finding int severity -> gate ValueError, not AttributeError
    with pytest.raises(ValueError, match="severity"):
        ctx.session.add_finding(
            title="t", severity=5, category="c", url="http://x",
            evidence_ids=[], evidence_excerpt="e", description="",
            remediation="")


def test_mcp_config_malformed_shapes(tmp_path):
    from argus.mcp import MCPManager
    # a valid-JSON wrong-shape config must not crash startup
    for payload, want in (
        ([1, 2], "root"),
        ("x", "root"),
        ({"servers": "x"}, "servers"),
        ({"servers": {"a": "y"}}, "not an object"),
        ({"servers": {"a": {"command": 'unbal "q'}}}, "command"),
        ({"servers": {"a": {"command": 5}}}, "command"),
    ):
        p = tmp_path / "mcp.json"
        p.write_text(json.dumps(payload))
        m = MCPManager(p)
        errs = m.errors()
        assert errs, f"{payload!r} should produce an error"
        assert want in str(errs), errs


def test_dispatch_total_on_malformed_args(ctx):
    """Every registered tool x wrong-JSON-type args must return a
    JSON-serializable dict - dispatch is the run's only boundary between
    model output and a crash, so it must be total, not just usually
    safe."""
    from argus.tools.registry import TOOL_SCHEMAS, dispatch

    pool = [None, True, 0, -1, 1.5, "x", "", "http://[bad", [1, 2],
            {"a": 1}, 1e9]
    for schema in TOOL_SCHEMAS:
        name = schema["name"]
        keys = list((schema.get("input_schema") or {})
                    .get("properties") or {}) or ["x"]
        for bad_value in pool[:5]:
            args = {k: bad_value for k in keys[:3]}
            out = dispatch(ctx, name, args)
            assert isinstance(out, dict), (name, args, out)
            json.dumps(out)  # must be serializable for tool_result
            assert "result" in out or "error" in out, (name, out)


def test_readers_survive_mutated_session_dir(tmp_path):
    """argus verify/report/findings on a tampered session dir must degrade
    to warnings/errors - these readers exist to audit artifacts an
    attacker or accident may have corrupted, so crashing is the worst
    possible answer."""
    from argus.cli import main as cli_main

    sdir = tmp_path / "sess"
    sdir.mkdir()
    (sdir / "transcript.jsonl").write_text(
        json.dumps({"id": "r1", "chain": "x",
                    "response": "x"}) + "\n[1,2]\n")
    (sdir / "meta.json").write_text("[1]")
    (sdir / "summary.json").write_text('"x"')
    (sdir / "findings.json").write_text(
        '[1,"x",{"id":"F","severity":"high","evidence_excerpt":"b",'
        '"evidence_ids":[[1]]}]')
    for cmd in ("verify", "report", "findings"):
        argv = [cmd, str(sdir)]
        if cmd == "findings":
            argv += ["--json"]
        rc = cli_main(argv)
        assert isinstance(rc, int)  # returned a status, never raised
