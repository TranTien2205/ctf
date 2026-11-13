"""Cross-family verification. The invariants, not the opinion.

A judge's opinion is not testable offline and should not be: it is a model
reading evidence. What IS testable, and what matters, is that the opinion can
only ever weaken a claim. The proof matrix is deterministic and auditable; if
a model could promote a `candidate` to `proven`, the strongest claim this
system makes would rest on its weakest check.

So every test here is about a one-way door, about refusing to manufacture
agreement from a non-answer, or about the judge genuinely being from another
family.
"""
from __future__ import annotations

import json

import pytest

from argus import judge, models, proof


FINDING = {
    "id": "F01", "title": "SQL injection in /item id parameter",
    "vuln_class": "sqli", "severity": "critical", "grade": "proven",
    "url": "http://t.local/item?id=1",
    "evidence_excerpt": "admin - s3cr3t", "evidence_ids": ["r2", "r15"],
    "proof": {"requirement": "the DBMS fingerprint plus at least one row",
              "vuln_class": "sqli", "missing": []},
}

ENTRY = {
    "id": "r15", "kind": "http",
    "request": {"method": "GET",
                "url": "http://t.local/item?id=1' UNION SELECT a,b FROM users",
                "headers": {}, "body": None},
    "response": {"status": 200, "headers": {"server": "LabVuln/1.0"},
                 "body": "<li>admin - s3cr3t</li>"},
}


class _LLM:
    def __init__(self, *replies):
        self.replies = list(replies)
        self.sent = []

    def chat(self, messages, tools, system):
        self.sent.append({"case": messages[0]["content"], "system": system})
        return {"content": [{"type": "text",
                             "text": self.replies.pop(0)}]}


def _ok(**kw):
    body = {"agrees": True, "reason": "rows came back from users",
            "severity": "critical", "class": "sqli", "missing": []}
    body.update(kw)
    return json.dumps(body)


# --- the one-way doors ------------------------------------------------------

def test_a_judge_cannot_raise_a_grade():
    low = dict(FINDING, grade="candidate")
    verdict = judge.judge_finding(
        _LLM(_ok(reason="this is clearly proven")), low, [ENTRY], "gpt-4.1")
    assert judge.apply_verdict(low, verdict)["grade"] == "candidate"


def test_a_judge_cannot_clear_a_grade_either():
    verdict = judge.judge_finding(_LLM(_ok()), FINDING, [ENTRY], "gpt-4.1")
    out = judge.apply_verdict(FINDING, verdict)
    assert out["grade"] == "proven"
    assert "disputed" not in out


def test_a_judge_cannot_raise_severity():
    low = dict(FINDING, severity="low")
    verdict = judge.judge_finding(
        _LLM(_ok(severity="critical")), low, [ENTRY], "gpt-4.1")
    out = judge.apply_verdict(low, verdict)
    assert out["severity"] == "low"
    assert "severity_claimed" not in out


def test_a_judge_can_lower_severity_and_the_original_is_kept():
    verdict = judge.judge_finding(
        _LLM(_ok(agrees=False, severity="low",
                 reason="the 500 is an error message, not rows")),
        FINDING, [ENTRY], "gpt-4.1")
    out = judge.apply_verdict(FINDING, verdict)
    assert out["severity"] == "low"
    assert out["severity_claimed"] == "critical"
    assert out["disputed"] is True


def test_a_dispute_is_recorded_and_never_cleared():
    disputed = judge.apply_verdict(
        FINDING, judge.Verdict("F01", "gpt-4.1", agrees=False,
                               reason="no control"))
    # a later judge agreeing does not un-dispute what the first one found;
    # apply_verdict only ever adds the flag
    again = judge.apply_verdict(
        disputed, judge.Verdict("F01", "claude-opus-4-5", agrees=True))
    assert again["disputed"] is True


def test_a_class_disagreement_is_recorded_separately():
    verdict = judge.judge_finding(
        _LLM(_ok(agrees=False, **{"class": "disclosure"})),
        FINDING, [ENTRY], "gpt-4.1")
    out = judge.apply_verdict(FINDING, verdict)
    assert out["class_disputed"] == "disclosure"
    assert out["vuln_class"] == "sqli", "the filed class is not overwritten"


