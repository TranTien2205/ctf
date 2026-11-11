#!/usr/bin/env python3
"""proto_decode.py -- decode a protobuf wire blob without the .proto.

CTF services increasingly speak raw protobuf (gRPC, custom IPC) and
protoc/protoc-gen are absent here. This walks field keys as varints:
wire 0 varint, 1 64-bit, 2 length-delimited, 5 32-bit; type-2 fields
are reported as utf8 strings when printable, hex otherwise, and are
also parsed as nested messages when they decode cleanly.

  python3 tools/proto_decode.py blob.bin
  python3 tools/proto_decode.py blob.bin --hex
  python3 tools/proto_decode.py --selftest

JSON out per field: number, wire type, value, and guessed role
(string / bytes / nested). Depth capped at 8; truncated tails are
reported, not silently dropped.
"""
import argparse
import json
import sys


def varint(b, i):
    v, s = 0, 0
    while i < len(b):
        c = b[i]
        i += 1
        v |= (c & 0x7F) << s
        if not c & 0x80:
            return v, i
        s += 7
    return None, i


def _txt(b):
    try:
        t = b.decode("utf-8")
    except UnicodeDecodeError:
        return None
    return t if all(32 <= ord(c) < 127 or c in "\r\n\t" for c in t) \
        else None


def decode(b, depth=0):
    fields, i = [], 0
    while i < len(b):
        key, i2 = varint(b, i)
        if key is None or key == 0:
            fields.append({"error": "bad field key", "offset": i})
            break
        num, wt = key >> 3, key & 7
        f = {"field": num, "wire": wt, "offset": i}
        i = i2
        if wt == 0:
            v, i = varint(b, i)
            if v is None:
                f["error"] = "truncated varint"
            else:
                f["value"] = v
        elif wt == 1:
            f["value"] = b[i:i + 8].hex()
            i += 8
        elif wt == 5:
            f["value"] = b[i:i + 4].hex()
            i += 4
        elif wt == 2:
            ln, i = varint(b, i)
            if ln is None or i + ln > len(b):
                f["error"] = "truncated length-delimited"
                fields.append(f)
                break
            raw = b[i:i + ln]
            i += ln
            t = _txt(raw)
            if t is not None:
                f["value"], f["role"] = t, "string"
            else:
                f["value"], f["role"] = raw.hex(), "bytes"
            if depth < 8 and len(raw) >= 2:
                nested = decode(raw, depth + 1)
                if nested and all("error" not in x for x in nested) \
                        and nested[-1].get("end") == len(raw):
                    for x in nested:
                        x.pop("end", None)
                    f["nested"] = nested
                    f["role"] = "nested"
        else:
            f["error"] = f"wire type {wt} unsupported (groups skipped)"
            fields.append(f)
            break
        fields.append(f)
    for f in fields:
        f["end"] = i
    return fields


def _selftest():
    # field1 varint=150, field2 string "flag{ok}", field3 nested(f1=7)
    msg = bytes([0x08, 0x96, 0x01,
                 0x12, 0x08]) + b"flag{ok}" + bytes(
                     [0x1A, 0x02, 0x08, 0x07])
    d = decode(msg)
    assert d[0]["value"] == 150 and d[1]["value"] == "flag{ok}", d
    assert d[2]["role"] == "nested" and \
        d[2]["nested"][0]["value"] == 7, d[2]
    # truncated: claims 10 bytes, gives 3
    d2 = decode(bytes([0x12, 0x0A]) + b"abc")
    assert "error" in d2[-1], d2
    print("proto_decode selftest: ok")


def main():
    ap = argparse.ArgumentParser(
        description="decode protobuf wire without .proto")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--hex", help="hex string instead of a file")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    data = bytes.fromhex(a.hex) if a.hex else \
        open(a.path, "rb").read() if a.path else None
    if data is None:
        ap.error("a path or --hex is required")
    fields = decode(data)
    for f in fields:
        f.pop("end", None)
    print(json.dumps({"size": len(data), "fields": fields}, indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
