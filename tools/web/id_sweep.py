#!/usr/bin/env python3
"""Identifier-existence oracle and IDOR sweep.

Three parts, because an id sweep is never just a loop:

  GENERATOR   a numeric range, a wordlist, a printf-style format over a range,
              a UUID/ObjectId-shaped mutation of a known id, or stdin
  CLASSIFIER  each response is bucketed against a baseline taken from an id that
              cannot exist, so a soft-404 is not counted as a hit; buckets can
              also be named by regex (--hit-regex / --miss-regex)
  BULK MODE   one request carries many ids and the response NAMES the misses.
              An endpoint that answers "not found: 7, 9, 12" for a batch of 50 is
              a far cheaper oracle than 50 requests, and it usually is not rate
              limited the same way.

Rate limiting is honoured: --rate caps requests per second, 429 and 503 trigger
exponential backoff, and Retry-After is obeyed when the server sends it.

    # numeric range with a baseline
    python3 tools/web/id_sweep.py --url 'http://t/api/order/{id}' --range 1-500 \\
        --rate 10 --header 'Cookie: session=...'

    # bulk oracle: 50 ids per request, the response lists what is missing
    python3 tools/web/id_sweep.py --url http://t/api/orders --method POST \\
        --header 'Content-Type: application/json' --body '{"ids":[{ids}]}' \\
        --range 1-5000 --bulk 50 --miss-regex 'not found: ([0-9]+)'

    # mutate one known identifier
    python3 tools/web/id_sweep.py --url 'http://t/u/{id}' --mutate 507f1f77bcf86cd799439011
"""
import argparse
import json
import os
import re
import string
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import httpkit  # noqa: E402

HEX = "0123456789abcdef"


# ------------------------------------------------------------------ generators


def gen_range(spec, step=1):
    """'1-500' or '1-500:5' -> ['1', ...]"""
    if ":" in spec:
        spec, _, raw_step = spec.partition(":")
        step = int(raw_step)
    low, _, high = spec.partition("-")
    return [str(n) for n in range(int(low), int(high) + 1, step)]


def gen_format(fmt, spec):
    """'user{n}' or 'ORD-%05d' over a range."""
    values = gen_range(spec)
    out = []
    for value in values:
        if "{n}" in fmt:
            out.append(fmt.replace("{n}", value))
        elif "%" in fmt:
            out.append(fmt % int(value))
        else:
            out.append(fmt + value)
    return out


def gen_mutate(known, per_position=2):
    """Neighbours of a known id: +-1 on each hex/decimal position, plus endpoints.

    An ObjectId or a UUID is not guessable in bulk, but its NEIGHBOURS are: the
    counter tail of an ObjectId and the last block of a sequential UUID both move
    by one, and that is usually enough to prove ownership is unchecked.
    """
    out, base = [known], list(known)
    alphabet = HEX if all(c in HEX for c in known.lower()) else (
        string.digits if known.isdigit() else string.hexdigits[:16] + string.ascii_lowercase)
    for index in range(len(known) - 1, -1, -1):
        ch = known[index].lower()
        if ch not in alphabet:
            continue
        pos = alphabet.index(ch)
        for delta in range(1, per_position + 1):
            for candidate in (pos - delta, pos + delta):
                if 0 <= candidate < len(alphabet):
                    mutated = base.copy()
                    mutated[index] = alphabet[candidate]
                    out.append("".join(mutated))
    return list(dict.fromkeys(out))


def load_ids(args):
    if args.range and args.format:
        return gen_format(args.format, args.range), "format"
    if args.range:
        return gen_range(args.range), "range"
    if args.wordlist:
        with open(args.wordlist, encoding="utf-8", errors="replace") as handle:
            return [l.strip() for l in handle if l.strip()
                    and not l.startswith("#")], "wordlist"
    if args.mutate:
        return gen_mutate(args.mutate), "mutate"
    if args.stdin:
        return [l.strip() for l in sys.stdin if l.strip()], "stdin"
    if args.id:
        return list(args.id), "explicit"
    return [], "none"


