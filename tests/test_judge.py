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


def test_a_refusal_in_WORDS_contradicts_a_later_true():
    """The test above used real JSON booleans - the one case `bool()` got right.

    `_FALSE = {"false", "no", "0"}` is in this module because a judge
    answers in words, and every one of those words is truthy under
    `bool()`. The contradiction detector used `bool()` while the value it
    guards used `_as_bool`, so a reply that refused in words and then
    restated the format was not seen as contradicting, the trailing `true`
    was taken, and the recorded verdict read `"agrees": true` while
    carrying the refusal's own reason.

    That is the one failure this module names as the worst it can have:
    "a guess landing on `agrees` manufactures assent". It did not even
    guess - it did not notice there was a disagreement.
    """
    for word in ("false", "no", "0", "FALSE", "No"):
        verdict = judge.judge_finding(
            _LLM('{"agrees": "%s", "reason": "only one response is cited; '
                 'no control shows the quote depended on the payload"}\n'
                 'Format reminder: {"agrees": true}' % word),
            FINDING, [ENTRY], "gpt-4.1")
        assert verdict.agrees is False, (
            f'`agrees: {word!r}` then `true` was recorded as agreement: '
            f'{verdict}')
        assert "contradict" in (verdict.error or ""), verdict

    # and an answer that is neither, beside a `true`, is also no verdict
    # rather than the `true` - None is its own member of that set
    verdict = judge.judge_finding(
        _LLM('{"agrees": "maybe", "reason": "unsure"}\n{"agrees": true}'),
        FINDING, [ENTRY], "gpt-4.1")
    assert verdict.agrees is False and verdict.error, verdict


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


def test_an_unjudged_finding_says_so_and_claims_no_verdict():
    """This asserted the OPPOSITE until the absence had to be printed, and
    the change was deliberate - so the retired half is written down here
    rather than quietly dropped.

    It was named `..._renders_exactly_as_before` and required the string
    "Cross-verification" to be absent. That was the right guard WHEN THE
    JUDGE WAS INTRODUCED: it proved the new feature leaked no markup into
    findings that have no verdict. It is the wrong guard now, because
    silence is what made a finding nobody cross-read indistinguishable from
    one the format does not discuss, under a proof grade that reads as the
    whole verification.

    The half that still holds, and the half that mattered: an unjudged
    finding must not read as AGREED or DISPUTED. Saying a check was not
    performed and implying its outcome are different claims.
    """
    from argus.report.markdown import _proof_block

    text = "\n".join(_proof_block(FINDING))
    assert "not performed" in text.lower(), text
    for implied in ("agreed", "DISPUTED", "no verdict"):
        assert implied not in text, (
            f"an unreviewed finding must not read as {implied!r}")


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


def test_a_credential_does_not_survive_its_own_redaction():
    """`_scrub` preserved three credential shapes and appended a marker.

    The substitution is `"".join(m.groups()) + _REDACTED`, so a pattern's
    group is the part to KEEP - `(bearer\\s+)` keeps the scheme word and
    drops the token. One pattern captured the WHOLE credential, so the
    substitution preserved it and glued the marker on the end:

        AKIAIOSFODNN7EXAMPLE  ->  AKIAIOSFODNN7EXAMPLE<redacted>

    which is worse than no redaction, because it reads as redacted. This
    is the one function in the package that deliberately sends engagement
    data to a second vendor.
    """
    from argus.judge import _scrub
    for secret, keep in (
            ("AKIAIOSFODNN7EXAMPLE", "AKIA"),
            ("ghp_16C7e42F292c6912E7710c838347Ae178B4a", "ghp_"),
            ("sk-abcdefghijklmnopqrstuvwx", "sk-"),
            ("eyJhbGciOiJIUzI1NiJ9.abcdefghij.signature", ""),
    ):
        out = _scrub(f"IDOR exposes {secret} on /x")
        assert secret not in out, f"{secret!r} survived _scrub: {out!r}"
        assert "redacted" in out, out
        if keep:
            assert keep in out, (
                f"the credential TYPE is worth keeping: {out!r}")

    # ...and the title is the field this goes through, which had no _scrub
    case = judge.render_case(
        {"id": "F01", "title": "IDOR exposes AKIAIOSFODNN7EXAMPLE",
         "vuln_class": "sqli", "severity": "high", "url": "http://x/",
         "grade": "proven", "proof": {}}, [])
    assert "AKIAIOSFODNN7EXAMPLE" not in case, case[:300]

    # prose that merely contains a prefix is not a credential
    for plain in ("AKIA is a prefix", "the /admin endpoint returned 200",
                  "SQL injection in the q parameter"):
        assert _scrub(plain) == plain, _scrub(plain)


