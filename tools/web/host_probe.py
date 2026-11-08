#!/usr/bin/env python3
"""host_probe.py — Host / forwarded-header canary matrix for web-host-header.

The class's question is mechanical: does a header the app trusts rewrite
the URLs it generates or the routing it applies? This sends a unique
canary through Host, X-Forwarded-Host, X-Forwarded-Server, X-Host, and
X-Original-Host one at a time, then grades each response: canary echoed
into the body (generated link / reset-URL poisoning shape), a routing
delta versus baseline (status or body-signature change = vhost/ACL
routing), or nothing. Every hit is a CANDIDATE with the verbatim excerpt
— an echoed canary means the header reaches link generation; whether a
password-reset or SSO flow actually uses it is the agent's confirm.

    python3 tools/web/host_probe.py --url http://h/forgot-password
    python3 tools/web/host_probe.py --selftest
"""
from __future__ import annotations

import argparse
import sys
import time

import httpkit

_HEADERS = ["Host", "X-Forwarded-Host", "X-Forwarded-Server", "X-Host",
            "X-Original-Host", "Forwarded"]


def _text(r):
    b = r.get("body", "")
    return b.decode("utf-8", "replace") if isinstance(b, bytes) else (b or "")


def _sig(r):
    return {"status": r.get("status"), "len": len(_text(r)),
            "sig": httpkit.body_signature(_text(r)) if _text(r) else None}


def probe(args) -> dict:
    mark = f"hostmk-{int(time.time())}.example"
    base = _sig(httpkit.request(args["url"], headers=args.get("headers"),
                                timeout=args.get("timeout", 10)))
    out = {"url": args["url"], "marker": mark, "baseline": base, "cases": []}
    cand = []
    for name in _HEADERS:
        h = dict(args.get("headers") or {})
        h[name] = f"host={mark}" if name == "Forwarded" else mark
        r = httpkit.request(args["url"], headers=h,
                            timeout=args.get("timeout", 10))
        body = _text(r)
        i = body.find(mark)
        s = _sig(r)
        rec = {"header": name, **s, "echoed": i >= 0}
        if i >= 0:
            rec["excerpt"] = body[max(0, i - 40):i + len(mark) + 40]
            rec["kind"] = "reflected-into-body"
            cand.append(rec)
        elif s["status"] != base["status"] or s["sig"] != base["sig"]:
            rec["kind"] = "routing-delta"
            cand.append(rec)
        out["cases"].append(rec)
    out["host_candidates"] = cand
    out["candidate_only"] = True
    if not cand:
        out["note"] = ("no header echoed or changed routing — record "
                       "negative; ACL bypass via Host usually needs a "
                       "path that 403s first")
    return out


def _selftest() -> int:
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    class App(BaseHTTPRequestHandler):
        def do_GET(self):
            xfh = self.headers.get("X-Forwarded-Host", "")
            body = f"<a href='http://{xfh}/reset?tok=1'>reset</a>" if xfh \
                else "<p>home</p>"
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body.encode())

        def log_message(self, *_a):
            pass

    srv = ThreadingHTTPServer(("127.0.0.1", 0), App)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_address[1]}/forgot"
    out = probe({"url": url, "headers": {}, "timeout": 10})
    srv.shutdown()
    hits = {c["header"] for c in out["host_candidates"]}
    assert hits == {"X-Forwarded-Host"}, out
    print("host_probe selftest: ok")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url")
    ap.add_argument("--headers", nargs="*")
    ap.add_argument("--timeout", type=float, default=10)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if not args.url:
        ap.print_help()
        return 2
    a = vars(args) | {"headers": httpkit.parse_headers(args.headers)}
    httpkit.jprint(probe(a))
    return 0


if __name__ == "__main__":
    sys.exit(main())
