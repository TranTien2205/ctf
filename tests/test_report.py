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


def test_a_file_added_after_sealing_is_named(tmp_path, capsys):
    """The seal covered a whitelist and nothing compared the directory to it.

    `seal_artifacts` enumerates the files at seal time -
    `self.dir.glob("agent*.log")` among them - and `verify_transcript` only
    iterated the names it recorded. So a file created afterwards was
    invisible, INCLUDING one matching that glob exactly: an
    `agent-ghost.log` dropped into a sealed session verified clean, `ok`
    True, under a human line reading "artifacts sealed" that names nothing.
    Only `--json` ever printed the covered set.

    Reported rather than failed, and deliberately: `ok` means the chain is
    intact and the sealed bytes still match, and an addition breaks
    neither - an operator may legitimately leave a screenshot beside the
    run. What it must not do is pass unmentioned while wearing the name of
    covered output. Measured on a real `argus demo`, the directory holds
    exactly the sealed files plus transcript.jsonl, which the hash chain
    covers instead - so this check has no legitimate occupant to cry wolf
    over.
    """
    from argus.cli import main
    from argus.session import verify_transcript

    assert main(["demo", "--session-dir", str(tmp_path), "--quiet"]) == 0
    sdir = next(p for p in tmp_path.iterdir() if p.is_dir())

    clean = verify_transcript(sdir)
    # `chained`, not `ok`: `ok` is computed by the CLI for its --json
    # output, and `verify_transcript` does not return it
    assert clean["chained"] and clean.get("sealed")
    assert not clean.get("unsealed_additions"), (
        "a freshly sealed session must have nothing to report: "
        f"{clean.get('unsealed_additions')}")
    # transcript.jsonl is covered by the chain, not the artifact digest, so
    # it must not be reported as an addition
    assert "transcript.jsonl" not in (clean.get("unsealed_additions") or [])

    (sdir / "agent-ghost.log").write_text("ghost", encoding="utf-8")
    after = verify_transcript(sdir)
    assert after.get("unsealed_additions") == ["agent-ghost.log"], after
    # the chain and the sealed bytes are untouched, so this is a note
    assert after["chained"] and not after.get("artifact_mismatch")

    capsys.readouterr()
    assert main(["verify", str(sdir)]) == 0
    out = capsys.readouterr()
    assert "agent-ghost.log" in out.err, (
        "the human output said 'artifacts sealed' and named nothing: "
        f"{out.out!r} / {out.err!r}")
    assert "added after sealing" in out.err, out.err


def test_a_reseal_over_a_mismatch_survives_the_reseal(tmp_path, capsys):
    """That a re-render re-seals is documented and accepted. Its invisibility was not.

    docs/ARCHITECTURE.md states the residual: "`argus report` recomputes
    the artifact digests, which is what makes a legitimate re-render verify
    - and therefore what lets an edit made before the re-render come out
    the other side digest-valid." The mitigations named there are real: the
    grade is recomputed from the transcript, and `--seal-key` closes the
    forgery case.

    What was missing is that the only signal of the edit was a stderr line
    at render time. Afterwards `argus verify` printed OK and named nothing,
    so a reader of the session later could not see that a mismatch had ever
    been there - which is the difference between an accepted residual and a
    hidden one.

    The transcript is an append-only hash chain, so an event recorded at
    re-render time cannot be removed without breaking the chain. That makes
    it the one place a durable note can go. This does not close the
    residual; it stops it being silent.
    """
    import json

    from argus.cli import main
    from argus.session import verify_transcript

    assert main(["demo", "--session-dir", str(tmp_path), "--quiet"]) == 0
    sdir = next(p for p in tmp_path.iterdir() if p.is_dir())

    before = verify_transcript(sdir)
    assert before["chained"] and not before.get("artifact_mismatch")
    assert not before.get("resealed_over_mismatch"), (
        "a clean session must carry no such record")

    fp = sdir / "findings.json"
    rows = json.loads(fp.read_text(encoding="utf-8"))
    # the TITLE, because the first finding of the demo may already carry
    # whatever severity a test picks - a first version set
    # `severity = "critical"` on a row that was already critical, wrote the
    # same bytes back, and asserted a mismatch that never happened
    rows[0]["title"] = rows[0]["title"] + " (edited by hand)"
    fp.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    assert fp.read_text(encoding="utf-8") != "", fp

    tampered = verify_transcript(sdir)
    assert tampered.get("artifact_mismatch") == ["findings.json"], tampered

    capsys.readouterr()
    assert main(["report", str(sdir)]) == 0
    assert "edited since the run was sealed" in capsys.readouterr().err

    after = verify_transcript(sdir)
    # the seal matches again - that is the documented part
    assert not after.get("artifact_mismatch"), after
    # ...and the chain remembers that it did not
    rec = after.get("resealed_over_mismatch")
    assert rec, (
        "the re-render re-sealed over an edit and left nothing saying so")
    assert "findings.json" in rec[0]["files"], rec
    assert after["chained"], "the record must not break the chain"

    capsys.readouterr()
    assert main(["verify", str(sdir)]) == 0
    out = capsys.readouterr()
    assert "re-sealed while" in out.err and "findings.json" in out.err, (
        f"`argus verify` did not name it: {out.out!r} / {out.err!r}")


