"""web — the classes a single request cannot settle.

Nine classes in the proof matrix had a requirement and no probe ladder, because
no tool produced the evidence shape their verifier reads. This server builds the
ones that can be built honestly with the standard library, and each tool here is
shaped by the control its class needs rather than by the payload it sends:

* a **race** is two orderings of the same N requests. The parallel burst alone is
  a story about a flaky endpoint, so `web.race_probe` runs the serial control
  itself and reports both outcome distributions. One call, two orderings, or the
  differential verifier sees nothing to compare — and a state-changing burst must
  bring a `reset_url`, because a resource consumed by the first ordering is not
  there for the second and the difference would be the order, not the window.
* a **poisoned cache** is proven by the *second* request, not the first.
  `web.cache_probe` sends the unkeyed header and then fetches the URL clean; the
  clean response is the evidence and the poisoning request is the context.
* an **open redirect** is measured in the `Location` header. Nothing here follows
  a redirect: following one is a request to a host the scope gate never checked.
* **CORS** is a matrix of (origin sent -> origin returned, credentials), most of
  whose rows are noise. `web.cors_probe` says which row is exploitable and why
  the others are not.
* a **GraphQL** schema dump is an inventory, not a finding. `web.graphql_probe`
  produces the inventory and names the queries worth trying; only its bounded
  `query` mode can satisfy the class requirement.
* an **upload** is proven by execution, and this system proves execution with
  `id; echo <nonce>` and nothing else. `web.upload_probe` therefore uploads one
  inert marker file, reports whether and where it is served back, and stops.
  There is no argument for the file's content, and no argument that can be made
  into one: every caller value that reaches a MIME header line — the filename,
  the field name, the declared type, each extra form field — is refused if it
  carries a quote or a line break, because a filename that closes its own quoted
  string writes the part's body, and that is a shell uploaded through the one
  tool here that says it cannot upload one.

What this server refuses:

* **No destructive demonstration.** The race probe caps N at 40 because the
  measurement is a window, not load; the upload probe writes exactly one file and
  records what cleanup needs; nothing here retries to exhaust anything.
* **No guessing about state.** `web.race_probe` will not infer from the HTTP
  method whether a request changes state. The caller declares it, and a declared
  state change needs the intrusive tier enabled on the engagement — as does a
  `reset_url`, which puts state back and therefore changes it, and a GraphQL
  document declaring a mutation, which `web.graphql_probe` reads out of the
  document rather than trusting its own `active` tier.
* **No redirect following, no off-origin fetch, and no second URL the gate did
  not see.** Every request a tool here makes is to the origin the gate checked,
  and every URL a tool derives — a reset endpoint, a cleanup endpoint, a path
  read out of the target's own response — is checked against the engagement's
  scope again. An in-scope rule may be a URL prefix, so sharing an origin is not
  authorisation: `http://host/app/` does not cover `http://host/admin/`.
* **No outcome that is not an outcome.** A request that never completed is
  excluded from the race comparison, and only the nonce reaching a clean
  requester is called a poisoned cache. A dropped connection and a fresh CSRF
  token are the two cheapest ways to invent a finding here.
"""
from __future__ import annotations

import json
import re
import secrets
import threading
import time
import urllib.parse

from ... import config
from ...ledger import proof as matrix
from ...ledger.scope import origin_of
from ...util import append_jsonl, bound, now_iso, read_jsonl
from .. import httpkit
from ..mcp import Server, ToolContext, ToolError

SERVER = Server("web", "race, cache, redirect, CORS, GraphQL and upload probes")

RACE_CAP = 40
BODY_KEEP = 4000

