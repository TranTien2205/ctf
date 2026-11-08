"""Evidence gating: findings only accept verbatim recorded bytes."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from argus.session import Session


def _sess(tmp_path):
    return Session(tmp_path, "http://t.local", meta={})


def test_finding_requires_verbatim_evidence(tmp_path):
    s = _sess(tmp_path)
    rid = s.record_exchange("t", {"method": "GET", "url": "http://t/x"},
                            {"status": 200, "body": "root:x:0:0 root"})
    s.add_finding("lfi", "high", "file-read", "http://t/x", [rid],
                  "root:x:0:0", "desc", "fix")
    with pytest.raises(ValueError):
        s.add_finding("bad", "high", "x", "http://t/x", [rid],
                      "invented excerpt not in body", "d", "r")


def test_finding_requires_known_ids(tmp_path):
    s = _sess(tmp_path)
    with pytest.raises(ValueError):
        s.add_finding("bad", "high", "x", "u", ["r99"], "x", "d", "r")


def test_finding_requires_some_evidence(tmp_path):
    s = _sess(tmp_path)
    with pytest.raises(ValueError):
        s.add_finding("bad", "high", "x", "u", [], "x", "d", "r")


def test_finding_autoresolves_evidence_id(tmp_path):
    s = _sess(tmp_path)
    rid = s.record_exchange("t", {}, {"status": 200, "body": "proof bytes"})
    f = s.add_finding("lfi", "high", "x", "u", [], "proof bytes", "d", "r")
    assert f["evidence_ids"] == [rid]
    with pytest.raises(ValueError):
        s.add_finding("other", "high", "y", "u", [], "not recorded", "d", "r")


def test_severity_enum(tmp_path):
    s = _sess(tmp_path)
    rid = s.record_exchange("t", {}, {"status": 200, "body": "proof"})
    with pytest.raises(ValueError):
        s.add_finding("bad", "superultra", "x", "u", [rid], "proof", "d", "r")


def test_finding_dedup_same_class_endpoint(tmp_path):
    s = _sess(tmp_path)
    rid = s.record_exchange("t", {}, {"status": 200, "body": "proof"})
    s.add_finding("sqli on /item", "high", "SQLi", "http://t/item?id=1",
                  [rid], "proof", "d", "r")
    # same bug class + same endpoint+params = duplicate, even with new evidence
    with pytest.raises(ValueError, match="duplicate of F01"):
        s.add_finding("sqli again", "medium", "sqli",
                      "http://t/item?id=2", [rid], "proof", "d", "r")
    # a different parameter IS a distinct finding
    f = s.add_finding("sqli on q", "high", "sqli", "http://t/item?q=x",
                      [rid], "proof", "d", "r")
    assert f["id"] == "F02"


def test_finding_key_tolerates_nonstr():
    # findings.json is operator-editable - a null/odd url must not crash
    # dedup or `argus diff`
    from argus.session import _finding_key
    assert _finding_key("xss", None) == ("xss", "", "/", ())
    assert _finding_key(None, 123) == ("", "123", "/", ())


def test_finding_cvss_vector_validated(tmp_path):
    s = _sess(tmp_path)
    rid = s.record_exchange("t", {}, {"status": 200, "body": "proof"})
    f = s.add_finding("sqli", "high", "sqli", "http://t/x", [rid], "proof",
                      "d", "r",
                      cvss="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H")
    assert f["cvss"].startswith("CVSS:3.1")
    with pytest.raises(ValueError):
        s.add_finding("bad", "high", "x", "u", [rid], "proof", "d", "r",
                      cvss="9.8 critical")


def test_finding_records_agent(tmp_path):
    s = _sess(tmp_path)
    rid = s.record_exchange("t", {}, {"status": 200, "body": "proof"})
    f = s.add_finding("x", "low", "c", "http://t/a", [rid], "proof", "d", "r",
                      agent="exploit-2")
    assert f["agent"] == "exploit-2"


def test_session_resume(tmp_path):
    s = Session(tmp_path, "http://t.local", meta={})
    rid = s.record_exchange("t", {}, {"status": 200, "body": "proof"})
    s.add_finding("x", "low", "sqli", "http://t/item?id=1",
                  [rid], "proof", "d", "r")

    s2 = Session(tmp_path, "http://t.local", meta={}, resume=s.dir)
    assert s2.resumed and s2.id == s.id
    assert s2.get_exchange(rid) is not None          # old evidence intact
    rid2 = s2.record_exchange("t", {}, {"status": 200, "body": "more"})
    assert rid2 == "r2"                              # ids continue, not reset
    # dedup still applies across the resume boundary
    with pytest.raises(ValueError, match="duplicate"):
        s2.add_finding("x2", "low", "sqli", "http://t/item?id=9",
                       [rid2], "more", "d", "r")
    f = s2.add_finding("new", "low", "c", "http://t/other",
                       [rid2], "more", "d", "r")
    assert f["id"] == "F02"                          # finding ids continue
    # verbatim gate also reaches back across the boundary
    f2 = s2.add_finding("cites old", "low", "lfi", "http://t/old",
                        [rid], "proof", "d", "r")
    assert f2["id"] == "F03"


def test_session_resume_wrong_target_refused(tmp_path):
    """Resuming a session recorded against a different target would mix
    two engagements' evidence - it must fail loudly."""
    s = Session(tmp_path, "http://a.local", meta={})
    with pytest.raises(ValueError, match="target"):
        Session(tmp_path, "http://b.local", meta={}, resume=s.dir)
    # same target still resumes fine
    s2 = Session(tmp_path, "http://a.local", meta={}, resume=s.dir)
    assert s2.resumed


