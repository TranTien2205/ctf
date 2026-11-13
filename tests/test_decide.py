"""The decision controller: the next move computed from recorded bytes.

The claim under test is narrow and checkable: given a session directory, the
recommendation depends only on what is on disk. So every test here writes a
transcript and a findings file and reads back one action - no loop, no model,
no network. The rules are ordered, so most tests are about which rule fires
when several could.

The tests that matter most are the ones asserting what the controller does
NOT say: it must not recommend recording a finding for a page that merely
echoes its input, and it must not invent an endpoint or a parameter that no
recorded request carried.
"""
from __future__ import annotations

import json

import pytest

from argus import decide


def _session(tmp_path, entries=(), findings=()):
    sdir = tmp_path / "sess" if tmp_path.name != "sess" else tmp_path
    sdir.mkdir(parents=True, exist_ok=True)
    (sdir / "transcript.jsonl").write_text(
        "".join(json.dumps(e) + "\n" for e in entries), encoding="utf-8")
    (sdir / "findings.json").write_text(
        json.dumps(list(findings)), encoding="utf-8")
    return sdir


def _exchange(rid, url, body="hello", tool="http_request", status=200,
              method="GET", req_body=None):
    return {"id": rid, "kind": "http", "tool": tool,
            "request": {"method": method, "url": url, "headers": {},
                        "body": req_body},
            "response": {"status": status, "headers": {}, "body": body}}


# --- the degenerate cases ---------------------------------------------------

def test_a_missing_directory_asks_for_a_session_not_a_probe(tmp_path):
    action = decide.next_action(tmp_path / "nope")
    assert action.action == "open_session"


def test_an_empty_transcript_asks_for_recon(tmp_path):
    action = decide.next_action(_session(tmp_path))
    assert action.action == "recon"
    assert "surface" in action.why


def test_a_malformed_transcript_line_is_skipped_not_fatal(tmp_path):
    sdir = _session(tmp_path, [_exchange("r1", "http://t/?q=1")])
    with (sdir / "transcript.jsonl").open("a", encoding="utf-8") as fh:
        fh.write("{not json\n")
    action = decide.next_action(sdir)
    assert action.action != "open_session"


def test_an_unreadable_findings_file_does_not_crash_the_controller(tmp_path):
    sdir = _session(tmp_path, [_exchange("r1", "http://t/?q=1")])
    (sdir / "findings.json").write_text("{{{", encoding="utf-8")
    assert decide.next_action(sdir).action == "probe"


# --- rule 3 / 4: surface ----------------------------------------------------

def test_an_endpoint_with_a_parameter_and_no_probe_is_the_next_probe(tmp_path):
    sdir = _session(tmp_path, [_exchange("r1", "http://t/search?q=cat")])
    action = decide.next_action(sdir)
    assert action.action == "probe"
    assert action.target == "http://t/search"
    assert action.detail["params"] == ["q"]


def test_an_endpoint_with_no_named_input_is_not_recommended(tmp_path):
    # there is nowhere to put a payload; recommending one anyway is how a
    # ledger starts inventing work
    sdir = _session(tmp_path, [_exchange("r1", "http://t/about")])
    action = decide.next_action(sdir)
    assert action.action != "probe"


def test_a_static_asset_is_not_surface(tmp_path):
    sdir = _session(tmp_path, [
        _exchange("r1", "http://t/app.js?v=2"),
        _exchange("r2", "http://t/logo.png?w=10")])
    assert decide.next_action(sdir).action != "probe"


def test_a_form_body_contributes_its_field_names(tmp_path):
    sdir = _session(tmp_path, [
        _exchange("r1", "http://t/login", method="POST",
                  req_body="user=admin&pass=x")])
    action = decide.next_action(sdir)
    assert action.action == "probe"
    assert action.detail["params"] == ["pass", "user"]


def test_a_json_body_is_not_parsed_as_a_form(tmp_path):
    sdir = _session(tmp_path, [
        _exchange("r1", "http://t/api", method="POST",
                  req_body='{"a": "b=c"}')])
    action = decide.next_action(sdir)
    assert action.action != "probe" or action.detail.get("params") != ["a"]


def test_a_probed_endpoint_still_missing_a_first_pass_class(tmp_path):
    sdir = _session(tmp_path, [
        _exchange("r1", "http://t/search?q=cat"),
        _exchange("r2", "http://t/search?q=cat'", tool="probe_sqli")])
    action = decide.next_action(sdir)
    assert action.action == "probe"
    assert action.vuln_class == "xss"
    assert "sqli" in action.detail["classes_tried"]


