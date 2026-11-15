"""Report rendering invariants."""


def test_report_excludes_tampered_findings(tmp_path, capsys):
    """`argus report` must not re-render claims whose evidence fails
    re-validation against the chained transcript."""
    import json
    from argus.cli import main
    assert main(["demo", "--session-dir", str(tmp_path), "--quiet"]) == 0
    sdir = next(p for p in tmp_path.iterdir() if p.is_dir())
    fp = sdir / "findings.json"
    data = json.loads(fp.read_text(encoding="utf-8"))
    data.append({"id": "F99", "title": "FAKE", "severity": "critical",
                 "category": "sqli", "url": "http://x/",
                 "evidence_ids": ["r999"], "evidence_excerpt": "invented",
                 "description": "x", "remediation": "x"})
    fp.write_text(json.dumps(data), encoding="utf-8")
    assert main(["report", str(sdir)]) == 0
    err = capsys.readouterr().err
    assert "F99" in err and "re-validation" in err
    rep = (sdir / "report.md").read_text(encoding="utf-8")
    assert "F99" not in rep and "F01" in rep
    # `argus findings` keeps the forensic listing but flags the bad row
    assert main(["findings", str(sdir)]) == 0
    out = capsys.readouterr()
    assert "F99" in out.err
    assert "UNVERIFIED" in out.out


def test_sealed_artifacts_detect_edits(tmp_path):
    """After a run seals, editing findings/meta/summary must fail verify;
    a legitimate `argus report` re-render must not."""
    import json
    from argus.cli import main
    from argus.session import verify_transcript
    assert main(["demo", "--session-dir", str(tmp_path), "--quiet"]) == 0
    sdir = next(p for p in tmp_path.iterdir() if p.is_dir())
    res = verify_transcript(sdir)
    assert res["chained"] and not res.get("artifact_mismatch")
    # re-render is legitimate - digests skip the mutable head/duration
    assert main(["report", str(sdir)]) == 0
    assert not verify_transcript(sdir).get("artifact_mismatch")
    # editing findings.json is not (byte-exact restore: artifacts are
    # LF-pinned so a digest holds across platforms)
    fp = sdir / "findings.json"
    orig = fp.read_bytes()
    d = json.loads(orig)
    d[0]["severity"] = "low" if d[0]["severity"] != "low" else "high"
    fp.write_bytes(json.dumps(d, indent=2, ensure_ascii=False).encode())
    assert verify_transcript(sdir)["artifact_mismatch"] == ["findings.json"]
    fp.write_bytes(orig)
    assert not verify_transcript(sdir).get("artifact_mismatch")


def test_verify_json_output(tmp_path, capsys):
    """`argus verify --json` prints the machine-readable verdict and maps
    the same failures to the exit code."""
    import json
    from argus.cli import main
    assert main(["demo", "--session-dir", str(tmp_path), "--quiet"]) == 0
    sdir = next(p for p in tmp_path.iterdir() if p.is_dir())
    capsys.readouterr()  # flush demo output before reading --json stdout
    assert main(["verify", str(sdir), "--json"]) == 0
    res = json.loads(capsys.readouterr().out)
    recorded = len(json.loads((sdir / "findings.json").read_text(encoding="utf-8")))
    assert res["ok"] and res["chained"] and res["findings_checked"] == recorded
    assert "findings.json" in res["sealed"]
    # tamper -> ok flips false and rc goes 1
    fp = sdir / "findings.json"
    orig = fp.read_bytes()
    d = json.loads(orig)
    d[0]["severity"] = "low"
    fp.write_text(json.dumps(d, indent=2), encoding="utf-8")
    assert main(["verify", str(sdir), "--json"]) == 1
    res = json.loads(capsys.readouterr().out)
    assert not res["ok"] and res["artifact_mismatch"] == ["findings.json"]


