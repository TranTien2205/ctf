"""Do the probes and the proof matrix agree about the same evidence?

Every verifier fixed in this tree exposed a defect in the probe that feeds it,
always the same shape: the probe reported a signal it could not prove, because
nobody had read the requirement while writing it.

* `probe_crlf` reported a header injection and sent no control, so its
  evidence could never satisfy "a control response does not carry it".
* `probe_method` looked for the canary *filename* in the read-back while
  writing a fixed string, so a PUT that really landed read as unverified.
* `probe_upload` called a `.svg` served as `text/plain` an upload candidate,
  conflating "an active type was stored" with "it is served as something a
  browser runs".

Those were found one at a time, by hand, while writing each verifier. This
module finds the whole class at once and keeps finding it: drive each probe
against the lab and grade the exchanges it recorded under its own class.

Two directions, and no reading of the probe's prose - a verdict is English and
this asserts against evidence:

* **VULNERABLE** - the lab really has this bug at this endpoint, so some
  honest quote from what the probe recorded must reach `proven` (or the
  class's ceiling). A probe that cannot get there is not collecting what the
  requirement names, whatever its verdict says.
* **CLEAN** - the same probe against an endpoint without the bug must NOT
  reach `proven`. This is the direction that matters: it is the one that fails
  when a verifier is too loose rather than when a probe is too thin.
"""
from __future__ import annotations

import pytest

from argus import proof
from argus.decide import PROBE_CLASS
from argus.tools import probes

# (probe, class, callable) where the lab genuinely has the bug.
VULNERABLE = [
    ("probe_sqli", "sqli",
     lambda c, b: probes.probe_sqli(c, b + "/item?id=1", "id",
                                    extract_table="users",
                                    extract_columns="username,password")),
    ("probe_cmdi", "rce",
     lambda c, b: probes.probe_cmdi(c, b + "/ping?host=127.0.0.1", "host")),
    ("probe_ssti", "ssti",
     lambda c, b: probes.probe_ssti(c, b + "/hello?name=x", "name")),
    ("probe_lfi", "lfi",
     lambda c, b: probes.probe_lfi(c, b + "/download?file=x", "file")),
    ("probe_idor", "idor",
     lambda c, b: probes.probe_idor(c, b + "/api/user/2")),
    ("probe_disclosure", "disclosure", lambda c, b: probes.probe_disclosure(c, b)),
    ("probe_redirect", "redirect",
     lambda c, b: probes.probe_redirect(c, b + "/redirect?next=/", "next")),
    ("probe_crlf", "crlf",
     lambda c, b: probes.probe_crlf(c, b + "/redirect?next=/", "next")),
    ("probe_upload", "upload", lambda c, b: probes.probe_upload(c, b + "/upload")),
    ("probe_cors", "cors", lambda c, b: probes.probe_cors(c, b + "/api/data")),
    ("probe_websocket", "websocket",
     lambda c, b: probes.probe_websocket(c, b + "/ws")),
    ("probe_smuggle", "smuggle",
     lambda c, b: probes.probe_smuggle(c, b + "/desync")),
    ("probe_nosqli", "nosqli",
     lambda c, b: probes.probe_nosqli(
         c, b + "/api/login", '{"username":"admin","password":"x"}',
         "password")),
    ("probe_lockout", "lockout",
     lambda c, b: probes.probe_lockout(c, b + "/login2",
                                       "username=x&password=x")),
    # `/redeem` holds ONE coupon in a class variable shared by every test on
    # the session-scoped server, so reset it first or there is nothing to race
    ("probe_race", "race", lambda c, b: _race_or_skip(c, b)),
]


def _race_or_skip(ctx, base):
    """Drive the race probe, and skip if the environment serialised it.

    This is the one case here whose evidence depends on wall-clock
    concurrency, and on a loaded CI runner the burst does not always overlap -
    all three Windows jobs failed this way while Ubuntu passed. The verifier
    is RIGHT to refuse then: a burst the server serialised cannot evidence a
    race, and `probe_race` says so itself with `overlapped: false` and an
    "inconclusive" verdict. Asserting that a timing-dependent probe always
    proves would be asserting something the probe does not claim, so the
    honest test is conditional on the probe having actually overlapped. The
    unconditional assertions for this class are synthetic, in
    `tests/test_proof.py`.
    """
    ctx.client.send("GET", base + "/redeem/reset", tool="http_request",
                    note="reset the coupon")
    out = probes.probe_race(ctx, base + "/redeem", n=8)
    if not out.get("overlapped"):
        pytest.skip(f"the burst did not overlap here, so there is no race to "
                    f"grade: {out.get('verdict', '')[:90]}")
    return out