def test_agreeing_on_the_same_class_records_no_disagreement():
    verdict = judge.judge_finding(_LLM(_ok()), FINDING, [ENTRY], "gpt-4.1")
    assert "class_disputed" not in judge.apply_verdict(FINDING, verdict)


# --- refusing to manufacture agreement -------------------------------------

def test_prose_instead_of_json_is_no_verdict_not_assent():
    verdict = judge.judge_finding(
        _LLM("Looks fine to me, I'd call this a real finding."),
        FINDING, [ENTRY], "gpt-4.1")
    assert verdict.agrees is False
    assert "no JSON object" in verdict.error


def test_a_json_object_without_agrees_is_no_verdict():
    verdict = judge.judge_finding(
        _LLM('{"reason": "fine", "severity": "high"}'),
        FINDING, [ENTRY], "gpt-4.1")
    assert verdict.agrees is False
    assert verdict.error


def test_a_transport_failure_is_no_verdict_not_a_dispute():
    class _Boom:
        def chat(self, **kw):
            raise RuntimeError("502 from provider")
    verdict = judge.judge_finding(_Boom(), FINDING, [ENTRY], "gpt-4.1")
    assert verdict.agrees is False
    assert "502" in verdict.error
    # a transport failure must not read as a substantive dispute in the report
    assert not verdict.reason


def test_the_object_is_found_inside_surrounding_prose():
    verdict = judge.judge_finding(
        _LLM("Here is my review.\n\n```json\n" + _ok(agrees=False)
             + "\n```\nHope that helps."),
        FINDING, [ENTRY], "gpt-4.1")
    assert verdict.agrees is False
    assert verdict.reason


def test_two_contradicting_objects_are_no_verdict_rather_than_a_guess():
    # a model that showed the format then answered, and one that answered
    # then hedged, emit the same two objects in the same order - picking one
    # is a guess, and a guess landing on "agrees" manufactures assent
    verdict = judge.judge_finding(
        _LLM('A template looks like {"agrees": true, "reason": "example"}.\n'
             'My actual verdict: ' + _ok(agrees=False, reason="no control")),
        FINDING, [ENTRY], "gpt-4.1")
    assert verdict.agrees is False
    assert "contradict" in verdict.error


def test_two_agreeing_objects_resolve_to_the_fuller_one():
    verdict = judge.judge_finding(
        _LLM('First pass: {"agrees": false}\nFinal: '
             + _ok(agrees=False, reason="no control, no baseline")),
        FINDING, [ENTRY], "gpt-4.1")
    assert verdict.agrees is False
    assert verdict.reason == "no control, no baseline"
    assert not verdict.error


def test_an_unknown_severity_is_dropped_rather_than_stored():
    verdict = judge.judge_finding(
        _LLM(_ok(severity="catastrophic")), FINDING, [ENTRY], "gpt-4.1")
    assert verdict.severity == ""
    assert judge.apply_verdict(FINDING, verdict)["severity"] == "critical"


# --- the case file ---------------------------------------------------------

def test_the_case_file_carries_the_requirement_and_the_bytes():
    case = judge.render_case(FINDING, [ENTRY])
    assert proof.requirement_of("sqli") in case
    assert "admin - s3cr3t" in case
    assert "UNION SELECT a,b FROM users" in case
    assert "HTTP 200" in case


def test_the_case_file_never_carries_the_first_models_reasoning():
    # the disagreement worth having is the one that reasoning would not
    # produce, so description/remediation prose stays out
    rich = dict(FINDING,
                description="I reasoned that the UNION proved the read.",
                remediation="Use parameterised queries.")
    case = judge.render_case(rich, [ENTRY])
    assert "I reasoned" not in case
    assert "parameterised" not in case


def test_a_finding_citing_nothing_says_so_rather_than_looking_complete():
    case = judge.render_case(dict(FINDING, evidence_ids=[]), [])
    assert "cites no recorded exchange" in case