def test_diff_retest(tmp_path, capsys):
    """`argus diff` matches findings across fresh instances (different
    ports) by class+host+path+params and reports fixed/still/new."""
    import json
    from argus.cli import main
    assert main(["demo", "--session-dir", str(tmp_path), "--quiet"]) == 0
    s1 = next(p for p in tmp_path.iterdir() if p.is_dir())
    other = tmp_path / "retest"
    assert main(["demo", "--session-dir", str(other), "--quiet"]) == 0
    s2 = next(p for p in other.iterdir() if p.is_dir())
    capsys.readouterr()
    assert main(["diff", str(s1), str(s2)]) == 0
    out = capsys.readouterr().out
    n = len(json.loads((s1 / "findings.json").read_text(encoding="utf-8")))
    assert f"0 fixed, {n} still present, 0 new" in out
    # drop one finding from the "after" session -> shows FIXED
    fp = s2 / "findings.json"
    d = json.loads(fp.read_text(encoding="utf-8"))
    fp.write_text(json.dumps(d[1:], indent=2), encoding="utf-8")
    assert main(["diff", str(s1), str(s2), "--json"]) == 0
    res = json.loads(capsys.readouterr().out)
    assert len(res["fixed"]) == 1 and len(res["still_present"]) == n - 1


def test_report_flags_bogus_severity(tmp_path, capsys):
    """A finding whose evidence still verifies but whose severity was
    inflated is corrupt metadata - findings_bad must flag it so report/
    findings/diff all warn instead of trusting the row."""
    import json
    from argus.cli import main
    assert main(["demo", "--session-dir", str(tmp_path), "--quiet"]) == 0
    sdir = next(p for p in tmp_path.iterdir() if p.is_dir())
    fp = sdir / "findings.json"
    data = json.loads(fp.read_text(encoding="utf-8"))
    data[0]["severity"] = "apocalyptic"   # valid evidence, bogus severity
    fp.write_text(json.dumps(data), encoding="utf-8")
    assert main(["findings", str(sdir)]) == 0
    out = capsys.readouterr()
    assert "UNVERIFIED" in out.out
    # and report excludes the row rather than rendering it
    assert main(["report", str(sdir)]) == 0
    assert "apocalyptic" not in (sdir / "report.md").read_text()


def test_cli_tolerates_corrupt_session_files(tmp_path, capsys):
    """forensic commands must not traceback on damaged session dirs -
    verify/report decide trust; the CLI's job is to read what it can."""
    import json
    from argus.cli import main
    d = tmp_path / "corrupt"
    d.mkdir()
    (d / "transcript.jsonl").write_text(
        '{"id":"r1","chain":"x"}\nGARBAGE\n{"id":7}\n', encoding="utf-8")
    # non-list findings.json -> clean refusal, not a traceback
    (d / "findings.json").write_text('{"x": 1}', encoding="utf-8")
    assert main(["findings", str(d)]) == 1
    assert "not a findings list" in capsys.readouterr().out
    # invalid JSON -> same
    (d / "findings.json").write_text("NOT JSON", encoding="utf-8")
    assert main(["findings", str(d)]) == 1
    # finding missing severity -> listed as UNVERIFIED, no crash
    (d / "findings.json").write_text(json.dumps(
        [{"id": "F1", "title": "t", "url": "u",
          "evidence_ids": [], "evidence_excerpt": "x"}]), encoding="utf-8")
    assert main(["findings", str(d)]) == 0
    assert "UNVERIFIED" in capsys.readouterr().out


def test_verify_tolerates_nonregular_artifact(tmp_path):
    """A directory swapped in for a sealed file is tamper, not a traceback:
    verify must flag it in artifact_mismatch and carry on."""
    import shutil
    from argus.cli import main
    from argus.session import verify_transcript
    assert main(["demo", "--session-dir", str(tmp_path), "--quiet"]) == 0
    sdir = next(p for p in tmp_path.iterdir() if p.is_dir())
    (sdir / "findings.json").unlink()
    (sdir / "findings.json").mkdir()
    res = verify_transcript(sdir)
    assert "findings.json" in res.get("artifact_mismatch", [])
    # transcript.jsonl itself swapped for a directory -> clean error, no crash
    sdir2 = tmp_path / "weird"
    (sdir2 / "transcript.jsonl").mkdir(parents=True)
    res2 = verify_transcript(sdir2)
    assert "not a regular file" in res2.get("error", "")


