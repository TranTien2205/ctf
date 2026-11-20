"""The operator console: the HTTP contract, and the refusals.

Every test drives a real server on an ephemeral port with urllib, because
the things worth asserting here - a path that cannot leave the session root,
a body that is refused before it is read, a run that is never reported as
having run - are properties of the wire, not of a function.

Both directions, everywhere: for each route that admits a request there is a
case for the request it must refuse.
"""
from __future__ import annotations

import http.client
import json
import os
import socket
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from argus import __version__
from argus.session import Session
from argus.tools.analysis import _ALLOWED_TOOLS
from argus.web import api
from argus.web.server import (ALLOW_REMOTE_ENV, _check_bind_host, _Handler,
                              make_server, serve)

LAB_TARGET = "http://127.0.0.1:9"      # loopback, never contacted by these tests
CRED_TARGET = "http://admin:SuperSecret123@127.0.0.1:9/app"
FULL_AUTH = {"authorised_by": "the client's CISO", "scope": "one host",
             "window": "2026-11-18 09:00 to 17:00 UTC", "reference": "TKT-1"}


# ---------------------------------------------------------------------------
# harness


class _Web:
    def __init__(self, srv, root):
        self.srv = srv
        self.root = Path(root)
        self.registry = srv.registry
        self.base = f"http://127.0.0.1:{srv.server_address[1]}"


def _spawn(root, **kwargs):
    kwargs.setdefault("model_configured", False)
    srv = make_server("127.0.0.1", 0, root=root, quiet=True, **kwargs)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return _Web(srv, root)


@pytest.fixture()
def web(tmp_path):
    root = tmp_path / "engagements"
    root.mkdir()
    w = _spawn(root)
    yield w
    w.srv.shutdown()
    w.srv.server_close()


def _req(url, method="GET", payload=None, raw=None, headers=None):
    """(status, body bytes, headers). HTTP errors are results, not raises."""
    data = raw
    hdrs = dict(headers or {})
    if payload is not None:
        data = json.dumps(payload).encode()
        hdrs.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, data=data, method=method, headers=hdrs)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status, resp.read(), dict(resp.headers)
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(), dict(exc.headers)


def _json_req(url, method="GET", payload=None, **kw):
    status, body, headers = _req(url, method, payload, **kw)
    return status, json.loads(body.decode()), headers


def _wait_state(web, run_id, wanted, timeout=10.0):
    deadline = time.time() + timeout
    seen = None
    while time.time() < deadline:
        status, data, _ = _json_req(f"{web.base}/api/runs/{run_id}")
        assert status == 200, data
        seen = data["run"]["state"]
        if seen in wanted:
            return data
        time.sleep(0.05)
    raise AssertionError(f"run {run_id} stayed in {seen!r}, wanted {wanted}")


def _plant_session(root, target=LAB_TARGET, *, transcript=True,
                   findings=None, report=True, sidecar=None):
    """A session directory as the CLI leaves one: built with the real
    Session so meta.json, the id format and the redaction are not reinvented
    here."""
    session = Session(Path(root), target, meta={"planted": True})
    if transcript:
        session.record_event("external_result", {"tool": "nmap", "rc": 0})
    if findings is not None:
        (session.dir / "findings.json").write_text(
            json.dumps(findings), encoding="utf-8")
    if report:
        # `newline=""` or Windows translates the "\n" to "\r\n" and every
        # byte-level assertion about this file is off by one per line.
        # MEASURED: this fixture failed `test_reports_listing_names_the_
        # formats_present` with b"# report\r\n" != b"# report\n" and
        # `test_head_is_routed_and_sends_no_body` with Content-Length 10
        # against 9 - two failures, one line, on every Windows job of the
        # project's own CI while the Linux gate here stayed green.
        (session.dir / "report.md").write_text("# report\n", encoding="utf-8",
                                               newline="")
    if sidecar is not None:
        (session.dir / api.WEB_STATE_FILE).write_text(
            json.dumps(sidecar), encoding="utf-8")
    return session.dir


# ---------------------------------------------------------------------------
# health


def test_health_shape(web):
    status, data, headers = _json_req(f"{web.base}/api/health")
    assert status == 200
    assert data["ok"] is True
    assert data["version"] == __version__
    assert data["model_configured"] is False
    assert set(data["tools"]) == set(api.HEALTH_TOOLS)
    assert all(isinstance(v, bool) for v in data["tools"].values())
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["Content-Type"].startswith("application/json")


def test_health_never_advertises_a_tool_the_broker_refuses(web):
    """The invariant between two lists naming one concept: the console's
    tool row and `run_external`'s allowlist. A tool shown here that the
    broker would refuse is a claim of capability the system does not have."""
    _, data, _ = _json_req(f"{web.base}/api/health")
    assert set(data["tools"]) <= _ALLOWED_TOOLS


def test_health_does_not_resolve_credentials():
    """`credential_source_present` must not reach `config.resolve_auth`.

    That function refreshes a stale Claude Code OAuth token over the network
    and rewrites ~/.claude/.credentials.json. An unauthenticated GET on this
    server must not be able to cause either, so the check is presence of a
    source, never validity of a token.
    """
    calls = []
    import argus.config as config
    original = config.resolve_auth
    config.resolve_auth = lambda *a, **k: (calls.append(1), ("", ""))[1]
    try:
        api.credential_source_present()
    finally:
        config.resolve_auth = original
    assert calls == []


# ---------------------------------------------------------------------------
# prompt preview - the gate


def test_prompt_lab_mode_previews(web):
    status, data, _ = _json_req(
        f"{web.base}/api/prompt", "POST",
        {"mode": "lab", "target": LAB_TARGET, "auth": None,
         "extra": "map the surface"})
    assert status == 200
    assert data["errors"] == []
    assert data["ok"] is True
    assert data["prompt"].strip()


def test_prompt_engagement_without_auth_is_refused(web):
    """The refusal that matters: the intrusive tier does not open without an
    authorisation note, and a refused preview hands back no prompt at all -
    a UI showing one beside the refusal would be handing it over to paste."""
    status, data, _ = _json_req(
        f"{web.base}/api/prompt", "POST",
        {"mode": "engagement", "target": "http://target.example",
         "auth": None, "extra": ""})
    assert status == 200
    assert data["ok"] is False
    assert data["prompt"] == ""
    missing = " ".join(data["errors"])
    # the field list comes from the prompt builder when it is installed, so
    # this asserts against the same list the prompt is built from
    for field in api.required_auth_fields():
        assert f"auth.{field}" in missing


def test_prompt_engagement_with_a_partial_note_is_still_refused(web):
    partial = dict(FULL_AUTH)
    partial["window"] = "   "
    _, data, _ = _json_req(
        f"{web.base}/api/prompt", "POST",
        {"mode": "engagement", "target": "http://target.example",
         "auth": partial, "extra": ""})
    assert data["ok"] is False
    assert any("auth.window" in e for e in data["errors"])
    assert not any("auth.scope" in e for e in data["errors"])


def test_prompt_engagement_with_a_full_note_passes(web):
    _, data, _ = _json_req(
        f"{web.base}/api/prompt", "POST",
        {"mode": "engagement", "target": "http://target.example",
         "auth": FULL_AUTH, "extra": "authorised retest"})
    assert data["errors"] == []
    assert data["ok"] is True


@pytest.mark.parametrize("target,needle", [
    ("ftp://host/x", "http(s)"),
    ("file:///etc/passwd", "http(s)"),
    ("http://", "http(s)"),
    ("", "required"),
    ("http://1.2.3.4/a b", "whitespace"),
    ("http://1.2.3.4/\nHost: evil", "whitespace"),
])
def test_prompt_refuses_bad_targets(web, target, needle):
    _, data, _ = _json_req(
        f"{web.base}/api/prompt", "POST",
        {"mode": "lab", "target": target, "auth": None, "extra": ""})
    assert data["ok"] is False, target
    assert any(needle in e for e in data["errors"]), data["errors"]


def test_prompt_refuses_an_unknown_mode(web):
    _, data, _ = _json_req(
        f"{web.base}/api/prompt", "POST",
        {"mode": "intrusive", "target": LAB_TARGET, "auth": None,
         "extra": ""})
    assert data["ok"] is False
    assert any("mode must be" in e for e in data["errors"])


def test_prompt_refuses_oversized_extra(web):
    _, data, _ = _json_req(
        f"{web.base}/api/prompt", "POST",
        {"mode": "lab", "target": LAB_TARGET, "auth": None,
         "extra": "x" * (api.max_extra_chars() + 1)})
    assert data["ok"] is False
    assert any("extra is longer" in e or "the limit is" in e
               for e in data["errors"])


def test_the_console_and_the_prompt_builder_share_one_contract():
    """One list per concept. The console's copy of the modes, the required
    authorisation fields and the free-text bound exist for a tree without
    `argus.prompts`; when the module is there, its definitions are the ones
    used, or a request the prompt builder accepts would be refused at the
    door (and `reference`, which it deliberately does not require, is
    exactly where that happened first)."""
    prompts = api._prompts_module()
    if prompts is None:
        pytest.skip("argus.prompts is not installed in this tree")
    assert api.modes() == tuple(prompts.MODES)
    assert api.required_auth_fields() == tuple(prompts.REQUIRED_AUTH_FIELDS)
    assert api.max_extra_chars() == prompts.MAX_EXTRA
    for raw in ("example.com", "localhost:8080", "https://x.test/a",
                "127.0.0.1", "mailto:a@b"):
        assert api.normalise_target(raw) == prompts._normalise_target(raw), raw


