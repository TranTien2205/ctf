#!/usr/bin/env python3
"""Fire overlapping requests and report what concurrency produced that serial execution never did.

`web-race-condition` is verified here by two chain cards, and both of their first
probes were hand-written with threads while the clock ran: the SSOS card hammers
one registration request to win a check-then-act window against the challenge's
own bot, and the ApexSurvive card sends two interleaved profile updates to see
which address receives which token. Hand-rolled, that code always skips the same
three things. It never proves the requests actually overlapped, so a run that
merely went fast gets read as a race. It has no serial baseline, so the tool's
author compares the burst against a memory of what the endpoint "normally" does.
And it treats every differing body as a finding, when most of the difference is a
fresh CSRF token and a timestamp. This holds the three together:

  baseline      --baseline-count requests sent strictly one at a time; the set of
                response signatures serial execution can produce is measured, not
                remembered
  burst         --count requests through a ThreadPoolExecutor, released together
                by a threading.Barrier so the wave is tight
  overlap       per-request in-flight intervals, so max_in_flight is a number.
                max_in_flight == 1 means nothing raced and the verdict stays
                inconclusive no matter what the bodies said
  signature     status plus a body normalised for volatile fields (uuid,
                timestamp, and any run of 6+ hex or digit characters, all to one
                placeholder) — so a per-request receipt id cannot fake a
                divergence whichever characters it was drawn as.
                --signature-mode raw-body turns the normalisation off and shows
                what it was hiding

The finding is a signature present under concurrency and absent from the serial
baseline. Anything else is recorded with its count: "0 of 24 concurrent responses
produced a signature the baseline had not already produced" is a result, and it
is `inconclusive`, never a confirm.

Write-shaped by definition — a race that changes nothing is not worth racing — so
it refuses to run without --write-ack, and --concurrency is capped: a shared
challenge database dies of load faster than it dies of a race. Read the matching
chain card's `blast_radius` first (the two verified race cards here are
knowledge/chains/htb-ssos-oauth-registration-race-cookie-swap-json-csrf.json,
whose instance is permanently consumed once its startup has run, and
knowledge/chains/htb-apexsurvive-profile-race-template-literal-xss-template-overwrite-rce.json),
and delete every object the burst created before leaving the instance.

    # what it would send, no network, no --write-ack needed
    python3 tools/web/race_probe.py --url http://t/api/coupon/redeem --method POST \\
        --body '{"code":"MINE"}' --header 'Content-Type: application/json' --dry-run

    # N copies of one request, after a serial baseline (the SSOS shape)
    python3 tools/web/race_probe.py --url http://t/api/register --method POST \\
        --body 'user=bot&pass=mine' --count 20 --concurrency 8 --write-ack

    # two interleaved requests (the ApexSurvive shape): check-then-act
    python3 tools/web/race_probe.py --url http://t/profile --method POST \\
        --body 'email=a@x' --url-b http://t/profile --method-b POST \\
        --body-b 'email=b@y' --count 16 --write-ack
"""
import argparse
import concurrent.futures
import contextlib
import hashlib
import io
import json
import os
import re
import shlex
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import httpkit  # noqa: E402

# A shared challenge database is easy to kill with load, and a race needs a tight
# wave rather than a big one: measured against the loopback fixture at the bottom
# of this file, the spread between the first and last request leaving grows 6.0ms
# -> 10.6 -> 24.1 -> 80.4 as concurrency goes 4 -> 8 -> 16 -> 32, so past this cap
# the client's own scheduling is what widens the window it is trying to hit.
MAX_CONCURRENCY = 32
MAX_COUNT = 500
SIG_MODES = ("normalized-body", "raw-body", "status", "status-length", "regex")
HOOKS = os.path.join(os.path.dirname(HERE), "hooks.py")

