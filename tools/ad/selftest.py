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
import cap_split          # noqa: E402
import tick               # noqa: E402
import agent_lint         # noqa: E402
import host_diff          # noqa: E402
import secret_inventory   # noqa: E402

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


@case("sla: a check that PASSED and has vanished from the spec is a regression")
def _():
    # The failure this tool exists to stop: patch by deleting the feature, then
    # delete the check that noticed. A compare() that only walks `after` never
    # sees it and returns "safe to keep".
    before = {"results": [{"name": "index", "ok": True},
                          {"name": "store_note", "ok": True}]}
    after = {"results": [{"name": "index", "ok": True}]}
    c = sla_check.compare(before, after)
    assert [r["check"] for r in c["regressions"]] == ["store_note"], c
    assert c["verdict"] == "REVERT THE PATCH", c
    # and the message must name the legal escape hatch, or a blocked operator
    # stops running --compare at all, which is worse than the bug
    assert "--save" in c["regressions"][0]["reasons"][0], c


@case("sla: a check that was ALREADY FAILING and has vanished does not block")
def _():
    before = {"results": [{"name": "index", "ok": True},
                          {"name": "store_note", "ok": False}]}
    after = {"results": [{"name": "index", "ok": True}]}
    c = sla_check.compare(before, after)
    assert c["regressions"] == [] and c["verdict"] == "safe to keep", c


@case("sla: a RENAMED failing check is caught, not blessed")
def _():
    before = {"results": [{"name": "index", "ok": True},
                          {"name": "store_note", "ok": True}]}
    after = {"results": [{"name": "index", "ok": True},
                         {"name": "store_note_v2", "ok": False,
                          "reasons": ["status 404, wanted 201"], "excerpt": ""}]}
    c = sla_check.compare(before, after)
    assert c["regressions"], c
    assert c["verdict"] == "REVERT THE PATCH", c
    # the rename is visible in `added`, which is informational and never blocks
    assert c["added"] == ["store_note_v2"], c


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
            # The message names the consequence rather than the notation, because
            # slash notation was never the only way to write a range.
            assert "discovery" in str(exc), exc
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


@case("farm: dry-run submits nothing, says so, and reports it did not submit")
def _():
    text, err, for_real = flag_farm.submit(
        {"submit": {"url": "http://example/flags"}}, ["AAA", "BBB"], dry_run=True)
    assert err is None and "not submitted" in text, (text, err)
    # err is None here even though nothing was sent, which is exactly why a
    # caller must key its drain on for_real and not on err.
    assert for_real is False, for_real


# --- the host guard. The positive case matters as much as the refusals: a guard
# --- that rejects a valid host is a guard the operator switches off at hour four.
@case("farm: a wildcard host is refused")
def _():
    assert flag_farm.check_host("10.60.1.*"), "wildcard accepted"


@case("farm: a numeric range host is refused")
def _():
    assert flag_farm.check_host("10.60.1.1-50"), "range accepted"
    assert flag_farm.check_host("10.60.1-3.1"), "octet range accepted"


@case("farm: a comma-separated host list is refused")
def _():
    assert flag_farm.check_host("10.60.1.1,10.60.1.2"), "comma list accepted"


@case("farm: a space-separated host pair is refused")
def _():
    assert flag_farm.check_host("10.60.1.1 10.60.1.2"), "space list accepted"


@case("farm: a shell metacharacter in a host is refused")
def _():
    assert flag_farm.check_host("$(id)"), "command substitution accepted"
    assert flag_farm.check_host("a;id"), "semicolon accepted"


@case("farm: a host carrying a port is refused, and the message says where it goes")
def _():
    problem = flag_farm.check_host("10.60.1.1:5000")
    assert problem and "exploit argv" in problem, problem


@case("farm: real contest hosts are still accepted")
def _():
    for good in ("10.60.1.1", "2001:db8::1", "notes.team3.local", "team-1.local",
                 "web1-2.example.com"):
        assert flag_farm.check_host(good) is None, (good, flag_farm.check_host(good))


@case("farm: every bad host is reported, not just the first")
def _():
    with tempfile.TemporaryDirectory() as tmp:
        p = _write(tmp, "c.json", {
            "authorized_event": "lab", "exploit": ["true"], "flag_regex": "FLAG[0-9]",
            "teams": [{"id": 1, "host": "10.60.1.*"}, {"id": 2, "host": "10.60.2.0/24"}]})
        try:
            flag_farm.load_config(p)
        except SystemExit as exc:
            problems = json.loads(str(exc))["problems"]
            assert len(problems) >= 2, problems
            return
        raise AssertionError("two bad hosts were accepted")


@case("farm: a flag_regex with a capturing group is refused at load time")
def _():
    with tempfile.TemporaryDirectory() as tmp:
        p = _write(tmp, "c.json", {
            "authorized_event": "lab", "exploit": ["true"],
            "teams": [{"id": 1, "host": "10.60.1.1"}],
            "flag_regex": r"FLAG\{(.*?)\}"})
        try:
            flag_farm.load_config(p)
        except SystemExit as exc:
            assert "capturing group" in str(exc), exc
            return
        raise AssertionError("a capturing group was accepted")


@case("farm: the extractor returns the whole flag, not the captured group")
def _():
    # The defect this replaces: re.findall with a group returns the group, so
    # every flag would be submitted with its wrapper stripped.
    import re
    out = "got FLAG{abc123} here"
    assert {m.group(0) for m in re.finditer(r"FLAG\{(.*?)\}", out)} == {"FLAG{abc123}"}
    assert re.findall(r"FLAG\{(.*?)\}", out) == ["abc123"]