def test_prompt_rejects_wrong_field_types(web):
    _, data, _ = _json_req(
        f"{web.base}/api/prompt", "POST",
        {"mode": 7, "target": ["x"], "auth": "note", "extra": 3})
    assert data["ok"] is False
    joined = " ".join(data["errors"])
    for needle in ("mode must be a string", "target must be a string",
                   "auth must be an object", "extra must be a string"):
        assert needle in joined


def test_prompt_preview_failing_closed_on_a_broken_module(web, monkeypatch):
    """A prompt module that claims ok with an error list, or returns an
    unreadable result, must not open the gate."""
    assert api._normalise_preview({"ok": True, "prompt": "p",
                                   "errors": ["nope"]}) == (True, "p", ["nope"])
    result = api.preview_prompt("lab", LAB_TARGET)
    assert result["ok"] is True

    class _Fake:
        @staticmethod
        def preview(*a, **k):
            return {"ok": True, "prompt": "GO", "errors": ["unauthorised"]}

    monkeypatch.setitem(__import__("sys").modules, "argus.prompts", _Fake)
    monkeypatch.setattr("argus.prompts", _Fake, raising=False)
    refused = api.preview_prompt("lab", LAB_TARGET)
    assert refused["ok"] is False
    assert refused["prompt"] == ""
    assert "unauthorised" in refused["errors"]


# ---------------------------------------------------------------------------
# starting runs


def test_post_runs_with_an_invalid_body_starts_nothing(web):
    before = sorted(p.name for p in web.root.iterdir())
    status, data, _ = _json_req(
        f"{web.base}/api/runs", "POST",
        {"mode": "engagement", "target": "http://target.example",
         "auth": None, "extra": ""})
    assert status == 400
    assert data["ok"] is False
    assert data["run_id"] == ""
    assert data["errors"]
    # nothing created, nothing queued: the directory and the thread are both
    # behind the gate
    assert sorted(p.name for p in web.root.iterdir()) == before
    _, listing, _ = _json_req(f"{web.base}/api/runs")
    assert listing["runs"] == []


def test_post_runs_without_a_model_is_blocked_not_run(web):
    status, data, _ = _json_req(
        f"{web.base}/api/runs", "POST",
        {"mode": "lab", "target": LAB_TARGET, "auth": None,
         "extra": "find the sqli"})
    assert status == 200 and data["ok"] is True
    run_id = data["run_id"]
    detail = _wait_state(web, run_id, {"blocked"})
    assert "tool half" in detail["run"]["note"]
    rdir = web.root / run_id
    assert (rdir / "meta.json").exists()
    assert (rdir / api.PROMPT_FILE).read_text(encoding="utf-8").strip()
    assert (rdir / api.WEB_STATE_FILE).exists()
    # No transcript is written for a run that never probed: seeding the
    # evidence chain with "a form was submitted" is how an empty run comes
    # to verify like a real one.
    assert not (rdir / "transcript.jsonl").exists()
    assert detail["events"]
    assert any("blocked" in e["text"] for e in detail["events"])


def test_post_runs_rejects_an_out_of_scope_shape(web):
    """A target the scope guard refuses is a refusal, not a 500."""
    status, data, _ = _json_req(
        f"{web.base}/api/runs", "POST",
        {"mode": "lab", "target": "http://[::bad::]/", "auth": None,
         "extra": ""})
    assert status == 400
    assert data["ok"] is False
    assert not any(p.is_dir() for p in web.root.iterdir())


def test_runner_path_records_done_and_its_events(tmp_path):
    root = tmp_path / "e"
    root.mkdir()
    seen = {}

    def runner(info, log):
        seen.update(info)
        # This runner records evidence, through `Session` - the only path
        # allowed to append to the transcript. It used to record nothing at
        # all while the test asserted `done`, which is what locked in the
        # defect the next test now pins: `done` is a claim about what was
        # recorded, so a runner that records nothing cannot be the subject
        # of a test that asserts it.
        session = Session(Path(info["dir"]).parent, info["target"], meta={},
                          resume=Path(info["dir"]))
        session.record_event("external_result", {"tool": "nmap", "rc": 0})
        log("probe 1 sent")

    w = _spawn(root, model_configured=True, runner=runner)
    try:
        _, data, _ = _json_req(f"{w.base}/api/runs", "POST",
                               {"mode": "lab", "target": LAB_TARGET,
                                "auth": None, "extra": "go"})
        detail = _wait_state(w, data["run_id"], {"done"})
        assert detail["run"]["finished"] is not None
        assert any("probe 1 sent" in e["text"] for e in detail["events"])
        assert seen["mode"] == "lab" and seen["target"] == LAB_TARGET
        assert Path(seen["dir"]).is_dir()
    finally:
        w.srv.shutdown()
        w.srv.server_close()


def test_a_runner_that_records_nothing_is_not_reported_done(tmp_path):
    """The honesty invariant on the path this server actually creates.

    A runner can return normally having recorded nothing:
    `argus.team.coordinator.run` RETURNS {"lead_error": ...} instead of
    raising, so a runner built on it returns when the lead agent errored.
    Measured before the fix: GET /api/runs gave
    {"state":"done","note":"","findings":0,"finished":1794989484.135} for a
    directory holding only meta.json, notes.md, prompt.txt and the sidecar,
    while `api._derive_state` on that same directory said ('failed', 'no
    transcript entries - nothing was recorded', None). A dead run looked
    clean, and `done` was reported for an agent that never probed.
    """
    root = tmp_path / "e"
    root.mkdir()

    def runner(info, log):
        log("starting work")      # no transcript, no finding, no report

    w = _spawn(root, model_configured=True, runner=runner)
    try:
        _, data, _ = _json_req(f"{w.base}/api/runs", "POST",
                               {"mode": "lab", "target": LAB_TARGET,
                                "auth": None, "extra": ""})
        run_id = data["run_id"]
        detail = _wait_state(w, run_id, {"done", "failed", "blocked"})
        row = detail["run"]
        assert row["state"] == "failed", row
        assert "without recording" in row["note"]
        assert not (root / run_id / "transcript.jsonl").exists()
        # and the row no longer contradicts the directory it describes
        assert api._derive_state(root / run_id)[0] == "failed"
        # The same after a restart, when only the sidecar is left: a
        # terminal state skips the stale check, so a `done` written there
        # was permanent.
        #
        # JOINED, NOT POLLED. The API row and this FILE are written by
        # different parties: the row is derived from the directory and is
        # terminal as soon as the runner returns, while the sidecar is
        # flushed by the WORKER THREAD in its `finally`. Asserting both in
        # one breath read `'running' == 'failed'` on one Windows CI job; a
        # 10-second poll was the first remedy and it failed on TWO Windows
        # jobs of the same run, so the window was never the problem - the
        # test was racing a thread it can simply wait for.
        #
        # `registry.wait()` joins the worker threads, which is what it
        # exists for. After it returns, the flush has happened or the
        # thread is gone, and the assertion is exact rather than probable:
        # the sidecar ends up terminal, with no claim about when.
        w.registry.wait(30)
        side = root / run_id / api.WEB_STATE_FILE
        written = json.loads(side.read_text(encoding="utf-8"))
        assert written.get("state") == "failed", written
    finally:
        w.srv.shutdown()
        w.srv.server_close()


def _until(cond, timeout: float = 10.0, step: float = 0.02):
    """Wait for a background thread to finish making a post-condition true.

    Several assertions in this file read state that a WORKER THREAD sets
    after the request that started it returned. `registry.wait()` joins the
    threads, but some of what these tests assert is set elsewhere - a run's
    state transition, a lazily reaped thread list - so asserting immediately
    after `wait()` is a race, and CI found three of them one at a time while
    the local gate stayed green.

    Returns the condition's last value either way, so the caller asserts on
    it and gets the real value in the failure message rather than `False`.

    AND A TRANSIENT OSError IS "NOT YET", NOT A FAILURE. CI #590 went red on
    windows-latest/3.10 only:

        tests/test_web.py:439: state = _until(lambda: json.loads(
            side.read_text(encoding="utf-8")).get("state") == "failed")
        E   PermissionError: [Errno 13] Permission denied:
            'C:\\Users\\runneradmin\\AppData\\Local\\Temp\\pytest-of-...'

    The condition READS a file the worker thread is WRITING. On POSIX a
    reader may open a file mid-write and a rename is atomic, so the poll
    either sees the old content or the new one. On Windows the file is
    briefly unopenable - during the write, and during the replace that puts
    the new content in place - and `read_text` raises.

    "The file is momentarily unreadable" is not "the condition is false";
    it is the same not-yet the loop already exists to wait through. So an
    OSError is swallowed WHILE THERE IS TIME LEFT and re-raised if the
    deadline passes without one clean evaluation - a persistent permission
    problem must still surface as itself, not as a confusing assertion on
    None.

    This is the same shape as the callback polling fixed in `probes.py`: a
    check that treats an in-progress state as a verdict.
    """
    deadline = time.time() + timeout
    value, failure = None, None
    while True:
        try:
            value, failure = cond(), None
        except OSError as exc:
            value, failure = None, exc
        if value or time.time() >= deadline:
            break
        time.sleep(step)
    if failure is not None:
        raise failure
    return value


