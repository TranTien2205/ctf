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


def test_bound_value_handles_unserializable():
    class Weird:
        def __str__(self):
            return "weird"
    v = _bound_value(Weird())
    assert v == "weird" or isinstance(v, str)
    # a normal small dict passes through untouched
    assert _bound_value({"a": 1}) == {"a": 1}
