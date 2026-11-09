#!/usr/bin/env python3
"""vba_extract.py -- dump VBA module source from an Office file.

Usage:
  python3 tools/forensics/vba_extract.py doc.doc
  python3 tools/forensics/vba_extract.py book.xlsm
  python3 tools/forensics/vba_extract.py --selftest

.doc/.xls/vbaProject.bin are CFB; .docx/.xlsm are zip files whose
vbaProject.bin is a CFB. Streams under VBA/ (plus _VBA_PROJECT/dir)
hold modules in MS-OVBA CompressedContainer form: 0x01 signature,
then chunks of 4096 raw or compressed bytes. Compressed tokens are
16-bit: copy-token (offset+length back-reference) or literal. The
dir stream's module records give offsets into each module stream.
"""
import argparse
import io
import json
import math
import struct
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cfb_parse import CFB  # noqa: E402


def decompress_vba(data, start=0):
    """MS-OVBA CompressedContainer -> bytes."""
    if data[start] != 1:
        return data[start:]
    out, pos = bytearray(), start + 1
    while pos + 2 <= len(data):
        hdr = struct.unpack("<H", data[pos:pos + 2])[0]
        pos += 2
        size = (hdr & 0x0FFF) + 3
        if pos + size > len(data):
            break
        chunk = data[pos:pos + size]
        pos += size
        if hdr & 0x8000:            # compressed chunk
            chunk_base = len(out)   # copy-token window is per-chunk
            ci = 0
            while ci < len(chunk):
                flag = chunk[ci]
                ci += 1
                for bit in range(8):
                    if ci >= len(chunk):
                        break
                    if flag & (1 << bit):
                        tok = struct.unpack("<H", chunk[ci:ci + 2])[0]
                        ci += 2
                        # offset field width = ceil(log2(position in
                        # decompressed chunk)), min 4 (MS-OVBA)
                        pos_in = len(out) - chunk_base
                        bits = 4 if pos_in < 2 else max(
                            4, min(12, math.ceil(
                                math.log2(pos_in))))
                        lmask = (1 << (16 - bits)) - 1
                        length = (tok & lmask) + 3
                        off = (tok >> (16 - bits)) + 1
                        for _ in range(length):
                            out.append(out[-off])
                    else:
                        out.append(chunk[ci])
                        ci += 1
        else:
            out += chunk
    return bytes(out)


def _cfb_from(path):
    data = Path(path).read_bytes()
    if data[:2] == b"PK":
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            for n in z.namelist():
                if n.lower().endswith("vbaproject.bin"):
                    tmp = Path(tempfile.mkdtemp()) / "vba.bin"
                    tmp.write_bytes(z.read(n))
                    return CFB(tmp)
        raise ValueError("zip has no vbaProject.bin")
    return CFB(path)


def modules(path):
    c = _cfb_from(path)
    out = {}
    for e in c.dirs():
        if e["type"] != 2:
            continue
        name = e["name"]
        raw = c.stream(name)
        if raw is None:
            continue
        if name == "dir" or name.startswith("_VBA_PROJECT"):
            continue
        out[name] = decompress_vba(raw)
    return out


def _selftest():
    # build a compressed container holding one literal-only chunk
    src = b"Sub AutoOpen(): MsgBox \"flag{vba}\": End Sub"
    chunk = bytearray()
    body = bytearray()
    for i in range(0, len(src), 8):
        grp = src[i:i + 8]
        body.append(0)                    # flag byte: all literals
        body += grp
    chunk = struct.pack("<H", 0x8000 | (len(body) - 3)) + bytes(body)
    container = b"\x01" + chunk
    de = decompress_vba(container)
    assert de == src, de
    # token path: 5 literals "flag{" then a copy token (off 5 len 3)
    pre = b"flag{"
    grp = bytes([0b00100000]) + pre       # bits 0-4 lit, bit5 token
    tok = ((5 - 1) << 12) | (3 - 3)       # off=5 len=3 -> 'fla'
    grp += struct.pack("<H", tok)
    c2 = b"\x01" + struct.pack("<H", 0x8000 | (len(grp) - 3)) + grp
    de2 = decompress_vba(c2)
    assert de2 == b"flag{fla", de2
    print("vba_extract selftest: ok")


def main():
    ap = argparse.ArgumentParser(
        description="dump VBA module source from an Office file")
    ap.add_argument("file", nargs="?")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.file:
        ap.error("file required")
    mods = modules(a.file)
    print(json.dumps({"modules": {k: v.decode("utf-8", "replace")
                                  for k, v in mods.items()}},
                     indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