def test_many_sequential_runs_do_not_accumulate(tmp_path):
    """The concurrency cap is not a total cap, and nothing else bounded it.

    Measured: 60 sequential POST /api/runs completed in 0.7 s (each run
    blocks instantly, so MAX_CONCURRENT_RUNS=4 never throttled) and left 60
    session dirs, 60 live records, 60 event lists and 60 dead Thread
    objects, with GET /api/runs already 19.6 KB. At ~85 runs/s from the
    loopback port that is ~5000 of each per minute.
    """
    root = tmp_path / "e"
    root.mkdir()
    n = api.MAX_TRACKED_RUNS + 16
    w = _spawn(root)              # runner=None: every run blocks at once
    try:
        # A 429 HERE IS THE CONCURRENCY CAP WORKING, NOT THE BEHAVIOUR UNDER
        # TEST. `MAX_CONCURRENT_RUNS` slots are released by each run's worker
        # thread, so a POST issued before the previous thread has released
        # its slot is refused - correctly. Whether that happens depends on
        # thread scheduling against the speed of this loop, and it is a race:
        # CI failed one job of eleven on `assert 429 == 200` while ten passed
        # and the local gate was green.
        #
        # What this test claims is everything below: n runs on disk, live
        # records bounded, dead threads reaped, an evicted run still
        # readable. Reaching n runs is its PRECONDITION, so the precondition
        # retries and the claim stays strict.
        #
        # The retries are counted, so a regression that refuses everything
        # still fails: a blind retry loop would turn "the server 429s every
        # request" into a slow pass.
        retries = 0
        for _ in range(n):
            for attempt in range(40):
                status, data, _ = _json_req(
                    f"{w.base}/api/runs", "POST",
                    {"mode": "lab", "target": LAB_TARGET, "auth": None,
                     "extra": ""})
                if status != 429:
                    break
                retries += 1
                time.sleep(0.02)
            assert status == 200 and data["ok"] is True
        assert retries <= n, (
            f"{retries} slot refusals for {n} runs - the cap is refusing "
            "more than it admits, which is not a scheduling race")
        w.registry.wait(10)
        assert len(list(root.iterdir())) == n      # every run is on disk
        assert len(w.registry.live()) <= api.MAX_TRACKED_RUNS
        # THE DETERMINISTIC INVARIANT, not a snapshot comparison. This read
        # `len(_threads) <= len(alive) + 1` with `alive` computed AFTER
        # `wait()` joined every thread - so `alive` is always 0 and the
        # assertion meant `<= 1`. That holds only when runs finish faster
        # than the loop creates them, which is the very condition that fails
        # under load: CI failed it with `assert 3 <= (0 + 1)`.
        #
        # Reaping happens inside `create()`, which filters the list to the
        # live threads and appends one. Concurrency bounds the live set, so
        # the list is bounded by `max_concurrent + 1` ALWAYS - and if reaping
        # were broken this would be n, which is 80 here.
        assert len(w.registry._threads) <= w.registry.max_concurrent + 1, (
            f"{len(w.registry._threads)} thread objects for "
            f"{w.registry.max_concurrent} slots - dead threads are "
            "accumulating")
        assert not [t for t in w.registry._threads if t.is_alive()], \
            "wait() returned with threads still running"
        # nothing a reader can see was lost: the sidecar carries the state
        # and the event log of an evicted run
        oldest = sorted(p.name for p in root.iterdir())[0]
        assert oldest not in w.registry.live()
        status, detail, _ = _json_req(f"{w.base}/api/runs/{oldest}")
        assert status == 200
        assert detail["run"]["state"] == "blocked"
        assert detail["events"]
        assert _json_req(f"{w.base}/api/health")[0] == 200
    finally:
        w.srv.shutdown()
        w.srv.server_close()


def test_a_raising_runner_fails_the_run(tmp_path):
    root = tmp_path / "e"
    root.mkdir()

    def runner(info, log):
        raise RuntimeError("the probe never reached the target")

    w = _spawn(root, model_configured=True, runner=runner)
    try:
        _, data, _ = _json_req(f"{w.base}/api/runs", "POST",
                               {"mode": "lab", "target": LAB_TARGET,
                                "auth": None, "extra": ""})
        detail = _wait_state(w, data["run_id"], {"failed"})
        assert "RuntimeError" in detail["run"]["note"]
        assert "never reached" in detail["run"]["note"]
    finally:
        w.srv.shutdown()
        w.srv.server_close()


def test_concurrency_cap_refuses_the_extra_run(tmp_path):
    root = tmp_path / "e"
    root.mkdir()
    gate = threading.Event()

    def runner(info, log):
        gate.wait(10)

    registry = api.RunRegistry(root, model_configured=True, runner=runner,
                               max_concurrent=1)
    w = _spawn(root, registry=registry)
    try:
        _, first, _ = _json_req(f"{w.base}/api/runs", "POST",
                                {"mode": "lab", "target": LAB_TARGET,
                                 "auth": None, "extra": ""})
        assert first["ok"] is True
        _wait_state(w, first["run_id"], {"running"})
        before = sorted(p.name for p in root.iterdir())
        status, second, _ = _json_req(f"{w.base}/api/runs", "POST",
                                      {"mode": "lab", "target": LAB_TARGET,
                                       "auth": None, "extra": ""})
        assert status == 429
        assert second["ok"] is False and second["run_id"] == ""
        # and it names THIS registry's cap: the body quoted the module
        # constant, so a registry built with max_concurrent=1 told the
        # operator "4 runs are already in progress" with one in flight
        assert second["errors"] == ["1 run is already in progress"]
        # refused before anything was created, so there is no directory
        # standing for a run that never started
        assert sorted(p.name for p in root.iterdir()) == before
    finally:
        gate.set()
        registry.wait(10)
        w.srv.shutdown()
        w.srv.server_close()


def test_the_lifetime_run_cap_stops_an_unbounded_post_loop(web, monkeypatch):
    """A concurrency cap is not a total cap. Measured: 60 sequential POST
    /api/runs completed in 0.7 s against a server with runner=None, because
    every run blocks instantly and MAX_CONCURRENT_RUNS=4 never throttles -
    ~85 runs/s from the unauthenticated loopback port, each one a session
    directory on disk. Driven here with the cap monkeypatched small, so the
    test asserts the refusal rather than the clock.
    """
    monkeypatch.setattr("argus.web.api.MAX_RUNS_PER_SERVER", 2)
    # The precondition tolerates the CONCURRENCY cap; the claim below does
    # not. This test patches the lifetime cap and left the slot cap as an
    # unstated dependency - `MAX_CONCURRENT_RUNS` is a constructor parameter
    # with a module default, and lowering that default made this test fail
    # one run in five on a refusal from the OTHER cap. Found by amplifying
    # the race deterministically (cap 4 -> 1) rather than waiting for load
    # to reproduce it.
    #
    # The claim stays exact because it reads the message: `"lifetime cap" in
    # errors[0]` already distinguishes the two 429s, so a slot refusal can
    # never satisfy it. Only reaching two started runs needed to be robust.
    for _ in range(2):
        for attempt in range(40):
            status, data, _ = _json_req(
                f"{web.base}/api/runs", "POST",
                {"mode": "lab", "target": LAB_TARGET, "auth": None,
                 "extra": ""})
            if status != 429 or "lifetime cap" in str(data.get("errors")):
                break
            time.sleep(0.02)
        assert status == 200 and data["ok"] is True
    before = sorted(p.name for p in web.root.iterdir())
    status, data, _ = _json_req(
        f"{web.base}/api/runs", "POST",
        {"mode": "lab", "target": LAB_TARGET, "auth": None, "extra": ""})
    assert status == 429, data
    assert "lifetime cap" in data["errors"][0]
    # refused before anything was created, like the concurrency cap
    assert sorted(p.name for p in web.root.iterdir()) == before


def test_a_credential_in_the_target_is_refused_not_stored(web):
    """The URL an operator certainly types with a credential in it is the
    target, and the prompt and meta.json are both artifacts. Refused rather
    than masked - and the refusal does not echo the value back either."""
    before = sorted(p.name for p in web.root.iterdir())
    status, body, _ = _req(f"{web.base}/api/runs", "POST",
                           {"mode": "lab", "target": CRED_TARGET,
                            "auth": None, "extra": ""})
    assert status == 400
    assert b"SuperSecret123" not in body
    assert b"credentials in the URL" in body
    assert sorted(p.name for p in web.root.iterdir()) == before


def test_a_runner_error_quoting_a_credential_is_redacted(tmp_path):
    """The remaining path a credential can take into an artifact: a
    runner's own exception text, which routinely quotes the URL it failed
    on. The event log is a second write path, so it carries the same gate
    `Session` applies to the first."""
    root = tmp_path / "e"
    root.mkdir()

    def runner(info, log):
        log(f"connecting to {CRED_TARGET}")
        raise RuntimeError(f"connection refused for {CRED_TARGET}")

    w = _spawn(root, model_configured=True, runner=runner)
    try:
        _, data, _ = _json_req(f"{w.base}/api/runs", "POST",
                               {"mode": "lab", "target": LAB_TARGET,
                                "auth": None, "extra": ""})
        run_id = data["run_id"]
        _wait_state(w, run_id, {"failed"})
        _, raw, _ = _req(f"{w.base}/api/runs/{run_id}")
        assert b"SuperSecret123" not in raw
        assert b"admin:***@" in raw
        sidecar = (root / run_id / api.WEB_STATE_FILE).read_text(
            encoding="utf-8")
        assert "SuperSecret123" not in sidecar
    finally:
        w.srv.shutdown()
        w.srv.server_close()


