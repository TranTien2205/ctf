#!/usr/bin/env python3
"""enum_probe.py — user-enumeration oracle for the web-user-enum class.

The class's question is a differential: does a login/reset endpoint answer
a KNOWN user differently from random ones — status, length, body text, or
timing? This fires the same request for one known account and a handful
of random users, measures each channel against the spread, and reports
which channel separates them (with verbatim excerpts). A separating
channel is a CANDIDATE — the skill's own confirm (repeatable across
several known users, not a fluke) still runs; a uniform response is an
honest negative worth recording.

    python3 tools/web/enum_probe.py --url http://h/login \
        --body 'user={U}&pass=x' --known-user admin
    python3 tools/web/enum_probe.py --selftest
"""
from __future__ import annotations

import argparse
import statistics
import sys
import time
import urllib.parse

import httpkit

_RANDOMS = ["zxq9_user_a", "zxq9_user_b", "zxq9_user_c", "zxq9_user_d"]


def _fire(args, user):
    body = args["body"].replace("{U}", urllib.parse.quote_plus(user))
    if args.get("pass_field"):
        body += "&" + urllib.parse.urlencode({args["pass_field"]: "x"})
    t0 = time.time()
    r = httpkit.request(args["url"], method=args.get("method", "POST"),
                        headers=args.get("headers"), body=body,
                        timeout=args.get("timeout", 15))
    r["_elapsed"] = round(time.time() - t0, 3)
    return r


def _sig(r):
    body = r.get("body", "")
    if isinstance(body, bytes):
        body = body.decode("utf-8", "replace")
    return {"status": r.get("status"), "len": len(body),
            "sig": httpkit.body_signature(body) if body else None,
            "elapsed": r.get("_elapsed"), "body": body[:300]}


def probe(args) -> dict:
    known = _sig(_fire(args, args["known_user"]))
    rands = [_sig(_fire(args, u)) for u in _RANDOMS]
    out = {"url": args["url"], "known_user": args["known_user"],
           "known": {k: v for k, v in known.items() if k != "body"},
           "randoms": [{k: v for k, v in s.items() if k != "body"}
                       for s in rands]}
    chans = []
    if all(s["status"] == rands[0]["status"] for s in rands):
        if known["status"] != rands[0]["status"]:
            chans.append({"channel": "status",
                          "signal": f"known={known['status']} vs random={rands[0]['status']}"})
    if all(s["sig"] == rands[0]["sig"] for s in rands):
        if known["sig"] != rands[0]["sig"]:
            chans.append({"channel": "body",
                          "signal": f"known len={known['len']} vs random len={rands[0]['len']}",
                          "known_excerpt": known["body"][:120],
                          "random_excerpt": rands[0]["body"][:120]})
    el = [s["elapsed"] for s in rands if s["elapsed"] is not None]
    if len(el) >= 3 and known["elapsed"] is not None:
        med = statistics.median(el)
        spread = max(el) - min(el)
        if abs(known["elapsed"] - med) > max(0.5, 3 * spread + 0.05):
            chans.append({"channel": "timing",
                          "signal": f"known={known['elapsed']}s vs random median={med}s "
                                    f"(spread {round(spread, 3)}s)"})
    out["enum_channels"] = chans
    out["candidate_only"] = True
    if not chans:
        out["note"] = ("known and random users are indistinguishable on "
                       "status/body/timing — record a real negative; "
                       "throttled endpoints may need slower retries")
    return out


def _selftest() -> int:
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    class Login(BaseHTTPRequestHandler):
        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0))
            q = urllib.parse.parse_qs(self.rfile.read(n).decode())
            user = q.get("user", [""])[0]
            if user == "admin":
                self.send_response(200)
                body = b"Welcome back, admin"
            else:
                self.send_response(200)
                body = b"Invalid credentials"
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_a):
            pass

    srv = ThreadingHTTPServer(("127.0.0.1", 0), Login)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_address[1]}/login"
    out = probe({"url": url, "method": "POST", "headers": {},
                 "body": "user={U}&pass=x", "known_user": "admin",
                 "timeout": 15})
    srv.shutdown()
    kinds = {c["channel"] for c in out["enum_channels"]}
    assert "body" in kinds, out
    print("enum_probe selftest: ok")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url")
    ap.add_argument("--body", help="request body; {U} marks the username slot")
    ap.add_argument("--pass-field", help="extra password field to append")
    ap.add_argument("--known-user", help="a username that exists")
    ap.add_argument("--method", default="POST", choices=["POST", "GET"])
    ap.add_argument("--headers", nargs="*")
    ap.add_argument("--timeout", type=float, default=15)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if not args.url or not args.body or not args.known_user:
        ap.print_help()
        return 2
    a = vars(args) | {"headers": httpkit.parse_headers(args.headers)}
    httpkit.jprint(probe(a))
    return 0


if __name__ == "__main__":
    sys.exit(main())
