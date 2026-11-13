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


def test_api_base_url_shared_by_run_and_check(monkeypatch):
    """`argus check` must probe the same endpoint a real run targets.
    Regressed once: check used the hardcoded API_URL while run honored
    ANTHROPIC_BASE_URL, so a gateway operator got a green check for a
    path run would never use."""
    from argus import config
    from argus.config import api_base_url

    monkeypatch.delenv("ANTHROPIC_BASE_URL", raising=False)
    assert api_base_url() == config.API_URL

    monkeypatch.setenv("ANTHROPIC_BASE_URL", "http://gw.local/api/")
    assert api_base_url() == "http://gw.local/api/messages"

    # load_config resolves api_base through the same helper - no drift
    # between the check ping and a real engagement's endpoint
    args = type("A", (), {"api_key": None, "target": "http://t.example",
                          "header": None, "header_file": None,
                          "exclude": "", "rate": 1.0, "max_time": 60,
                          "max_requests": 5, "max_turns": 5,
                          "proxy": "", "no_external": True,
                          "mcp_config": "", "model": None, "secret": None,
                          "session_dir": "", "resume": "", "tools": "",
                          "tls_verify": True, "goal": "", "operator": "",
                          "allow_private": False, "llm_max_tokens": 4096})()
    cfg = config.load_config(args)
    assert cfg.api_base == "http://gw.local/api/messages"


def test_nonfinite_budgets_rejected(monkeypatch):
    """`--rate nan` used to slip past the `x < 0` check (nan comparisons
    are all False) and silently become 'unlimited'. Non-finite and
    negative rate/time budgets must fail loudly, in both load_config and
    the RateLimiter itself."""
    import argparse
    import math
    import pytest
    from argus.config import load_config
    from argus.ratelimit import RateLimiter

    def args_for(**over):
        base = dict(api_key="k", auth_token=None, header_file=None,
                    header=[], scope=[], exclude=[],
                    target="http://127.0.0.1:1", model=None, max_turns=1,
                    max_requests=1, max_time=1, rate=1.0, goal="",
                    operator="", proxy="", llm_max_tokens=1,
                    mcp_config=None, resume=None, allow_private=True,
                    tls_verify=False, no_external=False, quiet=True,
                    session_dir="", tools="", secret=None)
        base.update(over)
        return argparse.Namespace(**base)

    for bad in (math.nan, math.inf, -math.inf, -1.0):
        with pytest.raises(SystemExit):
            load_config(args_for(rate=bad))
        with pytest.raises((ValueError, SystemExit)):
            RateLimiter(bad)
    for bad_t in (math.nan, math.inf, -1.0):
        with pytest.raises(SystemExit):
            load_config(args_for(max_time=bad_t))
    cfg = load_config(args_for(rate=2.5, max_time=30))
    assert cfg.rate_rps == 2.5 and cfg.max_time_s == 30


def test_atomic_write_cleans_temp_on_failure(tmp_path):
    """A failed _atomic_write (e.g. target swapped for a directory) must
    not litter .tmp-* files next to the deliverable (bed2276)."""
    import pytest
    from argus.session import _atomic_write
    target = tmp_path / "findings.json"
    target.mkdir()  # replace() onto a dir must fail
    with pytest.raises(OSError):
        _atomic_write(target, "[]")
    assert not list(tmp_path.glob("*.tmp-*")), "temp file left behind"

