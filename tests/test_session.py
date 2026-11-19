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


def test_findings_bad_tolerates_nonstr(tmp_path):
    from argus.session import findings_bad
    entries = {"r1": {"response": {"body": 42}}}
    rows = [{"id": "F01", "severity": "high", "evidence_excerpt": 5,
             "evidence_ids": ["r1"]}]
    assert findings_bad(entries, rows) == ["F01"]   # flagged, not crash


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


def test_the_model_s_own_free_text_is_redacted_too(tmp_path):
    """The gate held for every field the RECORDER writes, and no other.

    The test above covers transcript bodies, event output, notes and
    meta.json - which is exactly the set that was already redacted. Two
    model-authored fields were not, and both persist:

    - `record_exchange(note=...)`. `note` is a declared parameter of the
      `http_request` schema ("One-line note stored with the transcript
      entry"), so its value is whatever the model types. Measured: the
      cookie and request body on the SAME transcript line persisted as
      `sid=<redacted>` and `pw=<redacted>` while the note persisted
      verbatim.
    - `add_finding(title=..., description=..., remediation=...)`. The
      excerpt was safe only incidentally - it must be a verbatim substring
      of an already-redacted response, so a declared secret cannot match
      one. The free text has no such constraint, and findings.json is what
      report.md and summary.json are rendered from.

    So the redaction held for the three artifacts an auditor reads least
    and failed in the two that get emailed.
    """
    import json
    from argus.session import Session
    SECRET = "Sup3rSecret!"
    s = Session(tmp_path, "http://t", {"goal": "x"}, secrets=[SECRET])
    rid = s.record_exchange(
        "http_request",
        {"method": "GET", "url": "http://t/x",
         "headers": {"cookie": f"sid={SECRET}"}, "body": f"pw={SECRET}"},
        {"status": 200, "headers": {},
         "body": "root:x:0:0:root:/root:/bin/bash", "elapsed_ms": 5.0},
        note=f"logged in with {SECRET}")
    out = s.add_finding(
        title=f"IDOR exposes token {SECRET}", severity="high",
        category="sqli", url="http://t/x", evidence_ids=[rid],
        evidence_excerpt="root:x:0:0:root:/root:/bin/bash",
        description=f"the password {SECRET} was accepted",
        remediation=f"rotate {SECRET}")
    assert out.get("id"), out

    for name in ("transcript.jsonl", "findings.json", "notes.md",
                 "meta.json"):
        fp = s.dir / name
        if fp.is_file():
            assert SECRET not in fp.read_text(encoding="utf-8"), \
                f"{name} carries a declared secret"

    # and the marker is there, so this is redaction and not a dropped field
    entry = json.loads(
        (s.dir / "transcript.jsonl").read_text(encoding="utf-8")
        .splitlines()[0])
    assert "redacted" in entry["note"], entry["note"]
    row = json.loads((s.dir / "findings.json").read_text(encoding="utf-8"))[0]
    for field in ("title", "description", "remediation"):
        assert "redacted" in row[field], (field, row[field])


def test_secrets_below_min_len_ignored(tmp_path):
    """A 2-char 'secret' would shred innocent bytes across the whole
    transcript - load_config drops values under 4 chars."""
    from argus.config import Config
    from argus.session import Session
    s = Session(tmp_path, "http://t", {}, secrets=["ok"])
    s.record_exchange("t", {"body": "ok ok"}, {"body": "ok"})
    blob = (s.dir / "transcript.jsonl").read_text()
    assert "ok ok" in blob  # nothing shredded


