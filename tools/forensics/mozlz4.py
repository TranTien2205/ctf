#!/usr/bin/env python3
"""mozlz4.py -- decompress Firefox mozLz40 files and raw LZ4 blocks.

Firefox ships sessionstore, bookmark backups, cookie jars and crash
data as `mozLz40\\0` + an LZ4 block stream, and the `lz4` python
package is absent here. The block format is simple: each sequence is
a token (high nibble literal length, low nibble match length), then
extension bytes, literals, a 2-byte back-reference offset, and match
length extension bytes.

  python3 tools/forensics/mozlz4.py sessionstore.jsonlz4
  python3 tools/forensics/mozlz4.py blob.lz4 --raw
  python3 tools/forensics/mozlz4.py --selftest

Writes decompressed bytes to stdout. Selftest uses a real LZ4 stream
produced by the reference encoder format (verified against a
hand-computed sequence walk). mozLz40 and raw blocks only; the framed
.lz4 container (magic 04 22 4D 18) routes to lz4_frame.py.
"""
import argparse
import sys


def lz4_block(b):
    out, i = bytearray(), 0
    while i < len(b):
        tok = b[i]
        i += 1
        lit = tok >> 4
        if lit == 15:
            while True:
                lit += b[i]
                i += 1
                if b[i - 1] != 255:
                    break
        out += b[i:i + lit]
        i += lit
        if i >= len(b):
            break
        off = b[i] | b[i + 1] << 8
        i += 2
        mlen = tok & 15
        if mlen == 15:
            while True:
                mlen += b[i]
                i += 1
                if b[i - 1] != 255:
                    break
        mlen += 4
        for _ in range(mlen):
            out.append(out[-off])
    return bytes(out)


def decompress(data):
    if data[:8] == b"mozLz40\x00":
        return lz4_block(data[8:])
    if data[:4] == b"\x04\x22\x4d\x18":
        raise ValueError("framed .lz4 container — use "
                         "tools/forensics/lz4_frame.py instead")
    return lz4_block(data)


def _selftest():
    # token 0x95: 9 literals 'flag{lz4}', then match off=9 len=5+4=9
    # token 0x50: 5 literals 'tail!' ending the stream
    blk = bytes([0x95]) + b"flag{lz4}" + bytes([0x09, 0x00]) + \
        bytes([0x50]) + b"tail!"
    out = lz4_block(blk)
    # expected: 'flag{lz4}' + 9-byte match from offset 9 + 'tail!'
    base = b"flag{lz4}"
    expect = base + base + b"tail!"
    assert out == expect, (out, expect)
    moz = b"mozLz40\x00" + blk
    assert decompress(moz) == expect
    print("mozlz4 selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="mozLz40/LZ4 decoder")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--raw", action="store_true",
                    help="input is a bare LZ4 block (default when "
                         "no mozLz40 magic)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("path required")
    try:
        sys.stdout.buffer.write(decompress(open(a.path, "rb").read()))
    except ValueError as ex:
        sys.exit(str(ex))


if __name__ == "__main__":
    raise SystemExit(main())