def test_a_declared_secret_a_runner_logs_is_redacted(tmp_path):
    """The other credential shape: a declared value that is not in a URL.

    `Session` carries `secret_values` precisely so every artifact writer
    scrubs declared values - notes.md, the transcript, agent.log, the
    report. The registry's event log is a new write path AND a new response
    path and was wired to none of it: measured, a runner logging
    "Authorization: Bearer sk-live-SuperSecret123" wrote it verbatim into
    web-run.json and GET /api/runs/<id> returned it, while the `user:pass@`
    line beside it WAS masked.
    """
    root = tmp_path / "e"
    root.mkdir()
    secret = "sk-live-SuperSecret123"

    def runner(info, log):
        log(f"GET /admin with Authorization: Bearer {secret}")
        log(f"retrying {CRED_TARGET}")

    registry = api.RunRegistry(root, model_configured=True, runner=runner,
                               secrets=[secret])
    w = _spawn(root, registry=registry)
    try:
        _, data, _ = _json_req(f"{w.base}/api/runs", "POST",
                               {"mode": "lab", "target": LAB_TARGET,
                                "auth": None, "extra": ""})
        run_id = data["run_id"]
        registry.wait(10)
        _, raw_body, _ = _req(f"{w.base}/api/runs/{run_id}")
        assert secret.encode() not in raw_body
        assert b"admin:***@" in raw_body        # the URL form still masked
        rdir = root / run_id
        sidecar = (rdir / api.WEB_STATE_FILE).read_text(encoding="utf-8")
        assert secret not in sidecar
        # Session's own marker, so there is one redaction rule and not two
        assert "redacted" in sidecar
        for name in ("meta.json", "notes.md"):
            assert secret not in (rdir / name).read_text(encoding="utf-8")
    finally:
        w.srv.shutdown()
        w.srv.server_close()


def test_redact_masks_only_the_credential():
    assert api._redact("http://u:pw1234@h/x") == "http://u:***@h/x"
    # and leaves an ordinary URL, and an unrelated '@', alone
    assert api._redact("http://h/x?a=b@c") == "http://h/x?a=b@c"
    assert api._redact("see note for user admin") == "see note for user admin"


# ---------------------------------------------------------------------------
# listing what is on disk


def test_run_list_includes_a_session_made_without_the_web_ui(web):
    rdir = _plant_session(web.root, findings=[{
        "id": "F01", "title": "SQL injection in /item", "severity": "critical",
        "category": "sqli", "url": LAB_TARGET + "/item?id=1",
        "evidence_excerpt": "sqlite3.OperationalError", "grade": "proven",
        "vuln_class": "sqli"}])
    _, data, _ = _json_req(f"{web.base}/api/runs")
    rows = {r["id"]: r for r in data["runs"]}
    assert rdir.name in rows
    row = rows[rdir.name]
    assert row["state"] == "done"
    assert row["findings"] == 1
    assert row["mode"] == "unknown"   # not started here; nothing claims it was
    assert row["started"] > 0

    _, flat, _ = _json_req(f"{web.base}/api/findings")
    assert [f["run_id"] for f in flat["findings"]] == [rdir.name]
    assert flat["findings"][0]["vuln_class"] == "sqli"
    assert flat["findings"][0]["grade"] == "proven"


def test_a_session_that_recorded_nothing_is_not_done(web):
    """A run that died before its first request leaves meta.json, notes.md
    and an empty transcript. Reporting that as a finished run is how a dead
    run comes to look clean."""
    rdir = _plant_session(web.root, transcript=False, report=False)
    _, data, _ = _json_req(f"{web.base}/api/runs")
    row = next(r for r in data["runs"] if r["id"] == rdir.name)
    assert row["state"] == "failed"
    assert "nothing was recorded" in row["note"]


def test_a_done_sidecar_over_an_empty_directory_is_not_believed(web):
    """Plant the self-contradiction and watch it be named.

    `done` in the sidecar of a directory with no transcript entry is the
    shape a server that graded `done` from "the runner returned" left
    behind on every empty run, and it was permanent: a terminal sidecar
    state skips the stale check, so the row read {"state":"done","note":""}
    for ever over artifacts that recorded nothing. Measured in both
    directions here - through the sidecar, and through the live record,
    which is the highest authority this module has.
    """
    rdir = _plant_session(web.root, transcript=False, report=False,
                          sidecar={"id": "x", "state": "done", "mode": "lab",
                                   "note": "", "finished": 1794989484.135})
    _, data, _ = _json_req(f"{web.base}/api/runs")
    row = next(r for r in data["runs"] if r["id"] == rdir.name)
    assert row["state"] == "failed"
    assert "nothing was recorded" in row["note"]
    assert row["finished"] is None
    live = {"state": "done", "note": "", "finished": 1794989484.135}
    assert api.run_from_dir(rdir, live)["state"] == "failed"
    # and the states that claim nothing ran are left alone
    for state in ("blocked", "failed"):
        assert api.run_from_dir(
            rdir, {"state": state, "note": "n"})["state"] == state


def test_a_resumed_run_being_appended_to_now_is_running_not_done(web):
    """The inverse of the stale-sidecar case: a report from the PREVIOUS
    pass. Every `argus run --resume` starts from a directory that already
    holds report.*, and the report check used to come before the live
    window, so a run probing right now was reported `done` with a
    `finished` timestamp earlier than its own last recorded evidence.
    Measured: a transcript appended 0.0 s ago beside a 2 h-old report.md
    graded ('done', '', <report mtime>).
    """
    rdir = _plant_session(web.root)              # transcript + report.md
    old = time.time() - 7200
    os.utime(rdir / "report.md", (old, old))
    state, note, finished = api._derive_state(rdir)
    assert state == "running", (state, note)
    assert "a pass is in progress" in note
    assert finished is None
    _, data, _ = _json_req(f"{web.base}/api/runs")
    row = next(r for r in data["runs"] if r["id"] == rdir.name)
    assert row["state"] == "running"
    # the other direction, which is the common case: a report rendered
    # after the last transcript write is a finished run
    now = time.time()
    os.utime(rdir / "report.md", (now, now))
    assert api._derive_state(rdir)[0] == "done"


def test_a_stale_running_sidecar_is_not_reported_as_running(web):
    """Plant the bad shape and watch it be named: `running` in a sidecar
    written by a server that has since exited describes a thread that does
    not exist in this process."""
    rdir = _plant_session(web.root, report=False,
                          sidecar={"id": "x", "state": "running",
                                   "mode": "lab", "note": "working"})
    _, data, _ = _json_req(f"{web.base}/api/runs")
    row = next(r for r in data["runs"] if r["id"] == rdir.name)
    assert row["state"] == "failed"
    assert "never recorded" in row["note"]
    assert row["mode"] == "lab"       # the sidecar is still believed on mode


def test_findings_survive_a_hand_edited_file(web):
    rdir = _plant_session(web.root, findings=[
        "not a finding at all",
        {"id": "F01", "title": 1234, "severity": None, "grade": "candidate",
         "url": LAB_TARGET, "evidence_excerpt": "x" * (api.EXCERPT_CAP + 50)},
    ])
    status, data, _ = _json_req(f"{web.base}/api/findings")
    assert status == 200
    rows = [f for f in data["findings"] if f["run_id"] == rdir.name]
    assert len(rows) == 1
    assert rows[0]["title"] == "1234"
    assert len(rows[0]["excerpt"]) == api.EXCERPT_CAP


def test_the_run_list_is_capped(web, monkeypatch):
    """One directory must not grow a dashboard poll without bound, and the
    cap has to keep the NEWEST runs: `/api/runs` was 19.6 KB at 60 runs,
    and `reports_rows`, which scans the same list, had no cap at all."""
    planted = [_plant_session(web.root).name for _ in range(4)]
    monkeypatch.setattr("argus.web.api.MAX_RUN_ROWS", 2)
    _, data, _ = _json_req(f"{web.base}/api/runs")
    ids = [r["id"] for r in data["runs"]]
    assert len(ids) == 2
    assert set(ids) == set(planted[-2:])
    assert len(api.reports_rows(web.root)) <= 2


def test_unknown_and_invalid_run_ids(web):
    status, data, _ = _json_req(f"{web.base}/api/runs/20261118-000000-nope")
    assert status == 404 and data == {"error": "not found"}
    status, data, _ = _json_req(f"{web.base}/api/runs/..")
    assert status in (400, 404)
    assert "not found" in json.dumps(data) or "invalid" in json.dumps(data)


# ---------------------------------------------------------------------------
# reports: traversal, and bytes a target chose


def test_reports_listing_names_the_formats_present(web):
    rdir = _plant_session(web.root, findings=[])
    (rdir / "report.sarif").write_text("{}", encoding="utf-8")
    _, data, _ = _json_req(f"{web.base}/api/reports")
    row = next(r for r in data["reports"] if r["run_id"] == rdir.name)
    assert row["formats"] == ["md", "sarif"]
    assert row["when"] > 0

    status, body, headers = _req(f"{web.base}/api/reports/{rdir.name}?fmt=md")
    assert status == 200
    assert body == b"# report\n"
    assert headers["Content-Type"].startswith("text/markdown")
    assert headers["X-Content-Type-Options"] == "nosniff"

    status, _, headers = _req(
        f"{web.base}/api/reports/{rdir.name}?fmt=sarif")
    assert status == 200
    assert headers["Content-Type"].startswith("application/json")

    status, data, _ = _json_req(
        f"{web.base}/api/reports/{rdir.name}?fmt=exe")
    assert status == 400
    assert "fmt must be one of" in data["error"]

    status, _, _ = _req(f"{web.base}/api/reports/{rdir.name}?fmt=html")
    assert status == 404      # not rendered for this run


