"""Deterministic re-verification, against a real loopback target.

Driven through the REAL `GuardedClient` against a real socket, not a stub.
Three times in one session a stub or a plant was the defect rather than the
code it was measuring, and the thing being tested here is precisely what
happens on the wire: which headers are replayed, which are dropped, and
whether the bytes come back.
"""
from __future__ import annotations

import json
import pathlib
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from argus import replay as replay_mod
from argus.httpclient import GuardedClient, RateLimiter
from argus.replay import (Replay, apply_replay, credentials_needed,
                          replay_finding, replay_headers, reverified,
                          witness_for)
from argus.scope import ScopeGuard
from argus.session import Session

PROOF = "uid=0(root) gid=0(root)"
NONCE = "NONCE-a1b2c3"


class _Target(BaseHTTPRequestHandler):
    """Answers the proof only when the state the class variables describe
    says it should, so a test can make a target patched, authenticated or
    flaky without touching the replay code."""

    serves_proof = True
    require_cookie = ""
    seen: list[dict] = []

    def _answer(self):
        type(self).seen.append({"path": self.path,
                                "headers": dict(self.headers)})
        if self.require_cookie and \
                self.headers.get("Cookie") != self.require_cookie:
            body = b"<p>please log in</p>"
            code = 403
        elif type(self).serves_proof:
            body = f"<pre>{PROOF}\n{NONCE}</pre>".encode()
            code = 200
        else:
            body = b"<p>nothing here</p>"
            code = 200
        self.send_response(code)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    do_GET = do_POST = _answer

    def log_message(self, *a):
        pass


@pytest.fixture
def target():
    _Target.serves_proof = True
    _Target.require_cookie = ""
    _Target.seen = []
    srv = ThreadingHTTPServer(("127.0.0.1", 0), _Target)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}/"
    srv.shutdown()
    srv.server_close()


def _client(base: str, headers: dict | None = None):
    sdir = pathlib.Path(tempfile.mkdtemp())
    session = Session(sdir, base, {"target": base})
    return GuardedClient(ScopeGuard(base), session, RateLimiter(50.0),
                         default_headers=headers), session


def _recorded(base: str, *, cookie: str = "", cred: dict | None = None):
    """A transcript entry shaped the way the recorder writes one, including
    `credential_sha256_16` holding a HASH rather than a value."""
    headers = {"User-Agent": "Argus/1.0", "Accept": "*/*",
               "Host": "127.0.0.1", "Content-Length": "0"}
    if cookie:
        headers["Cookie"] = cookie
    req = {"method": "GET", "url": base + "a?q=1", "headers": headers,
           "body": None}
    if cred:
        req["credential_sha256_16"] = cred
    return {"id": "r1", "tool": "probe_rce", "ts": 1.0, "request": req,
            "response": {"status": 200, "headers": {}, "truncated": False,
                         "final_url": req["url"], "elapsed_ms": 9,
                         "body": f"<pre>{PROOF}\n{NONCE}</pre>"}}


def _finding(**over):
    base = {"id": "F01", "vuln_class": "rce", "grade": "proven",
            "severity": "critical", "evidence_ids": ["r1"],
            "evidence_excerpt": PROOF}
    base.update(over)
    return base


# ------------------------------------------------- 1. the three outcomes

def test_a_target_that_still_does_it_reproduces(target):
    client, session = _client(target)
    out = replay_finding(client, _finding(), [_recorded(target)])
    assert out.outcome == "reproduced", out.reason
    assert out.status == 200
    assert out.source_id == "r1"
    # the replay's OWN exchange is recorded and citable, so the
    # verification is auditable rather than asserted
    assert out.evidence_id
    lines = (session.dir / "transcript.jsonl").read_text().splitlines()
    ids = [json.loads(l).get("id") for l in lines]
    assert out.evidence_id in ids
    assert any(json.loads(l).get("tool") == "replay" for l in lines)


