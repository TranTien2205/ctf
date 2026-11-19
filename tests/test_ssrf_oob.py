"""The callback nobody was producing.

`ssrf`'s ceiling was removed and `argus/collector.py` was written to be the
out-of-band witness, and the wiring between them was never done:
`routable_host()` - the function that picks an address a callback can come
back to - had no caller anywhere, which `collector.py` said in its own
docstring. So the class was freed and unreachable at the same time, and
freeing a cap is only real if the class can then be proven.
"""
from __future__ import annotations

import http.server
import pathlib
import socket
import sys
import tempfile
import threading
import urllib.parse
import urllib.request

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from argus import collector as C                        # noqa: E402
from argus.httpclient import GuardedClient              # noqa: E402
from argus.ratelimit import RateLimiter                 # noqa: E402
from argus.scope import ScopeGuard                      # noqa: E402
from argus.session import Session                       # noqa: E402
from argus.tools.registry import Context, dispatch      # noqa: E402


# ----------------------------------------------- routable_host takes a URL

def test_routable_host_accepts_the_shapes_a_caller_actually_holds():
    """MEASURED: passing the engagement target - a URL, which is what this
    package holds everywhere - made `sock.connect(("http://host:8080", 9))`
    raise, and the old fallback answered `127.0.0.1`. The callback URL then
    pointed at the TARGET's own loopback, nothing arrived, and zero hits
    reads as "the target did not call back": a refusal that reads as an
    empty result, in the measurement plumbing itself.
    """
    for shape in ("127.0.0.1", "http://127.0.0.1:8777/", "127.0.0.1:8777",
                  "localhost", "http://localhost/x?y=1", "[::1]:80"):
        assert C.routable_host(shape) == "127.0.0.1", shape


def test_routable_host_refuses_rather_than_answering_loopback():
    """A loopback answer for a non-local target is the failure that hides.
    `.invalid` cannot resolve, by RFC 2606."""
    with pytest.raises(ValueError, match="no route toward"):
        C.routable_host("http://nothing.invalid/")
    with pytest.raises(ValueError, match="no host in"):
        C.routable_host("")


def test_routable_host_picks_the_interface_a_remote_host_would_see():
    """Not a loopback answer when a real route exists. No packet is sent -
    connecting a UDP socket only picks the route - so this needs no peer."""
    try:
        chosen = C.routable_host("8.8.8.8")
    except ValueError:
        pytest.skip("no route off this machine")
    assert not chosen.startswith("127."), chosen
    socket.inet_aton(chosen)


# ------------------------------------------------- the probe, both directions

class _Fetcher(http.server.BaseHTTPRequestHandler):
    """A target that fetches whatever URL lands in `?u=` - an SSRF, so the
    positive direction can be measured without the lab."""

    fetch = True

    def do_GET(self):
        query = urllib.parse.parse_qs(urllib.parse.urlsplit(self.path).query)
        url = (query.get("u") or [""])[0]
        if self.fetch and url.startswith("http://"):
            try:
                urllib.request.urlopen(url, timeout=3).read()
            except Exception:                           # noqa: BLE001
                pass
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, *args):
        pass


def _serve(fetch: bool):
    handler = type("H", (_Fetcher,), {"fetch": fetch})
    srv = http.server.HTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}"


def _ctx(base: str) -> Context:
    scope = ScopeGuard(base, allow_private=True)
    sess = Session(pathlib.Path(tempfile.mkdtemp()), base, {"model": "t"})
    return Context(cfg=None, scope=scope, session=sess,
                   client=GuardedClient(scope, sess, RateLimiter(0.0),
                                        max_requests=12),
                   skills_dir=ROOT / "argus" / "skills")


def test_a_target_that_fetches_produces_a_recorded_callback():
    srv, base = _serve(fetch=True)
    try:
        ctx = _ctx(base)
        out = dispatch(ctx, "probe_ssrf_oob",
                       {"url": base + "/?u=x", "param": "u",
                        "settle_s": 8})["result"]
        assert out["attempted"] and out["fetched"], out
        assert len(out["callbacks"]) == 1, out
        hit = out["callbacks"][0]
        # The hit is in the TRANSCRIPT, not just in this result: a finding
        # has to be able to cite it.
        assert hit["request_id"] in ctx.session._transcript, hit
        assert "the gate pairs them by nonce" in out["note"]
    finally:
        srv.shutdown()
        srv.server_close()


def test_a_loopback_callback_is_reported_as_not_remote():
    """The probe reports what arrived; the GATE decides. For `ssrf` the
    target is another machine, so a loopback peer proves nothing, and the
    probe must hand that fact over rather than hide it."""
    srv, base = _serve(fetch=True)
    try:
        out = dispatch(_ctx(base), "probe_ssrf_oob",
                       {"url": base + "/?u=x", "param": "u",
                        "settle_s": 8})["result"]
        assert out["callbacks"][0]["peer"].startswith("127."), out
        assert out["callbacks"][0]["remote"] is False, out
    finally:
        srv.shutdown()
        srv.server_close()