# --- durability: `seen` means SUBMITTED, `pending` means HELD.
def _farm_cfg(**over):
    cfg = {"authorized_event": "lab", "service": "notes",
           "teams": [{"id": 1, "host": "10.60.1.1"}, {"id": 2, "host": "10.60.1.2"}],
           "exploit": ["true"], "flag_regex": "FLAG[0-9]", "skip_self": 9,
           "submit": {"url": "http://127.0.0.1:1/flags"}}
    cfg.update(over)
    return cfg


def _with_stubs(flags_by_team, submit_result):
    """Run one tick with run_exploit and submit replaced. No socket, no subprocess."""
    real_run, real_submit = flag_farm.run_exploit, flag_farm.submit
    flag_farm.run_exploit = lambda cfg, team: {
        "team": team.get("id"), "host": team["host"],
        "flags": list(flags_by_team.get(team.get("id"), [])), "status": "ok",
        "stderr": "", "seconds": 0.0}
    if submit_result is not None:
        flag_farm.submit = lambda cfg, flags, dry_run=False: submit_result
    try:
        return real_run, real_submit
    finally:
        pass


@case("farm: a failed submit HOLDS flags as pending, and never as submitted")
def _():
    real_run, real_submit = flag_farm.run_exploit, flag_farm.submit
    try:
        _with_stubs({1: ["FLAG1"], 2: ["FLAG2"]}, ("", "HTTP 503", True))
        seen, pending = set(), set()
        out = flag_farm.tick(_farm_cfg(), seen, pending)
        assert out["new_flags"] == 2, out
        assert out["pending_flags"] == 2, out
        assert out["submitted_ok"] is False, out
        assert seen == set(), seen
        assert pending == {"FLAG1", "FLAG2"}, pending
    finally:
        flag_farm.run_exploit, flag_farm.submit = real_run, real_submit


@case("farm: the next successful submit drains pending into seen")
def _():
    real_run, real_submit = flag_farm.run_exploit, flag_farm.submit
    try:
        _with_stubs({1: ["FLAG1"]}, ("", "HTTP 503", True))
        seen, pending = set(), set()
        flag_farm.tick(_farm_cfg(), seen, pending)
        assert pending == {"FLAG1"} and seen == set()
        # scoreboard comes back
        flag_farm.submit = lambda cfg, flags, dry_run=False: ("accepted", None, True)
        out = flag_farm.tick(_farm_cfg(), seen, pending)
        assert out["submitted_ok"] is True, out
        assert pending == set(), pending
        assert seen == {"FLAG1"}, seen
    finally:
        flag_farm.run_exploit, flag_farm.submit = real_run, real_submit


@case("farm: a flag already submitted is never resubmitted")
def _():
    real_run, real_submit = flag_farm.run_exploit, flag_farm.submit
    try:
        _with_stubs({1: ["FLAG1"]}, ("accepted", None, True))
        seen, pending = {"FLAG1"}, set()
        out = flag_farm.tick(_farm_cfg(), seen, pending)
        assert out["new_flags"] == 0, out
        assert out["pending_flags"] == 0, out
        assert seen == {"FLAG1"} and pending == set()
    finally:
        flag_farm.run_exploit, flag_farm.submit = real_run, real_submit


@case("farm: a dry run holds flags instead of draining them")
def _():
    real_run = flag_farm.run_exploit
    try:
        _with_stubs({1: ["FLAG1"]}, None)   # the REAL submit, dry-run branch
        seen, pending = set(), set()
        out = flag_farm.tick(_farm_cfg(), seen, pending, dry_run=True)
        assert out["submitted_ok"] is False, out
        assert pending == {"FLAG1"}, pending
        assert seen == set(), seen
        assert "held, not lost" in out.get("pending_note", ""), out
    finally:
        flag_farm.run_exploit = real_run


@case("farm: a config with no submit.url holds flags instead of draining them")
def _():
    real_run = flag_farm.run_exploit
    try:
        _with_stubs({1: ["FLAG1"]}, None)   # the REAL submit, missing-url branch
        seen, pending = set(), set()
        out = flag_farm.tick(_farm_cfg(submit={}), seen, pending)
        assert out["submitted_ok"] is False, out
        assert pending == {"FLAG1"} and seen == set()
    finally:
        flag_farm.run_exploit = real_run


@case("farm: two teams returning the same flag counts once")
def _():
    real_run, real_submit = flag_farm.run_exploit, flag_farm.submit
    try:
        _with_stubs({1: ["FLAG9"], 2: ["FLAG9"]}, ("accepted", None, True))
        seen, pending = set(), set()
        out = flag_farm.tick(_farm_cfg(), seen, pending)
        assert out["new_flags"] == 1, out
        assert seen == {"FLAG9"}, seen
    finally:
        flag_farm.run_exploit, flag_farm.submit = real_run, real_submit


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


# ----------------------------------------------------------------- cap_split
HERE_FIXTURE = os.path.join(HERE, "fixtures", "http_requests.fields")


def _fixture_rows():
    with open(HERE_FIXTURE, encoding="utf-8") as fh:
        return cap_split.split_rows(fh.read())


@case("cap: the tshark invocation asks for hex fields, not rendered text")
def _():
    argv = cap_split.tshark_argv("cap.pcap", "http.request")
    assert "-T" in argv and "fields" in argv, argv
    # the two hex carriers are what makes this lossless; a text field renders a
    # real CR/LF/TAB as a two-character escape and cannot be reversed
    assert "tcp.reassembled.data" in argv and "tcp.payload" in argv, argv
    assert "-Y" in argv, argv