_COMMON = {
    "url": {"type": "string", "description": "absolute URL; must be in scope"},
    "method": {"type": "string", "enum": ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD"]},
    "headers": {"type": "object", "description": "extra request headers"},
    "body": {"type": "string", "description": "raw request body"},
    "json_body": {"type": "object", "description": "body sent as application/json"},
    "cookies": {"type": "string", "description": "Cookie header value"},
    "timeout": {"type": "integer", "description": "seconds, default 15"},
    "note": {"type": "string", "description": "why this probe was issued"},
}


def _send(url: str, method: str = "GET", headers: dict | None = None, body=None,
          json_body: dict | None = None, cookies: str = "", timeout: int = 15):
    return httpkit.request(method or "GET", url, headers=headers or None, data=body,
                           json_body=json_body, cookies=cookies or None, timeout=timeout or 15)


def _require_intrusive(context: ToolContext, why: str) -> dict | None:
    """The in-tool half of the tier gate, for tools whose risk depends on an
    argument rather than on which tool was called.

    The framework checks `spec.tier` before the handler runs, which is the right
    place for a tool that is always intrusive. A race probe is not: the same code
    is read-only against a search endpoint and state-changing against a checkout
    endpoint. So the caller declares which, and the declaration is checked here
    against the tiers the engagement actually enabled — before any request is
    sent, and never inferred from the HTTP method, because a caller's guess about
    its own request is not a measurement.
    """
    if config.TIER_INTRUSIVE in context.state.tiers:
        return None
    return {"ok": False, "error": "tier-not-enabled", "result": "refused", "evidence": None,
            "summary": f"refused: {why}",
            "message": (f"{why} needs the intrusive tier; this engagement enables "
                        f"{context.state.tiers}. Open the engagement with --tier intrusive and an "
                        f"authorisation note, or point this probe at a request that changes "
                        f"nothing and say so with changes_state=false."),
            "next": "either enable the tier with authorisation, or pick a read-only request"}


def _bounded(value, limit: int = 20) -> list:
    return list(value)[:limit]


def _scope_verdict(context: ToolContext, url: str):
    return context.state.scope.check(url)


def _require_in_scope(context: ToolContext, url: str, what: str) -> None:
    """Check a URL this tool derived, rather than inheriting the gate's verdict.

    The framework scope-checks the `url` argument before the handler runs. Any
    second URL — a reset endpoint, a cleanup endpoint, a path read out of the
    target's own response — is a new target and is checked again, because an
    in-scope rule may be a URL prefix (`http://host/app/`) and not a whole host.
    Comparing origins alone passed every path on the origin, so a `reset_url` of
    `/admin/reset` under a scope of `http://host/app/` was a request nothing
    authorised: same origin, different path, and the gate never saw it. That is
    exactly the silent widening `argus/ledger/scope.py` is built to prevent.
    """
    verdict = _scope_verdict(context, url)
    if not verdict:
        raise ToolError(
            f"{what} {url!r} is not in this engagement's scope: {verdict.reason}. The broker "
            f"scope-checked the `url` argument, not this one, and an in-scope rule can be a URL "
            f"prefix rather than a whole host — so a second URL on the same origin is still a "
            f"target nothing authorised. Widen the scope deliberately, or point this at a URL the "
            f"engagement covers.")


# --- race condition ----------------------------------------------------------

def _distribution(responses: list) -> dict:
    counts: dict[str, int] = {}
    for response in responses:
        if response is None:
            key = "no-response"
        elif response.status is None:
            key = f"transport-error:{(response.error or 'unknown')[:48]}"
        else:
            key = str(response.status)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _marker_hits(responses: list, marker: str) -> int:
    if not marker:
        return 0
    return sum(1 for r in responses if r is not None and marker in (r.body or ""))


def _completed(responses: list) -> list:
    """The requests that came back with an HTTP status, and only those.

    A dropped connection is not an outcome. `urllib` reports one as a transport
    error with `status=None`, and ranking it as the least permissive outcome
    handed it to the differential verifier as the thing serial execution did not
    produce: against an endpoint with no state at all, one connection dropped by
    a small server under the burst graded `proven`. That is the flaky endpoint
    this class exists to refuse. Incompletes stay visible — they are keyed in the
    distribution and counted in `extracted.incomplete` — but they never become a
    record's response and never make an outcome differ.
    """
    return [r for r in responses if r is not None and r.status is not None]


def _ranked(responses: list) -> list:
    return sorted(_completed(responses), key=lambda r: r.status)


def _statuses_only(distribution: dict) -> dict:
    """The distribution with the transport-error keys dropped, which is what the
    two orderings may honestly be compared on."""
    return {key: value for key, value in distribution.items() if key.isdigit()}


def _first_divergence(parallel: list, serial: list) -> tuple:
    """The outcome serial execution did not produce, and what it produced instead.

    Both orderings' outcomes are ranked most-permissive first and compared
    position by position. The first position where they disagree is the pair the
    records carry: the parallel response there is an outcome that N requests
    could not reach when they could not overlap, and the serial response at the
    same rank is what should have happened. When the ranked lists agree all the
    way down there was no window, and both records carry the first outcome, which
    makes the two statuses identical and the differential verifier say so.

    Only completed requests are ranked. A transport error has no status, and
    offering one as the outcome serial execution did not produce turns a dropped
    connection into a proven race — see `_completed`.

    The first draft of this took "the request that finished last" from each side.
    Against a stock-of-one endpoint that is a 409 on both sides — the two
    successes in the parallel burst, which were the entire finding, never reached
    the evidence. Taking the most permissive response from each side instead
    hides the opposite case: one surplus success looks the same as none, because
    both sides' best outcome is a 200. The rank comparison is the only one of the
    three that answers the question the class asks.
    """
    left, right = _ranked(parallel), _ranked(serial)
    for index in range(min(len(left), len(right))):
        if left[index].status != right[index].status:
            return left[index], right[index], index
    return (left[0] if left else None, right[0] if right else None, None)


@SERVER.tool(
    "web.race_probe",
    "Fire N identical requests as close together as possible, then run the serial control: the "
    "same N requests one after another. Reports both outcome distributions, the width of the "
    "parallel window, and the two records the race-condition requirement needs — the parallel "
    "burst and the serial control, tagged ordering=parallel and ordering=serial, which is what "
    "makes the differential verifier see two orderings rather than one noisy endpoint. N is capped "
    "at 40 because the measurement is a timing window, not load: a request count that stresses the "
    "target is a different test with a different name. A request that never completed is excluded "
    "from the comparison and reported as `incomplete`, because a dropped connection is evidence "
    "about the server's accept queue and not about a window. `changes_state` is required and is "
    "never inferred from the method; declaring true needs the intrusive tier AND a `reset_url`, "
    "because "
    "a consumable resource cannot be measured twice — whichever ordering ran second would see what "
    "the first one consumed, and the difference would be an artifact of the order rather than of "
    "concurrency.",
    {"properties": {
        **_COMMON,
        "count": {"type": "integer", "description": f"requests per ordering, 2-{RACE_CAP}, default 10"},
        "changes_state": {"type": "boolean",
                          "description": "true when a single one of these requests changes server "
                                         "state (a purchase, a redeem, a transfer, a password "
                                         "reset). Required, and intrusive when true"},
        "reset_url": {"type": "string",
                      "description": "a request that restores the state the burst consumes, issued "
                                     "before each ordering. Required when changes_state is true. "
                                     "Putting state back is itself a state change, so supplying one "
                                     "needs the intrusive tier, and it must be in the engagement's "
                                     "scope rather than merely on the same origin"},
        "reset_method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE"]},
        "success_marker": {"type": "string",
                           "description": "a string whose presence in a response means the request "
                                          "was accepted; counted per ordering"},
    }, "required": ["url", "changes_state"]},
    tier=config.TIER_ACTIVE, step="parallel-vs-serial", proves="differential",
)
def race_probe(context: ToolContext, url: str, changes_state: bool, method: str = "GET",
               headers: dict | None = None, body: str = "", json_body: dict | None = None,
               cookies: str = "", timeout: int = 15, count: int = 10, reset_url: str = "",
               reset_method: str = "POST", success_marker: str = "", note: str = "") -> dict:
    if changes_state or (method or "GET").upper() not in ("GET", "HEAD") or reset_url:
        refusal = _require_intrusive(
            context, (f"a reset request to {reset_url}, which puts server state back and therefore "
                      f"changes it" if reset_url and not changes_state
                      and (method or "GET").upper() in ("GET", "HEAD") else
                      f"a {(method or 'GET').upper()} burst that the caller declares "
                      f"{'does' if changes_state else 'may'} change state"))
        if refusal:
            return refusal
    if changes_state and not reset_url:
        raise ToolError(
            "a state-changing race needs `reset_url`: a request that puts the resource back "
            "between the two orderings. Without it, whichever ordering runs second starts from "
            "what the first one consumed — a stock of one is gone after the burst, so the serial "
            "control returns nothing but rejections and the tool would report a race it did not "
            "measure. Supply the reset the application already has (a cart clear, a re-add, a test "
            "endpoint), or point the probe at a request that changes nothing and set "
            "changes_state=false.")
    if reset_url:
        if origin_of(reset_url) != origin_of(url):
            raise ToolError(f"reset_url is on {origin_of(reset_url)} and the burst is on "
                            f"{origin_of(url)}. The scope gate checked the burst's origin only, so "
                            f"a reset on another origin is a request nothing authorised.")
        _require_in_scope(context, reset_url, "the reset URL")
    number = max(2, min(int(count or 10), RACE_CAP))
    resets: list[dict] = []

    def once():
        return _send(url, method, headers, body or None, json_body, cookies, timeout)

    def reset(phase: str) -> None:
        if not reset_url:
            return
        response = _send(reset_url, reset_method, headers, None, None, cookies, timeout)
        resets.append({"before": phase, "status": response.status,
                       "ok": response.status is not None and response.status < 400})

    # The serial control runs FIRST, each ordering preceded by the reset, so both
    # start from the same state. Running the burst first and the control second
    # measures the burst's own aftermath.
    reset("serial")
    serial = [once() for _ in range(number)]

    reset("parallel")
    # Threads over separate connections: httpkit sends `Connection: close`, so
    # every call here opens its own socket and no request waits behind another on
    # a shared one. The barrier is what makes it a burst rather than a loop.
    parallel: list = [None] * number
    offsets: list[float] = [0.0] * number
    gate = threading.Barrier(number)
    started = time.monotonic()

    def worker(index: int) -> None:
        try:
            gate.wait(timeout=max(10, timeout))
        except threading.BrokenBarrierError:
            pass
        offsets[index] = (time.monotonic() - started) * 1000
        parallel[index] = once()

    threads = [threading.Thread(target=worker, args=(i,), daemon=True) for i in range(number)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=max(30, timeout * 2))
    window_ms = round(max(offsets) - min(offsets), 2) if number else 0.0

    parallel_dist, serial_dist = _distribution(parallel), _distribution(serial)
    parallel_marker = _marker_hits(parallel, success_marker)
    serial_marker = _marker_hits(serial, success_marker)
    # Compared on HTTP statuses only. A burst that drops a connection and a
    # serial run that does not differ in their distributions, and that
    # difference is about the server's accept queue, not about a window.
    incomplete = {"parallel": number - len(_completed(parallel)),
                  "serial": number - len(_completed(serial))}
    differs = (_statuses_only(parallel_dist) != _statuses_only(serial_dist)) \
        or (parallel_marker != serial_marker)
    surplus = parallel_marker - serial_marker if success_marker else None
    parallel_rep, serial_rep, rank = _first_divergence(parallel, serial)
    resets_ok = all(r["ok"] for r in resets) if resets else None

    shared = {"target": url, "note": note,
              "payload": f"{(method or 'GET').upper()} {url} x{number}"}
    rule = ("the outcomes of both orderings ranked most-permissive first; this record carries the "
            "first rank at which they disagree" if rank is not None else
            "the orderings agree at every rank, so this record carries the best outcome of each")
    parallel_record = {
        "kind": "probe", "ordering": "parallel", **shared,
        "extracted": {"count": number, "distribution": parallel_dist,
                      "success_marker": success_marker or None,
                      "marker_hits": parallel_marker, "surplus_successes": surplus,
                      "window_ms": window_ms,
                      "completed": len(_completed(parallel)),
                      "incomplete": incomplete["parallel"],
                      "divergence_rank": rank, "representative": rule,
                      "state_reset": resets, "state_reset_ok": resets_ok,
                      "changes_state_declared": bool(changes_state)},
        **(parallel_rep.to_evidence(BODY_KEEP) if parallel_rep is not None else {}),
    }
    serial_record = {
        "kind": "control", "is_control": True, "ordering": "serial", **shared,
        "extracted": {"count": number, "distribution": serial_dist,
                      "success_marker": success_marker or None,
                      "marker_hits": serial_marker,
                      "completed": len(_completed(serial)),
                      "incomplete": incomplete["serial"],
                      "divergence_rank": rank, "representative": rule,
                      "state_reset": resets, "state_reset_ok": resets_ok,
                      "purpose": "what the same N requests do when they cannot overlap"},
        **(serial_rep.to_evidence(BODY_KEEP) if serial_rep is not None else {}),
    }
    verdict = matrix.verify("race-condition", [parallel_record, serial_record])
    warning = ("" if resets_ok is not False else
               " | WARNING: a reset request failed, so the two orderings may not have started from "
               "the same state and this differential proves nothing")
    if incomplete["parallel"] or incomplete["serial"]:
        warning += (f" | {incomplete['parallel']} parallel and {incomplete['serial']} serial "
                    f"request(s) never completed; a dropped connection is evidence about the "
                    f"server's accept queue and nothing else, so it is excluded from the "
                    f"comparison. If the burst cannot complete, lower `count` before reading "
                    f"anything into the difference")
    return {
        "summary": (f"parallel {parallel_dist} vs serial {serial_dist}"
                    + (f" | marker {success_marker!r} {parallel_marker}x parallel, "
                       f"{serial_marker}x serial"
                       + (f" ({surplus:+d} surplus)" if surplus else "") if success_marker else "")
                    + f" | {number} requests each, window {window_ms}ms"
                    + f" | race-condition: {verdict.grade}" + warning),
        "result": "signal" if differs else "no-signal",
        "data": {"count": number, "window_ms": window_ms,
                 "parallel": parallel_dist, "serial": serial_dist,
                 "marker_hits": {"parallel": parallel_marker, "serial": serial_marker},
                 "surplus_successes": surplus, "divergence_rank": rank,
                 "incomplete": incomplete,
                 "state_resets": resets, "distributions_differ": differs,
                 "proof_grade": verdict.grade, "missing": verdict.missing},
        "output": ("ordering   outcomes\n"
                   f"serial     {json.dumps(serial_dist)}   (control, ran first)\n"
                   f"parallel   {json.dumps(parallel_dist)}\n"
                   f"\nwindow: all {number} parallel requests released within {window_ms}ms of "
                   f"each other\n"
                   + (f"divergence: the orderings first disagree at rank {rank} — parallel "
                      f"{parallel_rep.status if parallel_rep else '-'} where serial gave "
                      f"{serial_rep.status if serial_rep else '-'}\n" if rank is not None else
                      "divergence: none; the two orderings agree at every rank\n")
                   + (f"resets: {json.dumps(resets)}\n" if resets else
                      "resets: none (read-only burst)\n")),
        "evidence": parallel_record,
        "extra_evidence": [serial_record],
        "next": ("the race-condition requirement is met — two orderings, the serial control, and "
                 "outcomes that differ. Record the finding with both evidence ids, and put the two "
                 "distributions in it: they are what makes it readable"
                 if verdict.proven else
                 "the two orderings produced the same outcomes, so there is no window here: this "
                 "is what a correctly-locked endpoint looks like. A wider window will not appear "
                 "from more requests — either the state change is guarded, or the request you are "
                 "repeating is not the one that mutates. Do not re-run with a larger count"
                 if not differs else
                 f"the distributions differ but the requirement is not met: "
                 f"{', '.join(verdict.missing)}. When the two orderings reach the same set of "
                 f"HTTP statuses and differ only in HOW MANY requests succeeded — "
                 f"{parallel_marker} parallel against {serial_marker} serial — the status "
                 f"comparison in the differential verifier cannot see it. Record both records "
                 f"anyway: the distributions and surplus_successes are in the evidence, and the "
                 f"candidate names exactly what a count-based check would settle"),
    }


# --- CORS --------------------------------------------------------------------

def _host_only(url: str) -> str:
    return (urllib.parse.urlsplit(url).hostname or "").lower()


def _cors_origins(url: str, token: str) -> list[tuple[str, str, str]]:
    """(label, Origin to send, which naive check the shape defeats)."""
    split = urllib.parse.urlsplit(url)
    host = _host_only(url)
    own = f"{split.scheme or 'http'}://{split.netloc}"
    return [
        ("own-origin", own,
         "control: whether this endpoint answers with CORS headers at all"),
        ("untrusted", f"https://argus-{token}.test",
         "an origin with no relationship to the target; reflection here is an allow-any policy"),
        ("null", "null",
         "a sandboxed iframe, a data: document and a cross-site redirect all send Origin: null, "
         "so `null` in the allowlist is reachable from any page on the internet"),
        ("subdomain", f"https://argus-{token}.{host}",
         "a subdomain of the target; exploitable when any subdomain can be taken over or has XSS"),
        ("suffix-match", f"https://{host}.argus-{token}.test",
         "defeats a check written as origin.startswith(host) or `host in origin`"),
        ("prefix-match", f"https://argus-{token}-{host}",
         "defeats a check written as origin.endswith(host)"),
    ]


