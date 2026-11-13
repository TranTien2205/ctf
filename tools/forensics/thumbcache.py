#!/usr/bin/env python3
"""thumbcache.py -- Windows thumbcache_*.db entry recovery.

Thumbcache databases keep JPEG/PNG previews of images long after the
originals are deleted -- the standard "show me the deleted picture"
question in Sherlocks. Layout: an 'IMMM' file header, then 'CMMM'
entries, each carrying a UTF-16 filename and an embedded image body
(most entries are JPEG: \\xff\\xd8..\\xff\\xd9). This tool walks
entries, reports name/size/dimensions, and `--extract N` writes the
embedded image. Entries whose payload isn't a recognised image are
named by size, not guessed.

  python3 tools/forensics/thumbcache.py thumbcache_96.db
  python3 tools/forensics/thumbcache.py thumbcache_96.db --extract 3 --to out/
  python3 tools/forensics/thumbcache.py --selftest
"""
import argparse
import json
import struct
import sys


def parse(data):
    if len(data) < 24 or data[:4] not in (b"IMMM", b"CMMM"):
        return {"error": "not a thumbcache db (bad magic)"}
    ver, _ft, first_off, _av, _cnt = struct.unpack(
        "<IIIII", data[4:24])
    entries = []
    pos = first_off
    seen = set()
    while pos and pos + 24 <= len(data) and pos not in seen:
        seen.add(pos)
        if data[pos:pos + 4] != b"CMMM":
            break
        (size, ehash, fnlen, pad, dsize) = struct.unpack(
            "<IQIII", data[pos + 4:pos + 28])
        hdr = pos + 28
        if len(data) >= pos + 52:
            _w, _h, _dck, _hck = struct.unpack(
                "<IIQQ", data[pos + 28:pos + 52])
            hdr = pos + 52
        name = data[hdr:hdr + fnlen].decode(
            "utf-16-le", "replace").rstrip("\x00")
        body_off = hdr + fnlen + pad
        body = data[body_off:body_off + dsize]
        kind = "jpeg" if body[:2] == b"\xff\xd8" else \
            "png" if body[:8] == b"\x89PNG\r\n\x1a\n" else \
            "bmp" if body[:2] == b"BM" else \
            "other(%dB)" % len(body)
        entries.append({"offset": pos, "hash": hex(ehash),
                        "name": name, "size": size,
                        "data_size": dsize, "kind": kind,
                        "body_off": body_off})
        if size < 24:
            break
        pos += size
    return {"version": ver, "entries": entries,
            "count": len(entries),
            "kinds": sorted({e["kind"] for e in entries})}


def _selftest():
    jpg = b"\xff\xd8\xff\xe0" + b"FAKEJPEG" + b"\xff\xd9"
    name = "flag_pic.jpg".encode("utf-16-le") + b"\x00\x00"
    fnlen = len(name)
    dsize = len(jpg)
    pad = 0
    size = 52 + fnlen + pad + dsize
    ent = (b"CMMM" + struct.pack("<IQIII", size, 0xDEAD, fnlen, pad,
                                 dsize)
           + struct.pack("<IIQQ", 96, 96, 0, 0)
           + name + jpg)
    hdr = b"IMMM" + struct.pack("<IIIII", 0x1C, 3, 28, 0, 1)
    blob = hdr + b"\x00" * 4 + ent
    r = parse(blob)
    e = r["entries"][0]
    assert e["name"].startswith("flag_pic"), e
    assert e["kind"] == "jpeg" and e["data_size"] == dsize
    body = blob[e["body_off"]:e["body_off"] + dsize]
    assert body.startswith(b"\xff\xd8") and body.endswith(b"\xff\xd9")
    print("thumbcache selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="thumbcache db reader")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--extract", type=int, metavar="N")
    ap.add_argument("--to", default=".")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("path required")
    data = open(a.path, "rb").read()
    r = parse(data)
    if a.extract is not None:
        e = r["entries"][a.extract]
        body = data[e["body_off"]:e["body_off"] + e["data_size"]]
        ext = {"jpeg": ".jpg", "png": ".png", "bmp": ".bmp"}.get(
            e["kind"], ".bin")
        dest = "%s/thumb_%d%s" % (a.to, a.extract, ext)
        open(dest, "wb").write(body)
        print(json.dumps({"wrote": dest, "size": len(body),
                          "name": e["name"]}))
        return
    print(json.dumps(r, indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
