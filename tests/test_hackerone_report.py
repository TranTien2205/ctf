"""The bug-bounty shape: one section per finding, with the PoC.

The existing renderers answer "what did this engagement find". A triager
asks something narrower and in a fixed order, and three refusals in this
renderer came out of what the recorder actually holds rather than out of
taste. Each one has a test here, because a refusal nobody checks is a
comment.
"""
from __future__ import annotations

import pathlib
import sys
import tempfile
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from argus.report.hackerone import render_hackerone     # noqa: E402
from argus.session import Session                        # noqa: E402


class _Cfg:
    model = "test-model"


def _session(tmp: pathlib.Path) -> Session:
    sess = Session(tmp, "http://t.local", {"model": "t"})
    sess.record_exchange(
        "http_request",
        {"method": "GET", "url": "http://t.local/search?q=benign", "headers": {}},
        {"status": 200, "headers": {"content-type": "text/html"},
         "body": "<html><body>no results</body></html>"})
    sess.record_exchange(
        "probe_sqli",
        {"method": "GET", "url": "http://t.local/search?q=%27", "headers": {},
         "body": ""},
        {"status": 500, "headers": {"content-type": "text/html"},
         "body": "x" * 3000 + "SQLITE_ERROR: near \")\": syntax error" + "y" * 3000})
    return sess


def _attrs_of(html: str) -> list[tuple[str, str, str]]:
    found: list[tuple[str, str, str]] = []

    class _P(HTMLParser):
        def handle_starttag(self, tag, attrs):
            for key, value in attrs:
                found.append((tag, key, str(value or "")))

    parser = _P()
    parser.feed(html)
    return found


def test_no_url_ever_reaches_an_attribute():
    """Every byte in a finding is target-influenced and this file is served
    under `sandbox; default-src 'none'`. Text nodes only means a hostile
    value has nowhere to go even if the escaping were wrong - the same
    reasoning the operator console uses for having no innerHTML at all
    rather than escaped innerHTML.

    MEASURED, and the first check of this was wrong: grepping for `href=`
    found 101 hits and reported a defect, because the TARGET's recorded HTML
    body is quoted - escaped - inside a `<pre>`. Parsing settles it: the
    only attribute names in the whole document are charset, class, content,
    lang, name and style.
    """
    with tempfile.TemporaryDirectory() as tmp:
        sess = _session(pathlib.Path(tmp))
        sess.add_finding(
            "Reflected markup in q", "medium", "xss",
            "http://t.local/search?q=%27", ["r2"], "SQLITE_ERROR",
            '<img src=x onerror=alert(1)> and <a href="//evil">', "")
        page = render_hackerone(sess, _Cfg()).read_text(encoding="utf-8")

    names = {k for _t, k, _v in _attrs_of(page)}
    assert names <= {"charset", "class", "content", "lang", "name", "style"}, names
    for tag, key, value in _attrs_of(page):
        assert "http://" not in value and "https://" not in value, (tag, key, value)
        assert "javascript:" not in value.lower(), (tag, key, value)
    # the hostile description IS present, as text
    assert "onerror=alert(1)" in page
    assert "&lt;img" in page, "it must be escaped, not stripped"


def test_no_replay_command_is_ever_composed():
    """A curl built from a recorded exchange would carry the redaction
    marker where twelve request header names and Set-Cookie are masked, so
    it would be wrong to READ and wrong to SEND - and a reader would
    reasonably assume a command in a PoC was the command that ran. The
    literal recorded request is printed instead.
    """
    with tempfile.TemporaryDirectory() as tmp:
        sess = _session(pathlib.Path(tmp))
        sess.add_finding("t", "high", "sqli", "http://t.local/search",
                         ["r2"], "SQLITE_ERROR", "d", "")
        page = render_hackerone(sess, _Cfg()).read_text(encoding="utf-8")

    low = page.lower()
    for shape in ("curl ", "wget ", "http -v", "requests.get("):
        assert shape not in low, f"a replay command was composed: {shape!r}"
    assert "no command here was composed" in low
    # and the real request IS shown
    assert "GET http://t.local/search?q=%27" in page