def _cors_row(label: str, origin: str, defeats: str, response, host: str) -> dict:
    acao = response.header("access-control-allow-origin")
    acac = response.header("access-control-allow-credentials").strip().lower() == "true"
    reflected = bool(acao) and acao.strip() == origin
    wildcard = acao.strip() == "*"
    if label == "own-origin":
        verdict, why = "baseline", ("establishes whether the endpoint does CORS at all; its own "
                                    "origin being allowed is correct behaviour")
    elif reflected and acac:
        verdict, why = "exploitable", ("the untrusted origin is reflected AND credentials are "
                                       "allowed: any page can read this response as the victim")
    elif wildcard and acac:
        verdict, why = "noise", ("`*` with credentials is rejected by every browser, so this "
                                 "combination is a server bug with no client-side exploit")
    elif reflected:
        verdict, why = "reflected-without-credentials", ("readable cross-origin, but only the "
                                                         "unauthenticated response; worth a look "
                                                         "only if this endpoint leaks without a "
                                                         "session")
    elif wildcard:
        verdict, why = "noise", "`*` without credentials is a public endpoint, which is not a finding"
    else:
        verdict, why = "noise", "the origin was not reflected and no wildcard was returned"
    return {"label": label, "origin_sent": origin, "acao": acao or None, "acac": acac,
            "reflected": reflected, "wildcard": wildcard, "status": response.status,
            "allow_credentials_header": response.header("access-control-allow-credentials") or None,
            "vary": response.header("vary") or None,
            "allow_methods": response.header("access-control-allow-methods") or None,
            "allow_headers": response.header("access-control-allow-headers") or None,
            "verdict": verdict, "why": why, "defeats": defeats, "host": host}


@SERVER.tool(
    "web.cors_probe",
    "Send a set of Origin headers the application cannot legitimately trust and read back "
    "Access-Control-Allow-Origin and -Credentials for each: the target's own origin as the "
    "baseline, a wholly untrusted origin, `null`, a subdomain, a suffix match "
    "(victim.com.attacker.test) and a prefix match. Returns the full matrix with a verdict per "
    "row, because most rows are noise: a reflected origin WITHOUT credentials exposes only the "
    "unauthenticated response, and `*` with credentials is rejected by every browser. The only "
    "exploitable row is a reflected or null origin with credentials allowed. This measures a "
    "policy; it does not prove a class on its own, and the result says what would.",
    {"properties": {
        "url": _COMMON["url"],
        "method": {"type": "string", "enum": ["GET", "OPTIONS", "POST"]},
        "headers": _COMMON["headers"], "cookies": _COMMON["cookies"],
        "timeout": _COMMON["timeout"], "note": _COMMON["note"],
        "extra_origins": {"type": "array",
                          "description": "additional Origin values to include in the matrix"},
        "preflight": {"type": "boolean",
                      "description": "also send an OPTIONS preflight per origin (default false)"},
    }, "required": ["url"]},
    tier=config.TIER_ACTIVE, step="cors-origin-matrix", proves=None,
)
def cors_probe(context: ToolContext, url: str, method: str = "GET", headers: dict | None = None,
               cookies: str = "", timeout: int = 15, extra_origins: list | None = None,
               preflight: bool = False, note: str = "") -> dict:
    token = context.nonce()
    host = _host_only(url)
    shapes = _cors_origins(url, token)
    shapes += [(f"operator-{index}", str(value), "supplied by the caller")
               for index, value in enumerate(_bounded(extra_origins or [], 6))]

    rows, responses = [], {}
    for label, sent_origin, defeats in shapes:
        sent = {**(headers or {}), "Origin": sent_origin}
        response = _send(url, method, sent, None, None, cookies, timeout)
        row = _cors_row(label, sent_origin, defeats, response, host)
        if preflight:
            pre = _send(url, "OPTIONS", {**sent,
                                         "Access-Control-Request-Method": "GET",
                                         "Access-Control-Request-Headers": "authorization"},
                        None, None, cookies, timeout)
            row["preflight"] = {"status": pre.status,
                                "acao": pre.header("access-control-allow-origin") or None,
                                "acac": pre.header("access-control-allow-credentials") or None,
                                "allow_methods": pre.header("access-control-allow-methods") or None}
        rows.append(row)
        responses[label] = response

    exploitable = [r for r in rows if r["verdict"] == "exploitable"]
    partial = [r for r in rows if r["verdict"] == "reflected-without-credentials"]
    baseline = next((r for r in rows if r["label"] == "own-origin"), None)
    # Two records, not one per origin. Six near-identical responses in the
    # evidence index make the index unreadable and prove nothing the matrix does
    # not already hold: the whole matrix is in `extracted.matrix` on both, and
    # what the records carry separately is the one row that matters and the
    # baseline it has to be read against.
    lead = (exploitable or partial or [r for r in rows if r["label"] == "untrusted"] or rows)[0]
    records = [
        {"kind": "probe", "target": url, "payload": f"Origin: {lead['origin_sent']}", "note": note,
         "extracted": {"cors_row": lead, "matrix": rows, "probe_nonce": token},
         **responses[lead["label"]].to_evidence(1500)},
    ]
    if baseline is not None and baseline is not lead:
        records.append(
            {"kind": "control", "is_control": True, "target": url,
             "payload": f"Origin: {baseline['origin_sent']}", "note": note,
             "extracted": {"purpose": "the application's own origin: what an allowed origin looks "
                                      "like here, and whether this endpoint does CORS at all",
                           "cors_row": baseline, "matrix": rows},
             **responses[baseline["label"]].to_evidence(1500)})
    primary = records[0]
    table = "\n".join(
        f"{r['label']:<14} {str(r['origin_sent'])[:46]:<46} -> acao={str(r['acao'])[:40]:<40} "
        f"acac={str(r['acac']):<5} {r['verdict']}" for r in rows)
    return {
        "summary": (f"{len(exploitable)} exploitable row(s), {len(partial)} reflected without "
                    f"credentials, {len(rows) - len(exploitable) - len(partial)} noise"
                    + (f" | exploitable: {[r['label'] for r in exploitable]}" if exploitable else "")
                    + (f" | baseline own-origin acao={baseline['acao']!r} "
                       f"acac={baseline['acac']}" if baseline else "")),
        "result": "signal" if exploitable else "no-signal",
        "data": {"rows": rows, "exploitable": [r["label"] for r in exploitable],
                 "reflected_without_credentials": [r["label"] for r in partial],
                 "origin": origin_of(url)},
        "output": table,
        "evidence": primary,
        "extra_evidence": [rec for rec in records if rec is not primary],
        "next": ("there is no `cors` class in the proof matrix, and that is deliberate: a policy is "
                 "not an impact. What this row establishes is the precondition. To make it a "
                 "finding, demonstrate the cross-origin read in a real browser with the victim's "
                 "session and record it with ledger.add_evidence under the class of the data you "
                 "obtained — or, for a cross-origin write, under csrf with the before/action/after "
                 "phases. Reporting the header alone is reporting a configuration, which belongs in "
                 "the candidate section"
                 if exploitable else
                 "no origin we cannot be trusted with was reflected with credentials, so there is "
                 "no cross-origin read here. The remaining rows are noise by construction — do not "
                 "re-send them with more origin shapes unless you have read the allowlist code")
    }


# --- cache poisoning ---------------------------------------------------------

CACHE_HEADERS = ("age", "x-cache", "x-cache-hits", "cf-cache-status", "vary",
                 "cache-control", "x-varnish", "x-served-by", "akamai-cache-status")

UNKEYED_CANDIDATES = ("X-Forwarded-Host", "X-Forwarded-Scheme", "X-Original-URL", "X-Rewrite-URL",
                      "X-Forwarded-Proto", "X-Host", "X-Forwarded-Server")


def _cache_view(response) -> dict:
    return {name: response.header(name) for name in CACHE_HEADERS if response.header(name)}


def _unkeyed_value(header: str, token: str) -> tuple[str, bool]:
    """The value to put in a candidate unkeyed header, and whether it carries the
    nonce. A scheme header cannot carry one: its only legal values are `http` and
    `https`, so for those the observation is the clean response changing shape,
    not the nonce coming back."""
    lower = header.lower()
    if lower in ("x-forwarded-host", "x-host", "x-forwarded-server"):
        return f"argus-{token}.test", True
    if lower in ("x-original-url", "x-rewrite-url"):
        return f"/argus-{token}-no-such-path", True
    if lower in ("x-forwarded-scheme", "x-forwarded-proto"):
        return "http", False
    return f"argus-{token}", True


