#!/usr/bin/env python3
"""lz4_frame.py -- decompress framed .lz4 files (magic 04 22 4D 18).

mozlz4.py handles Firefox's mozLz40 wrapper and raw blocks; this one
handles the standard `lz4`-CLI frame format seen in Linux/firmware
handouts and `*.lz4` artifacts. Layout: magic, FLG/BD bytes, optional
content-size/dictID, a header checksum, then length-prefixed blocks
(bit 31 = stored uncompressed), EndMark, optional content checksum.
Block payloads reuse the LZ4-block decoder from mozlz4.py. The
xxhash32 checksums can't be verified without the module -- flagged
fields are reported, not checked.

  python3 tools/forensics/lz4_frame.py file.lz4          (stdout)
  python3 tools/forensics/lz4_frame.py file.lz4 -o out.bin
  python3 tools/forensics/lz4_frame.py --selftest
"""
import argparse
import json
import struct
import sys

from mozlz4 import lz4_block

MAGIC = 0x184D2204
BSIZE = {4: 1 << 16, 5: 1 << 18, 6: 1 << 20, 7: 1 << 22}


def decompress(data):
    if struct.unpack("<I", data[:4])[0] != MAGIC:
        raise ValueError("not a framed .lz4 (bad magic)")
    flg, bd = data[4], data[5]
    i = 6
    meta = {"block_independence": bool(flg & 0x20),
            "block_checksum": bool(flg & 0x10),
            "content_checksum": bool(flg & 0x04),
            "block_max": BSIZE.get((bd >> 4) & 7)}
    if flg & 0x08:
        meta["content_size"] = struct.unpack("<Q", data[i:i + 8])[0]
        i += 8
    if flg & 0x01:
        meta["dict_id"] = struct.unpack("<I", data[i:i + 4])[0]
        i += 4
    i += 1                                          # header checksum
    out = bytearray()
    nblocks = 0
    while True:
        sz = struct.unpack("<I", data[i:i + 4])[0]
        i += 4
        if sz == 0:
            break
        raw = sz & 0x80000000
        n = sz & 0x7FFFFFFF
        blk = data[i:i + n]
        i += n
        if meta["block_checksum"]:
            i += 4
        out += blk if raw else lz4_block(blk)
        nblocks += 1
    if meta["content_checksum"]:
        i += 4
    meta["blocks"] = nblocks
    if "content_size" in meta and len(out) != meta["content_size"]:
        meta["size_mismatch"] = len(out)
    return bytes(out), meta


def _selftest():
    # compressed block: token 0xF0 + ext 0 = 15 literals, no match
    pay = b"flag{lz4fframe}"
    blk = bytes([0xF0, 0x00]) + pay
    assert lz4_block(blk) == pay, lz4_block(blk)
    frame = (struct.pack("<I", MAGIC) + bytes([0x60, 0x40])
             + b"\x00"                              # HC
             + struct.pack("<I", len(blk)) + blk
             + struct.pack("<I", 0))
    # FLG: version 01 (bits 7-6 = 0b01 → 0x40) + B.Indep 0x20 = 0x60
    out, meta = decompress(frame)
    assert out == pay, (out, meta)
    # uncompressed block (bit31)
    frame2 = (struct.pack("<I", MAGIC) + bytes([0x60, 0x40]) + b"\x00"
              + struct.pack("<I", len(pay) | 0x80000000) + pay
              + struct.pack("<I", 0))
    out2, _ = decompress(frame2)
    assert out2 == pay
    print("lz4_frame selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="framed .lz4 decompress")
    ap.add_argument("path", nargs="?")
    ap.add_argument("-o", "--out")
    ap.add_argument("--info", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("path required")
    out, meta = decompress(open(a.path, "rb").read())
    if a.info:
        print(json.dumps(meta, indent=1))
        return
    if a.out:
        open(a.out, "wb").write(out)
        print(json.dumps({"wrote": a.out, "size": len(out), **meta}))
    else:
        sys.stdout.buffer.write(out)


if __name__ == "__main__":
    raise SystemExit(main())
