#!/usr/bin/env python3
r"""net_dialog.py — scripted socket dialog for services that talk. Stdlib only.

`nc host port` captures a banner; the misc-constraint-puzzle and pwn skills
then have the agent hand-roll a socket loop to wait for a prompt, send a
line, and log each round. This tool is that loop, once: a step script of
wait:/send:/sleep:/dump: directives, a per-op timeout, a recv byte ceiling,
and a JSON transcript that records exactly what arrived — including a
timeout or a desync — so a negative is a measurement, not a hang.

    python3 tools/net_dialog.py HOST PORT                     # banner grab, like nc | head
    python3 tools/net_dialog.py HOST PORT --steps steps.txt   # scripted dialog
    python3 tools/net_dialog.py HOST PORT --send 'help\n' --recv-until '>'
    python3 tools/net_dialog.py --selftest

Steps file (or --steps 'w:> ; s:1\\n ; d:'): one directive per line —
  wait:LITERAL   receive until LITERAL appears (else step fails, dialog stops)
  send:DATA      write DATA (\n \r \t \xNN escapes honoured)
  sleep:SECONDS  pause
  dump           receive whatever is available right now (bounded)
"""
from __future__ import annotations

import argparse
import json
import re
import socket
import sys
import time

_RECV_CHUNK = 65536
_MAX_RECV = 1 << 20          # 1 MiB per wait — a bigger burst is a flood, not a prompt
_ESCAPES = {"\\n": b"\n", "\\r": b"\r", "\\t": b"\t", "\\0": b"\0", "\\e": b"\x1b"}


def _unescape(s: str) -> bytes:
    out = bytearray()
    i = 0
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s):
            two = s[i:i + 2]
            if two in _ESCAPES:
                out += _ESCAPES[two]
                i += 2
                continue
            if s[i + 1] == "x" and i + 3 < len(s):
                try:
                    out.append(int(s[i + 2:i + 4], 16))
                    i += 4
                    continue
                except ValueError:
                    pass
            if s[i + 1] == "\\":
                out.append(ord("\\"))
                i += 2
                continue
        out += s[i].encode()
        i += 1
    return bytes(out)


def _parse_steps(text: str):
    steps = []
    for raw in re.split(r"[;\n]", text):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line in ("dump",):
            steps.append(("dump", None))
            continue
        m = re.match(r"(wait|w|send|s|sleep)\s*:(.*)", line, re.S)
        if not m:
            raise ValueError(f"bad step {line!r} — expected wait:/send:/sleep:/dump")
        op, arg = m.group(1), m.group(2).strip()
        steps.append(({"w": "wait", "s": "send"}.get(op, op), arg))
    return steps


def _recv_until(sock, marker: bytes, timeout: float, buf: bytearray, transcript: dict):
    """Read until marker in buf or timeout. Returns matched bytes."""
    deadline = time.time() + timeout
    while True:
        idx = buf.find(marker)
        if idx != -1:
            got = bytes(buf[: idx + len(marker)])
            del buf[: idx + len(marker)]
            return got, True
        if len(buf) >= _MAX_RECV or time.time() >= deadline:
            got = bytes(buf)
            buf.clear()
            return got, False
        sock.settimeout(max(0.01, deadline - time.time()))
        try:
            chunk = sock.recv(_RECV_CHUNK)
        except socket.timeout:
            got = bytes(buf)
            buf.clear()
            return got, False
        if not chunk:  # peer closed
            got = bytes(buf)
            buf.clear()
            transcript["peer_closed"] = True
            return got, False
        buf.extend(chunk)