@SERVER.tool(
    "web.cache_probe",
    "Unkeyed-input detection, proven by the second request. Sends one request carrying a candidate "
    "unkeyed header (X-Forwarded-Host, X-Forwarded-Scheme, X-Original-URL, X-Rewrite-URL and "
    "friends) with a nonce in it, then fetches the SAME URL clean — no header at all — and looks "
    "for the nonce, or for the clean response having moved materially (status, or body past "
    "httpkit's similarity floor; a fresh CSRF token or a timestamp is not a change). Only the "
    "nonce in a clean requester's response is called POISONED. That second fetch is the whole "
    "proof: a poisoned response reaching a requester who did not send the header. Reports `age`, "
    "`x-cache`, `cf-cache-status` and `vary` from every fetch so the reader can see whether there "
    "is a cache in front of this at all. INTRUSIVE: a poisoned cache entry is served to other "
    "users, not to you. By default the probe appends its own cache buster so the entry it poisons "
    "is one only this probe requests; cache_buster=false poisons the entry real users share, and "
    "needs a reason recorded in `note`.",
    {"properties": {
        "url": _COMMON["url"], "headers": _COMMON["headers"], "cookies": _COMMON["cookies"],
        "timeout": _COMMON["timeout"], "note": _COMMON["note"],
        "candidates": {"type": "array",
                       "description": f"headers to try, in order; default {list(UNKEYED_CANDIDATES[:4])}"},
        "cache_buster": {"type": "boolean",
                         "description": "append argus-cb=<nonce> to the query so only this probe "
                                        "requests the poisoned entry (default true)"},
        "settle_seconds": {"type": "integer",
                           "description": "wait between the poisoning request and the clean fetch, "
                                          "0-5, default 1"},
    }, "required": ["url"]},
    tier=config.TIER_INTRUSIVE, step="unkeyed-input", proves="differential",
)
def cache_probe(context: ToolContext, url: str, headers: dict | None = None, cookies: str = "",
                timeout: int = 15, candidates: list | None = None, cache_buster: bool = True,
                settle_seconds: int = 1, note: str = "") -> dict:
    token = context.nonce()
    wanted = [str(h) for h in _bounded(candidates or UNKEYED_CANDIDATES[:4], 8)]
    settle = max(0, min(int(settle_seconds), 5))
    if not cache_buster and not note:
        raise ToolError(
            "cache_buster=false poisons the cache entry that real users of this URL share. "
            "Say why in `note` — which authorisation covers it and how the entry will be "
            "evicted — or leave the buster on and prove the unkeyed input on an entry only this "
            "probe requests.")

    def bust(suffix: str) -> str:
        if not cache_buster:
            return url
        split = urllib.parse.urlsplit(url)
        query = urllib.parse.parse_qsl(split.query, keep_blank_values=True)
        query.append(("argus-cb", f"{token}-{suffix}"))
        return urllib.parse.urlunsplit(split._replace(query=urllib.parse.urlencode(query)))

    # Each attempt gets its OWN cache entry, and the control gets another.
    # Sharing one entry between the control and the poisoning attempt is the
    # mistake that made the first version of this tool report nothing against a
    # cache it had itself warmed: the control fetch populated the entry with the
    # clean response, and every later poisoning request was answered from that
    # entry before it ever reached the application.
    target = bust("control")
    clean_before = _send(target, "GET", headers, None, None, cookies, timeout)
    attempts, hit, last = [], None, None
    for index, header in enumerate(wanted):
        value, carries_nonce = _unkeyed_value(header, token)
        entry = bust(str(index))
        poison = _send(entry, "GET", {**(headers or {}), header: value}, None, None,
                       cookies, timeout)
        if settle:
            time.sleep(settle)
        clean_after = _send(entry, "GET", headers, None, None, cookies, timeout)
        nonce_in_clean = token in (clean_after.body or "")
        nonce_in_poison = token in (poison.body or "")
        # Not byte equality. The control entry and this attempt's entry are two
        # different URLs — they carry different cache-buster values — so any page
        # that echoes its own query string, carries a CSRF token or prints a
        # timestamp differs between them on every request. Comparing the bytes
        # reported POISONED on an uncacheable page whose only difference was a
        # fresh form token, which is the invented finding httpkit.compare's
        # floors exist to refuse. A difference counts when the status moved or
        # the body moved materially; anything smaller is noise and is reported
        # as such. The trade is stated rather than hidden: a real poisoning that
        # moves only a few bytes — a scheme rewritten in a short page, where no
        # nonce can be carried — now reads as "body changed slightly" instead of
        # a hit. Every attempt's `difference` verdict is on record for exactly
        # that case, and it is the right way round: the headers that can carry
        # the nonce are judged on the nonce, not on the diff.
        difference = httpkit.compare(clean_before, clean_after)
        changed = difference.status_changed or difference.verdict == "body changed materially"
        attempt = {"header": header, "value": value, "carries_nonce": carries_nonce,
                   "entry": entry, "control_entry": target,
                   "difference": difference.to_dict(),
                   "poison_status": poison.status, "poison_reflected_nonce": nonce_in_poison,
                   "clean_before": {"status": clean_before.status, "length": clean_before.length,
                                    "cache": _cache_view(clean_before)},
                   "clean_after": {"status": clean_after.status, "length": clean_after.length,
                                   "cache": _cache_view(clean_after)},
                   "nonce_in_clean_response": nonce_in_clean,
                   "clean_response_changed": changed}
        attempts.append(attempt)
        last = (attempt, poison, clean_after)
        if nonce_in_clean or changed:
            hit = last
            break                                 # bounded: the first proof is the proof

    # Without a hit the LAST attempt is still what the records describe: a probe
    # that reports nothing it sent is not a negative result, it is an untestable
    # one, and the next session has to repeat the whole thing to find out which
    # headers were actually tried.
    attempt, poison, clean_after = hit or last or ({}, None, clean_before)
    shared = {"note": note}
    control_record = {
        "kind": "control", "is_control": True, "ordering": "clean-requester-before",
        "target": target, **shared,
        "extracted": {"purpose": "a separate cache entry, fetched clean: what a requester who "
                                 "sends no unkeyed header gets from this URL",
                      "cache_entry": target,
                      "cache_headers": _cache_view(clean_before)},
        **clean_before.to_evidence(BODY_KEEP),
    }
    # The token lives in `extracted.cache_token`, NOT in `nonce`. A record that
    # declares a `nonce` and also mentions it anywhere in `extracted` satisfies
    # every required check of `verify_command_output` — "a benign marker command
    # was declared" and "the nonce was echoed by the target" — because that
    # verifier reads the nonce out of `str(extracted)`. The unkeyed value this
    # probe sends IS the nonce, so these records declaring one let a cache probe
    # be recorded as a CONFIRMED critical rce finding with nothing having
    # executed: open an rce hypothesis, run this tool against it, record the
    # finding. Measured, not theorised. Until that verifier matches the nonce
    # against output only, no record here offers the field.
    clean_record = {
        "kind": "probe", "ordering": "clean-requester-after",
        "target": attempt.get("entry") or target, **shared,
        "extracted": {"cache_token": token,
                      "unkeyed_header": attempt.get("header"),
                      "unkeyed_value": attempt.get("value"),
                      "nonce_in_clean_response": bool(attempt.get("nonce_in_clean_response")),
                      "clean_response_changed": bool(attempt.get("clean_response_changed")),
                      "cache_headers": _cache_view(clean_after),
                      "cache_buster": token if cache_buster else None,
                      "attempts": _bounded(attempts, 8)},
        **clean_after.to_evidence(BODY_KEEP),
    }
    extra = [control_record]
    if poison is not None:
        extra.append({
            "kind": "probe", "ordering": "poisoning-requester",
            "target": attempt.get("entry") or target, **shared,
            "payload": f"{attempt.get('header')}: {attempt.get('value')}",
            "extracted": {"cache_token": token,
                          "purpose": "the request that put the value into the cache entry",
                          "cache_entry": attempt.get("entry"),
                          "cache_headers": _cache_view(poison)},
            **poison.to_evidence(BODY_KEEP),
        })
    verdict = matrix.verify("cache-poisoning", [clean_record, *extra])
    cache_seen = any(a["clean_after"]["cache"] or a["clean_before"]["cache"] for a in attempts)
    poisoned = bool(attempt.get("nonce_in_clean_response"))
    return {
        # Only the nonce in a clean requester's response earns the word POISONED.
        # A material difference between the control entry and the attempt entry
        # is a candidate: two cache entries can also differ because the page
        # does, and the word for that is not "poisoned".
        "summary": (("POISONED: " if poisoned else
                     "MATERIAL CHANGE, no nonce: " if hit else "no unkeyed input found: ")
                    + (f"{attempt.get('header')} -> nonce in the clean response"
                       if poisoned else
                       f"{attempt.get('header')} -> the clean response differs materially "
                       f"({clean_before.status}/{clean_before.length}B -> "
                       f"{clean_after.status}/{clean_after.length}B, "
                       f"{attempt.get('difference', {}).get('verdict')}), which is not yet the "
                       f"nonce reaching a requester who did not send the header" if hit else
                       f"{len(attempts)} header(s) tried, no clean fetch changed materially")
                    + f" | cache headers {'present' if cache_seen else 'ABSENT'}"
                    + (" | cache_buster=false: the control fetch warmed the shared entry, so a "
                       "poisoning request may have been answered from cache without reaching the "
                       "application at all" if not cache_buster else "")
                    + f" | cache-poisoning: {verdict.grade}"),
        "result": "signal" if hit else "no-signal",
        "data": {"attempts": attempts, "cache_headers_seen": cache_seen,
                 "cache_buster": cache_buster, "cache_token": token, "poisoned": poisoned,
                 "proof_grade": verdict.grade, "missing": verdict.missing},
        "output": "\n".join(
            f"{a['header']:<22} poison={a['poison_status']} clean={a['clean_after']['status']} "
            f"nonce_in_clean={a['nonce_in_clean_response']} changed={a['clean_response_changed']} "
            f"({a.get('difference', {}).get('verdict')}) "
            f"cache={a['clean_after']['cache'] or '-'}" for a in attempts),
        "evidence": clean_record,
        "extra_evidence": extra,
        "next": ("the clean fetch carries what the poisoning request put there, with the "
                 "pre-poisoning control alongside: record the finding, then state in the report "
                 "which cache entry was affected and whether it was the buster entry or the shared "
                 "one"
                 if verdict.proven else
                 ("no cache headers were returned by any fetch, so there is probably no shared "
                  "cache in front of this URL. Unkeyed-input testing against an origin with no "
                  "cache cannot produce this class — park it and spend the budget elsewhere"
                  if not cache_seen else
                  f"a cache is present but the clean fetch did not carry the nonce. Missing: "
                  f"{', '.join(verdict.missing) or 'a change in the clean response'}. The usual "
                  f"reason is that the response was not cacheable (read `cache-control`) or that "
                  f"the header IS keyed (read `vary`); neither is fixed by more header names"
                  + (". The clean response did differ materially from the control entry, which is "
                     "worth one look at the two bodies — but the two entries carry different "
                     "cache-buster values, so a page that varies by itself differs here too. The "
                     "proof is the nonce, not the difference" if hit and not poisoned else ""))),
    }


# --- open redirect -----------------------------------------------------------

PLACEHOLDER = "{payload}"


def _redirect_shapes(off_host: str, own_host: str) -> list[tuple[str, str, str]]:
    """(label, destination value, what it is testing)."""
    return [
        ("absolute", f"https://{off_host}/argus",
         "the plain case: an absolute URL to another host"),
        ("scheme-relative", f"//{off_host}/argus",
         "no scheme, so a filter looking for `http` does not see it; browsers resolve it off-origin"),
        ("backslash", f"/\\{off_host}/argus",
         "browsers normalise the backslash to a slash and leave the origin; most parsers do not"),
        ("backslash-double", f"\\\\{off_host}/argus",
         "the same trick without a leading slash"),
        ("userinfo", f"https://{own_host}@{off_host}/argus",
         "the in-scope host appears first, as userinfo; the authority is the host after the @"),
        ("whitespace", f"%09//{off_host}/argus",
         "a leading tab, which several parsers strip after the filter has run"),
        ("newline", f"%0d%0a//{off_host}/argus",
         "a leading CRLF, same idea, and worth separating because filters differ on it"),
        ("encoded", f"%2f%2f{off_host}/argus",
         "the slashes percent-encoded once"),
        ("double-encoded", f"%252f%252f{off_host}/argus",
         "percent-encoded twice, for a destination that is decoded on the way through"),
    ]


def _location_reading(request_url: str, location: str) -> dict:
    """Where this Location actually points, read twice.

    Two readings, because browsers and parsers disagree and the disagreement is
    the vulnerability in several of the shapes above: `urljoin` leaves a
    backslash alone, and every browser turns it into a slash. Reporting one
    reading would either miss the finding or overstate it, so both are recorded
    and the row says which one made it off-origin.
    """
    request_origin = origin_of(request_url)
    if not location:
        # No Location at all is a third outcome, and it must not read as "the
        # destination stayed in origin". The newline shape produces exactly this:
        # a CRLF in the value splits the header on the way out, so the response
        # carries no Location — which is an observation about header injection,
        # not about the redirect being closed.
        return {"request_origin": request_origin, "readings": {}, "location_present": False,
                "off_origin": False, "off_origin_via": [], "off_origin_location": None}
    readings = {}
    for name, text in (("strict", location),
                       ("browser", (location or "").replace("\\", "/"))):
        try:
            resolved = urllib.parse.urljoin(request_url, text or "")
        except ValueError:
            readings[name] = {"resolved": None, "origin": None, "off_origin": False,
                              "error": "unparseable"}
            continue
        resolved_origin = origin_of(resolved) if "://" in resolved else request_origin
        readings[name] = {"resolved": resolved[:500], "origin": resolved_origin,
                          "off_origin": resolved_origin != request_origin}
    off_via = [name for name, reading in readings.items() if reading["off_origin"]]
    return {"request_origin": request_origin, "readings": readings, "location_present": True,
            "off_origin": bool(off_via), "off_origin_via": off_via,
            "off_origin_location": (readings["strict"]["origin"] if readings["strict"]["off_origin"]
                                    else readings["browser"]["origin"] if off_via else None)}