def test_no_test_hard_codes_an_absolute_path_to_this_checkout():
    """A test that names an absolute path passes on one machine only.

    `tests/test_windows.py` hard-coded the author's own checkout, so it was
    green locally and red on all six CI runners with a FileNotFoundError
    naming that path - and it could not be reproduced in a clean clone on the
    same machine, because the path still existed there.
    """
    import pathlib
    import re
    root = pathlib.Path(__file__).resolve().parent.parent
    bad = re.compile(r"""['"](/(?:home|Users|root|mnt|media)/[^'"\n]+)['"]""")
    # this package's own files - not the vendored CTF challenges that share
    # the checkout, and not a site-packages tree somebody's venv put here
    targets = [root / "selftest.py"]
    for folder in ("argus", "tests", "lab", "test"):
        targets += sorted((root / folder).glob("**/*.py"))
    offenders = []
    for path in targets:
        if not path.exists() or any(
                part in (".git", "__pycache__", "build", "dist", ".venv",
                         "site-packages")
                for part in path.parts):
            continue
        for n, line in enumerate(
                path.read_text(encoding="utf-8", errors="replace").splitlines(),
                1):
            if line.lstrip().startswith("#"):
                continue
            hit = bad.search(line)
            if hit:
                offenders.append(
                    f"{path.relative_to(root)}:{n}: {hit.group(1)}")
    assert not offenders, (
        "absolute paths into somebody's home directory:\n  "
        + "\n  ".join(offenders))


def test_raw_wire_redaction_is_not_defeated_by_the_header_name():
    """Two shapes walked an operator credential into the transcript.

    `_redact_request_text` keyed on `": "`, and the header names on this
    path are MODEL-supplied input:

      `Authorization:Bearer tok`   - the space after the colon is optional
          in HTTP, so `": " in line` was False and the line persisted
          verbatim.
      `Authorization:Bearer tok: ` - a name carrying the colon and the
          value, so `partition(": ")` took the token as part of the NAME,
          the name did not match the sensitive list, and the token
          persisted.

    Neither is reachable through send_raw's own composition, which always
    writes `f"{k}: {v}"`. Both are reachable through the header pairs a
    model hands it - which is what this path exists to send. And a
    credential the operator did not declare with `--secret` has no second
    line of defence, because Session's substring redaction only knows
    declared values.
    """
    from argus.httpclient import _REDACTED, _redact_request_text

    def line_of(header, secrets=frozenset()):
        raw = f"GET / HTTP/1.1\r\nHost: t\r\n{header}\r\n\r\n"
        return _redact_request_text(raw, set(secrets)).split("\r\n")[2]

    for header in ("Authorization:Bearer live-tok-9",
                   "Authorization:Bearer live-tok-9: ",
                   "Authorization: Bearer live-tok-9",
                   "Cookie:sid=secret9",
                   "  authorization : Bearer live-tok-9"):
        got = line_of(header)
        assert _REDACTED in got, (header, got)
        assert "live-tok-9" not in got and "secret9" not in got, (header, got)

    # ...and the lines that ARE the evidence must survive untouched: the
    # framing headers are the whole point of a desync probe, and a
    # redaction that ate them would destroy the finding it protects
    assert line_of("Transfer-Encoding: chunked") == "Transfer-Encoding: chunked"
    assert line_of("Content-Length: 6") == "Content-Length: 6"
    assert line_of("X-Request-Id: abc-123") == "X-Request-Id: abc-123"


def test_header_name_whitespace_does_not_defeat_redaction():
    """The sibling of the fix above, which that fix did not check.

    `_redact_headers` tested `ks.lower() in _SENSITIVE_REQ_HEADERS`, and
    these names are model-supplied: `"Authorization "` lowercases to
    `"authorization "`, which is not in the set, so a live Bearer token
    persisted into the transcript verbatim. The recorded dict is what gets
    persisted whether or not httpx normalises the wire.

    This is the same class as the `": "` split one function above - found
    only because the question was asked a second time, one function over,
    after the first fix shipped. That is the seventh half-fix in this
    stretch and the second in my own work.
    """
    from argus.httpclient import _REDACTED, _redact_headers

    for name in ("Authorization", " Authorization", "Authorization ",
                 "Authorization\t", "AUTHORIZATION", "\tCookie "):
        out = _redact_headers({name: "Bearer live-tok-9"}, set())
        rendered = str(out)
        assert "live-tok-9" not in rendered, (name, out)
        assert _REDACTED in rendered, (name, out)
        # the KEY keeps its original spelling: an audit must show exactly
        # what was sent, a malformed name included
        assert name in out, (name, out)

    # a benign header is untouched, or the redaction eats the evidence
    assert _redact_headers({"X-Request-Id": "abc-123"}, set()) == {
        "X-Request-Id": "abc-123"}
    assert _redact_headers({"Content-Length": "6"}, set()) == {
        "Content-Length": "6"}


