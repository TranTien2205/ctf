"""End-to-end checks for the offline `argus demo` CLI path."""
import json

from argus.cli import main


def test_demo_single(tmp_path):
    rc = main(["demo", "--session-dir", str(tmp_path), "--quiet"])
    assert rc == 0
    (sdir,) = [d for d in tmp_path.iterdir() if d.is_dir()]
    findings = json.loads((sdir / "findings.json").read_text())
    cats = {f["category"] for f in findings}
    assert {"sqli", "xss", "idor", "info-disclosure", "jwt"} <= cats
    assert (sdir / "report.md").exists()
    html = (sdir / "report.html").read_text(encoding="utf-8")
    assert "F01" in html and "sqlite3" in html
    sarif = json.loads((sdir / "report.sarif").read_text())
    run = sarif["runs"][0]
    assert sarif["version"] == "2.1.0"
    assert len(run["results"]) == len(findings)
    assert {r["ruleId"] for r in run["results"]} >= {"CWE-89", "CWE-347"}


def test_demo_team(tmp_path):
    rc = main(["demo", "--session-dir", str(tmp_path), "--quiet", "--team"])
    assert rc == 0
    (sdir,) = [d for d in tmp_path.iterdir() if d.is_dir()]
    findings = json.loads((sdir / "findings.json").read_text())
    cats = {f["category"] for f in findings}
    assert {"sqli", "xss", "idor", "info-disclosure", "jwt"} <= cats
    assert all(f.get("agent") for f in findings)  # credited to a worker
    agents = json.loads((sdir / "summary.json").read_text())["agents"]
    assert "lead" in agents and "exploit-1" in agents


def test_sessions_listing(tmp_path, capsys):
    rc = main(["demo", "--session-dir", str(tmp_path), "--quiet"])
    assert rc == 0
    sdir = next(p for p in tmp_path.iterdir() if p.is_dir())
    n = len(json.loads((sdir / "findings.json").read_text(encoding="utf-8")))
    rc = main(["sessions", "--session-dir", str(tmp_path)])
    assert rc == 0
    out = capsys.readouterr().out
    assert f"findings={n}" in out


def test_sessions_json(tmp_path, capsys):
    rc = main(["demo", "--session-dir", str(tmp_path), "--quiet"])
    assert rc == 0
    capsys.readouterr()
    rc = main(["sessions", "--session-dir", str(tmp_path), "--json"])
    assert rc == 0
    rows = json.loads(capsys.readouterr().out)
    assert len(rows) == 1
    row = rows[0]
    sdir = next(p for p in tmp_path.iterdir() if p.is_dir())
    n = len(json.loads((sdir / "findings.json").read_text(encoding="utf-8")))
    assert row["findings"] == n and row["mode"] == "single"
    assert row["requests"] > 0 and "dir" in row and "duration" in row