def test_transcript_hash_chain_detects_tamper(tmp_path):
    import json
    from argus.session import Session, verify_transcript
    s = Session(tmp_path, "http://t", {})
    s.record_exchange("t", {"method": "GET", "url": "http://t/"},
                      {"status": 200, "body": "hello"})
    s.record_event("note", {"output": "ev"})
    res = verify_transcript(s.dir)
    assert res["chained"] and not res["bad_lines"] and res["entries"] == 2
    # tamper with line 1's body -> chain must flag it
    tpath = s.dir / "transcript.jsonl"
    lines = tpath.read_text().splitlines()
    e = json.loads(lines[0])
    e["response"]["body"] = "forged"
    lines[0] = json.dumps(e, ensure_ascii=False)
    tpath.write_text("\n".join(lines) + "\n")
    res = verify_transcript(s.dir)
    assert res["bad_lines"] == [1]


def test_record_finding_rejects_out_of_scope(ctx):
    from argus.tools.analysis import record_finding
    out = record_finding(ctx, title="t", severity="low", category="x",
                         url="https://evil.example/x",
                         evidence_excerpt="x", description="d",
                         remediation="r")
    assert "scope guard" in out.get("error", "")


def test_verify_revalidates_findings(tmp_path):
    """findings.json is not chained, so verify re-checks every claim
    against the (immutable) transcript: edited excerpts or invented
    evidence ids must surface as tamper."""
    import json
    from argus.session import Session, verify_transcript
    s = Session(tmp_path, "http://t", {})
    s.record_exchange("t", {"method": "GET", "url": "http://t/"},
                      {"status": 200, "body": "proof bytes here"})
    s.add_finding(title="x", severity="low", category="x",
                  url="http://t/", evidence_ids=["r1"],
                  evidence_excerpt="proof bytes",
                  description="d", remediation="r")
    res = verify_transcript(s.dir)
    assert res["findings_checked"] == 1 and not res.get("findings_bad")
    # tamper: rewrite the excerpt - the transcript is untouched yet the
    # finding no longer verifies
    fp = s.dir / "findings.json"
    fs = json.loads(fp.read_text())
    fs[0]["evidence_excerpt"] = "invented"
    fs.append({"id": "F99", "evidence_ids": ["r999"],
               "evidence_excerpt": "x", "title": "t"})
    fp.write_text(json.dumps(fs))
    res = verify_transcript(s.dir)
    assert res["findings_bad"] == ["F01", "F99"]


def test_chain_head_anchor_catches_tail_truncation(tmp_path):
    import json
    from argus.session import Session, verify_transcript
    from argus.report.markdown import render_report
    from argus.config import Config
    cfg = Config(target="http://t", allow_private=True, session_dir=tmp_path)
    s = Session(tmp_path, "http://t", {})
    s.record_exchange("t", {"method": "GET", "url": "http://t/"},
                      {"status": 200, "body": "hello"})
    s.record_event("note", {"output": "ev"})
    render_report(s, cfg)
    res = verify_transcript(s.dir)
    assert res.get("head_anchor") and not res.get("tail_truncated")
    lines = (s.dir / "transcript.jsonl").read_text().splitlines()
    (s.dir / "transcript.jsonl").write_text(
        "\n".join(lines[:-1]) + "\n")
    res = verify_transcript(s.dir)
    assert res.get("tail_truncated") is True


def test_declared_secrets_redacted_from_artifacts(tmp_path):
    """--secret values must not persist in ANY session artifact: transcript
    bodies, event output, notes, meta.json - the model sees the real bytes;
    only what hits disk is scrubbed."""
    import json
    from argus.session import Session
    from argus.config import Config
    cfg = Config(target="http://t", allow_private=True, session_dir=tmp_path,
                 secret_values=["Sup3rSecret!", "s3ss!0n"])
    s = Session(tmp_path, "http://t",
                {"goal": "login as admin:Sup3rSecret!"},
                secrets=cfg.secret_values)
    s.record_exchange("http_request",
                      {"method": "POST", "url": "http://t/login",
                       "headers": {}, "body": "u=admin&p=Sup3rSecret!"},
                      {"status": 200, "headers": {},
                       "body": "welcome, token s3ss!0n"})
    s.record_event("mcp_call", {"output": "echoed Sup3rSecret!",
                                "arguments": {"q": "Sup3rSecret!"}})
    s.note("creds admin/Sup3rSecret! verified")
    blob = (s.dir / "transcript.jsonl").read_text() \
        + (s.dir / "meta.json").read_text() \
        + (s.dir / "notes.md").read_text()
    assert "Sup3rSecret!" not in blob and "s3ss!0n" not in blob
    assert "redacted" in blob  # marker present, bytes replaced


def test_secrets_below_min_len_ignored(tmp_path):
    """A 2-char 'secret' would shred innocent bytes across the whole
    transcript - load_config drops values under 4 chars."""
    from argus.config import Config
    from argus.session import Session
    s = Session(tmp_path, "http://t", {}, secrets=["ok"])
    s.record_exchange("t", {"body": "ok ok"}, {"body": "ok"})
    blob = (s.dir / "transcript.jsonl").read_text()
    assert "ok ok" in blob  # nothing shredded
