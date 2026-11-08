#!/usr/bin/env python3
"""redirect_probe.py — open-redirect sweep for the web-open-redirect class.

The question is mechanical: does a parameter move the Location header to
an off-site URL? This tries the usual parameter names (next, url,
redirect, return, dest, callback, to, continue, redir, target) with a
canary URL, then the bypass forms (//host, %5chost, https://host@target,
target.evil) on any parameter that moved the header. A hit is a
candidate — a 3xx Location pointing off-site is verbatim evidence; which
victim flow consumes it (oauth, login, invite) is still the agent's call.

    python3 tools/web/redirect_probe.py --url 'http://h/login?next=/home'
    python3 tools/web/redirect_probe.py --url URL --param next
    python3 tools/web/redirect_probe.py --selftest
"""
from __future__ import annotations

import argparse
import sys
import urllib.parse

import httpkit

_PARAMS = ["next", "url", "redirect", "redirect_uri", "return", "returnUrl",
           "dest", "destination", "callback", "to", "continue", "redir", "target"]
_FORMS = ["https://{evil}/", "//{evil}/", "https://{host}.{evil}/",
          "https://{evil}@{host}/", "/%5c{evil}/", "https://{evil}%2f%2f."]
_evil = "evxl.example"


def _hit(location):
    """Grade a Location header: does it resolve off-site to the canary host?"""
    if not location:
        return None
    if _evil in location:
        return location
    p = urllib.parse.urlparse(location)
    if p.hostname and p.hostname.endswith(_evil):
        return location
    if location.startswith(f"//{_evil}") or location.startswith(f"/%5c{_evil}"):
        return location
    return None


def probe(args) -> dict:
    out = {"url": args["url"], "cases": [], "candidates": []}
    u = urllib.parse.urlparse(args["url"])
    params = [args["param"]] if args.get("param") else _PARAMS
    host = u.hostname or "target"
    for name in params:
        for form in _FORMS:
            val = form.format(evil=_evil, host=host)
            q = urllib.parse.urlparse(args["url"])
            pairs = urllib.parse.parse_qsl(q.query, keep_blank_values=True)
            pairs = [(k, val if k == name else v) for k, v in pairs]
            if name not in [k for k, _ in pairs]:
                pairs.append((name, val))
            url = urllib.parse.urlunparse(
                q._replace(query=urllib.parse.urlencode(pairs)))
            r = httpkit.request(url, method="GET",
                                headers=args.get("headers"),
                                timeout=args.get("timeout", 10),
                                follow=False)
            h = {k.lower(): v for k, v in (r.get("headers") or {}).items()}
            loc = h.get("location")
            hit = _hit(loc)
            rec = {"param": name, "form": val, "status": r.get("status"),
                   "location": loc}
            if hit:
                rec["candidate"] = True
                out["candidates"].append(rec)
            out["cases"].append(rec)
            if hit:
                break  # one winning form per parameter is enough evidence
    out["candidate_only"] = True
    if not out["candidates"]:
        out["note"] = ("no parameter moved Location off-site — record "
                       "negative; a 200-rendered meta refresh or JS "
                       "redirect needs a different read")
    return out


def _selftest() -> int:
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    class Red(BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            nxt = q.get("next", [""])[0]
            if nxt.startswith("https://evxl") or nxt.startswith("//evxl"):
                self.send_response(302)
                self.send_header("Location", nxt)
            else:
                self.send_response(200)
            self.end_headers()

        def log_message(self, *_a):
            pass

    srv = ThreadingHTTPServer(("127.0.0.1", 0), Red)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_address[1]}/login?next=/home"
    out = probe({"url": url, "param": "next", "headers": {}, "timeout": 10})
    srv.shutdown()
    assert out["candidates"] and out["candidates"][0]["param"] == "next", out
    print("redirect_probe selftest: ok")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url")
    ap.add_argument("--param", help="test only this parameter (default: sweep)")
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