NONEXISTENT_NUMERIC = "999999999"
NONEXISTENT_TEXT = "ctf-v2-no-such-id-%d" % os.getpid()


# ------------------------------------------------------------------ throttle


class Throttle:
    """A rate cap plus exponential backoff on 429/503."""

    def __init__(self, rate=0.0, max_backoff=30.0):
        self.interval = 1.0 / rate if rate else 0.0
        self.max_backoff = max_backoff
        self.backoff = 0.0
        self.last = 0.0
        self.sleeps = 0.0
        self.backoff_events = 0

    def wait(self):
        delay = max(0.0, self.interval - (time.monotonic() - self.last)) + self.backoff
        if delay > 0:
            time.sleep(delay)
            self.sleeps += delay
        self.last = time.monotonic()

    def observe(self, resp):
        status = resp.get("status")
        if status in (429, 503):
            retry = resp.get("headers", {}).get("Retry-After")
            try:
                hinted = float(retry)
            except (TypeError, ValueError):
                hinted = 0.0
            self.backoff = min(self.max_backoff,
                               max(hinted, (self.backoff * 2) or 1.0))
            self.backoff_events += 1
            return True
        self.backoff = 0.0
        return False


# ------------------------------------------------------------------ classifier


def send(args, headers, value, key="id"):
    url = httpkit.fill(args.url, **{key: value})
    body = httpkit.fill(args.body, **{key: value}) if args.body else None
    hdrs = {k: httpkit.fill(v, **{key: value}) for k, v in headers.items()}
    return httpkit.request(url, args.method, hdrs, body, timeout=args.timeout,
                           follow=not args.no_follow)


def classify(resp, baseline, hit_rx, miss_rx):
    if not resp["ok"]:
        return "transport-error", resp.get("error", "")
    text = resp["body"]
    if miss_rx and miss_rx.search(text):
        return "miss", "matched --miss-regex"
    if hit_rx and hit_rx.search(text):
        return "hit", "matched --hit-regex"
    if baseline is None:
        return ("hit" if (resp["status"] or 0) < 400 else "miss"), "status only"
    if resp["status"] != baseline["status"]:
        return "hit", "status %s vs baseline %s" % (resp["status"], baseline["status"])
    if text == baseline["body"]:
        return "miss", "body identical to the non-existent-id baseline"
    if abs(resp["length"] - baseline["length"]) > 2:
        return "hit", "length %d vs baseline %d" % (resp["length"], baseline["length"])
    return "ambiguous", "same status and length as the baseline"


FLAGRX = re.compile(r"[A-Za-z0-9_]{2,16}\{[^}\n]{3,120}\}")


# ------------------------------------------------------------------ bulk


def _names(rx, body):
    """Ids named by a bulk response.

    A server answers either one id per match ("missing: 7" x3) or the whole
    batch in one capture ("not found: 2, 4, 5"). Splitting every capture on
    commas and whitespace handles both; without the split the single-capture
    form silently marked the entire chunk as existing.
    """
    if not rx:
        return []
    out = []
    for match in rx.findall(body):
        text = match if isinstance(match, str) else (match[0] if match else "")
        out.extend(part for part in re.split(r"[,\s;|]+", text.strip()) if part)
    return list(dict.fromkeys(out))


