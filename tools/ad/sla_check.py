#!/usr/bin/env python3
"""Run the service's own health checks, and refuse a patch that breaks them.

In attack-defense the scoreboard pays for availability as well as for flags, and
the usual way a team loses is not being exploited -- it is patching the exploit
and the feature in the same edit. So the contract here is deliberately narrow:

    before a patch:  sla_check.py <spec> --save before.json
    apply the patch
    after:           sla_check.py <spec> --save after.json --compare before.json

and `--compare` exits non-zero when a check that PASSED before now fails. That
is the only signal worth acting on: a check that was already red is the
organiser's problem or an earlier mistake, and blocking on it would stop you
patching at all.

The spec is JSON the operator writes once per service, e.g.

    {
      "service": "notes",
      "base": "http://10.60.1.2:5000",
      "checks": [
        {"name": "index",  "path": "/",            "expect_status": 200},
        {"name": "login",  "path": "/api/login",   "method": "POST",
         "body": "{\\"u\\":\\"probe\\",\\"p\\":\\"probe\\"}",
         "headers": {"Content-Type": "application/json"},
         "expect_status": 200, "expect_contains": "token"},
        {"name": "store",  "path": "/api/note",    "method": "POST",
         "body": "hello", "expect_status": 201}
      ]
    }

Write the checks from the ORGANISER's checker if they publish it, and from the
service's own happy path if they do not. A check that only asserts "200 on /"
will happily pass while the feature the checker exercises is broken.

Output is JSON on stdout, like every other tool in this tree.
"""
import argparse
import json
import os
import ssl
import sys
import time
import urllib.error
import urllib.request


def run_check(base, check, default_timeout=5.0):
    """Run one check and return a plain dict. Never raises."""
    url = base.rstrip("/") + check.get("path", "/")
    method = check.get("method", "GET").upper()
    body = check.get("body")
    data = body.encode() if isinstance(body, str) else body
    headers = dict(check.get("headers") or {})
    timeout = float(check.get("timeout", default_timeout))

    started = time.monotonic()
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    ctx = ssl.create_default_context()
    # A contest service usually has a self-signed certificate or none at all,
    # and a TLS error here would read as "the service is down".
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    status, text, error = None, "", None
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            status = resp.status
            text = resp.read(65536).decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        status = exc.code
        try:
            text = exc.read(65536).decode("utf-8", "replace")
        except Exception:
            text = ""
    except Exception as exc:
        error = "%s: %s" % (type(exc).__name__, exc)

    elapsed = round(time.monotonic() - started, 3)
    return evaluate(check, status, text, error, elapsed)


def evaluate(check, status, text, error, elapsed):
    """Decide pass/fail from a response. Split out so selftest can drive it."""
    reasons = []
    if error is not None:
        reasons.append("transport: " + error)
    else:
        want_status = check.get("expect_status")
        if want_status is not None and status != want_status:
            reasons.append("status %s, wanted %s" % (status, want_status))
        needle = check.get("expect_contains")
        if needle and needle not in text:
            reasons.append("body does not contain %r" % needle)
        forbidden = check.get("expect_absent")
        if forbidden and forbidden in text:
            reasons.append("body contains forbidden %r" % forbidden)
    return {
        "name": check.get("name") or check.get("path", "?"),
        "ok": not reasons,
        "status": status,
        "seconds": elapsed,
        "reasons": reasons,
        # A short excerpt, because a diff between runs is usually enough to see
        # what a patch changed, and a full body makes the saved file unreadable.
        "excerpt": text[:200],
    }


def run_all(spec):
    base = spec["base"]
    results = [run_check(base, c, float(spec.get("timeout", 5.0)))
               for c in spec.get("checks", [])]
    return {
        "mode": "sla-check",
        "service": spec.get("service", "?"),
        "base": base,
        "checks": len(results),
        "passed": sum(1 for r in results if r["ok"]),
        "ok": all(r["ok"] for r in results) and bool(results),
        "results": results,
    }


def compare(before, after):
    """Regressions only: a check that passed before and fails now.

    Deliberately asymmetric. Something newly FIXED is not a reason to block, and
    something that was already broken is not caused by this patch.
    """
    was = {r["name"]: r["ok"] for r in before.get("results", [])}
    regressions, recovered = [], []
    for r in after.get("results", []):
        name = r["name"]
        if was.get(name) and not r["ok"]:
            regressions.append({"check": name, "reasons": r["reasons"],
                                "excerpt": r["excerpt"]})
        elif was.get(name) is False and r["ok"]:
            recovered.append(name)
    return {
        "regressions": regressions,
        "recovered": recovered,
        "verdict": "REVERT THE PATCH" if regressions else "safe to keep",
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", help="path to the service spec JSON")
    ap.add_argument("--save", help="write this run to a file for a later --compare")
    ap.add_argument("--compare", help="an earlier saved run; exits 1 on a regression")
    args = ap.parse_args()

    with open(args.spec, encoding="utf-8") as fh:
        spec = json.load(fh)
    if not spec.get("checks"):
        raise SystemExit(json.dumps({
            "error": "the spec has no checks",
            "why": "a spec with no checks always passes, which is worse than no "
                   "check at all because it reads as a green light"}))

    out = run_all(spec)

    if args.compare:
        with open(args.compare, encoding="utf-8") as fh:
            out["comparison"] = compare(json.load(fh), out)

    if args.save:
        with open(args.save, "w", encoding="utf-8") as fh:
            json.dump(out, fh, indent=1)
        out["saved"] = args.save

    print(json.dumps(out, ensure_ascii=False, indent=1))
    if out.get("comparison", {}).get("regressions"):
        return 1
    return 0 if out["ok"] else 2


if __name__ == "__main__":
    sys.exit(main())
