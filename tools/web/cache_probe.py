#!/usr/bin/env python3
"""cache_probe.py — unkeyed-input matrix for web-cache-poisoning.

The class's first probe is a fixed pair: send an unkeyed header carrying a
unique marker under a cache-buster URL, then request the SAME URL cleanly
and look for the marker — a marker that persists into the clean response
means the poisoned copy was cached under a key anyone can hit. This fires
that pair per candidate header (X-Forwarded-Host/Scheme/Server, X-Host,
X-Original-URL, X-Rewrite-URL), records the cache headers the response
carries, and reports reflected / persisted-into-clean per header as
CANDIDATES with verbatim excerpts — a marker echo alone is reflection,
only persistence is poisoning, and impact still needs a reader.

    python3 tools/web/cache_probe.py --url http://h/page
    python3 tools/web/cache_probe.py --selftest
"""
from __future__ import annotations

import argparse
import sys
import time
import urllib.parse

import httpkit

_HEADERS = ["X-Forwarded-Host", "X-Forwarded-Scheme", "X-Forwarded-Server",
            "X-Host", "X-Original-URL", "X-Rewrite-URL"]


def _buster(url):
    u = urllib.parse.urlparse(url)
    pairs = urllib.parse.parse_qsl(u.query, keep_blank_values=True)
    pairs.append(("cb", str(int(time.time() * 1000))))
    return urllib.parse.urlunparse(u._replace(query=urllib.parse.urlencode(pairs)))


def _fire(url, headers, timeout):
    return httpkit.request(url, method="GET", headers=headers, timeout=timeout)


def _text(r):
    b = r.get("body", "")
    return b.decode("utf-8", "replace") if isinstance(b, bytes) else (b or "")


def probe(args) -> dict:
    mark = f"cachemk-{int(time.time())}.example"
    base_url = _buster(args["url"])
    base = _fire(base_url, args.get("headers"), args.get("timeout", 10))
    bh = {k.lower(): v for k, v in (base.get("headers") or {}).items()}
    out = {"url": base_url, "marker": mark,
           "cache_headers": {k: v for k, v in bh.items()
                             if k in ("age", "x-cache", "cache-control",
                                      "cf-cache-status", "via")},
           "cases": []}
    cand = []
    for i, name in enumerate(_HEADERS):
        url = _buster(args["url"]) + str(i)  # fresh key per header: no
        h = dict(args.get("headers") or {})  # cross-case contamination
        h[name] = mark
        r = _fire(url, h, args.get("timeout", 10))
        body = _text(r)
        i = body.find(mark)
        reflected = i >= 0
        rec = {"header": name, "status": r.get("status"),
               "reflected": reflected}
        if reflected:
            rec["excerpt"] = body[max(0, i - 30):i + len(mark) + 30]
            clean = _fire(url, args.get("headers"), args.get("timeout", 10))
            cbody = _text(clean)
            j = cbody.find(mark)
            rec["case_url"] = url
            rec["persisted_in_clean"] = j >= 0
            if j >= 0:
                rec["clean_excerpt"] = cbody[max(0, j - 30):j + len(mark) + 30]
                cand.append(rec)
        out["cases"].append(rec)
    out["poison_candidates"] = cand
    out["candidate_only"] = True
    if not cand:
        out["note"] = ("no unkeyed header's marker survived into the clean "
                       "request — reflection without persistence is not "
                       "poisoning; record per-case negative")
    return out


def _selftest() -> int:
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    cache = {}

    class C(BaseHTTPRequestHandler):
        def do_GET(self):
            key = self.path
            xfh = self.headers.get("X-Forwarded-Host")
            if key in cache:
                body, hits = cache[key]
                cache[key] = (body, hits + 1)
            else:
                body = f"<link href='http://{xfh or 'cdn'}/a'>" if xfh else "<p>ok</p>"
                cache[key] = (body, 1)
            self.send_response(200)
            self.send_header("X-Cache", "HIT" if cache[key][1] > 1 else "MISS")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body.encode())

        def log_message(self, *_a):
            pass

    srv = ThreadingHTTPServer(("127.0.0.1", 0), C)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_address[1]}/page"
    out = probe({"url": url, "headers": {}, "timeout": 10})
    srv.shutdown()
    hits = {c["header"] for c in out["poison_candidates"]}
    assert "X-Forwarded-Host" in hits, out
    assert out["cache_headers"], out
    print("cache_probe selftest: ok")
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