@SERVER.tool(
    "web.redirect_probe",
    "Measure an open redirect in the one place it is visible: the `Location` header. Sends a set of "
    "destination shapes — absolute, scheme-relative //host, backslash variants, @-userinfo, "
    "whitespace and percent-encoded forms — and reports which produce a Location pointing off "
    "origin, reading each Location twice: strictly, and the way a browser reads it, because "
    "browsers normalise a backslash to a slash and parsers do not. Takes its own two controls: an "
    "in-origin destination, which must stay in origin, and the endpoint with no destination at all. "
    "Nothing here follows a redirect — following one is a request to a host the scope gate never "
    "checked, and httpkit refuses it anyway.",
    {"properties": {
        "url": {"type": "string",
                "description": f"the redirecting URL, with {PLACEHOLDER} where the destination "
                               f"goes, or a plain URL together with `param`"},
        "param": {"type": "string",
                  "description": "the query parameter that carries the destination, when `url` has "
                                 f"no {PLACEHOLDER}"},
        "off_origin_host": {"type": "string",
                            "description": "the host to aim at. Default argus-redirect-<nonce>."
                                           "invalid — a reserved name, because the Location header "
                                           "is the measurement and nothing contacts it. Override it "
                                           "with a host you control when the report needs one"},
        "in_origin_destination": {"type": "string",
                                  "description": "the control destination, default /robots.txt"},
        "method": {"type": "string", "enum": ["GET", "POST", "HEAD"]},
        "headers": _COMMON["headers"], "cookies": _COMMON["cookies"],
        "timeout": _COMMON["timeout"], "note": _COMMON["note"],
        "shapes": {"type": "array", "description": "restrict to these shape labels"},
    }, "required": ["url"]},
    tier=config.TIER_ACTIVE, step="destination-shapes", proves="differential",
)
def redirect_probe(context: ToolContext, url: str, param: str = "", off_origin_host: str = "",
                   in_origin_destination: str = "/robots.txt", method: str = "GET",
                   headers: dict | None = None, cookies: str = "", timeout: int = 15,
                   shapes: list | None = None, note: str = "") -> dict:
    token = context.nonce()
    off_host = off_origin_host or f"argus-redirect-{token}.invalid"
    own_host = _host_only(url) or "localhost"

    if PLACEHOLDER in url:
        template = url
    elif param:
        separator = "&" if "?" in url else "?"
        template = f"{url}{separator}{urllib.parse.quote(param)}={PLACEHOLDER}"
    else:
        raise ToolError(f"put {PLACEHOLDER} in the url at the exact place the destination belongs, "
                        f"or pass `param` with the name of the query parameter that carries it")

    def issue(destination: str):
        return _send(template.replace(PLACEHOLDER, destination), method, headers, None, None,
                     cookies, timeout)

    wanted = _redirect_shapes(off_host, own_host)
    if shapes:
        keep = {str(s).lower() for s in shapes}
        wanted = [shape for shape in wanted if shape[0] in keep] or wanted

    rows, responses, lead = [], {}, None
    for label, destination, testing in wanted:
        response = issue(destination)
        location = response.header("location")
        reading = _location_reading(response.url, location)
        row = {"shape": label, "destination": destination, "status": response.status,
               "location": location or None, "testing": testing, **reading}
        rows.append(row)
        responses[label] = response
        if lead is None and reading["off_origin"] and (response.status or 0) // 100 == 3:
            lead = row

    # One record for the shape that got through, not nine for nine shapes. The
    # whole table is in `extracted.rows`, which is what a reader needs: which
    # encodings the filter let past is the thing the fix has to cover, and nine
    # near-identical 302s in the evidence index hide it rather than showing it.
    lead = lead or rows[0]
    primary = {
        "kind": "probe", "target": responses[lead["shape"]].url, "payload": lead["destination"],
        "note": note,
        "extracted": {"shape": lead["shape"], "destination": lead["destination"],
                      "location": lead["location"],
                      "location_present": lead["location_present"],
                      "off_origin_location": lead["off_origin_location"],
                      "off_origin_via": lead["off_origin_via"],
                      "request_origin": lead["request_origin"],
                      "readings": lead["readings"],
                      "rows": rows},
        **responses[lead["shape"]].to_evidence(1500),
    }

    in_origin = issue(in_origin_destination)
    in_reading = _location_reading(in_origin.url, in_origin.header("location"))
    control_in = {
        "kind": "control", "is_control": True, "target": in_origin.url,
        "payload": in_origin_destination, "note": note,
        "extracted": {"purpose": "an in-origin destination: shows the parameter is honoured, and "
                                 "what an acceptable Location looks like here",
                      "location": in_origin.header("location") or None,
                      "off_origin_location": in_reading["off_origin_location"],
                      "off_origin_via": in_reading["off_origin_via"]},
        **in_origin.to_evidence(1200),
    }
    absent_url = _strip_param(template, param)
    control_absent = None
    if absent_url is not None:
        absent = _send(absent_url, method, headers, None, None, cookies, timeout)
        control_absent = {
            "kind": "control", "is_control": True, "target": absent.url, "note": note,
            "extracted": {"purpose": "the same endpoint with no destination parameter at all: what "
                                     "the answer should have been",
                          "location": absent.header("location") or None},
            **absent.to_evidence(1200),
        }

    off_rows = [r for r in rows if r["off_origin"]]
    no_location = [r for r in rows if not r["location_present"]]
    controls = [c for c in (control_in, control_absent) if c]
    verdict = matrix.verify("open-redirect", [primary, *controls])
    table = "\n".join(
        f"{r['shape']:<16} {r['status'] or '-':<4} {str(r['location'])[:52]:<52} "
        + ("OFF-ORIGIN via " + ",".join(r["off_origin_via"]) if r["off_origin"]
           else "no Location header returned" if not r["location_present"] else "in origin")
        for r in rows)
    return {
        "summary": (f"{len(off_rows)}/{len(rows)} destination shape(s) produced an off-origin "
                    f"Location"
                    + (f": {[r['shape'] for r in off_rows]}" if off_rows else "")
                    + (f" | {len(no_location)} shape(s) returned NO Location header "
                       f"({[r['shape'] for r in no_location]}), which is a header-injection "
                       f"observation, not a closed redirect" if no_location else "")
                    + f" | in-origin control -> {in_origin.status} "
                      f"{in_origin.header('location') or 'no Location'}"
                    + f" | open-redirect: {verdict.grade}"),
        "result": "signal" if off_rows else "no-signal",
        "data": {"rows": rows, "off_origin_shapes": [r["shape"] for r in off_rows],
                 "no_location_shapes": [r["shape"] for r in no_location],
                 "off_origin_host": off_host,
                 "in_origin_control": {"status": in_origin.status,
                                       "location": in_origin.header("location") or None,
                                       "off_origin": in_reading["off_origin"]},
                 "no_destination_control": (None if control_absent is None else
                                            {"status": control_absent["response"]["status"],
                                             "location": (control_absent["extracted"]
                                                          ["location"])}),
                 "proof_grade": verdict.grade, "missing": verdict.missing},
        "output": table,
        "evidence": primary,
        "extra_evidence": controls,
        "next": ("the off-origin Location is recorded with both controls and the requirement is "
                 "met: record the finding, and name in it which shape got through, because that is "
                 "what the fix has to cover"
                 if verdict.proven else
                 ("an off-origin Location is on record, but `open-redirect`'s only required check "
                  "in the current matrix is `outcomes actually differ`, which compares HTTP STATUS "
                  "— and this endpoint answers the same 3xx to the in-origin and the off-origin "
                  "destination, which is exactly what being vulnerable looks like. The evidence "
                  "carries extracted.off_origin_location for a Location-based check; until the "
                  "matrix has one, this grades `unproven` and ledger.record_finding will refuse "
                  "it. Do not re-send more destination shapes: the measurement already succeeded"
                  if off_rows else
                  "no shape produced an off-origin Location, so the destination is validated or "
                  "ignored. Read what the parameter actually does before trying more encodings")
                 + (f" | separately: {[r['shape'] for r in no_location]} came back with no "
                    f"Location header at all. A CRLF in the value splitting the response header "
                    f"is a header-injection observation and belongs to its own hypothesis, not "
                    f"to this one" if no_location else "")),
    }


def _strip_param(template: str, param: str) -> str | None:
    """The same endpoint with the destination parameter removed, for the control.

    Returns None when the caller gave a `{payload}` template instead of a named
    parameter: substituting an empty string is not the same observation as the
    parameter being absent, and claiming it is would make the control a fiction.
    """
    if not param:
        return None
    base = template.replace(PLACEHOLDER, "")
    split = urllib.parse.urlsplit(base)
    query = [(key, value) for key, value in
             urllib.parse.parse_qsl(split.query, keep_blank_values=True) if key != param]
    return urllib.parse.urlunsplit(split._replace(query=urllib.parse.urlencode(query)))


# --- GraphQL -----------------------------------------------------------------

INTROSPECTION = ("query{__schema{queryType{name} mutationType{name} "
                 "types{name kind fields{name args{name} type{name kind ofType{name}}}}}}")
SUGGESTION_PROBE = "query{__typename %s}"
_DID_YOU_MEAN = re.compile(r"[Dd]id you mean ([^?.]+)")
_SUGGESTION_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def _suggestions(response) -> list[str]:
    """Field names a server offered after a deliberately wrong field.

    Read from the parsed `errors[].message` when the body is JSON, and from the
    raw body only as a fallback. Regexing the raw body first produced names
    carrying the JSON escaping around them — `\\"users\\"` — which is a schema
    field name that does not exist, recorded as evidence that it does.
    """
    parsed = _json_of(response)
    messages = []
    if isinstance(parsed, dict):
        messages = [str(error.get("message") or "") for error in (parsed.get("errors") or [])
                    if isinstance(error, dict)]
    if not messages:
        messages = [response.body or ""]
    names: set[str] = set()
    for message in messages:
        for phrase in _DID_YOU_MEAN.findall(message):
            names.update(_SUGGESTION_NAME.findall(phrase.replace(" or ", ",")))
    return _bounded(sorted(names - {"or"}), 24)
_SENSITIVE_FIELD = re.compile(r"(?i)(user|account|admin|secret|token|password|credential|email|"
                              r"ssn|card|invoice|order|message|note|session|key)")


def _graphql_send(url: str, document, headers: dict | None, cookies: str, timeout: int,
                  variables: dict | None = None):
    payload = document if isinstance(document, list) else {"query": document,
                                                           **({"variables": variables}
                                                              if variables else {})}
    return httpkit.request("POST", url, headers={**(headers or {}),
                                                 "Content-Type": "application/json"},
                           data=json.dumps(payload), cookies=cookies or None, timeout=timeout or 20)


