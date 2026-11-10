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