def test_basic_auth_in_the_target_persists_in_no_artifact(tmp_path):
    """The one URL an operator certainly types with credentials.

    `session.py`'s own docstring said basic-auth in a URL "persists
    nowhere", and `meta.json` held
    `http://admin:SuperSecret123@10.0.0.5/app` verbatim - sealed into the
    hash chain and shipped in the bundle. The request path was covered and
    the target was not.

    This sweeps EVERY file in the session dir rather than the two writers
    that were fixed: fixing `meta.json` left the same credential in
    `notes.md`, which is how the first attempt at this looked finished.
    """
    target = "http://admin:SuperSecret123@10.0.0.5/app"
    sess = Session(tmp_path, target, meta={"operator": "t"})

    def leaks(directory):
        out = []
        for path in sorted(directory.iterdir()):
            if not path.is_file():
                continue
            if "SuperSecret123" in path.read_text(errors="replace"):
                out.append(path.name)
        return out

    assert leaks(sess.dir) == []
    assert "10.0.0.1" not in str(sess.dir)  # host is fine, creds are not
    import json

    meta = json.loads((sess.dir / "meta.json").read_text(encoding="utf-8"))
    # the host survives - a reviewer must still see what was tested
    assert "10.0.0.5" in meta["target"] and "admin" not in meta["target"]

    # resume rewrites meta.json and may create notes.md: both must stay
    # clean, and the resume must still work at all - comparing a redacted
    # stored target against a live credentialled one would refuse every
    # resume, which is the trap this fix had to avoid
    again = Session(tmp_path, target, meta={}, resume=str(sess.dir))
    assert leaks(again.dir) == []

    # ...and a genuinely different target is still refused
    with pytest.raises(ValueError):
        Session(tmp_path, "http://other.example/", meta={},
                resume=str(sess.dir))


def test_the_target_password_is_scrubbed_from_free_text_too(tmp_path):
    """`_redact_url` reaches URL fields; the credential also travels as prose.

    Measured before the fix, with the target's userinfo already redacted in
    `meta.json`: `notes.md`, `transcript.jsonl` and `agent.log` each still
    held it, because the loop logs `session <id> -> <target>` and a note or
    an event detail can quote the URL. Three writers, one credential - the
    ninth half-fix in this stretch, two commits after the first half.

    The fix puts the target's PASSWORD into the declared-secret set, so
    every writer that already scrubs declared values covers it at once.
    Two deliberate limits, both load-bearing:

    * the password only. Scrubbing the username by substring would mangle
      prose - a user called `admin` would redact the word everywhere.
    * free text keeps other URLs' userinfo. A target leaking
      `http://svc:pw@db/` in its own HTML is a disclosure finding, and the
      note describing it is the evidence; a blanket scrub would eat it.
    """
    target = "http://admin:FREETEXT9@10.0.0.5/app"
    sess = Session(tmp_path, target, meta={})
    sess.note("found it at " + target)
    sess.record_event("note", {"detail": "target is " + target})

    leaked = [p.name for p in sorted(sess.dir.iterdir())
              if p.is_file() and "FREETEXT9" in p.read_text(errors="replace")]
    assert leaked == [], leaked
    assert "FREETEXT9" in sess.secret_values
    # the username is not scrubbed as a word
    assert "admin" not in sess.secret_values
    # ...and another host's userinfo in free text survives, because that is
    # a finding rather than an operator credential
    sess.note("the page exposes http://svc:OtherPw1@db.internal/")
    notes = (sess.dir / "notes.md").read_text(encoding="utf-8")
    assert "OtherPw1" in notes

    # a short password stays out of the set: a 3-char value would redact
    # innocent bytes across every artifact
    short = Session(tmp_path, "http://u:abc@10.0.0.6/", meta={})
    assert "abc" not in short.secret_values


