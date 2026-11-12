#!/usr/bin/env python3
"""bson_dump.py -- MongoDB .bson file to JSON.

A .bson handout (mongodb export, `bsondump` absent) is a sequence of
documents: int32 length, typed elements, NUL. Element types needed
for CTF triage are all decodable read-only: strings, docs, arrays,
binary, ObjectId, bool, datetime, int32/64, double, regex. Each doc
is decoded and flag-format-grepped; trailing bytes after the last
declared doc are reported, not silently dropped.

  python3 tools/forensics/bson_dump.py dump.bson
  python3 tools/forensics/bson_dump.py --selftest
"""
import argparse
import json
import re
import struct
import sys


def _cstr(b, i):
    j = b.index(b"\x00", i)
    return b[i:j].decode("utf-8", "replace"), j + 1


def _doc(b, i, depth=0):
    end = i + struct.unpack("<I", b[i:i + 4])[0]
    i += 4
    out = {}
    while i < end - 1:
        t = b[i]
        i += 1
        k, i = _cstr(b, i)
        if t == 0x01:
            out[k] = struct.unpack("<d", b[i:i + 8])[0]
            i += 8
        elif t in (0x02, 0x0D, 0x0E, 0x0F):       # string/code/symbol
            n = struct.unpack("<i", b[i:i + 4])[0]
            i += 4
            out[k] = b[i:i + n - 1].decode("utf-8", "replace")
            i += n
        elif t == 0x03:
            out[k], i = _doc(b, i, depth + 1)
        elif t == 0x04:
            v, i = _doc(b, i, depth + 1)
            out[k] = [v[x] for x in sorted(v, key=lambda s: int(s) if str(s).isdigit() else s)]
        elif t == 0x05:
            n = struct.unpack("<i", b[i:i + 4])[0]
            i += 4
            sub = b[i]
            i += 1
            out[k] = {"$binary": b[i:i + n].hex(), "subtype": sub}
            i += n
        elif t == 0x07:
            out[k] = {"$oid": b[i:i + 12].hex()}
            i += 12
        elif t == 0x08:
            out[k] = b[i] == 1
            i += 1
        elif t == 0x09:
            out[k] = {"$date_ms": struct.unpack("<q", b[i:i + 8])[0]}
            i += 8
        elif t == 0x0A:
            out[k] = None
        elif t == 0x0B:
            pat, i = _cstr(b, i)
            opt, i = _cstr(b, i)
            out[k] = {"$regex": pat, "$options": opt}
        elif t == 0x10:
            out[k] = struct.unpack("<i", b[i:i + 4])[0]
            i += 4
        elif t == 0x11:
            out[k] = {"$timestamp": struct.unpack("<Q", b[i:i + 8])[0]}
            i += 8
        elif t == 0x12:
            out[k] = struct.unpack("<q", b[i:i + 8])[0]
            i += 8
        elif t in (0x06, 0x0C, 0xFF, 0x7F):        # undef/dbref/min/max
            out[k] = {"$type": hex(t)}
            if t == 0x0C:
                i += 4 + 12
        else:
            out[k] = {"$unknown_type": hex(t), "at": i}
            break
    return out, end


def parse(data):
    docs, i, err = [], 0, None
    while i + 4 <= len(data):
        n = struct.unpack("<I", data[i:i + 4])[0]
        if n < 5 or i + n > len(data):
            err = "bad doc length %d at %d" % (n, i)
            break
        d, _ = _doc(data, i)
        docs.append(d)
        i += n
    out = {"documents": docs, "count": len(docs),
           "trailing": len(data) - i}
    if err:
        out["note"] = err
    hits = re.findall(r"[A-Za-z0-9_]+\{[^}]{3,}\}", json.dumps(docs))
    if hits:
        out["flag_strings"] = sorted(set(hits))
    return out


def _selftest():
    def elem(t, k, v):
        return bytes([t]) + k.encode() + b"\x00" + v
    body = (elem(0x02, "user", struct.pack("<i", 4) + b"bob\x00")
            + elem(0x10, "uid", struct.pack("<i", 7))
            + elem(0x02, "flag", struct.pack("<i", 15)
                   + b"flag{bson_doc}\x00")
            + elem(0x07, "_id", b"\x00" * 12))
    doc = struct.pack("<I", len(body) + 5) + body + b"\x00"
    d = parse(doc + b"TAIL")
    assert d["documents"][0]["user"] == "bob" and d["documents"][0]["uid"] == 7
    assert d["flag_strings"] == ["flag{bson_doc}"], d
    assert d["trailing"] == 4, d
    print("bson_dump selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="BSON dump to JSON")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("bson path required")
    print(json.dumps(parse(open(a.path, "rb").read()), indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