@case("cap: a single-segment row rebuilds the whole request")
def _():
    rows = _fixture_rows()
    raw = cap_split.rebuild(rows[0])
    assert raw is not None, rows[0]
    assert raw.startswith(b"GET /health HTTP/1.1"), raw[:40]
    assert raw.endswith(b"\r\n\r\n"), raw[-8:]


@case("cap: a body carrying the field separator and a real TAB survives exactly")
def _():
    raw = cap_split.rebuild(_fixture_rows()[1])
    assert raw is not None
    # a "|" inside the body is only safe because the payload travels as hex
    assert b'"__proto__[x]=1|y"' in raw, raw
    # a REAL tab, not the two characters backslash-t that -T fields would render
    assert b'"t":"a\tb"' in raw, raw
    assert b"a\\tb" not in raw, raw


@case("cap: a multi-segment row prefers reassembled data over the frame payload")
def _():
    rows = _fixture_rows()
    multi = rows[2]
    # the frame payload alone holds only the tail, and a reader that trusted it
    # would emit a truncated request that replays as a 400
    tail_only = cap_split.rebuild([multi[0], multi[1], multi[2], multi[3],
                                   multi[4], "", multi[6]])
    whole = cap_split.rebuild(multi)
    assert whole is not None and whole.startswith(b"GET /static?f=../../flags/current")
    assert tail_only is None or len(whole) > len(tail_only), (whole, tail_only)


@case("cap: a malformed row is skipped, never guessed")
def _():
    rows = _fixture_rows()
    # no method, non-hex payload, and the wrong field count
    skipped = [r for r in rows if cap_split.rebuild(r) is None]
    assert len(skipped) == 3, [len(r) for r in skipped]


@case("cap: strip_follow drops the banner and the server direction")
def _():
    follow = ("===================================================================\n"
              "Follow: tcp,ascii\n\n"
              "GET /api/note?id=1 HTTP/1.1\r\nHost: x\r\n\r\n\n\n"
              "HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\nFLAG{leaked}\n")
    kept = cap_split.strip_follow(follow)
    assert len(kept) == 1, kept
    assert kept[0].startswith("GET /api/note"), kept
    # the flag out of the RESPONSE must not travel into a replay aimed at a
    # third team; this is the whole reason cap_split exists
    assert all("FLAG{leaked}" not in k for k in kept), kept


@case("cap: a rebuilt GET replays with no body and no response line")
def _():
    raw = cap_split.rebuild(_fixture_rows()[2])
    req = traffic_mine.parse_request(raw.decode("utf-8", "replace"))
    cmd = traffic_mine.replay_template(req)
    # the defect this guards: a follow dump put the response in the request body,
    # so a GET came out of the miner carrying --data-binary with the response
    assert "--data-binary" not in cmd, cmd
    assert "HTTP/1.0" not in cmd, cmd
    assert "$TARGET" in cmd, cmd


@case("cap: a rebuilt POST keeps its own body in the replay")
def _():
    raw = cap_split.rebuild(_fixture_rows()[1])
    req = traffic_mine.parse_request(raw.decode("utf-8", "replace"))
    cmd = traffic_mine.replay_template(req)
    # distinguished from the GET case by method on purpose: a POST SHOULD carry
    # its body, so the two cases together say "the body is the request's, and
    # only the request's"
    assert "--data-binary" in cmd, cmd
    assert "__proto__" in cmd, cmd
    assert "HTTP/1.0" not in cmd, cmd


# --- honesty of the non-yielding buckets. "returned no flag" is three
# --- different facts, and only one of them is a patch.
def _farm_status_stub(by_team):
    """Replace run_exploit with a per-team table of results. No subprocess."""
    return lambda cfg, team: dict(by_team[team["id"]], team=team["id"],
                                  host=team["host"], stderr="", seconds=0.0)


@case("farm: immune holds only the team that ran the exploit and gave nothing")
def _():
    real_run, real_submit = flag_farm.run_exploit, flag_farm.submit
    try:
        flag_farm.run_exploit = _farm_status_stub({
            1: {"flags": ["FLAG1"], "status": "ok"},
            2: {"flags": [], "status": "timeout"},
            3: {"flags": [], "status": "error: [Errno 2] No such file or directory"},
            4: {"flags": [], "status": "exit 0"},
        })
        flag_farm.submit = lambda cfg, flags, dry_run=False: ("accepted", None, True)
        cfg = _farm_cfg(teams=[{"id": i, "host": "10.60.%d.1" % i}
                               for i in (1, 2, 3, 4)])
        out = flag_farm.tick(cfg, set(), set())
        assert out["teams_yielding"] == [1], out
        # the whole point of the item: a timeout and a crashed exploit are not
        # patches, and sending the operator to read team 2's patch is the most
        # expensive wrong turn this tool can cause
        assert out["immune"] == [4], out
        assert out["unreachable"] == [2], out
        assert out["exploit_broken"] == [3], out
        for lst, note in (("immune", "immune_note"),
                          ("unreachable", "unreachable_note"),
                          ("exploit_broken", "exploit_broken_note")):
            assert bool(out[note]) == bool(out[lst]), (lst, out[lst], out[note])
        assert "ALERT" not in out, list(out)
    finally:
        flag_farm.run_exploit, flag_farm.submit = real_run, real_submit