def test_the_response_window_is_centred_on_the_quoted_bytes():
    """`html.py` prints `response.body[:4000]` from the START, so on a longer
    body whose proving bytes are later the HTML report omits the proof while
    the markdown report, which centres with `_excerpt()`, shows it. The
    fixture's body puts the engine error at offset 3000 behind 3000 bytes of
    padding."""
    with tempfile.TemporaryDirectory() as tmp:
        sess = _session(pathlib.Path(tmp))
        sess.add_finding("t", "high", "sqli", "http://t.local/search",
                         ["r2"], "SQLITE_ERROR", "d", "")
        page = render_hackerone(sess, _Cfg()).read_text(encoding="utf-8")

    assert "SQLITE_ERROR" in page, "the proving bytes must be in the window"
    assert "centred on the quoted bytes" in page
    assert "at offset 3000" in page, "the offset is stated, not implied"


def test_a_citation_with_no_request_is_a_sentence_not_a_blank_box():
    """`html.py` renders a missing field as an empty cell - an empty
    `<pre></pre>` under "Proof (verbatim excerpt)" - which reads as "no
    proof" when it means "no field". A finding may cite an EVENT id that has
    no request at all; the shipped sample's jwt finding does exactly that.
    """
    with tempfile.TemporaryDirectory() as tmp:
        sess = Session(pathlib.Path(tmp), "http://t.local", {"model": "t"})
        sess.record_exchange("jwt_forge",
                             {"method": "", "url": "", "headers": {}},
                             {"status": 0, "headers": {},
                              "body": "alg=none token minted"})
        sess.add_finding("Forged token accepted", "high", "jwt",
                         "http://t.local/api", ["r1"], "alg=none", "d", "")
        page = render_hackerone(sess, _Cfg()).read_text(encoding="utf-8")

    assert "<pre></pre>" not in page, "an empty box says the wrong thing"
    assert "carries no request" in page
    assert "it is not a step" in page
    # the event's own output is still shown as evidence
    assert "alg=none token minted" in page


def test_no_remediation_is_invented():
    with tempfile.TemporaryDirectory() as tmp:
        sess = _session(pathlib.Path(tmp))
        sess.add_finding("t", "high", "sqli", "http://t.local/search",
                         ["r2"], "SQLITE_ERROR", "d", "")
        page = render_hackerone(sess, _Cfg()).read_text(encoding="utf-8")
    assert "does not generate fix advice it has not observed" in page


def test_it_is_self_contained_like_the_other_artifacts():
    """Served under `sandbox; default-src 'none'; style-src 'unsafe-inline'`,
    so an external stylesheet, font or script would be blocked with no
    visible error. Inline style is a requirement of the serving contract,
    not a preference."""
    with tempfile.TemporaryDirectory() as tmp:
        sess = _session(pathlib.Path(tmp))
        sess.add_finding("t", "low", "sqli", "http://t.local/", ["r1"],
                         "no results", "d", "")
        page = render_hackerone(sess, _Cfg()).read_text(encoding="utf-8")
    assert "<script" not in page.lower()
    assert "<link" not in page.lower()
    assert "@import" not in page
    assert "<style>" in page


def test_an_empty_session_says_so():
    with tempfile.TemporaryDirectory() as tmp:
        sess = _session(pathlib.Path(tmp))
        page = render_hackerone(sess, _Cfg()).read_text(encoding="utf-8")
    assert "recorded no findings" in page
    assert "That is a result" in page


def test_it_is_reachable_as_a_served_format_and_from_render_report():
    import inspect

    from argus.report import markdown as md
    from argus.web import api

    assert "h1" in api.REPORT_FORMATS
    assert api.REPORT_FORMATS["h1"][0] == "report-h1.html"
    assert "render_hackerone" in inspect.getsource(md.render_report), \
        "a renderer nothing calls is the defect this session kept finding"