def run(host: str, port: int, steps, timeout: float, banner_only: bool) -> dict:
    tr = {"host": host, "port": port, "steps": []}
    buf = bytearray()
    try:
        with socket.create_connection((host, port), timeout=timeout) as sock:
            if banner_only:
                got, _ = _recv_until(sock, b"\x00-never", 1.0, buf, tr)  # time-bound grab
                tr["banner"] = got.decode("utf-8", "replace")
            for op, arg in steps:
                rec = {"op": op, "arg": arg}
                t0 = time.time()
                if op == "send":
                    data = _unescape(arg)
                    sock.sendall(data)
                    rec["sent"] = len(data)
                elif op == "wait":
                    got, ok = _recv_until(sock, _unescape(arg), timeout, buf, tr)
                    rec["matched"] = ok
                    rec["received"] = got.decode("utf-8", "replace")[-4096:]
                    if not ok:
                        rec["error"] = "timeout/close before marker"
                        tr["steps"].append(rec)
                        break
                elif op == "sleep":
                    time.sleep(min(float(arg), 30))
                elif op == "dump":
                    sock.settimeout(0.5)
                    try:
                        buf.extend(sock.recv(_RECV_CHUNK))
                    except (socket.timeout, BlockingIOError):
                        pass
                    got = bytes(buf[:_MAX_RECV])
                    del buf[: len(got)]
                    rec["received"] = got.decode("utf-8", "replace")[-4096:]
                rec["elapsed"] = round(time.time() - t0, 3)
                tr["steps"].append(rec)
    except OSError as exc:
        tr["error"] = f"{type(exc).__name__}: {exc}"
    tr["leftover"] = bytes(buf).decode("utf-8", "replace")[-4096:]
    return tr


def _selftest() -> int:
    import threading
    from http.server import ThreadingHTTPServer  # only for bind-free port pattern; use raw socket instead
    srv = socket.socket()
    srv.bind(("127.0.0.1", 0))
    srv.listen(1)
    port = srv.getsockname()[1]

    def peer():
        c, _ = srv.accept()
        c.sendall(b"menu>\n")
        data = c.recv(64)
        c.sendall(b"you said " + data + b"menu>\n")
        c.close()
        srv.close()

    threading.Thread(target=peer, daemon=True).start()
    tr = run("127.0.0.1", port, _parse_steps("wait:menu>\nsend:choice 1\\n\nwait:menu>"), 5.0, False)
    assert len(tr["steps"]) == 3, tr
    assert tr["steps"][0]["matched"] and "menu>" in tr["steps"][0]["received"]
    assert tr["steps"][1]["sent"] == 9
    assert tr["steps"][2]["matched"] and "you said choice 1" in tr["steps"][2]["received"]
    # timeout path is a recorded negative, not a hang
    srv2 = socket.socket(); srv2.bind(("127.0.0.1", 0)); srv2.listen(1)
    def peer2():
        c, _ = srv2.accept(); time.sleep(1.0); c.close(); srv2.close()
    threading.Thread(target=peer2, daemon=True).start()
    tr2 = run("127.0.0.1", srv2.getsockname()[1], _parse_steps("wait:never>"), 0.3, False)
    assert tr2["steps"][0]["matched"] is False and "error" in tr2["steps"][0]
    print("net_dialog selftest: ok")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("host", nargs="?")
    ap.add_argument("port", nargs="?", type=int)
    ap.add_argument("--steps", help="step script: path to a file or the script itself")
    ap.add_argument("--send", help="one-shot: send this (escapes honoured)")
    ap.add_argument("--recv-until", help="one-shot: wait for this marker first")
    ap.add_argument("--timeout", type=float, default=5.0)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if not args.host or not args.port:
        ap.print_help()
        return 2
    steps = []
    if args.steps:
        import os
        text = open(args.steps, encoding="utf-8").read() if os.path.exists(args.steps) else args.steps
        try:
            steps = _parse_steps(text)
        except ValueError as exc:
            print(json.dumps({"error": str(exc)}))
            return 2
    elif args.send or args.recv_until:
        if args.recv_until:
            steps.append(("wait", args.recv_until))
        if args.send:
            steps.append(("send", args.send))
        steps.append(("dump", None))
    tr = run(args.host, args.port, steps, args.timeout, banner_only=not steps)
    print(json.dumps(tr, indent=1))
    return 0 if "error" not in tr else 1


if __name__ == "__main__":
    sys.exit(main())