@case("farm: an exploit that runs nowhere alerts instead of reporting a patched field")
def _():
    real_run, real_submit = flag_farm.run_exploit, flag_farm.submit
    try:
        broke = "error: [Errno 2] No such file or directory: '/nonexistent/python'"
        flag_farm.run_exploit = _farm_status_stub({1: {"flags": [], "status": broke},
                                                   2: {"flags": [], "status": broke}})
        flag_farm.submit = lambda cfg, flags, dry_run=False: ("accepted", None, True)
        out = flag_farm.tick(_farm_cfg(), set(), set())
        # first key, so it survives a scrolling log
        assert list(out)[0] == "ALERT", list(out)[:3]
        assert "local problem" in out["ALERT"], out["ALERT"]
        assert out["exploit_broken"] == [1, 2], out
        assert out["immune"] == [] and out["unreachable"] == [], out
    finally:
        flag_farm.run_exploit, flag_farm.submit = real_run, real_submit


# --- the submission dialect. Pure, so it is provable here rather than by the
# --- first real submission of the contest.
@case("farm: the three submission dialects produce exactly the bytes they claim")
def _():
    def build(**sub):
        sub.setdefault("url", "http://scoreboard/flags")
        return flag_farm.build_submission({"submit": sub}, ["FLAG1", "FLAG2"])

    # the default is byte-for-byte what this tool sent before the keys existed;
    # changing it would silently break every config already written
    method, url, headers, body = build()
    assert method == "PUT", method
    assert url == "http://scoreboard/flags", url
    assert headers == {"Content-Type": "application/json"}, headers
    assert body == b'["FLAG1", "FLAG2"]', body

    method, _, headers, body = build(format="newline", method="post")
    assert method == "POST", method
    assert headers["Content-Type"] == "text/plain", headers
    assert body == b"FLAG1\nFLAG2\n", body

    _, _, headers, body = build(format="form")
    assert headers["Content-Type"] == "application/x-www-form-urlencoded", headers
    assert body == b"flag=FLAG1&flag=FLAG2", body
    _, _, _, body = build(format="form", field="flag_str")
    assert body == b"flag_str=FLAG1&flag_str=FLAG2", body

    # both keys or neither: a header name with no token sends an empty
    # credential, which some scoreboards answer 200 to and score nothing
    assert build(header="X-Team-Token", token="t")[2]["X-Team-Token"] == "t"
    assert "X-Team-Token" not in build(header="X-Team-Token")[2]
    assert build(token="t")[2] == {"Content-Type": "application/json"}


@case("farm: an unknown submit.format is refused by the builder and at load time")
def _():
    try:
        flag_farm.build_submission(
            {"submit": {"url": "http://scoreboard/flags", "format": "nonsense"}},
            ["FLAG1"])
    except ValueError as exc:
        for valid in flag_farm.SUBMIT_FORMATS:
            assert valid in str(exc), (valid, exc)
    else:
        raise AssertionError("build_submission accepted an unknown format")
    # and refused at startup, which is the only place finding it is free
    with tempfile.TemporaryDirectory() as tmp:
        p = _write(tmp, "c.json", {"authorized_event": "lab",
                                   "teams": [{"id": 1, "host": "10.0.0.1"}],
                                   "exploit": ["true"], "flag_regex": "X",
                                   "submit": {"url": "http://s/f",
                                              "format": "nonsense"}})
        try:
            flag_farm.load_config(p)
        except SystemExit as exc:
            for valid in flag_farm.SUBMIT_FORMATS:
                assert valid in str(exc), (valid, exc)
            return
        raise AssertionError("load_config accepted an unknown submit.format")


# --- the replay must not carry the ATTACKING team's identity to a third team,
# --- and the strip has to be visible or the operator will not add their own.
@case("mine: a replay drops the attacker's Cookie and Authorization")
def _():
    req = traffic_mine.parse_request(
        "POST /api/note HTTP/1.1\r\nHost: 10.60.1.1\r\n"
        "Cookie: session=THEIRS\r\nAuthorization: Bearer THEIRTOKEN\r\n"
        "X-Token: keepme\r\nContent-Type: application/json\r\n\r\n{\"a\":1}")
    cmd = traffic_mine.replay_template(req)
    assert "THEIRS" not in cmd, cmd
    assert "THEIRTOKEN" not in cmd, cmd
    # a non-credential header is the request's own shape and must survive
    assert "keepme" in cmd, cmd


@case("mine: the strip is reported, not silent")
def _():
    req = traffic_mine.parse_request(
        "GET /a HTTP/1.1\r\nHost: h\r\nCookie: session=THEIRS\r\n\r\n")
    plan = traffic_mine.replay_plan(req)
    assert "cookie" in plan["stripped_identity"], plan
    assert plan["needs_auth"] is True, plan
    # the note has to say what happens next, or a 401 reads as "no bug here"
    assert "401" in plan["note"], plan["note"]


@case("mine: a request that carried no credential says so instead of nothing")
def _():
    req = traffic_mine.parse_request("GET /a HTTP/1.1\r\nHost: h\r\n\r\n")
    plan = traffic_mine.replay_plan(req)
    assert plan["stripped_identity"] == [], plan
    assert plan["needs_auth"] is False, plan
    assert plan["note"], plan


@case("mine: a request line with leading whitespace still parses")
def _():
    # One of two shapes that returned None before: a proxy or an editor that
    # indents the first line made the whole request unparseable.
    req = traffic_mine.parse_request("   GET /a?x=1 HTTP/1.1\nHost: h\n\n")
    assert req is not None, "leading whitespace still rejected"
    assert (req["method"], req["path"], req["query"]) == ("GET", "/a", "x=1"), req


