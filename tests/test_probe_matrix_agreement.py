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

It also had the defect it exists to find. The proving table covered fourteen
classes - every class whose verifier had been written here - and the lab
plants nine more that nothing drove. Extending it found two real defects and
one in this module:

* `verify_restricted_access` could not prove the variant its own alias is
  named after. It required the refusal to be on the SAME path as the bypass,
  which is true of IP spoofing and false of `X-Original-URL`, where the
  request line asks an allowed path and the header names the forbidden one.
  Those paths cannot be equal, so the shape the lab plants was unprovable.
* `probe_xfh` built the restricted URL by putting `restricted` into the path
  component, so a caller passing a URL - which an agent naturally does - got
  `http://host/http://host/admin`, a 404. The probe's whole second half ran
  against a page that was never restricted. It also sent no control without
  the header, which the requirement needs.
* `probe_enum` sent each username exactly once while `verify_oracle` asks
  that each answer be observed more than once - and its docstring asserted
  the probe "sends a known and an unknown account, more than once". It did
  not. One difference is a coincidence; the probe repeats it now.
* `_best_grade` offered only whole lines, and `ppoll` and `cache` are proven
  by quoting the marker alone - the verifier asks that the excerpt appear
  verbatim in the poisoning REQUEST, where the surrounding markup is not.
  Both read as probe failures while probe and matrix actually agreed.

`csrf` was the fourth defect, and the only one in the loose direction. The
probe collected two of the four checks - no foreign Origin, no before/after
pair - so it got a foreign `Origin`/`Referer`, a `read_url` to bracket the
write with, and the form content type a cross-origin form actually sends.
It then graded `proven` on the quote `{"theme": "dark", "lang": "en"}`:
the body BEFORE the write. `verify_state_change` never checked the order of
its own two reads, so quoting the pre-write state and citing a later read
that no longer carried it satisfied "the state changed between two reads" -
which any site whose two reads differ can satisfy.

The clean direction had the same asymmetry the proving one did - 11 entries
against 24 - and driving the nine new classes against a measured-clean
endpoint found the fifth defect, also in the loose direction:
`verify_mass_assignment` accepted ANY response body as the read-back, so a
write that merely mentioned `role` and got a 200, paired with any later
read, proved the class. `/api/order` drops every injected field and its own
probe says so; it graded `proven` on that endpoint's ordinary answer.

`graphql` and `jwt` had no row at all, and the reason they were missed is
the same counting error: neither is driven by a `probe_*` tool, so neither
appeared in any coverage figure derived from the probe table. Both were
already reachable - `graphql_introspect` sends the introspection query and
the GET fallback under its own name, and `jwt` is `jwt_decode` recovering
the weak HMAC secret offline, `jwt_forge` minting a token, then three plain
requests. Driving them found two more things:

* `graphql` was absent from `decide.PROBE_CLASS`, so the ledger attributed
  none of `graphql_introspect`'s exchanges to the class. A run could call it
  five times and `argus next` would still say the class had never been
  probed - the per-class budget never counted it and rule 6 never offered
  its evidence. That is exactly the drift the decision controller exists to
  prevent.
* This module could not have graded `jwt` even with a row, because
  `_exchanges` filters the transcript to entries carrying a response - and
  `jwt`'s first requirement, "this system minted the credential", is made
  of the `jwt_forge` EVENT and nothing else. Measured: the same evidence
  grades `unproven` on the exchanges and `proven` on the full set. Grading
  now sees the events; quotes still come from responses only.

`deserialize` was on that list and came off it. The claim was that
`/import` returns a parser error and never executes, so the class was
unprovable here - which was true of the lab and not of the class, and the
fix needed no new capability: `/import` routes a gadget's command into the
SAME bounded executor `/ping` already uses (seven commands, no shell, no
path component, `cat` confined to the fake tree). A gadget carrying no
runnable command still gets the parser error, so "a surface is not
execution" stays a measurable distinction. The probe's gadget also had to
carry a nonce - it sent `['id']` - because the class is proven the way rce
is, and the first attempt used `_marker("deser")` while `NONCE_RE` is
`\bargus[a-z0-9]{4,24}\b`, so the token was unrecognisable as this probe's
own and the class sat at a candidate with its nonce in plain sight.