def test_a_partial_team_total_says_it_is_partial(tmp_path):
    """A team total is the sum of the agents that COULD be priced.

    The cost line printed it as the run's cost and read `unpriced` only on
    the branch where there is no figure at all - so a reader saw a definite
    number with nothing saying it covered part of the run.

    The sweep refused this as a state no run can reach, and that was true
    of the tree at the time: it needed an agent whose MODEL is absent from
    the table, which the spawn path cannot produce. Making a crashed worker
    unpriced earlier in this stretch - because pricing its missing tokens
    at $0.00 was worse - is what made it reachable. A fix that creates the
    precondition for another finding has to close it too, which is the
    whole reason this test exists.
    """
    from argus.config import Config
    from argus.session import Session
    from argus.report.markdown import render_report
    from pathlib import Path

    def cost_line(cost, name):
        cfg = Config(target="http://127.0.0.1:9", allow_private=True,
                     session_dir=tmp_path / name)
        s = Session(tmp_path / name, cfg.target, {})
        render_report(s, cfg, summary="", extra={
            "llm_cost": cost,
            "llm_tokens": {"in": 200_000, "out": 7_000, "cache_read": 0}})
        return next(l for l in (Path(s.dir) / "report.md")
                    .read_text(encoding="utf-8").splitlines()
                    if "Model cost" in l)

    whole = cost_line({"usd": 0.014, "table_version": 2, "unpriced": []},
                      "whole")
    assert "$0.0140 USD" in whole and "PARTIAL" not in whole, whole

    partial = cost_line(
        {"usd": 0.014, "table_version": 2,
         "unpriced": ["exploit-1 (no token record: RuntimeError: boom)"]},
        "partial")
    assert "$0.0140 USD" in partial, partial
    assert "PARTIAL" in partial, (
        "the priced subset's total was printed as the run's cost with "
        f"nothing saying so: {partial}")
    assert "exploit-1" in partial, partial

    # and the no-figure branch still names its reason, as before
    none_line = cost_line({"usd": None, "basis": "nothing to price"}, "none")
    assert "not priced - nothing to price" in none_line, none_line


def test_the_target_line_names_what_was_tested_not_the_directory(tmp_path):
    """MEASURED ACROSS EVERY SEALED SESSION IN THE REPOSITORY, 0 of 5 right.

    The Target line was `session.dir.name.split('-', 2)[-1]`, so the
    report's claim about WHAT WAS TESTED - the authorisation boundary in a
    system whose whole premise is authorised testing - was parsed out of a
    filename:

        directory          meta.json                   rendered
        sample-session     http://127.0.0.1:43673      "session"
        argus-lab          http://192.168.223.221:8777 "lab"
        argus-lab-team     http://192.168.223.221:8777 "team"
        dvwa               http://192.168.223.221:8081 "dvwa"
        bwapp              http://192.168.223.221:8080 "bwapp"

    The two that look right drop the scheme and the port. It was correct
    only by coincidence of the live naming convention, and a directory that
    is renamed, copied or moved - which is what re-rendering a checked-in
    example does - names a target that was never tested.

    Found by re-rendering the committed reference session rather than by
    reading the renderer: the bug is invisible while the directory still
    carries the host.
    """
    from argus.report.markdown import _target_of

    class _S:
        dir = tmp_path / "20261116-043207-127.0.0.1"

    assert _target_of(_S(), {"target": "http://127.0.0.1:43673"}) == \
        "http://127.0.0.1:43673"
    # the derivation would have produced the host without scheme or port
    assert _target_of(_S(), {"target": "http://10.0.0.9:8080"}) == \
        "http://10.0.0.9:8080", "a recorded target must win over the path"


