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
               "request_id": f"r{len(self.sent)}", "elapsed_ms": 1}
        return out


class _Ctx:
    def __init__(self, client):
        self.client = client


def _resp(body, headers=None, status=200):
    return {"status": status, "body": body, "headers": headers or {}}


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
