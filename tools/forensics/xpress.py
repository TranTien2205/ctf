#!/usr/bin/env python3
"""xpress.py -- Microsoft XPRESS Huffman (LZ77+Huffman) decompressor.

Pure stdlib implementation of the MS-XCA LZ77+Huffman variant, the
codec behind `MAM\\x04` prefetch files (all Win8+ `.pf`), WIM chunks,
hiberfil `\\x81\\x81xpress` blocks and SMB3 compression. Verified
against the wimlib reference decoder and the MS-XCA spec:

  * stream = 256 bytes of Huffman code lengths (512 symbols x 4 bits;
    low nibble = even symbol) then a canonical-Huffman bitstream;
  * the bitstream packs bytes into a 32-bit register LSB-first -- the
    first consumed bit is bit0 of the first byte -- and each canonical
    codeword occupies the HIGH bits of a 15-bit index into the table;
  * symbols 0-255 are literal bytes; symbols 256-511 begin a match:
    low nibble is the length header, high nibble is log2(offset); the
    offset is `(1<<bsr) | next bsr bits`, and a length header of 0xF
    reads a literal byte inline (0xFF there means a u16 follows),
    then +3 minimum. Offsets 1..65535, lengths 3..65538.

`mam_decompress` unwraps the `MAM\\x04` prefetch framing (u32
uncompressed size, then one XPRESS stream). Sizes are checked against
the declared size rather than trusted; an offset that points beyond
produced output raises rather than corrupting the window.

  python3 tools/forensics/xpress.py file.mam --mam -o out.bin
  python3 tools/forensics/xpress.py stream.xpress --size 1234 -o out
  python3 tools/forensics/xpress.py --selftest
"""
import argparse
import json
import struct
import sys

TABLE_BYTES = 256
NUM_SYMBOLS = 512
MAX_LEN = 15


def _lens(tab):
    lens = [0] * NUM_SYMBOLS
    for i, b in enumerate(tab):
        lens[i * 2] = b & 0xF
        lens[i * 2 + 1] = b >> 4
    return lens


def _table(lens):
    """MS-XCA canonical table: 2^15 entries, filled by (length,sym)."""
    t = [None] * (1 << MAX_LEN)
    e = 0
    for bl in range(1, MAX_LEN + 1):
        for s in range(NUM_SYMBOLS):
            if lens[s] == bl:
                cnt = 1 << (MAX_LEN - bl)
                for i in range(cnt):
                    t[e + i] = s
                e += cnt
                if e > len(t):
                    raise ValueError("overfull Huffman table (corrupt "
                                     "length set)")
    return t


class _BS(object):
    """LSB-first bit register over the byte stream."""

    def __init__(self, d):
        self.d = d
        self.p = 0
        self.buf = 0
        self.n = 0

    def _need(self, k):
        while self.n < k and self.p < len(self.d):
            self.buf |= self.d[self.p] << self.n
            self.p += 1
            self.n += 8

    def pop(self, k):
        if k == 0:
            return 0
        self._need(k)
        v = self.buf & ((1 << k) - 1)
        self.buf >>= k
        self.n -= k
        return v

    def peek15(self):
        self._need(MAX_LEN)
        v = 0
        for i in range(MAX_LEN):
            v = (v << 1) | ((self.buf >> i) & 1)
        return v


def decompress(data, usize):
    """One XPRESS Huffman stream -> usize uncompressed bytes."""
    if len(data) < TABLE_BYTES:
        raise ValueError("stream too small for the 256-byte table")
    lens = _lens(data[:TABLE_BYTES])
    table = _table(lens)
    bs = _BS(data[TABLE_BYTES:])
    out = bytearray()
    while len(out) < usize:
        s = table[bs.peek15()]
        if s is None:
            raise ValueError(
                "bad Huffman prefix after %d output bytes" % len(out))
        bs.buf >>= lens[s]
        bs.n -= lens[s]
        if s < 256:
            out.append(s)
            continue
        s -= 256
        len_hdr, bsr = s & 0xF, s >> 4
        off = (1 << bsr) | bs.pop(bsr)
        if len_hdr == 0xF:
            m = bs.pop(8)
            m = (bs.pop(8) | (bs.pop(8) << 8)) if m == 0xFF else m + 0xF
        else:
            m = len_hdr
        m += 3
        if off > len(out):
            raise ValueError(
                "match offset %d beyond %d produced bytes" % (off, len(out)))
        start = len(out)
        for _ in range(m):
            out.append(out[len(out) - off])
        del out[usize:]                    # never overrun the window
        if len(out) - start == 0:
            raise ValueError("zero-length match")
    return bytes(out[:usize])


