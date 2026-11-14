"""Probe verdict logic, driven with a stubbed client.

The lab cannot exercise every branch: `probe_cache`'s "the cache was already
warm" answer needs a response that announces a cache in its headers, and the
lab serves none. A stub is the honest way to assert that branch, and keeping
it out of `test_lab.py` keeps that module's claim - probes against the real
app - true.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from argus.tools import probes


class _Client:
    """Returns one canned response per request, in order."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.sent = []

    def send(self, method, url, headers=None, body=None, tool="", note=""):
        self.sent.append({"method": method, "url": url,
                          "headers": headers or {}, "note": note})
        r = self._responses.pop(0) if self._responses else {}
        out = {"status": r.get("status", 200), "body": r.get("body", ""),
               "headers": r.get("headers", {}),
               "request_id": f"r{len(self.sent)}",
               # pass-through, because a probe that reads a duration has to
               # be testable against one. `probe_time` decides entirely on
               # this field and the status beside it.
               "elapsed_ms": r.get("elapsed_ms", 1)}
        return out


class _Ctx:
    def __init__(self, client):
        self.client = client


def _resp(body, headers=None, status=200, elapsed_ms=None):
    out = {"status": status, "body": body, "headers": headers or {}}
    if elapsed_ms is not None:
        out["elapsed_ms"] = elapsed_ms
    return out


def test_cache_probe_says_undecided_when_the_entry_predates_it():
    """A warm cache is not a keyed header, and must not read like one.

    Three requests, two carrying different canaries, all answering
    byte-identically, with a cache announcing itself: nothing the probe sent
    could reach the cache, so the header was never given a chance. Reporting
    the same "no signal" as a properly keyed header read as a defence that
    was never tested.
    """
    page = "<html>cached page</html>"
    marks = {"X-Cache": "HIT", "Age": "412"}
    ctx = _Ctx(_Client([
        _resp(page, marks),          # poison attempt
        _resp(page, marks),          # clean fetch
        _resp(page, marks),          # reflection check
        _resp("not found", status=404),   # deception .css suffix
    ]))
    out = probes.probe_cache(ctx, "http://t/page")
    assert "undecided" in out["verdict"], out
    assert "X-Cache: HIT" in out["verdict"], out


def test_cache_probe_does_not_call_a_static_page_a_warm_cache():
    """The same three identical bodies with no cache header prove nothing.

    A page that simply does not reflect the header answers identically three
    times. Calling that a warm cache would be a claim about infrastructure
    nothing here observed, so the cache indicator is required rather than
    inferred from the bodies matching.
    """
    page = "<html>static</html>"
    ctx = _Ctx(_Client([
        _resp(page), _resp(page), _resp(page),
        _resp("not found", status=404),
    ]))
    out = probes.probe_cache(ctx, "http://t/page")
    assert "undecided" not in out["verdict"], out


def test_cache_probe_still_reports_the_poisoning_it_finds():
    """The canary coming back to a clean request outranks everything else.

    The canary is random per call, so the stub reflects whatever the first
    request sent rather than asserting against a fixed string.
    """
    class _Echo(_Client):
        def send(self, method, url, headers=None, body=None, tool="",
                 note=""):
            out = super().send(method, url, headers, body, tool, note)
            if note == "clean fetch":
                canary = self.sent[0]["headers"].get("X-Forwarded-Host", "")
                out["body"] = f"<html>profile: http://{canary}/me</html>"
            return out

    ctx = _Ctx(_Echo([
        _resp("<html>ok</html>"), _resp("<html>ok</html>"),
        _resp("<html>ok</html>"), _resp("not found", status=404),
    ]))
    out = probes.probe_cache(ctx, "http://t/page")
    assert "cache-poisoning candidate" in out["verdict"], out