def test_the_recommendation_names_a_real_requirement(tmp_path):
    sdir = _session(tmp_path, [
        _exchange("r1", "http://t/search?q=cat"),
        _exchange("r2", "http://t/search?q=cat", tool="probe_sqli")])
    action = decide.next_action(sdir)
    from argus import proof
    assert action.detail["requirement"] == proof.requirement_of(
        action.vuln_class)
    assert action.detail["requirement"]


# --- rule 2: the proof gap --------------------------------------------------

def test_a_candidate_finding_turns_into_the_missing_check(tmp_path):
    sdir = _session(
        tmp_path,
        [_exchange("r1", "http://t/item?id=1")],
        [{"id": "F01", "vuln_class": "sqli", "grade": "candidate",
          "url": "http://t/item?id=1", "evidence_ids": ["r1"],
          "proof": {"missing": ["rows returned, not an error message"]}}])
    action = decide.next_action(sdir)
    assert action.action == "close_proof_gap"
    assert action.finding_id == "F01"
    assert action.detail["missing"] == ["rows returned, not an error message"]
    assert action.tool == "probe_sqli"


def test_a_candidate_in_a_capped_class_does_not_starve_the_ledger(tmp_path):
    """Found by an adversarial audit. `xss` is capped at `candidate`, so no
    amount of probing closes its gap - and rule 2 recommended closing it
    forever, which meant every rule below it never ran."""
    sdir = _session(
        tmp_path,
        [_exchange("r1", "http://t/search?q=cat")],
        [{"id": "F01", "vuln_class": "xss", "grade": "candidate",
          "url": "http://t/search?q=cat", "evidence_ids": ["r1"],
          "proof": {"missing": ["a real browser executed it"]}}])
    action = decide.next_action(sdir)
    assert action.action != "close_proof_gap", action.render()
    # and an UNcapped candidate still does produce the gap
    from argus import proof
    assert proof.spec_for("xss").ceiling == "candidate"
    assert proof.spec_for("sqli").ceiling == ""


def test_a_proven_finding_is_not_a_gap(tmp_path):
    sdir = _session(
        tmp_path,
        [_exchange("r1", "http://t/p?x=1", tool="probe_sqli")],
        [{"id": "F01", "vuln_class": "sqli", "grade": "proven",
          "url": "http://t/p?x=1", "evidence_ids": ["r1"],
          "proof": {"missing": []}}])
    assert decide.next_action(sdir).action != "close_proof_gap"


def test_a_refused_class_is_not_chased(tmp_path):
    # a refused class is a policy decision, not a gap to close
    sdir = _session(
        tmp_path,
        [_exchange("r1", "http://t/p?x=1", tool="probe_sqli")],
        [{"id": "F01", "vuln_class": "dos", "grade": "refused",
          "url": "http://t/p?x=1", "evidence_ids": ["r1"],
          "proof": {"missing": ["this system does not prove this class"]}}])
    assert decide.next_action(sdir).action != "close_proof_gap"


def test_the_gap_rule_outranks_the_surface_rule(tmp_path):
    # closing a proof you nearly hold beats opening a new one
    sdir = _session(
        tmp_path,
        [_exchange("r1", "http://t/item?id=1"),
         _exchange("r2", "http://t/other?z=9")],
        [{"id": "F01", "vuln_class": "sqli", "grade": "candidate",
          "url": "http://t/item?id=1", "evidence_ids": ["r1"],
          "proof": {"missing": ["rows returned, not an error message"]}}])
    assert decide.next_action(sdir).action == "close_proof_gap"


# --- rule 1: a proof already on disk ---------------------------------------

def test_an_unrecorded_command_output_is_the_first_thing_to_record(tmp_path):
    body = "uid=33(www-data) gid=33(www-data) groups=33(www-data)\nargusabcd1234\n"
    sdir = _session(tmp_path, [
        {"id": "r7", "kind": "http", "tool": "probe_cmdi",
         "request": {"method": "GET",
                     "url": "http://t/ping?host=1;id;echo argusabcd1234",
                     "headers": {}, "body": None},
         "response": {"status": 200, "headers": {}, "body": body}}])
    action = decide.next_action(sdir)
    assert action.action == "record_finding", action.render()
    assert action.vuln_class == "rce"
    assert action.detail["evidence_ids"] == ["r7"]