def test_report_html_cannot_execute_in_the_dashboard_origin(web):
    rdir = _plant_session(web.root)
    (rdir / "report.html").write_text(
        "<html><body><script>alert(1)</script></body></html>",
        encoding="utf-8")
    status, body, headers = _req(
        f"{web.base}/api/reports/{rdir.name}?fmt=html")
    assert status == 200
    assert b"<script>" in body          # served verbatim, as the artifact is
    csp = headers["Content-Security-Policy"]
    assert csp.startswith("sandbox")    # unique origin, scripting disabled
    assert "default-src 'none'" in csp
    assert headers["X-Content-Type-Options"] == "nosniff"


@pytest.mark.parametrize("rid", [
    "..%2f..%2fetc%2fpasswd",
    "..%2Fsecret",
    "%2e%2e%2f%2e%2e%2fAGENTS.md",
    "%2fetc%2fpasswd",
    "a%00b",
    ".",
])
def test_traversal_on_the_reports_route_is_refused(web, rid):
    outside = web.root.parent / "secret"
    outside.mkdir(exist_ok=True)
    (outside / "report.md").write_text("TOP SECRET\n", encoding="utf-8",
                                   newline="")
    status, body, _ = _req(f"{web.base}/api/reports/{rid}?fmt=md")
    assert status in (400, 404), (rid, status)
    assert b"TOP SECRET" not in body
    assert b"AGENTS.md" not in body
    assert b"root:" not in body


def test_a_session_dir_symlinked_out_of_root_is_refused(web):
    """The id comes from the URL, so resolution is the only place this can
    be caught: a link inside the root that points outside it would otherwise
    serve any file on the box that happens to be called report.md."""
    outside = web.root.parent / "elsewhere"
    outside.mkdir(exist_ok=True)
    (outside / "report.md").write_text("TOP SECRET\n", encoding="utf-8",
                                   newline="")
    (outside / "meta.json").write_text("{}", encoding="utf-8")
    link = web.root / "20261118-000000-linked"
    try:
        os.symlink(outside, link, target_is_directory=True)
    except (OSError, NotImplementedError, AttributeError) as exc:
        pytest.skip(f"symlinks unavailable: {exc}")
    status, body, _ = _req(f"{web.base}/api/reports/{link.name}?fmt=md")
    assert status in (400, 404)
    assert b"TOP SECRET" not in body
    # and it is not LISTED either. `child.is_dir()` follows the link, so
    # measured before the fix GET /api/runs carried the row
    # {"id": "20261118-000000-linked", "target": "http://evil.example",
    #  "state": "done", ...} while its own detail and report routes both
    # 404'd through `resolve()` - the list/detail disagreement the test
    # below declares must not happen.
    _, data, _ = _json_req(f"{web.base}/api/runs")
    assert [r["id"] for r in data["runs"] if r["id"] == link.name] == []
    assert _json_req(f"{web.base}/api/runs/{link.name}")[0] == 404


# ---------------------------------------------------------------------------
# the wire: unknown routes, methods, body limits, binding


def test_unknown_paths_are_json_404s(web):
    for path in ("/nope", "/api", "/api/nope", "/api/runs/a/b/c",
                 "/../../etc/passwd"):
        status, body, headers = _req(web.base + path)
        assert status == 404, path
        assert json.loads(body.decode()) == {"error": "not found"}, path
        assert headers["Content-Type"].startswith("application/json")


def test_an_error_page_never_reflects_the_request(web):
    """The stdlib's send_error interpolates the request path into an HTML
    page; served from this origin that is a reflected-injection surface, and
    it is reached before any route of ours runs."""
    status, body, headers = _req(
        f"{web.base}/api/runs/%3Cimg%20src%3Dx%20onerror%3Dalert(1)%3E")
    assert status in (400, 404)
    assert b"<img" not in body and b"onerror" not in body
    assert headers["Content-Type"].startswith("application/json")

    # and for a request the stdlib itself rejects, before our router
    conn = http.client.HTTPConnection("127.0.0.1",
                                      web.srv.server_address[1], timeout=10)
    conn.request("TRACE", "/api/health")
    resp = conn.getresponse()
    raw = resp.read()
    conn.close()
    assert resp.status in (400, 404, 405, 501)
    assert b"<html" not in raw.lower()


def test_method_not_allowed_is_json(web):
    status, data, _ = _json_req(f"{web.base}/api/prompt")
    assert status == 405 and data == {"error": "method not allowed"}
    status, data, _ = _json_req(f"{web.base}/api/health", "POST", {})
    assert status == 405


def test_a_known_path_with_the_wrong_method_is_405_not_404(web):
    """404 is for a path that does not exist. Measured before this: `POST /`
    and `POST /api/runs/<id>` both answered 404, because do_POST listed
    only api/health, api/findings and api/reports."""
    rdir = _plant_session(web.root)
    for path in ("/", f"/api/runs/{rdir.name}", f"/api/reports/{rdir.name}",
                 "/api/health", "/api/findings", "/api/reports"):
        status, data, _ = _json_req(web.base + path, "POST", {})
        assert status == 405, (path, status)
        assert data == {"error": "method not allowed"}, path
    # and a path that really does not exist stays a 404
    for path in ("/nope", "/api", "/api/nope", "/api/runs/a/b/c"):
        assert _json_req(web.base + path, "POST", {})[0] == 404, path


def test_head_is_routed_and_sends_no_body(web):
    """`_send` and `_send_file` both branch on HEAD, which reads as support
    for it - and there was no do_HEAD at all, so the stdlib answered 501 to
    every HEAD (measured on /api/health). Both branches are driven here."""
    _, get_body, _ = _req(f"{web.base}/api/health")
    status, body, headers = _req(f"{web.base}/api/health", "HEAD")
    assert status == 200
    assert body == b""
    assert headers["Content-Length"] == str(len(get_body))
    rdir = _plant_session(web.root)
    status, body, headers = _req(
        f"{web.base}/api/reports/{rdir.name}?fmt=md", "HEAD")
    assert status == 200 and body == b""
    assert headers["Content-Length"] == str(len(b"# report\n"))


@pytest.mark.parametrize("ctype", [
    "text/plain",
    "application/x-www-form-urlencoded",
    "multipart/form-data; boundary=x",
])
def test_a_form_content_type_cannot_start_a_run(web, ctype):
    """The layer the JSON parser was credited with and never provided.

    A form POST needs no preflight, and `enctype="text/plain"` does produce
    a parseable body: `<input name='{"mode":"lab","target":"http://x/",
    "extra":"' value='"}'>` serialises to {"mode":"lab","target":"http://x/",
    "extra":"="}. Measured before the allowlist: POST /api/runs with
    Content-Type: text/plain -> 200 {"ok":true,"run_id":"...-attacker.
    example"} and a run directory on disk; urlencoded -> a second one. Only
    the Origin check refused it, and `_origin_ok` returns True whenever
    Origin is absent - which a form navigation never sends.
    """
    before = sorted(p.name for p in web.root.iterdir())
    body = json.dumps({"mode": "lab", "target": "http://attacker.example/",
                       "extra": "csrf"}).encode()
    status, data, _ = _json_req(f"{web.base}/api/runs", "POST", raw=body,
                                headers={"Content-Type": ctype})
    assert status == 415, (ctype, data)
    assert "application/json" in data["error"]
    assert sorted(p.name for p in web.root.iterdir()) == before


def test_a_post_with_no_content_type_is_refused(web):
    """Refused as well as the form types: a cross-site `fetch` with a
    typeless Blob body sends no Content-Type and needs no preflight
    either."""
    before = sorted(p.name for p in web.root.iterdir())
    body = b'{"mode":"lab","target":"http://attacker.example/"}'
    conn = http.client.HTTPConnection("127.0.0.1",
                                      web.srv.server_address[1], timeout=10)
    conn.putrequest("POST", "/api/runs")
    conn.putheader("Content-Length", str(len(body)))
    conn.endheaders()
    conn.send(body)
    resp = conn.getresponse()
    data = json.loads(resp.read().decode())
    conn.close()
    assert resp.status == 415, data
    assert sorted(p.name for p in web.root.iterdir()) == before


def test_a_json_content_type_with_parameters_is_accepted(web):
    """The admit direction of the allowlist: the dashboard sends
    `application/json`, and a charset parameter is still JSON."""
    for ctype in ("application/json", "application/json; charset=utf-8",
                  "application/vnd.argus+json"):
        status, data, _ = _json_req(
            f"{web.base}/api/prompt", "POST",
            raw=json.dumps({"mode": "lab", "target": LAB_TARGET}).encode(),
            headers={"Content-Type": ctype})
        assert status == 200, (ctype, data)
        assert data["ok"] is True, ctype


def test_a_request_without_a_host_header_is_refused(web):
    """On a loopback bind the Host check IS the anti-rebinding check, so
    skipping it for a request that simply omits the header hands over the
    bypass. Measured: `GET /api/health` with no Host -> 200 OK."""
    conn = http.client.HTTPConnection("127.0.0.1",
                                      web.srv.server_address[1], timeout=10)
    conn.putrequest("GET", "/api/health", skip_host=True,
                    skip_accept_encoding=True)
    conn.endheaders()
    resp = conn.getresponse()
    body = resp.read()
    conn.close()
    assert resp.status == 421, body