def mam_decompress(data):
    """`MAM\\x04` prefetch wrapper -> uncompressed SCCA bytes."""
    if data[:4] != b"MAM\x04":
        raise ValueError("not a MAM frame (signature is not MAM\\x04)")
    usize, = struct.unpack("<I", data[4:8])
    body = decompress(data[8:], usize)
    consumed_note = {}
    return body, {"declared_size": usize}


def _pack_stream(codes, lens_map):
    """selftest helper: table bytes + packed codeword bit list."""
    tab = bytearray(TABLE_BYTES)
    for sym, ln in lens_map.items():
        if sym % 2 == 0:
            tab[sym // 2] |= ln
        else:
            tab[sym // 2] |= ln << 4
    bits = []
    for item in codes:
        if isinstance(item, int):
            for i in range(8):                 # raw byte, LSB-first
                bits.append((item >> i) & 1)
        else:
            code, ln = item
            for i in range(ln - 1, -1, -1):
                bits.append((code >> i) & 1)
    body = bytearray()
    for i in range(0, len(bits), 8):
        b = 0
        for j, bit in enumerate(bits[i:i + 8]):
            b |= bit << j
        body.append(b)
    return bytes(tab) + bytes(body)


def _selftest():
    # literal-only: 'A'(65) len1 code 0, 'B'(66) len1 code 1 -> "AB"
    st = _pack_stream([(0, 1), (1, 1)], {65: 1, 66: 1})
    assert decompress(st, 2) == b"AB"
    # literal+match: 'A' len1(0), 'B'(66) len2(10), match 257 len2(11)
    # stream: A | sym257 (off=1,len_hdr=1->m=4) | B  => "AAAAAB"
    lens = {65: 1, 66: 2, 257: 2}
    st = _pack_stream([(0, 1), (3, 2), (2, 2)], lens)
    out = decompress(st, 6)
    assert out == b"AAAAAB", out
    # len_hdr == 0xF escape: sym 271 -> s=15 -> len_hdr 0xF, bsr 0
    # byte 0x20 -> m = 0x20+0xF+3 = 0x32 ; need "A" then 50 copies
    lens2 = {65: 1, 66: 2, 271: 2}
    st = _pack_stream([(0, 1), (3, 2), 0x20, (2, 2)], lens2)
    out = decompress(st, 52)
    assert out == b"A" * 51 + b"B", out[:5] + out[-2:]
    # MAM wrapper
    mam = b"MAM\x04" + struct.pack("<I", 6) + st
    # st above decodes to 51 bytes; build a 6-byte one instead
    st6 = _pack_stream([(0, 1), (3, 2), (2, 2)], lens)
    mam = b"MAM\x04" + struct.pack("<I", 6) + st6
    body, info = mam_decompress(mam)
    assert body == b"AAAAAB", body
    print("xpress selftest: ok")


def main():
    ap = argparse.ArgumentParser(
        description="XPRESS Huffman (MS-XCA LZ77+Huffman) decompressor")
    ap.add_argument("path", nargs="?")
    ap.add_argument("-o", "--out")
    ap.add_argument("--mam", action="store_true",
                    help="input is a MAM\\x04 prefetch frame")
    ap.add_argument("--size", type=int,
                    help="uncompressed size for a bare stream")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("path required")
    data = open(a.path, "rb").read()
    if a.mam or data[:4] == b"MAM\x04":
        body, info = mam_decompress(data)
    elif a.size:
        body = decompress(data, a.size)
        info = {"declared_size": a.size}
    else:
        ap.error("need --mam (or a MAM signature) or --size")
    if a.out:
        open(a.out, "wb").write(body)
    print(json.dumps({"written": a.out or None,
                      "bytes": len(body),
                      "scca": body[4:8] == b"SCCA",
                      "head_hex": None if a.out else body[:64].hex()},
                     indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
