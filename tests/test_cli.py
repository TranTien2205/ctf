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
    rc = main(["sessions", "--session-dir", str(tmp_path)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "findings=5" in out


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
    assert "Duration" in text and "1970" not in text
    rc = main(["verify", str(sdir)])
    assert rc == 0
    rc = main(["findings", str(sdir)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "SQL injection" in out