def test_a_body_over_the_cap_is_refused_and_starts_nothing(web):
    before = sorted(p.name for p in web.root.iterdir())
    oversized = b"{\"mode\":\"lab\",\"pad\":\"" + b"A" * (api.MAX_BODY + 1024) \
        + b"\"}"
    status, data, _ = _json_req(
        f"{web.base}/api/runs", "POST", raw=oversized,
        headers={"Content-Type": "application/json"})
    assert status == 413
    assert "larger than" in data["error"]
    assert sorted(p.name for p in web.root.iterdir()) == before
    # the server is still serving: the oversized request was refused, not
    # survived by luck
    assert _json_req(f"{web.base}/api/health")[0] == 200


def test_a_body_just_under_the_cap_is_read(web):
    pad = "A" * (api.MAX_BODY - 4096)
    status, data, _ = _json_req(
        f"{web.base}/api/prompt", "POST",
        {"mode": "lab", "target": LAB_TARGET, "auth": None, "extra": "x",
         "pad": pad})
    assert status == 200
    assert data["ok"] is True


def test_a_chunked_body_is_refused(web):
    """No declared length means no cap before the read, and the console has
    no need for a streamed request.

    WRITTEN AT THE SOCKET AND TOLERATING A BROKEN PIPE, because the server
    is RIGHT to refuse before the body arrives and the first version of
    this test could not survive it. `http.client` with an iterator body
    sends the head, then a chunk-size line, then the chunk, then the
    terminator - and the server answers 411 and closes as soon as it sees
    no Content-Length, which is the whole point of the test. If that close
    lands between two of those writes, `conn.request()` raises
    BrokenPipeError before `getresponse()` is ever reached.

    Measured: 1 failure in 12 local runs, and 3 of 5 ubuntu CI jobs on one
    commit while all 5 Windows jobs passed - a race, not a platform or a
    version. The pattern that ruled those out was ubuntu 3.12 and 3.14
    passing between 3.11 and 3.13 failing.

    So the write may fail, and the response may still be readable: the
    server wrote it before closing. Reading to EOF is correct here because
    411 closes the connection.
    """
    sock = socket.create_connection(
        ("127.0.0.1", web.srv.server_address[1]), timeout=10)
    try:
        body = b'{"mode":"lab"}'
        req = (b"POST /api/prompt HTTP/1.1\r\n"
               b"Host: 127.0.0.1\r\n"
               b"Content-Type: application/json\r\n"
               b"Transfer-Encoding: chunked\r\n\r\n"
               + f"{len(body):x}".encode() + b"\r\n" + body
               + b"\r\n0\r\n\r\n")
        try:
            sock.sendall(req)
        except (BrokenPipeError, ConnectionResetError):
            pass            # refused mid-write, which is the behaviour asserted
        raw = b""
        while True:
            try:
                chunk = sock.recv(4096)
            except (ConnectionResetError, TimeoutError):
                break
            if not chunk:
                break
            raw += chunk
    finally:
        sock.close()

    assert raw, "the server closed without answering at all"
    head, _, payload = raw.partition(b"\r\n\r\n")
    assert b"411" in head.split(b"\r\n")[0], head.split(b"\r\n")[0]
    data = json.loads(payload.decode())
    assert "Content-Length" in data["error"]


def test_malformed_json_is_a_400(web):
    status, data, _ = _json_req(f"{web.base}/api/prompt", "POST",
                                raw=b"{not json",
                                headers={"Content-Type": "application/json"})
    assert status == 400
    assert "JSON" in data["error"]
    status, data, _ = _json_req(f"{web.base}/api/prompt", "POST",
                                raw=b"[1,2,3]",
                                headers={"Content-Type": "application/json"})
    assert status == 400
    assert "object" in data["error"]


def test_dashboard_is_served_or_says_it_is_absent(web):
    status, body, headers = _req(web.base + "/")
    assert status == 200
    assert headers["Content-Type"].startswith("text/html")
    assert "sandbox" not in headers["Content-Security-Policy"]
    assert headers["X-Frame-Options"] == "DENY"
    page = Path(api.__file__).resolve().parent / "dashboard.html"
    if page.exists():
        assert body == page.read_bytes()
    else:
        assert b"is not present" in body
        assert b"/api/health" in body


def test_a_missing_dashboard_file_is_a_notice_not_a_crash(web, monkeypatch):
    """The page is written by another module and may not be installed - a
    wheel that does not ship it is the normal case, not an error. Asserted
    with the file forced absent, because it is present in this tree and the
    branch would otherwise never be exercised."""
    monkeypatch.setattr("argus.web.server.DASHBOARD_FILE", "no-such-page.html")
    status, body, headers = _req(web.base + "/")
    assert status == 200
    assert headers["Content-Type"].startswith("text/html")
    assert b"is not present" in body
    assert b"/api/health" in body
    # and the API is unaffected
    assert _json_req(f"{web.base}/api/health")[0] == 200


def test_a_rebound_host_header_is_refused(web):
    """DNS rebinding is the attack a loopback console is actually exposed
    to: a page on another name resolved to 127.0.0.1 becomes same-origin
    and can read every finding here. The Host header is where that shows."""
    status, data, _ = _json_req(f"{web.base}/api/findings",
                                headers={"Host": "evil.example"})
    assert status == 421
    assert "Host" in data["error"]
    # the same request with the real Host is served
    assert _json_req(f"{web.base}/api/findings")[0] == 200
    for good in ("localhost", "127.0.0.1"):
        assert _json_req(
            f"{web.base}/api/health",
            headers={"Host": f"{good}:{web.srv.server_address[1]}"}
        )[0] == 200


def test_a_cross_site_origin_cannot_start_a_run(web):
    host = f"127.0.0.1:{web.srv.server_address[1]}"
    status, data, _ = _json_req(
        f"{web.base}/api/runs", "POST",
        {"mode": "lab", "target": LAB_TARGET, "auth": None, "extra": ""},
        headers={"Origin": "https://evil.example", "Host": host})
    assert status == 421
    assert not any(p.is_dir() for p in web.root.iterdir())
    # the dashboard's own origin is accepted
    status, ok, _ = _json_req(
        f"{web.base}/api/runs", "POST",
        {"mode": "lab", "target": LAB_TARGET, "auth": None, "extra": ""},
        headers={"Origin": f"http://{host}", "Host": host})
    assert status == 200 and ok["ok"] is True


def test_a_directory_name_no_session_produced_is_not_listed(web):
    """List and detail must agree about what a run is: a row the detail
    route would refuse as an invalid id has no business in the list."""
    odd = web.root / "not a session id"
    odd.mkdir()
    (odd / "meta.json").write_text('{"target": "x", "started": 1}',
                                   encoding="utf-8")
    _, data, _ = _json_req(f"{web.base}/api/runs")
    assert [r["id"] for r in data["runs"]] == []
    status, _, _ = _json_req(
        f"{web.base}/api/runs/{urllib.parse.quote(odd.name)}")
    assert status == 400


def test_non_loopback_bind_needs_the_explicit_argument(tmp_path):
    with pytest.raises(ValueError) as exc:
        make_server("0.0.0.0", 0, root=tmp_path)
    assert "allow_remote" in str(exc.value)
    for host in ("127.0.0.1", "localhost", "::1"):
        assert _check_bind_host(host, False) is None
    # the allow direction is asserted on the gate, not by binding a socket
    # to every interface inside a test suite
    assert _check_bind_host("0.0.0.0", True) is None


class _NoBind(Exception):
    """Raised instead of binding, so these tests drive `serve` without ever
    putting a socket on a wildcard interface - and without the risk that a
    regression leaves `serve_forever` running inside the suite."""


def _serve_without_binding(monkeypatch, seen):
    """`serve` with the real bind gate and no socket.

    The gate is the thing under test, so the stand-in calls it; everything
    after it would bind.
    """
    def no_bind(host, port, **kwargs):
        seen["host"] = host
        seen["allow_remote"] = kwargs.get("allow_remote")
        _check_bind_host(host, kwargs.get("allow_remote", False))
        raise _NoBind(host)

    monkeypatch.setattr("argus.web.server.make_server", no_bind)


def test_serve_does_not_grant_the_remote_override_from_the_bind_address(
        tmp_path, monkeypatch, capsys):
    """`serve` is the function the CLI calls - cli.py does
    `serve(args.bind, args.port, Path(args.session_dir))` - and it used to
    compute `allow_remote = not _is_loopback(host)` from the host it was
    asked to bind, i.e. it granted the override exactly when the gate would
    have fired. Measured: `serve("0.0.0.0", 0, root)` returned 0 having
    bound ('0.0.0.0', 35413) with handler.loopback_bind False, after which
    `GET /api/findings` with `Host: evil.example` answered 200 OK. The
    bind-gate test above exercises `make_server`, which no shipped caller
    uses.
    """
    monkeypatch.delenv(ALLOW_REMOTE_ENV, raising=False)
    seen: dict = {}
    _serve_without_binding(monkeypatch, seen)
    rc = serve("0.0.0.0", 0, tmp_path)
    assert rc != 0
    assert seen["allow_remote"] is False
    err = capsys.readouterr().err
    assert "refusing to bind" in err
    assert ALLOW_REMOTE_ENV in err           # the message names the opt-in

    # a loopback bind is unaffected: it reaches the bind with no override
    seen.clear()
    with pytest.raises(_NoBind):
        serve("127.0.0.1", 0, tmp_path)
    assert seen["allow_remote"] is False