def test_a_cookie_part_with_no_equals_is_redacted_whole():
    """Found by the case above being more adversarial than its own fix.

    The cookie branch kept any part without `=` as-is, on the reasoning
    that a bare part is a Set-Cookie attribute (`Secure`, `HttpOnly`) worth
    preserving. True for those, and false for the case that matters:
    `Cookie: live-session-token` carries no `=`, so nothing was dropped and
    the credential persisted verbatim.
    """
    from argus.httpclient import _REDACTED, _redact_header_value

    for value, secret in (("live-session-token", "live-session-token"),
                          ("sid=abc9; live-bare-token", "live-bare-token"),
                          ("sid=abc9", "abc9")):
        out = _redact_header_value("Cookie", value)
        assert secret not in out, (value, out)
        assert _REDACTED in out, (value, out)

    # the pair NAMES stay visible - the audit still shows the request was
    # authenticated and with which cookie
    assert _redact_header_value("Cookie", "sid=abc9").startswith("sid=")

    # ...and Set-Cookie attributes survive, because they are the evidence
    # for the cookie-hygiene class the lab plants
    attrs = _redact_header_value("Set-Cookie", "sid=abc9; HttpOnly; Secure")
    assert "HttpOnly" in attrs and "Secure" in attrs and "abc9" not in attrs


def test_no_operator_credential_reaches_any_artifact(lab_url, tmp_path):
    """End-to-end sweep: no operator credential in any artifact.

    What this actually covers, measured by reverting each fix and watching
    the test - because the first draft of this docstring claimed it would
    have caught all four redaction leaks and that is false:

    * the target's userinfo - **caught**: reverting it fails here with
      `{"meta.json": ["userinfo"]}`.
    * the unstripped header name, the `": "` split and the cookie part with
      no `=` - **not caught here**. A malformed header name never reaches
      the recorder: httpx drops `"Authorization "` before the request is
      built, so the recorded header dict is empty and the planted shape
      cannot arrive through this path. Those three are covered by the
      unit-level tests above, which hand the redactors the shapes directly.

    So this is the artifact-surface guard, not a replacement for those.
    Scope, stated so a later reader does not widen it wrongly: response
    bodies and WebSocket frame payloads are target data - evidence, not
    scrubbed unless declared with `--secret`. What must never persist is a
    credential the OPERATOR supplied.
    """
    import json as _json

    from argus.httpclient import GuardedClient
    from argus.ratelimit import RateLimiter
    from argus.scope import ScopeGuard
    from argus.session import Session

    planted = {
        "userinfo": "TARGETPW9",
        "bearer": "HDRTOKEN9",
        "cookie": "COOKIEVAL9",
    }
    host = lab_url.split("//", 1)[1]
    target = f"http://admin:{planted['userinfo']}@{host}/"
    session = Session(tmp_path, target, meta={"operator": "audit"})
    scope = ScopeGuard(target, allow_private=True)
    client = GuardedClient(
        scope, session, RateLimiter(0), tls_verify=False, max_requests=40,
        # the shapes that defeated redaction before: a name with trailing
        # whitespace, and a cookie value carrying no `=`
        default_headers={"Authorization ": f"Bearer {planted['bearer']}",
                         "Cookie": planted["cookie"]})
    try:
        client.send("GET", lab_url + "/", tool="http_request", note="audit")
        client.send_raw(lab_url + "/", [{"method": "GET", "headers": []}])
    finally:
        client.close()

    leaked = {}
    for path in sorted(session.dir.iterdir()):
        if not path.is_file():
            continue
        text = path.read_text(errors="replace")
        hits = sorted(k for k, v in planted.items() if v in text)
        if hits:
            leaked[path.name] = hits
    assert not leaked, _json.dumps(leaked, indent=2)
