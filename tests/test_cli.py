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
    assert "Duration" in text and "1970" not in text
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
