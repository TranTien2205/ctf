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
    assert "not performed" in blank.lower()
    assert "another family" in blank

    agreed = html_mod._judge_html(_finding(
        judge={"judge_model": "other-1", "agrees": True, "reason": "ok"}))
    assert "not performed" not in agreed.lower()


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