def test_the_case_file_is_bounded():
    huge = dict(FINDING, evidence_excerpt="A" * 200_000)
    entry = {"id": "r1", "kind": "http",
             "request": {"method": "GET", "url": "http://t/", "headers": {},
                         "body": "B" * 200_000},
             "response": {"status": 200, "headers": {},
                          "body": "C" * 500_000}}
    case = judge.render_case(huge, [entry] * 40)
    assert len(case) < 60_000, len(case)


def test_the_prompt_tells_the_judge_it_cannot_promote():
    assert "cannot promote" in judge.PROMPT
    assert "different model family" in judge.PROMPT


# --- picking an independent judge ------------------------------------------

def test_a_judge_is_never_from_the_authors_own_family(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-x")
    for author in ("claude-sonnet-4-5", "claude-opus-4-5", "gpt-4.1"):
        pick = judge.pick_judge(author)
        if pick is None:
            continue
        assert models.family(pick.key) != models.family(author), author


def test_no_independent_judge_is_an_answer_not_a_fallback(monkeypatch):
    for name in ("OPENAI_API_KEY", "DEEPSEEK_API_KEY",
                 "ARGUS_LOCAL_API_KEY", "OLLAMA_API_KEY"):
        monkeypatch.delenv(name, raising=False)
    # with only Anthropic credentialed, a Claude author has no judge
    assert judge.pick_judge("claude-sonnet-4-5") is None


def test_a_judge_must_be_listed_for_the_judge_role(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-x")
    pick = judge.pick_judge("claude-sonnet-4-5")
    assert pick is not None
    assert "judge" in pick.roles


def test_a_pick_without_a_credential_is_not_returned(monkeypatch):
    for name in ("OPENAI_API_KEY", "DEEPSEEK_API_KEY",
                 "ARGUS_LOCAL_API_KEY", "OLLAMA_API_KEY"):
        monkeypatch.delenv(name, raising=False)
    assert judge.pick_judge("gpt-4.1") is None or \
        models.get(judge.pick_judge("gpt-4.1").key).provider == "anthropic"


# --- what a reader sees ----------------------------------------------------

def test_the_report_prints_a_dispute_next_to_the_grade_it_disputes():
    from argus.report.markdown import _proof_block
    verdict = judge.judge_finding(
        _LLM(_ok(agrees=False, severity="low", reason="the 500 is an error",
                 **{"class": "disclosure"})),
        FINDING, [ENTRY], "gpt-4.1")
    block = "\n".join(_proof_block(judge.apply_verdict(FINDING, verdict)))
    assert "Proof grade: proven" in block
    assert "DISPUTED by cross-verification" in block
    assert "gpt-4.1" in block
    assert "disclosure" in block
    assert "Severity lowered from `critical`" in block


def test_the_report_distinguishes_no_verdict_from_a_dispute():
    from argus.report.markdown import _proof_block
    block = "\n".join(_proof_block(judge.apply_verdict(
        FINDING, judge.Verdict("F01", "gpt-4.1", agrees=False,
                               error="RuntimeError: 502"))))
    assert "no verdict" in block
    assert "DISPUTED" not in block


def test_an_unjudged_finding_renders_exactly_as_before():
    from argus.report.markdown import _proof_block
    assert "Cross-verification" not in "\n".join(_proof_block(FINDING))


def test_sanitized_findings_keeps_the_judge_fields():
    from argus.session import sanitized_findings
    verdict = judge.Verdict("F01", "gpt-4.1", agrees=False, reason="no rows")
    row = sanitized_findings([judge.apply_verdict(FINDING, verdict)])[0]
    assert row["disputed"] is True
    assert row["judge"]["judge_model"] == "gpt-4.1"


# --- what the audit's unverified findings turned out to be -----------------

def test_a_transport_failure_is_not_recorded_as_a_dispute():
    """The docstring said a transport failure is not a dispute and
    `apply_verdict` marked one anyway, because it only looked at `agrees`. A
    judge that could not be reached has not disagreed with anything."""
    class _Boom:
        def chat(self, **kw):
            raise RuntimeError("502 from provider")
    verdict = judge.judge_finding(_Boom(), FINDING, [ENTRY], "gpt-4.1")
    out = judge.apply_verdict(FINDING, verdict)
    assert "disputed" not in out, out
    assert out["judge"]["error"]

    # an unparseable reply is the same: no verdict, not a dispute
    out = judge.apply_verdict(
        FINDING, judge.judge_finding(_LLM("looks fine"), FINDING, [ENTRY],
                                     "gpt-4.1"))
    assert "disputed" not in out, out


def test_a_later_judge_cannot_present_itself_as_the_whole_story():
    """A second judge overwrote `finding["judge"]`, so a report read
    "Cross-verification: agreed" over a finding whose `disputed` flag was
    still set - telling the reader the opposite of the record."""
    from argus.report.markdown import _proof_block
    disputed = judge.apply_verdict(
        FINDING, judge.Verdict("F01", "gpt-4.1", agrees=False,
                               reason="no control"))
    agreed = judge.apply_verdict(
        disputed, judge.Verdict("F01", "claude-opus-4-5", agrees=True,
                                reason="fine"))
    assert agreed["disputed"] is True
    assert len(agreed["judges"]) == 2
    block = "\n".join(_proof_block(agreed))
    assert "DISPUTED by cross-verification" in block, block
    assert "2 judges read this evidence" in block
    assert "gpt-4.1 disputed" in block and "claude-opus-4-5 agreed" in block


def test_the_verdict_scan_is_linear_in_the_reply_length():
    """It restarted from every `{` and ran to the end, so an 8 KB answer with
    nested objects took seconds - per finding."""
    import time
    timings = {}
    for n in (500, 8000):
        reply = "{" * n + "}" * n + '{"agrees": false, "reason": "no control"}'
        start = time.monotonic()
        verdict = judge.parse_verdict(reply, "F01", "gpt-4.1")
        timings[n] = time.monotonic() - start
        assert verdict.agrees is False
        assert verdict.reason == "no control"
    # sixteen times the input must not cost anything like sixteen times as long
    assert timings[8000] < timings[500] * 8 + 0.5, timings


def test_a_brace_inside_a_string_is_not_an_object():
    verdict = judge.parse_verdict(
        '{"agrees": false, "reason": "the body was {not} json"}', "F", "m")
    assert verdict.agrees is False
    assert verdict.reason == "the body was {not} json"
    assert not verdict.error


def test_a_cited_http_exchange_is_not_labelled_an_event():
    """Every record was labelled `(event)` - the word this module's own prompt
    uses for evidence that is NOT class evidence - so a judge reading a real
    request/response pair was told it was not one."""
    case = judge.render_case(FINDING, [ENTRY])
    headers = [l for l in case.splitlines() if l.startswith("### ")]
    assert headers and "http exchange" in headers[0], headers
    event = {"id": "r9", "kind": "jwt_forge", "claims_set": "{}"}
    case = judge.render_case(FINDING, [event])
    assert "(jwt_forge)" in case


def test_an_unrated_finding_still_takes_a_severity_reduction():
    """A finding with no canonical severity swallowed the reduction silently -
    the one direction this module is supposed to allow."""
    out = judge.apply_verdict(
        {"id": "F01", "vuln_class": "sqli", "grade": "proven"},
        judge.Verdict("F01", "gpt-4.1", agrees=False, severity="low"))
    assert out["severity"] == "low"
    assert out["severity_was_unrated"] is True
    # and raising is still refused, unrated or not
    out = judge.apply_verdict(
        {"id": "F01", "severity": "low", "grade": "proven"},
        judge.Verdict("F01", "gpt-4.1", agrees=False, severity="critical"))
    assert out["severity"] == "low"


def test_agreeing_verdicts_merge_rather_than_the_last_one_winning():
    """A model that answers and then appends `Summary: {"agrees": false}` put
    its reason, severity and missing list in the FIRST object; taking the last
    discarded all three."""
    verdict = judge.parse_verdict(
        '{"agrees": false, "reason": "no control was cited", '
        '"severity": "low", "missing": ["a baseline"]}\n'
        'Summary: {"agrees": false}', "F01", "gpt-4.1")
    assert verdict.agrees is False
    assert verdict.reason == "no control was cited"
    assert verdict.severity == "low"
    assert verdict.missing == ["a baseline"]

    # and a later object still wins on the fields it carries
    verdict = judge.parse_verdict(
        '{"agrees": true}\n'
        '{"agrees": true, "reason": "rows came back", "severity": "critical"}',
        "F01", "gpt-4.1")
    assert verdict.reason == "rows came back"
    assert verdict.severity == "critical"

    # a contradiction is still no verdict, however full either object is
    verdict = judge.parse_verdict(
        '{"agrees": true, "reason": "fine"}\n{"agrees": false}', "F", "m")
    assert verdict.agrees is False
    assert "contradict" in verdict.error


def test_judging_re_renders_the_report_before_sealing(tmp_path, monkeypatch):
    """Writing the verdict into findings.json and then sealing left report.md,
    report.html, report.sarif and summary.json describing findings that no
    longer matched - a reader opening the report saw a `proven` finding with
    no sign a judge had disputed it, under a seal covering both."""
    import json
    import pathlib
    import shutil
    import types

    src = pathlib.Path(__file__).resolve().parent.parent / "docs" / "sample-session"
    sdir = tmp_path / "sess"
    shutil.copytree(src, sdir)

    class _Fake:
        def chat(self, messages, tools, system):
            return {"content": [{"type": "text", "text": json.dumps({
                "agrees": False,
                "reason": "the 500 is an error message, not rows",
                "severity": "low", "class": "disclosure",
                "missing": ["one row from a named table"]})}]}

    from argus import llm
    monkeypatch.setattr(llm, "make_client", lambda cfg: _Fake())
    monkeypatch.setattr(judge, "pick_judge", lambda author, policy="strong":
                        types.SimpleNamespace(
                            key="gpt-4.1", provider="openai",
                            roles=["judge"], api_key_env=["OPENAI_API_KEY"],
                            credential=lambda: "sk-x"))

    from argus.cli import main
    assert main(["judge", str(sdir), "--only", "F01"]) == 0

    rows = json.loads((sdir / "findings.json").read_text(encoding="utf-8"))
    first = next(r for r in rows if r["id"] == "F01")
    assert first["disputed"] is True
    assert first["severity"] == "low"
    assert first["severity_claimed"] == "critical"

    report = (sdir / "report.md").read_text(encoding="utf-8")
    assert "DISPUTED by cross-verification" in report
    assert "Severity lowered from `critical`" in report

    # and the session still verifies: the seal covers the re-rendered report
    from argus.session import verify_transcript
    assert verify_transcript(sdir).get("chained") is True


def test_scrub_catches_url_credentials_inside_prose():
    """The case file goes to a SECOND vendor, and this defence could not fire.

    `_scrub` called `_redact_url` on the whole blob, and `_redact_url` only
    works when the entire string is a URL. Measured:
    `"target is http://admin:SuperSecret123@10.0.0.5/app now"` came back
    unchanged. A line that looks like a defence and never fires is worse
    than none, because it is counted as one.

    Only the password is replaced: a judge asked whether a disclosure
    happened needs the shape of what leaked, not its value, so the host and
    the username still read.
    """
    from argus.judge import _REDACTED, _scrub

    for text, secret in (
            ("http://admin:SuperSecret123@10.0.0.5/app", "SuperSecret123"),
            ("target is http://admin:SuperSecret123@10.0.0.5/app now",
             "SuperSecret123"),
            ("the page exposes http://svc:DbPass9@db.internal/", "DbPass9"),
    ):
        out = _scrub(text)
        assert secret not in out, (text, out)
        assert _REDACTED in out, (text, out)

    # two in one blob, both scrubbed
    both = _scrub("see http://a:pw1xx@h1/x and https://b:pw2yy@h2/y")
    assert "pw1xx" not in both and "pw2yy" not in both

    # the host and user survive - the judge needs to see what leaked
    kept = _scrub("http://admin:SuperSecret123@10.0.0.5/app")
    assert "10.0.0.5" in kept

    # ...and text without a URL credential is untouched: an `@` in prose or
    # a credential-free URL must not be mangled
    assert _scrub("no creds: http://10.0.0.5:8080/app") == (
        "no creds: http://10.0.0.5:8080/app")
    assert _scrub("mailto style a@b.c and a plain @ sign") == (
        "mailto style a@b.c and a plain @ sign")
