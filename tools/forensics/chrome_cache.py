#!/usr/bin/env python3
"""chrome_cache.py -- Chrome/Chromium SimpleCache entry recovery.

Chromium's SimpleCache keeps response bodies in `data_1`/`data_2`/
`data_3` files under `Cache/Cache_Data`. The entry layout (stable in
Chromium since the format shipped) is:

  SimpleFileHeader:  magic(8=0xfcfb6d88aa11d0f1) flags(4)
                     key_length(4) key_hash(4) header_size(4)
  stream 0 data (response headers)
  SimpleFileEOF:     magic(8=0xf4fa6f45970d41d8) flags_crc(4)
                     data_size(4) [sha256(32) when flag bit 4 set]
  stream 1 data (the body)
  SimpleFileEOF for stream 1
  key (key_length bytes -- the URL)

This tool walks a data_* file for entry magic, finds each stream's
EOF record to locate bodies and keys honestly, and can extract a
stream. It never guesses a key: the key bytes come from after the
last EOF record, where the format puts them.

  python3 tools/forensics/chrome_cache.py Cache_Data/data_1 --list
  python3 tools/forensics/chrome_cache.py data_1 --stream N --to out.bin
  python3 tools/forensics/chrome_cache.py --selftest
"""
import argparse
import json
import struct
import sys

INIT_MAGIC = 0xFCFB6D88AA11D0F1
EOF_MAGIC = 0xF4FA6F45970D41D8
FLAG_HAS_SHA256 = 0x4


def _eofs(data, start, end):
    """yield (pos, flags, data_size) for each EOF record in [start,end)."""
    p = start
    needle = struct.pack("<Q", EOF_MAGIC)
    while True:
        p = data.find(needle, p, end)
        if p < 0 or p + 16 > end:
            return
        flags, size = struct.unpack("<II", data[p + 8:p + 16])
        yield p, flags, size
        p += 16 + (32 if flags & FLAG_HAS_SHA256 else 0)


def entries(data):
    out = []
    needle = struct.pack("<Q", INIT_MAGIC)
    p = 0
    marks = []
    while True:
        p = data.find(needle, p)
        if p < 0:
            break
        marks.append(p)
        p += 8
    for n, off in enumerate(marks):
        end = marks[n + 1] if n + 1 < len(marks) else len(data)
        if off + 24 > end:
            continue
        _m, flags, klen, khash, hsize = struct.unpack(
            "<QIIII", data[off:off + 24])
        ent = {"offset": off, "key_length": klen, "key_hash": khash,
               "flags": flags, "streams": []}
        eos = list(_eofs(data, off + 24, end))
        if len(eos) >= 2:
            for pos, eflags, size in eos[:2]:
                body = data[pos - size:pos]
                ent["streams"].append(
                    {"eof_at": pos, "size": size,
                     "preview": body[:48].decode("utf-8", "replace")})
            last_pos, last_fl, _ = eos[-1]
            rec_len = 16 + (32 if last_fl & FLAG_HAS_SHA256 else 0)
            key = data[last_pos + rec_len:last_pos + rec_len + klen]
            ent["key"] = key.decode("utf-8", "replace")
        else:
            ent["note"] = "incomplete entry: %d eof records" % len(eos)
        out.append(ent)
    return out


def _selftest():
    key = b"https://ex.test/flag.png"
    s0 = b"HTTP/1.1 200 OK\r\nContent-Type: image/png\r\n\r\n"
    s1 = b"PNGDATA:flag{cache_entry}"
    ent = (struct.pack("<QIIII", INIT_MAGIC, 0, len(key), 0xBEEF, 0)
           + s0 + struct.pack("<QII", EOF_MAGIC, 0, len(s0))
           + s1 + struct.pack("<QII", EOF_MAGIC, 0, len(s1))
           + key)
    ents = entries(ent + b"\x00" * 64 + ent)
    assert len(ents) == 2, ents
    e = ents[0]
    assert e["key"] == key.decode(), e
    assert e["streams"][0]["size"] == len(s0)
    assert e["streams"][1]["preview"].startswith("PNGDATA:flag{")
    print("chrome_cache selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="Chrome SimpleCache reader")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--stream", type=int, metavar="N",
                    help="dump stream-1 body of entry N to stdout file")
    ap.add_argument("--to", default=".")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("path required")
    data = open(a.path, "rb").read()
    ents = entries(data)
    if a.stream is not None:
        e = ents[a.stream]
        eos = list(_eofs(data, e["offset"] + 24,
                         e.get("key") and len(data) or len(data)))
        pos, _fl, size = eos[-1]
        body = data[pos - size:pos]
        dest = "%s/cache_%d.bin" % (a.to, a.stream)
        open(dest, "wb").write(body)
        print(json.dumps({"wrote": dest, "size": len(body),
                          "key": e.get("key")}))
        return
    print(json.dumps({"file": a.path, "entries": ents,
                      "count": len(ents)}, indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