def test_report_refuses_non_session_dir(tmp_path, capsys):
    """`argus report` must not fabricate a sealed session out of an empty
    directory - refuse before render/seal."""
    import json
    from argus.cli import main
    empty = tmp_path / "nothing"
    empty.mkdir()
    assert main(["report", str(empty)]) == 1
    assert "not a session dir" in capsys.readouterr().out
    assert not (empty / "report.md").exists()
    assert not (empty / "summary.json").exists()


def test_sarif_does_not_fail_ci_on_a_candidate(tmp_path):
    """SARIF `level` is meaningful only when `kind` is "fail". A candidate
    ingested as an error would fail a build on evidence the project itself
    grades as incomplete."""
    import json
    from argus.cli import main
    assert main(["demo", "--session-dir", str(tmp_path), "--quiet"]) == 0
    sdir = next(p for p in tmp_path.iterdir() if p.is_dir())
    doc = json.loads((sdir / "report.sarif").read_text(encoding="utf-8"))
    results = doc["runs"][0]["results"]
    assert results, "demo produced no sarif results"
    by_grade = {}
    for r in results:
        by_grade.setdefault(r["properties"]["argus-grade"], []).append(r)
    assert "proven" in by_grade and "candidate" in by_grade, by_grade.keys()
    for r in by_grade["proven"]:
        assert r["kind"] == "fail"
        assert r["level"] in ("error", "warning", "note")
    for r in by_grade["candidate"]:
        assert r["kind"] == "review"
        assert r["level"] == "none"
        assert r["message"]["text"].startswith("[CANDIDATE]")
        assert r["properties"]["argus-proof-missing"]
    # proven results sort first, so a reader who stops early reads proof
    grades = [r["properties"]["argus-grade"] for r in results]
    assert grades == sorted(grades, key=lambda g: g != "proven")


def test_html_report_shows_the_grade(tmp_path):
    """report.html is the file handed to a reader in a presentation; it
    carried no grade while report.md did."""
    from argus.cli import main
    assert main(["demo", "--session-dir", str(tmp_path), "--quiet"]) == 0
    sdir = next(p for p in tmp_path.iterdir() if p.is_dir())
    html = (sdir / "report.html").read_text(encoding="utf-8")
    assert "Proof grades" in html
    assert "PROOF: PROVEN" in html
    assert "PROOF: CANDIDATE" in html
    assert "a real browser executed it" in html


def test_verify_rejects_an_inflated_grade_even_after_a_rerender(tmp_path):
    """The artifact seal is recomputed by a legitimate re-render, so a grade
    edited before one is no longer a byte mismatch. Re-grading is what still
    catches it."""
    import json
    from argus.cli import main
    assert main(["demo", "--session-dir", str(tmp_path), "--quiet"]) == 0
    sdir = next(p for p in tmp_path.iterdir() if p.is_dir())
    assert main(["verify", str(sdir)]) == 0
    fp = sdir / "findings.json"
    data = json.loads(fp.read_text(encoding="utf-8"))
    touched = False
    for f in data:
        if f.get("grade") == "candidate":
            f["grade"] = "proven"
            touched = True
    assert touched, "demo recorded no candidate to inflate"
    fp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    assert main(["report", str(sdir)]) == 0          # launders the seal
    assert main(["verify", str(sdir)]) == 1