@case("mine: a combined access-log line parses and marks what it cannot recover")
def _():
    # The hedge for a containerised estate, a box with no root, or a host with no
    # capture tooling. An access log has no headers and no body, so the record
    # must SAY that rather than look like a complete request.
    line = ('10.60.7.7 - - [29/Sep/2026:10:15:02 +0000] '
            '"GET /static?f=../../flags/current HTTP/1.1" 200 512 "-" "curl/8.5.0"')
    rec = traffic_mine.parse_access_log_line(line)
    assert rec is not None, "a combined log line is still unparseable"
    assert rec["method"] == "GET" and rec["path"] == "/static", rec
    assert rec["query"] == "f=../../flags/current", rec
    assert rec["_unrecoverable"], rec
    assert rec["_source"], rec


@case("mine: a line that is not a log line is refused rather than guessed")
def _():
    assert traffic_mine.parse_access_log_line("this is not a log line") is None
    assert traffic_mine.parse_access_log_line("") is None


@case("mine: a request recovered from a log still scores against a baseline")
def _():
    normal = traffic_mine.parse_access_log_line(
        '1.1.1.1 - - [29/Sep/2026:10:00:00 +0000] "GET /api/note?id=1 HTTP/1.1" 200 10 "-" "checker"')
    attack = traffic_mine.parse_access_log_line(
        '2.2.2.2 - - [29/Sep/2026:10:15:02 +0000] "GET /static?f=../../flags/current HTTP/1.1" 200 512 "-" "x"')
    base = traffic_mine.build_baseline([normal])
    points, reasons = traffic_mine.score(attack, base)
    assert points > 0, (points, reasons)
    assert any("traversal" in r for r in reasons), reasons

# ------------------------------------------------------------------ agent_lint
# A prohibition in a prompt is decorative until something reads it back.
@case("lint: frontmatter is parsed, and an unclosed block is refused not guessed")
def _():
    front, body = agent_lint.split_frontmatter(
        "---\nname: ad-x\ntools: Read, Grep\n---\nthe body\n")
    assert front == {"name": "ad-x", "tools": "Read, Grep"}, front
    assert "the body" in body, body
    bad, reason = agent_lint.split_frontmatter("---\nname: ad-x\nno closing line\n")
    assert bad is None and "never closed" in reason, reason
    missing, reason = agent_lint.split_frontmatter("name: ad-x\n")
    assert missing is None and "does not open" in reason, reason


@case("lint: a scoped Bash entry is one entry, not two")
def _():
    # 'Bash(python3 tools/ad/sla_check.py:*)' contains a comma in real configs;
    # splitting naively turns one scoped entry into two bogus tools.
    entries = agent_lint.tool_entries("Read, Grep, Bash(python3 a.py:*, python3 b.py:*)")
    assert entries == ["Read", "Grep", "Bash(python3 a.py:*, python3 b.py:*)"], entries


@case("lint: write capability is decided by the tool list, not by the prose")
def _():
    assert agent_lint.declares_write(["Read", "Edit"]) is True
    assert agent_lint.declares_write(["Read", "Write"]) is True
    assert agent_lint.declares_write(["Read", "Bash"]) is True
    assert agent_lint.declares_write(["Read", "Grep", "Glob"]) is False
    # a SCOPED Bash is not a general write capability, which is the whole reason
    # the scoped form exists
    assert agent_lint.declares_write(["Read", "Bash(python3 tools/ad/sla_check.py:*)"]) is False


@case("lint: the shipped attack-defense agents pass their own lint")
def _():
    report = agent_lint.audit()
    assert report["failures"] == [], report["failures"]
    # if the directory is ever emptied this must fail loudly rather than pass on
    # an empty set, which is how a guard over zero files reads as green
    assert report["agents"] >= 5, report
    assert report["roles_rows"] >= report["agents"], report


@case("lint: audit never raises, even with nothing on disk")
def _():
    real_dir, real_proh, real_roles = (agent_lint.AGENT_DIR, agent_lint.PROHIBITIONS,
                                       agent_lint.ROLES)
    try:
        agent_lint.AGENT_DIR = os.path.join(HERE, "no-such-dir")
        agent_lint.PROHIBITIONS = os.path.join(HERE, "no-such-file.md")
        agent_lint.ROLES = os.path.join(HERE, "no-such-roles.md")
        report = agent_lint.audit()
    finally:
        # unconditional: a failed assertion must not leave the module pointing at
        # a directory that does not exist for every later case
        (agent_lint.AGENT_DIR, agent_lint.PROHIBITIONS,
         agent_lint.ROLES) = real_dir, real_proh, real_roles
    assert report["agents"] == 0, report
    assert any(f["check"] == "exists" for f in report["failures"]), report

# ------------------------------------------------------------------- host_diff
# There is no debsums, no aide and no host IDS on this box, so this pair is the
# whole answer to "did anything change since the baseline".
def _snap(units=(), keys=(), **surfaces):
    snap = {"host": "h", "taken_utc": "t",
            "enabled_units": {"status": "ok", "lines": list(units)},
            "authorized_keys": {"status": "ok", "lines": list(keys)}}
    snap.update(surfaces)
    return snap


@case("diff: a change on EVERY host reads as the image, not as an intruder")
def _():
    base = _snap(units=["a.service", "b.service"])
    after = _snap(units=["a.service", "b.service", "upgrade.service"])
    report = host_diff.diff_snapshots(base, [("web1", after), ("web2", after),
                                            ("web3", after)])
    assert report["findings"] == 1, report
    assert report["results"][0]["on_all_hosts"] is True, report["results"][0]
    assert report["on_one_host_only"] == 0, report


@case("diff: a change on ONE host of three reads as a person")
def _():
    base = _snap(units=["a.service"])
    planted = _snap(units=["a.service"],
                    keys=["/root/.ssh/authorized_keys: ssh-rsa AAAA attacker"])
    clean = _snap(units=["a.service"])
    report = host_diff.diff_snapshots(base, [("web1", planted), ("web2", clean),
                                            ("web3", clean)])
    first = report["read_this_first"]
    assert first["surface"] == "authorized_keys", first
    assert first["on_all_hosts"] is False, first
    assert first["hosts"] == ["web1"], first
    assert report["on_one_host_only"] == 1, report