def test_an_echoing_page_is_never_recommended_for_recording(tmp_path):
    # the exact failure the proof matrix exists to prevent: a search box that
    # reflects its query is not a database, a shell or a template engine
    for tool, payload in (("probe_sqli", "' OR 1=1--"),
                          ("probe_cmdi", "; id"),
                          ("probe_ssti", "{{7*7}}"),
                          ("probe_nosqli", '{"$ne": null}')):
        body = f"<html><p>No results for: {payload}</p></html>"
        sdir = _session(tmp_path, [
            _exchange("r1", f"http://t/search?q={payload}", body=body,
                      tool=tool)])
        action = decide.next_action(sdir)
        assert action.action != "record_finding", (
            f"{tool}: an echo of the payload was recommended as a proof\n"
            + action.render())


def test_an_already_cited_exchange_is_not_recommended_again(tmp_path):
    body = "uid=0(root) gid=0(root)\nargusabcd1234\n"
    sdir = _session(
        tmp_path,
        [{"id": "r7", "kind": "http", "tool": "probe_cmdi",
          "request": {"method": "GET",
                      "url": "http://t/ping?host=1;id;echo argusabcd1234",
                      "headers": {}, "body": None},
          "response": {"status": 200, "headers": {}, "body": body}}],
        [{"id": "F01", "vuln_class": "rce", "grade": "proven",
          "url": "http://t/ping", "evidence_ids": ["r7"],
          "proof": {"missing": []}}])
    assert decide.next_action(sdir).action != "record_finding"


def test_rule_one_outranks_everything_else(tmp_path):
    body = "uid=0(root) gid=0(root)\nargusabcd1234\n"
    sdir = _session(
        tmp_path,
        [{"id": "r7", "kind": "http", "tool": "probe_cmdi",
          "request": {"method": "GET",
                      "url": "http://t/ping?h=1;id;echo argusabcd1234",
                      "headers": {}, "body": None},
          "response": {"status": 200, "headers": {}, "body": body}},
         _exchange("r8", "http://t/other?z=9")],
        [{"id": "F01", "vuln_class": "xss", "grade": "candidate",
          "url": "http://t/s?q=1", "evidence_ids": ["r1"],
          "proof": {"missing": ["a real browser executed it"]}}])
    action = decide.next_action(sdir)
    assert action.action == "record_finding"
    assert action.vuln_class == "rce"


def test_a_probe_tool_only_grades_its_own_class(tmp_path):
    # re-grading every exchange against all 29 classes is what makes a
    # controller hallucinate; a cmdi probe's output is graded as rce only
    assert decide.PROBE_CLASS["probe_cmdi"] == "rce"
    body = "uid=0(root) gid=0(root)"
    sdir = _session(tmp_path, [
        _exchange("r1", "http://t/p?x=1", body=body, tool="http_request")])
    # the same bytes, from a tool that names no class: no recommendation
    assert decide.next_action(sdir).action != "record_finding"


# --- rule 5: the budget -----------------------------------------------------

def test_a_class_that_spent_its_budget_is_parked_by_name(tmp_path):
    entries = [_exchange("r0", "http://t/s?q=1")]
    entries += [_exchange(f"p{i}", "http://t/s?q=1", tool=t)
                for t in decide._FIRST_PASS
                for i in range(decide.BUDGET_PER_CLASS)]
    # give each probe a distinct id so nothing is deduped
    for n, e in enumerate(entries):
        e["id"] = f"r{n}"
    action = decide.next_action(_session(tmp_path, entries))
    assert action.action == "park_and_switch"
    assert action.detail["requests_sent"] >= decide.BUDGET_PER_CLASS
    assert action.vuln_class in decide.PROBE_CLASS.values()


def test_a_class_with_a_recorded_finding_is_not_parked(tmp_path):
    entries = [_exchange("r0", "http://t/s?q=1")]
    entries += [_exchange(f"p{i}", "http://t/s?q=1", tool=t)
                for t in decide._FIRST_PASS
                for i in range(decide.BUDGET_PER_CLASS)]
    for n, e in enumerate(entries):
        e["id"] = f"r{n}"
    findings = [{"id": f"F{n}", "vuln_class": c, "grade": "proven",
                 "url": "http://t/s?q=1", "evidence_ids": [],
                 "proof": {"missing": []}}
                for n, c in enumerate(decide.PROBE_CLASS[t]
                                      for t in decide._FIRST_PASS)]
    action = decide.next_action(_session(tmp_path, entries, findings))
    assert action.action != "park_and_switch"