def test_a_rerender_keeps_the_executive_summary(tmp_path):
    """`argus report` replaced the agent's summary with "_No agent summary was
    recorded._" and then re-sealed, so the delivered artifact was worse than
    the original and digest-valid."""
    import json
    from argus.cli import main
    assert main(["demo", "--session-dir", str(tmp_path), "--quiet"]) == 0
    sdir = next(p for p in tmp_path.iterdir() if p.is_dir())
    first = (sdir / "report.md").read_text(encoding="utf-8")
    assert "_No agent summary was recorded._" not in first
    summary = json.loads((sdir / "summary.json").read_text(encoding="utf-8"))
    assert summary["agent_summary"].startswith("Demo run")
    assert main(["report", str(sdir)]) == 0
    again = (sdir / "report.md").read_text(encoding="utf-8")
    assert "_No agent summary was recorded._" not in again
    assert summary["agent_summary"][:60] in again
    assert main(["verify", str(sdir)]) == 0


def test_an_ungraded_row_appears_in_the_grade_table(tmp_path):
    """It rendered as a card with no line in the table that is supposed to
    summarise the cards."""
    import json
    from argus.cli import main
    assert main(["demo", "--session-dir", str(tmp_path), "--quiet"]) == 0
    sdir = next(p for p in tmp_path.iterdir() if p.is_dir())
    fp = sdir / "findings.json"
    rows = json.loads(fp.read_text(encoding="utf-8"))
    rows.append({"id": "F99", "title": "legacy row", "severity": "high",
                 "category": "sqli", "url": "http://x/",
                 "evidence_ids": rows[0]["evidence_ids"],
                 "evidence_excerpt": rows[0]["evidence_excerpt"],
                 "description": "x", "remediation": "x"})
    fp.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    assert main(["report", str(sdir)]) == 0
    html = (sdir / "report.html").read_text(encoding="utf-8")
    assert "F99" in html
    assert "UNGRADED" in html


def test_a_rerender_of_a_keyed_session_keeps_the_chain(tmp_path):
    """`argus report` re-seals, so chaining the seal entry unkeyed over a
    keyed transcript would break the chain this command exists to preserve."""
    import threading
    from argus.cli import main
    from argus.config import Config
    from argus.httpclient import GuardedClient
    from argus.ratelimit import RateLimiter
    from argus.scope import ScopeGuard
    from argus.session import Session
    import sys as _sys
    from pathlib import Path as _P
    _sys.path.insert(0, str(_P(__file__).resolve().parent.parent / "lab"))
    import vulnapp
    srv = vulnapp.make_server(0)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    key = "engagement-key-2026"
    try:
        scope = ScopeGuard(base, allow_private=True)
        s = Session(tmp_path, base, meta={"chain_keyed": True}, seal_key=key)
        client = GuardedClient(scope, s, RateLimiter(0), tls_verify=False,
                               max_requests=10)
        try:
            client.send("GET", base + "/", tool="t")
        finally:
            client.close()
        s.seal_artifacts()
        assert main(["verify", str(s.dir), "--seal-key", key]) == 0
        # without the key, verify refuses rather than crying tamper
        assert main(["verify", str(s.dir)]) == 1
        # a re-render with the key keeps it verifying
        assert main(["report", str(s.dir), "--seal-key", key]) == 0
        assert main(["verify", str(s.dir), "--seal-key", key]) == 0
    finally:
        srv.shutdown()