def test_a_target_with_no_record_says_it_was_derived(tmp_path):
    """The fallback must not pass itself off as a recorded fact.

    Printing nothing would be worse than printing the convention, so the
    parse stays - but a reader has to be able to tell a target the run
    recorded from one this renderer inferred, which is the same rule as
    every other absence in these reports.
    """
    from argus.report.markdown import _target_of

    class _S:
        dir = tmp_path / "20261116-043207-10.1.1.5"

    for meta in ({}, None, {"target": ""}, {"target": "   "}):
        out = _target_of(_S(), meta)
        assert "10.1.1.5" in out, out
        assert "directory name" in out, \
            "a derived target that looks recorded is the defect restated"


def test_two_sessions_against_one_target_render_one_target(tmp_path):
    """THE STRUCTURAL FORM, and it is stronger than the 0-of-5 tally.

    `argus-lab` and `argus-lab-team` are two sealed sessions in this
    repository with ONE recorded target, `http://192.168.223.221:8777` -
    two runs against the same application. Under
    `session.dir.name.split('-', 2)[-1]` they rendered "lab" and "team".

    So the defect did not merely mangle a label: it MANUFACTURED A
    DISTINCTION THE EVIDENCE DOES NOT CONTAIN, presenting one target as
    two. The directory name cannot be the target even in principle here,
    because the mapping is not one-to-one - which is why this assertion
    fails on the name-split for a structural reason rather than a cosmetic
    one.

    Raised by the session that owns the console, which checked its own
    renderer for the same bug (it reads `r.target`, 4 of 4 exact) and then
    pointed out that this pair makes the fix unarguable.
    """
    from argus.report.markdown import _target_of

    one_target = "http://192.168.223.221:8777"

    class _Lab:
        dir = tmp_path / "argus-lab"

    class _Team:
        dir = tmp_path / "argus-lab-team"

    rendered = {_target_of(_Lab(), {"target": one_target}),
                _target_of(_Team(), {"target": one_target})}
    assert rendered == {one_target}, (
        "two runs against one target rendered as "
        f"{sorted(rendered)} - the report invents a distinction the "
        "evidence does not contain")


def test_the_grading_claim_states_the_count_when_a_row_is_ungraded():
    """MEASURED BY PLANTING, in the deliverable's own prose.

    The report printed, four lines apart:

        | **ungraded** | 1 | recorded before grading existed |
        Every finding is graded against the proof requirement for its class

    A universal claim and, in the same document, a count contradicting it.
    `ungraded` is a real bucket in `_GRADE_MEANING` - "recorded before
    grading existed" - so a resumed session or a findings.json from an older
    version holds rows the matrix never graded.

    A number cannot quietly become false, which is the property this whole
    system is built to have, so the sentence now carries one.
    """
    from argus.report.markdown import _grade_line

    rows = [{"grade": "proven"}, {"grade": "candidate"}, {"id": "F03"}]
    line = _grade_line(rows)
    assert "2 of 3" in line, line
    assert "1 carries no grade" in line, line
    assert "Every finding is graded" not in line
    assert "never as a verdict" in line, \
        "an ungraded row must not read as a claim about its evidence"


def test_the_grading_claim_stays_universal_when_it_is_true():
    """The direction that keeps the fix from hedging a true statement.

    With every row graded the universal sentence is correct, and replacing
    it with a count would make a true claim read as a qualified one.
    """
    from argus.report.markdown import _grade_line

    for rows in ([{"grade": "proven"}], [{"grade": "refused"},
                                         {"grade": "unproven"}], [], None):
        line = _grade_line(rows)
        assert line == ("Every finding is graded against the proof "
                        "requirement for its class"), (rows, line)