def test_compare_two_sessions(tmp_path, capsys):
    """The thesis comparison table must print metrics for both runs."""
    rc = main(["demo", "--session-dir", str(tmp_path), "--quiet"])
    assert rc == 0
    (sdir,) = [d for d in tmp_path.iterdir() if d.is_dir()]
    other = tmp_path / "b"
    rc = main(["demo", "--session-dir", str(other), "--quiet", "--team"])
    assert rc == 0
    (tdir,) = [d for d in other.iterdir() if d.is_dir()]
    capsys.readouterr()
    rc = main(["compare", str(sdir), str(tdir)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "findings" in out and "llm_calls" in out
    assert "single" in out and "team" in out
    rc = main(["compare", str(sdir), str(tdir), "--csv"])
    assert rc == 0
    csv_out = capsys.readouterr().out
    assert csv_out.splitlines()[0].startswith("session,mode,findings")
    assert len([l for l in csv_out.splitlines() if l.strip()]) == 3


def test_report_fence_cant_be_broken(tmp_path):
    """Evidence containing ``` must not break out of its code fence - a
    target could otherwise inject fake report sections (finding spoof)."""
    from argus.report.markdown import _fence, _code
    evil = "before\n```\n# FAKE CRITICAL FINDING\n```\nafter"
    f = _fence(evil)
    assert f == "````"  # one longer than the longest ```-run
    block = f"{f}\n{evil}\n{f}"
    # every fence in the block is the long one - the inner ``` can't close it
    assert block.count("````") == 2
    assert "```\n# FAKE" in block  # payload stays literal inside the fence
    assert _code("http://x/?a=1") == "`http://x/?a=1`"
    assert _code("has`tick").startswith("`` ")


def test_finding_carries_cwe(tmp_path):
    """Category -> canonical CWE auto-mapped for audit-grade reports;
    unknown categories just omit the field."""
    from argus.session import _cwe_of
    assert _cwe_of("sqli") == "CWE-89"
    assert _cwe_of("info-disclosure") == "CWE-200"
    assert _cwe_of("open redirect") == "CWE-601"
    assert _cwe_of("something-else") == ""
    rc = main(["demo", "--session-dir", str(tmp_path), "--quiet"])
    assert rc == 0
    (sdir,) = [d for d in tmp_path.iterdir() if d.is_dir()]
    findings = json.loads((sdir / "findings.json").read_text())
    cwes = {f["category"]: f.get("cwe") for f in findings}
    assert cwes["sqli"] == "CWE-89" and cwes["jwt"] == "CWE-347"
    assert "CWE-89" in (sdir / "report.md").read_text()


def test_finding_carries_owasp(tmp_path):
    """CWE -> OWASP Top 10 (2021) bucket: findings, md summary table,
    html and sarif all carry the taxonomy audit reports speak in."""
    from argus.session import _owasp_of
    assert _owasp_of("CWE-89") == "A03 Injection"
    assert _owasp_of("CWE-918") == "A10 SSRF"
    assert _owasp_of("CWE-999") == ""
    rc = main(["demo", "--session-dir", str(tmp_path), "--quiet"])
    assert rc == 0
    (sdir,) = [d for d in tmp_path.iterdir() if d.is_dir()]
    findings = json.loads((sdir / "findings.json").read_text())
    ow = {f["category"]: f.get("owasp") for f in findings}
    assert ow["sqli"] == "A03 Injection" and ow["jwt"] == \
        "A02 Cryptographic Failures"
    md = (sdir / "report.md").read_text()
    assert "OWASP Top 10 (2021)" in md and "A03 Injection" in md
    sarif = json.loads((sdir / "report.sarif").read_text())
    assert sarif["runs"][0]["results"][0]["properties"]["owasp"]


def test_tools_allowlist_validation(capsys):
    """--tools: bad names fail fast with the valid list; good names are
    restricted to exactly those tools (finish auto-included)."""
    import pytest
    from argus.cli import _parse_tools
    assert _parse_tools("") is None
    allowed = _parse_tools("probe_sqli, http_request ,record_finding")
    assert allowed == frozenset(
        {"probe_sqli", "http_request", "record_finding", "finish"})
    with pytest.raises(SystemExit):
        _parse_tools("probe_sqli,nosuchtool")


def test_reopen_report_findings_verify(tmp_path, capsys):
    """Regression: _reopen must restore lock/chain/started so the offline
    commands work on an existing session dir."""
    rc = main(["demo", "--session-dir", str(tmp_path), "--quiet"])
    assert rc == 0
    (sdir,) = [d for d in tmp_path.iterdir() if d.is_dir()]
    (sdir / "report.md").unlink()
    rc = main(["report", str(sdir)])
    assert rc == 0
    text = (sdir / "report.md").read_text(encoding="utf-8")
    assert "Duration" in text
    # `"1970" not in text` is what this asserted, and it failed on CI
    # (windows 3.11) against a report that was perfectly correct: the lab
    # binds an ephemeral port, the finding URL was `127.0.0.1:51970/item`,
    # and `51970` contains `1970`. The epoch bug this guards against shows
    # up in ONE place - the rendered Date line - so look there. An
    # assertion that reads like a precise claim and is really a substring
    # search over a whole document fails on correct output, which is worse
    # than not asserting.
    date_line = next((l for l in text.splitlines()
                      if l.startswith("- **Date:**")), "")
    assert date_line, text[:200]
    assert "1970-" not in date_line, date_line
    rc = main(["verify", str(sdir)])
    assert rc == 0
    rc = main(["findings", str(sdir)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "SQL injection" in out


def test_dotenv_whitelists_keys(tmp_path, monkeypatch):
    """A .env inside an untrusted cwd must not redirect trust:
    ANTHROPIC_BASE_URL would exfiltrate the API key to a hostile gateway
    and ARGUS_MCP_CONFIG names subprocesses to run - both stay refused,
    while plain credentials still load."""
    import os
    from argus.config import _load_dotenv
    (tmp_path / ".env").write_text(
        "ANTHROPIC_BASE_URL=https://evil.example\n"
        "ARGUS_MCP_CONFIG=mcp.json\n"
        "ANTHROPIC_API_KEY=sk-test-ok\n"
        "ARGUS_MODEL=m1\n", encoding="utf-8")
    for k in ("ANTHROPIC_BASE_URL", "ARGUS_MCP_CONFIG",
              "ANTHROPIC_API_KEY", "ARGUS_MODEL"):
        monkeypatch.delenv(k, raising=False)
    _load_dotenv(tmp_path / ".env")
    assert "ANTHROPIC_BASE_URL" not in os.environ
    assert "ARGUS_MCP_CONFIG" not in os.environ
    assert os.environ["ANTHROPIC_API_KEY"] == "sk-test-ok"
    assert os.environ["ARGUS_MODEL"] == "m1"


def _synth_session(tmp_path, name, target, findings=None, version="1.0.0"):
    """Minimal session dir: meta.json + findings.json + summary.json."""
    d = tmp_path / name
    d.mkdir(parents=True)
    (d / "meta.json").write_text(
        json.dumps({"target": target}), encoding="utf-8")
    (d / "findings.json").write_text(
        json.dumps(findings or []), encoding="utf-8")
    (d / "summary.json").write_text(json.dumps({
        "mode": "single", "counts": {"findings": len(findings or [])},
        "argus_version": version,
        "requests_total": 1}), encoding="utf-8")
    return d


def _finding(url):
    return {"category": "xss", "title": "t", "endpoint": url,
            "url": url, "severity": "medium", "evidence": "e",
            "evidence_excerpt": "e"}


def test_diff_warns_on_different_hosts(tmp_path, capsys):
    a = _synth_session(tmp_path, "a", "http://a.example",
                       [_finding("http://a.example/x?p=1")])
    b = _synth_session(tmp_path, "b", "http://b.example",
                       [_finding("http://b.example/x?p=1")])
    rc = main(["diff", str(a), str(b)])
    err = capsys.readouterr().err
    assert rc == 0 and "targets differ" in err


def test_diff_same_host_new_port_matches(tmp_path, capsys):
    """Retest scenario: same host, port changed -> keying still matches."""
    a = _synth_session(tmp_path, "a", "http://a.example",
                       [_finding("http://a.example/x?p=1")])
    b = _synth_session(tmp_path, "b", "http://a.example:8443",
                       [_finding("http://a.example:8443/x?p=1")])
    rc = main(["diff", str(a), str(b)])
    cap = capsys.readouterr()
    assert rc == 0
    assert "targets differ" not in cap.err and "STILL" in cap.out


def test_compare_warns_on_different_hosts(tmp_path, capsys):
    a = _synth_session(tmp_path, "a", "http://a.example")
    b = _synth_session(tmp_path, "b", "http://b.example")
    rc = main(["compare", str(a), str(b)])
    err = capsys.readouterr().err
    assert rc == 0 and "targets differ" in err


def test_compare_same_target_no_warning(tmp_path, capsys):
    a = _synth_session(tmp_path, "a", "http://a.example")
    b = _synth_session(tmp_path, "b", "http://a.example:8443")
    rc = main(["compare", str(a), str(b)])
    err = capsys.readouterr().err
    assert rc == 0 and "targets differ" not in err


def test_compare_warns_on_different_versions(tmp_path, capsys):
    """Metric deltas across builds are not like-for-like either."""
    a = _synth_session(tmp_path, "a", "http://a.example", version="1.0.0")
    b = _synth_session(tmp_path, "b", "http://a.example", version="0.9.0")
    rc = main(["compare", str(a), str(b)])
    err = capsys.readouterr().err
    assert rc == 0 and "argus versions differ" in err


def test_sessions_lists_version(tmp_path, capsys):
    root = tmp_path / "sessions"
    _synth_session(root, "s1", "http://a.example", version="1.0.0")
    rc = main(["sessions", "--session-dir", str(root)])
    out = capsys.readouterr().out
    assert rc == 0 and "v1.0.0" in out


def test_both_demo_paths_match_what_the_evaluation_doc_claims(tmp_path):
    """`docs/EXPERIMENTS.md` states the offline reproduction numbers - 6
    findings on both paths, 5 `proven` and one honest `candidate` - and uses
    them as the shape every measured run is compared against. Nothing checked
    them, which is how the same document came to claim nine unreachable
    classes when there were three.

    Both paths run offline against the bundled lab, so this is cheap and
    deterministic. If the demo legitimately changes, change the doc in the
    same commit; the point is that the two cannot drift apart silently.
    """
    import collections
    import json
    import pathlib
    import re

    from argus.cli import main

    doc = (pathlib.Path(__file__).resolve().parent.parent
           / "docs" / "EXPERIMENTS.md").read_text(encoding="utf-8")
    claim = re.search(r"(\d+) findings on both paths, (\d+) of them "
                      r"`proven` and one an\s+honest `candidate`", doc)
    assert claim, "docs/EXPERIMENTS.md no longer states the demo numbers"
    want_total, want_proven = int(claim.group(1)), int(claim.group(2))

    for args in ([], ["--team"]):
        out = tmp_path / ("team" if args else "single")
        assert main(["demo", *args, "--session-dir", str(out)]) == 0
        sessions = sorted(p for p in out.iterdir() if p.is_dir())
        assert len(sessions) == 1, sessions
        rows = json.loads((sessions[0] / "findings.json")
                          .read_text(encoding="utf-8"))
        grades = collections.Counter(r.get("grade") for r in rows)
        label = "team" if args else "single"
        assert len(rows) == want_total, f"{label}: {len(rows)} findings"
        assert grades["proven"] == want_proven, f"{label}: {dict(grades)}"
        assert grades["candidate"] == want_total - want_proven, \
            f"{label}: {dict(grades)}"


def _fake_session(root, arm, trial, *, proven, requests=10, usd=0.5,
                  summary=True):
    """A session dir in the layout docs/EXPERIMENTS.md lays out.

    `exp/<arm>-<trial>/<session>`: the arm is the parent directory with the
    trial suffix stripped, which is what `compare --by-arm` groups on.
    """
    sdir = root / f"{arm}-{trial}" / "20260101-000000-127.0.0.1"
    sdir.mkdir(parents=True)
    (sdir / "meta.json").write_text(
        json.dumps({"target": "http://127.0.0.1:8000"}), encoding="utf-8")
    if summary:
        (sdir / "summary.json").write_text(json.dumps({
            "mode": arm, "argus_version": "1.0.0",
            "findings": [{"grade": "proven"}] * proven,
            "grades": {"proven": proven, "candidate": 0, "unproven": 0},
            "requests": requests, "duration_s": 3.0,
            "time_to_first_finding_s": 0.5,
            "coverage": {"endpoints": ["/a", "/b"]},
            "llm_calls": 4,
            "llm_tokens": {"in": 100, "out": 20,
                           "cache_read": 0, "cache_write": 0},
            "llm_cost": {"usd": usd},
        }), encoding="utf-8")
    return sdir


def test_by_arm_groups_trials_and_reports_the_median_with_the_spread(
        tmp_path, capsys):
    """EXPERIMENTS asks for medians per configuration; this computes them.

    Three single trials at 1, 5 and 9 proven and two team trials at 2 and 8:
    the medians are 5 and 2, and both arms print their min-max so a median
    cannot hide a bimodal arm.
    """
    for trial, proven in enumerate([1, 5, 9], start=1):
        _fake_session(tmp_path, "single", trial, proven=proven)
    for trial, proven in enumerate([2, 8], start=1):
        _fake_session(tmp_path, "team", trial, proven=proven)
    dirs = [str(p) for a in sorted(tmp_path.iterdir()) for p in a.iterdir()]
    capsys.readouterr()
    assert main(["compare", "--by-arm", *dirs]) == 0
    out = capsys.readouterr().out
    assert "single (n=3)" in out and "team (n=2)" in out
    line = next(ln for ln in out.splitlines()
                if ln.startswith("proven findings"))
    assert "5  [1-9]" in line, line
    # median_low on an even N: 2 is a count a trial produced, 5.0 is not
    assert "2  [2-8]" in line, line
    assert "5.0" not in line


def test_by_arm_median_never_reports_a_figure_no_trial_produced(
        tmp_path, capsys):
    """An even N must not average the middle two.

    This system's claim is that it does not invent numbers, and a mean of
    two trials is a number no run of the tool ever measured.
    """
    for trial, reqs in enumerate([40, 60], start=1):
        _fake_session(tmp_path, "single", trial, proven=1, requests=reqs)
    dirs = [str(p) for a in sorted(tmp_path.iterdir()) for p in a.iterdir()]
    capsys.readouterr()
    assert main(["compare", "--by-arm", *dirs]) == 0
    line = next(ln for ln in capsys.readouterr().out.splitlines()
                if ln.startswith("wire requests"))
    assert "40" in line and "50" not in line, line


def test_by_arm_says_so_when_an_arm_has_a_single_trial(tmp_path, capsys):
    _fake_session(tmp_path, "single", 1, proven=3)
    sdir = next(next(tmp_path.iterdir()).iterdir())
    capsys.readouterr()
    # one arm is allowed: the two-dir guard belongs to the A/B table
    assert main(["compare", "--by-arm", str(sdir)]) == 0
    out = capsys.readouterr().out
    assert "n=1 for single" in out and "no median" in out


def test_by_arm_reports_no_cost_unless_every_trial_in_the_arm_is_priced(
        tmp_path, capsys):
    """A median over the priced subset would describe part of the arm.

    It would still print under `cost (usd)`, read as the arm's cost, and be
    wrong by however many trials ran an unpriced model.
    """
    _fake_session(tmp_path, "single", 1, proven=1, usd=0.4)
    _fake_session(tmp_path, "single", 2, proven=1, usd=None)
    _fake_session(tmp_path, "team", 1, proven=1, usd=0.8)
    _fake_session(tmp_path, "team", 2, proven=1, usd=0.6)
    dirs = [str(p) for a in sorted(tmp_path.iterdir()) for p in a.iterdir()]
    capsys.readouterr()
    assert main(["compare", "--by-arm", *dirs]) == 0
    line = next(ln for ln in capsys.readouterr().out.splitlines()
                if ln.startswith("cost (usd)"))
    cells = line[len("cost (usd)"):].split()
    assert cells[0] == "-", line          # single: one trial unpriced
    assert cells[1].startswith("0.6"), line   # team: both priced


def test_by_arm_warns_about_a_trial_with_no_summary(tmp_path, capsys):
    """A dir with no summary.json counts toward N and skews every median."""
    _fake_session(tmp_path, "single", 1, proven=5)
    _fake_session(tmp_path, "single", 2, proven=5, summary=False)
    dirs = [str(p) for a in sorted(tmp_path.iterdir()) for p in a.iterdir()]
    capsys.readouterr()
    assert main(["compare", "--by-arm", *dirs]) == 0
    cap = capsys.readouterr()
    assert "no summary.json" in cap.err
    assert "single (1)" in cap.err
    assert "single (n=2)" in cap.out


def test_by_arm_csv_is_one_row_per_arm_and_metric(tmp_path, capsys):
    for trial, proven in enumerate([1, 5, 9], start=1):
        _fake_session(tmp_path, "single", trial, proven=proven)
    dirs = [str(p) for a in sorted(tmp_path.iterdir()) for p in a.iterdir()]
    capsys.readouterr()
    assert main(["compare", "--by-arm", "--csv", *dirs]) == 0
    rows = capsys.readouterr().out.splitlines()
    assert rows[0] == "arm,n,metric,median,min,max"
    assert "single,3,proven,5,1,9" in rows


def test_compare_does_not_crash_on_a_dir_with_no_summary(tmp_path, capsys):
    """`sorted({"1.0.0", None})` raises, and a missing summary.json gave None.

    Found while adding `--by-arm`; the A/B table had the same crash, so a
    comparison against an interrupted run died with a TypeError from the
    version warning instead of reporting what it had.
    """
    a = _fake_session(tmp_path, "single", 1, proven=4)
    b = _fake_session(tmp_path, "single", 2, proven=4, summary=False)
    capsys.readouterr()
    assert main(["compare", str(a), str(b)]) == 0
    assert "findings" in capsys.readouterr().out


def test_by_arm_excludes_a_trial_that_ended_in_an_error(tmp_path, capsys):
    """A run that died is not a measurement.

    Measured on a real failed run: an `Anthropic API error 400` on the first
    call produced a SEALED session that `argus verify` calls OK, carrying
    `findings: []`, `grades: {}`, `requests: 0` and `cost: 0.0` - and the
    terminal error reached only `agent.log`. `compare` reads summary.json,
    so that run folded into its arm as a trial with zero proven: paired with
    one real trial that found four, `median_low([0, 4])` reported **0**.

    It is excluded and NAMED now. Dropping it silently would be the same
    defect one level up.
    """
    dead = _fake_session(tmp_path, "single", 1, proven=0, requests=0)
    live = _fake_session(tmp_path, "single", 2, proven=4, requests=61)
    payload = json.loads((dead / "summary.json").read_text(encoding="utf-8"))
    payload["error"] = "Anthropic API error 400: invalid_request_error"
    (dead / "summary.json").write_text(json.dumps(payload), encoding="utf-8")

    capsys.readouterr()
    assert main(["compare", "--by-arm", str(dead), str(live)]) == 0
    cap = capsys.readouterr()
    assert "ended in an error" in cap.err
    assert "Anthropic API error 400" in cap.err
    # the label must say a trial was dropped, not just report a smaller n
    assert "1 failed" in cap.out, cap.out
    line = next(ln for ln in cap.out.splitlines()
                if ln.startswith("proven findings"))
    assert "4" in line and not line.split()[2:3] == ["0"], line


def test_a_run_that_dies_records_the_error_in_its_summary():
    """The artifact said nothing was wrong.

    `_last_error` reached `agent.log` and the loop's return value, and never
    `summary.json` - so a run that never completed one API call was
    indistinguishable from a clean run that found nothing, for any reader
    who did not open the log. `compare`, `sessions` and the report all read
    summary.json.
    """
    import inspect
    from argus import loop as loop_mod
    src = inspect.getsource(loop_mod)
    assert '"error": self._last_error or None}))' in src, (
        "the summary extra must carry the terminal error")


def test_every_reader_of_a_dead_run_says_so(tmp_path, capsys):
    """One reader learning the lesson is the half-fix shape again.

    `compare --by-arm` was taught to exclude a failed trial. `sessions`,
    the A/B table, the CSV and the report all read the same summary.json and
    had not been: each rendered a run that died on its first API call as a
    clean, sealed run with nothing found - `findings=0 requests=0 sealed`.
    """
    dead = _fake_session(tmp_path, "single", 1, proven=0, requests=0)
    payload = json.loads((dead / "summary.json").read_text(encoding="utf-8"))
    payload["error"] = "Anthropic API error 400: no extra usage"
    (dead / "summary.json").write_text(json.dumps(payload), encoding="utf-8")

    capsys.readouterr()
    assert main(["sessions", "--session-dir", str(dead.parent)]) == 0
    out = capsys.readouterr().out
    assert "FAILED" in out and "400" in out, out

    assert main(["sessions", "--session-dir", str(dead.parent), "--json"]) == 0
    rows = json.loads(capsys.readouterr().out)
    assert rows and rows[0].get("error"), rows

    live = _fake_session(tmp_path, "team", 1, proven=3)
    assert main(["compare", str(dead), str(live)]) == 0
    table = capsys.readouterr().out
    assert "FAILED" in table.splitlines()[2], table.splitlines()[:4]

    assert main(["compare", "--csv", str(dead), str(live)]) == 0
    csv_out = capsys.readouterr().out
    assert csv_out.splitlines()[0].rstrip().endswith("error"), csv_out
    assert "Anthropic API error 400" in csv_out


def test_the_report_warns_before_the_numbers_not_after(tmp_path):
    """A reader must be told before reading the findings table.

    A dead run's report was indistinguishable from a clean one: 0 requests,
    0 findings, an empty table. The warning sits above every figure because
    each of them describes a run that may not have happened.
    """
    from argus.config import Config
    from argus.report.markdown import render_report
    from argus.session import Session

    sess = Session(tmp_path, "http://127.0.0.1:8777", meta={"t": 1})
    cfg = Config(target="http://127.0.0.1:8777", allow_private=True,
                 session_dir=tmp_path)
    path = render_report(sess, cfg, "", extra={
        "mode": "single", "llm_calls": 0,
        "llm_tokens": {"in": 0, "out": 0, "cache_read": 0, "cache_write": 0},
        "llm_cost": {"usd": 0.0},
        "error": "Anthropic API error 400: no extra usage"})
    text = path.read_text(encoding="utf-8")
    assert "RUN DID NOT COMPLETE" in text
    # ...and above the findings section, not buried under it
    assert text.index("RUN DID NOT COMPLETE") < text.index("Requests sent") \
        or text.index("RUN DID NOT COMPLETE") < len(text) // 2, text[:400]
    # a clean run must not grow the banner
    clean = render_report(sess, cfg, "", extra={
        "mode": "single", "llm_calls": 1,
        "llm_tokens": {"in": 10, "out": 2, "cache_read": 0, "cache_write": 0},
        "llm_cost": {"usd": 0.0}, "error": None})
    assert "RUN DID NOT COMPLETE" not in clean.read_text(encoding="utf-8")
