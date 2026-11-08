"""End-to-end checks for the offline `argus demo` CLI path."""
import json

from argus.cli import main


def test_demo_single(tmp_path):
    rc = main(["demo", "--session-dir", str(tmp_path), "--quiet"])
    assert rc == 0
    (sdir,) = [d for d in tmp_path.iterdir() if d.is_dir()]
    findings = json.loads((sdir / "findings.json").read_text())
    cats = {f["category"] for f in findings}
    assert {"sqli", "xss", "idor"} <= cats
    assert (sdir / "report.md").exists()
    html = (sdir / "report.html").read_text(encoding="utf-8")
    assert "F01" in html and "sqlite3" in html


def test_demo_team(tmp_path):
    rc = main(["demo", "--session-dir", str(tmp_path), "--quiet", "--team"])
    assert rc == 0
    (sdir,) = [d for d in tmp_path.iterdir() if d.is_dir()]
    findings = json.loads((sdir / "findings.json").read_text())
    cats = {f["category"] for f in findings}
    assert {"sqli", "xss", "idor"} <= cats
    assert all(f.get("agent") for f in findings)  # credited to a worker
    agents = json.loads((sdir / "summary.json").read_text())["agents"]
    assert "lead" in agents and "exploit-1" in agents


def test_sessions_listing(tmp_path, capsys):
    rc = main(["demo", "--session-dir", str(tmp_path), "--quiet"])
    assert rc == 0
    rc = main(["sessions", "--session-dir", str(tmp_path)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "findings=3" in out


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