def bulk_sweep(args, headers, ids, throttle, miss_rx, hit_rx):
    """One request per chunk; the response names the misses, so hits = rest."""
    sep = args.bulk_sep
    chunks = [ids[i:i + args.bulk] for i in range(0, len(ids), args.bulk)]
    hits, misses, requests, samples = [], [], 0, []
    for chunk in chunks:
        joined = sep.join(chunk)
        for attempt in range(args.retries + 1):
            throttle.wait()
            resp = send(args, headers, joined, key="ids")
            requests += 1
            if not throttle.observe(resp):
                break
        named_misses = _names(miss_rx, resp.get("body", ""))
        named_hits = _names(hit_rx, resp.get("body", ""))
        if named_misses:
            missing = set(named_misses)
            misses.extend([i for i in chunk if i in missing])
            hits.extend([i for i in chunk if i not in missing])
        elif named_hits:
            present = set(named_hits)
            hits.extend([i for i in chunk if i in present])
            misses.extend([i for i in chunk if i not in present])
        else:
            samples.append({"chunk_first": chunk[0], "chunk_size": len(chunk),
                            "status": resp.get("status"),
                            "body_sample": resp.get("body", "")[:400]})
        if len(samples) <= 3 and resp.get("body"):
            flags = FLAGRX.findall(resp["body"])
            if flags:
                samples.append({"flag_shapes": flags[:5],
                                "chunk_first": chunk[0]})
    return {"mode_used": "bulk", "requests": requests,
            "chunks": len(chunks), "hits": hits, "misses": misses,
            "unclassified_samples": samples[:6]}