# ------------- the second reading, and the absence of it, on every artifact

def _finding(**over):
    base = {"id": "F01", "title": "SQL injection in q", "severity": "high",
            "category": "sqli", "vuln_class": "sqli", "grade": "proven",
            "url": "http://t.test/a?q=1", "evidence_ids": ["r1"],
            "evidence_excerpt": "root@localhost", "cwe": "CWE-89",
            "description": "d", "remediation": "r",
            "proof": {"requirement": "a row from a named table",
                      "missing": []}}
    base.update(over)
    return base


def test_html_states_that_no_second_model_read_the_evidence():
    """MEASURED: `_judge_html` returned "" for a finding with no verdict, so
    a finding nobody cross-read was indistinguishable from one the renderer
    does not discuss - under a PROOF badge that reads as the whole
    verification."""
    from argus.report import html as html_mod

    blank = html_mod._judge_html(_finding())
    assert blank, "an unreviewed finding still renders nothing"
    assert "Cross-verification: not performed" in blank
    assert "another family" in blank

    # NAMED, not the bare substring - and this broke for the SECOND time
    # the same way. The markdown test asserted `"not performed" not in` and
    # broke when a second absence used those words; this one then did the
    # same when the replay absence was added to the html box an hour later.
    # Thirty-fifth instance, with the fix already known and applied next
    # door. The lesson is not "name the claim once": it is that adding ANY
    # second absence to a block invalidates every bare-substring assertion
    # about the first.
    agreed = html_mod._judge_html(_finding(
        judge={"judge_model": "other-1", "agrees": True, "reason": "ok"}))
    assert "Cross-verification: not performed" not in agreed
    assert "Cross-verification: agreed" in agreed


def test_the_bug_bounty_artifact_badges_the_second_reading_or_its_absence():
    """The artifact that leaves this machine. A proof badge with no second
    opinion beside it claims more verification than was done."""
    from argus.report import hackerone as h1

    none = h1._badges(_finding())
    assert "NOT CROSS-VERIFIED" in none
    assert "PROOF: PROVEN" in none, "the first reading is still shown"

    agreed = h1._badges(_finding(
        judge={"judge_model": "other-1", "agrees": True}))
    assert "CROSS-VERIFIED BY OTHER-1" in agreed
    assert "NOT CROSS-VERIFIED" not in agreed

    disputed = h1._badges(_finding(
        judge={"judge_model": "other-1", "agrees": False,
               "reason": "reflected, not executed"}))
    assert "DISPUTED BY OTHER-1" in disputed

    # a judge that could not answer is not a review
    failed = h1._badges(_finding(
        judges=[{"judge_model": "other-1", "error": "no credential"}]))
    assert "NOT CROSS-VERIFIED" in failed, \
        "a failed judge call must not read as a completed review"


def test_a_dispute_outranks_a_later_agreement_on_the_badge():
    """Same rule the markdown renderer already applied to its history: a
    later agreement must not present itself as the whole story over a
    finding an earlier judge disputed."""
    from argus.report import hackerone as h1

    badges = h1._badges(_finding(judges=[
        {"judge_model": "other-1", "agrees": False, "reason": "no row"},
        {"judge_model": "other-2", "agrees": True, "reason": "looks fine"},
    ]))
    assert "DISPUTED BY OTHER-1" in badges
    assert "CROSS-VERIFIED" not in badges.replace("NOT CROSS-VERIFIED", "")


def test_markdown_states_the_absence_too():
    """The third renderer. It already discussed a verdict that exists; the
    gap was the same one in all three - silence for a finding nobody read,
    under a grade that reads as the whole verification."""
    from argus.report import markdown as md

    blank = "\n".join(md._proof_block(_finding()))
    assert "Cross-verification: not performed" in blank, blank
    assert "another family" in blank

    agreed = "\n".join(md._proof_block(_finding(
        judge={"judge_model": "other-1", "agrees": True, "reason": "ok"})))
    # NAMED, not "not performed". This asserted the bare substring and broke
    # the moment a SECOND absence used the same words: a finding with a
    # judge verdict and no replay prints "Re-verification: not performed",
    # so the string stopped discriminating between two different claims.
    # Twenty-eighth instance this session of a check keyed on words rather
    # than on the claim's form, and the first one I wrote and broke myself
    # inside an hour.
    assert "Cross-verification: not performed" not in agreed
    assert "Cross-verification: agreed" in agreed


