#!/usr/bin/env python3
"""csrf_probe.py — replay matrix for the web-csrf class.

CSRF confirmation is mechanical: the same state-changing POST replayed
(a) as submitted, (b) with the token field stripped, (c) under a foreign
Origin/Referer. If the stripped or foreign replay is indistinguishable
from the baseline — same status, same signature — the token was not
enforced. This fires exactly that matrix through httpkit and reports the
accepted-without-token cases as CANDIDATES with verbatim measurements;
a candidate is a measurement, not a finding — whether the victim browser
actually carries the ambient credential is the agent's question.

    python3 tools/web/csrf_probe.py --url http://h/transfer \
        --body 'amount=1&to=x&csrf_token=TOK' --token-field csrf_token
    python3 tools/web/csrf_probe.py --selftest
"""
from __future__ import annotations

import argparse
import sys
import urllib.parse

import httpkit

_FOREIGN = "https://foreign.example"


def _sig(r):
    body = r.get("body", "")
    if isinstance(body, bytes):
        body = body.decode("utf-8", "replace")
    return {"status": r.get("status"), "len": len(body),
            "sig": httpkit.body_signature(body) if body else None}


def _fire(args, body, headers):
    return httpkit.request(args["url"], method=args.get("method", "POST"),
                           headers=headers, body=body,
                           timeout=args.get("timeout", 15))


def _strip_token(body, field):
    pairs = urllib.parse.parse_qsl(body, keep_blank_values=True)
    return urllib.parse.urlencode([(k, v) for k, v in pairs if k != field])


def _same(a, b):
    return a["status"] == b["status"] and a["sig"] == b["sig"] and \
           abs(a["len"] - b["len"]) <= 8


def probe(args) -> dict:
    body = args["body"]
    tf = args.get("token_field")
    base_h = dict(args.get("headers") or {})
    base = _sig(_fire(args, body, base_h))
    out = {"url": args["url"], "baseline": base, "cases": []}

    cases = []
    if tf and tf + "=" in body:
        cases.append(("token-stripped", _strip_token(body, tf), base_h))
    else:
        cases.append(("as-sent-no-token-field", body, base_h))
    h2 = dict(base_h)
    h2["Origin"] = _FOREIGN
    h2["Referer"] = _FOREIGN + "/p"
    cases.append(("foreign-origin", body, h2))
    h3 = dict(base_h)
    h3.pop("Origin", None)
    h3.pop("Referer", None)
    cases.append(("no-origin-referer", body, h3))

    cand = []
    for name, b, h in cases:
        s = _sig(_fire(args, b, h))
        accepted = _same(s, base)
        rec = {"case": name, **s, "indistinguishable_from_baseline": accepted}
        # a replay that dropped the token and was still accepted is the
        # vuln shape; accepted-with-token under a foreign origin only says
        # the origin check is absent — context, not a candidate
        if accepted and name in ("token-stripped", "as-sent-no-token-field"):
            cand.append(rec)
        out["cases"].append(rec)
    fo = next((c for c in out["cases"] if c["case"] == "foreign-origin"), None)
    out["origin_check"] = ("absent" if fo and fo["indistinguishable_from_baseline"]
                           else "present-or-partial")
    out["csrf_candidates"] = cand
    out["candidate_only"] = True
    if not cand:
        out["note"] = ("every replay shape differed from baseline — the "
                       "enforcement point exists; record negative")
    return out


def _selftest() -> int:
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    class App(BaseHTTPRequestHandler):
        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(n).decode()
            q = urllib.parse.parse_qs(raw, keep_blank_values=True)
            if "csrf_token" not in q:
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b"missing token")
            else:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"done")

        def log_message(self, *_a):
            pass

    srv = ThreadingHTTPServer(("127.0.0.1", 0), App)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_address[1]}/t"
    out = probe({"url": url, "method": "POST", "headers": {},
                 "body": "amount=1&csrf_token=TOK", "token_field": "csrf_token",
                 "timeout": 15})
    srv.shutdown()
    names = {c["case"]: c["indistinguishable_from_baseline"] for c in out["cases"]}
    # foreign replay still carries the token → accepted (server ignores Origin)
    assert names["foreign-origin"] is True, out
    assert names["token-stripped"] is False, out
    # token enforced → no candidates even though origin check is absent
    assert out["csrf_candidates"] == [], out
    assert out["origin_check"] == "absent", out
    print("csrf_probe selftest: ok")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url")
    ap.add_argument("--method", default="POST", choices=["POST", "GET"])
    ap.add_argument("--body", help="urlencoded body of the state-changing request")
    ap.add_argument("--token-field", help="name of the CSRF token field, if any")
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
    httpkit.jprint(probe(a))
    return 0


if __name__ == "__main__":
    sys.exit(main())