def test_serve_takes_the_remote_override_as_its_own_opt_in(tmp_path,
                                                           monkeypatch):
    """Two deliberate acts, not one: the bind address, and the override."""
    seen: dict = {}
    _serve_without_binding(monkeypatch, seen)
    monkeypatch.delenv(ALLOW_REMOTE_ENV, raising=False)
    with pytest.raises(_NoBind):
        serve("0.0.0.0", 0, tmp_path, allow_remote=True)
    assert seen["allow_remote"] is True

    seen.clear()
    monkeypatch.setenv(ALLOW_REMOTE_ENV, "1")
    with pytest.raises(_NoBind):
        serve("0.0.0.0", 0, tmp_path)
    assert seen["allow_remote"] is True

    seen.clear()
    monkeypatch.setenv(ALLOW_REMOTE_ENV, "no")
    assert serve("0.0.0.0", 0, tmp_path) != 0
    assert seen["allow_remote"] is False


def test_a_non_loopback_bind_turns_the_host_check_off(tmp_path):
    """Named because it is not visible from the routes: the Host
    anti-rebinding check is skipped for an explicit non-loopback bind, and
    the Origin check cannot stand in for it - `expected` is built from the
    caller's own Host header, so an attacker who sets both matches. That is
    what `serve`'s second opt-in and its warning are for, and the loopback
    direction is where the check has teeth.
    """
    class _Req:
        def __init__(self, headers, loopback):
            self.headers = headers
            self.loopback_bind = loopback
            self.bound_host = "127.0.0.1" if loopback else "0.0.0.0"

    rebind = {"Host": "evil.example", "Origin": "http://evil.example"}
    assert _Handler._origin_ok(_Req(rebind, True)) is False
    assert _Handler._origin_ok(_Req(rebind, False)) is True
    # a request with no Host at all is refused on a loopback bind: the
    # check must not be skippable by omitting the header it reads
    assert _Handler._origin_ok(_Req({}, True)) is False
    assert _Handler._origin_ok(_Req({"Host": "127.0.0.1:8787"}, True)) is True


def test_two_servers_do_not_share_a_root(tmp_path):
    """The handler is subclassed per server; a module-level root would make
    one server serve the other's sessions."""
    a_root, b_root = tmp_path / "a", tmp_path / "b"
    a_root.mkdir()
    b_root.mkdir()
    rdir = _plant_session(a_root)
    a, b = _spawn(a_root), _spawn(b_root)
    try:
        _, in_a, _ = _json_req(f"{a.base}/api/runs")
        _, in_b, _ = _json_req(f"{b.base}/api/runs")
        assert [r["id"] for r in in_a["runs"]] == [rdir.name]
        assert in_b["runs"] == []
    finally:
        for srv in (a.srv, b.srv):
            srv.shutdown()
            srv.server_close()


def test_a_missing_root_is_an_empty_list_not_a_crash(tmp_path):
    w = _spawn(tmp_path / "does-not-exist")
    try:
        status, data, _ = _json_req(f"{w.base}/api/runs")
        assert status == 200 and data["runs"] == []
        assert _json_req(f"{w.base}/api/findings")[1]["findings"] == []
        assert _json_req(f"{w.base}/api/reports")[1]["reports"] == []
    finally:
        w.srv.shutdown()
        w.srv.server_close()


def test_the_server_binds_loopback_only(web):
    """A socket on 127.0.0.1 is not reachable on another local address."""
    host, port = web.srv.server_address[:2]
    assert host == "127.0.0.1"
    probe = socket.socket()
    probe.settimeout(1.0)
    try:
        failed = probe.connect_ex(("127.0.0.2", port)) != 0
    except OSError:
        failed = True
    finally:
        probe.close()
    assert failed


def test_no_target_shape_echoes_the_password_into_the_json():
    """The CRITICAL that survived two rounds of fixing.

    `urlsplit("http://admin:hunter2@ex℀ample.com/")` raises from urllib's
    `_checknetloc` with the ORIGINAL netloc in the message, and that message
    was interpolated into a refusal returned to the dashboard as JSON - so
    previewing a prompt, before launching anything, put the operator's
    password in an HTTP response. The check fires BEFORE the credential
    check, so no ordering of the checks could have saved it.

    The fix is not to redact the message but not to echo it: the wording
    belongs to urllib and can place the netloc anywhere in the sentence, and
    a reader of the refusal needs to know their target was rejected, not how
    a standard-library parser phrases it.

    The trigger class is exactly "a non-ASCII character whose NFKC form
    contains / ? # @ or :", so this enumerates the whole class over the BMP
    rather than sampling it - 19 characters, six URL shapes, both entry
    points. Sampling is what let it survive the first two fixes.
    """
    import unicodedata
    from argus import prompts as _prompts
    from argus.web import api as _api

    password = "zQ7hunter2Xy"
    triggers = [chr(c) for c in range(0x80, 0x10000)
                if any(x in unicodedata.normalize("NFKC", chr(c))
                       for x in "/?#@:")]
    assert len(triggers) >= 15, (
        "the trigger class shrank - if urllib changed, re-derive this test "
        "rather than weakening it")

    shapes = ["http://u:{p}@ex{t}ample.com/", "http://u:{p}@{t}.com/",
              "http://u:{p}@a.com{t}/", "https://u:{p}@[{t}::1]/",
              "http://u:{p}@a.com:8{t}0/", "http://u:{p}@a{t}"]
    leaked = []
    for trigger in triggers:
        for shape in shapes:
            url = shape.format(p=password, t=trigger)
            for name, call in (("api.preview_prompt", _api.preview_prompt),
                               ("prompts.preview", _prompts.preview)):
                try:
                    out = call("lab", url)
                except Exception as exc:          # noqa: BLE001
                    # An exception that escapes carries the message too, and
                    # the dashboard would render it or drop the connection.
                    if password in repr(exc):
                        leaked.append((name, "raised", url))
                    continue
                if password in repr(out):
                    leaked.append((name, "returned", url))
    assert not leaked, leaked[:5]


# ------------------- the scope comment on the run path must stay truthful

def test_the_run_path_claims_only_the_protection_it_has():
    """A comment that states a protection the code lacks is worse than no
    comment, because a reader stops looking.

    MEASURED: `ScopeGuard.check` has five raise branches and exactly one is
    reachable when the guard was built from the target it then checks - the
    scheme/parse branch. The host is the whole allowlist, `exclude_paths` is
    empty, and `allow_private` is forced True for a private target, so the
    cloud-metadata address, `http://10.0.0.1/`, `http://192.168.1.1/admin`
    and `http://[::1]/` all pass. What stood here claimed the opposite -
    "fail-closed: private addresses are only allowed when the target itself
    is private" - which is vacuous, since the target is always itself.

    This asserts the pair that matters: the measured behaviour, and that the
    comment beside it does not claim more than that. Change one and this
    names the other.
    """
    from argus.scope import ScopeGuard, ScopeError

    refused, passed = [], []
    for target in ("http://169.254.169.254/latest/meta-data/",
                   "http://10.0.0.1/", "http://192.168.1.1/admin",
                   "http://[::1]/", "ftp://example.com/", "file:///etc/passwd"):
        try:
            # The constructor refuses too - `file:///etc/passwd` raises
            # there, not in `check()` - and for this question the two are
            # one gate: either the call pair accepts the target or it does
            # not. The first version of this test built the guard outside
            # the try and the ScopeError escaped it.
            ScopeGuard(target).check(target)
            passed.append(target)
        except ScopeError:
            refused.append(target)

    assert refused == ["ftp://example.com/", "file:///etc/passwd"], (
        "the self-built guard refuses the scheme/parse class and nothing "
        f"else; refused={refused}")
    assert "http://169.254.169.254/latest/meta-data/" in passed, (
        "if a real address refusal was added, the comment on the run path "
        "has to be updated to describe it")

    api_src = (Path(__file__).resolve().parents[1]
               / "argus" / "web" / "api.py").read_text(encoding="utf-8")
    # Checked in its CLAIM form, not as a string. The replacement comment
    # quotes the old sentence to say what was wrong with it, and the first
    # version of this assertion could not tell a quote from a claim - the
    # third time in this session that a checker read a mention as an
    # assertion. The claim form is a trailing comment on the construction
    # line itself, which is how it was written.
    import re as _re
    claim = _re.search(r"ScopeGuard\(target\)\s*#\s*(.+)", api_src)
    assert claim is None, (
        "the construction line carries a trailing claim again: "
        f"{claim.group(1)[:60]!r} - say what the guard does in the block "
        "above it, where there is room to be exact")

    # The protection that IS real there is structural, not conditional:
    # there is no parameter for a scope list to arrive in over HTTP, so no
    # branch for it to pass through.
    # The word appears in the comment that explains the absence, so the
    # check is for the PASSING form: no caller on this path hands a scope
    # list to the guard.
    assert "extra_hosts=" not in api_src, (
        "a scope list arriving in a JSON body is a scope decision made by "
        "whoever reached the port")