def test_the_two_absences_are_distinguishable():
    """One block now carries two independent absences - no second model has
    read the evidence, and the target has not been asked again - and a
    reader must be able to tell which is which. They answer different
    questions, and a finding can have either, both or neither.
    """
    from argus.report import markdown as md

    both = "\n".join(md._proof_block(_finding()))
    assert "Cross-verification: not performed" in both
    assert "Re-verification: not performed" in both

    judged_only = "\n".join(md._proof_block(_finding(
        judge={"judge_model": "other-1", "agrees": True, "reason": "ok"})))
    assert "Cross-verification: agreed" in judged_only
    assert "Re-verification: not performed" in judged_only

    replayed_only = "\n".join(md._proof_block(_finding(
        replay={"outcome": "reproduced", "reason": "bytes came back"})))
    assert "Cross-verification: not performed" in replayed_only
    assert "reproduced" in replayed_only
    assert "Re-verification: not performed" not in replayed_only

    neither_absent = "\n".join(md._proof_block(_finding(
        judge={"judge_model": "other-1", "agrees": True, "reason": "ok"},
        replay={"outcome": "reproduced", "reason": "bytes came back"})))
    assert "not performed" not in neither_absent, neither_absent


# --- a finding the target no longer does, on every artifact a reader gets

_GONE = {"outcome": "not_reproduced",
         "reason": "the request was sent and answered HTTP 200, and the "
                   "quoted bytes were not in the response"}
_BACK = {"outcome": "reproduced", "reason": "the target returned the "
                                            "quoted bytes again (HTTP 200)"}
_UNASKED = {"outcome": "inconclusive", "reason": "no credential supplied"}


def test_a_failed_re_verification_reaches_every_artifact():
    """MEASURED GAP, and the worst shape on this axis.

    `argus replay` writes `replay`/`replays` and a one-way `replay_failed`
    into findings.json. Measured by counting mentions per renderer:

        markdown   17        html   0        hackerone   0        sarif   0

    So a finding the operator has evidence the target NO LONGER DOES was
    published unchanged to the one artifact that leaves this machine. Not a
    fabricated finding - an EXPIRED one presented as current, which is
    assertion-beyond-the-evidence one field over, and a bug-bounty triager
    reading `PROOF: PROVEN` has no way to know.
    """
    from argus.report import hackerone as h1
    from argus.report import html as html_mod
    from argus.report import markdown as md
    from argus.report import sarif as sarif_mod

    gone = _finding(replay=_GONE)
    assert "DID NOT REPRODUCE" in h1._badges(gone)
    assert "DID NOT REPRODUCE" in html_mod._judge_html(gone)
    assert "DID NOT REPRODUCE" in "\n".join(md._proof_block(gone))
    assert sarif_mod._replay_state(gone) == "not_reproduced"
    assert "quoted bytes were not" in sarif_mod._replay_reason(gone)


def test_a_reproduced_finding_says_so_on_every_artifact():
    from argus.report import hackerone as h1
    from argus.report import html as html_mod
    from argus.report import markdown as md
    from argus.report import sarif as sarif_mod

    back = _finding(replay=_BACK)
    assert "RE-VERIFIED: REPRODUCED" in h1._badges(back)
    assert "reproduced" in html_mod._judge_html(back).lower()
    assert "reproduced" in "\n".join(md._proof_block(back)).lower()
    assert sarif_mod._replay_state(back) == "reproduced"
    for rendered in (h1._badges(back), html_mod._judge_html(back),
                     "\n".join(md._proof_block(back))):
        assert "DID NOT REPRODUCE" not in rendered


