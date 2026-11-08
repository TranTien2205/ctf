#!/usr/bin/env python3
"""cmdi_probe.py — command-injection channel matrix for one parameter.

The web-command-injection skill's confirm is fixed: one benign separator
carrying a command whose output is unmistakable, plus a timing variant as
the fallback channel. This fires that matrix through httpkit — separators
(`; | $( )` backtick `&& ||` newline) each wrapped around an echo marker,
then bounded sleep forms — and measures each response against the
baseline (status, length, body signature, elapsed). It reports which
*channels* showed signal: output-marker (with the verbatim excerpt),
time (repeatable delta), or error — channel CANDIDATES, never a finding;
the class's own confirming probe still has to run.

    python3 tools/web/cmdi_probe.py --url 'http://h/ping?host=127.0.0.1' --param host
    python3 tools/web/cmdi_probe.py --url URL --body 'host={M}' --method POST
    python3 tools/web/cmdi_probe.py --selftest
"""
from __future__ import annotations

import argparse
import re
import sys
import time
import urllib.parse

import httpkit

_MARK = "CMDMK7x"
_SLEEP_S = 2.0
_TIME_MIN = 1.5

_OUT = [f";echo {_MARK}", f"|echo {_MARK}", "$(echo " + _MARK + ")",
        f"`echo {_MARK}`", f"&&echo {_MARK}", f"||echo {_MARK}", f"\necho {_MARK}"]
_TIME = [f";sleep {int(_SLEEP_S)}", f"|sleep {int(_SLEEP_S)}",
         f"$(sleep {int(_SLEEP_S)})", f"`sleep {int(_SLEEP_S)}`",
         f"&&sleep {int(_SLEEP_S)}", f"||sleep {int(_SLEEP_S)}"]
_ERR = re.compile(r"(?:sh: |bash: |cmd\.exe|not recognized|syntax error|"
                  r"cannot find|No such file|/bin/(?:ba)?sh)", re.I)


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


def _text(r):
    b = r.get("body", "")
    return b.decode("utf-8", "replace") if isinstance(b, bytes) else (b or "")


def detect(args) -> dict:
    base_val = args.get("value", "127.0.0.1")
    base = _fire(args, base_val)
    b = _sig(base)
    out = {"url": args["url"], "param": args.get("param"), "baseline": b, "cases": []}

    res = {}
    for payload in _OUT + _TIME:
        label = "out" if payload in _OUT else "time"
        r = _fire(args, base_val + payload)
        s = _sig(r)
        body = _text(r)
        has_mark = _MARK in body
        err = _ERR.search(body)
        i = body.find(_MARK)
        rec = {"payload": payload, "kind": label, **s,
               "marker_echo": has_mark,
               "excerpt": body[max(0, i - 30):i + len(_MARK) + 30] if has_mark else None,
               "err_text": bool(err)}
        res[payload] = rec
        out["cases"].append(rec)

    chan = []
    marked = [c for c in res.values() if c["marker_echo"]]
    if marked and _MARK not in _text(base):
        chan.append({"channel": "output", "signal": "echo marker returned",
                     "payload": marked[0]["payload"], "excerpt": marked[0]["excerpt"]})
    slow = [c for c in res.values() if c["kind"] == "time"
            and c["elapsed"] and c["elapsed"] >= _TIME_MIN and b["elapsed"] < _TIME_MIN]
    if slow:
        chan.append({"channel": "time", "signal":
                     f"{len(slow)} sleep form(s) took ≥{_TIME_MIN}s vs baseline {b['elapsed']}s",
                     "payload": slow[0]["payload"]})
    errs = [c for c in res.values() if c["err_text"]]
    if errs and not _ERR.search(_text(base)):
        chan.append({"channel": "error", "signal": "shell error text on injection only",
                     "payload": errs[0]["payload"]})
    out["channels"] = chan
    out["candidate_only"] = True
    if not chan:
        out["note"] = "no separator carried a signal — record inconclusive, not clean"
    return out


def _selftest() -> int:
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    class Cmd(BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            v = q.get("host", [""])[0]
            body, code = b"ping ok", 200
            if f"echo {_MARK}" in v:
                body += _MARK.encode()
            elif "sleep" in v:
                time.sleep(_SLEEP_S)
            self.send_response(code)
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_a):
            pass

    srv = ThreadingHTTPServer(("127.0.0.1", 0), Cmd)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_address[1]}/?host=127.0.0.1"
    out = detect({"url": url, "param": "host", "method": "GET", "timeout": 15})
    srv.shutdown()
    chans = {c["channel"] for c in out["channels"]}
    assert "output" in chans and "time" in chans, out
    print("cmdi_probe selftest: ok")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url")
    ap.add_argument("--param")
    ap.add_argument("--value", default="127.0.0.1", help="known-good baseline value")
    ap.add_argument("--method", default="GET", choices=["GET", "POST"])
    ap.add_argument("--body", help="POST body; {M} marks the injection slot")
    ap.add_argument("--headers", nargs="*")
    ap.add_argument("--timeout", type=float, default=15)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if not args.url or not (args.param or args.body or "{M}" in args.url):
        ap.print_help()
        return 2
    a = vars(args) | {"headers": httpkit.parse_headers(args.headers)}
    httpkit.jprint(detect(a))
    return 0


if __name__ == "__main__":
    sys.exit(main())