def test_no_callback_says_which_half_failed():
    """"The target did not fetch" and "the collector was unreachable" are
    different facts and only one of them is about the target. The note names
    the collector address that WAS reachable, so the two cannot be confused.

    MEASURED against bWAPP's `rlfi.php`: status 200, no callback in 4s,
    collector reachable at the LAN address - PHP's `allow_url_include` is
    off, which is a fact about the target and not a plumbing failure.
    """
    srv, base = _serve(fetch=False)
    try:
        out = dispatch(_ctx(base), "probe_ssrf_oob",
                       {"url": base + "/?u=x", "param": "u",
                        "settle_s": 1})["result"]
        assert out["attempted"] and not out["fetched"], out
        assert out["callbacks"] == []
        assert "not a plumbing failure" in out["note"], out["note"]
        assert out["collector_host"] in out["note"], out["note"]
    finally:
        srv.shutdown()
        srv.server_close()


def test_an_unroutable_target_is_refused_before_any_request():
    out = dispatch(_ctx("http://127.0.0.1:1/"), "probe_ssrf_oob",
                   {"url": "http://nothing.invalid/?u=x", "param": "u",
                    "settle_s": 1})["result"]
    assert out["attempted"] is False
    assert "no route toward" in out["reason"], out


def test_the_probe_is_on_the_tool_table():
    """The orphan this file exists because of. A probe nothing can call is
    the same shape of missing as a module nothing imports."""
    from argus.tools import registry
    assert "probe_ssrf_oob" in {t["name"] for t in registry.TOOL_SCHEMAS}


# ---- one definition of waiting, shared by both callback probes

class _LateCollector:
    """A collector whose hit appears partway through the window."""

    def __init__(self, at_second: float):
        import time as _t
        self._due = _t.time() + at_second
        self.polls = 0

    def hits_for(self, nonce, after=0.0):
        import time as _t
        self.polls += 1
        if _t.time() >= self._due:
            return [{"peer": "10.0.0.9", "nonce": nonce}]
        return []


def test_a_callback_inside_the_window_is_seen_whenever_it_arrives():
    """THE DEFECT BOTH CALLBACK PROBES HAD, and the reason this is one
    function rather than two copies.

    Each slept the whole settle window and then checked ONCE, so a callback
    arriving at the window plus anything was missed and the probe reported
    that the target did not call back. The stored-XSS site had a comment
    four lines above it naming that failure - "the probe then reported
    'reflected but did not execute' ... the worst shape of wrong: a
    confident negative" - and then produced the same confident negative
    from a clock instead of from a wrong URL.

    A hit at 0.35s of a 2s window must be returned, which a
    sleep-then-check-once cannot do and a poll does.
    """
    import time

    from argus.tools.probes import wait_for_callback

    col = _LateCollector(0.35)
    started = time.time()
    hits = wait_for_callback(col, "n0nce", started, 2.0)
    assert hits, "a callback inside the window was not seen"
    assert col.polls > 1, "a single check cannot observe a late hit"


def test_an_early_callback_does_not_pay_the_whole_window():
    """The second property: a hit is acted on when it arrives.

    A 20-second window for a target that answers in 50ms used to cost 20
    seconds, which is how a settle window becomes something an operator
    shortens below what a slow target needs.
    """
    import time

    from argus.tools.probes import wait_for_callback

    col = _LateCollector(0.0)
    started = time.time()
    hits = wait_for_callback(col, "n0nce", started, 30.0)
    assert hits
    assert time.time() - started < 5.0, "an immediate hit waited anyway"


def test_the_window_is_still_a_ceiling_when_nothing_calls_back():
    """The property the sleep DID have, and which a fix must not trade away:
    a target that never calls back costs what it did before. Otherwise this
    is a timeout increase wearing a different name."""
    import time

    from argus.tools.probes import wait_for_callback

    class _Silent:
        def hits_for(self, nonce, after=0.0):
            return []

    # ENFORCED, NOT ASSERTED. The first version of this computed `waited`
    # and asserted it was under 3s - and when the ceiling was removed as a
    # plant, the call never returned, so the assertion was never reached:
    # the test HUNG instead of failing. A hang is worse than a red test,
    # because in CI it burns the job's whole timeout and names nothing.
    #
    # Same defect as everything else found today, one level up: the check
    # stated the bound and did not hold it. A thread with a join timeout
    # turns an unbounded wait back into a failure, with the stdlib only.
    import threading

    out: list = []
    started = time.time()
    worker = threading.Thread(
        target=lambda: out.append(
            wait_for_callback(_Silent(), "n0nce", started, 0.4)),
        daemon=True)
    worker.start()
    worker.join(timeout=5.0)
    assert not worker.is_alive(), \
        "the window is not a ceiling - the wait never returned"
    assert out == [[]]
    waited = time.time() - started
    assert 0.3 <= waited < 3.0, f"waited {waited:.2f}s for a 0.4s window"


def test_a_zero_or_negative_window_still_checks_once():
    """A window of 0 must not mean "never look": the callback may already
    have arrived during the request itself, which is the common case for a
    fast loopback target."""
    from argus.tools.probes import wait_for_callback

    col = _LateCollector(0.0)
    assert wait_for_callback(col, "n0nce", 0.0, 0.0)
    assert wait_for_callback(_LateCollector(0.0), "n0nce", 0.0, -5.0)
