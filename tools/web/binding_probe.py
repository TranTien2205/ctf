#!/usr/bin/env python3
"""binding_probe.py — extra-field read-back matrix for web-mass-assignment.

The class's question is 'does the server bind fields the form never sent?'
— answered by adding one candidate field at a time and reading whether it
lands: echoed in the response body, or visible on a --readback URL
(profile/record GET). This tries a small default set (role, admin,
is_admin, isAdmin, debug, permissions, group, verified) with a canary
value, grading each by verbatim echo. A landed field is a CANDIDATE —
'it bound' is the measurement; whether the bound field changes
authorization is the agent's confirm.

    python3 tools/web/binding_probe.py --url http://h/register \
        --body 'user={V}&pass=x' --readback http://h/me
    python3 tools/web/binding_probe.py --selftest
"""
from __future__ import annotations

import argparse
import sys
import urllib.parse

import httpkit

_FIELDS = ["role", "admin", "is_admin", "isAdmin", "debug", "permissions",
           "group", "verified", "is_staff"]


def _text(r):
    b = r.get("body", "")
    return b.decode("utf-8", "replace") if isinstance(b, bytes) else (b or "")


def _post(args, extra):
    body = args["body"] + "&" + urllib.parse.urlencode(extra)
    return httpkit.request(args["url"], method=args.get("method", "POST"),
                           headers=args.get("headers"), body=body,
                           timeout=args.get("timeout", 15))


def probe(args) -> dict:
    base = _text(_post(args, {}))
    out = {"url": args["url"], "baseline_len": len(base), "cases": []}
    cand = []
    for field in _FIELDS:
        val = "bmk7x"
        r = _post(args, {field: val})
        body = _text(r)
        i = body.find(val)
        rec = {"field": field, "status": r.get("status"), "len": len(body)}
        landed = False
        if i >= 0 and val not in base:
            rec["echo_excerpt"] = body[max(0, i - 30):i + 40]
            landed = True
            rec["landed"] = "echoed-in-response"
        elif args.get("readback") and r.get("status") and r["status"] < 400:
            rb = _text(httpkit.request(args["readback"],
                                       headers=args.get("headers"),
                                       timeout=args.get("timeout", 15)))
            j = rb.find(val)
            if j >= 0:
                rec["readback_excerpt"] = rb[max(0, j - 30):j + 40]
                landed = True
                rec["landed"] = "visible-on-readback"
        if landed:
            cand.append(rec)
        out["cases"].append(rec)
    out["binding_candidates"] = cand
    out["candidate_only"] = True
    if not cand:
        out["note"] = ("no extra field echoed or appeared on readback — "
                       "record negative; a whitelist binder or a sink that "
                       "never reflects is indistinguishable from here")
    return out


def _selftest() -> int:
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    store = {}

    class App(BaseHTTPRequestHandler):
        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0))
            q = urllib.parse.parse_qs(self.rfile.read(n).decode())
            store.update({k: v[0] for k, v in q.items()})
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")

        def do_GET(self):
            body = "&".join(f"{k}={v}" for k, v in store.items())
            self.send_response(200)
            self.end_headers()
            self.wfile.write(body.encode())

        def log_message(self, *_a):
            pass

    srv = ThreadingHTTPServer(("127.0.0.1", 0), App)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    port = srv.server_address[1]
    out = probe({"url": f"http://127.0.0.1:{port}/register",
                 "method": "POST", "headers": {},
                 "body": "user=b&pass=x",
                 "readback": f"http://127.0.0.1:{port}/me", "timeout": 15})
    srv.shutdown()
    # binder accepts everything → all fields land on readback
    assert len(out["binding_candidates"]) == len(_FIELDS), out
    print("binding_probe selftest: ok")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url")
    ap.add_argument("--body",
                    help="documented form body, e.g. 'user=b&pass=x'")
    ap.add_argument("--method", default="POST", choices=["POST", "GET"])
    ap.add_argument("--readback", help="URL that shows the stored record")
    ap.add_argument("--fields", nargs="*", help="override the default field set")
    ap.add_argument("--headers", nargs="*")
    ap.add_argument("--timeout", type=float, default=15)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if not args.url or not args.body:
        ap.print_help()
        return 2
    a = vars(args) | {"headers": httpkit.parse_headers(args.headers)}
    if args.fields:
        global _FIELDS
        _FIELDS = args.fields
    httpkit.jprint(probe(a))
    return 0


if __name__ == "__main__":
    sys.exit(main())