def test_an_unreachable_judge_is_reported_as_no_verdict_not_a_dispute(
        tmp_path, monkeypatch, capsys):
    """`argus judge` contradicted the artifact it had just written.

    `apply_verdict` already distinguishes three states - "A transport
    failure or an unparseable reply is NO VERDICT, which this module's own
    docstring says is not a dispute" - and records `disputed` only when
    `not agrees and not error`. The CLI's accounting looked at `agrees`
    alone, which an error verdict sets to False, so an unreachable judge
    printed `DISPUTES F01` and summed into "0 agreed, 1 disputed" while
    findings.json carried no `disputed` flag and report.md said no verdict
    was obtained. The command exits 0, so nothing else told the operator
    that the cross-verification had not happened.
    """
    import json
    import pathlib
    import shutil
    import types

    src = (pathlib.Path(__file__).resolve().parent.parent / "docs"
           / "sample-session")
    sdir = tmp_path / "sess"
    shutil.copytree(src, sdir)

    class _Unreachable:
        def chat(self, messages, tools, system):
            raise RuntimeError("connection refused")

    from argus import llm
    monkeypatch.setattr(llm, "make_client", lambda cfg: _Unreachable())
    monkeypatch.setattr(judge, "pick_judge", lambda author, policy="strong":
                        types.SimpleNamespace(
                            key="gpt-4.1", provider="openai",
                            roles=["judge"], api_key_env=["OPENAI_API_KEY"],
                            credential=lambda: "sk-x"))

    from argus.cli import main
    assert main(["judge", str(sdir), "--only", "F01"]) == 0
    out = capsys.readouterr()

    # the store's reading: no verdict, so no dispute flag
    rows = json.loads((sdir / "findings.json").read_text(encoding="utf-8"))
    first = next(r for r in rows if r["id"] == "F01")
    assert not first.get("disputed"), (
        "an unreachable judge marked the finding disputed")

    # ...and the CLI must say the same thing the store does
    printed = out.out + out.err
    assert "DISPUTES F01" not in printed, printed
    assert "NO VERDICT" in printed, printed
    assert "1 disputed" not in printed, printed
    assert "0 agreed, 0 disputed" in printed, printed


# ---------- the one-way door, across the module that does not own it

def _judged_then_upgraded(tmp_path, judged_severity="low",
                          upgrade_severity="critical"):
    """A finding a judge lowered, then upgraded by a later worker.

    The real sequence: `argus run` records a candidate, `argus judge`
    disputes it and lowers the severity, `argus run --resume` reloads
    findings.json and a worker collects the missing checks, so
    `add_finding` takes the UPGRADE branch for the same (class, url).

    The fixture was built against the MEASURED requirement rather than
    guessed - three attempts failed first. `argus proof sqli` wants a
    fingerprint plus a row from a named table, and reaching `proven` needs
    all four of: a CONTROL exchange cited alongside the injection (the
    request without a table is what separates a read from the page's own
    furniture), the table named in the request, the DBMS fingerprint in the
    EXCHANGE, and the excerpt quoting THE ROWS - an excerpt carrying the
    fingerprint matches `DBMS_RE` and is rejected as "an error or a
    refusal, not data".
    """
    from argus.session import Session

    s = Session(tmp_path, "http://t.test/", {"target": "http://t.test/"})
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
    first = s.add_finding("sqli in q", "critical", "sqli",
                          "http://t.test/p?q=1", [weak],
                          "You have an error in your SQL syntax near ''",
                          "d", "r")
    assert first["grade"] == "candidate", first["grade"]

    # the judge lowers it, exactly the way apply_verdict does
    lowered = dict(s.findings[0])
    lowered["severity_claimed"] = lowered["severity"]
    lowered["severity"] = judged_severity
    lowered["disputed"] = True
    lowered["judges"] = [{"judge_model": "other-1", "agrees": False,
                          "reason": "an error is not a row"}]
    s.findings = [lowered]

    # a later worker collects the missing checks for the SAME bug
    strong = s.record_exchange(
        "probe_sqli",
        {"method": "GET",
         "url": "http://t.test/p?q=1'+UNION+SELECT+email,name+FROM+users--",
         "headers": {}, "body": ""},
        {"status": 200, "headers": {},
         "body": "8.0.36-MySQL\nadmin|a@x.io\nbob|b@x.io\ncarol|c@x.io",
         "final_url": "http://t.test/p", "elapsed_ms": 9,
         "truncated": False})
    s.add_finding("sqli in q", upgrade_severity, "sqli",
                  "http://t.test/p?q=1", [strong, control],
                  "admin|a@x.io\nbob|b@x.io", "d", "r")
    out = s.findings[0]
    assert out["grade"] == "proven", f"the upgrade did not take: {out['grade']}"
    return out