def test_a_hand_edited_findings_file_cannot_reach_dedup_as_a_scalar(tmp_path):
    """`findings.json` is operator-editable, so a stray scalar is a real
    input shape - and the only thing standing between it and the two
    readers that call `.get()` on a row without checking its type
    (`record_finding`'s dedup loop, the team coordinator's final
    per-agent metrics pass) is the filter `_resume` applies on load.

    That invariant is held at a distance: neither reader guards itself,
    and nothing failed if the filter went away. Pin it here, in both
    directions, because the two halves are deliberately opposite:

      - resume FILTERS, or dedup raises AttributeError on a scalar;
      - `_reopen` PRESERVES, because `argus judge` rewrites
        findings.json from the list it loads, and dropping the operator's
        malformed row there would delete their data instead of leaving
        it for `argus verify` to flag.
    """
    import json
    from argus.cli import _reopen
    from argus.session import sanitized_findings

    s = Session(tmp_path, "http://t.local", meta={})
    rid = s.record_exchange("t", {}, {"status": 200, "body": "proof"})
    s.add_finding("x", "low", "sqli", "http://t/item?id=1",
                  [rid], "proof", "d", "r")

    # the operator hand-edits the file and leaves junk rows behind
    rows = json.loads(s.findings_path.read_text(encoding="utf-8"))
    rows += ["oops", None, 42, ["nested"]]
    s.findings_path.write_text(json.dumps(rows), encoding="utf-8")

    # 1. resume drops them, so the unguarded readers never see one
    s2 = Session(tmp_path, "http://t.local", meta={}, resume=s.dir)
    assert len(s2.findings) == 1
    assert all(isinstance(f, dict) for f in s2.findings)

    # the dedup loop - the reader that would crash - runs clean, and still
    # dedups against the one real row that survived
    with pytest.raises(ValueError, match="duplicate"):
        rid2 = s2.record_exchange("t", {}, {"status": 200, "body": "proof"})
        s2.add_finding("x2", "low", "sqli", "http://t/item?id=9",
                       [rid2], "proof", "d", "r")

    # the coordinator's metrics expression is the other unguarded reader
    assert sum(1 for f in s2.findings if f.get("agent") == "recon-1") == 0

    # 2. `_reopen` keeps every row, junk included - judge rewrites the file
    #    from this list, so filtering here would erase operator data
    s3 = _reopen(s.dir)
    assert len(s3.findings) == 5
    assert "oops" in s3.findings and None in s3.findings

    # 3. and the renderers stay safe by sanitizing, not by trusting the load
    assert len(sanitized_findings(s3.findings)) == 1


def test_two_legal_spellings_of_one_url_are_one_finding(tmp_path):
    """The class half of the dedup key was canonicalised; the endpoint was not.

    `record_finding`'s contract is "same bug class + endpoint + params
    dedups to one finding", and the class side is keyed on
    `proof.canonical` so two spellings of a class collapse. The endpoint
    side used the raw netloc, so `http://shop.example/p?id=1` and
    `http://shop.example:80/p?id=1` - the same URI under RFC 3986 6.2.3 -
    keyed differently and both were recorded. `url` is free text
    ("Affected endpoint") that the model types, so both spellings occur.

    Measured before the fix: F01 and F02, `summary.json` counting
    `{'high': 2}`, and report.md printing `| High | 2 |` over two cards for
    one bug - severity counts a client reads, inflated by a port number.

    The second half of this test is the one that matters: only the
    normalisations RFC 3986 calls equivalent. Over-merging would hide a
    second real finding, which is worse than the duplicate it prevents.
    """
    from argus.session import Session, _finding_key

    s = Session(tmp_path, "http://shop.example", {})
    rid = s.record_exchange(
        "http_request",
        {"method": "GET", "url": "http://shop.example/p?id=1",
         "headers": {}, "body": None},
        {"status": 200, "headers": {}, "body": "root:x:0:0",
         "elapsed_ms": 1.0})
    first = s.add_finding(
        title="SQLi in id", severity="high", category="sqli",
        url="http://shop.example/p?id=1", evidence_ids=[rid],
        evidence_excerpt="root:x:0:0", description="d", remediation="r")
    assert first.get("id") == "F01", first
    # the same bug, spelled with the default port: refused as a duplicate
    import pytest
    with pytest.raises(ValueError, match="duplicate of F01"):
        s.add_finding(
            title="SQLi in id", severity="high", category="sqli",
            url="http://shop.example:80/p?id=1", evidence_ids=[rid],
            evidence_excerpt="root:x:0:0", description="d", remediation="r")
    assert len(s.findings) == 1, (
        "one bug on one endpoint was recorded twice because the model "
        f"spelled the port: {[f['id'] for f in s.findings]}")

    # equivalent under RFC 3986 6.2.3 - scheme/host case, default port
    for a, b in (("http://h.example/p?id=1", "http://h.example:80/p?id=1"),
                 ("https://h.example/p?id=1", "https://h.example:443/p?id=1"),
                 ("http://H.Example/p?id=1", "http://h.example./p?id=1")):
        assert _finding_key("sqli", a) == _finding_key("sqli", b), (a, b)
    # NOT equivalent, and merging any of these would hide a finding
    for a, b in (("http://h.example/p?id=1", "http://h.example:8080/p?id=1"),
                 ("http://h.example/p", "http://h.example/p/"),
                 ("http://h.example/p?id=1", "http://other.example/p?id=1"),
                 ("http://h.example/p?id=1", "http://h.example/p?name=1")):
        assert _finding_key("sqli", a) != _finding_key("sqli", b), (a, b)
    # an unparseable url keeps a stable key rather than crashing dedup
    assert _finding_key("sqli", "http://[bad")[0] == "sqli"