def single_sweep(args, headers, ids, baseline, throttle, hit_rx, miss_rx):
    results, flags, sent = [], [], 0
    for value in ids:
        for attempt in range(args.retries + 1):
            throttle.wait()
            resp = send(args, headers, value)
            sent += 1
            if not throttle.observe(resp):
                break
        verdict, why = classify(resp, baseline, hit_rx, miss_rx)
        entry = {"id": value, "verdict": verdict, "why": why,
                 "status": resp.get("status"), "length": resp.get("length")}
        if resp.get("error"):
            entry["error"] = resp["error"]
        if verdict == "hit":
            entry["body_sample"] = resp.get("body", "")[:args.sample_chars]
            entry["signature"] = httpkit.body_signature(resp.get("body", ""))
            found = FLAGRX.findall(resp.get("body", ""))
            if found:
                entry["flag_shapes"] = found[:5]
                flags.extend(found[:5])
        results.append(entry)
        if args.stop_on_flag and flags:
            break
    return {"mode_used": "single", "requests": sent,
            "candidates_classified": len(results),
            "results": results, "flag_shapes": sorted(set(flags))}


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    parser.add_argument("--url", required=True, metavar="URL_WITH_{id}",
                        help="request template; {id} single mode, {ids} bulk mode")
    parser.add_argument("--method", default="GET")
    parser.add_argument("--header", action="append", default=[], metavar="K: V")
    parser.add_argument("--body", metavar="BODY_WITH_{id}_or_{ids}")
    parser.add_argument("--no-follow", action="store_true",
                        help="do not follow redirects; a 302 is often the oracle")

    g = parser.add_argument_group("generator")
    g.add_argument("--range", metavar="LOW-HIGH[:STEP]")
    g.add_argument("--format", metavar="TEMPLATE",
                   help="printf or {n} template applied over --range")
    g.add_argument("--wordlist")
    g.add_argument("--mutate", metavar="KNOWN_ID",
                   help="sweep the single-character neighbours of a known id")
    g.add_argument("--id", action="append", default=[])
    g.add_argument("--stdin", action="store_true")
    g.add_argument("--limit", type=int, default=5000,
                   help="hard cap on candidates actually sent")

    c = parser.add_argument_group("classifier")
    c.add_argument("--hit-regex", metavar="REGEX",
                   help="a response matching this is a hit; in bulk mode, group 1 "
                        "names the ids that exist")
    c.add_argument("--miss-regex", metavar="REGEX",
                   help="a response matching this is a miss; in bulk mode, group 1 "
                        "names the ids that do NOT exist")
    c.add_argument("--baseline-id", help="id used for the non-existent baseline")
    c.add_argument("--no-baseline", action="store_true")
    c.add_argument("--sample-chars", type=int, default=300)

    b = parser.add_argument_group("bulk oracle")
    b.add_argument("--bulk", type=int, default=0, metavar="N",
                   help="ids per request; substitutes {ids} instead of {id}")
    b.add_argument("--bulk-sep", default=",")

    parser.add_argument("--rate", type=float, default=0.0,
                        help="max requests per second (0 = no cap)")
    parser.add_argument("--retries", type=int, default=2,
                        help="retries after a 429/503 backoff")
    parser.add_argument("--timeout", type=float, default=10)
    parser.add_argument("--stop-on-flag", action="store_true")
    parser.add_argument("--out", metavar="FILE")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args(argv)

    placeholder = "{ids}" if args.bulk else "{id}"
    where = args.url + (args.body or "") + "".join(args.header)
    if placeholder not in where:
        httpkit.jprint({"mode": "id-sweep", "ok": False,
                        "error": "no %s placeholder in --url, --body or --header"
                                 % placeholder}, args.compact)
        return 2

    try:
        ids, source = load_ids(args)
    except (ValueError, OSError) as exc:
        httpkit.jprint({"mode": "id-sweep", "ok": False,
                        "error": "%s: %s" % (type(exc).__name__, exc)}, args.compact)
        return 2
    if not ids:
        httpkit.jprint({"mode": "id-sweep", "ok": False,
                        "error": "no candidates: give --range, --format, "
                                 "--wordlist, --mutate, --id or --stdin"},
                       args.compact)
        return 2
    truncated = len(ids) > args.limit
    ids = ids[: args.limit]

    headers = httpkit.parse_headers(args.header)
    hit_rx = re.compile(args.hit_regex, re.S) if args.hit_regex else None
    miss_rx = re.compile(args.miss_regex, re.S) if args.miss_regex else None
    throttle = Throttle(args.rate)

    baseline = None
    if not args.no_baseline and not args.bulk:
        probe_id = args.baseline_id or (NONEXISTENT_NUMERIC if ids[0].isdigit()
                                       else NONEXISTENT_TEXT)
        probe = send(args, headers, probe_id)
        if probe["ok"]:
            baseline = {"id": probe_id, "status": probe["status"],
                        "length": probe["length"], "body": probe["body"]}

    started = time.monotonic()
    if args.bulk:
        outcome = bulk_sweep(args, headers, ids, throttle, miss_rx, hit_rx)
        hits, tried = len(outcome["hits"]), len(ids)
    else:
        outcome = single_sweep(args, headers, ids, baseline, throttle, hit_rx,
                              miss_rx)
        hits = sum(1 for r in outcome["results"] if r["verdict"] == "hit")
        tried = len(outcome["results"])

    report = {
        "mode": "id-sweep", "ok": True,
        "target": {"url": args.url, "method": args.method.upper()},
        "generator": {"source": source, "candidates": len(ids),
                      "truncated_by_limit": truncated},
        "baseline": None if baseline is None else
                    {k: baseline[k] for k in ("id", "status", "length")},
        "throttle": {"rate_per_second": args.rate or None,
                     "slept_seconds": round(throttle.sleeps, 2),
                     "backoff_events": throttle.backoff_events},
        "requests_sent": outcome["requests"],
        "hits": hits, "tried": tried,
        "verdict_line": "%d of %d identifiers exist" % (hits, tried),
        "requests_saved_by_bulk": (tried - outcome["requests"]) if args.bulk else 0,
        "elapsed": round(time.monotonic() - started, 3),
        "outcome": outcome,
        "evidence_note": ("existence is not access: quote the body of one hit that "
                          "belongs to another principal to record an IDOR"),
    }
    if baseline is None and not args.bulk:
        report["caution"] = ("no baseline: 'hit' means status < 400 only, which a "
                             "soft-404 satisfies")
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            json.dump(report, handle, ensure_ascii=False, indent=2, default=str)
        report["out"] = os.path.abspath(args.out)
    httpkit.jprint(report, args.compact)
    return 0 if hits else 1


if __name__ == "__main__":
    sys.exit(main())