# Volatile fields are the reason hand-written race code reports phantom findings:
# a fresh receipt id or a millisecond timestamp differs on every response. The
# uuid and timestamp shapes are matched before the generic run.
#
# One rule and ONE placeholder for the generic run, because the placeholder has to
# depend on the token's shape and not on which characters it was drawn as.
# Measured with the previous pair of rules (\d{6,} -> <num> before
# [0-9a-fA-F]{8,} -> <hex>): the same receipt field read
# {"receipt": "<hex>"} for a1b2c3d4e5f60718 and {"receipt": "<num>"} for
# 0123456789012345, two different signatures, so the field this rule exists to
# absorb became the divergence — 1 run in 40 against the /volatile fixture, which
# holds no shared state and cannot race, came back verdict_hint race-candidate.
# An all-digit draw is 1 in 4300 at 16 characters and 1 in 43 at 8.
# The threshold is 6, the lower of the two it replaces, so nothing that used to be
# absorbed now leaks; the cost is that a 6-character hex-shaped word ("decade")
# is absorbed too, which --signature-mode raw-body exists to show.
VOLATILE = (
    (re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
                r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"), "<uuid>"),
    (re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:[.,]\d+)?Z?"), "<ts>"),
    (re.compile(r"\b[0-9a-fA-F]{6,}\b"), "<hex>"),
    (re.compile(r"[ \t\r\n]+"), " "),
)

HIST_EDGES = (10, 25, 50, 100, 250, 500, 1000, 2500)


def normalize(text):
    """Collapse the fields that differ on every response, whatever happened."""
    out = text
    for rx, placeholder in VOLATILE:
        out = rx.sub(placeholder, out)
    return out.strip()


def signature(resp, mode, regex, limit, header_names):
    """-> (sig_id, label). sig_id is what the two phases are compared on."""
    status = resp.get("status")
    body = resp.get("body", "") or ""
    if not resp.get("ok"):
        # A dead connection is a distinct outcome and must not be blended into a
        # body signature; it is never, on its own, a race.
        material = "transport:%s" % resp.get("error", "unknown")
        label = material[:160]
    elif mode == "status":
        material, label = "s=%s" % status, "HTTP %s" % status
    elif mode == "status-length":
        material = "s=%s|len=%d" % (status, resp.get("length", 0))
        label = "HTTP %s, %d bytes" % (status, resp.get("length", 0))
    elif mode == "regex":
        match = re.search(regex, body, re.S) if regex else None
        captured = ("|".join(g or "" for g in match.groups()) or match.group(0)) \
            if match else "<no-match>"
        material = "s=%s|rx=%s" % (status, captured)
        label = "HTTP %s, %s" % (status, captured[:120])
    else:
        core = body if mode == "raw-body" else normalize(body)
        truncated = core[:limit]
        material = "s=%s|b=%s" % (status, truncated)
        label = "HTTP %s, %s" % (status, truncated[:160])
    for name in header_names or []:
        # httpkit's `headers` dict keeps only the LAST value of a repeated header,
        # and the cookie-swap shape this tool exists for diverges in the FIRST
        # Set-Cookie: folding the collapsed dict into the signature hides that
        # divergence and reports a false negative. `headers_all` preserves order
        # and duplicates, so every value the header carried is folded in.
        pairs = resp.get("headers_all")
        if pairs:
            values = [raw for key, raw in pairs if key.lower() == name.lower()]
        else:
            values = [raw for key, raw in (resp.get("headers") or {}).items()
                      if key.lower() == name.lower()]
        folded = " | ".join(normalize(v) for v in values)
        material += "|%s=%s" % (name.lower(), folded)
        label += " [%s: %s]" % (name, folded[:80])
    return hashlib.sha1(material.encode("utf-8", "replace")).hexdigest()[:12], label


def build_specs(args):
    """The request list for one phase, alternating a/b when --url-b is given."""
    a = {"variant": "a", "method": args.method.upper(), "url": args.url,
         "body": args.body}
    if not args.url_b and not args.body_b and not args.method_b:
        return [a]
    b = {"variant": "b",
         "method": (args.method_b or args.method).upper(),
         "url": args.url_b or args.url,
         "body": args.body_b if args.body_b is not None else args.body}
    return [a, b]


def materialise(spec, index, run_token):
    """{i} and {run} are substituted per attempt, for a burst that needs a
    distinct value per request (a unique username, an idempotency key)."""
    url = httpkit.fill(spec["url"], i=index, run=run_token)
    body = None if spec["body"] is None else httpkit.fill(spec["body"], i=index,
                                                          run=run_token)
    return {"variant": spec["variant"], "method": spec["method"], "url": url,
            "body": body}


def request_line(spec):
    line = "%s %s" % (spec["method"], spec["url"])
    if spec.get("body"):
        line += " -d %s" % shlex.quote(spec["body"][:120])
    return line


def send_one(spec, headers, args, barrier, stats):
    """One request, with its own in-flight interval recorded by the client."""
    if barrier is not None:
        try:
            barrier.wait(timeout=args.barrier_timeout)
        except threading.BrokenBarrierError:
            # The final partial wave, or a straggler thread: the request still
            # goes out, just less synchronised. Counted, not hidden.
            with stats["lock"]:
                stats["barrier_timeouts"] += 1
    t0 = time.monotonic()
    resp = httpkit.request(spec["url"], spec["method"], headers, spec["body"],
                           timeout=args.timeout, follow=args.follow)
    t1 = time.monotonic()
    # --count can be 500 and httpkit reads up to 1 MiB per response; only the
    # prefix the signature and the excerpt will read is worth keeping.
    keep = max(args.signature_bytes, args.excerpt)
    resp["body"] = resp.get("body", "")[:keep]
    resp.pop("body_bytes", None)
    return {"variant": spec["variant"], "request": request_line(spec),
            "ok": resp["ok"], "status": resp.get("status"),
            "length": resp.get("length", 0),
            "elapsed_ms": round((t1 - t0) * 1000, 1),
            "error": resp.get("error"), "t0": t0, "t1": t1, "_resp": resp}


def serial_phase(specs, headers, args, count, stats):
    """Strictly one at a time: this is what the endpoint can do without a race."""
    out = []
    for index in range(count):
        spec = materialise(specs[index % len(specs)], index, args.run_token)
        out.append(send_one(spec, headers, args, None, stats))
        if args.delay:
            time.sleep(args.delay)
    return out


def concurrent_phase(specs, headers, args, stats):
    parties = min(args.concurrency, args.count)
    barrier = None if args.no_barrier or parties < 2 else threading.Barrier(parties)
    jobs = [materialise(specs[i % len(specs)], i, args.run_token)
            for i in range(args.count)]
    out = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = [pool.submit(send_one, spec, headers, args, barrier, stats)
                   for spec in jobs]
        for future in futures:
            out.append(future.result())
    return out


def overlap_stats(records):
    """Did the requests actually overlap? max_in_flight is the whole question."""
    if not records:
        return {"requests": 0, "max_in_flight": 0, "overlapped_ms": 0.0,
                "start_spread_ms": 0.0, "wall_ms": 0.0}
    events = []
    for rec in records:
        events.append((rec["t0"], 1))
        events.append((rec["t1"], -1))
    # Starts before ends at an identical timestamp: that is the reading most
    # favourable to "they overlapped", so a low max_in_flight is not an artefact
    # of tie-breaking.
    events.sort(key=lambda e: (e[0], -e[1]))
    current = best = 0
    overlapped = 0.0
    previous = None
    for when, delta in events:
        if previous is not None and current >= 2:
            overlapped += when - previous
        current += delta
        best = max(best, current)
        previous = when
    starts = [r["t0"] for r in records]
    return {"requests": len(records), "max_in_flight": best,
            "overlapped_ms": round(overlapped * 1000, 1),
            "start_spread_ms": round((max(starts) - min(starts)) * 1000, 1),
            "wall_ms": round((max(r["t1"] for r in records) - min(starts)) * 1000, 1)}


def histogram(records):
    labels = ["<%dms" % HIST_EDGES[0]]
    labels += ["%d-%dms" % (HIST_EDGES[i], HIST_EDGES[i + 1])
               for i in range(len(HIST_EDGES) - 1)]
    labels.append(">=%dms" % HIST_EDGES[-1])
    counts = dict.fromkeys(labels, 0)
    for rec in records:
        value = rec["elapsed_ms"]
        placed = False
        for index, edge in enumerate(HIST_EDGES):
            if value < edge:
                counts[labels[index]] += 1
                placed = True
                break
        if not placed:
            counts[labels[-1]] += 1
    return {k: v for k, v in counts.items() if v}


def index_signatures(records, args):
    """-> {(variant, sig_id): {label, count, statuses, excerpt}}"""
    table = {}
    for rec in records:
        sig_id, label = signature(rec["_resp"], args.signature_mode,
                                  args.signature_regex, args.signature_bytes,
                                  args.signature_header)
        rec["signature"] = sig_id
        key = (rec["variant"], sig_id)
        entry = table.setdefault(key, {
            "variant": rec["variant"], "signature": sig_id, "label": label,
            "count": 0, "statuses": [],
            # verbatim, un-normalised: hooks.py post-probe only accepts an
            # excerpt that really appears in the response
            "excerpt": (rec["_resp"].get("body", "") or "")[:args.excerpt],
            "example_request": rec["request"],
            # a response the client could not finish reading is evidence about
            # load, not about a window; run() keeps it out of the finding
            "transport_failure": not rec["ok"],
            "error": rec.get("error")})
        entry["count"] += 1
        if rec["status"] not in entry["statuses"]:
            entry["statuses"].append(rec["status"])
    return table


def dry_run_report(specs, args, headers):
    plan = []
    for index in range(args.count):
        spec = materialise(specs[index % len(specs)], index, args.run_token)
        plan.append({"n": index + 1, "variant": spec["variant"],
                     "method": spec["method"], "url": spec["url"],
                     "body": spec["body"]})
    # the baseline is its own sequence: it can be longer or shorter than the burst
    baseline_requested = 0 if args.no_baseline else max(0, args.baseline_count)
    baseline = [
        dict(materialise(specs[i % len(specs)], i, args.run_token),
             n=i + 1, phase="serial-baseline")
        for i in range(baseline_requested)]
    # one reset per phase that will really run: with no serial baseline there is
    # only the burst, so the plan has to drop that reset too, or the planned total
    # is one request larger than the run's own sent_requests
    phases = 1 + (1 if baseline_requested else 0)
    resets = args.reset_url and [
        {"method": args.reset_method.upper(), "url": args.reset_url,
         "body": args.reset_body,
         "when": "once before each of the %d phase(s) that will run" % phases}]
    return {
        "mode": "race-probe-dry-run", "sent_requests": 0,
        "would_send": {
            "serial_baseline": {"count": len(baseline), "concurrency": 1,
                                "requests": baseline[:20]},
            "concurrent_burst": {"count": args.count,
                                 "concurrency": args.concurrency,
                                 "barrier_parties": 1 if args.no_barrier
                                 else min(args.concurrency, args.count),
                                 "requests": plan[:20]},
            "reset": resets or None,
            "total_requests": len(baseline) + args.count
            + (phases if resets else 0),
            "requests_listed": "at most the first 20 of each phase",
            "plan_truncated": args.count > 20 or len(baseline) > 20,
        },
        "variants": [s["variant"] for s in specs],
        "headers": headers,
        "follow_redirects": args.follow,
        "signature_mode": args.signature_mode,
        "write_ack": bool(args.write_ack),
        "note": "nothing was sent; --dry-run needs no network and no --write-ack",
    }


REFUSAL = {
    "mode": "race-probe", "ok": False, "refused": True, "sent_requests": 0,
    "reason": "a race probe is write-shaped by definition and --write-ack was "
              "not passed, so nothing was sent",
    "required_before_running": [
        "read the matching chain card's blast_radius in knowledge/chains/ — the "
        "two verified web-race-condition cards here warn that an SSOS-shaped "
        "instance is permanently consumed once its startup has run, and that "
        "overwriting configuration or an imported module bricks an instance",
        "run tools/hooks.py pre-probe <challenge> --write-ack so the burst is "
        "recorded against the probe budget before it is fired",
        "plan the cleanup: every object the burst creates has to be deleted "
        "afterwards, and a burst creates --count of them, not one",
        "use --dry-run first; it needs no network and no --write-ack",
    ],
}


def run(args, headers, specs):
    stats = {"lock": threading.Lock(), "barrier_timeouts": 0, "resets": []}

    def reset(phase):
        if not args.reset_url:
            return
        resp = httpkit.request(args.reset_url, args.reset_method,
                               headers, args.reset_body, timeout=args.timeout,
                               follow=args.follow)
        stats["resets"].append({"phase": phase, "ok": resp["ok"],
                                "status": resp.get("status"),
                                "error": resp.get("error")})

    # --baseline-count 0 is --no-baseline spelled differently: skipping the phase
    # skips its reset too, so sent_requests matches what --dry-run planned.
    baseline_requested = 0 if args.no_baseline else max(0, args.baseline_count)
    serial = []
    if baseline_requested:
        reset("before-serial-baseline")
        serial = serial_phase(specs, headers, args, baseline_requested, stats)
    reset("before-concurrent-burst")
    burst = concurrent_phase(specs, headers, args, stats)

    serial_table = index_signatures(serial, args)
    burst_table = index_signatures(burst, args)
    new_keys = [k for k in burst_table if k not in serial_table]
    # The dangerous false positive: the baseline answered, the burst knocked the
    # service over, and the resulting connection error is a signature serial
    # execution never produced. That is a load result, so it is counted and
    # cautioned about but never offered as the finding.
    collapsed = [k for k in new_keys if burst_table[k]["transport_failure"]]
    new_signatures = [burst_table[k] for k in sorted(new_keys)
                      if k not in collapsed]

    overlap = overlap_stats(burst)
    # Keyed on the MEASUREMENT, never on the flag: --no-baseline and
    # --baseline-count 0 both leave the serial signature set empty, and against an
    # empty set every burst signature is trivially new. Measured while this keyed
    # on args.no_baseline: --baseline-count 0 against the /volatile fixture, which
    # holds no shared state and cannot race, returned verdict_hint race-candidate
    # and a confirms-shaped record_as.
    no_baseline_data = len(serial) == 0
    baseline_cause = ("--no-baseline" if args.no_baseline
                      else "--baseline-count 0" if no_baseline_data else None)
    cautions = []
    if no_baseline_data:
        cautions.append("%s: there is no serial signature set to "
                        "compare against, so new_signatures_under_concurrency is "
                        "null and this run cannot distinguish a race from the "
                        "endpoint's ordinary behaviour" % baseline_cause)
    if not args.reset_url and not no_baseline_data:
        cautions.append("no --reset-url: the serial baseline ran first and may "
                        "have consumed the very state the burst targets (a "
                        "one-shot coupon, the last unit of stock), which "
                        "suppresses the finding — a false negative, not a clean "
                        "result")
    if stats["barrier_timeouts"]:
        cautions.append("%d request(s) timed out on the release barrier and were "
                        "sent unsynchronised" % stats["barrier_timeouts"])
    if collapsed:
        cautions.append("%d signature(s) unique to the burst were transport "
                        "failures and are excluded from the finding: the "
                        "baseline answered and the burst did not, which measures "
                        "what the service does under load"
                        % len(collapsed))
    transport_failures = [r for r in burst if not r["ok"]]
    if transport_failures:
        cautions.append("%d of %d concurrent requests failed at the transport "
                        "layer; a reset or a refused connection is evidence about "
                        "load, never about a race"
                        % (len(transport_failures), len(burst)))

    overlapped = overlap["max_in_flight"] >= 2
    if no_baseline_data:
        hint = "inconclusive"
        why = ("no serial baseline was taken (%s), so no signature can be called "
               "new: these %d concurrent responses measured nothing about a "
               "window" % (baseline_cause, len(burst)))
    elif not new_signatures:
        hint = "inconclusive"
        why = ("0 of %d concurrent responses produced a signature the %d-request "
               "serial baseline had not already produced (max_in_flight=%d, so "
               "the requests did overlap)" % (len(burst), len(serial),
                                              overlap["max_in_flight"])
               if overlapped else
               "0 of %d concurrent responses produced a new signature, and "
               "max_in_flight=%d means they never overlapped either — this run "
               "tested nothing" % (len(burst), overlap["max_in_flight"]))
    elif not overlapped:
        hint = "inconclusive"
        why = ("%d new signature(s) appeared, but max_in_flight=%d: the requests "
               "never overlapped, so this is ordinary state drift between the two "
               "phases, not a window" % (len(new_signatures),
                                         overlap["max_in_flight"]))
    else:
        hint = "race-candidate"
        why = ("%d signature(s) appeared under concurrency that %d serial "
               "requests never produced, with up to %d requests in flight at once"
               % (len(new_signatures), len(serial), overlap["max_in_flight"]))

    report = {
        "mode": "race-probe", "ok": True,
        "target": {"variants": specs, "concurrency": args.concurrency,
                   "count": args.count, "baseline_count": len(serial),
                   "signature_mode": args.signature_mode,
                   "follow_redirects": args.follow,
                   "barrier": not args.no_barrier,
                   "barrier_timeouts": stats["barrier_timeouts"]},
        "resets": stats["resets"] or None,
        "sent_requests": len(serial) + len(burst) + len(stats["resets"]),
        "serial": {
            "responses": [_public(r) for r in serial],
            "distinct_signatures": _sig_list(serial_table),
            "timing_histogram": histogram(serial),
        },
        "concurrent": {
            "responses": [_public(r) for r in burst],
            "distinct_signatures": _sig_list(burst_table),
            "timing_histogram": histogram(burst),
            "overlap": overlap,
        },
        "new_signatures_under_concurrency": None if no_baseline_data
        else new_signatures,
        "counts": {
            "serial_requests": len(serial),
            "concurrent_requests": len(burst),
            "serial_distinct_signatures": len(serial_table),
            "concurrent_distinct_signatures": len(burst_table),
            "new_under_concurrency": None if no_baseline_data
            else len(new_signatures),
            "transport_failures": len(transport_failures),
            "new_but_transport_failures_excluded": len(collapsed),
        },
        "verdict_hint": hint,
        "verdict_hint_reason": why,
        "cautions": cautions,
        "cleanup_required": ("this run sent %d write-shaped requests; delete "
                             "every object they created before leaving the "
                             "instance" % (len(serial) + len(burst)
                                           + len(stats["resets"]))),
        "record_as": _record_as(hint, new_signatures, len(burst), len(serial),
                                overlap),
    }
    if args.challenge:
        report["post_probe_command"] = _post_probe_command(args, hint,
                                                           new_signatures, burst,
                                                           serial, overlap)
    return report


def _public(rec):
    return {k: rec[k] for k in ("variant", "status", "length", "elapsed_ms",
                                "signature", "ok", "error") if k in rec}


def _sig_list(table):
    return [dict(v) for _, v in sorted(table.items())]


def _result_line(burst, serial, overlap):
    return ("%d concurrent / %d serial requests, max_in_flight=%d, "
            "start spread %.1fms" % (len(burst), len(serial),
                                     overlap["max_in_flight"],
                                     overlap["start_spread_ms"]))


def _record_as(hint, new_signatures, burst_n, serial_n, overlap):
    if serial_n == 0:
        # nothing was measured to be new AGAINST: this is not a negative result
        # with a count, it is an absent comparison, and it must not be offered as
        # "0 of N produced a signature the baseline had not already produced"
        return ("verdict=inconclusive: no serial baseline was taken, so none of "
                "the %d concurrent responses can be called new and this run "
                "measured nothing. Re-run with --baseline-count >= 1 before "
                "recording anything about a window." % burst_n)
    if hint == "race-candidate":
        return ("verdict=confirms candidate for web-race-condition: %d signature(s) "
                "in %d concurrent responses were absent from the %d-request serial "
                "baseline, max_in_flight=%d. Quote one new signature's verbatim "
                "excerpt as --evidence, and use --evidence-kind impact only if "
                "that body shows the limit actually broken."
                % (len(new_signatures), burst_n, serial_n,
                   overlap["max_in_flight"]))
    return ("verdict=inconclusive: 0 of %d concurrent responses produced a "
            "signature the %d-request serial baseline had not already produced "
            "(max_in_flight=%d). Record the count and change mechanism layer "
            "rather than firing a wider burst." % (burst_n, serial_n,
                                                   overlap["max_in_flight"]))


def _post_probe_command(args, hint, new_signatures, burst, serial, overlap):
    # a confirm needs a serial baseline to be new against, and an excerpt to
    # quote; without either, the rendered command stays inconclusive
    verdict = ("confirms" if hint == "race-candidate" and serial and new_signatures
               else "inconclusive")
    argv = ["python3", HOOKS, "post-probe", args.challenge,
            "--request", "race: %d concurrent x %s" % (args.count,
                                                       request_line(
                                                           build_specs(args)[0])),
            "--verdict", verdict,
            "--result", _result_line(burst, serial, overlap)]
    if verdict == "confirms":
        argv += ["--evidence", new_signatures[0]["excerpt"],
                 "--evidence-kind", "class"]
    if args.probe_class:
        argv += ["--class", args.probe_class]
    if args.hypothesis_id:
        argv += ["--hypothesis-id", args.hypothesis_id]
    return " ".join(shlex.quote(part) for part in argv)


# Offline fixtures: /buy has a real TOCTOU window, /buy-locked does not,
# /collapse imitates the server dying under the burst, /drift/<tag> diverges on a
# deterministic hit count with no concurrency involved at all, and /cookie/<tag>
# puts that divergence in the FIRST of two Set-Cookie headers.
class _Shop:
    def __init__(self, window):
        self.window = window
        self.lock = threading.Lock()
        self.counter = threading.Lock()
        self.stock = 1
        self.orders = []
        self.hits = 0
        self.inflight = 0
        # every response body this fixture really put on the wire, verbatim: the
        # only way a check can prove an excerpt was copied and not summarised
        self.served = []
        # per-tag hit counters for /drift and /cookie. Deliberately NOT cleared by
        # reset(): a check needs the phase boundary to fall between the serial
        # baseline and the burst.
        self.drift = {}

    def reset(self):
        self.stock = 1
        self.orders = []


def _mock_server(window=0.2):
    """A loopback target: /buy is non-atomic, /buy-locked is not, /volatile has
    no shared state at all and only ever answers with fresh random fields."""
    import socket
    import urllib.parse
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    shop = _Shop(window)

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *args):
            pass

        def _json(self, code, payload, extra_headers=()):
            body = json.dumps(payload).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            for header_name, header_value in extra_headers:
                self.send_header(header_name, header_value)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            with shop.counter:
                shop.served.append(body.decode())

        def _noise(self):
            # every response carries a fresh receipt and an epoch in ms: exactly
            # the fields that make a hand-written race tool cry wolf
            return {"receipt": os.urandom(8).hex(),
                    "at": int(time.time() * 1000)}

        def _drain(self):
            length = int(self.headers.get("Content-Length") or 0)
            if length:
                self.rfile.read(length)

        def _phase(self, path, params):
            """phase-one for the first `after` hits on this exact path, phase-two
            after that. A function of the hit count alone: nothing here races, so a
            divergence between the two phases is state drift and not a window."""
            after = int((params.get("after") or ["3"])[0])
            with shop.counter:
                shop.drift[path] = shop.drift.get(path, 0) + 1
                seen = shop.drift[path]
            return "phase-one" if seen <= after else "phase-two"

        def _route(self):
            self._drain()
            path, _, query = self.path.partition("?")
            params = urllib.parse.parse_qs(query)
            if path == "/stats":
                return self._json(200, {"hits": shop.hits, "stock": shop.stock,
                                        "orders": len(shop.orders)})
            shop.hits += 1
            if path == "/reset":
                shop.reset()
                return self._json(200, dict(self._noise(), result="reset"))
            if path == "/volatile":
                return self._json(200, dict(self._noise(), result="pong"))
            if path == "/collapse":
                return self._collapse()
            if path.startswith("/drift/"):
                return self._json(200, dict(self._noise(),
                                            result=self._phase(path, params)))
            if path.startswith("/cookie/"):
                # the body is identical in both phases; the divergence is in the
                # FIRST Set-Cookie, and the last one is the same either way, so a
                # signature built from a collapsed header dict cannot see it
                return self._json(200, dict(self._noise(), result="pong"),
                                  extra_headers=(
                                      ("Set-Cookie", "sid=%s"
                                       % self._phase(path, params)),
                                      ("Set-Cookie", "flavour=vanilla")))
            if path in ("/buy", "/buy-locked"):
                if path == "/buy-locked":
                    with shop.lock:
                        return self._json(200, self._buy())
                return self._json(200, self._buy())
            return self._json(404, {"result": "no route"})

        def _collapse(self):
            """Answers cleanly one at a time; while requests overlap it half-closes
            the socket without a status line, which is what a service falling over
            under the burst looks like to the client — not a race window."""
            with shop.counter:
                shop.inflight += 1
                overlapped = shop.inflight > 1
            try:
                time.sleep(shop.window)
                if not overlapped:
                    return self._json(200, dict(self._noise(), result="pong"))
                self.close_connection = True
                self.connection.shutdown(socket.SHUT_WR)
            finally:
                with shop.counter:
                    shop.inflight -= 1

        def _buy(self):
            seen = shop.stock                    # read
            time.sleep(shop.window)              # the check-then-act window
            if seen <= 0:
                return dict(self._noise(), result="out-of-stock",
                            stock=shop.stock)
            shop.stock = seen - 1                # write, against a stale read
            shop.orders.append(1)
            return dict(self._noise(), result="ordered",
                        order_no=len(shop.orders), stock=shop.stock)

        do_GET = do_POST = _route

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, "http://127.0.0.1:%d" % server.server_address[1], shop