@case("diff: the person outranks the image when both changed")
def _():
    # Ranking the image first is how the real finding gets buried, so this is the
    # ordering that earns the tool its place.
    base = _snap(units=["a.service"])
    both = _snap(units=["a.service", "upgrade.service"],
                 keys=["/root/.ssh/authorized_keys: attacker"])
    only_image = _snap(units=["a.service", "upgrade.service"])
    report = host_diff.diff_snapshots(base, [("web1", both), ("web2", only_image),
                                            ("web3", only_image)])
    order = [(f["surface"], f["on_all_hosts"]) for f in report["results"]]
    assert order[0] == ("authorized_keys", False), order
    assert report["read_this_first"]["on_all_hosts"] is False, report["read_this_first"]


@case("diff: a collector that timed out is NOT read as everything disappearing")
def _():
    # None and [] are different answers. A timeout treated as an empty set invents
    # a disappearance for every line the baseline held, which buries the real one.
    base = _snap(units=["a.service", "b.service", "c.service"])
    timed_out = {"host": "h", "taken_utc": "t",
                 "enabled_units": {"status": "timeout", "seconds": 10}}
    report = host_diff.diff_snapshots(base, [("web1", timed_out)])
    assert report["findings"] == 0, report["results"]
    surfaces = [x.get("surface") for x in report["surfaces_not_compared"]]
    assert "enabled_units" in surfaces, report["surfaces_not_compared"]


@case("diff: a surface nobody ranked is reported, never silently dropped")
def _():
    base = _snap(units=["a.service"], unranked_surface={"status": "ok", "lines": ["x"]})
    after = _snap(units=["a.service"],
                  unranked_surface={"status": "ok", "lines": ["x", "y"]})
    report = host_diff.diff_snapshots(base, [("web1", after)])
    found = [f for f in report["results"] if f["surface"] == "unranked_surface"]
    assert found, report["results"]
    # it lands after every ranked surface, but it does land
    assert found[0]["line"] == "y", found[0]

# ------------------------------------------------------------ secret_inventory
# The loss does not come from rotating a credential. It comes from the ORDER.
@case("secrets: the same value in three files is ONE rotation group")
def _():
    findings = []
    findings += secret_inventory.find_secrets('db_password = Sup3rS3cretDB!\n', "a.conf")
    findings += secret_inventory.find_secrets(
        'URL = "postgres://app:Sup3rS3cretDB!@db:5432/n"\n', "b.py")
    findings += secret_inventory.find_secrets(
        '  - MYSQL_ROOT_PASSWORD=Sup3rS3cretDB!\n', "c.yml")
    groups = secret_inventory.group(findings)
    shared = [g for g in groups if g["consumers"] == 3]
    assert shared, [(g["fingerprint"], g["consumers"]) for g in groups]
    assert sorted(p["path"] for p in shared[0]["places"]) == ["a.conf", "b.py", "c.yml"], \
        shared[0]["places"]


@case("secrets: the widely-shared value is rotated LAST, not first")
def _():
    # It is the one most likely to take a service down, so it is rotated while
    # there is still time to fix what it breaks.
    findings = (secret_inventory.find_secrets('token = onlyhere12345\n', "one.conf")
                + secret_inventory.find_secrets('pw = sharedvalue99\n', "x.conf")
                + secret_inventory.find_secrets('pw = sharedvalue99\n', "y.conf"))
    order = secret_inventory.rotation_order(secret_inventory.group(findings))
    assert [item["consumers"] for item in order] == [1, 2], order
    assert "takes the service down later" in order[-1]["note"], order[-1]


@case("secrets: no more than four characters of a value are ever printed")
def _():
    secret = "Sup3rS3cretDB-with-a-long-tail"
    findings = secret_inventory.find_secrets("db_password = %s\n" % secret, "a.conf")
    blob = json.dumps({"groups": secret_inventory.group(findings),
                       "rotation": secret_inventory.rotation_order(
                           secret_inventory.group(findings))})
    # a tool that prints secrets creates a new artifact holding every secret on the
    # box, which is worse than the exposure it was run to measure
    assert secret not in blob, "the whole value leaked"
    assert secret[:8] not in blob, "more than four characters leaked"
    assert findings[0]["shown"].startswith(secret[:4]), findings[0]


@case("secrets: a placeholder and an environment reference are not credentials")
def _():
    for line in ('password = changeme\n', 'secret: CHANGEME\n',
                 'JWT_SECRET=${JWT_FROM_ENV}\n', 'api_key = "%s"\n' % "{{vault}}",
                 'token = $TOKEN\n'):
        assert secret_inventory.find_secrets(line, "f") == [], line


@case("secrets: a private key header is reported without its bytes")
def _():
    text = "-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEA1234567890abcdef\n"
    findings = secret_inventory.find_secrets(text, "id_rsa")
    assert findings, findings
    assert findings[0]["kind"] == "private-key-header", findings[0]
    assert "MIIEow" not in json.dumps(findings), findings


@case("secrets: a minified line is not scanned for credentials")
def _():
    # A bundle line matches a dozen high-entropy patterns, and a finding the
    # operator dismisses forty times is a finding they stop reading.
    line = "var a=1;" + ("x" * 5000) + "password=realsecret123\n"
    assert secret_inventory.find_secrets(line, "bundle.js") == []