def test_an_inconclusive_replay_is_not_reported_as_re_verified():
    """The question never reached the target, so it is not coverage - the
    same rule the coverage table and the judge's error case apply."""
    from argus.report import hackerone as h1
    from argus.report import sarif as sarif_mod

    unasked = _finding(replay=_UNASKED)
    assert sarif_mod._replay_state(unasked) == "not_re_verified"
    assert "NOT RE-VERIFIED" in h1._badges(unasked)
    assert "DID NOT REPRODUCE" not in h1._badges(unasked)


def test_a_failure_outranks_a_later_success_on_every_artifact():
    """A target answering differently on two replays is information about
    the target, not a correction - so the failure is what a reader sees."""
    from argus.report import hackerone as h1
    from argus.report import sarif as sarif_mod

    both = _finding(replays=[_GONE, _BACK])
    assert sarif_mod._replay_state(both) == "not_reproduced"
    assert "DID NOT REPRODUCE" in h1._badges(both)
    assert "RE-VERIFIED: REPRODUCED" not in h1._badges(both)


# -------- a dispute, attributed to the model that actually raised it

_DISPUTE_THEN_AGREE = [
    {"judge_model": "other-1", "agrees": False,
     "reason": "an error is not a row"},
    {"judge_model": "other-2", "agrees": True, "reason": "looks fine"},
]


def test_a_dispute_names_the_model_that_raised_it_on_every_renderer():
    """MEASURED, and a fixed defect surviving in a sibling renderer.

    `apply_verdict` keeps every verdict in `judges` and overwrites `judge`
    with the newest, while `disputed` is a one-way flag. So judge #1
    disputing and judge #2 agreeing leaves `disputed` true and `judge`
    pointing at the one that AGREED.

    `report.html` read `judge` alone and printed "DISPUTED by
    cross-verification (other-2)" - sending a reader to ask other-2 about a
    dispute it never raised, with no reason shown. markdown, on the same
    finding, said "DISPUTED (other-1) - an error is not a row".

    `apply_verdict`'s own comment records this hazard being found and fixed
    once: "A second judge that agrees used to replace the first one's
    block, so a report read 'Cross-verification: agreed' over a finding
    whose `disputed` flag was still set - telling the reader the opposite
    of the record." It was fixed for markdown and missed here, which is the
    same shape as a redaction holding in one branch and not the other.
    """
    from argus.report import html as html_mod
    from argus.report import markdown as md

    f = _finding(disputed=True, judges=_DISPUTE_THEN_AGREE,
                 judge=_DISPUTE_THEN_AGREE[-1])

    # ASSERTED ON THE DISPUTE LINE, not on the whole document - and the
    # first version of this got it wrong in the direction the whole session
    # has been about. It required `other-2` to be absent, and markdown
    # DELIBERATELY lists both: "(2 judges read this evidence: other-1
    # disputed, other-2 agreed)", precisely so a later agreement cannot
    # present itself as the whole story. Mentioning the agreeing model is
    # correct; attributing the dispute to it is not.
    for name, rendered in (("html", html_mod._judge_html(f)),
                           ("markdown", "\n".join(md._proof_block(f)))):
        # The ATTRIBUTION line, not every line containing the word.
        # markdown prints a roll-call too - "(2 judges read this evidence:
        # other-1 disputed, other-2 agreed)" - which legitimately names
        # both, so a filter on "disput" catches it and the assertion below
        # then reads the roll-call as the attribution. Third filter
        # attempt; the first two were too broad in the same way.
        lines = [ln for ln in rendered.replace("<br>", "\n").splitlines()
                 if "DISPUTED by cross-verification" in ln]
        assert lines, f"{name} does not report the dispute at all"
        line = " ".join(lines)
        assert "other-1" in line, (
            f"{name} does not name the model that raised the dispute: "
            f"{line[:200]}")
        assert "other-2" not in line, (
            f"{name} attributes the dispute to the model that agreed: "
            f"{line[:200]}")
        assert "an error is not a row" in rendered, \
            f"{name} shows no reason, or the wrong one"


