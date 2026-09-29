#!/usr/bin/env python3
"""Offline selftest for tools/ad/. No network, no subprocess, no sockets.

Every case drives a pure function directly, so this is safe to wire into
test/run_all.sh next to tools/web/selftest.py and the others. It proves the
decision logic -- which is where these tools are actually wrong when they are
wrong -- not that a socket connects.

    python3 tools/ad/selftest.py
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import sla_check          # noqa: E402
import flag_farm          # noqa: E402
import traffic_mine       # noqa: E402

CASES = []


def case(name):
    def deco(fn):
        CASES.append((name, fn))
        return fn
    return deco


# --------------------------------------------------------------- sla_check
@case("sla: a matching status and body passes")
def _():
    r = sla_check.evaluate({"name": "x", "expect_status": 200,
                            "expect_contains": "token"},
                           200, '{"token":"abc"}', None, 0.01)
    assert r["ok"], r


@case("sla: a wrong status fails and says both numbers")
def _():
    r = sla_check.evaluate({"name": "x", "expect_status": 200}, 500, "", None, 0.01)
    assert not r["ok"]
    assert "500" in r["reasons"][0] and "200" in r["reasons"][0], r


@case("sla: a transport error is a failure, not a pass")
def _():
    r = sla_check.evaluate({"name": "x", "expect_status": 200}, None, "",
                           "TimeoutError: timed out", 5.0)
    assert not r["ok"] and "transport" in r["reasons"][0], r


@case("sla: expect_absent catches a patch that leaks a stack trace")
def _():
    r = sla_check.evaluate({"name": "x", "expect_status": 200,
                            "expect_absent": "Traceback"},
                           200, "oops Traceback (most recent call last)", None, 0.01)
    assert not r["ok"], r


@case("sla: compare reports only REGRESSIONS")
def _():
    before = {"results": [{"name": "a", "ok": True}, {"name": "b", "ok": False}]}
    after = {"results": [{"name": "a", "ok": False, "reasons": ["boom"], "excerpt": ""},
                         {"name": "b", "ok": True}]}
    c = sla_check.compare(before, after)
    assert [r["check"] for r in c["regressions"]] == ["a"], c
    assert c["recovered"] == ["b"], c
    assert c["verdict"] == "REVERT THE PATCH", c


@case("sla: an already-broken check does not block a patch")
def _():
    before = {"results": [{"name": "a", "ok": False}]}
    after = {"results": [{"name": "a", "ok": False, "reasons": ["still"], "excerpt": ""}]}
    c = sla_check.compare(before, after)
    assert c["regressions"] == [] and c["verdict"] == "safe to keep", c


# --------------------------------------------------------------- flag_farm
def _write(tmp, name, obj):
    p = os.path.join(tmp, name)
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(obj, fh)
    return p


@case("farm: a config without authorized_event is rejected")
def _():
    with tempfile.TemporaryDirectory() as tmp:
        p = _write(tmp, "c.json", {"teams": [{"id": 1, "host": "10.0.0.1"}],
                                   "exploit": ["true"], "flag_regex": "X"})
        try:
            flag_farm.load_config(p)
        except SystemExit as exc:
            assert "authorized_event" in str(exc), exc
            return
        raise AssertionError("config was accepted without an authorized_event")


@case("farm: a CIDR in the team list is rejected")
def _():
    with tempfile.TemporaryDirectory() as tmp:
        p = _write(tmp, "c.json", {"authorized_event": "lab",
                                   "teams": [{"id": 1, "host": "10.0.0.0/24"}],
                                   "exploit": ["true"], "flag_regex": "X"})
        try:
            flag_farm.load_config(p)
        except SystemExit as exc:
            assert "CIDR" in str(exc), exc
            return
        raise AssertionError("a CIDR range was accepted as a team host")


@case("farm: a complete config is accepted")
def _():
    with tempfile.TemporaryDirectory() as tmp:
        p = _write(tmp, "c.json", {"authorized_event": "lab",
                                   "teams": [{"id": 1, "host": "10.0.0.1"}],
                                   "exploit": ["echo", "{host}"],
                                   "flag_regex": "[A-Z]{3}"})
        cfg = flag_farm.load_config(p)
        assert cfg["teams"][0]["host"] == "10.0.0.1"


@case("farm: dry-run submits nothing and says so")
def _():
    text, err = flag_farm.submit({"submit": {"url": "http://example/flags"}},
                                 ["AAA", "BBB"], dry_run=True)
    assert err is None and "not submitted" in text, (text, err)


# ------------------------------------------------------------ traffic_mine
@case("mine: a raw request parses into its parts")
def _():
    req = traffic_mine.parse_request(
        "POST /api/note?id=7 HTTP/1.1\r\nHost: x\r\nContent-Type: application/json\r\n"
        "\r\n{\"body\":\"hi\"}")
    assert req["method"] == "POST" and req["path"] == "/api/note", req
    assert req["query"] == "id=7", req
    assert req["headers"]["content-type"] == "application/json", req


@case("mine: parameters are found in query, form body and JSON body")
def _():
    q = traffic_mine.parse_request("GET /a?x=1&y=2 HTTP/1.1\n\n")
    assert traffic_mine.param_names(q) == {"x", "y"}
    form = traffic_mine.parse_request("POST /a HTTP/1.1\n\nu=1&p=2")
    assert traffic_mine.param_names(form) == {"u", "p"}
    js = traffic_mine.parse_request("POST /a HTTP/1.1\n\n{\"k\":1,\"j\":2}")
    assert traffic_mine.param_names(js) == {"k", "j"}


@case("mine: checker traffic scores zero against its own baseline")
def _():
    normal = [traffic_mine.parse_request("GET /api/note?id=1 HTTP/1.1\n\n")]
    base = traffic_mine.build_baseline(normal)
    pts, reasons = traffic_mine.score(normal[0], base)
    assert pts == 0, (pts, reasons)


@case("mine: an unseen path and an injection payload both raise the score")
def _():
    base = traffic_mine.build_baseline(
        [traffic_mine.parse_request("GET /api/note?id=1 HTTP/1.1\n\n")])
    evil = traffic_mine.parse_request(
        "GET /api/note?id=1'%20OR%201=1--%20 HTTP/1.1\n\n")
    pts, reasons = traffic_mine.score(evil, base)
    assert pts > 0 and any("sql" in r for r in reasons), (pts, reasons)

    unseen = traffic_mine.parse_request("GET /admin/debug HTTP/1.1\n\n")
    pts2, reasons2 = traffic_mine.score(unseen, base)
    assert pts2 >= 3 and any("never appears" in r for r in reasons2), (pts2, reasons2)


@case("mine: the replay template drops Host and parameterises the target")
def _():
    req = traffic_mine.parse_request(
        "POST /x HTTP/1.1\nHost: 10.60.1.1\nX-Token: abc\n\npayload")
    cmd = traffic_mine.replay_template(req)
    assert "$TARGET" in cmd, cmd
    # the captured team's address must not survive into a command that will be
    # pointed at every other team
    assert "10.60.1.1" not in cmd, cmd
    # header names are normalised to lower case on parse, and HTTP header names
    # are case-insensitive, so assert the header survived rather than its case
    assert "x-token: abc" in cmd.lower(), cmd
    assert "--data-binary" in cmd, cmd


@case("mine: a directory of requests round-trips through load_dir")
def _():
    with tempfile.TemporaryDirectory() as tmp:
        with open(os.path.join(tmp, "a.txt"), "w", encoding="utf-8") as fh:
            fh.write("GET /one HTTP/1.1\nHost: h\n\n"
                     "GET /two HTTP/1.1\nHost: h\n\n")
        reqs = traffic_mine.load_dir(tmp)
        assert [r["path"] for r in reqs] == ["/one", "/two"], reqs


def main():
    failed = []
    for name, fn in CASES:
        try:
            fn()
        except Exception as exc:
            failed.append((name, "%s: %s" % (type(exc).__name__, exc)))
    print(json.dumps({
        "mode": "ad-selftest",
        "cases": len(CASES),
        "passed": len(CASES) - len(failed),
        "failed": [{"case": n, "error": e} for n, e in failed],
        "offline": True,
    }, ensure_ascii=False, indent=1))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
