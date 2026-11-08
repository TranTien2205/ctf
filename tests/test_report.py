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