def test_the_citation_claims_are_left_universal():
    """DELIBERATELY NOT WEAKENED, and the distinction is the point.

    The two neighbouring claims are about CITATION, and those are enforced:
    `add_finding` refuses an excerpt that is not a verbatim substring of a
    cited response, and `findings_bad` re-validates every one on re-read.
    Grading is the one that can be absent, so it is the only sentence that
    needed a number.
    """
    import pathlib

    src = (pathlib.Path(__file__).resolve().parent.parent / "argus" /
           "report" / "markdown.py").read_text(encoding="utf-8")
    assert "_All findings cite verbatim response excerpts verified" in src
    assert "_grade_line(findings)" in src, \
        "the grading sentence must be the computed one"


def test_a_plural_count_reads_correctly():
    from argus.report.markdown import _grade_line

    line = _grade_line([{"grade": "proven"}, {"id": "a"}, {"id": "b"}])
    assert "1 of 3" in line and "2 carry no grade" in line, line


def test_every_artifact_reports_the_same_findings(tmp_path):
    """THE CLASS OF DEFECT PER-FINDING VERIFICATION CANNOT SEE, asserted.

    Each of the three verification layers answers a question about ONE
    finding: did the target produce these bytes, do they demonstrate this
    class, does the target still do it. None of them can see a relation
    BETWEEN findings - so a store holding two rows for one bug, or a
    renderer dropping one row, passes every per-finding check while the
    deliverable is wrong.

    Both failure modes have occurred in this project. Two rows for one bug:
    a REST path subject keyed separately from a query-string subject, so an
    engagement against N enumerable subjects produced N findings. One row
    dropped: a console filter that rendered one of ten findings.

    Nothing asserted the relation. This does: every artifact must report the
    same count, carry every finding id, and the summary's severity tally
    must equal the findings' own severities.
    """
    import json
    import re

    from argus.cli import main

    assert main(["demo", "--session-dir", str(tmp_path), "--quiet"]) == 0
    # the demo writes into a timestamped SUBDIRECTORY, as the tests above do
    sdir = next(q for q in tmp_path.iterdir() if q.is_dir())

    findings = json.loads((sdir / "findings.json").read_text(
        encoding="utf-8"))
    ids = [str(f.get("id")) for f in findings]
    assert len(ids) >= 2, "premise: the demo records more than one finding"

    summary = json.loads((sdir / "summary.json").read_text(
        encoding="utf-8"))
    sarif = json.loads((sdir / "report.sarif").read_text(
        encoding="utf-8"))
    md = (sdir / "report.md").read_text(encoding="utf-8")
    html = (sdir / "report.html").read_text(encoding="utf-8")

    counted = {
        "summary.json": len(summary.get("findings") or []),
        "report.sarif": len(sarif.get("runs", [{}])[0].get("results", [])),
        "report.md": len(re.findall(r"^#{2,4}\s*F\d+\b", md, re.M)),
    }
    for name, n in counted.items():
        assert n == len(ids), (
            f"{name} reports {n} findings, findings.json holds {len(ids)}")

    for fid in ids:
        assert fid in md, f"{fid} is missing from report.md"
        assert fid in html, f"{fid} is missing from report.html"

    from collections import Counter
    own = dict(Counter(str(f.get("severity")) for f in findings))
    assert summary.get("counts") == own, (
        f"summary.json tallies {summary.get('counts')} against the "
        f"findings' own {own}")