def _json_of(response) -> dict | list | None:
    try:
        return json.loads(response.body or "")
    except (ValueError, TypeError):
        return None


def _inventory(parsed) -> dict:
    schema = (((parsed or {}).get("data") or {}).get("__schema") or {}) if isinstance(parsed, dict) else {}
    types = []
    for entry in _bounded(schema.get("types") or [], 60):
        name = entry.get("name") or ""
        if name.startswith("__"):
            continue
        fields = [f.get("name") for f in _bounded(entry.get("fields") or [], 24) if f.get("name")]
        types.append({"name": name, "kind": entry.get("kind"), "fields": fields})
    return {"query_type": (schema.get("queryType") or {}).get("name"),
            "mutation_type": (schema.get("mutationType") or {}).get("name"),
            "types": types, "type_count": len(types)}


def _state_changing_types(inventory: dict) -> set[str]:
    """The type names whose fields change state when they are selected."""
    names = {inventory.get("mutation_type") or "Mutation", "Subscription"}
    return {name for name in names if name}


def _interesting(inventory: dict) -> list[str]:
    """Queries worth trying, named from the inventory. An inventory of a hundred
    types is not a lead; the fields whose names say they hold other people's
    records are.

    The mutation and subscription types are excluded. `next` tells the model to
    take a field from this list and send it with mode=query, and the mutation
    type's fields match the same sensitive-name pattern as everything else —
    `deleteUserAccount`, `resetAdminPassword` — so listing them here was an
    instruction to send a state-changing document on a read-only budget. They are
    reported separately, as what they are.
    """
    skip = _state_changing_types(inventory)
    out = []
    for entry in inventory.get("types") or []:
        if (entry.get("name") or "") in skip:
            continue
        for field in entry.get("fields") or []:
            if _SENSITIVE_FIELD.search(field) or _SENSITIVE_FIELD.search(entry["name"] or ""):
                out.append(f"{entry['name']}.{field}")
    return _bounded(sorted(set(out)), 24)


def _state_changing_fields(inventory: dict) -> list[str]:
    """What the schema says it will let a caller change. Reported, never offered
    as a next step: a mutation is an engagement decision, not a read."""
    wanted = _state_changing_types(inventory)
    out = [f"{entry['name']}.{field}"
           for entry in inventory.get("types") or []
           if (entry.get("name") or "") in wanted
           for field in entry.get("fields") or []]
    return _bounded(sorted(set(out)), 24)


# A document declaring a mutation or a subscription changes state, whatever the
# field is called. The word is matched anywhere in the document rather than at
# its start, because a multi-operation document carries one per operation and the
# server runs whichever `operationName` picks. A query that merely contains the
# word is refused too: a refusal the caller can read and act on is cheaper than
# a write at the active tier.
_STATE_CHANGING_GQL = re.compile(r"(?i)(?<![\w$])(mutation|subscription)(?![\w$])")


def _first_rows(parsed) -> tuple[str | None, list]:
    """The first list of objects under `data`, and the field path that named it.

    A GraphQL result is a tree; the proof requirement wants a named collection
    and the documents it returned. So the walk stops at the first list of objects
    and reports where it was, rather than flattening the whole response into
    something that cannot be pointed at.
    """
    data = (parsed or {}).get("data") if isinstance(parsed, dict) else None
    queue: list[tuple[str, object]] = [(key, value) for key, value in (data or {}).items()] \
        if isinstance(data, dict) else []
    while queue:
        path, value = queue.pop(0)
        if isinstance(value, list) and value and all(isinstance(item, dict) for item in value):
            return path, value
        if isinstance(value, dict):
            queue.extend((f"{path}.{key}", child) for key, child in value.items())
    return None, []


@SERVER.tool(
    "web.graphql_probe",
    "Map a GraphQL endpoint in three passes and then read from it under a bound. `inventory` (the "
    "default) runs introspection, then field suggestion for when introspection is disabled — a "
    "deliberately wrong field name makes many servers answer `Did you mean ...` — then a "
    "batched-array query to show whether N operations can ride in one request. `query` sends a "
    "document you supply and keeps at most five documents from the first named collection in the "
    "answer; a document declaring a mutation or a subscription is refused unless the engagement "
    "enables the intrusive tier, because this tool is declared read-only and the document is "
    "yours. The inventory lists the mutation type's fields separately and never offers them as a "
    "next step. An introspection dump is an inventory and NOT the proof: the graphql-exposure "
    "requirement is documents from a named collection the caller should not have reached, which "
    "only the `query` mode can produce.",
    {"properties": {
        "url": {"type": "string", "description": "the GraphQL endpoint, usually /graphql"},
        "mode": {"type": "string", "enum": ["inventory", "introspect", "suggest", "batch", "query"]},
        "query": {"type": "string", "description": "the document to send in `query` mode"},
        "variables": {"type": "object", "description": "variables for `query` mode"},
        "batch_size": {"type": "integer", "description": "operations per batch, 2-10, default 3"},
        "headers": _COMMON["headers"], "cookies": _COMMON["cookies"],
        "timeout": _COMMON["timeout"], "note": _COMMON["note"],
    }, "required": ["url"]},
    tier=config.TIER_ACTIVE, proves="data_extraction",
)
def graphql_probe(context: ToolContext, url: str, mode: str = "inventory", query: str = "",
                  variables: dict | None = None, batch_size: int = 3,
                  headers: dict | None = None, cookies: str = "", timeout: int = 20,
                  note: str = "") -> dict:
    if mode == "query" and not query:
        raise ToolError("`query` mode needs the document to send. Run mode=inventory first and "
                        "pick a field from `interesting_fields`; a query the tool invented would "
                        "be a guess recorded as evidence.")

    if mode == "query":
        # This tool is declared `active`, which means read-only, and the document
        # is the caller's. A mutation sent through it changed server state on an
        # engagement that had enabled nothing beyond `active` — the gate had
        # already passed on the tool's own tier and never saw the document. So
        # the declaration is read out of the document itself, here, before the
        # request is built.
        declared = _STATE_CHANGING_GQL.search(query)
        if declared:
            refusal = _require_intrusive(
                context, f"a GraphQL document declaring a {declared.group(1).lower()}, which "
                         f"changes server state")
            if refusal:
                return refusal
        response = _graphql_send(url, query, headers, cookies, timeout, variables)
        parsed = _json_of(response)
        collection, rows = _first_rows(parsed)
        errors = [str(e.get("message"))[:300] for e in
                  (parsed.get("errors") or [] if isinstance(parsed, dict) else [])]
        evidence = {
            "kind": "probe", "target": url, "payload": bound(query, 2000), "note": note,
            "extracted": {"table": collection, "rows": _bounded(rows, 5),
                          "row_count": len(rows), "rows_kept": min(len(rows), 5),
                          "graphql_errors": _bounded(errors, 5),
                          "operation": bound(query, 500)},
            **response.to_evidence(BODY_KEEP),
        }
        verdict = matrix.verify("graphql-exposure", [evidence])
        # The document is the caller's, so the row cap cannot be enforced on the
        # request the way sqlmap's `--stop` is. What the tool can do is refuse to
        # be quiet about it: five documents are kept, and a larger answer is
        # named here and in the report as a collection taken wider than the proof
        # needed.
        overrun = len(rows) - 5 if len(rows) > 5 else 0
        return {
            "summary": (f"{collection or 'no named collection'}: {len(rows)} document(s), "
                        f"{min(len(rows), 5)} kept | HTTP {response.status}"
                        + (f" | {len(errors)} graphql error(s)" if errors else "")
                        + (f" | the answer carried {overrun} document(s) more than the proof "
                           f"needs; a bounded span of the raw body is on record too" if overrun
                           else "")
                        + f" | graphql-exposure: {verdict.grade}"),
            "result": "signal" if rows else "no-signal",
            "step": "bounded-document-read",
            "data": {"collection": collection, "row_count": len(rows),
                     "rows": _bounded(rows, 5), "errors": _bounded(errors, 5),
                     "proof_grade": verdict.grade, "missing": verdict.missing},
            "output": bound(json.dumps(_bounded(rows, 5), ensure_ascii=False, indent=2)
                            if rows else (response.body or ""), 6000),
            "evidence": evidence,
            "next": ((("documents from a named collection are on record, bounded to five: record "
                       "the finding, and say in it whose records these are and why this caller "
                       "should not have reached them — that sentence is the finding, not the row "
                       "count")
                      + (f". Next time ask for fewer: the document returned {len(rows)} and the "
                         f"proof is five, so the report has to state that the read was wider than "
                         f"it needed to be" if overrun else ""))
                     if verdict.proven else
                     f"no named collection with at least one document: {', '.join(verdict.missing)}. "
                     f"The errors above usually say which argument the server wanted; read them "
                     f"rather than permuting the query"),
        }

    passes, records = {}, []
    want = ("introspect", "suggest", "batch") if mode == "inventory" else (mode,)

    if "introspect" in want:
        response = _graphql_send(url, INTROSPECTION, headers, cookies, timeout)
        parsed = _json_of(response)
        inventory = _inventory(parsed)
        enabled = bool(inventory.get("types"))
        passes["introspection"] = {"enabled": enabled, "status": response.status,
                                   "type_count": inventory.get("type_count", 0),
                                   "query_type": inventory.get("query_type"),
                                   "mutation_type": inventory.get("mutation_type"),
                                   "interesting_fields": _interesting(inventory),
                                   "state_changing_fields": _state_changing_fields(inventory)}
        records.append({"kind": "probe", "target": url, "payload": INTROSPECTION, "note": note,
                        "extracted": {"introspection_enabled": enabled, "inventory": inventory,
                                      "interesting_fields": _interesting(inventory),
                                      "state_changing_fields": _state_changing_fields(inventory)},
                        **response.to_evidence(BODY_KEEP)})

    if "suggest" in want:
        probe_field = f"argus{context.nonce()[5:]}"
        response = _graphql_send(url, SUGGESTION_PROBE % probe_field, headers, cookies, timeout)
        suggestions = _suggestions(response)
        passes["field_suggestion"] = {"status": response.status, "probe_field": probe_field,
                                      "suggestions": suggestions,
                                      "note": ("suggestion is how the schema leaks when "
                                               "introspection is off" if suggestions else
                                               "no suggestions returned")}
        records.append({"kind": "probe", "target": url, "payload": SUGGESTION_PROBE % probe_field,
                        "note": note,
                        "extracted": {"field_suggestions": suggestions,
                                      "probe_field": probe_field},
                        **response.to_evidence(2000)})

    if "batch" in want:
        size = max(2, min(int(batch_size or 3), 10))
        response = _graphql_send(url, [{"query": "query{__typename}"} for _ in range(size)],
                                 headers, cookies, timeout)
        parsed = _json_of(response)
        batched = isinstance(parsed, list) and len(parsed) == size
        passes["batching"] = {"status": response.status, "sent": size,
                              "returned": len(parsed) if isinstance(parsed, list) else 0,
                              "enabled": batched,
                              "note": ("N operations per request: a rate limit counted in requests "
                                       "does not see them" if batched else
                                       "the array form was not answered as an array")}
        records.append({"kind": "probe", "target": url, "payload": f"[{size} x query{{__typename}}]",
                        "note": note,
                        "extracted": {"batching_enabled": batched, "batch_size": size},
                        **response.to_evidence(2000)})

    leads = (passes.get("introspection", {}).get("interesting_fields")
             or passes.get("field_suggestion", {}).get("suggestions") or [])
    writeable = passes.get("introspection", {}).get("state_changing_fields") or []
    primary = records[0] if records else None
    return {
        "summary": (f"introspection {'ENABLED' if passes.get('introspection', {}).get('enabled') else 'off'}"
                    f" ({passes.get('introspection', {}).get('type_count', 0)} types)"
                    f" | {len(passes.get('field_suggestion', {}).get('suggestions') or [])} field "
                    f"suggestion(s)"
                    f" | batching {'enabled' if passes.get('batching', {}).get('enabled') else 'off'}"
                    f" | {len(leads)} field(s) worth querying"
                    + (f" | {len(writeable)} mutation field(s) listed, NOT offered as a next step"
                       if writeable else "")),
        "result": "signal" if leads or passes.get("introspection", {}).get("enabled") else "no-signal",
        "step": "graphql-inventory",
        "data": {"passes": passes, "interesting_fields": _bounded(leads, 24),
                 "state_changing_fields": _bounded(writeable, 24)},
        "output": bound(json.dumps(passes, ensure_ascii=False, indent=2), 8000),
        "evidence": primary,
        "extra_evidence": [rec for rec in records if rec is not primary],
        "next": ((("this is an inventory, not a finding: an introspection dump proves the schema is "
                   "readable and nothing else. graphql-exposure needs documents from a named "
                   "collection this caller should not have reached, so pick one of the fields "
                   "above and run mode=query with a document that asks for it plus an id you are "
                   "not entitled to — then the five kept documents are the proof")
                  + (f". The {len(writeable)} field(s) in state_changing_fields are the mutation "
                     f"type's and are not on that list: selecting one writes to the application, "
                     f"so it needs the intrusive tier, and this tool refuses a document declaring "
                     f"a mutation without it. The schema offering a mutation is not a finding "
                     f"either — what would be is an authorisation check it does not make, and that "
                     f"is read, acted and read again under csrf" if writeable else ""))
                 if leads else
                 "introspection is off and the server offered no suggestions, so the schema is not "
                 "readable from here. Mine the client bundle with recon.js_mine for the operations "
                 "the application itself sends; that is where the field names are"),
    }