def test_the_client_holds_the_session_and_an_explicit_cookie_replaces_it():
    """The behaviour that cost five attempts against a live target.

    `GuardedClient` keeps a cookie jar, which the `http_request` schema has
    always said. What it did not say is the CONSEQUENCE: a `Cookie` header
    passed in `headers` REPLACES the jar's, so reading Set-Cookie from a
    successful login and sending it back by hand loses the session.

    MEASURED against bWAPP. `login=bee&password=bug` returned 302 to
    portal.php while wrong credentials returned 200 and the login page
    again, so authentication plainly worked - and every following request
    with a hand-set Cookie got 302 to login.php, while the same sequence
    with NO Cookie header reached the authenticated page and the SQLi
    endpoint behind it. A target that looks unreachable right after a login
    that returned its success redirect is this, not the target.

    This drives a local server rather than the lab, so it runs anywhere.
    """
    import http.server
    import threading

    seen = []

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            seen.append(self.headers.get("Cookie"))
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Set-Cookie", "SID=fromserver; path=/")
            self.end_headers()
            self.wfile.write(b"ok")

        def log_message(self, *a):
            pass

    srv = http.server.HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        base = f"http://127.0.0.1:{srv.server_address[1]}"
        from argus.httpclient import GuardedClient
        from argus.ratelimit import RateLimiter
        from argus.scope import ScopeGuard
        from argus.session import Session
        import tempfile

        sess = Session(Path(tempfile.mkdtemp()), base, {"model": "t"})
        cl = GuardedClient(ScopeGuard(base, allow_private=True), sess,
                           RateLimiter(0.0), max_requests=8)

        cl.send("GET", base + "/one")                     # server sets SID
        cl.send("GET", base + "/two")                     # jar should carry it
        cl.send("GET", base + "/three",
                headers={"Cookie": "SID=mine"})           # and this replaces it

        assert seen[0] is None, "nothing to send on the first request"
        assert seen[1] is not None and "fromserver" in seen[1], \
            "the client must carry the session it was given"
        assert "mine" in seen[2] and "fromserver" not in seen[2], \
            ("an explicit Cookie header REPLACES the jar's - which is why "
             "the schema tells the caller not to set one")
    finally:
        srv.shutdown()
        srv.server_close()


def test_the_session_handed_to_another_process_comes_from_the_jar():
    """The second site of one root cause, and the expensive one.

    `_prove_execution` hands the probe's session to the browser so a
    reflected payload is driven at the page that reflected it. It read
    `ctx.client._default_headers` for a Cookie - which is `{}` after a
    login, because `GuardedClient` keeps cookies in the httpx client it
    wraps. So the transfer never fired, the browser visited an
    authenticated page with no session, landed on the login screen, and the
    result read `executed: False`.

    That is exactly the false negative the comment above the code was
    written to prevent, and it made the `xss` class unprovable on any
    authenticated target. MEASURED on bWAPP: before the fix, three payload
    shapes navigated and zero called back; after it, `cookies_set: 2`, two
    shapes executed, and the gate graded the class `proven` on all four
    checks.
    """
    import http.server
    import tempfile
    import threading

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Set-Cookie", "SID=abc; path=/")
            self.send_header("Set-Cookie", "lvl=0; path=/")
            self.end_headers()
            self.wfile.write(b"ok")

        def log_message(self, *a):
            pass

    srv = http.server.HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        base = f"http://127.0.0.1:{srv.server_address[1]}"
        from argus.httpclient import GuardedClient
        from argus.ratelimit import RateLimiter
        from argus.scope import ScopeGuard
        from argus.session import Session
        from argus.tools.probes import _client_cookie_header

        scope = ScopeGuard(base, allow_private=True)
        sess = Session(Path(tempfile.mkdtemp()), base, {"model": "t"})
        cl = GuardedClient(scope, sess, RateLimiter(0.0), max_requests=6)

        assert _client_cookie_header(cl) == "", "nothing to hand over yet"
        cl.send("GET", base + "/login")
        header = _client_cookie_header(cl)
        assert "SID=abc" in header and "lvl=0" in header, header
        # ...and NOT from _default_headers, which is where it used to look
        assert not (getattr(cl, "_default_headers", None) or {}), \
            "the fixture must reproduce the empty header dict"
    finally:
        srv.shutdown()
        srv.server_close()


def test_the_cookie_reader_tolerates_a_renamed_internal():
    """An attribute name is not a contract. A probe must not raise because
    an internal moved - it must report no session, which the caller already
    handles as "the probe holds no session"."""
    from argus.tools.probes import _client_cookie_header

    class Odd:
        pass

    assert _client_cookie_header(Odd()) == ""

    class Broken:
        class _client:
            cookies = object()          # not dict()-able
    assert _client_cookie_header(Broken()) == ""

    class Legacy:
        _default_headers = {"Cookie": "SID=legacy"}
    assert _client_cookie_header(Legacy()) == "SID=legacy", \
        "the old path stays as a fallback rather than being deleted"


def test_until_waits_through_a_transient_read_error():
    """The Windows failure, reproduced without Windows.

    CI #590 went red on windows-latest/3.10 only: a condition that reads a
    file the worker thread is writing raised `PermissionError`, because on
    Windows the file is briefly unopenable during the write and during the
    replace. On POSIX the same poll silently sees old content or new.

    So this plants the transient directly - two raises, then a value - and
    requires the poll to wait through them.
    """
    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] <= 2:
            raise PermissionError(13, "Permission denied")
        return "failed"

    assert _until(flaky, timeout=5.0, step=0.01) == "failed"
    assert calls["n"] == 3


def test_until_surfaces_an_error_that_never_clears():
    """The direction that keeps the tolerance from hiding a real problem.

    A permission error that persists for the whole window is not a slow
    condition - it is a broken one, and it must arrive as itself rather
    than as an assertion about None further up the test.
    """
    import pytest as _pytest

    def always():
        raise PermissionError(13, "Permission denied")

    with _pytest.raises(PermissionError):
        _until(always, timeout=0.3, step=0.01)


def test_until_still_returns_a_falsy_value_for_the_caller():
    """Unchanged contract: the condition's last value comes back either
    way, so a failing assertion names the real value and not `False`."""
    assert _until(lambda: 0, timeout=0.2, step=0.01) == 0
    assert _until(lambda: "ready", timeout=0.2, step=0.01) == "ready"


def test_the_api_aggregate_equals_what_is_on_disk(web):
    """TWO LISTS, ONE CONCEPT, across sessions - where double counting lives.

    One session's findings were covered; the multi-session aggregate was
    not, and that is exactly where a bug counted twice would appear: the
    console reads this endpoint, so an aggregate that sums a session into
    itself, or drops one, misreports the engagement while every individual
    finding is correct.

    Measured against the sealed evidence before writing this: the endpoint
    returns 16 findings over four runs with no repeated (run, id) pair, and
    a direct read of the four findings.json files gives the same 16 and the
    same grade split. The relation held and nothing asserted it.
    """
    import json as _json

    a = _plant_session(web.root, findings=[
        {"id": "F01", "title": "sqli one", "severity": "critical",
         "category": "sqli", "vuln_class": "sqli", "grade": "proven",
         "url": f"{LAB_TARGET}/item?id=1", "evidence_ids": ["r1"],
         "evidence_excerpt": "sqlite"},
        {"id": "F02", "title": "xss one", "severity": "medium",
         "category": "xss", "vuln_class": "xss", "grade": "candidate",
         "url": f"{LAB_TARGET}/search?q=x", "evidence_ids": ["r2"],
         "evidence_excerpt": "<svg"},
    ])
    b = _plant_session(web.root, findings=[
        {"id": "F01", "title": "rce two", "severity": "critical",
         "category": "rce", "vuln_class": "rce", "grade": "proven",
         "url": f"{LAB_TARGET}/ping?host=x", "evidence_ids": ["r1"],
         "evidence_excerpt": "uid=0(root)"},
    ])

    _, flat, _ = _json_req(f"{web.base}/api/findings")
    rows = flat["findings"]

    on_disk = []
    for sdir in (a, b):
        for f in _json.loads((sdir / "findings.json").read_text(
                encoding="utf-8")):
            on_disk.append((sdir.name, str(f.get("id"))))

    served = [(str(r.get("run_id")), str(r.get("id"))) for r in rows
              if str(r.get("run_id")) in {a.name, b.name}]

    assert sorted(served) == sorted(on_disk), (
        f"the endpoint serves {sorted(served)} against {sorted(on_disk)} "
        "on disk")
    assert len(served) == len(set(served)), \
        "a (run, id) pair appears twice - one finding counted twice"

    from collections import Counter
    grades = Counter(str(r.get("grade")) for r in rows
                     if str(r.get("run_id")) in {a.name, b.name})
    assert grades == Counter({"proven": 2, "candidate": 1}), grades


def test_one_session_is_not_summed_into_itself(web):
    """The specific failure the audit named: a bug counted twice because an
    aggregate walks the same directory more than once. With a single
    session planted, the endpoint must serve exactly its findings - not
    two of each."""
    a = _plant_session(web.root, findings=[
        {"id": "F01", "title": "only one", "severity": "high",
         "category": "idor", "vuln_class": "idor", "grade": "proven",
         "url": f"{LAB_TARGET}/api/user/2", "evidence_ids": ["r1"],
         "evidence_excerpt": "user2@x.io"},
    ])
    _, flat, _ = _json_req(f"{web.base}/api/findings")
    mine = [r for r in flat["findings"] if str(r.get("run_id")) == a.name]
    assert len(mine) == 1, f"one finding served {len(mine)} times"