# --- rule 6 / 7: the exits --------------------------------------------------

def test_one_endpoint_and_a_finding_asks_to_widen(tmp_path):
    entries = [_exchange("r0", "http://t/s?q=1")]
    entries += [_exchange(f"p{i}", "http://t/s?q=1", tool=t)
                for i, t in enumerate(decide._FIRST_PASS)]
    for n, e in enumerate(entries):
        e["id"] = f"r{n}"
    findings = [{"id": "F01", "vuln_class": "sqli", "grade": "proven",
                 "url": "http://t/s?q=1", "evidence_ids": [],
                 "proof": {"missing": []}}]
    action = decide.next_action(_session(tmp_path, entries, findings))
    assert action.action == "widen_surface"


def test_a_fully_probed_surface_with_no_gap_says_report(tmp_path):
    entries = []
    for ep in ("http://t/a?q=1", "http://t/b?q=1"):
        entries.append(_exchange(f"base{ep}", ep))
        for tool in decide._FIRST_PASS:
            entries.append(_exchange(f"{ep}{tool}", ep, tool=tool))
    for n, e in enumerate(entries):
        e["id"] = f"r{n}"
    findings = [{"id": "F01", "vuln_class": "sqli", "grade": "proven",
                 "url": "http://t/a?q=1", "evidence_ids": [],
                 "proof": {"missing": []}}]
    action = decide.next_action(_session(tmp_path, entries, findings))
    assert action.action == "report", action.render()
    assert action.detail["endpoints"] == 2


# --- the shape of the answer -----------------------------------------------

def test_every_action_names_an_observation(tmp_path):
    cases = [
        _session(tmp_path / "a", []),
        _session(tmp_path / "b", [_exchange("r1", "http://t/s?q=1")]),
        _session(tmp_path / "c", [_exchange("r1", "http://t/s?q=1")],
                 [{"id": "F01", "vuln_class": "xss", "grade": "candidate",
                   "url": "http://t/s?q=1", "evidence_ids": ["r1"],
                   "proof": {"missing": ["a real browser executed it"]}}]),
    ]
    for sdir in cases:
        sdir.parent.mkdir(parents=True, exist_ok=True)
        action = decide.next_action(sdir)
        assert action.why and action.why[0].islower() or action.why[0].isupper()
        assert len(action.why) > 30, f"{action.action}: {action.why!r}"
        assert action.to_dict()["action"] == action.action
        assert action.render().startswith("NEXT: ")


def test_every_mapped_probe_tool_exists():
    from argus.tools import registry
    known = {t["name"] for t in registry.TOOL_SCHEMAS}
    for tool in decide.PROBE_CLASS:
        assert tool in known, f"{tool} is mapped but is not a tool"


def test_every_mapped_class_is_in_the_proof_matrix():
    from argus import proof
    for tool, klass in decide.PROBE_CLASS.items():
        assert (proof.spec_for(klass) is not None
                or klass in proof.CANDIDATE_ONLY), (
            f"{tool} -> {klass!r} is not a class the matrix knows")


def test_the_first_pass_tools_are_all_mapped():
    for tool in decide._FIRST_PASS:
        assert tool in decide.PROBE_CLASS


def test_the_tool_handler_returns_the_same_action(tmp_path):
    import types
    from argus.tools import analysis
    sdir = _session(tmp_path, [_exchange("r1", "http://t/s?q=1")])
    ctx = types.SimpleNamespace(session=types.SimpleNamespace(dir=sdir))
    out = analysis.next_action(ctx)
    assert out["action"] == decide.next_action(sdir).action
    assert "conversation" in out["note"]


def test_the_tool_handler_survives_a_broken_controller(tmp_path, monkeypatch):
    import types
    from argus.tools import analysis

    def _boom(_sdir):
        raise RuntimeError("ledger exploded")
    monkeypatch.setattr(decide, "next_action", _boom)
    ctx = types.SimpleNamespace(
        session=types.SimpleNamespace(dir=tmp_path))
    out = analysis.next_action(ctx)
    assert "error" in out and "ledger exploded" in out["error"]


# --- what the adversarial audit found in this module -----------------------