def test_a_patched_target_does_not_reproduce_and_says_it_is_not_a_retraction(
        target):
    _Target.serves_proof = False
    client, _ = _client(target)
    out = replay_finding(client, _finding(), [_recorded(target)])
    assert out.outcome == "not_reproduced"
    assert out.status == 200, "the request was answered; only the bytes differ"
    # the wording matters: this is the outcome most likely to be read as a
    # refutation, and a patched target is the commonest cause
    assert "not a retraction" in out.reason
    assert "patched" in out.reason


def test_an_unreachable_target_is_inconclusive_not_a_refutation(target):
    """A target that cannot be reached has not refuted anything. Driven by
    shutting the real server down, so the failure is a real connection
    refusal and not a mocked exception."""
    import socket
    client, _ = _client(target)
    entry = _recorded(target)
    # a port nothing listens on, inside the same scoped host
    probe = socket.socket()
    probe.bind(("127.0.0.1", 0))
    dead = probe.getsockname()[1]
    probe.close()
    host = target.rstrip("/").rsplit(":", 1)[0]
    entry["request"]["url"] = f"{host}:{dead}/a?q=1"
    out = replay_finding(client, _finding(), [entry])
    assert out.outcome == "inconclusive", out.reason
    # MEASURED, AND THIS IS WHY THE TEST DRIVES A REAL SOCKET: the client
    # does NOT raise on a connection failure, it returns
    # {"error": "ConnectError: ...", "status": 0}. Before that branch
    # existed this came back `not_reproduced`, so a target that was merely
    # DOWN retracted every finding in the session.
    assert "ConnectError" in out.reason, out.reason
    assert "never asked" in out.reason
    assert out.status == 0
    assert out.source_id == "r1"
    # and the error MESSAGE is not repeated - it can carry a URL, and a URL
    # can carry a credential
    assert "Errno" not in out.reason and "refused" not in out.reason


def test_the_client_still_exposes_the_headers_this_reads():
    """`supplied_headers` reads a PRIVATE attribute of the client, which is
    the only thing that knows what goes on the wire. The first version read
    a public name that does not exist, so every supplied credential was
    reported missing and an authenticated finding could never reproduce.
    A rename must fail here rather than silently restore that."""
    client, _ = _client("http://127.0.0.1:1/", {"Cookie": "a=b"})
    assert replay_mod.supplied_headers(client) == {"Cookie": "a=b"}
    assert replay_mod.supplied_headers(object()) == {}


# ------------------- 2. redaction must not manufacture false refutations

def test_a_credential_in_the_record_is_inconclusive_without_one_supplied(
        target):
    """MEASURED ON THIS REPOSITORY'S OWN SEALED SESSIONS: bwapp and dvwa
    carry a credential on 100% of requests, the self-written lab on 2-3%.
    So on the targets that look like real work, replaying without the
    operator re-supplying the credential can say nothing - and reporting a
    target that refused an unauthenticated request as a finding that did
    not hold would make redaction a generator of false retractions."""
    _Target.require_cookie = "PHPSESSID=real-value"
    client, _ = _client(target)                     # no header supplied
    entry = _recorded(target, cookie="PHPSESSID=real-value",
                      cred={"cookie": "46ba47849c7917a8"})
    out = replay_finding(client, _finding(), [entry])
    assert out.outcome == "inconclusive"
    assert "cookie" in out.reason
    assert "hash, not the value" in out.reason
    assert "--header" in out.reason
    assert _Target.seen == [], "nothing should have been sent at all"


def test_the_same_finding_reproduces_once_the_credential_is_supplied(target):
    _Target.require_cookie = "PHPSESSID=real-value"
    client, _ = _client(target, {"Cookie": "PHPSESSID=real-value"})
    entry = _recorded(target, cookie="PHPSESSID=real-value",
                      cred={"cookie": "46ba47849c7917a8"})
    out = replay_finding(client, _finding(), [entry])
    assert out.outcome == "reproduced", out.reason
    # and the HASH was never put on the wire where the value belongs
    sent = [h.get("Cookie") for h in (e["headers"] for e in _Target.seen)]
    assert "46ba47849c7917a8" not in str(sent)
    assert "PHPSESSID=real-value" in str(sent)


