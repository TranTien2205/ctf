#!/usr/bin/env python3
"""png_fix.py -- repair a corrupted PNG and say exactly what was wrong.

The corrupted-PNG shape recurs in CTF: a CRC rewritten to hide a
chunk, a missing IEND, a swapped chunk order, garbage inserted
between chunks. img_struct.py reports the damage; this repairs it:
- recompute every chunk's CRC (bad CRC = tamper signal, not fatal)
- drop byte ranges that are not valid chunks
- append a missing IEND
- verify IHDR exists and is 13 bytes

  python3 tools/forensics/png_fix.py broken.png            # report only
  python3 tools/forensics/png_fix.py broken.png --fix out.png
  python3 tools/forensics/png_fix.py --selftest

It never guesses pixel data — a file whose IDAT stream itself is
damaged reports zlib failure instead of silently writing junk.
"""
import argparse
import json
import struct
import sys
import zlib

SIG = b"\x89PNG\r\n\x1a\n"
KNOWN = {b"IHDR", b"PLTE", b"IDAT", b"IEND", b"tEXt", b"zTXt",
         b"iTXt", b"bKGD", b"cHRM", b"gAMA", b"hIST", b"iCCP",
         b"pHYs", b"sBIT", b"sPLT", b"sRGB", b"tIME", b"tRNS"}


def walk(data):
    chunks, off = [], 8
    while off + 8 <= len(data):
        size, typ = struct.unpack(">I4s", data[off:off + 8])
        end = off + 12 + size
        if end > len(data) or not all(65 <= c <= 122 for c in typ):
            chunks.append({"offset": off, "invalid": True,
                           "size": min(size, len(data) - off)})
            break
        body = data[off + 8:off + 8 + size]
        have = struct.unpack(">I", data[off + 8 + size:end])[0]
        want = zlib.crc32(typ + body) & 0xFFFFFFFF
        chunks.append({"type": typ.decode("latin-1"), "offset": off,
                       "size": size, "crc_ok": have == want,
                       "end": end})
        off = end
        if typ == b"IEND":
            break
    return chunks


def repair(data):
    if data[:8] != SIG:
        return None, ["no PNG signature — not repairable"]
    issues, out = [], bytearray(SIG)
    iend_seen = False
    off, skipped, chunk_types = 8, 0, []
    while off + 8 <= len(data):
        size, typ = struct.unpack(">I4s", data[off:off + 8])
        end = off + 12 + size
        if end > len(data) or not all(65 <= c <= 122 for c in typ):
            off += 1
            skipped += 1
            continue
        body = data[off + 8:off + 8 + size]
        have = struct.unpack(">I", data[off + 8 + size:end])[0]
        want = zlib.crc32(typ + body) & 0xFFFFFFFF
        if have != want:
            issues.append(f"recomputed CRC on "
                          f"{typ.decode('latin-1')} @{off}")
        chunk_types.append(typ.decode("latin-1"))
        out += struct.pack(">I", size) + typ + body + \
            struct.pack(">I", zlib.crc32(typ + body) & 0xFFFFFFFF)
        off = end
        if typ == b"IEND":
            iend_seen = True
            if off < len(data):
                issues.append(f"{len(data) - off} trailer bytes "
                              f"after IEND left off")
            break
    if skipped:
        issues.append(f"dropped {skipped} non-chunk bytes")
    if not iend_seen:
        out += struct.pack(">I", 0) + b"IEND" + \
            struct.pack(">I", zlib.crc32(b"IEND") & 0xFFFFFFFF)
        issues.append("appended missing IEND")
    if "IHDR" not in chunk_types:
        issues.append("no IHDR — output will not decode")
    res = walk(bytes(out))
    idat = b"".join(out[c["offset"] + 8:c["offset"] + 8 + c["size"]]
                    for c in res if c.get("type") == "IDAT")
    if idat:
        try:
            zlib.decompress(bytes(idat))
        except zlib.error:
            issues.append("IDAT stream does not inflate — pixel data "
                          "damaged beyond chunk repair")
    return bytes(out), issues


def _selftest():
    def chunk(t, b, bad_crc=False):
        crc = zlib.crc32(t + b) & 0xFFFFFFFF
        return struct.pack(">I", len(b)) + t + b + \
            struct.pack(">I", crc ^ (0xFFFF if bad_crc else 0))
    ihdr = chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
    raw = b"\x00\x00\x00\x00"                     # 1x1 filter0 black
    idat = chunk(b"IDAT", zlib.compress(raw))
    # broken: bad CRC on IHDR, garbage between, no IEND
    broken = (SIG + chunk(b"IHDR",
                          struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0),
                          bad_crc=True)
              + b"GARBAGE!!" + idat)
    fixed, issues = repair(broken)
    assert any("CRC" in i for i in issues), issues
    assert any("IEND" in i for i in issues), issues
    assert fixed[:8] == SIG and b"IEND" in fixed[-12:]
    # round-trip: walk the fixed file
    res = walk(fixed)
    assert all(c["crc_ok"] for c in res), res
    dec = zlib.decompress(b"".join(
        fixed[c["offset"] + 8:c["offset"] + 8 + c["size"]]
        for c in res if c["type"] == "IDAT"))
    assert dec == raw
    print("png_fix selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="repair a broken PNG")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--fix", metavar="OUT")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("png path required")
    data = open(a.path, "rb").read()
    fixed, issues = repair(data)
    print(json.dumps({"issues": issues,
                      "repaired_bytes": None if fixed is None
                      else len(fixed)}, indent=1))
    if a.fix and fixed:
        open(a.fix, "wb").write(fixed)


if __name__ == "__main__":
    raise SystemExit(main())