def test_probe_time_does_not_call_a_transport_failure_a_delay():
    """A request that never came back was counted as a delay.

    `slow = r["elapsed_ms"] >= threshold` read a duration and ignored the
    `status` sitting in the same dict. On a read timeout the client records
    status 0 and keeps `elapsed_ms` as the whole wait - against a 15s read
    timeout, while the threshold at the default delay is only
    baseline + 2800ms. So a WAF that blackholes requests containing
    `SLEEP(`, `pg_sleep(` or `WAITFOR` rather than rejecting them reported a
    time-based candidate on every payload family at once: the defence
    manufacturing the evidence for the bug it is defending against.

    A status of 0 is this client's "no response". Anything the server
    actually sent still counts, including a 500 - a database that errors
    after sleeping did sleep.
    """
    # two quick baselines, then every payload blackholed
    responses = [_resp("ok", elapsed_ms=40), _resp("ok", elapsed_ms=45)]
    responses += [_resp("", status=0, elapsed_ms=15000.0) for _ in range(7)]
    ctx = _Ctx(_Client(responses))
    out = probes.probe_time(ctx, "http://t/item?id=1", "id")
    assert out["verdict"] == "no delay observed", out
    assert all(not r["slow"] for r in out["results"]), out["results"]
    assert all(r["status"] == 0 and not r["answered"]
               for r in out["results"]), out["results"]

    # ...and a target that really does sleep still reports it
    responses = [_resp("ok", elapsed_ms=40), _resp("ok", elapsed_ms=45)]
    responses += [_resp("ok", status=200, elapsed_ms=4200.0) for _ in range(7)]
    out2 = probes.probe_time(_Ctx(_Client(responses)),
                             "http://t/item?id=1", "id")
    assert "time-based candidate" in out2["verdict"], out2
    assert any(r["slow"] for r in out2["results"]), out2["results"]


def test_probe_lockout_and_its_verifier_agree_on_one_ramp():
    """The probe's half read a DERIVED quantity and lost the signal.

    `probe_lockout` decided soft throttling with means of three and
    `last > first * 3 + 150`. On the commonest real ramp - ten failed
    logins answering 150ms and creeping to 600ms, no 429, no lockout
    wording - that computes 553 > 650 and reported "online password
    guessing is unthrottled", while `verify_no_throttle` refuses the same
    bytes. One property, two quantities, and the probe was wrong in the
    direction that writes a false finding into a report.

    Both halves now call `proof.latency_ramp`, so this test asserts the
    agreement rather than either number: it fails if the probe stops
    calling it, and it fails if the two disagree for any other reason.
    """
    from argus import proof

    ramp = [150.0, 150.0, 200.0, 250.0, 300.0, 350.0, 420.0, 500.0, 560.0,
            600.0]
    responses = [_resp("Invalid username or password", status=401,
                       elapsed_ms=ms) for ms in ramp]
    out = probes.probe_lockout(_Ctx(_Client(responses)), "http://t/login",
                               "username=x&password=y")
    assert "throttling observed" in out["verdict"], out["verdict"]
    assert "grow slower" in out["verdict"], out["verdict"]
    assert len(out["results"]) == len(ramp), out["results"]

    # the same evidence through the gate's own half, which must not call it
    # unthrottled either
    entries = [
        {"id": f"p{n + 1}", "ts": 1000.0 + n,
         "request": {"method": "POST", "url": "http://t/login",
                     "headers": {"content-type":
                                 "application/x-www-form-urlencoded"},
                     "body": f"username=admin&password=guess{n}"},
         "response": {"status": 401, "headers": {}, "elapsed_ms": ms,
                      "body": "Invalid username or password"}}
        for n, ms in enumerate(ramp)]
    assert proof.grade("lockout", "Invalid username or password",
                       entries).grade != "proven"

    # ...and the unthrottled direction, where both must still say so
    flat = [_resp("Invalid username or password", status=401, elapsed_ms=120.0)
            for _ in ramp]
    clean = probes.probe_lockout(_Ctx(_Client(flat)), "http://t/login",
                                 "username=x&password=y")
    assert "unthrottled" in clean["verdict"], clean["verdict"]


def test_probe_lockout_does_not_read_a_dropped_attempt_as_a_slowdown():
    """An attempt that got no answer has the timeout in `elapsed_ms`.

    This is the correction `probe_time` took in the same module. Ten
    attempts where the last few are blackholed at 15s look exactly like a
    savage ramp, and reading them as one reports a throttle that the target
    never applied - the opposite error, but the same unread status beside
    the duration.

    The verdict has to say what it judged on, because "no lockout after ten
    attempts" means something different when four of them got no answer.
    """
    responses = [_resp("Invalid", status=401, elapsed_ms=120.0)
                 for _ in range(6)]
    responses += [_resp("", status=0, elapsed_ms=15000.0) for _ in range(4)]
    out = probes.probe_lockout(_Ctx(_Client(responses)), "http://t/login",
                               "username=x&password=y")
    assert "throttling observed" not in out["verdict"], out["verdict"]
    assert "got no answer" in out["verdict"], out["verdict"]