def test_a_session_with_no_start_stamp_reports_unknown_not_1970(tmp_path):
    """Two figures in the header were computed from a start time of zero.

    `_reopen` initialises `started` to 0.0 and only overwrites it when
    meta.json exists, parses, and carries a truthy `started` - and that
    `except: pass` is deliberate, so a damaged session is still reportable.
    summary.json is written BY this renderer, so on the FIRST report of such
    a session both sources were absent and the header printed
    `Date: 1970-01-01 00:00:00` and a duration of `time.time() - 0.0`:
    about 1.76e9 seconds, roughly fifty-six years, in a report whose whole
    job is to be checkable.

    Saying "unknown" is the only honest answer, and summary.json carries
    null rather than a number so a reader can tell "no measurable time"
    from "nothing recorded when it began".
    """
    import json
    from argus.cli import main

    assert main(["demo", "--session-dir", str(tmp_path), "--quiet"]) == 0
    sdir = next(p for p in tmp_path.iterdir() if p.is_dir())

    meta = json.loads((sdir / "meta.json").read_text(encoding="utf-8"))
    meta.pop("started", None)
    (sdir / "meta.json").write_text(json.dumps(meta), encoding="utf-8")
    (sdir / "summary.json").unlink()          # as on a first render

    assert main(["report", str(sdir)]) == 0
    report = (sdir / "report.md").read_text(encoding="utf-8")
    assert "1970" not in report, "a start time of zero reached the header"
    assert "- **Date:** unknown" in report
    assert "- **Duration:** unknown" in report
    assert json.loads(
        (sdir / "summary.json").read_text(encoding="utf-8")
    )["duration_s"] is None

    # ...and a healthy session still reports real figures, or this has just
    # made every report say "unknown"
    fresh = tmp_path / "fresh"
    assert main(["demo", "--session-dir", str(fresh), "--quiet"]) == 0
    fdir = next(p for p in fresh.iterdir() if p.is_dir())
    healthy = (fdir / "report.md").read_text(encoding="utf-8")
    assert "- **Date:** unknown" not in healthy
    assert "- **Duration:** unknown" not in healthy


def _rendered(tmp_path, *, error="", dispute=False):
    """One rendered session, so three artifacts can be compared side by side."""
    import json
    from argus.config import Config
    from argus.session import Session
    from argus.report.markdown import render_report
    from pathlib import Path
    cfg = Config(target="http://127.0.0.1:9", allow_private=True,
                 session_dir=tmp_path)
    s = Session(tmp_path, cfg.target, meta={"t": True})
    if dispute:
        s.findings = [{
            "id": "F01", "severity": "high", "title": "SQLi in q",
            "category": "sqli", "url": "http://127.0.0.1:9/s",
            "grade": "proven", "description": "d", "remediation": "r",
            "evidence_excerpt": "root:x:0:0", "evidence_ids": [],
            "vuln_class": "sqli", "proof": {"checks": []},
            "disputed": True, "severity_claimed": "critical",
            "class_disputed": "disclosure",
            "judge": {"judge_model": "gpt-5-mini", "agrees": False,
                      "reason": "only one response is cited",
                      "missing": ["a benign-input control"]}}]
    render_report(s, cfg, summary="",
                  extra={"error": error} if error else {})
    d = Path(s.dir)
    return {
        "md": (d / "report.md").read_text(encoding="utf-8"),
        "html": (d / "report.html").read_text(encoding="utf-8"),
        "sarif": json.loads((d / "report.sarif").read_text(encoding="utf-8")),
    }


def test_a_run_that_died_is_not_a_clean_assessment_in_ANY_artifact(tmp_path):
    """"A dead run looks clean" was fixed in one reader out of three.

    `render_html` took `extra` in its signature and read it nowhere in its
    body, while `render_report` passed it in. Measured before this test
    existed: the same session rendered with `extra["error"]` set exactly as
    `loop.py` sets it, and without, produced two report.html files
    IDENTICAL after normalising the session id and timestamps. The dead
    run's page said "No findings recorded." and footered "every finding
    cites verbatim response bytes verified against the recorded
    transcript". report.md differed correctly by its banner.

    `render_sarif` was worse: it was not even given `extra`, and wrote the
    literal `executionSuccessful: True` on every render. A run that died on
    authentication emitted that with `results: []`, which is the wire shape
    of a scan that completed and found nothing - and GitHub code scanning,
    Azure DevOps and most CI dashboards read exactly that field to tell
    "scanned, clean" from "scan broke".

    report.html is the file `test_report_html_is_self_contained` calls the
    one handed to a reader, and SARIF is the one a pipeline gates on. Both
    said the engagement was fine.
    """
    err = "Anthropic API error 401: invalid x-api-key"
    dead = _rendered(tmp_path / "dead", error=err)
    clean = _rendered(tmp_path / "clean")

    for name in ("md", "html"):
        assert dead[name] != clean[name], (
            f"report.{name} renders a run that died identically to a clean "
            "assessment")
        assert "RUN DID NOT COMPLETE" in dead[name], \
            f"report.{name} does not say the run died"
    assert err in dead["html"], "report.html hides which error stopped the run"

    inv = dead["sarif"]["runs"][0]["invocations"][0]
    assert inv["executionSuccessful"] is False, \
        "SARIF calls a run that died a successful scan"
    notes = inv.get("toolExecutionNotifications") or []
    assert notes and err in notes[0]["message"]["text"]
    # ...and the clean one must still read as a clean, successful scan
    ok = clean["sarif"]["runs"][0]["invocations"][0]
    assert ok["executionSuccessful"] is True
    assert not ok.get("toolExecutionNotifications")