def test_the_ledger_cost_is_bounded_by_the_window_not_the_run():
    """Rule 1 re-grades transcript exchanges, and an audit measured one call
    at over five minutes: the cap bounded how many exchanges it looked at,
    but each one was graded line by line against the WHOLE transcript, and
    `_pairs` makes that quadratic. It now cites a local window, so the cost
    is flat in the length of the run."""
    import json
    import pathlib
    import tempfile
    import time

    def session(n):
        d = pathlib.Path(tempfile.mkdtemp())
        rows = [json.dumps({
            "id": f"r{i}", "tool": "probe_sqli",
            "request": {"method": "GET", "url": f"http://t/item?id={i}",
                        "headers": {}, "body": None},
            "response": {"status": 200, "headers": {},
                         "body": "\n".join(f"line {j} of some text"
                                           for j in range(30))}})
                for i in range(n)]
        d.joinpath("transcript.jsonl").write_text("\n".join(rows),
                                                  encoding="utf-8")
        d.joinpath("findings.json").write_text("[]", encoding="utf-8")
        return d

    timings = {}
    for n in (200, 2000):
        sdir = session(n)
        start = time.monotonic()
        decide.next_action(sdir)
        timings[n] = time.monotonic() - start
    # ten times the transcript must not cost appreciably more
    assert timings[2000] < timings[200] * 3 + 1.0, timings


def test_the_ledger_does_not_invent_parameter_names():
    """`'=' in body` admitted XML prologs, SQL and multipart preambles, so
    `_params` produced names like `<?xml version` and
    `SELECT 1 FROM t WHERE a`, and the ledger recommended probing them."""
    def req(body):
        return {"id": "r1",
                "request": {"method": "POST", "url": "http://t/x",
                            "headers": {}, "body": body},
                "response": {"status": 200, "headers": {}, "body": ""}}
    for body in ('<?xml version="1.0"?><a>1</a>',
                 '{"a":"b=c"}',
                 "SELECT 1 FROM t WHERE a=1",
                 '--b\r\nContent-Disposition: form-data; name="f"'):
        assert decide._params(req(body)) == set(), body
    assert decide._params(req("user=admin&pass=x")) == {"user", "pass"}
    assert decide._params(req("q=hello+world&page=2")) == {"q", "page"}


def test_rule_one_does_not_shop_for_a_verdict(tmp_path):
    """It tried every line of a response until one graded `proven`. A page
    that returns no rows must not become a recommended sqli finding however
    many lines it has."""
    body = "\n".join([
        "<html><body><h1>Search</h1>",
        "No results for: ' UNION SELECT username, password FROM users --",
        "<p>Try a different term</p></body></html>"])
    sdir = _session(tmp_path, [
        _exchange("r1", "http://t/search?q=x", body=body, tool="probe_sqli")])
    action = decide.next_action(sdir)
    assert action.action != "record_finding", action.render()


def test_the_ledger_does_not_say_report_about_a_run_that_probed_nothing():
    """Rule 7 is the only exit and it was reachable from a single fetch of a
    root page: no parameterised surface so rules 3-5 pass, no findings so
    rule 6 passes, and the ledger said "write the report" about a run that
    had tested nothing."""
    import json
    import pathlib
    import tempfile
    sdir = pathlib.Path(tempfile.mkdtemp())
    sdir.joinpath("transcript.jsonl").write_text(json.dumps({
        "id": "r1", "tool": "http_request",
        "request": {"method": "GET", "url": "http://t/", "headers": {},
                    "body": None},
        "response": {"status": 200, "headers": {},
                     "body": "<html>home</html>"}}) + "\n", encoding="utf-8")
    sdir.joinpath("findings.json").write_text("[]", encoding="utf-8")
    action = decide.next_action(sdir)
    assert action.action == "recon", action.render()
    assert "probed" in action.why


def test_the_class_budget_is_counted_in_the_unit_it_is_documented_in():
    """It counted recorded REQUESTS while being documented as probes, and one
    `probe_sqli` call records about eleven - so a single call spent 220% of
    the budget and rule 5 recommended parking a class nobody had finished."""
    assert decide.BUDGET_PER_CLASS == (decide.REQUESTS_PER_PROBE
                                       * decide.PROBE_CALLS_PER_CLASS)
    assert decide.PROBE_CALLS_PER_CLASS >= 5
    assert decide.REQUESTS_PER_PROBE >= 10