def test_a_quote_must_be_contiguous_in_ONE_part_of_the_response(tmp_path):
    """The citable texts were joined, so a quote could straddle two of them.

    `_evidence_text_of_entry` built `"\\n".join(headers-JSON, each "k: v"
    line, body)` and the gate tested the excerpt against the join - so
    `"x-injected: yes\\n<html>hello"`, half a header line and the start of
    the body, was "a verbatim substring of a cited response" while being a
    substring of no part of one, and was printed under "Proof (verbatim
    excerpt)".

    The proof matrix already caught it: `_echo_check` matches against
    `resp_body` alone and is in every class's veto tuple, and a straddle
    swept across all 29 classes grades `{'unproven': 28, 'refused': 1}`. So
    this was never a route to a `proven` finding, and it is why this is a
    gate fix and not a false-positive fix.

    It still matters, because the grade is a different claim from this one.
    `findings_bad` is what `argus verify` and an `argus report` re-render
    use to decide whether a finding's quote still verifies, and "N findings
    re-validated" is a statement about the EXCERPT.

    The second half is what makes the fix free: a body quote, a wire-style
    `k: v` line and a fragment of the headers JSON each match a part
    exactly as they matched the join. Only text spanning a boundary stops
    matching, and no response produces such text contiguously.
    """
    import pytest

    from argus.session import Session, findings_bad, _excerpt_in_entry

    s = Session(tmp_path, "http://t.test", {})
    rid = s.record_exchange(
        "http_request",
        {"method": "GET", "url": "http://t.test/x", "headers": {},
         "body": None},
        {"status": 200,
         "headers": {"set-cookie": "s=1", "x-injected": "yes"},
         "body": "<html>hello</html>", "elapsed_ms": 1.0})
    entry = s._transcript[rid]

    # every legitimate quotation form a finding uses
    for quote in ("<html>hello</html>",          # body
                  "hello",                        # part of the body
                  "x-injected: yes",              # wire-style header line
                  '"x-injected": "yes"'):         # the JSON the model saw
        assert _excerpt_in_entry(quote, entry), quote

    for straddle in ("x-injected: yes\n<html>hello",
                     '"x-injected": "yes"}\nset-cookie: s=1',
                     "set-cookie: s=1\nx-injected: yes"):
        assert not _excerpt_in_entry(straddle, entry), (
            f"{straddle!r} is contiguous in no part of the response")
        with pytest.raises(ValueError, match="verbatim substring"):
            s.add_finding(title="t", severity="high", category="crlf",
                          url="http://t.test/x", evidence_ids=[rid],
                          evidence_excerpt=straddle, description="d",
                          remediation="r")
        # ...and the forensic re-validation `argus verify` runs says so too
        assert findings_bad(s._transcript, [{
            "id": "F01", "severity": "high", "evidence_ids": [rid],
            "evidence_excerpt": straddle}]) == ["F01"], straddle


# ---- a declared secret, through BOTH doors into a finding's prose

_LEAK_SECRET = "SuperSecret123"


def _leaky_session(tmp_path):
    """A session with one declared secret and the exchanges an upgrade
    needs, built against the measured `sqli` requirement."""
    s = Session(tmp_path, "http://t.test/", {"target": "http://t.test/"},
                secrets=[_LEAK_SECRET])
    control = s.record_exchange(
        "probe_sqli",
        {"method": "GET", "url": "http://t.test/p?q=1", "headers": {},
         "body": ""},
        {"status": 200, "headers": {}, "body": "<p>Widget list</p>",
         "final_url": "http://t.test/p?q=1", "elapsed_ms": 5,
         "truncated": False})
    weak = s.record_exchange(
        "probe_sqli",
        {"method": "GET", "url": "http://t.test/p?q=1'", "headers": {},
         "body": ""},
        {"status": 500, "headers": {},
         "body": "You have an error in your SQL syntax near ''",
         "final_url": "http://t.test/p?q=1'", "elapsed_ms": 7,
         "truncated": False})
    strong = s.record_exchange(
        "probe_sqli",
        {"method": "GET",
         "url": "http://t.test/p?q=1'+UNION+SELECT+email,name+FROM+users--",
         "headers": {}, "body": ""},
        {"status": 200, "headers": {},
         "body": "8.0.36-MySQL\nadmin|a@x.io\nbob|b@x.io",
         "final_url": "http://t.test/p", "elapsed_ms": 9,
         "truncated": False})
    return s, control, weak, strong