def test_credentials_needed_counts_only_what_is_missing():
    entry = _recorded("http://t/", cred={"cookie": "aa", "authorization": "bb"})
    assert credentials_needed(entry, None) == ["authorization", "cookie"]
    assert credentials_needed(entry, {"Cookie": "x"}) == ["authorization"]
    assert credentials_needed(entry, {"cookie": "x", "AUTHORIZATION": "y"}) == []
    assert credentials_needed({"request": {}}, None) == []


# ---------------------------------- 3. which headers reach the wire again

def test_hop_by_hop_and_credential_headers_are_not_replayed():
    entry = _recorded("http://t/", cookie="PHPSESSID=v",
                      cred={"cookie": "hash16"})
    out = replay_headers(entry)
    assert "Cookie" not in out, \
        "the recorded value is a hash; sending it is a different request"
    for gone in ("Host", "Content-Length"):
        assert gone not in out, f"{gone} is computed by the wire"
    assert out.get("User-Agent") == "Argus/1.0"
    assert out.get("Accept") == "*/*"


def test_the_witness_is_the_entry_whose_response_carries_the_quote():
    """Not `evidence_ids[0]`. A finding cites the pair and only the response
    half can be re-verified, so the entry to repeat is the one the proof
    matrix's own universal check would name."""
    a = _recorded("http://t/")
    a["id"] = "r1"
    a["response"]["body"] = "<p>nothing</p>"
    b = _recorded("http://t/")
    b["id"] = "r2"
    found = witness_for(_finding(evidence_ids=["r1", "r2"]), [a, b])
    assert found is not None and found["id"] == "r2"
    assert witness_for(_finding(evidence_excerpt=""), [a, b]) is None
    assert witness_for(_finding(), [a]) is None


# ------------------------------------------- 4. the three one-way doors

def test_a_replay_never_raises_a_finding_and_never_touches_the_grade():
    finding = _finding(grade="proven", severity="critical")
    out = apply_replay(finding, Replay("F01", "not_reproduced", "gone"))
    assert out["grade"] == "proven", "the grade belongs to the proof matrix"
    assert out["severity"] == "critical"
    assert out["replay_failed"] is True

    # a later success does NOT clear the earlier failure
    out2 = apply_replay(out, Replay("F01", "reproduced", "back"))
    assert out2["replay_failed"] is True, \
        "a target answering differently twice is information, not a fix"
    assert [r["outcome"] for r in out2["replays"]] == \
        ["not_reproduced", "reproduced"]


def test_an_inconclusive_replay_is_not_a_re_verification():
    """The same hole as counting a judge's transport failure as a review:
    the question never reached the target."""
    base = _finding()
    assert reverified(base) is False
    assert reverified(apply_replay(
        base, Replay("F01", "inconclusive", "no credential"))) is False
    assert reverified(apply_replay(
        base, Replay("F01", "not_reproduced", "gone"))) is True
    assert reverified(apply_replay(
        base, Replay("F01", "reproduced", "back"))) is True


def test_an_outcome_outside_the_three_is_refused():
    with pytest.raises(ValueError):
        Replay("F01", "probably_fine", "")
    assert replay_mod.OUTCOMES == ("reproduced", "not_reproduced",
                                   "inconclusive")


def test_a_finding_quoting_nothing_is_inconclusive(target):
    client, _ = _client(target)
    out = replay_finding(client, _finding(evidence_excerpt=""),
                         [_recorded(target)])
    assert out.outcome == "inconclusive"
    assert "quotes no bytes" in out.reason
    assert _Target.seen == []


# ------------------------------------------- 5. the command, end to end