# --- file upload -------------------------------------------------------------

UPLOAD_LOG = "web-uploads.jsonl"
_PATHISH_CHARS = r"[\w./:~%+-]"


def _inert_content(token: str) -> bytes:
    """The only content this tool will upload.

    There is no argument for it, deliberately. A tool that can be handed file
    content can be talked into uploading a shell, and this system proves code
    execution with `id; echo <nonce>` through `proof.exec_marker` or not at all.
    What this file establishes is whether the upload is accepted and where it is
    served from — the precondition, which is a different question from execution
    and is answered by text.
    """
    return (f"argus upload probe {token}\n"
            f"inert marker, no code, written {now_iso()}\n"
            f"safe to delete; argus records its own cleanup\n").encode()


_HEADER_UNSAFE = re.compile(r'[\r\n"]')


def _header_safe(value, what: str) -> str:
    """A caller's value on its way into a MIME header line, with the characters
    that end one refused.

    This guard is what makes "there is no argument for the file's content" true.
    Without it `filename` closed its own quoted string and opened the part's
    body: the template

        shell-{nonce}.php"\\r\\nContent-Type: application/x-php\\r\\n\\r\\n<?php ... ?>

    stored a file named `shell-<nonce>.php` whose body began with the caller's
    PHP, because a part's headers end at the first blank line and everything
    after it — the inert marker included — is body. Measured against a stdlib
    multipart parser, not reasoned about. The `{nonce}` requirement does not
    help: the nonce can sit anywhere in the template. The extension is the
    caller's choice because the extension is what is being tested; the bytes
    never are.
    """
    text = str(value)
    if _HEADER_UNSAFE.search(text):
        raise ToolError(
            f"{what} contains a carriage return, a newline or a double quote: {text!r}. Those "
            f"characters end a MIME header line, so a value carrying them writes the rest of the "
            f"part — including the file's own body — and this tool would be uploading content the "
            f"caller supplied. The extension is yours to choose; the bytes are not.")
    return text


def _multipart(field: str, filename: str, content_type: str, content: bytes,
               fields: dict | None) -> tuple[bytes, str]:
    boundary = "argus" + secrets.token_hex(12)
    chunks = []
    for name, value in (fields or {}).items():
        name = _header_safe(name, "a multipart field name")
        value = _header_safe(value, f"the value of multipart field {name!r}")
        chunks.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n"
                      f"{value}\r\n".encode())
    chunks.append((f"--{boundary}\r\nContent-Disposition: form-data; name=\""
                   f"{_header_safe(field, 'the form field name')}\"; "
                   f"filename=\"{_header_safe(filename, 'the filename')}\"\r\n"
                   f"Content-Type: {_header_safe(content_type, 'content_type')}\r\n\r\n").encode())
    chunks.append(content)
    chunks.append(f"\r\n--{boundary}--\r\n".encode())
    return b"".join(chunks), f"multipart/form-data; boundary={boundary}"


def _candidate_paths(body: str, token: str, origin: str, serve_url: str, filename: str,
                     allowed=None) -> tuple[list[str], list[str]]:
    """Where the uploaded file might be served from: (fetchable, refused).

    Every candidate comes out of the target's own response, so each one is a new
    target and is checked twice — the origin the scope gate saw, and the
    engagement's scope rules. The origin test alone was not enough: a scope of
    `http://host/app/` and a response naming `/admin/uploads/<nonce>` share an
    origin, and this function fetched it, which is a request to a path nothing
    authorised chosen by the target. A response naming
    `https://cdn.example.net/u/<nonce>` is interesting and is reported in the
    refused list, never fetched.
    """
    found: list[str] = []
    if serve_url:
        found.append(serve_url.replace("{nonce}", token).replace("{filename}", filename))
    pattern = re.compile(_PATHISH_CHARS + r"*" + re.escape(token) + _PATHISH_CHARS + r"*")
    for match in pattern.findall(body or "")[:20]:
        found.append(match)
    parsed = None
    try:
        parsed = json.loads(body or "")
    except (ValueError, TypeError):
        parsed = None
    stack = [parsed]
    while stack:
        item = stack.pop()
        if isinstance(item, dict):
            stack.extend(item.values())
        elif isinstance(item, list):
            stack.extend(item)
        elif isinstance(item, str) and (token in item or filename in item):
            found.append(item)
    out, refused, seen = [], [], set()
    for candidate in found:
        candidate = candidate.strip().strip('",\'')
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        resolved = urllib.parse.urljoin(origin + "/", candidate)
        if resolved in seen:
            continue
        seen.add(resolved)
        if origin_of(resolved) != origin_of(origin):
            refused.append(f"{resolved} (another origin)")
        elif allowed is not None and not allowed(resolved):
            refused.append(f"{resolved} (in the origin, outside the engagement's scope)")
        else:
            out.append(resolved)
    return out[:5], refused[:5]