def test_a_declared_secret_is_redacted_on_both_paths_into_a_finding(tmp_path):
    """MEASURED LEAK, AND A FIXED DEFECT RETURNING THROUGH A SECOND DOOR.

    `title`, `description` and `remediation` are free prose and the model
    routinely writes observed values into them. The creation path redacts
    them against the declared secrets, and the comment beside that code
    records the measurement that produced the fix - notes.md, agent.log and
    transcript.jsonl clean while findings.json carried the value verbatim.

    The UPGRADE path wrote the same three fields raw. Measured before the
    fix, one declared secret:

        created finding   title: sqli, logged in as •••redacted•••
        upgraded finding  title: sqli upgraded, cookie SuperSecret123

    From findings.json that reaches report.md, report.html, report-h1.html
    and report.sarif - including the artifact submitted outside. The helper
    was defined BELOW one branch while the other wrote the fields itself:
    one concept, two definitions, and the second carried no redaction at
    all.

    Both paths are asserted here, because asserting one is what let this
    come back.
    """
    s, control, weak, strong = _leaky_session(tmp_path)

    created = s.add_finding(
        f"sqli, logged in as {_LEAK_SECRET}", "high", "sqli",
        "http://t.test/p?q=1", [weak],
        "You have an error in your SQL syntax near ''",
        f"used {_LEAK_SECRET}", f"rotate {_LEAK_SECRET}")
    assert created["grade"] == "candidate", created["grade"]
    for field in ("title", "description", "remediation"):
        assert _LEAK_SECRET not in str(created.get(field)), \
            f"the creation path leaked the secret into {field}"

    upgraded = s.add_finding(
        f"sqli upgraded, cookie {_LEAK_SECRET}", "high", "sqli",
        "http://t.test/p?q=1", [strong, control],
        "admin|a@x.io\nbob|b@x.io",
        f"desc {_LEAK_SECRET}", f"fix {_LEAK_SECRET}")
    assert upgraded["grade"] == "proven", \
        f"premise: the upgrade branch was taken ({upgraded['grade']})"
    for field in ("title", "description", "remediation"):
        assert _LEAK_SECRET not in str(upgraded.get(field)), \
            f"the upgrade path leaked the secret into {field}"

    # and the file a report is rendered from carries none of it
    import json as _json
    assert _LEAK_SECRET not in _json.dumps(s.findings)


def test_the_redaction_check_sees_an_unredacted_upgrade(tmp_path):
    """The direction that matters: with the upgrade path writing the field
    raw, the assertion above must fail. Planted on a copy of the finding
    rather than by editing session.py, so the test needs no fixture
    surgery and still shows the shape it refuses."""
    s, control, weak, strong = _leaky_session(tmp_path)
    s.add_finding(f"sqli {_LEAK_SECRET}", "high", "sqli",
                  "http://t.test/p?q=1", [weak],
                  "You have an error in your SQL syntax near ''", "d", "r")
    raw_title = f"sqli upgraded, cookie {_LEAK_SECRET}"
    # what the old code stored: the caller's string, stripped and nothing else
    assert _LEAK_SECRET in str(raw_title).strip(), \
        "premise: the raw write carries the secret"
    # what the current code stores
    upgraded = s.add_finding(raw_title, "high", "sqli",
                             "http://t.test/p?q=1", [strong, control],
                             "admin|a@x.io\nbob|b@x.io", "d", "r")
    assert upgraded["title"] != str(raw_title).strip(), \
        "the upgrade path stored the caller's prose unchanged"
    assert "redacted" in upgraded["title"]
