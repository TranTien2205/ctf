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