def test_a_lone_agreement_is_still_reported_as_agreement():
    """The direction that keeps the fix from reading every finding as
    disputed: with no dispute in the history, the latest verdict stands."""
    from argus.report import html as html_mod

    agreed = html_mod._judge_html(_finding(
        judge={"judge_model": "other-9", "agrees": True, "reason": "ok"}))
    assert "other-9" in agreed
    assert "DISPUTED" not in agreed
    assert "Cross-verification: not performed" not in agreed


def test_a_dispute_with_no_disputed_flag_is_still_a_dispute():
    """`disputed` is written by `apply_verdict`, so a findings.json edited
    by hand or produced by an older version can carry the verdict without
    the flag. The history is the record; the flag is a convenience."""
    from argus.report import html as html_mod

    rendered = html_mod._judge_html(_finding(judges=_DISPUTE_THEN_AGREE))
    assert "DISPUTED" in rendered
    assert "other-1" in rendered


# ------------- a cited event, rendered as what it is

class _FakeSession:
    def __init__(self, entries):
        self._e = entries

    def get_exchange(self, rid):
        return self._e.get(rid)


_HTTP_ENTRY = {
    "id": "r1", "ts": 1.0, "chain": "deadbeef" * 8, "agent": "agent",
    "tool": "probe_sqli",
    "request": {"method": "GET", "url": "http://t.test/p?q=1",
                "headers": {}, "body": ""},
    "response": {"status": 200, "headers": {}, "body": "admin|a@x.io",
                 "final_url": "http://t.test/p?q=1", "elapsed_ms": 9,
                 "truncated": False},
}

_EVENT_ENTRY = {
    "id": "r62", "ts": 2.0, "chain": "cafebabe" * 8, "agent": "agent",
    "kind": "jwt_forge",
    "claims_set": {"user": "admin", "role": "admin"},
    "alg_in": "HS256", "weak_secret_used": True,
    "token_sha256_16": {"resigned": "217f52fcd4a6fb35"},
}


def test_a_cited_event_is_rendered_as_what_it_is():
    """MEASURED IN THE COMMITTED REFERENCE ARTIFACT.
    `docs/sample-session/report.html` showed, for the proven jwt finding's
    cited event r62:

        Transcript r62:   ->
        <pre></pre>

    The citation was built unconditionally from `request.method`,
    `request.url`, `response.status` and `response.body`, and an event
    entry has none of those. So the operator-facing report rendered an
    empty box for evidence its own narrative describes two lines below:
    "r62 set ['role','user'], echoed 'admin'".

    `report-h1.html` already said "r62 is a jwt_forge event, which carries
    no request - its output is evidence but it is not a step", so this
    renderer was the one missing it: the fourth fixed-elsewhere defect
    found in a sibling renderer today.
    """
    from argus.report import html as html_mod

    out = html_mod._citation(_FakeSession({"r62": _EVENT_ENTRY}), "r62")
    assert "jwt_forge event" in out, out
    assert "no request, so no status" in out
    assert "HS256" in out, "the recorded evidence must be shown"
    assert "role" in out and "admin" in out
    assert ":   -&gt;" not in out and ":   ->" not in out, \
        "the empty-arrow shape is what this replaces"


def test_a_cited_event_does_not_print_bookkeeping():
    """`chain` is a digest, `ts` a float, `agent` a role name - none is
    evidence, and the chain digest in particular invites a reader to treat
    it as part of the proof."""
    from argus.report import html as html_mod

    out = html_mod._citation(_FakeSession({"r62": _EVENT_ENTRY}), "r62")
    for noise in ("cafebabe", "chain", "1.0", "2.0"):
        assert noise not in out, f"{noise} is bookkeeping, not evidence"