# ------------------------------------------------------------- the separation
# tools/ad/ is a deliberate SIBLING control plane: it does not go through
# tools/hooks.py and it does not write challenges/<name>/state.json. Until now
# that was a sentence in a README, and the cheapest way for this design to rot is
# one future edit that imports hooks.py "to record the flag properly".
FORBIDDEN_SIBLINGS = frozenset(("state", "hooks", "decide"))


def _ad_python_files():
    """Every .py under tools/ad, so a file created after today is covered too."""
    out = []
    for name in sorted(os.listdir(HERE)):
        if name.endswith(".py") and name != "selftest.py":
            out.append(os.path.join(HERE, name))
    return out


def _docstring_nodes(tree):
    """The string nodes that are docstrings, so prose is exempt from a literal check."""
    import ast
    nodes = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef,
                                 ast.ClassDef)):
            continue
        body = getattr(node, "body", None) or []
        if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
                and isinstance(body[0].value.value, str):
            nodes.add(id(body[0].value))
    return nodes


@case("sep: nothing under tools/ad imports the jeopardy control plane")
def _():
    import ast
    offenders = []
    for path in _ad_python_files():
        with open(path, encoding="utf-8") as fh:
            tree = ast.parse(fh.read(), filename=path)
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            for name in names:
                # the FIRST dotted component, never startswith: `import decider`
                # must not read as `decide`, or the guard cries wolf and gets
                # deleted by whoever is holding the clock
                if name.split(".")[0] in FORBIDDEN_SIBLINGS:
                    offenders.append((os.path.basename(path), name))
    assert not offenders, offenders


@case("sep: the import check matches a component, not a prefix")
def _():
    # The negative control for the rule above, and it writes nothing: a module
    # named `decider` or `stateful` is legitimate and must not be reported.
    for benign in ("decider", "stateful", "hooksmith", "decide_helper"):
        assert benign.split(".")[0] not in FORBIDDEN_SIBLINGS, benign
    for real in ("state", "hooks", "decide", "hooks.py"):
        assert real.split(".")[0].replace(".py", "") in FORBIDDEN_SIBLINGS or \
            real.split(".")[0] in FORBIDDEN_SIBLINGS, real


@case("sep: no code under tools/ad writes the jeopardy ledger path")
def _():
    import ast
    offenders = []
    for path in _ad_python_files():
        with open(path, encoding="utf-8") as fh:
            tree = ast.parse(fh.read(), filename=path)
        exempt = _docstring_nodes(tree)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
                continue
            if id(node) in exempt:
                continue          # prose may explain the boundary it must not cross
            if "challenges/" in node.value:
                offenders.append((os.path.basename(path), node.value[:60]))
    assert not offenders, offenders


@case("sep: the docstring exemption is real, and only covers docstrings")
def _():
    import ast
    src = ('"""a module docstring naming challenges/<name>/state.json"""\n'
           'def f():\n'
           '    """a function docstring naming challenges/ as well"""\n'
           '    return "challenges/live/state.json"\n')
    tree = ast.parse(src)
    exempt = _docstring_nodes(tree)
    hits = [n.value for n in ast.walk(tree)
            if isinstance(n, ast.Constant) and isinstance(n.value, str)
            and id(n) not in exempt and "challenges/" in n.value]
    # exactly one: the returned literal. Both docstrings are exempt.
    assert hits == ["challenges/live/state.json"], hits

# --------------------------------------------------------------------- tick
# The decider is pure by design, so every ordering rule is provable here rather
# than in a contest. `decide_next(ledger, facts)` touches no file and no clock.
TICK_NOW = 1790000000.0


def _tick_ledger(phase="steady", done=True, **over):
    with open(os.path.join(HERE, "ledger.template.json"), encoding="utf-8") as fh:
        led = json.load(fh)
    led["service"] = "notes"
    led["authorized_event"] = "offline selftest"
    led["phase"] = phase
    for step in led["intake"]:
        step["done"] = done
    led.update(over)
    return led


def _tick_green(**over):
    """A facts dict where all three steady-state questions are answered.

    The mining rule keys on `live_newest` and `mined_newest`, the absolute
    mtimes -- NOT on the `_age_seconds` values, which are derived for display.
    A facts dict that sets only the age fields silently skips that rule, which
    is why `tick: gather_facts reports both ...` below pins the contract.
    """
    facts = {"sla_ok": True, "sla_failed": [], "sla_age_seconds": 10.0,
             "sla_save": "runs/notes/sla/after.json",
             "live_files": 40, "live_newest": TICK_NOW - 30, "live_age_seconds": 30.0,
             "mined_path": "runs/notes/mined/m.json",
             "mined_newest": TICK_NOW - 5, "mined_age_seconds": 5.0,
             "mined_top": None, "new_flags": 2, "immune": [], "teams_yielding": [1, 2],
             "submit_error": None, "pending_flags": 0, "alert": None,
             "last_farm_age_seconds": 20.0}
    facts.update(over)
    return facts


def _tick(ledger, facts):
    return tick.decide_next(ledger, facts, now=TICK_NOW, ledger_path="L.json")


@case("tick: intake runs in order and names the first step not done")
def _():
    out = _tick(_tick_ledger(phase="intake", done=False), {})
    assert out["action"] == "intake_step", out
    # the RUNBOOK's corrected order: nothing is touched before it is copied, and
    # the health spec exists before any credential rotates
    assert "snapshot-before-touching" in out["rationale"], out["rationale"]


@case("tick: every intake step done but the phase still intake asks to close it")
def _():
    out = _tick(_tick_ledger(phase="intake", done=True), {})
    assert out["action"] == "close_intake", out