def _cli(argv):
    """Run main() in-process and return (exit code, parsed JSON, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(argv)
    except SystemExit as exc:                    # argparse.error()
        code = exc.code if isinstance(exc.code, int) else 2
    try:
        payload = json.loads(out.getvalue())
    except ValueError:
        payload = {"_unparsed_stdout": out.getvalue()[:400]}
    return code, payload, err.getvalue()


def _hits(base):
    resp = httpkit.request(base + "/stats")
    return json.loads(resp["body"])["hits"] if resp["ok"] else None


def selftest(window=0.2):
    checks = []
    server, base, shop = _mock_server(window)
    try:
        common = ["--method", "POST", "--count", "6", "--concurrency", "6",
                  "--baseline-count", "3", "--timeout", "10",
                  "--reset-url", base + "/reset"]

        # (a) --dry-run must not touch the network and must not need --write-ack
        before = _hits(base)
        code, dry, _ = _cli(["--url", base + "/buy"] + common + ["--dry-run"])
        after = _hits(base)
        checks.append({
            "name": "--dry-run sends nothing and needs no --write-ack",
            "expect": "exit 0, sent_requests 0, server hit count unchanged",
            "got": {"exit": code, "sent": dry.get("sent_requests"),
                    "hits_before": before, "hits_after": after,
                    "planned_total": dry.get("would_send", {}).get("total_requests")},
            "pass": code == 0 and dry.get("sent_requests") == 0
            and before == after and before is not None
            and dry.get("would_send", {}).get("total_requests") == 11})

        # (b) a live run without --write-ack is refused before anything is sent
        before = _hits(base)
        code, refused, _ = _cli(["--url", base + "/buy"] + common)
        after = _hits(base)
        checks.append({
            "name": "live run without --write-ack is refused, nothing sent",
            "expect": "exit 2, refused true, hit count unchanged",
            "got": {"exit": code, "refused": refused.get("refused"),
                    "sent": refused.get("sent_requests"),
                    "hits_before": before, "hits_after": after,
                    "reasons": len(refused.get("required_before_running", []))},
            "pass": code == 2 and refused.get("refused") is True
            and refused.get("sent_requests") == 0 and before == after
            and len(refused.get("required_before_running", [])) >= 3})

        # (c) the non-atomic handler: concurrency must produce an outcome the
        # serial baseline cannot reach (an order number past the single unit of
        # stock), and the burst must be shown to have overlapped
        code, racy, _ = _cli(["--url", base + "/buy"] + common
                             + ["--write-ack", "--challenge", "selftest",
                                "--class", "web-race-condition",
                                "--hypothesis-id", "h1"])
        new = racy.get("new_signatures_under_concurrency") or []
        overlap = racy.get("concurrent", {}).get("overlap", {})
        # only the first request after a reset can legitimately be order 1, so
        # every NEW signature must show an order past the single unit of stock:
        # the excerpt has to carry the broken limit, not just a differing body
        oversold = [n for n in new
                    if re.search(r'"order_no": ([2-9]|\d\d+)', n["excerpt"])]
        checks.append({
            "name": "non-atomic read-modify-write: a signature only concurrency produces",
            "expect": "new_signatures_under_concurrency non-empty, every new "
                      "excerpt shows order_no > 1, verdict_hint race-candidate, "
                      "max_in_flight >= 2",
            "got": {"exit": code, "new": len(new), "oversold_excerpts": len(oversold),
                    "hint": racy.get("verdict_hint"),
                    "max_in_flight": overlap.get("max_in_flight"),
                    "serial_signatures": racy.get("counts", {})
                    .get("serial_distinct_signatures"),
                    "concurrent_signatures": racy.get("counts", {})
                    .get("concurrent_distinct_signatures"),
                    "example": (new[0]["excerpt"][:120] if new else None)},
            "pass": code == 1 and len(new) >= 1 and len(oversold) == len(new)
            and racy.get("verdict_hint") == "race-candidate"
            and (overlap.get("max_in_flight") or 0) >= 2})

        # the rendered gate command must quote an excerpt that really came back;
        # hooks.py post-probe refuses a --evidence that is not verbatim
        command = racy.get("post_probe_command", "")
        quoted = "--verdict confirms" in command and new and \
            shlex.quote(new[0]["excerpt"]) in command
        # the fixture records every body it really put on the wire: an excerpt that
        # is not a prefix of one of them was summarised or normalised. hooks.py
        # post-probe only rejects an empty or timeout-shaped --evidence, so nothing
        # downstream would catch it — a prefix assertion would survive normalise().
        excerpt = new[0]["excerpt"] if new else ""
        verbatim = bool(excerpt) and any(body.startswith(excerpt)
                                        for body in list(shop.served))
        # and the volatile fields must still be the real ones: normalize() turns the
        # receipt into <hex> and the epoch into <num>
        unnormalised = bool(re.search(r'"receipt": "[0-9a-f]{16}", "at": \d{13}',
                                      excerpt))
        checks.append({
            "name": "post-probe command quotes a verbatim excerpt",
            "expect": "confirms, --evidence-kind class, and the excerpt is a "
                      "prefix of a body the fixture really sent, volatile fields "
                      "and all — not a normalised or summarised copy",
            "got": {"has_verbatim_evidence": bool(quoted),
                    "prefix_of_a_served_body": verbatim,
                    "volatile_fields_unnormalised": unnormalised,
                    "bodies_served_by_fixture": len(shop.served),
                    "excerpt": excerpt[:120], "command_head": command[:150]},
            "pass": bool(quoted) and verbatim and unnormalised
            and "--evidence-kind class" in command
            and "--class web-race-condition" in command})

        # (d) the one that matters: the same shape behind a lock must come back
        # empty, with the overlap still measured, so the empty result is a
        # statement about the server and not about a burst that never happened
        code, safe, _ = _cli(["--url", base + "/buy-locked"] + common
                             + ["--write-ack"])
        safe_new = safe.get("new_signatures_under_concurrency")
        safe_overlap = safe.get("concurrent", {}).get("overlap", {})
        checks.append({
            "name": "atomic handler under a lock: no race claimed",
            "expect": "new_signatures_under_concurrency empty, verdict_hint "
                      "inconclusive, max_in_flight still >= 2",
            "got": {"exit": code, "new": safe_new,
                    "hint": safe.get("verdict_hint"),
                    "max_in_flight": safe_overlap.get("max_in_flight"),
                    "record_as": safe.get("record_as", "")[:100]},
            "pass": code == 0 and safe_new == []
            and safe.get("verdict_hint") == "inconclusive"
            and (safe_overlap.get("max_in_flight") or 0) >= 2})

        # (e) volatile fields must not fake a divergence - and raw-body mode must
        # show what the normaliser was absorbing, or the normaliser is untested
        code, norm, _ = _cli(["--url", base + "/volatile"] + common
                             + ["--write-ack"])
        code_raw, raw, _ = _cli(["--url", base + "/volatile"] + common
                                + ["--write-ack", "--signature-mode", "raw-body"])
        checks.append({
            "name": "a fresh receipt and timestamp do not fake a race",
            "expect": "normalized-body: 1 signature, 0 new; raw-body: new ones",
            "got": {"normalized_new": norm.get("new_signatures_under_concurrency"),
                    "normalized_distinct": norm.get("counts", {})
                    .get("concurrent_distinct_signatures"),
                    "raw_new": len(raw.get("new_signatures_under_concurrency") or []),
                    "hint": norm.get("verdict_hint")},
            "pass": code == 0
            and norm.get("new_signatures_under_concurrency") == []
            and norm.get("counts", {}).get("concurrent_distinct_signatures") == 1
            and len(raw.get("new_signatures_under_concurrency") or []) >= 1
            and code_raw == 1})

        # (f) a service that falls over under the burst produces a signature the
        # baseline never did - and that must NOT be offered as the finding
        code, dead, _ = _cli(["--url", base + "/collapse"] + common
                             + ["--write-ack"])
        checks.append({
            "name": "a service collapsing under load is not reported as a race",
            "expect": "new_signatures empty, inconclusive, the excluded "
                      "transport signatures counted and cautioned",
            "got": {"exit": code,
                    "new": dead.get("new_signatures_under_concurrency"),
                    "hint": dead.get("verdict_hint"),
                    "excluded": dead.get("counts", {})
                    .get("new_but_transport_failures_excluded"),
                    "transport_failures": dead.get("counts", {})
                    .get("transport_failures")},
            "pass": code == 0
            and dead.get("new_signatures_under_concurrency") == []
            and dead.get("verdict_hint") == "inconclusive"
            and (dead.get("counts", {})
                 .get("new_but_transport_failures_excluded") or 0) >= 1
            and any("under load" in c for c in (dead.get("cautions") or []))})

        # (g) A/B mode plans an alternating sequence, and a b-variant response is
        # accounted separately so b's normal answer is never new for a
        code, ab, _ = _cli(["--url", base + "/buy", "--url-b", base + "/volatile",
                            "--method-b", "POST"] + common + ["--dry-run"])
        plan = ab.get("would_send", {}).get("concurrent_burst", {}).get("requests", [])
        variants = [p["variant"] for p in plan]
        checks.append({
            "name": "A/B mode alternates the two requests",
            "expect": "['a','b','a','b','a','b']",
            "got": variants,
            "pass": code == 0 and variants == ["a", "b"] * 3})

        # (h) the concurrency cap is enforced, with the reason on stderr
        code, _, err = _cli(["--url", base + "/buy", "--write-ack",
                             "--concurrency", "999"])
        checks.append({
            "name": "--concurrency is capped",
            "expect": "exit 2 and the cap named in the error",
            "got": {"exit": code, "stderr_tail": err.strip()[-120:]},
            "pass": code == 2 and str(MAX_CONCURRENCY) in err})

        # (i) --no-baseline cannot report new signatures at all
        code, nb, _ = _cli(["--url", base + "/buy"] + common
                           + ["--write-ack", "--no-baseline"])
        checks.append({
            "name": "--no-baseline reports null, not a finding",
            "expect": "new_signatures_under_concurrency null, inconclusive, caution",
            "got": {"exit": code,
                    "new": nb.get("new_signatures_under_concurrency"),
                    "hint": nb.get("verdict_hint"),
                    "cautions": len(nb.get("cautions") or [])},
            "pass": code == 0
            and nb.get("new_signatures_under_concurrency") is None
            and nb.get("verdict_hint") == "inconclusive"
            and any("--no-baseline" in c for c in (nb.get("cautions") or []))
            and "confirms" not in nb.get("record_as", "")})

        # (j) an EMPTY baseline is the same thing by another name: against an empty
        # serial signature set every burst signature is trivially new. /volatile
        # holds no shared state and cannot race, /buy-locked is atomic, so anything
        # but inconclusive here is a false confirmation put in front of a solver.
        zero = {}
        for route in ("/volatile", "/buy-locked"):
            code, out, _ = _cli(["--url", base + route, "--method", "POST",
                                 "--count", "6", "--concurrency", "6",
                                 "--baseline-count", "0", "--timeout", "10",
                                 "--reset-url", base + "/reset", "--write-ack",
                                 "--challenge", "selftest",
                                 "--class", "web-race-condition"])
            zero[route] = {
                "exit": code, "new": out.get("new_signatures_under_concurrency"),
                "new_count": out.get("counts", {}).get("new_under_concurrency"),
                "hint": out.get("verdict_hint"),
                "cause_named": any("--baseline-count 0" in c
                                   for c in (out.get("cautions") or [])),
                "stale_baseline_caution": any("baseline ran first" in c
                                              for c in (out.get("cautions") or [])),
                "record_as_confirms": "confirms" in out.get("record_as", ""),
                "post_probe_confirms": "--verdict confirms" in
                                       (out.get("post_probe_command") or ""),
                "sent_requests": out.get("sent_requests"),
                "resets": len(out.get("resets") or [])}
        checks.append({
            "name": "--baseline-count 0 cannot confirm: no baseline, no finding",
            "expect": "both routes exit 0, new null, inconclusive, the real cause "
                      "named in a caution, nothing confirms-shaped, and no reset "
                      "sent for a phase that sends nothing (7 = 6 burst + 1 reset)",
            "got": zero,
            "pass": all(v["exit"] == 0 and v["new"] is None
                        and v["new_count"] is None
                        and v["hint"] == "inconclusive" and v["cause_named"]
                        and not v["stale_baseline_caution"]
                        and not v["record_as_confirms"]
                        and not v["post_probe_confirms"]
                        and v["resets"] == 1 and v["sent_requests"] == 7
                        for v in zero.values())})

        # (k) max_in_flight is the number the whole verdict turns on, so measure the
        # measurement: strictly sequential intervals must read 1, never more, or an
        # inflated overlap number would make every burst look like a race.
        seq_stats = overlap_stats([{"t0": 0.0, "t1": 1.0}, {"t0": 1.5, "t1": 2.0},
                                   {"t0": 3.0, "t1": 3.5}])
        par_stats = overlap_stats([{"t0": 0.0, "t1": 1.0}, {"t0": 0.5, "t1": 1.5},
                                   {"t0": 0.9, "t1": 1.2}])
        empty_stats = overlap_stats([])
        checks.append({
            "name": "overlap_stats measures overlap instead of asserting it",
            "expect": "three sequential intervals -> max_in_flight 1, 0.0ms "
                      "overlapped; three staggered -> 3 and >0ms; none -> 0",
            "got": {"sequential": seq_stats, "staggered": par_stats,
                    "empty": empty_stats},
            "pass": seq_stats["max_in_flight"] == 1
            and seq_stats["overlapped_ms"] == 0.0
            and par_stats["max_in_flight"] == 3
            and par_stats["overlapped_ms"] > 0
            and empty_stats["max_in_flight"] == 0})

        # (l) the headline defence, in the direction that matters: new signatures
        # that did NOT overlap are drift, not a race. /drift diverges on its own hit
        # count, so at --concurrency 1 the burst produces a signature the baseline
        # never did while max_in_flight stays 1 — the one shape that must never be
        # called a candidate however different the bodies are.
        code, drift, _ = _cli(["--url", base + "/drift/gate?after=2",
                               "--method", "POST", "--count", "4",
                               "--concurrency", "1", "--baseline-count", "2",
                               "--timeout", "10", "--write-ack",
                               "--challenge", "selftest"])
        drift_new = drift.get("new_signatures_under_concurrency") or []
        drift_overlap = drift.get("concurrent", {}).get("overlap", {})
        checks.append({
            "name": "new signatures without overlap are drift, not a race",
            "expect": "new non-empty, max_in_flight 1, verdict_hint inconclusive, "
                      "the reason says they never overlapped, nothing confirms-shaped",
            "got": {"exit": code, "new": len(drift_new),
                    "max_in_flight": drift_overlap.get("max_in_flight"),
                    "hint": drift.get("verdict_hint"),
                    "reason": drift.get("verdict_hint_reason", "")[:130],
                    "record_as_confirms": "confirms" in drift.get("record_as", ""),
                    "post_probe_confirms": "--verdict confirms" in
                    (drift.get("post_probe_command") or "")},
            "pass": code == 0 and len(drift_new) >= 1
            and drift_overlap.get("max_in_flight") == 1
            and drift.get("verdict_hint") == "inconclusive"
            and "never overlapped" in drift.get("verdict_hint_reason", "")
            and "confirms" not in drift.get("record_as", "")
            and "--verdict confirms" not in (drift.get("post_probe_command") or "")})

        # (m) the release barrier: --count 6 at --concurrency 4 leaves a final wave
        # two threads short of the 4 parties, so it must break, be counted and be
        # cautioned about rather than reported as a tight wave it was not.
        # baseline 3, not 1: one transport hiccup in a single-request baseline
        # would invert the comparison and fail this check for a reason that has
        # nothing to do with the barrier
        barrier_argv = ["--method", "POST", "--count", "6", "--concurrency", "4",
                        "--baseline-count", "3", "--timeout", "10", "--write-ack"]
        code, held, _ = _cli(["--url", base + "/volatile"] + barrier_argv
                             + ["--barrier-timeout", "0.3"])
        code_nb, unheld, _ = _cli(["--url", base + "/volatile"] + barrier_argv
                                  + ["--no-barrier"])
        held_t, unheld_t = held.get("target", {}), unheld.get("target", {})
        checks.append({
            "name": "the release barrier is real: a short final wave is counted",
            "expect": "with the barrier: barrier true, barrier_timeouts >= 1 and a "
                      "caution naming it; with --no-barrier: barrier false, 0 "
                      "timeouts, no such caution",
            "got": {"exit": code, "barrier": held_t.get("barrier"),
                    "barrier_timeouts": held_t.get("barrier_timeouts"),
                    "caution": [c[:60] for c in (held.get("cautions") or [])
                                if "release barrier" in c],
                    "no_barrier_exit": code_nb,
                    "no_barrier": unheld_t.get("barrier"),
                    "no_barrier_timeouts": unheld_t.get("barrier_timeouts")},
            "pass": code == 0 and held_t.get("barrier") is True
            and (held_t.get("barrier_timeouts") or 0) >= 1
            and any("release barrier" in c for c in (held.get("cautions") or []))
            and code_nb == 0 and unheld_t.get("barrier") is False
            and unheld_t.get("barrier_timeouts") == 0
            and not any("release barrier" in c
                        for c in (unheld.get("cautions") or []))})

        # (n) live A/B, not just a plan: the table is keyed on (variant, signature),
        # so variant b's ordinary answer is never new for variant a. Both variants
        # hit the same drift path here and the two phases produce ONE body
        # signature, so only the keying can keep the two ledgers apart: 2 serial
        # signatures and 2 new, one per variant. Keyed on the signature alone both
        # collapse to 1. The hint is not what this check is about - the fixture's
        # divergence is a hit-count boundary that happens to overlap.
        code, ab_live, _ = _cli(["--url", base + "/drift/ab?after=2",
                                 "--body", "v=a", "--body-b", "v=b",
                                 "--method", "POST", "--count", "4",
                                 "--concurrency", "4", "--baseline-count", "2",
                                 "--timeout", "10", "--write-ack"])
        ab_new = ab_live.get("new_signatures_under_concurrency") or []
        ab_counts = ab_live.get("counts", {})
        checks.append({
            "name": "A/B accounting is per variant, live under concurrency",
            "expect": "2 serial signatures (a and b in phase one), 2 concurrent, "
                      "and 2 new — one per variant, both phase-two",
            "got": {"exit": code, "new": len(ab_new),
                    "new_variants": sorted(n["variant"] for n in ab_new),
                    "serial_distinct": ab_counts.get("serial_distinct_signatures"),
                    "concurrent_distinct":
                        ab_counts.get("concurrent_distinct_signatures"),
                    "labels": sorted(n["label"][:70] for n in ab_new)},
            "pass": len(ab_new) == 2
            and sorted(n["variant"] for n in ab_new) == ["a", "b"]
            and ab_counts.get("serial_distinct_signatures") == 2
            and ab_counts.get("concurrent_distinct_signatures") == 2
            and all("phase-two" in n["label"] for n in ab_new)})

        # (o) the cookie-swap shape: the divergence is in the FIRST of two
        # Set-Cookie headers and the last one is identical either way, so a
        # signature folded from httpkit's collapsed `headers` dict cannot see it.
        # Without the flag the two phases really are one signature (same body).
        cookie_argv = ["--method", "POST", "--count", "4", "--concurrency", "4",
                       "--baseline-count", "2", "--timeout", "10", "--write-ack"]
        code_off, cookie_off, _ = _cli(["--url", base + "/cookie/off?after=2"]
                                       + cookie_argv)
        code_on, cookie_on, _ = _cli(["--url", base + "/cookie/on?after=2"]
                                     + cookie_argv
                                     + ["--signature-header", "Set-Cookie"])
        on_new = cookie_on.get("new_signatures_under_concurrency") or []
        checks.append({
            "name": "every value of a repeated response header is folded in",
            "expect": "no --signature-header: 0 new, the bodies are identical. "
                      "--signature-header Set-Cookie: 1 new whose label carries "
                      "BOTH cookies, the swapped sid and the unchanged flavour",
            "got": {"without_header_new":
                    cookie_off.get("new_signatures_under_concurrency"),
                    "without_header_exit": code_off,
                    "with_header_new": len(on_new), "with_header_exit": code_on,
                    "label": on_new[0]["label"][-90:] if on_new else None},
            "pass": code_off == 0
            and cookie_off.get("new_signatures_under_concurrency") == []
            and len(on_new) == 1
            and "sid=phase-two" in on_new[0]["label"]
            and "flavour=vanilla" in on_new[0]["label"]})

        # (o2) --signature-mode status, status-length and regex are documented
        # capabilities with nothing behind them. Each one narrows what counts as a
        # difference, and on the SAME non-atomic handler that check (c) confirms,
        # the narrow modes see nothing: that is a negative result with a count, not
        # a clean endpoint, and only a capture that reads the order number sees the
        # oversell. --signature-mode regex without --signature-regex is refused.
        narrow_argv = ["--url", base + "/buy", "--method", "POST", "--count", "6",
                       "--concurrency", "6", "--baseline-count", "3",
                       "--timeout", "10", "--reset-url", base + "/reset",
                       "--write-ack"]
        modes = {}
        for tag, extra in (
                ("status", ["--signature-mode", "status"]),
                ("status-length", ["--signature-mode", "status-length"]),
                ("regex on result", ["--signature-mode", "regex",
                                     "--signature-regex", r'"result": "(\w+)"']),
                ("regex on order_no", ["--signature-mode", "regex",
                                       "--signature-regex", r'"order_no": (\d+)'])):
            code, out, _ = _cli(narrow_argv + extra)
            modes[tag] = {"exit": code,
                          "new": out.get("counts", {}).get("new_under_concurrency"),
                          "concurrent_distinct": out.get("counts", {})
                          .get("concurrent_distinct_signatures"),
                          "hint": out.get("verdict_hint")}
        bad_regex_code, _, bad_regex_err = _cli(["--url", base + "/buy",
                                                 "--signature-mode", "regex",
                                                 "--write-ack"])
        checks.append({
            "name": "a narrower signature mode reports a counted negative, not a pass",
            "expect": "status and status-length: 0 new and inconclusive on the same "
                      "handler check (c) confirms; a capture of result only: 0 new; "
                      "a capture of order_no: new >= 1; regex mode without a regex: "
                      "exit 2",
            "got": dict(modes, regex_without_pattern={
                "exit": bad_regex_code, "stderr_tail": bad_regex_err.strip()[-90:]}),
            "pass": modes["status"]["new"] == 0
            and modes["status"]["concurrent_distinct"] == 1
            and modes["status"]["hint"] == "inconclusive"
            and modes["status-length"]["new"] == 0
            and modes["status-length"]["hint"] == "inconclusive"
            and modes["regex on result"]["new"] == 0
            and (modes["regex on order_no"]["new"] or 0) >= 1
            and modes["regex on order_no"]["hint"] == "race-candidate"
            and bad_regex_code == 2
            and "--signature-regex" in bad_regex_err})

        # (p) the normaliser has to key on the token's SHAPE, not on the characters
        # it was drawn as: a receipt drawn as 16 digits must read the same as one
        # drawn with a letter in it, or the volatile field this rule exists to
        # absorb becomes the divergence and the burst reports a signature the
        # baseline never produced on an endpoint with no shared state at all.
        draws = ('{"receipt": "%s", "at": 1759183920123, "result": "pong"}' % tok
                 for tok in ("a1b2c3d4e5f60718", "0123456789012345",
                             "deadbeefdeadbeef", "1234567890abcdef"))
        body_forms = sorted({normalize(d) for d in draws})
        sig_forms = sorted({signature({"ok": True, "status": 200, "body": b,
                                       "headers": {}, "headers_all": []},
                                      "normalized-body", None, 4096, [])[0]
                            for b in body_forms})
        short_forms = sorted({normalize('{"id": "%s"}' % t)
                              for t in ("123456", "abcdef", "12ab56", "aaaaaa")})
        checks.append({
            "name": "a volatile token normalises by shape, not by its characters",
            "expect": "four draws of one 16-character receipt -> ONE normalised "
                      "body and ONE signature; four draws of a 6-character id -> "
                      "one form as well",
            "got": {"normalised_forms": body_forms, "signatures": sig_forms,
                    "six_char_forms": short_forms},
            "pass": len(body_forms) == 1 and len(sig_forms) == 1
            and len(short_forms) == 1})

        # (q) the plan's total and what a run then sends must be the same number,
        # resets included: a plan that over-counts a phase that never runs is a
        # budget the solver cannot reconcile against sent_requests.
        accounting = []
        for extra, tag in (([], "baseline 3"),
                           (["--no-baseline"], "--no-baseline"),
                           (["--baseline-count", "0"], "--baseline-count 0")):
            argv = ["--url", base + "/volatile", "--method", "POST",
                    "--count", "4", "--concurrency", "4", "--baseline-count", "3",
                    "--timeout", "10", "--reset-url", base + "/reset"] + extra
            _, planned, _ = _cli(argv + ["--dry-run"])
            _, actual, _ = _cli(argv + ["--write-ack"])
            accounting.append({
                "args": tag,
                "planned_total": planned.get("would_send", {}).get("total_requests"),
                "sent_requests": actual.get("sent_requests")})
        # and a plan whose request list was cut short has to say so: either phase's
        # list stops at 20, so the flag cannot key on --count alone
        _, cut, _ = _cli(["--url", base + "/volatile", "--method", "POST",
                          "--baseline-count", "25", "--count", "5", "--dry-run"])
        cut_send = cut.get("would_send", {})
        truncation = {
            "baseline_count": cut_send.get("serial_baseline", {}).get("count"),
            "baseline_listed": len(cut_send.get("serial_baseline", {})
                                   .get("requests") or []),
            "burst_count": cut_send.get("concurrent_burst", {}).get("count"),
            "burst_listed": len(cut_send.get("concurrent_burst", {})
                                .get("requests") or []),
            "plan_truncated": cut_send.get("plan_truncated")}
        checks.append({
            "name": "the dry-run plan totals exactly what a run then sends",
            "expect": "planned_total == sent_requests for all three baseline "
                      "shapes; and --baseline-count 25 --count 5 lists 20 of the 25 "
                      "baseline requests with plan_truncated true",
            "got": {"accounting": accounting, "truncation": truncation},
            "pass": all(row["planned_total"] is not None
                        and row["planned_total"] == row["sent_requests"]
                        for row in accounting)
            and truncation["baseline_count"] == 25
            and truncation["baseline_listed"] == 20
            and truncation["burst_count"] == 5
            and truncation["burst_listed"] == 5
            and truncation["plan_truncated"] is True})
    finally:
        server.shutdown()
        server.server_close()

    failures = [c["name"] for c in checks if not c["pass"]]
    return {"mode": "race-probe-selftest", "checks": checks,
            "total": len(checks), "failures": len(failures), "failed": failures,
            "verdict": "PASS" if not failures else "FAIL"}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    parser.add_argument("--url", help="the request to race (required unless --selftest)")
    parser.add_argument("--method", default="GET")
    parser.add_argument("--body")
    parser.add_argument("-H", "--header", action="append", default=[],
                        metavar="K: V")
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--follow", action="store_true",
                        help="follow redirects; off by default because a follow "
                             "doubles the load and hides the immediate response, "
                             "which is where a race shows")

    ab = parser.add_argument_group(
        "A/B mode: two different requests interleaved, the shape that wins a "
        "check-then-act race")
    ab.add_argument("--url-b", dest="url_b")
    ab.add_argument("--method-b", dest="method_b")
    ab.add_argument("--body-b", dest="body_b",
                    help="--count is the TOTAL, alternating a,b,a,b,...")

    load = parser.add_argument_group("load")
    load.add_argument("--count", type=int, default=20,
                      help="concurrent requests in the burst (max %d)" % MAX_COUNT)
    load.add_argument("--concurrency", type=int, default=8,
                      help="requests in flight at once (default 8, max %d): a "
                           "shared challenge database is easy to kill with load, "
                           "and a bigger wave is not a tighter one — measured "
                           "against this file's own loopback fixture, the spread "
                           "between the first and last request leaving went 6.0ms "
                           "at 4 in flight, 10.6 at 8, 24.1 at 16 and 80.4 at 32"
                           % MAX_CONCURRENCY)
    load.add_argument("--baseline-count", type=int, default=5,
                      help="serial requests sent first, one at a time, to measure "
                           "what the endpoint produces WITHOUT a race (default 5); "
                           "0 is the same as --no-baseline — with no serial "
                           "signature set, nothing can be called new")
    load.add_argument("--no-baseline", action="store_true",
                      help="skip it; then no signature can be called new")
    load.add_argument("--delay", type=float, default=0.0,
                      help="seconds between the serial baseline requests")
    load.add_argument("--no-barrier", action="store_true",
                      help="do not hold the worker threads on a release barrier")
    load.add_argument("--barrier-timeout", type=float, default=2.0)

    reset = parser.add_argument_group(
        "reset: without one, the serial baseline can consume the state the burst "
        "targets, which hides the finding")
    reset.add_argument("--reset-url")
    reset.add_argument("--reset-method", default="POST")
    reset.add_argument("--reset-body")

    sig = parser.add_argument_group("signature")
    sig.add_argument("--signature-mode", default="normalized-body",
                     choices=SIG_MODES,
                     help="normalized-body (default) blanks uuid, timestamp and "
                          "every run of 6+ hex or digit characters to ONE "
                          "placeholder, so a per-request receipt cannot fake a "
                          "divergence whichever characters it was drawn as; "
                          "raw-body shows what that hides")
    sig.add_argument("--signature-regex",
                     help="with --signature-mode regex: capture groups become the "
                          "signature")
    sig.add_argument("--signature-header", action="append", default=[],
                     metavar="NAME",
                     help="also fold this response header into the signature "
                          "(e.g. Location); repeatable. EVERY value of a repeated "
                          "header is folded in order, so a divergence in the first "
                          "of several Set-Cookie headers is still visible")
    sig.add_argument("--signature-bytes", type=int, default=4096)
    sig.add_argument("--excerpt", type=int, default=400,
                     help="verbatim response characters kept per signature, for "
                          "--evidence")

    gate = parser.add_argument_group("write gate")
    gate.add_argument("--write-ack", action="store_true",
                      help="required: this probe writes. Read the chain card's "
                           "blast_radius first and clean up the objects the burst "
                           "creates")
    gate.add_argument("--challenge",
                      help="render a tools/hooks.py post-probe command for the "
                           "result (printed, never run)")
    gate.add_argument("--class", dest="probe_class")
    gate.add_argument("--hypothesis-id", dest="hypothesis_id")

    parser.add_argument("--dry-run", action="store_true",
                        help="print exactly what would be sent, how many times "
                             "and at what concurrency; sends nothing")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    if args.selftest:
        out = selftest()
        httpkit.jprint(out, compact=args.compact)
        return 0 if out["verdict"] == "PASS" else 1

    if not args.url:
        parser.error("--url is required (or --selftest)")
    if args.concurrency < 1 or args.concurrency > MAX_CONCURRENCY:
        parser.error("--concurrency must be 1..%d: a shared challenge database is "
                     "easy to kill with load" % MAX_CONCURRENCY)
    if args.count < 1 or args.count > MAX_COUNT:
        parser.error("--count must be 1..%d" % MAX_COUNT)
    if args.baseline_count < 0:
        parser.error("--baseline-count cannot be negative")
    if args.signature_mode == "regex" and not args.signature_regex:
        parser.error("--signature-mode regex needs --signature-regex")

    args.run_token = os.urandom(4).hex()
    headers = httpkit.parse_headers(args.header)
    specs = build_specs(args)

    if args.dry_run:
        httpkit.jprint(dry_run_report(specs, args, headers), compact=args.compact)
        return 0

    if not args.write_ack:
        payload = dict(REFUSAL)
        payload["would_have_sent"] = {
            "serial_baseline": 0 if args.no_baseline else args.baseline_count,
            "concurrent_burst": args.count, "concurrency": args.concurrency}
        httpkit.jprint(payload, compact=args.compact)
        return 2

    report = run(args, headers, specs)
    httpkit.jprint(report, compact=args.compact)
    return 1 if report["verdict_hint"] == "race-candidate" else 0


if __name__ == "__main__":
    sys.exit(main())