def test_a_dispute_reaches_every_artifact_not_just_report_md(tmp_path):
    """Cross-verification exists so a disagreement reaches a human.

    `apply_verdict` writes `judges`, `judge`, `disputed`,
    `severity_claimed` and `class_disputed`. `_proof_html` read none of
    them and neither did SARIF, so a `proven` finding a second model
    disputed kept an unqualified green `PROOF: PROVEN` badge in the
    client's page - no occurrence of "disput" anywhere in the file - and
    `kind: fail` / `level: error` / `rank: 9.5` in SARIF, breaking the
    build on a finding a second model read as a different class entirely.
    A severity the judge lowered vanished the same way: the reduced value
    shown with no record it had been claimed higher.
    """
    r = _rendered(tmp_path, dispute=True)
    assert "DISPUTED" in r["md"].upper()
    for token in ("DISPUTED", "gpt-5-mini", "critical", "disclosure",
                  "only one response is cited"):
        assert token in r["html"], f"report.html drops {token!r}"

    res = r["sarif"]["runs"][0]["results"][0]
    assert res["kind"] == "review", \
        f"a disputed finding is still kind={res['kind']}"
    assert res["level"] == "none" and res["rank"] < 0, \
        "a disputed finding still breaks the build"
    p = res["properties"]
    assert p["argus-disputed"] is True
    assert p["argus-judge-model"] == "gpt-5-mini"
    assert p["argus-class-disputed"] == "disclosure"
    assert p["argus-severity-claimed"] == "critical"
    assert "DISPUTED" in res["message"]["text"]


def test_requests_sent_counts_requests_and_agrees_with_its_own_table(tmp_path):
    """Every reader printing "requests sent" read the RECORD counter.

    `_seq` is shared: `record_event` increments it too, under the same
    lock, because the id sequence has to be authoritative over the whole
    transcript. So a scanner run (two events), an `mcp_call`, a
    `jwt_forge`, an `exploit_run`, a `cross_verification` and the
    `artifacts_digest` seal all counted as traffic to the target - while
    the enforced HTTP counter, `GuardedClient.sent`, was reported nowhere.

    Measured: one request plus five offline `jwt_forge` calls gave
    `client.sent == 1` and "Requests sent: 6". The repo's own committed
    reference artifact carries it - 66 entries, 64 with a response,
    `summary.json` saying 65 - and that file is left alone, because it is
    a faithful record of a real run made by the code that produced it and
    re-sealing it would not make the run any different.

    The second assertion is the one that would have caught this without
    anyone measuring: the total and the per-tool table are computed
    separately, and they disagreed in opposite directions. `requests` is
    now derived from the transcript, so the two cannot drift.
    """
    import json
    from argus.config import Config
    from argus.session import Session
    from argus.report.markdown import render_report
    from pathlib import Path

    cfg = Config(target="http://127.0.0.1:9", allow_private=True,
                 session_dir=tmp_path)
    s = Session(tmp_path, cfg.target, {})
    for i in range(2):
        s.record_exchange(
            "http_request",
            {"method": "GET", "url": f"http://127.0.0.1:9/{i}",
             "headers": {}, "body": None},
            {"status": 200, "headers": {}, "body": "ok", "elapsed_ms": 1.0})
    for _ in range(4):                       # offline: no socket opened
        s.record_event("jwt_forge", {"claims_set": {"role": "admin"}})

    assert s._seq == 6 and s.requests_sent == 2, (s._seq, s.requests_sent)
    render_report(s, cfg, summary="", extra={})
    d = Path(s.dir)
    summary = json.loads((d / "summary.json").read_text(encoding="utf-8"))
    assert summary["requests"] == 2, summary["requests"]
    assert "- **Requests sent:** 2" in (d / "report.md").read_text(
        encoding="utf-8")
    assert "<b>Requests:</b> 2" in (d / "report.html").read_text(
        encoding="utf-8")

    by_tool = summary["coverage"]["requests_by_tool"]
    assert sum(by_tool.values()) == summary["requests"], (
        f"the total says {summary['requests']} and the per-tool table it "
        f"is printed beside sums to {sum(by_tool.values())}: {by_tool}")
    assert "jwt_forge" not in by_tool, (
        "docs/EXPERIMENTS.md documents this table as wire requests per "
        "tool, 'shows where budget went' - an offline tool spends none")