@case("tick: an UNMEASURED service is not a green one")
def _():
    # The whole point of the facts contract: a fact that could not be read must
    # arrive as None, because a zero or a False would read as "measured and fine"
    # and the attack rules would run against a service nobody has checked.
    out = _tick(_tick_ledger(), _tick_green(sla_ok=None, sla_failed=[],
                                            sla_save=None, sla_age_seconds=None))
    assert out["action"] == "restore_service", out
    assert "unmeasured" in out["rationale"], out["rationale"]


@case("tick: a red service outranks every attack action")
def _():
    out = _tick(_tick_ledger(), _tick_green(sla_ok=False, sla_failed=["store_note"],
                                            mined_path=None, mined_newest=None))
    assert out["action"] == "restore_service", out
    assert "store_note" in out["rationale"], out["rationale"]


@case("tick: held flags outrank mining a capture, because they are already stolen")
def _():
    out = _tick(_tick_ledger(),
                _tick_green(alert="submission has failed for 3 consecutive ticks; "
                                  "14 flag(s) are pending",
                            pending_flags=14, mined_path=None, mined_newest=None))
    assert out["action"] == "fix_submission", out


@case("tick: a capture newer than the newest mined output must be mined")
def _():
    out = _tick(_tick_ledger(), _tick_green(mined_path=None, mined_newest=None,
                                            mined_age_seconds=None))
    assert out["action"] == "mine_traffic", out
    joined = " ".join(out["commands"])
    assert "tools/ad/traffic_mine.py" in joined, out["commands"]
    assert "--baseline" in joined and "--live" in joined, out["commands"]
    # new traffic arriving after the last mining run is the same answer
    again = _tick(_tick_ledger(), _tick_green(mined_newest=TICK_NOW - 900,
                                             live_newest=TICK_NOW - 5))
    assert again["action"] == "mine_traffic", again


@case("tick: nothing newer than the last mining run is not a reason to mine again")
def _():
    out = _tick(_tick_ledger(), _tick_green())
    assert out["action"] == "hold", out


@case("tick: a top-ranked mined request that is not yet an idea is promoted")
def _():
    top = {"method": "GET", "path": "/static", "query": "f=../../flags/current",
           "score": 7, "reasons": ["path traversal"],
           "replay": "curl -sS 'http://$TARGET/static?f=../../flags/current'"}
    out = _tick(_tick_ledger(), _tick_green(mined_top=top))
    assert out["action"] == "promote_candidate", out


@case("tick: an attack action reached while the service is not green is SUPPRESSED")
def _():
    # The structural half of the guard, and it has to be tested with the ordering
    # OUT OF THE WAY. Rule 1 already returns restore_service on a red service, so
    # no ordinary state can reach an attack action while red -- which means a
    # state-driven test proves the ordering, not the guard. Replacing _rules is
    # what a future edit that reorders the rules would effectively do, and the
    # guard must still hold.
    real_rules = tick._rules
    try:
        tick._rules = lambda *a, **k: {"mode": "ad-tick", "action": "farm",
                                       "rationale": "forced", "commands": []}
        out = tick.decide_next(_tick_ledger(),
                               _tick_green(sla_ok=False, sla_failed=["index"]),
                               now=TICK_NOW, ledger_path="L.json")
    finally:
        # unconditional: a failing assertion above must not leave the module
        # patched for every case that runs after it
        tick._rules = real_rules
    assert out["action"] == "restore_service", out
    assert out.get("suppressed_action") == "farm", out
    assert "cannot be won back" in out["rationale"], out["rationale"]


@case("tick: the ordering ALSO keeps an attack action away from a red service")
def _():
    # The other half: with the real rules in place, a red service plus a juicy
    # candidate still answers restore_service, and never reaches the guard.
    top = {"method": "GET", "path": "/static", "query": "f=../../flags",
           "score": 9, "reasons": ["path traversal"], "replay": "curl ..."}
    out = _tick(_tick_ledger(),
                _tick_green(sla_ok=False, sla_failed=["index"], mined_top=top))
    assert out["action"] == "restore_service", out
    assert "suppressed_action" not in out, out


@case("tick: every action that puts packets on another team is registered")
def _():
    # Adding an outbound action without adding it here would let it run against a
    # red service, because the structural guard tests membership of this set.
    assert tick.ATTACK_ACTIONS, tick.ATTACK_ACTIONS
    assert "farm" in tick.ATTACK_ACTIONS, tick.ATTACK_ACTIONS
    assert "promote_candidate" in tick.ATTACK_ACTIONS, tick.ATTACK_ACTIONS


@case("tick: gather_facts reports both the mtime and the age of each source")
def _():
    # The mining rule compares live_newest against mined_newest. If a future edit
    # drops either key the rule stops firing and the tool goes quiet about
    # unmined traffic instead of failing loudly, so pin the contract here.
    facts, missing = tick.gather_facts({"paths": {}}, now=TICK_NOW)
    for key in ("live_newest", "mined_newest", "live_age_seconds",
                "mined_age_seconds", "sla_ok", "alert", "pending_flags"):
        assert key in facts, (key, sorted(facts))
    # nothing was readable, so every fact is None and every gap is reported
    assert facts["sla_ok"] is None and facts["live_newest"] is None, facts
    assert missing, missing


@case("tick: the shipped ledger template decides without crashing")
def _():
    with open(os.path.join(HERE, "ledger.template.json"), encoding="utf-8") as fh:
        template = json.load(fh)
    out = tick.decide(template, now=TICK_NOW, ledger_path="T.json")
    # a fresh template is in intake, which is the only correct answer for a
    # ledger whose paths have not been filled in yet
    assert out["action"] == "intake_step", out


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
