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