def _sealed_copy(tmp_path):
    """A real sealed session, copied. `docs/sample-session` is the one the
    wheel job re-verifies, so it is sealed the way a run leaves one."""
    import shutil
    root = pathlib.Path(__file__).resolve().parents[1]
    src = root / "docs" / "sample-session"
    if not src.exists():
        pytest.skip("no checked-in sample session")
    dst = tmp_path / "s"
    shutil.copytree(src, dst)
    return dst


def test_the_command_leaves_the_chain_verifying(tmp_path, capsys):
    """THE DEFECT THIS GUARDS, measured end to end: `record_event` appends a
    transcript entry, the tail moves past the chain head in summary.json,
    and `argus verify` answers MISMATCH - so a command whose whole purpose
    is verification invalidated the record of every session it touched. The
    re-render and re-seal are what `argus judge` already did.
    """
    from argus import cli
    from argus.session import chain_ok, verify_transcript

    sdir = _sealed_copy(tmp_path)
    assert chain_ok(verify_transcript(sdir, "")), "premise: starts verifying"

    rc = cli.main(["replay", str(sdir)])
    capsys.readouterr()
    assert rc == 0

    res = verify_transcript(sdir, "")
    assert chain_ok(res), (
        f"replay broke the chain it verifies: "
        f"{ {k: res.get(k) for k in ('chained', 'error', 'anchor_missing')} }")


def test_the_command_refuses_a_record_that_does_not_verify(tmp_path, capsys):
    """Amending findings over a transcript already in doubt presents the
    outcome as covering something it does not."""
    from argus import cli

    sdir = _sealed_copy(tmp_path)
    tpath = sdir / "transcript.jsonl"
    lines = tpath.read_text(encoding="utf-8").splitlines()
    tpath.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")

    rc = cli.main(["replay", str(sdir)])
    out = capsys.readouterr().out
    assert rc == 1
    assert "does not verify" in out
    assert "argus verify" in out


def test_the_outcomes_reach_findings_json_and_the_grade_does_not_move(
        tmp_path, capsys):
    from argus import cli

    sdir = _sealed_copy(tmp_path)
    before = json.loads((sdir / "findings.json").read_text(encoding="utf-8"))
    grades = {f["id"]: f.get("grade") for f in before}

    assert cli.main(["replay", str(sdir)]) == 0
    capsys.readouterr()

    after = json.loads((sdir / "findings.json").read_text(encoding="utf-8"))
    for finding in after:
        assert finding.get("grade") == grades[finding["id"]], \
            "the grade belongs to the proof matrix"
        assert isinstance(finding.get("replay"), dict), finding["id"]
        assert finding["replay"]["outcome"] in replay_mod.OUTCOMES


def test_a_header_reaches_the_replayed_request(tmp_path, target, capsys):
    """The documented escape from an inconclusive authenticated finding.
    Driven against the loopback target, which refuses without the cookie,
    so a header that does not arrive shows up as a failure to reproduce."""
    from argus import cli

    _Target.require_cookie = "SESS=v"
    sdir = tmp_path / "e"
    session = Session(sdir, target, {"target": target})
    client = GuardedClient(ScopeGuard(target), session, RateLimiter(50.0),
                           default_headers={"Cookie": "SESS=v"})
    result = client.send("GET", target + "a?q=1", tool="probe_rce")
    assert PROOF in str(result.get("body")), "premise: the target proved it"
    client.close()

    entries = [json.loads(l) for l in
               (session.dir / "transcript.jsonl").read_text().splitlines()]
    cited = [e for e in entries if isinstance(e, dict) and e.get("request")]
    assert cited, "premise: the exchange was recorded"
    finding = _finding(evidence_ids=[str(cited[0].get("id"))])

    # without the header: inconclusive, and nothing is sent
    bare, _ = _client(target)
    _Target.seen = []
    assert replay_finding(bare, finding, cited).outcome == "inconclusive"
    assert _Target.seen == []

    # with it: reproduced
    authed, _ = _client(target, {"Cookie": "SESS=v"})
    out = replay_finding(authed, finding, cited)
    assert out.outcome == "reproduced", out.reason
