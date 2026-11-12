#!/usr/bin/env python3
"""msgpack_read.py -- MessagePack blob to JSON.

MessagePack shows up in misc handouts and web service traffic
(ws://binary, Redis sessions, Flask-cache). `msgpack` the module is
not always installed; the format is a tag-per-value walk the stdlib
does fine. Decodes nil/bool/int/float/str/bin/array/map/ext and
reports trailing bytes; flag-format-greps every decoded string.

  python3 tools/msgpack_read.py blob.msgpack
  python3 tools/msgpack_read.py --hex 81a475736572a3...
  python3 tools/msgpack_read.py --selftest
"""
import argparse
import json
import re
import struct
import sys


def _u(b, i, n, f):
    return struct.unpack(f, b[i:i + n])[0], i + n


def parse(b, i=0, depth=0):
    if depth > 64:
        raise ValueError("depth guard")
    t = b[i]
    i += 1
    if t <= 0x7F:                                    # positive fixint
        return t, i
    if t >= 0xE0:                                    # negative fixint
        return t - 0x100, i
    if 0x80 <= t <= 0x8F:                            # fixmap
        return _map(b, i, t & 0xF, depth)
    if 0x90 <= t <= 0x9F:                            # fixarray
        return _arr(b, i, t & 0xF, depth)
    if 0xA0 <= t <= 0xBF:                            # fixstr
        n = t & 0x1F
        return b[i:i + n].decode("utf-8", "replace"), i + n
    if t == 0xC0:
        return None, i
    if t == 0xC2:
        return False, i
    if t == 0xC3:
        return True, i
    if t in (0xC4, 0xC5, 0xC6):                      # bin 8/16/32
        n, i = _u(b, i, {0xC4: 1, 0xC5: 2, 0xC6: 4}[t],
                {0xC4: ">B", 0xC5: ">H", 0xC6: ">I"}[t])
        return {"$bin": b[i:i + n].hex()}, i + n
    if t in (0xC7, 0xC8, 0xC9):                      # ext 8/16/32
        n, i = _u(b, i, {0xC7: 1, 0xC8: 2, 0xC9: 4}[t],
                {0xC7: ">B", 0xC8: ">H", 0xC9: ">I"}[t])
        ty = struct.unpack(">b", b[i:i + 1])[0]
        i += 1
        return {"$ext": {"type": ty, "data": b[i:i + n].hex()}}, i + n
    if t == 0xCA:
        v, i = _u(b, i, 4, ">f")
        return v, i
    if t == 0xCB:
        v, i = _u(b, i, 8, ">d")
        return v, i
    if t in (0xCC, 0xCD, 0xCE, 0xCF):                # u8/u16/u32/u64
        return _u(b, i, {0xCC: 1, 0xCD: 2, 0xCE: 4, 0xCF: 8}[t],
                {0xCC: ">B", 0xCD: ">H", 0xCE: ">I", 0xCF: ">Q"}[t])
    if t in (0xD0, 0xD1, 0xD2, 0xD3):                # i8/i16/i32/i64
        return _u(b, i, {0xD0: 1, 0xD1: 2, 0xD2: 4, 0xD3: 8}[t],
                {0xD0: ">b", 0xD1: ">h", 0xD2: ">i", 0xD3: ">q"}[t])
    if t in (0xD4, 0xD5, 0xD6, 0xD7, 0xD8):          # fixext 1/2/4/8/16
        n = {0xD4: 1, 0xD5: 2, 0xD6: 4, 0xD7: 8, 0xD8: 16}[t]
        ty = struct.unpack(">b", b[i:i + 1])[0]
        i += 1
        return {"$ext": {"type": ty, "data": b[i:i + n].hex()}}, i + n
    if t in (0xD9, 0xDA, 0xDB):                      # str 8/16/32
        n, i = _u(b, i, {0xD9: 1, 0xDA: 2, 0xDB: 4}[t],
                {0xD9: ">B", 0xDA: ">H", 0xDB: ">I"}[t])
        return b[i:i + n].decode("utf-8", "replace"), i + n
    if t in (0xDC, 0xDD):                            # array 16/32
        n, i = _u(b, i, 2 if t == 0xDC else 4,
                ">H" if t == 0xDC else ">I")
        return _arr(b, i, n, depth)
    if t in (0xDE, 0xDF):                            # map 16/32
        n, i = _u(b, i, 2 if t == 0xDE else 4,
                ">H" if t == 0xDE else ">I")
        return _map(b, i, n, depth)
    raise ValueError("unknown tag 0x%02x at %d" % (t, i - 1))


def _arr(b, i, n, depth):
    out = []
    for _ in range(n):
        v, i = parse(b, i, depth + 1)
        out.append(v)
    return out, i


def _map(b, i, n, depth):
    out = {}
    for _ in range(n):
        k, i = parse(b, i, depth + 1)
        v, i = parse(b, i, depth + 1)
        out[str(k) if isinstance(k, (dict, list)) else k] = v
    return out, i


def analyze(data):
    vals, i = [], 0
    try:
        while i < len(data):
            v, i = parse(data, i)
            vals.append(v)
    except (ValueError, IndexError, struct.error) as exc:
        return {"values": vals, "error": "%s at %d" % (exc, i),
                "consumed": i}
    hits = re.findall(r"[A-Za-z0-9_]+\{[^}]{3,}\}", json.dumps(vals))
    out = {"values": vals, "count": len(vals)}
    if hits:
        out["flag_strings"] = sorted(set(hits))
    return out


def _selftest():
    blob = (b"\x82"                                  # map of 2
            b"\xa4user\xa3bob"                       # fixstr/fixstr
            b"\xa4list\x93\x01\x02\xc3"              # array [1,2,true]
            + b"\xa9flag{x}ok"                       # fixstr 9
            + b"\x81\xa5outer\xacflag{msg_ok}")
    d = analyze(blob)
    assert d["values"][0]["user"] == "bob", d
    assert d["values"][0]["list"] == [1, 2, True]
    assert "flag{msg_ok}" in d["flag_strings"], d
    print("msgpack_read selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="MessagePack decode")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--hex", help="hex string instead of a file")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if a.hex:
        data = bytes.fromhex(a.hex)
    elif a.path:
        data = open(a.path, "rb").read()
    else:
        ap.error("path or --hex required")
    print(json.dumps(analyze(data), indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