The proving direction covers 27 of the 29 proof classes. Two are not driven
in it: `dos`, refused by construction because its proof is the damage, and
`race`, whose live case was re-added and reverted again - see the note at its
place in the table. That sentence is a count, and the test at the bottom of this
module asserts it against the tables AND against the living documents that
repeat it - this docstring included, which is why the figure is stated here
in full rather than described.

Two directions, and no reading of the probe's prose - a verdict is English and
this asserts against evidence:

* **VULNERABLE** - the lab really has this bug at this endpoint, so some
  honest quote from what the probe recorded must reach `proven` (or the
  class's ceiling). A probe that cannot get there is not collecting what the
  requirement names, whatever its verdict says.
* **CLEAN** - the same probe against an endpoint without the bug must NOT
  reach `proven`. This is the direction that matters: it is the one that fails
  when a verifier is too loose rather than when a probe is too thin.

`race` has now been out, re-added, and taken out again - four rounds of
Windows CI. The lab side is fixed and tested: a barrier puts every request
inside the window and the endpoint's delay keeps each recorded window wide.
What is still unexplained is why `verify_race` finds no usable evidence at
all on Windows 3.10-3.12 while 3.13, 3.14 and every ubuntu job pass. See the
note at its place in the table.
"""
from __future__ import annotations

import re

import pytest

from argus import proof
from argus.decide import CLASS_TOOL_CHAIN, PROBE_CLASS
from argus.tools import analysis, probes, web

def _drive_race(c, b):
    """Arm the window, then drive the burst into it.

    `/redeem/reset?parties=6` holds every request on a barrier INSIDE the
    TOCTOU window - after the `coupons > 0` check, before the commit - so
    all six are past the guard before any of them commits. The endpoint
    then still sleeps, which is what keeps each recorded window wide enough
    for two of them to be shown overlapping. Both halves are server-side;
    see the note at this entry in the table.
    """
    c.client.send("GET", b + "/redeem/reset?parties=6",
                  tool="http_request", note="arm a 6-party race window")
    return probes.probe_race(c, b + "/redeem", n=6)


def _drive_jwt(c, b, *, forge: bool):
    """The jwt class is a chain, not a probe, which is why it was never here.

    `jwt_decode` and `jwt_forge` send nothing - they recover the weak HMAC
    secret offline and mint a token - so the wire part is three plain
    requests: mint a real token, present a credential, present another and
    be refused. With `forge=False` the credential presented is the server's
    OWN token, which is an auth system working and must not grade.
    """
    import json as _json

    r = c.client.send("GET", b + "/token?user=guest", tool="http_request",
                      note="mint a real token")
    token = _json.loads(r["body"] or "{}")["token"]
    present = token
    out = None
    if forge:
        decoded = analysis.jwt_decode(c, token)
        out = analysis.jwt_forge(
            c, token, claims='{"role":"admin"}',
            secret=decoded.get("recovered_secret") or "")
        present = out.get("resigned") or ""
    c.client.send("GET", b + "/api/me",
                  headers={"Authorization": f"Bearer {present}"},
                  tool="http_request",
                  note="credential presented on a privileged resource")
    c.client.send("GET", b + "/api/me",
                  headers={"Authorization": "Bearer not.a.token"},
                  tool="http_request",
                  note="control: another credential on the same endpoint")
    return out or {"presented": "the server's own token"}


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
    # Nine classes the lab plants that this table never drove. The gap was
    # invisible because the table looked complete: it covered every class
    # whose verifier had been WRITTEN here, not every class the lab plants.
    # Two of the nine were real defects - see the module docstring.
    ("probe_reflection", "xss",
     lambda c, b: probes.probe_reflection(c, b + "/hello?name=x", "name")),
    ("probe_ssrf", "ssrf",
     lambda c, b: probes.probe_ssrf(c, b + "/fetch?url=x", "url")),
    ("probe_xxe", "xxe", lambda c, b: probes.probe_xxe(c, b + "/xml")),
    # the read-back the class requires: /api/register/<id> serves what the
    # write stored, so the field is shown set rather than merely echoed
    ("probe_massassign", "massassign",
     lambda c, b: probes.probe_massassign(c, b + "/api/register",
                                          '{"username":"newguy"}',
                                          read_url=b + "/api/register")),
    ("probe_method", "method", lambda c, b: probes.probe_method(c, b + "/")),
    # `/reset` builds its form action from X-Forwarded-Host, and the edge
    # honours X-Original-URL while 403ing /admin directly - the pair the
    # xfh requirement names
    ("probe_xfh", "xfh",
     lambda c, b: probes.probe_xfh(c, b + "/reset", restricted="/admin")),
    ("probe_enum", "enum",
     lambda c, b: probes.probe_enum(c, b + "/login",
                                    "username=x&password=x")),
    ("probe_ppoll", "ppoll",
     lambda c, b: probes.probe_ppoll(c, b + "/api/config",
                                     b + "/api/config")),
    # the cache is a class variable keyed on path, so whoever reads /cached
    # first decides what everyone else is served - clear it, or this case
    # grades an earlier test's canary
    ("probe_cache", "cache",
     lambda c, b: (c.client.send("GET", b + "/cached/reset",
                                 tool="probe_cache", note="clear the cache"),
                   probes.probe_cache(c, b + "/cached"))[1]),
    # /api/config merges whatever a write sends into state a GET reads back,
    # so the before/after pair the csrf requirement needs is collectable
    ("probe_csrf", "csrf",
     lambda c, b: probes.probe_csrf(c, b + "/api/config", method="POST",
                                    data="csrfmark=landed",
                                    read_url=b + "/api/config")),
    # The two classes that had no row at all. Neither is driven by a
    # `probe_*` tool, which is the whole reason: `graphql_introspect` sends
    # the introspection query under its own name, and `jwt` is a chain of
    # two offline tools plus three plain requests.
    ("graphql_introspect", "graphql",
     lambda c, b: web.graphql_introspect(c, b + "/graphql")),
    ("jwt_forge", "jwt", lambda c, b: _drive_jwt(c, b, forge=True)),
    # `/import` routes a gadget's command into the SAME bounded executor
    # `/ping` uses - seven commands, no shell - so the class is proven the
    # way rce is, with the identity line and the probe's own nonce. A gadget
    # carrying no runnable command still gets the parser error, which is the
    # clean case below.
    ("probe_deserialize", "deserialize",
     lambda c, b: probes.probe_deserialize(c, b + "/import?data=x", "data")),
    # `race` was absent here for three rounds of Windows CI failures, and
    # the note that stood in its place ended "if you re-add a live proving
    # case here, expect it to fail on somebody else's machine". That warning
    # was right about the design it described, so here is what changed.
    #
    # Proving this class needed two things from the host, and both are now
    # taken away from it. That every request is inside the window before any
    # commits is guaranteed by a barrier in `/redeem`, not hoped for from a
    # sleep. That each recorded window is wide enough for two of them to be
    # shown overlapping is guaranteed by the endpoint's own delay, which the
    # barrier release does not shorten - the first attempt removed that
    # delay, proved the race, and destroyed the `elapsed_ms` the overlap is
    # reconstructed from.
    #
    # The decisive evidence is in the Windows run that failed. Its first
    # assertion PASSED: six requests returned 200 against one coupon. Six
    # successes means all six were inside the window, so the burst does
    # achieve concurrency on Windows - only its MEASURABILITY ever failed
    # there, and measurability is the half that is now server-side.
    #
    # Measured before re-adding: 8/8 proven locally, six successes each,
    # narrowest recorded window 157-173ms against a 150ms server delay. If
    # this does start failing, the honest read is that a runner cannot get
    # two requests in flight at once - delete this entry, put `race` back in
    # NOT_DRIVEN, and say so. Do not add a conditional skip; that is how the
    # case came to be testing the scheduler the first time.
    # REVERTED, fourth round. Re-added on local evidence (8/8 proven,
    # windows 157-173ms) and on a reading of the Windows run that failed:
    # its first assertion passed, six requests returned 200 against one
    # coupon, so the burst does achieve concurrency there. That much was
    # right - `test_the_race_window_can_be_made_deterministic` passed on
    # the very Windows jobs that failed THIS case.
    #
    # But concurrency was never the whole requirement. On Windows 3.10,
    # 3.11 and 3.12 the grade came back `unproven` with
    # `missing: ['no evidence']` - which is `_best_grade`'s starting value,
    # so no quote from any recorded exchange graded above unproven at all.
    # Windows 3.13, 3.14 and every ubuntu job passed. Something about what
    # the burst RECORDS on those runners does not satisfy `verify_race`,
    # and I do not yet know what. The entry's own instruction said to delete
    # it and say so rather than add a conditional skip, so that is what this
    # is.
    #
    # What stays: the barrier and the window in `/redeem` are independently
    # green and independently tested in `tests/test_lab.py`, and the
    # unconditional both-direction assertions remain synthetic in
    # `tests/test_proof.py`. What is missing is a diagnosis, not a
    # mechanism. Do not re-add this on local measurement alone - that is
    # twice now.
]

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
    # The clean side of the nine classes added to the proving table. Each
    # endpoint was MEASURED clean, not assumed: this module has twice
    # asserted a lab endpoint was clean and been wrong, so the rule is to
    # drive it first and keep only what grades below its ceiling.
    # `/internal/status` serves a fixed JSON body and reflects nothing
    ("probe_reflection", "xss",
     lambda c, b: probes.probe_reflection(c, b + "/internal/status?x=y",
                                          "x")),
    # `/search` echoes its term and makes no server-side fetch
    ("probe_ssrf", "ssrf",
     lambda c, b: probes.probe_ssrf(c, b + "/search?q=x", "q")),
    # ...and parses no XML
    ("probe_xxe", "xxe", lambda c, b: probes.probe_xxe(c, b + "/search")),
    # `/api/order` echoes order/owner/total and drops every other field -
    # a whitelist, and the direction that caught the massassign verifier
    # accepting that endpoint's own ordinary answer as the proof
    ("probe_massassign", "massassign",
     lambda c, b: probes.probe_massassign(c, b + "/api/order",
                                          '{"order":1}')),
    # `/login2` answers every attempt with the same text; the only channel
    # is timing, which is a lead and must not grade
    ("probe_enum", "enum",
     lambda c, b: probes.probe_enum(c, b + "/login2",
                                    "username=x&password=x")),
    # `/api/order` merges nothing into shared state
    ("probe_ppoll", "ppoll",
     lambda c, b: probes.probe_ppoll(c, b + "/api/order", b + "/api/order")),
    # `/search` is not cached, so no canary can persist into a clean read
    ("probe_cache", "cache",
     lambda c, b: probes.probe_cache(c, b + "/search?q=x")),
    # a write that changes nothing the read returns is not a csrf finding,
    # however unprotected the form is
    ("probe_csrf", "csrf",
     lambda c, b: probes.probe_csrf(c, b + "/search", method="POST",
                                    data="q=x",
                                    read_url=b + "/internal/status")),
    # introspection disabled: the refusal is the defence working
    ("graphql_introspect", "graphql",
     lambda c, b: web.graphql_introspect(c, b + "/graphql-strict")),
    # the server's OWN token accepted and a bad one refused is an auth
    # system working - without the mint it must not grade, which is the
    # distinction `verify_token_forgery` exists to make
    ("jwt_forge", "jwt", lambda c, b: _drive_jwt(c, b, forge=False)),
    # `/search` parses nothing, so a gadget gets no parser error and no
    # execution - the distinction `deserialize` rests on
    ("probe_deserialize", "deserialize",
     lambda c, b: probes.probe_deserialize(c, b + "/search?q=x", "q")),
]
# `method` and `xfh` have no clean case either, for the same reason as `cors`
# below: the lab answers TRACE on every path and honours X-Original-URL
# before it routes, so both are properties of the server rather than of an
# endpoint. Their refusal cases are synthetic in `tests/test_proof.py`.
# `cors` has no clean case here: the lab reflects any `Origin` with
# credentials from the shared response helper, so every endpoint is
# vulnerable - including `/hello`, which this module was asserting as clean
# until it failed. `/safedirect` is not clean either; it is the deliberate
# "filter that allows //host" bypass. Both were my guesses and both were
# wrong, which is the layer working on its author. The synthetic refusal
# cases for those classes live in `tests/test_proof.py`.

# The coverage these tables claim, asserted below against the tables
# themselves and against every document that states it. The first version of
# that sentence said 23 and the tables held 24, which is the kind of number
# this repository's doc gate exists to refuse - it just did not reach here.
#
# The denominator is the MATRIX, not the set of classes that happen to have a
# `probe_*` tool. Counting against the tooling is how `graphql` and `jwt` sat
# outside this module without anyone noticing: neither is driven by a probe,
# so neither appeared in a coverage figure derived from the probe table.
PROVING_COVERAGE = 27
MATRIX_CLASSES = 29
# Each with a reason stated in the module docstring above.
NOT_DRIVEN = {"dos", "race"}

_ORDER = {"proven": 3, "candidate": 2, "unproven": 1, "refused": 0}

# A single distinctive value, which is what a tester quotes when the proof is
# "this marker crossed from there to here".
_TOKEN_RE = re.compile(r"[A-Za-z0-9_.@-]{8,200}")


def _exchanges(session) -> list[dict]:
    return [e for e in session._transcript.values()
            if isinstance(e.get("response"), dict)]


def _entries(session) -> list[dict]:
    """Everything recorded, events included.

    `_exchanges` drops the non-HTTP events, which is right for choosing a
    quote and wrong for grading: `jwt`'s first requirement - "this system
    minted the credential" - is made of the `jwt_forge` event and nothing
    else. Grading with exchanges alone put that class permanently out of
    this module's reach, which is the likeliest reason nobody added it.
    Measured: the same evidence grades `unproven` on exchanges and `proven`
    on the full set.
    """
    return [e for e in session._transcript.values() if isinstance(e, dict)]


def _best_grade(klass: str, entries: list[dict],
                graded: list[dict] | None = None) -> tuple[str, list[str]]:
    """The best grade any honest quote from this evidence can reach.

    A probe does not choose the excerpt - the agent does - so the question is
    whether *some* quote a tester would take satisfies the requirement. Lines
    are what a tester takes, which is also why a whole body is not offered:
    handing the matrix an entire response defeats its own echo veto.

    A tester also quotes ONE distinctive value, and for the classes whose
    proof is a marker crossing from one request to another response that is
    the only quote that works: `ppoll` and `cache` both reach `proven` on
    `<marker>` and `unproven` on the line containing it, because the
    verifier asks that the excerpt appear verbatim in the poisoning
    *request* - where the surrounding markup is not. Offering only lines
    read both classes as probe failures when the probe and the matrix
    actually agreed.
    """
    best, missing = "unproven", ["no evidence"]
    for entry in entries:
        body = proof.resp_body(entry)
        quotes = [ln.strip() for ln in body.splitlines()
                  if 8 <= len(ln.strip()) <= 400]
        whole = body.strip()
        if whole and len(whole) <= 400:
            quotes.append(whole)
        quotes += [t for t in dict.fromkeys(_TOKEN_RE.findall(body))
                   if t not in quotes]
        for quote in quotes[:60]:
            verdict = proof.grade(klass, quote, graded or entries)
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
    before_all = len(_entries(ctx.session))
    call(ctx, lab_url)
    entries = _exchanges(ctx.session)[before:]
    assert entries, f"{name} recorded no exchange at all"

    grade, missing = _best_grade(klass, entries,
                                 _entries(ctx.session)[before_all:])
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
        # A class whose proof needs a chain cannot be in PROBE_CLASS: those
        # steps send nothing, so mapping them as evidence would mark the
        # class tried on an offline call. `CLASS_TOOL_CHAIN` names them
        # instead, and a row may be driven by any step of its own chain.
        chain = CLASS_TOOL_CHAIN.get(klass, ())
        assert PROBE_CLASS.get(name) == klass or name in chain, (
            f"{name} is driven as {klass!r} but decide.PROBE_CLASS says "
            f"{PROBE_CLASS.get(name)!r} and the class's tool chain is "
            f"{list(chain)}")


def test_both_directions_are_exercised_for_the_classes_that_have_both():
    """A one-directional case proves little. Name the overlap explicitly so
    removing one half is visible."""
    vulnerable = {k for _, k, _ in VULNERABLE}
    clean = {k for _, k, _ in CLEAN}
    both = vulnerable & clean
    assert {"sqli", "rce", "ssti", "lfi", "crlf", "redirect",
            "websocket", "smuggle", "nosqli", "lockout"} <= both, (
        f"classes exercised in both directions: {sorted(both)}")


def test_the_stated_coverage_matches_the_tables_and_the_docs():
    """The coverage sentence is a count, so something has to count it.

    `docs/VERIFICATION.md`, `CHANGELOG.md`, `AGENTS.md` and this module's own
    docstring all state "N of the M probed classes". The first draft said 23
    while the table held 24. A number in prose that nothing checks is exactly
    what this repository's documentation gate exists to refuse; that gate
    counts tools, classes, flags and test totals, and does not reach a count
    stated about a test module, so this does.
    """
    import re
    from pathlib import Path

    driven = {k for _, k, _ in VULNERABLE}
    matrix = {spec.vuln_class for spec in proof.MATRIX.values()}
    assert len(driven) == PROVING_COVERAGE, sorted(driven)
    assert len(matrix) == MATRIX_CLASSES, sorted(matrix)
    # the ones left out are named with a reason in the docstring above
    assert matrix - driven == NOT_DRIVEN, matrix - driven
    for name in driven:
        assert proof.spec_for(name) is not None, name
    # and every class a probe tool claims to test is driven, or excluded
    assert set(PROBE_CLASS.values()) - driven <= NOT_DRIVEN, \
        set(PROBE_CLASS.values()) - driven

    root = Path(__file__).resolve().parent.parent
    pattern = re.compile(r"(\d+) of the (\d+) proof classes")

    # CHANGELOG.md is deliberately NOT in this list, and that is a
    # correction. It used to be, and it carries two entries stating the
    # figure that was current when they were written - so the assertion
    # "every stated figure equals the CURRENT coverage" made the number
    # unchangeable: raising it meant editing two historical entries into
    # saying something they did not say at the time. A check that can only
    # be satisfied by falsifying the record has frozen the measurement
    # instead of verifying it.
    #
    # Worse, the anti-rot guard below was load-bearing on exactly those two
    # frozen lines. `AGENTS.md` and this module stated the figure nowhere -
    # measured: zero matches in each, while this docstring CLAIMED to state
    # it - so `seen` reached its floor on the changelog alone. The living
    # documentation could have dropped the claim entirely and the guard
    # would not have noticed. It is now stated in both living sources, and
    # the floor is what proves they are both still saying it.
    current = ("docs/VERIFICATION.md", "AGENTS.md",
               "tests/test_probe_matrix_agreement.py")
    seen, by_file = 0, {}
    for rel in current:
        path = root / rel
        if not path.is_file():
            continue
        for stated, total in pattern.findall(
                path.read_text(encoding="utf-8")):
            seen += 1
            by_file[rel] = by_file.get(rel, 0) + 1
            assert int(stated) == PROVING_COVERAGE, f"{rel} says {stated}"
            assert int(total) == MATRIX_CLASSES, f"{rel} says of {total}"
    # a regex that stops matching would make this pass forever on nothing,
    # and naming the files is what keeps the floor honest: two sources that
    # both still say it, not one source saying it twice
    assert len(by_file) >= 2, (
        f"only {sorted(by_file) or 'nothing'} states the coverage - the "
        "living documents are where this claim has to survive")
    assert seen >= 2, "no document states the coverage any more"
