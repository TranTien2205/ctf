#!/usr/bin/env python3
"""oob_listener.py — out-of-band callback receiver. Stdlib only.

Half of every blind technique the skills teach needs a place for the target
to call home: blind XXE/SSRF hits, exfil in a Referer or User-Agent, a bot
navigation beacon, an OOB SQLi/XXE fetch. Nothing else in this tree opens a
socket that *receives*. This does, and it records every hit as a JSONL line
so each payload can carry its own canary path and hits are correlated by
token — not eyeballed out of a scrolling http.server log.

Field notes warn about the trap this tool exists to defeat: a curl smoke
test passes while the app silently swallows the real request, and 'no
callback' reads as 'exploit failed'. Record hits; let the agent decide what
a hit or a silence means.

Usage:
  python tools/web/oob_listener.py serve --port 8000 [--seconds N] [--log hits.jsonl]
  python tools/web/oob_listener.py hits --log hits.jsonl [--tail N]
  python tools/web/oob_listener.py canary --base http://10.0.0.5:8000 [--name xxe]
  python tools/web/oob_listener.py --selftest
"""
from __future__ import annotations

import argparse
import json
import secrets
import sys
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

_BODY_CAP = 65536       # record at most this many body bytes per hit
_MAX_HITS = 4096        # stop counting new hits past this — a flood is not signal


def _record_hit(log_path: str, handler: BaseHTTPRequestHandler, body: bytes) -> None:
    rec = {
        "ts": round(time.time(), 3),
        "client": handler.client_address[0],
        "method": handler.command,
        "path": handler.path,
        "headers": {k: v for k, v in handler.headers.items()},
        "body_len": len(body),
        "body": body[:_BODY_CAP].decode("utf-8", "replace"),
    }
    try:
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec) + "\n")
    except OSError as exc:  # a lost hit must not kill the listener
        print(f"hit not recorded: {exc}", file=sys.stderr)


def _make_handler(log_path: str, counter: list):
    class Handler(BaseHTTPRequestHandler):
        def _handle(self):
            counter[0] += 1
            if counter[0] > _MAX_HITS:
                self.send_response(429)
                self.end_headers()
                return
            n = int(self.headers.get("Content-Length") or 0)
            body = self.rfile.read(min(n, _BODY_CAP)) if n else b""
            _record_hit(log_path, self, body)
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Content-Length", "3")
            self.end_headers()
            self.wfile.write(b"ok\n")

        do_GET = do_POST = do_PUT = do_DELETE = do_PATCH = do_OPTIONS = do_HEAD = _handle

        def log_message(self, *_a):  # hits live in the JSONL log, not stderr
            pass

    return Handler


def cmd_serve(args) -> int:
    counter = [0]
    server = ThreadingHTTPServer((args.bind, args.port), _make_handler(args.log, counter))
    server.timeout = 0.5
    port = server.server_address[1]
    print(f"listening on {args.bind}:{port} — embed http://<reachable-ip>:{port}/cb/<token> in payloads; hits -> {args.log}",
          file=sys.stderr)
    deadline = time.time() + args.seconds if args.seconds else None
    try:
        while deadline is None or time.time() < deadline:
            server.handle_request()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    print(f"{counter[0]} hit(s) recorded in {args.log}", file=sys.stderr)
    return 0


def cmd_hits(args) -> int:
    try:
        lines = open(args.log, encoding="utf-8").read().splitlines()
    except OSError:
        print(json.dumps({"hits": 0, "log": args.log, "note": "no log yet"}))
        return 0
    recs = []
    for line in lines[-args.tail:]:
        try:
            recs.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    out = {
        "hits": len(lines),
        "log": args.log,
        "recent": [
            {"ts": r.get("ts"), "client": r.get("client"), "method": r.get("method"),
             "path": r.get("path"), "user_agent": r.get("headers", {}).get("User-Agent"),
             "referer": r.get("headers", {}).get("Referer"), "body_len": r.get("body_len")}
            for r in recs
        ],
    }
    print(json.dumps(out, indent=1))
    return 0


def cmd_canary(args) -> int:
    token = f"{args.name or 'hit'}-{secrets.token_hex(4)}"
    print(f"{args.base.rstrip('/')}/cb/{token}")
    return 0


def _selftest() -> int:
    import tempfile, os
    with tempfile.TemporaryDirectory() as td:
        log = os.path.join(td, "hits.jsonl")
        counter = [0]
        server = ThreadingHTTPServer(("127.0.0.1", 0), _make_handler(log, counter))
        port = server.server_address[1]
        t = threading.Thread(target=server.handle_request, daemon=True)
        t.start()
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/cb/test-abc?k=v",
            data=b"p", method="POST",
            headers={"User-Agent": "oob-selftest", "Referer": "http://victim/x"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            assert resp.status == 200
        t.join(timeout=5)
        server.server_close()
        rec = json.loads(open(log, encoding="utf-8").read().strip())
        assert rec["method"] == "POST" and rec["path"] == "/cb/test-abc?k=v"
        assert rec["headers"]["Referer"] == "http://victim/x" and rec["body"] == "p"
        assert rec["client"] == "127.0.0.1"
    print("oob_listener selftest: ok")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd")
    s = sub.add_parser("serve")
    s.add_argument("--port", type=int, default=8000)
    s.add_argument("--bind", default="0.0.0.0")
    s.add_argument("--seconds", type=float, default=0, help="0 = until Ctrl-C")
    s.add_argument("--log", default="oob_hits.jsonl")
    s.set_defaults(fn=cmd_serve)
    h = sub.add_parser("hits")
    h.add_argument("--log", default="oob_hits.jsonl")
    h.add_argument("--tail", type=int, default=20)
    h.set_defaults(fn=cmd_hits)
    c = sub.add_parser("canary")
    c.add_argument("--base", required=True)
    c.add_argument("--name")
    c.set_defaults(fn=cmd_canary)
    args = p.parse_args(argv)
    if getattr(args, "fn", None):
        return args.fn(args)
    return _selftest() if argv == ["--selftest"] or len(sys.argv) > 1 and sys.argv[1] == "--selftest" else p.print_help() or 2


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    sys.exit(main())