def test_an_http_citation_still_renders_the_exchange():
    """The direction that keeps the event branch from swallowing the
    ordinary case, which is 64 of the 66 entries in the sample session."""
    from argus.report import html as html_mod

    out = html_mod._citation(_FakeSession({"r1": _HTTP_ENTRY}), "r1")
    assert "GET" in out and "http://t.test/p?q=1" in out
    assert "200" in out
    assert "admin|a@x.io" in out
    assert "event" not in out


def test_an_entry_with_nothing_recorded_says_so():
    """Absence printed rather than an empty box - the same rule, one level
    down: an entry really carrying nothing must say that, not render blank."""
    from argus.report import html as html_mod

    bare = {"id": "r9", "ts": 3.0, "chain": "ab" * 32, "agent": "agent",
            "kind": "marker"}
    out = html_mod._citation(_FakeSession({"r9": bare}), "r9")
    assert "nothing to show" in out, out
    assert "marker event" in out


def test_a_missing_entry_does_not_render_a_blank_citation():
    from argus.report import html as html_mod

    out = html_mod._citation(_FakeSession({}), "r404")
    assert "r404" in out
    assert "nothing to show" in out or "no request" in out


_TWO_ATTEMPTS = [
    {"outcome": "inconclusive",
     "reason": "the recorded request carried authorization and the "
               "transcript stores the hash, not the value"},
    {"outcome": "reproduced",
     "reason": "the target returned the quoted bytes again (HTTP 200)"},
]


def test_a_reproduction_that_needed_a_credential_says_so():
    """MEASURED ON A LIVE SESSION, and it corrects a claim of mine.

    A finding's first replay was inconclusive - the recorded request carried
    a credential and the transcript keeps only its digest - and it
    reproduced once the credential was supplied. Both artifacts showed only
    "reproduced", so a reader could not tell it apart from a finding that
    reproduces unauthenticated.

    That difference is material: for whoever triages this, "it still works,
    with a valid session" is a different report from "it still works". The
    history already held the distinction, and a commit message of mine
    claimed a reader could see it - true of findings.json, false of the
    report.
    """
    from argus.report import hackerone as h1
    from argus.report import markdown as md

    f = _finding(replays=list(_TWO_ATTEMPTS), replay=_TWO_ATTEMPTS[-1])

    badges = h1._badges(f)   # an assembled HTML string, not a list
    assert "RE-VERIFIED: REPRODUCED" in badges
    assert "EARLIER ATTEMPT COULD NOT ASK" in badges, badges

    block = "\n".join(md._proof_block(f))
    assert "reproduced" in block
    assert "An earlier re-verification could not reach the target" in block
    assert "stores the hash" in block, "the reason must be carried over"


def test_a_clean_reproduction_is_not_qualified():
    """The direction that keeps the note from appearing on every finding:
    with one attempt and no inconclusive in the history, nothing is added,
    because qualifying a clean result is its own form of misreporting."""
    from argus.report import hackerone as h1
    from argus.report import markdown as md

    one = {"outcome": "reproduced", "reason": "the bytes came back"}
    f = _finding(replays=[one], replay=one)

    badges = h1._badges(f)   # an assembled HTML string, not a list
    assert "RE-VERIFIED: REPRODUCED" in badges
    assert "COULD NOT ASK" not in badges

    block = "\n".join(md._proof_block(f))
    assert "An earlier re-verification" not in block


def test_a_failure_still_outranks_everything():
    """Unchanged: a target that answered and did not produce the bytes is a
    one-way door, and an earlier inconclusive does not soften it."""
    from argus.report import hackerone as h1

    hist = [{"outcome": "inconclusive", "reason": "could not ask"},
            {"outcome": "not_reproduced", "reason": "answered 200, no bytes"},
            {"outcome": "reproduced", "reason": "came back later"}]
    badges = h1._badges(_finding(replays=hist, replay=hist[-1]))
    assert "DID NOT REPRODUCE" in badges
    assert "RE-VERIFIED: REPRODUCED" not in badges