def test_an_upgrade_does_not_undo_a_severity_a_judge_lowered(tmp_path):
    """MEASURED HOLE, and the rule was enforced in the wrong module.

    `judge.apply_verdict` documents three one-way doors and writes
    `severity_claimed` only when it LOWERS a severity - so that key is the
    reliable marker that a model from another family read this evidence and
    found the claim over-stated.

    `session.add_finding`'s upgrade branch wrote the caller's severity
    unconditionally when the grade improved, so the sequence run -> judge
    -> run --resume restored the severity the judge had reduced. The
    invariant was enforced in judge.py and violated in session.py, and the
    violating place is the one nobody looks at.
    """
    out = _judged_then_upgraded(tmp_path)
    assert out["severity"] == "low", (
        f"an upgrade raised the severity back to {out['severity']!r} over a "
        "judge's reduction")
    assert out["severity_claimed"] == "critical", \
        "the original claim must stay on record"
    assert out["disputed"] is True, "a dispute is a one-way door"
    # and the upgrade still did its job
    assert out["grade"] == "proven", out["grade"]
    assert "admin|a@x.io" in out["evidence_excerpt"], \
        "the upgrade's better evidence replaced the weaker excerpt"


def test_an_upgrade_may_still_raise_a_severity_no_judge_touched(tmp_path):
    """The direction that keeps the fix from being a blanket freeze.

    Better evidence showing worse impact SHOULD raise a severity. What may
    not happen is undoing a reduction, and the discriminator is
    `severity_claimed` - absent here, because no judge ran.
    """
    from argus.session import Session

    s = Session(tmp_path, "http://t.test/", {"target": "http://t.test/"})
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
    s.add_finding("sqli in q", "low", "sqli", "http://t.test/p?q=1", [weak],
                  "You have an error in your SQL syntax near ''", "d", "r")
    assert "severity_claimed" not in s.findings[0]

    strong = s.record_exchange(
        "probe_sqli",
        {"method": "GET",
         "url": "http://t.test/p?q=1'+UNION+SELECT+email,name+FROM+users--",
         "headers": {}, "body": ""},
        {"status": 200, "headers": {},
         "body": "8.0.36-MySQL\nadmin|a@x.io\nbob|b@x.io",
         "final_url": "http://t.test/p", "elapsed_ms": 9,
         "truncated": False})
    s.add_finding("sqli in q", "critical", "sqli", "http://t.test/p?q=1",
                  [strong, control], "admin|a@x.io\nbob|b@x.io", "d", "r")
    assert s.findings[0]["grade"] == "proven"
    assert s.findings[0]["severity"] == "critical", \
        "an upgrade with no judge in the history must be free to raise"


def test_an_upgrade_may_lower_further_after_a_judge(tmp_path):
    """One-way means one DIRECTION, not frozen. A later worker that reads
    the impact as smaller still may say so."""
    out = _judged_then_upgraded(tmp_path, judged_severity="medium",
                               upgrade_severity="info")
    assert out["severity"] == "info", out["severity"]


# --------- amending a record that does not verify, and saying so

