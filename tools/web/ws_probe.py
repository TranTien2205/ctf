#!/usr/bin/env python3
"""ws_probe.py — minimal RFC 6455 WebSocket probe. Stdlib only.

The web-websocket skill teaches what to test on a live ws channel; nothing
else in this tree can open one. This tool performs the handshake, verifies
the accept hash, optionally sends one masked text frame, and reads reply
frames. Every read is timeout- and size-bounded; the tool never loops a
frame flood — one message in, a bounded number of frames out.

It reports what happened on the wire. Whether a foreign-Origin handshake
or an unauthenticated channel is a *finding* is the agent's call — quote
the captured frames verbatim as evidence.

Usage:
  python tools/web/ws_probe.py URL [--message TEXT] [--origin URL]
                                   [--headers 'K: v;K2: v2'] [--timeout N]
  python tools/web/ws_probe.py --selftest
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import socket
import ssl
import struct
import sys
import urllib.parse

_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
_MAX_FRAME = 1 << 20      # 1 MiB per frame — a bigger server frame is not CTF scale
_MAX_FRAMES = 16          # read at most this many reply frames
_MAX_HANDSHAKE = 65536    # bytes of handshake response we will read


def _ws_url(url: str):
    u = urllib.parse.urlparse(url)
    if u.scheme not in ("ws", "wss", "http", "https"):
        raise ValueError(f"scheme {u.scheme!r} is not ws(s)/http(s)")
    use_tls = u.scheme in ("wss", "https")
    port = u.port or (443 if use_tls else 80)
    path = u.path or "/"
    if u.query:
        path += "?" + u.query
    return u.hostname, port, use_tls, path


def _connect(host: str, port: int, use_tls: bool, timeout: float):
    raw = socket.create_connection((host, port), timeout=timeout)
    if not use_tls:
        return raw
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE  # labs and CTF boxes ship self-signed certs
    return ctx.wrap_socket(raw, server_hostname=host)


def _recv_until(sock, marker: bytes, limit: int) -> bytes:
    buf = b""
    while marker not in buf and len(buf) < limit:
        chunk = sock.recv(4096)
        if not chunk:
            break
        buf += chunk
    return buf


def _recv_exact(sock, n: int) -> bytes:
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("socket closed mid-frame")
        buf += chunk
    return buf


def _send_text(sock, payload: bytes):
    mask = os.urandom(4)
    n = len(payload)
    if n < 126:
        head = struct.pack("!BB", 0x81, 0x80 | n)
    elif n < 65536:
        head = struct.pack("!BBH", 0x81, 0x80 | 126, n)
    else:
        head = struct.pack("!BBQ", 0x81, 0x80 | 127, n)
    masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
    sock.sendall(head + mask + masked)


def _read_frame(sock):
    """One frame -> (opcode, payload). Raises on oversize/close."""
    b1, b2 = _recv_exact(sock, 2)
    opcode = b1 & 0x0F
    masked = b2 & 0x80
    n = b2 & 0x7F
    if n == 126:
        (n,) = struct.unpack("!H", _recv_exact(sock, 2))
    elif n == 127:
        (n,) = struct.unpack("!Q", _recv_exact(sock, 8))
    if n > _MAX_FRAME:
        raise ConnectionError(f"frame of {n} bytes exceeds {_MAX_FRAME} bound")
    mask = _recv_exact(sock, 4) if masked else b""
    payload = _recv_exact(sock, n) if n else b""
    if masked:
        payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
    return opcode, payload


def probe(url: str, message: str | None = None, origin: str | None = None,
          headers: dict | None = None, timeout: float = 10.0) -> dict:
    host, port, use_tls, path = _ws_url(url)
    key = base64.b64encode(os.urandom(16)).decode()
    lines = [
        f"GET {path} HTTP/1.1",
        f"Host: {host}:{port}",
        "Upgrade: websocket",
        "Connection: Upgrade",
        f"Sec-WebSocket-Key: {key}",
        "Sec-WebSocket-Version: 13",
    ]
    if origin:
        lines.append(f"Origin: {origin}")
    for k, v in (headers or {}).items():
        lines.append(f"{k}: {v}")
    wire = "\r\n".join(lines) + "\r\n\r\n"

    out = {"url": url, "host": host, "port": port, "tls": use_tls,
           "origin_sent": origin}
    sock = None
    try:
        sock = _connect(host, port, use_tls, timeout)
        sock.settimeout(timeout)
        sock.sendall(wire.encode())
        raw = _recv_until(sock, b"\r\n\r\n", _MAX_HANDSHAKE)
    except Exception as exc:  # network failure is a recorded result
        out.update(verdict="no handshake (transport failure)", error=str(exc))
        return out

    head, _, rest = raw.partition(b"\r\n\r\n")
    hlines = head.decode("latin-1", "replace").split("\r\n")
    status = int(hlines[0].split()[1]) if len(hlines[0].split()) > 1 else 0
    resp_headers = {}
    for line in hlines[1:]:
        if ":" in line:
            k, v = line.split(":", 1)
            resp_headers[k.strip().lower()] = v.strip()
    out.update(handshake_status=status, handshake_headers=resp_headers)

    expect = base64.b64encode(
        hashlib.sha1((key + _GUID).encode()).digest()).decode()
    accept = resp_headers.get("sec-websocket-accept", "")
    if status != 101:
        out["verdict"] = ("no ws channel" if status else
                          f"rejected ({status})")
        return out
    if accept != expect:
        out["verdict"] = "101 but bad Sec-WebSocket-Accept (not a real ws server)"
        return out

    # leftover bytes after the handshake may already be the first frame
    pending = rest
    frames = []
    try:
        if message is not None:
            _send_text(sock, message.encode())
        while len(frames) < _MAX_FRAMES:
            if pending:
                # serve the buffered bytes first via a tiny shim
                class _Buf:
                    def __init__(self, s, first):
                        self._s, self._buf = s, bytearray(first)
                    def recv(self, n):
                        if self._buf:
                            take, self._buf = bytes(self._buf[:n]), self._buf[n:]
                            return take
                        return self._s.recv(n)
                sock_r = _Buf(sock, pending)
                opcode, payload = _read_frame(sock_r)
                pending = b""
                frames.append({"opcode": opcode, "len": len(payload),
                               "text": payload[:4000].decode("utf-8", "replace")})
            else:
                opcode, payload = _read_frame(sock)
                if opcode == 0x8:
                    frames.append({"opcode": opcode, "close": True})
                    break
                if opcode == 0x9:  # ping -> pong, keep reading
                    frames.append({"opcode": opcode, "ping": True})
                    continue
                frames.append({"opcode": opcode, "len": len(payload),
                               "text": payload[:4000].decode("utf-8", "replace")})
    except (socket.timeout, TimeoutError):
        pass
    except ConnectionError as exc:
        out["closed"] = str(exc)

    out["frames"] = frames
    if origin and origin != f"http{'s' if use_tls else ''}://{host}":
        out["verdict"] = ("foreign-Origin handshake accepted — check whether "
                          "the channel then serves another context's data")
    else:
        out["verdict"] = "ws channel confirmed"
    if not frames:
        out["note"] = ("handshake accepted but no frames read; the server may "
                       "wait for a specific first message — check the "
                       "front-end JS for the expected protocol")
    return out


def _selftest() -> int:
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    key_holder = {}

    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path != "/ws":
                self.send_response(404); self.end_headers(); return
            key = self.headers.get("Sec-WebSocket-Key", "")
            accept = base64.b64encode(hashlib.sha1(
                (key + _GUID).encode()).digest()).decode()
            self.send_response(101, "Switching Protocols")
            self.send_header("Upgrade", "websocket")
            self.send_header("Connection", "Upgrade")
            self.send_header("Sec-WebSocket-Accept", accept)
            self.end_headers()
            # read one masked text frame from raw socket, echo it back
            class _RF:
                def __init__(self, f):
                    self._f = f
                def recv(self, n):
                    return self._f.read(n)
            try:
                opcode, payload = _read_frame(_RF(self.rfile))
                if opcode == 0x1:
                    body = payload
                    head = struct.pack("!BB", 0x81, len(body)) \
                        if len(body) < 126 else b""
                    if head:
                        self.wfile.write(head + body)
                        self.wfile.flush()
            except Exception:
                pass
            self.close_connection = True

        def log_message(self, *a):
            pass

    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"ws://127.0.0.1:{srv.server_address[1]}/ws"
    ok = True
    try:
        out = probe(base, message="marker-41", timeout=5)
        ok &= out["verdict"] == "ws channel confirmed"
        ok &= out["handshake_status"] == 101
        ok &= any(f.get("text") == "marker-41" for f in out["frames"])
        out2 = probe(base, origin="https://evil.example", timeout=5)
        ok &= "foreign-Origin" in out2["verdict"]
        out3 = probe(f"ws://127.0.0.1:{srv.server_address[1]}/", timeout=5)
        ok &= out3["verdict"].startswith("rejected") or \
            "no ws" in out3["verdict"]
    finally:
        srv.shutdown()
    print(json.dumps({"selftest": "pass" if ok else "fail"}))
    return 0 if ok else 1


def main() -> int:
    p = argparse.ArgumentParser(description="WebSocket handshake + frame probe")
    p.add_argument("url", nargs="?")
    p.add_argument("--message", help="one text frame to send after the handshake")
    p.add_argument("--origin", help="Origin header for cross-site checks")
    p.add_argument("--headers", help="'Name: v;Name2: v2' extra headers (auth)")
    p.add_argument("--timeout", type=float, default=10.0)
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args()
    if args.selftest:
        return _selftest()
    if not args.url:
        p.error("URL required (or --selftest)")
    headers = {}
    for pair in (args.headers or "").split(";"):
        if ":" in pair:
            k, v = pair.split(":", 1)
            headers[k.strip()] = v.strip()
    try:
        out = probe(args.url, message=args.message, origin=args.origin,
                    headers=headers, timeout=args.timeout)
    except ValueError as exc:
        out = {"verdict": "no handshake (bad URL)", "error": str(exc)}
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