@SERVER.tool(
    "web.upload_probe",
    "Upload exactly ONE inert marker file named with a nonce, then report whether and where it is "
    "served back. There is no argument for the file's content: the content is a text marker, "
    "always, so this tool cannot be talked into uploading a shell. What it establishes is the "
    "precondition for file-upload-rce — the upload is accepted, with this extension, and the stored "
    "file is reachable at a path — which is a different question from execution, and this system "
    "proves execution with `id; echo <nonce>` or not at all. INTRUSIVE: it writes a file to the "
    "target. It records what cleanup needs, and mode=cleanup removes the file and records the "
    "removal; run it before you close the engagement. mode=list reads this engagement's own upload "
    "log and sends no request, but still spends a probe, because the tier and budget gate is "
    "applied per tool rather than per mode. A path discovered in the response is a new target "
    "chosen by the target, so it is fetched only when it resolves inside the origin the scope gate "
    "checked AND inside this engagement's scope rules — a scope of http://host/app/ does not "
    "authorise http://host/admin/. Anything else is reported in `paths_not_fetched` and left "
    "alone.",
    {"properties": {
        "url": {"type": "string", "description": "the upload endpoint"},
        "mode": {"type": "string", "enum": ["upload", "cleanup", "list"]},
        "field": {"type": "string", "description": "multipart form field name, default `file`"},
        "filename": {"type": "string",
                     "description": "filename template; must contain {nonce}. Default "
                                    "argus-{nonce}.txt. The extension is yours to choose — that is "
                                    "the thing being tested — and the content stays inert whatever "
                                    "you choose. A carriage return, a newline or a double quote in "
                                    "it is refused: those end a MIME header line, and a filename "
                                    "carrying them would write the file's body"},
        "content_type": {"type": "string", "description": "the part's Content-Type, default text/plain"},
        "fields": {"type": "object", "description": "extra multipart form fields"},
        "encoding": {"type": "string", "enum": ["multipart", "raw"],
                     "description": "multipart form-data (default), or the bytes as the whole body"},
        "method": {"type": "string", "enum": ["POST", "PUT"]},
        "serve_url": {"type": "string",
                      "description": "where to look for the file afterwards; {nonce} and {filename} "
                                     "are substituted. Must be in the same origin as `url`"},
        "token": {"type": "string", "description": "cleanup mode: the nonce of the file to remove"},
        "cleanup_url": {"type": "string",
                        "description": "cleanup mode: the URL to call; defaults to the served URL"},
        "cleanup_method": {"type": "string", "enum": ["DELETE", "POST", "GET"]},
        "headers": _COMMON["headers"], "cookies": _COMMON["cookies"],
        "timeout": _COMMON["timeout"], "note": _COMMON["note"],
    }, "required": ["url"]},
    tier=config.TIER_INTRUSIVE, proves=None,
)
def upload_probe(context: ToolContext, url: str, mode: str = "upload", field: str = "file",
                 filename: str = "argus-{nonce}.txt", content_type: str = "text/plain",
                 fields: dict | None = None, encoding: str = "multipart", method: str = "POST",
                 serve_url: str = "", token: str = "", cleanup_url: str = "",
                 cleanup_method: str = "DELETE", headers: dict | None = None, cookies: str = "",
                 timeout: int = 30, note: str = "") -> dict:
    log_path = context.paths.artifacts / UPLOAD_LOG
    origin = origin_of(url)

    if mode == "list":
        # The log is append-only, because an audit trail that rewrites itself is
        # not one. Folding by token here is what makes the listing a current
        # state rather than a history: without it a cleaned-up file is counted
        # twice, once as uploaded and once as removed.
        folded: dict[str, dict] = {}
        for entry in read_jsonl(log_path):
            folded[str(entry.get("token"))] = {**folded.get(str(entry.get("token")), {}), **entry}
        entries = list(folded.values())
        outstanding = [e for e in entries if not e.get("removed")]
        return {
            "summary": f"{len(entries)} upload(s) recorded, {len(outstanding)} not yet removed",
            # Never `signal`: this mode sends no request, so nothing discriminating
            # happened and the controller must not read it as progress on the class.
            "result": "no-signal",
            "step": "upload-list",
            "data": {"uploads": _bounded(entries, 20), "outstanding": _bounded(outstanding, 20)},
            "output": "\n".join(f"{e.get('ts')} {e.get('token')} {e.get('filename')} "
                                f"served={e.get('served_url') or '-'} "
                                f"removed={bool(e.get('removed'))}" for e in _bounded(entries, 20)),
            "evidence": None,
            "next": ("run mode=cleanup for each token above before closing the engagement; a file "
                     "left on a target is an artifact the client did not agree to"
                     if outstanding else "nothing outstanding"),
        }

    if mode == "cleanup":
        entries = read_jsonl(log_path)
        entry = next((e for e in reversed(entries)
                      if e.get("token") == token or (token and token in str(e.get("filename")))), None)
        if entry is None and not cleanup_url:
            raise ToolError(
                f"no upload recorded for token {token!r} in {log_path}. Pass `cleanup_url` "
                f"explicitly if the file was uploaded outside this engagement; cleaning up a path "
                f"this tool cannot tie to an upload it made would be a request with no record "
                f"behind it.")
        entry = entry or {}
        served = cleanup_url or entry.get("served_url") or entry.get("stored_path") or ""
        if not served:
            raise ToolError("the upload was never located, so there is nothing to call. Pass "
                            "`cleanup_url` with the delete endpoint this application exposes.")
        if origin_of(served) != origin:
            raise ToolError(f"the cleanup URL {served!r} is not in the origin {origin} that was "
                            f"scope-checked for this call. Call it against its own origin so the "
                            f"gate sees it.")
        _require_in_scope(context, served, "the cleanup URL")
        removal = _send(served, cleanup_method, headers, None, None, cookies, timeout)
        recheck = _send(served, "GET", headers, None, None, cookies, timeout)
        # Two ways to be gone, and the soft one needs the removal to have
        # succeeded. "the re-fetch does not echo the token" on its own read a
        # redirect to a login page, or an empty 200, as a deleted file: the
        # removal request could have been refused outright and this log would
        # still say `removed`. That log is the record of what was left on someone
        # else's host, so it may not guess.
        removal_ok = removal.status is not None and removal.status < 400
        token_absent = bool(entry.get("token")) and entry["token"] not in (recheck.body or "")
        gone = ((recheck.status is not None and recheck.status >= 400)
                or (removal_ok and token_absent))
        append_jsonl(log_path, {**entry, "ts": now_iso(), "token": entry.get("token") or token,
                                "removed": bool(gone), "cleanup_url": served,
                                "cleanup_status": removal.status, "recheck_status": recheck.status})
        evidence = {
            "kind": "artifact", "target": served, "note": note,
            "extracted": {"cleanup_of": entry.get("token") or token, "cleanup_url": served,
                          "cleanup_method": cleanup_method, "cleanup_status": removal.status,
                          "recheck_status": recheck.status, "removed": bool(gone),
                          "removal_accepted": removal_ok,
                          "purpose": "the removal of the file this probe wrote, on record"},
            **removal.to_evidence(1200),
        }
        return {
            "summary": (f"cleanup {cleanup_method} {served} -> {removal.status}; re-fetch "
                        f"{recheck.status}; "
                        + ("the file is gone" if gone else "THE FILE IS STILL THERE")
                        + ("" if removal_ok else
                           f" | the removal request itself returned {removal.status}, so this is "
                           f"not a removal the application accepted")),
            "result": "signal" if gone else "no-signal",
            "step": "upload-cleanup",
            "data": {"removed": bool(gone), "removal_accepted": removal_ok,
                     "cleanup_status": removal.status,
                     "recheck_status": recheck.status, "url": served},
            "output": bound(recheck.body or "", 1200),
            "evidence": evidence,
            "next": ("removal recorded; nothing of this probe is left on the target"
                     if gone else
                     "the file is still served. Say so in the report with its path: an artifact "
                     "left behind is something the client has to remove, and it belongs in the "
                     "report rather than in a cleanup retry loop"),
        }

    # --- upload ---
    nonce = context.nonce()
    if "{nonce}" not in filename:
        raise ToolError(
            "the filename template must contain {nonce}. The nonce is how the stored file is tied "
            "to this probe and how cleanup finds it again; an anonymous file left on a target "
            "cannot be attributed or removed.")
    # Checked here as well as inside `_multipart`, so that `encoding=raw` — which
    # builds no part and puts `content_type` straight into a request header —
    # refuses for the same reason instead of failing as a transport error.
    name = _header_safe(filename.replace("{nonce}", nonce), "the filename")
    content_type = _header_safe(content_type, "content_type")
    field = _header_safe(field, "the form field name")
    if serve_url:
        # Checked BEFORE the upload is sent. A serve path the tool may not fetch
        # was previously dropped in silence, and the summary then read "not
        # located (0 candidate path(s) tried)" — a file written to the target and
        # a result that says the path was tried when it never was. Refuse first,
        # write nothing.
        asked = urllib.parse.urljoin(origin + "/", serve_url.replace("{nonce}", nonce)
                                     .replace("{filename}", name))
        if origin_of(asked) != origin:
            raise ToolError(
                f"serve_url resolves to {asked!r}, which is on {origin_of(asked)} and not on "
                f"{origin}, the origin the scope gate checked for this call. A CDN-hosted serve "
                f"path is a host this engagement never declared: add it to the scope and probe it "
                f"as its own target, or leave serve_url out and read `candidate_paths`.")
        _require_in_scope(context, asked, "the serve URL")
    content = _inert_content(nonce)
    if encoding == "raw":
        body, declared_type = content, content_type
    else:
        body, declared_type = _multipart(field, name, content_type, content, fields)
    sent_headers = {**(headers or {}), "Content-Type": declared_type}
    response = httpkit.request(method, url, headers=sent_headers, data=body,
                               cookies=cookies or None, timeout=timeout or 30)

    accepted = response.status is not None and response.status < 400
    candidates, refused_candidates = _candidate_paths(
        response.body or "", nonce, origin, serve_url, name,
        allowed=lambda target: bool(_scope_verdict(context, target)))
    served_url, served_response, served_type = None, None, None
    for candidate in candidates:
        fetched = _send(candidate, "GET", headers, None, None, cookies, timeout)
        if fetched.status == 200 and nonce in (fetched.body or ""):
            served_url, served_response, served_type = candidate, fetched, fetched.header("content-type")
            break
    append_jsonl(log_path, {"ts": now_iso(), "token": nonce, "filename": name,
                            "upload_url": url, "method": method, "encoding": encoding,
                            "status": response.status, "served_url": served_url,
                            "candidates": candidates, "removed": False, "note": note})

    evidence = {
        "kind": "probe", "target": url, "payload": f"{method} {url} <- {name} ({len(content)}B inert)",
        "note": note,
        # The token lives in `extracted.upload_token`, NOT in `nonce`. Every
        # record attached to a file-upload-rce hypothesis is graded by
        # verify_command_output, which reads a record's own nonce appearing
        # anywhere in that record as "the target echoed our marker" — and a
        # stored filename containing the nonce would satisfy that without
        # anything having executed. That is a proof of nothing, so this record
        # does not offer the field.
        "extracted": {"upload_token": nonce, "filename": name, "accepted": accepted,
                      "content_inert": True, "content_bytes": len(content),
                      "stored_path": served_url, "served": bool(served_url),
                      "served_content_type": served_type,
                      "candidate_paths": candidates,
                      "paths_not_fetched": refused_candidates,
                      "cleanup": {"tool": "web.upload_probe", "mode": "cleanup", "token": nonce,
                                  "log": str(log_path)}},
        **response.to_evidence(BODY_KEEP),
    }
    extra = []
    if served_response is not None:
        extra.append({
            "kind": "probe", "target": served_url,
            "extracted": {"upload_token": nonce, "purpose": "the stored file fetched back",
                          "served_content_type": served_type},
            **served_response.to_evidence(1200),
        })
    return {
        "summary": (f"upload {'accepted' if accepted else 'rejected'} (HTTP {response.status}) as "
                    f"{name}"
                    + (f" | served at {served_url} as {served_type}" if served_url else
                       f" | not located ({len(candidates)} candidate path(s) tried)")
                    + (f" | {len(refused_candidates)} path(s) the response named were NOT fetched: "
                       f"{refused_candidates}" if refused_candidates else "")
                    + f" | cleanup: web.upload_probe mode=cleanup token={nonce}"),
        "result": "signal" if served_url else ("signal" if accepted else "no-signal"),
        "step": "upload-inert-marker",
        "data": {"token": nonce, "filename": name, "accepted": accepted,
                 "status": response.status, "served_url": served_url,
                 "served_content_type": served_type, "candidate_paths": candidates,
                 "paths_not_fetched": refused_candidates,
                 "upload_log": str(log_path)},
        "output": bound(response.body or "", 2000),
        "evidence": evidence,
        "extra_evidence": extra,
        "next": (f"the file is accepted and served from {served_url} as {served_type!r}. That is "
                 f"the precondition, not the proof: file-upload-rce requires the output of "
                 f"`id; echo <nonce>` returned by the target, and this tool will not upload code "
                 f"to get it. If the served path is handled by an interpreter, proving execution "
                 f"needs a file that runs a command — that is an engagement decision a human "
                 f"makes, and it belongs in scripts/exploits/ with the intrusive tier and its own "
                 f"cleanup. When the served path takes a parameter, point proof.exec_marker at it "
                 f"instead. Either way, run mode=cleanup token={nonce} when you are done"
                 if served_url else
                 (f"the upload returned {response.status} but the stored file was not located, so "
                  f"the class is not yet reachable: without a served path there is nothing an "
                  f"interpreter could run. Find where uploads are served — recon.js_mine on the "
                  f"client bundle, fuzz.content under the upload directory — then re-run with "
                  f"serve_url. Cleanup token is {nonce} if the write did land"
                  + (f". The response named {refused_candidates}, which this tool refused to "
                     f"fetch: outside the origin the gate checked, or outside this engagement's "
                     f"scope rules. Widen the scope deliberately and probe it as its own target "
                     f"rather than following a path the target chose" if refused_candidates else "")
                  if accepted else
                  f"the endpoint rejected the upload with {response.status}. Read the response "
                  f"above: it usually names the restriction (extension, size, magic bytes, a "
                  f"missing form field). One rejected extension is not a closed class, and one "
                  f"accepted extension is not an open one")),
    }
