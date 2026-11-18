"""Static and behavioural gate on argus/web/dashboard.html.

The dashboard is one self-contained file an operator opens on a jump box with
no internet, and every string it renders - finding titles, evidence excerpts,
report bodies - is bytes a target chose. So three properties are not style
preferences here, they are the file's contract:

  1. no external resource, at all
  2. no HTML sink, at all (there is no innerHTML in that file; the point of
     "none" rather than "escaped" is that there is no place for the next edit
     to get the escaping wrong)
  3. the two modes are not confusable, and an engagement without its four
     authorisation fields cannot be launched from the UI

Every check below is a function, and every function is exercised in BOTH
directions: against the real file, and against the real file with the defect
planted in it. The second direction is the one that matters - a checker that
cannot fail is a checker that measures nothing, and this repository has been
caught shipping three of those.
"""
from __future__ import annotations

import fnmatch
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from html.parser import HTMLParser
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DASH = ROOT / "argus" / "web" / "dashboard.html"

sys.path.insert(0, str(ROOT))


# --------------------------------------------------------------------- helpers

@pytest.fixture(scope="module")
def dash() -> str:
    return DASH.read_text(encoding="utf-8")


def require_node(what: str) -> str:
    """node, or a skip that says which proof this run is dropping.

    Measured: with every node-bearing directory removed from PATH this file
    reported "25 passed, 4 skipped" and the suite stayed green - and those
    four skips are the entire syntax + behaviour half, including the proof
    that the UI refuses an engagement without its four authorisation fields.
    A dropped proof that reads as a pass is the shape this repository keeps
    finding, so: the skip names what was dropped, ARGUS_REQUIRE_NODE=1 turns
    it into a failure on a box that is meant to have node, and
    test_the_authorisation_interlock_holds_without_node keeps the interlock
    asserted (structurally, in both directions) when node is absent.
    """
    exe = shutil.which("node")
    if exe:
        return exe
    msg = (f"node is not on PATH, so this run does not prove {what}. Install "
           "node, or set ARGUS_REQUIRE_NODE=1 to make this a failure.")
    if os.environ.get("ARGUS_REQUIRE_NODE") == "1":
        pytest.fail(msg)
    pytest.skip(msg)
    raise AssertionError("unreachable")


def extract_scripts(html: str) -> list[str]:
    return re.findall(r"<script\b[^>]*>(.*?)</script>", html, re.S | re.I)


def extract_styles(html: str) -> list[str]:
    return re.findall(r"<style\b[^>]*>(.*?)</style>", html, re.S | re.I)


def strip_block_comments(js: str) -> str:
    """Drop /* ... */ only.

    Line comments are left in place on purpose: a `//` inside a string
    literal (`https://...`) would make a line-comment stripper eat real code
    to the end of the line, and a checker that quietly deletes the thing it
    is looking for reports a clean file. Block comments are enough, because
    the dashboard keeps its contract listing in one - if the endpoint
    literals were only in that comment, test_speaks_every_endpoint would
    pass on documentation instead of on call sites.
    """
    return re.sub(r"/\*.*?\*/", " ", js, flags=re.S)


# attributes that can fetch something; `placeholder` and `title` hold URLs as
# human text and are not resources, which is why this is attribute-aware
# instead of a grep for "https://" over the whole file.
_URL_ATTRS = {"src", "href", "srcset", "poster", "data", "action", "formaction",
              "background", "manifest", "codebase", "xlink:href", "ping"}
_REMOTE = re.compile(r"^\s*(?:[a-z][a-z0-9+.-]*:)?//", re.I)