def test_the_target_does_not_choose_bytes_in_report_md_s_own_html(tmp_path):
    """report.md opens `<details><summary>` itself, and that IS parsed.

    Markdown fences and code spans are already defended here: `_fence`
    widens for a backtick run in the body and `_code` widens the span when
    a URL contains a backtick. The `<summary>` line had neither, and it is
    a raw HTML element - report.md cannot be rendered with raw HTML
    disabled, because its own collapsible transcript sections and its notes
    appendix depend on it, so any viewer that shows those also parses
    whatever the target put in the URL. The target chooses those bytes: the
    crawler follows its hrefs and the probes build URLs from its parameter
    names.

    report.html escapes the same value with `_esc`. This file had no
    equivalent, so the one artifact a reader opens in a browser was safe
    and the one they read on a forge was not.
    """
    from argus.config import Config
    from argus.session import Session
    from argus.report.markdown import render_report
    from pathlib import Path

    nasty = ('http://127.0.0.1:9/p?x="><script>alert(document.domain)'
             '</script>&b=1')
    cfg = Config(target="http://127.0.0.1:9", allow_private=True,
                 session_dir=tmp_path)
    s = Session(tmp_path, cfg.target, {})
    rid = s.record_exchange(
        "crawl", {"method": "GET", "url": nasty, "headers": {}, "body": None},
        {"status": 200, "headers": {}, "body": "root:x:0:0",
         "elapsed_ms": 2.0})
    s.add_finding(title="t", severity="high", category="sqli", url=nasty,
                  evidence_ids=[rid], evidence_excerpt="root:x:0:0",
                  description="d", remediation="r")
    render_report(s, cfg, summary="", extra={})
    md = (Path(s.dir) / "report.md").read_text(encoding="utf-8")

    summaries = [l for l in md.splitlines() if "<summary>" in l]
    assert summaries, "no transcript details block was rendered"
    for line in summaries:
        assert "<script>" not in line, f"live script tag in a <summary>: {line}"
        assert "&lt;script&gt;" in line or "script" not in line, line

    # the neighbouring defences must still hold, so a later "simplification"
    # cannot trade one for the other
    backtick = "http://127.0.0.1:9/p?x=`<img src=x onerror=alert(1)>`"
    s2 = Session(tmp_path / "two", cfg.target, {})
    rid2 = s2.record_exchange(
        "crawl", {"method": "GET", "url": backtick, "headers": {},
                  "body": None},
        {"status": 200, "headers": {}, "body": "root:x:0:0",
         "elapsed_ms": 2.0})
    s2.add_finding(title="t", severity="high", category="sqli", url=backtick,
                   evidence_ids=[rid2], evidence_excerpt="root:x:0:0",
                   description="d", remediation="r")
    render_report(s2, cfg, summary="", extra={})
    md2 = (Path(s2.dir) / "report.md").read_text(encoding="utf-8")
    endpoint = [l for l in md2.splitlines() if "**Endpoint:**" in l][0]
    assert endpoint.count("``") >= 2, (
        f"a backtick in the URL broke out of the code span: {endpoint}")