def _sealed_copy(tmp_path):
    import pathlib as _pl
    import shutil
    root = _pl.Path(__file__).resolve().parents[1]
    src = root / "docs" / "sample-session"
    if not src.exists():
        pytest.skip("no checked-in sample session")
    dst = tmp_path / "s"
    shutil.copytree(src, dst)
    return dst


def test_judge_checked_three_of_the_nine_ways_a_record_fails(tmp_path):
    """MEASURED HOLE, and the shared definition already existed.

    `argus judge` tested `chained`, `tail_truncated` and `bad_lines` -
    three of the nine flags `verify_transcript` returns - and
    `artifact_mismatch` was not among them. So a session whose report.md,
    meta.json, notes.md or agent.log had been edited after sealing passed
    silently, had a verdict written into findings.json, and was RE-SEALED
    over the edit: the tampering ended up covered by a fresh seal with
    nothing saying so.

    Measured on a copy of `docs/sample-session` with one line appended to
    report.md - `chain_ok` False, the old condition True - which is this
    test.

    `chain_ok` is the single definition of "this record is trustworthy",
    already used by `argus verify --json` and `argus replay`. This is one
    concept with four definitions, and the one that admitted a mismatch was
    the one that writes.
    """
    from argus.session import chain_ok, verify_transcript

    sdir = _sealed_copy(tmp_path)
    assert chain_ok(verify_transcript(sdir, "")), "premise: starts clean"

    (sdir / "report.md").write_text(
        (sdir / "report.md").read_text(encoding="utf-8")
        + "\nedited after sealing\n", encoding="utf-8")

    v = verify_transcript(sdir, "")
    assert v.get("artifact_mismatch"), \
        "premise: editing a sealed artifact raises artifact_mismatch"
    assert chain_ok(v) is False, "the shared definition must refuse this"
    # the condition the command used to apply, restated: it passes
    old_condition = not (not v.get("chained") or v.get("tail_truncated")
                         or v.get("bad_lines"))
    assert old_condition is True, (
        "if the narrow condition now refuses this, the hole is closed "
        "elsewhere and this test is measuring nothing")


def test_the_nine_flags_are_one_list_not_four(tmp_path):
    """The relation between the real lists, so a tenth flag added to
    `verify_transcript` reaches the commands that must honour it.

    `CHAIN_FAILURES` is the list `chain_ok` consults. Any command that
    AMENDS a session has to consider all of them; a command that only
    renders may warn on a subset. The failure this guards is a flag added
    to one place and not the other, which is how three of nine happened.
    """
    from argus.session import CHAIN_FAILURES, chain_ok

    assert len(CHAIN_FAILURES) >= 8, CHAIN_FAILURES
    assert "artifact_mismatch" in CHAIN_FAILURES
    # every member must be able to fail chain_ok on its own
    for flag in CHAIN_FAILURES:
        res = {"chained": True, flag: "something"}
        assert chain_ok(res) is False, (
            f"{flag} is in CHAIN_FAILURES and does not fail chain_ok, so a "
            "command consulting it would admit a record the list refuses")
    assert chain_ok({"chained": True}) is True
    assert chain_ok({"chained": False}) is False


def test_judge_itself_consults_the_shared_definition(tmp_path, capsys,
                                                     monkeypatch):
    """THE WIRING, NOT THE LOGIC - and a plant proved the difference.

    The two tests above assert the relation between the real lists and the
    construction of a mismatch, and both of them PASSED while
    `argus judge`'s own condition was reverted to the narrow three. So
    nothing held that the command consults `chain_ok` at all: logic and
    wiring are different claims, and this repository has been caught
    shipping the second without the first.

    Driven through `cli.main` rather than by reading the source, because a
    source grep cannot tell a call from a mention. The warning is emitted
    before the judge model is picked and long before a credential is
    needed, so this reaches it with no API key present.
    """
    from argus import cli

    sdir = _sealed_copy(tmp_path)
    (sdir / "report.md").write_text(
        (sdir / "report.md").read_text(encoding="utf-8")
        + "\nedited after sealing\n", encoding="utf-8")

    # no credential: the command will stop later, after the check under test
    for var in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN",
                "CLAUDE_CODE_OAUTH_TOKEN"):
        monkeypatch.delenv(var, raising=False)

    cli.main(["judge", str(sdir), "--dry-run"])
    out = capsys.readouterr()
    said = out.out + out.err
    assert "does not verify" in said, said[-400:]
    assert "artifact_mismatch" in said, (
        "the warning must NAME the flag - a session edited after sealing is "
        "a different problem from a broken chain, and the operator cannot "
        "act on 'something is wrong'")