def test_the_bug_bounty_artifact_carries_every_finding(tmp_path):
    """Rendered on request rather than by the run, so it is checked
    separately - and it is the artifact that leaves the building."""
    import json
    import pathlib
    import re

    from argus.cli import _reopen, main
    from argus.config import Config
    from argus.report.hackerone import render_hackerone

    assert main(["demo", "--session-dir", str(tmp_path), "--quiet"]) == 0
    sdir = next(q for q in tmp_path.iterdir() if q.is_dir())
    findings = json.loads((sdir / "findings.json").read_text(
        encoding="utf-8"))
    summary = json.loads((sdir / "summary.json").read_text(
        encoding="utf-8"))

    # THE SESSION DIRECTORY, not its parent, and the target from meta.json,
    # which is where it lives - summary.json has no such key. Reopening the
    # parent gave a session with no transcript, so the page rendered with no
    # findings on it, and the first version of this test read that as the
    # renderer dropping them. The diagnosis was wrong twice before the line
    # numbers settled it.
    meta = json.loads((sdir / "meta.json").read_text(encoding="utf-8"))
    session = _reopen(sdir, "")
    path = render_hackerone(
        session, Config(target=str(meta.get("target") or "http://t/")),
        "summary")
    page = pathlib.Path(path).read_text(encoding="utf-8")

    # COMPARED IN THE FORM IT APPEARS. One demo title contains angle
    # brackets, which the page escapes - correctly, since a report that
    # emitted a finding title raw would be an injection hole in the
    # deliverable. The first version asserted the raw title, so it was
    # asking the renderer NOT to escape.
    import html as _html

    for f in findings:
        title = str(f.get("title") or "")
        assert title, f"{f.get('id')} has no title"
        assert title in page or _html.escape(title) in page, \
            f"{f.get('id')} ({title[:40]}) is missing from report-h1.html"
    assert len(re.findall(r"PROOF:", page)) == len(findings)


def test_a_cross_host_diff_says_so_on_stdout_and_in_json(tmp_path, capsys):
    """MEASURED, and found by a grep of mine that lied.

    A diff across hosts reads every finding as fixed AND new, because the
    two runs are different applications rather than a retest. The code knew
    that and warned - on stderr. Stdout carried "N fixed, 0 still present,
    N new" with nothing saying why, and a diff is normally captured by
    redirecting stdout, so whoever reads the file sees a retraction of N
    findings and N discoveries as if they were facts about the world.

    The JSON carried both targets, from which a reader could INFER it.
    Inference is not a statement, and a machine consumer comparing hostnames
    is doing the tool's work.

    An earlier pass of mine concluded stdout already said it, because a
    grep for host-related words matched two lines - both of them the word
    "host" inside a finding TITLE. Twentieth wrong instrument in this
    session and the mirror of the worst one: that nearly published a false
    positive, this nearly retracted a real finding.
    """
    import json

    from argus.cli import main

    before = tmp_path / "b"
    after = tmp_path / "a"
    assert main(["demo", "--session-dir", str(before), "--quiet"]) == 0
    assert main(["demo", "--session-dir", str(after), "--quiet"]) == 0
    bdir = next(q for q in before.iterdir() if q.is_dir())
    adir = next(q for q in after.iterdir() if q.is_dir())

    # make the two runs look like different hosts, in meta only
    meta = json.loads((adir / "meta.json").read_text(encoding="utf-8"))
    meta["target"] = "http://other.test:8080"
    (adir / "meta.json").write_text(json.dumps(meta), encoding="utf-8")

    capsys.readouterr()
    assert main(["diff", str(bdir), str(adir)]) == 0
    out = capsys.readouterr()
    assert "targets differ" in out.out, \
        "the caveat reaches stderr only; a redirected diff loses it"
    assert "fixed AND new" in out.out

    capsys.readouterr()
    assert main(["diff", str(bdir), str(adir), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload.get("cross_host") is True, \
        "a machine reader should not have to compare hostnames itself"


def test_a_same_host_diff_is_not_qualified(tmp_path, capsys):
    """The direction that keeps the caveat off an ordinary retest, where it
    would teach a reader to ignore it."""
    import json

    from argus.cli import main

    before = tmp_path / "b"
    after = tmp_path / "a"
    assert main(["demo", "--session-dir", str(before), "--quiet"]) == 0
    assert main(["demo", "--session-dir", str(after), "--quiet"]) == 0
    bdir = next(q for q in before.iterdir() if q.is_dir())
    adir = next(q for q in after.iterdir() if q.is_dir())

    capsys.readouterr()
    assert main(["diff", str(bdir), str(adir)]) == 0
    out = capsys.readouterr()
    assert "targets differ" not in out.out
    assert "targets differ" not in out.err

    capsys.readouterr()
    assert main(["diff", str(bdir), str(adir), "--json"]) == 0
    assert json.loads(capsys.readouterr().out).get("cross_host") is False