def test_no_artifact_dates_a_session_to_1970(tmp_path):
    """`started` is 0.0 when meta.json is missing, corrupt or stampless.

    `markdown.py` guards it and prints "unknown (this session's meta.json
    carries no start time)". `html.py` and `sarif.py` did not, so the same
    session dated itself `1969-12-31 19:00:00` in one artifact and
    `1970-01-01T00:00:00Z` in another - local time in one, UTC in the
    other, so the two did not even agree. The date is the field an
    authorisation reviewer checks against the window the engagement was
    authorised for, and a 1970 stamp is not a missing value a consumer can
    detect; it is a definite wrong answer.
    """
    import json
    from argus.config import Config
    from argus.session import Session
    from argus.report.markdown import render_report
    from pathlib import Path

    cfg = Config(target="http://127.0.0.1:9", allow_private=True,
                 session_dir=tmp_path)
    s = Session(tmp_path, cfg.target, {})
    s.record_exchange(
        "http_request",
        {"method": "GET", "url": "http://127.0.0.1:9/", "headers": {},
         "body": None},
        {"status": 200, "headers": {}, "body": "ok", "elapsed_ms": 1.0})
    s.started = 0.0
    render_report(s, cfg, summary="", extra={})
    d = Path(s.dir)

    md = (d / "report.md").read_text(encoding="utf-8")
    html = (d / "report.html").read_text(encoding="utf-8")
    sarif = json.loads((d / "report.sarif").read_text(encoding="utf-8"))
    for name, text in (("report.md", md), ("report.html", html)):
        assert "1970" not in text and "1969" not in text, \
            f"{name} dates the session to the epoch"
        assert "carries no start time" in text, \
            f"{name} does not say the start time is unknown"
    inv = sarif["runs"][0]["invocations"][0]
    assert "startTimeUtc" not in inv, (
        "SARIF should omit a stamp it does not have, not invent one: "
        f"{inv.get('startTimeUtc')}")


def test_constraints_are_not_asserted_from_a_file_that_was_not_read(tmp_path):
    """"TLS verify: no" and "Tool surface: all" are claims, not defaults.

    Every value in the constraints block fell back to a definite NEGATIVE,
    and `argus report` needs only transcript.jsonl, so it renders happily
    with meta.json absent. Measured on a real demo session: with meta.json
    deleted the block was identical to the one rendered with it present
    except for the budgets degrading to `?`. A run constrained by a scope
    list, an exclusion and a tool subset re-rendered as unrestricted -
    wrong in the direction of a broader, less careful test than was run,
    or for scope a narrower one than was authorised. The re-render then
    re-seals and `argus verify` prints OK and exits 0.
    """
    from argus.config import Config
    from argus.session import Session
    from argus.report.markdown import render_report
    from pathlib import Path

    cfg = Config(target="http://127.0.0.1:9", allow_private=True,
                 session_dir=tmp_path)
    s = Session(tmp_path, cfg.target, {})
    s.record_exchange(
        "http_request",
        {"method": "GET", "url": "http://127.0.0.1:9/", "headers": {},
         "body": None},
        {"status": 200, "headers": {}, "body": "ok", "elapsed_ms": 1.0})
    (Path(s.dir) / "meta.json").unlink(missing_ok=True)
    render_report(s, cfg, summary="", extra={})
    d = Path(s.dir)
    md = (d / "report.md").read_text(encoding="utf-8")
    html = (d / "report.html").read_text(encoding="utf-8")

    for name, text in (("report.md", md), ("report.html", html)):
        assert "not on record for this session" in text, \
            f"{name} states constraints from a meta.json it never read"
        assert "not recorded" in text, name
    assert "Tool surface:** all" not in md and "(target only)" not in md, md
