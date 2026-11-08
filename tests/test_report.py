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
    # editing findings.json is not
    fp = sdir / "findings.json"
    orig = fp.read_text(encoding="utf-8")
    d = json.loads(orig)
    d[0]["severity"] = "low" if d[0]["severity"] != "low" else "high"
    fp.write_text(json.dumps(d, indent=2, ensure_ascii=False),
                  encoding="utf-8")
    assert verify_transcript(sdir)["artifact_mismatch"] == ["findings.json"]
    fp.write_text(orig, encoding="utf-8")
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
    assert res["ok"] and res["chained"] and res["findings_checked"] == 5
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
    assert "0 fixed, 5 still present, 0 new" in out
    # drop one finding from the "after" session -> shows FIXED
    fp = s2 / "findings.json"
    d = json.loads(fp.read_text(encoding="utf-8"))
    fp.write_text(json.dumps(d[1:], indent=2), encoding="utf-8")
    assert main(["diff", str(s1), str(s2), "--json"]) == 0
    res = json.loads(capsys.readouterr().out)
    assert len(res["fixed"]) == 1 and len(res["still_present"]) == 4