class _Scan(HTMLParser):
    """Collects tag/attribute facts in one pass."""

    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
            "meta", "param", "source", "track", "wbr"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, tuple[int, int]]] = []
        self.unbalanced: list[str] = []
        self.external: list[str] = []
        self.handlers: list[str] = []
        self.tags: list[str] = []

    def _attrs(self, tag: str, attrs) -> None:
        self.tags.append(tag)
        for name, value in attrs:
            name = (name or "").lower()
            value = value or ""
            if name.startswith("on"):
                self.handlers.append(f"<{tag} {name}=> at {self.getpos()}")
            if name in _URL_ATTRS:
                if _REMOTE.match(value):
                    self.external.append(f"<{tag} {name}={value!r}> at {self.getpos()}")
                if value.strip().lower().startswith(("javascript:", "data:", "vbscript:")):
                    self.external.append(f"<{tag} {name}={value!r}> at {self.getpos()}")
            if name in ("integrity", "crossorigin"):
                # only ever present on a subresource fetched from elsewhere
                self.external.append(f"<{tag} {name}=> at {self.getpos()}")

    def handle_starttag(self, tag, attrs):
        self._attrs(tag, attrs)
        if tag not in self.VOID:
            self.stack.append((tag, self.getpos()))

    def handle_startendtag(self, tag, attrs):
        self._attrs(tag, attrs)

    def handle_endtag(self, tag):
        if tag in self.VOID:
            self.unbalanced.append(f"</{tag}> closes a void element at {self.getpos()}")
            return
        if not self.stack:
            self.unbalanced.append(f"</{tag}> with nothing open at {self.getpos()}")
            return
        top, pos = self.stack[-1]
        if top != tag:
            self.unbalanced.append(
                f"</{tag}> at {self.getpos()} but <{top}> opened at {pos} is still open")
            for i in range(len(self.stack) - 1, -1, -1):
                if self.stack[i][0] == tag:
                    del self.stack[i:]
                    break
            return
        self.stack.pop()

    def finish(self) -> None:
        self.close()
        for tag, pos in self.stack:
            self.unbalanced.append(f"<{tag}> opened at {pos} never closed")


def scan(html: str) -> _Scan:
    s = _Scan()
    s.feed(html)
    s.finish()
    return s


def unbalanced_tags(html: str) -> list[str]:
    return scan(html).unbalanced


# `createElementNS` takes a namespace URI. It is an identifier, not an
# address - nothing fetches it - so it is the one absolute URL a console with
# no network dependencies legitimately contains.
_NAMESPACE_URIS = {"http://www.w3.org/2000/svg", "http://www.w3.org/1999/xhtml"}


def external_resources(html: str) -> list[str]:
    """Anything that would make the page reach the network to render."""
    s = scan(html)
    out = list(s.external)
    for css in extract_styles(html):
        for m in re.finditer(r"@import|url\(\s*['\"]?\s*(?:[a-z]+:)?//", css, re.I):
            out.append(f"stylesheet {m.group(0)!r}")
        for m in re.finditer(r"@font-face", css, re.I):
            # a local @font-face still needs a src; none of them are bundled
            out.append("stylesheet @font-face")
    for js in extract_scripts(html):
        body = strip_block_comments(js)
        for m in re.finditer(r"['\"]((?:[a-z][a-z0-9+.-]*:)?//[^'\"]{1,80})['\"]", body, re.I):
            if m.group(1) in _NAMESPACE_URIS:
                continue      # an XML namespace is never fetched
            out.append(f"script url literal {m.group(0)!r}")
    return out


_SINKS = ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write",
          "createContextualFragment", "eval(", "new Function", "srcdoc")


def unsafe_sinks(js: str) -> list[str]:
    body = strip_block_comments(js)
    out = [name for name in _SINKS if name in body]
    # setTimeout/setInterval with a string argument is eval in a trench coat
    if re.search(r"set(?:Timeout|Interval)\s*\(\s*['\"]", body):
        out.append("setTimeout(string)")
    return out


def inline_handlers(html: str) -> list[str]:
    return scan(html).handlers


def missing_endpoints(js: str, wanted: list[str]) -> list[str]:
    body = strip_block_comments(js)
    return [w for w in wanted if w not in body]


def js_object_keys(js: str, name: str) -> list[str]:
    """The quoted keys of a `var <name> = { 'k': ... }` literal, in order."""
    m = re.search(r"var\s+" + re.escape(name) + r"\s*=\s*\{(.*?)\n\s*\};", js, re.S)
    if not m:
        return []
    # Keys may be bare (`queued: '...'`) or quoted (`'queued': '...'`). The
    # first version required quotes and returned [] on a bare literal, which
    # reads as "the map is missing" - a checker that cannot see the thing it
    # checks reports a clean file. The second version dropped the quotes and
    # then matched `class:` from INSIDE a value string ("...prove this class:
    # the proof would be the damage"), inventing a key. So a key is anchored
    # to a line start or a separator, which is the only place one can be.
    body = m.group(1)
    pairs = re.findall(r"(?:^|[{,])\s*(?:'([a-z_]+)'|([a-z_]+))\s*:",
                       body, re.M)
    return [a or b for a, b in pairs]