def test_the_case_file_withholds_the_first_models_reasoning(tmp_path):
    """THE PROMPT'S OWN CLAIM, held by a test instead of by a docstring.

    `PROMPT` tells the second model "You are NOT shown the first model's
    reasoning, and you should not try to reconstruct it". That was a
    sentence in a string until now. Measured on a live case file - 8892
    bytes over six findings - the description, the remediation and the
    agent's run summary are all absent, and this asserts it so a later edit
    to the case file cannot quietly add one.

    What IS shown is load-bearing, and each disclosure is named as
    disputable in the prompt rather than offered as a hint:

        class, url, severity claimed   the claim under test
        grade from the proof matrix    the one-way door: a judge cannot
                                       promote, and is told to say so in
                                       prose if the evidence is stronger
        proof requirement              what would establish the class
        raw request/response records   the evidence itself
    """
    from argus.judge import render_case

    finding = {
        "id": "F01", "title": "SQL injection in /item id parameter",
        "vuln_class": "sqli", "category": "sqli", "severity": "critical",
        "grade": "proven", "url": "http://t.test/item?id=1",
        "evidence_ids": ["r1"], "evidence_excerpt": "sqlite 3.45",
        "description": "ID IS INTERPOLATED INTO THE QUERY STRING",
        "remediation": "USE PARAMETERIZED QUERIES",
        # a SOFTENED requirement, planted: the case file must ignore it
        "proof": {"requirement": "any 200 response will do", "missing": []},
    }
    entries = [{
        "id": "r1", "tool": "probe_sqli",
        "request": {"method": "GET", "url": "http://t.test/item?id=1",
                    "headers": {}, "body": ""},
        "response": {"status": 200, "headers": {}, "body": "sqlite 3.45",
                     "truncated": False},
    }]

    text = render_case(finding, entries)

    for leak in ("ID IS INTERPOLATED", "USE PARAMETERIZED"):
        assert leak not in text, (
            f"the case file carries the first model's reasoning: {leak!r}")

    # and the disclosures the prompt treats as disputable are present,
    # because a judge that does not know the claim cannot dispute it
    for needed in ("sqli", "critical", "proven", "http://t.test/item?id=1",
                   "sqlite 3.45"):
        assert needed in text, f"the case file omits {needed!r}"

    # THE REQUIREMENT COMES FROM THE MATRIX, NOT FROM THE FINDING, which is
    # stronger than it looks: a tampered findings.json cannot soften the bar
    # it is judged against. The planted "any 200 response will do" must not
    # appear, and the real sqli requirement must.
    from argus.proof import spec_for

    assert "any 200 response will do" not in text, \
        "a finding supplied its own requirement and the case file used it"
    real = str(spec_for("sqli").requirement)
    assert real[:40] in text, \
        "the case file does not carry the matrix's requirement"


def test_an_agent_summary_cannot_reach_the_case_file(tmp_path):
    """The run summary is the first model's narrative about its own work -
    the single largest piece of reasoning in a session - and it must not
    arrive as context for the review of a finding."""
    from argus.judge import render_case

    story = "I ESCALATED FROM SQLI TO RCE AND CONFIRMED ADMIN ACCESS"
    finding = {
        "id": "F01", "title": "t", "vuln_class": "sqli", "category": "sqli",
        "severity": "high", "grade": "proven", "url": "http://t.test/",
        "evidence_ids": ["r1"], "evidence_excerpt": "x",
        "agent_summary": story, "notes": story, "summary": story,
        "proof": {"requirement": "r", "missing": []},
    }
    entries = [{
        "id": "r1",
        "request": {"method": "GET", "url": "http://t.test/", "headers": {},
                    "body": ""},
        "response": {"status": 200, "headers": {}, "body": "x",
                     "truncated": False}}]

    assert story not in render_case(finding, entries)
