#!/usr/bin/env python3
"""cors_probe.py — Origin-reflection measurement for the web-cors class.

The CORS question is mechanical: send a foreign Origin, read back
Access-Control-Allow-Origin and Access-Control-Allow-Credentials, and
grade the pair. A reflected origin WITH credentials is the exploitable
shape; a wildcard without credentials is usually not; absent headers is a
negative. This fires one request per candidate origin (foreign, null,
subdomain-ish) and reports the graded pair for each — candidates, never
findings; whether any sensitive resource sits behind the policy is still
the agent's question.

    python3 tools/web/cors_probe.py --url http://h/api/me [--headers 'Cookie: ...']
    python3 tools/web/cors_probe.py --selftest
"""
from __future__ import annotations

import argparse
import sys
import urllib.parse

import httpkit

_ORIGINS = ["https://foreign.example", "null",
            "https://{host}.foreign.example", "{scheme}://sub.{host}"]


def probe(args) -> dict:
    u = urllib.parse.urlparse(args["url"])
    host = u.hostname or "target"
    scheme = u.scheme or "https"
    out = {"url": args["url"], "cases": []}
    for tpl in _ORIGINS:
        origin = tpl.format(host=host, scheme=scheme)
        hdrs = dict(args.get("headers") or {})
        hdrs["Origin"] = origin
        r = httpkit.request(args["url"], method=args.get("method", "GET"),
                            headers=hdrs, timeout=args.get("timeout", 10))
        h = {k.lower(): v for k, v in (r.get("headers") or {}).items()}
        acao = h.get("access-control-allow-origin")
        acac = (h.get("access-control-allow-credentials") or "").lower()
        if acao is None:
            verdict = "absent"
        elif acao == "*" and acac != "true":
            verdict = "wildcard-no-credentials"
        elif acao == "*" and acac == "true":
            verdict = "wildcard-with-credentials(unusual)"
        elif acao == origin and acac == "true":
            verdict = "reflected-with-credentials"
        elif acao == origin:
            verdict = "reflected-no-credentials"
        else:
            verdict = "other-origin-returned"
        out["cases"].append({"origin_sent": origin, "acao": acao, "acac": acac,
                             "verdict": verdict, "status": r.get("status")})
    hits = [c for c in out["cases"]
            if c["verdict"] in ("reflected-with-credentials",
                                "wildcard-with-credentials(unusual)")]
    out["cors_candidates"] = hits
    out["candidate_only"] = True
    if not hits:
        out["note"] = ("no origin shape earned the credential pair — "
                       "record negative; subdomain/null tricks need a real "
                       "victim domain to mean anything")
    return out


def _selftest() -> int:
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    class Cors(BaseHTTPRequestHandler):
        def do_GET(self):
            o = self.headers.get("Origin", "")
            self.send_response(200)
            if o and o.endswith("foreign.example"):
                self.send_header("Access-Control-Allow-Origin", o)
                self.send_header("Access-Control-Allow-Credentials", "true")
            self.end_headers()
            self.wfile.write(b"{}")

        def log_message(self, *_a):
            pass

    srv = ThreadingHTTPServer(("127.0.0.1", 0), Cors)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_address[1]}/api"
    out = probe({"url": url, "headers": {}, "timeout": 10})
    srv.shutdown()
    verdicts = {c["origin_sent"]: c["verdict"] for c in out["cases"]}
    assert verdicts["https://foreign.example"] == "reflected-with-credentials", verdicts
    assert verdicts["null"] == "absent", verdicts
    print("cors_probe selftest: ok")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url")
    ap.add_argument("--method", default="GET", choices=["GET", "POST", "OPTIONS"])
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