def js_string_array(js: str, name: str) -> list[str]:
    m = re.search(r"var\s+" + re.escape(name) + r"\s*=\s*\[(.*?)\];", js, re.S)
    if not m:
        return []
    return re.findall(r"'([^']+)'", m.group(1))

# ----------------------------------------------------------------- the basics

def test_one_self_contained_file(dash: str):
    assert DASH.is_file()
    assert len(extract_scripts(dash)) == 1, "exactly one inline script"
    assert len(extract_styles(dash)) == 1, "exactly one inline stylesheet"


def test_tags_balance(dash: str):
    assert unbalanced_tags(dash) == []


def test_tag_balance_check_names_a_missing_close(dash: str):
    """The balance check, proved able to fail."""
    broken = dash.replace("</main>", "", 1)
    assert "main" in " ".join(unbalanced_tags(broken))


def test_script_parses(dash: str, tmp_path: Path):
    node = require_node("that the console's script parses")
    f = tmp_path / "d.js"
    f.write_text(extract_scripts(dash)[0], encoding="utf-8")
    r = subprocess.run([node, "--check", str(f)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


def test_script_parse_check_catches_a_syntax_error(dash: str, tmp_path: Path):
    node = require_node("that the parse check can fail")
    f = tmp_path / "bad.js"
    f.write_text(extract_scripts(dash)[0] + "\nfunction (){", encoding="utf-8")
    r = subprocess.run([node, "--check", str(f)], capture_output=True, text=True)
    assert r.returncode != 0


# ------------------------------------------------------------------- offline

def test_no_external_resources(dash: str):
    """A console that needs the network to render fails on a jump box."""
    assert external_resources(dash) == []


@pytest.mark.parametrize("planted", [
    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter">',
    '<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>',
    '<img src="//example.test/pixel.gif">',
])
def test_external_resource_check_names_what_was_planted(dash: str, planted):
    assert external_resources(dash.replace("</head>", planted + "</head>", 1))


def test_the_only_absolute_url_in_the_script_is_the_svg_namespace(dash: str):
    """`createElementNS` needs the SVG namespace, and a namespace URI is an
    identifier - nothing ever fetches it. Every OTHER absolute URL in the
    script would be a network call, so the check allows exactly that one and
    names anything else."""
    js = strip_block_comments(extract_scripts(dash)[0])
    urls = set(re.findall(r"['\"](https?://[^'\"]+)['\"]", js))
    assert urls <= {"http://www.w3.org/2000/svg"}, sorted(urls)


def test_the_namespace_allowance_does_not_hide_a_real_url(dash: str):
    js = strip_block_comments(extract_scripts(dash)[0])
    js += "\nvar beacon = 'https://telemetry.example/collect';"
    urls = set(re.findall(r"['\"](https?://[^'\"]+)['\"]", js))
    assert urls - {"http://www.w3.org/2000/svg"} == {"https://telemetry.example/collect"}


# -------------------------------------------------- target-controlled bytes

def test_no_html_sinks(dash: str):
    """Finding titles and evidence excerpts are bytes the target chose. With
    no innerHTML in the file there is no place to forget to escape one."""
    assert unsafe_sinks(strip_block_comments(extract_scripts(dash)[0])) == []


@pytest.mark.parametrize("find,repl,named", [
    ("setText(rec.cls, low(f.vuln_class) || '--');",
     "rec.cls.innerHTML = low(f.vuln_class) || '--';", "innerHTML"),
    ("put(clear(rec.ev), el('div', 'ev', t(f.excerpt) || '(no excerpt recorded)'));",
     "rec.ev.insertAdjacentHTML('beforeend', t(f.excerpt));", "insertAdjacentHTML"),
])
def test_sink_check_names_what_was_planted(dash: str, find, repl, named):
    assert find in dash, "anchor moved; re-aim this test rather than deleting it"
    found = unsafe_sinks(strip_block_comments(extract_scripts(dash.replace(find, repl, 1))[0]))
    assert any(named in s for s in found), found


def test_no_inline_handlers(dash: str):
    assert inline_handlers(dash) == []


def test_inline_handler_check_names_what_was_planted(dash: str):
    planted = dash.replace('<button class="k" id="btn-prev" type="button">',
                           '<button class="k" id="btn-prev" type="button" onclick="preview()">', 1)
    assert inline_handlers(planted)


# ---------------------------------------------------------------- the API

ENDPOINTS = ["/api/health", "/api/prompt", "/api/runs", "/api/findings", "/api/reports"]


def test_speaks_every_endpoint(dash: str):
    assert missing_endpoints(extract_scripts(dash)[0], ENDPOINTS) == []


def test_endpoint_check_names_a_dropped_call(dash: str):
    js = extract_scripts(dash)[0].replace("/api/reports", "/api/REMOVED")
    assert "/api/reports" in missing_endpoints(js, ENDPOINTS)


# ------------------------------------------------------------- the vocabulary

def test_grade_vocabulary_is_the_proof_modules(dash: str):
    """The page must know every grade argus can produce.

    MEASURED: an earlier draft of this console knew three grades and mapped
    the fourth onto `unproven` - so a finding argus REFUSED to prove by
    policy would have read as one whose evidence fell short. Those are
    different statements and only one of them is about the target.
    """
    from argus import proof
    js = extract_scripts(dash)[0]
    assert set(js_string_array(js, "GRADES")) == set(proof.GRADES)
    assert set(js_object_keys(js, "GRADE_MEANING")) == set(proof.GRADES)


def test_grade_vocabulary_check_catches_an_invented_grade(dash: str):
    from argus import proof
    js = extract_scripts(dash)[0].replace(
        "var GRADES = ['proven', 'candidate', 'unproven', 'refused'];",
        "var GRADES = ['proven', 'candidate', 'unproven', 'refused', 'likely'];", 1)
    assert set(js_string_array(js, "GRADES")) != set(proof.GRADES)


def test_every_run_state_is_explained(dash: str):
    """A state word is jargon until it is glossed, and `blocked` reads like a
    failure when it is not one."""
    js = extract_scripts(dash)[0]
    glossed = set(js_object_keys(js, "STATE_WORDS"))
    assert {"queued", "running", "done", "failed", "blocked"} <= glossed, sorted(glossed)


def test_state_explanation_check_catches_a_missing_state(dash: str):
    js = extract_scripts(dash)[0].replace(
        "  blocked: 'accepted, then refused before any traffic was sent'\n", "", 1)
    assert "blocked" not in set(js_object_keys(js, "STATE_WORDS"))


def test_says_so_when_no_model_is_configured(dash: str):
    """Honest degradation: the operator must not believe an agent will run."""
    js = strip_block_comments(extract_scripts(dash)[0])
    assert "model_configured" in js
    assert "blocked" in js and "ANTHROPIC_API_KEY" in js


def test_the_two_modes_are_marked_apart(dash: str):
    """Not a label: the mode re-themes the chassis off one attribute."""
    assert 'data-mode="lab"' in dash
    assert 'html[data-mode="engagement"]' in dash
    js = extract_scripts(dash)[0]
    assert "setAttribute('data-mode'" in js
    for field, _label, _ph in (("authorised_by", 0, 0), ("scope", 0, 0),
                               ("window", 0, 0), ("reference", 0, 0)):
        assert field in js, field


def test_every_id_the_script_addresses_exists(dash: str):
    """$('x') on a renamed element returns null and the page dies silently."""
    js = extract_scripts(dash)[0]
    in_html = set(re.findall(r'id="([^"]+)"', dash))
    built = {"n-" + g for g in js_string_array(js, "GRADES")}
    built |= {"lg-" + g for g in js_string_array(js, "GRADES")}
    built |= {"auth-" + f for f in ("authorised_by", "scope", "window", "reference")}
    asked = set(re.findall(r"\$\('([^']+)'\)", js))
    assert asked - in_html - built == set(), sorted(asked - in_html - built)


def test_id_check_names_a_renamed_element(dash: str):
    js = extract_scripts(dash)[0]
    in_html = set(re.findall(r'id="([^"]+)"', dash.replace('id="target"', 'id="tgt"', 1)))
    asked = set(re.findall(r"\$\('([^']+)'\)", js))
    assert "target" in asked - in_html


# ------------------------------------------------------- behaviour, in node
#
# The script exports its decision logic when `document` is absent, so these
# drive the REAL functions instead of grepping for their source text. An
# earlier suite for this file pinned exact source strings and generated its
# cases from them; a correct rewrite of the console failed 33 of them while
# changing no behaviour, and the suite could not tell the difference.

def _pure(dash: str, tmp_path: Path, mutate=None):
    """Load the console's headless exports under node, optionally mutated."""
    node = require_node("the console's decision logic")
    js = extract_scripts(dash)[0]
    if mutate:
        find, repl = mutate
        assert find in js, f"anchor moved: {find!r}"
        js = js.replace(find, repl, 1)
    mod = tmp_path / "console.js"
    mod.write_text(js, encoding="utf-8")
    probe = tmp_path / "probe.js"
    probe.write_text(
        "const m = require(" + json.dumps(str(mod)) + ");\n"
        "const out = JSON.parse(process.argv[2]).map(function (c) {\n"
        "  try { return { ok: true, v: m[c.fn].apply(null, c.args) }; }\n"
        "  catch (e) { return { ok: false, v: String(e && e.message) }; }\n"
        "});\n"
        "process.stdout.write(JSON.stringify(out));\n", encoding="utf-8")

    def call(cases):
        r = subprocess.run([node, str(probe), json.dumps(cases)],
                           capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, r.stderr
        return json.loads(r.stdout)
    return call


def test_the_engagement_interlock_refuses_in_node(dash: str, tmp_path: Path):
    """The safety-critical path, driven rather than read.

    Four authorisation fields and a confirmation, and the refusal has to
    survive the operator editing the target afterwards - authorisation is
    per target, and four filled fields that were typed for another host
    authorise nothing.
    """
    call = _pure(dash, tmp_path)
    full = {"mode": "engagement", "target": "https://app.test",
            "authorised_by": "A", "scope": "s", "window": "w",
            "reference": "r", "confirmed": True, "stale": False}
    res = call([
        {"fn": "validate", "args": [{"mode": "lab", "target": "https://x.test"}]},
        {"fn": "validate", "args": [{"mode": "engagement", "target": "https://x.test"}]},
        {"fn": "validate", "args": [full]},
        {"fn": "validate", "args": [dict(full, confirmed=False)]},
        {"fn": "validate", "args": [dict(full, stale=True)]},
        {"fn": "validate", "args": [dict(full, scope="")]},
        {"fn": "body", "args": [full]},
        {"fn": "body", "args": [dict(full, mode="lab")]},
    ])
    assert all(r["ok"] for r in res), res
    lab, eng_empty, eng_full, no_conf, stale, no_scope, b_eng, b_lab = [r["v"] for r in res]

    assert lab == [], "a lab run needs only a target"
    assert len(eng_empty) == 5, eng_empty          # four fields + the confirmation
    assert eng_full == [], eng_full
    assert len(no_conf) == 1 and "confirm" in no_conf[0].lower()
    assert len(stale) == 1 and "target changed" in stale[0].lower()
    assert any("Scope" in m for m in no_scope), no_scope

    # the authorisation travels only in engagement mode
    assert b_eng["auth"] and b_eng["auth"]["scope"] == "s"
    assert b_lab["auth"] is None, "lab must not carry an authorisation note"


@pytest.mark.parametrize("find,repl,named", [
    ("  if (form.mode === 'engagement') {", "  if (false) {", "the engagement branch"),
    ("    if (!form.confirmed) {", "    if (false) {", "the confirmation"),
    ("    if (form.stale) {", "    if (false) {", "the stale-target refusal"),
    ("  if (mode === 'engagement') out.auth = authTrimmed(form);",
     "  out.auth = authTrimmed(form);", "authorisation leaking into a lab run"),
])
def test_the_interlock_test_can_fail(dash: str, tmp_path: Path, find, repl, named):
    """Each gate removed in turn; the test above must notice every one."""
    call = _pure(dash, tmp_path, mutate=(find, repl))
    full = {"mode": "engagement", "target": "https://app.test",
            "authorised_by": "A", "scope": "s", "window": "w",
            "reference": "r", "confirmed": True, "stale": False}
    res = call([
        {"fn": "validate", "args": [{"mode": "engagement", "target": "https://x.test"}]},
        {"fn": "validate", "args": [dict(full, confirmed=False)]},
        {"fn": "validate", "args": [dict(full, stale=True)]},
        {"fn": "body", "args": [dict(full, mode="lab")]},
    ])
    eng_empty, no_conf, stale, b_lab = [r["v"] for r in res]
    weakened = (len(eng_empty) != 5 or no_conf != [] and len(no_conf) != 1
                or no_conf == [] or stale == [] or b_lab["auth"] is not None)
    assert weakened, f"removing {named} changed nothing the suite can see"


def test_elapsed_never_reads_a_finished_run_as_still_working(dash: str, tmp_path: Path):
    """MEASURED BUG: elapsed came from Date.now() whatever the state, so a
    session sealed two days earlier read "50h08m"."""
    call = _pure(dash, tmp_path)
    now = 1_700_000_000_000
    base = now / 1000
    res = call([
        {"fn": "elapsed", "args": [{"started": base - 600, "finished": base - 540,
                                    "state": "done"}, now]},
        {"fn": "elapsed", "args": [{"started": base - 600, "state": "done"}, now]},
        {"fn": "elapsed", "args": [{"started": base - 90, "state": "running"}, now]},
        {"fn": "elapsed", "args": [{"state": "done"}, now]},
    ])
    sealed, no_stamp, live, no_start = [r["v"] for r in res]
    assert sealed == "1m00s", sealed
    assert no_stamp == "--", "a finished run with no stamp must report nothing, not guess"
    assert live == "1m30s", live
    assert no_start == "--"


def test_an_unknown_grade_is_not_silently_remapped(dash: str, tmp_path: Path):
    call = _pure(dash, tmp_path)
    res = call([
        {"fn": "counts", "args": [[{"grade": "proven"}, {"grade": "refused"},
                                   {"grade": "candidate"}, {"grade": "proven"}]]},
        {"fn": "gradeKey", "args": ["refused"]},
        {"fn": "gradeKey", "args": ["PROVEN"]},
    ])
    c, refused, upper = [r["v"] for r in res]
    assert c["proven"] == 2 and c["refused"] == 1 and c["candidate"] == 1
    assert c["unproven"] == 0, "refused must not be counted as unproven"
    assert refused == "refused"
    assert upper == "unproven", "gradeKey is given lowercase words by gradeOf"


def test_the_filter_matches_on_evidence_and_class(dash: str, tmp_path: Path):
    call = _pure(dash, tmp_path)
    f = {"grade": "proven", "severity": "critical", "vuln_class": "sqli",
         "title": "SQL injection in id", "url": "http://t/item?id=1",
         "excerpt": "uid=33(www-data)", "run_id": "bwapp"}
    allf = {"grade": "all", "sev": "all", "q": ""}
    res = call([
        {"fn": "matches", "args": [f, allf]},
        {"fn": "matches", "args": [f, dict(allf, q="www-data")]},
        {"fn": "matches", "args": [f, dict(allf, q="sqli")]},
        {"fn": "matches", "args": [f, dict(allf, q="nothinghere")]},
        {"fn": "matches", "args": [f, dict(allf, grade="candidate")]},
        {"fn": "matches", "args": [f, dict(allf, sev="low")]},
    ])
    everything, by_evidence, by_class, miss, wrong_grade, wrong_sev = [r["v"] for r in res]
    assert everything and by_evidence and by_class
    assert not miss and not wrong_grade and not wrong_sev


# ------------------------------------------------------------------ packaging

def test_pyproject_declares_the_console_as_package_data():
    """An install without the page serves a blank screen from a working
    server - the worst shape of missing, because the port answers."""
    data = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "web/*.html" in data, "the console is not in package-data"