# The same probes where the lab has no such bug. `proven` here would be the
# verifier accepting something it should refuse.
CLEAN = [
    ("probe_sqli", "sqli",
     lambda c, b: probes.probe_sqli(c, b + "/search?q=widget", "q")),
    ("probe_cmdi", "rce",
     lambda c, b: probes.probe_cmdi(c, b + "/search?q=widget", "q")),
    ("probe_ssti", "ssti",
     lambda c, b: probes.probe_ssti(c, b + "/search?q=widget", "q")),
    ("probe_lfi", "lfi",
     lambda c, b: probes.probe_lfi(c, b + "/search?q=widget", "q")),
    ("probe_crlf", "crlf",
     lambda c, b: probes.probe_crlf(c, b + "/search?q=widget", "q")),
    ("probe_redirect", "redirect",
     lambda c, b: probes.probe_redirect(c, b + "/search?q=widget", "q")),
    ("probe_nosqli", "nosqli",
     lambda c, b: probes.probe_nosqli(
         c, b + "/search?q=widget", '{"q":"widget"}', "q")),
    # `/ws-strict` is the same endpoint with the Origin check in place: the
    # probe's foreign Origin is refused before the upgrade, which is the
    # defence working and must not grade
    ("probe_websocket", "websocket",
     lambda c, b: probes.probe_websocket(c, b + "/ws-strict")),
    # `/desync-none` agrees with itself about framing: the ambiguous request
    # gets a clean follow-up, which is the defence working
    ("probe_smuggle", "smuggle",
     lambda c, b: probes.probe_smuggle(c, b + "/desync-none")),
    # `/login3` throttles after a few tries - the lockout working
    ("probe_lockout", "lockout",
     lambda c, b: probes.probe_lockout(c, b + "/login3",
                                       "username=x&password=x")),
    # `/hello` is repeatable: a burst succeeding there is the action working,
    # not a limited one crossed
    ("probe_race", "race",
     lambda c, b: probes.probe_race(c, b + "/hello", n=6)),
]
# `cors` has no clean case here: the lab reflects any `Origin` with
# credentials from the shared response helper, so every endpoint is
# vulnerable - including `/hello`, which this module was asserting as clean
# until it failed. `/safedirect` is not clean either; it is the deliberate
# "filter that allows //host" bypass. Both were my guesses and both were
# wrong, which is the layer working on its author. The synthetic refusal
# cases for those classes live in `tests/test_proof.py`.

_ORDER = {"proven": 3, "candidate": 2, "unproven": 1, "refused": 0}


def _exchanges(session) -> list[dict]:
    return [e for e in session._transcript.values()
            if isinstance(e.get("response"), dict)]


def _best_grade(klass: str, entries: list[dict]) -> tuple[str, list[str]]:
    """The best grade any honest quote from this evidence can reach.

    A probe does not choose the excerpt - the agent does - so the question is
    whether *some* quote a tester would take satisfies the requirement. Lines
    are what a tester takes, which is also why a whole body is not offered:
    handing the matrix an entire response defeats its own echo veto.
    """
    best, missing = "unproven", ["no evidence"]
    for entry in entries:
        body = proof.resp_body(entry)
        quotes = [ln.strip() for ln in body.splitlines()
                  if 8 <= len(ln.strip()) <= 400]
        whole = body.strip()
        if whole and len(whole) <= 400:
            quotes.append(whole)
        for quote in quotes[:25]:
            verdict = proof.grade(klass, quote, entries)
            if _ORDER.get(verdict.grade, 0) > _ORDER.get(best, 0):
                best, missing = verdict.grade, verdict.missing
            if best == "proven":
                return best, []
    return best, missing


@pytest.mark.parametrize("name,klass,call", VULNERABLE,
                         ids=[f"{n}-{k}" for n, k, _ in VULNERABLE])
def test_the_probe_collects_what_its_class_requires(
        name, klass, call, lab_url, ctx):
    spec = proof.spec_for(klass)
    assert spec is not None, f"{name} maps to {klass!r}, not a matrix class"
    before = len(_exchanges(ctx.session))
    call(ctx, lab_url)
    entries = _exchanges(ctx.session)[before:]
    assert entries, f"{name} recorded no exchange at all"

    grade, missing = _best_grade(klass, entries)
    want = spec.ceiling or "proven"
    assert _ORDER[grade] >= _ORDER[want], (
        f"{name} ran against a {klass} the lab really has, and nothing it "
        f"recorded grades `{want}`.\n"
        f"  reached:     {grade}\n"
        f"  requirement: {spec.requirement}\n"
        f"  missing:     {missing}\n"
        f"Either the probe is not collecting what the class needs, or the "
        f"requirement names something no probe produces.")


@pytest.mark.parametrize("name,klass,call", CLEAN,
                         ids=[f"{n}-{k}" for n, k, _ in CLEAN])
def test_the_matrix_refuses_a_probe_run_on_a_clean_endpoint(
        name, klass, call, lab_url, ctx):
    before = len(_exchanges(ctx.session))
    call(ctx, lab_url)
    entries = _exchanges(ctx.session)[before:]
    assert entries, f"{name} recorded no exchange at all"
    grade, _ = _best_grade(klass, entries)
    assert grade != "proven", (
        f"{name} against an endpoint with no {klass} produced evidence that "
        f"grades `proven`. That is the verifier accepting something it should "
        f"refuse - the search box that echoes its query, in whatever form it "
        f"has taken this time.")


def test_every_driven_probe_exists_and_maps_to_a_real_class():
    from argus.tools import registry
    known = {t["name"] for t in registry.TOOL_SCHEMAS}
    for name, klass, _ in VULNERABLE + CLEAN:
        assert name in known, f"{name} is driven here but is not a tool"
        assert PROBE_CLASS.get(name) == klass, (
            f"{name} is driven as {klass!r} but decide.PROBE_CLASS says "
            f"{PROBE_CLASS.get(name)!r}")


def test_both_directions_are_exercised_for_the_classes_that_have_both():
    """A one-directional case proves little. Name the overlap explicitly so
    removing one half is visible."""
    vulnerable = {k for _, k, _ in VULNERABLE}
    clean = {k for _, k, _ in CLEAN}
    both = vulnerable & clean
    assert {"sqli", "rce", "ssti", "lfi", "crlf", "redirect",
            "websocket", "smuggle", "nosqli", "lockout", "race"} <= both, (
        f"classes exercised in both directions: {sorted(both)}")
