#!/usr/bin/env python3
"""file_type.py — artifact identification + routing for rev-triage.

The router's identify step is `file`, `strings`, `binwalk` — all absent on
a Windows box. This is the stdlib answer: magic-byte identification for
the formats rev-triage routes on (ELF, PE, .NET-via-CLR, pyc, class, jar,
dex, wasm, archive/container formats, filesystem images), windowed
entropy for the packed-or-encrypted call, ASCII+UTF-16 string passes
grepping for flag-format and packer names — and one suggested route:
which class skill, which reference, which tool opens it.

    python3 tools/file_type.py ./bin
    python3 tools/file_type.py ./bin --strings --entropy
    python3 tools/file_type.py --selftest
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import struct
import sys

_FLAG_RX = re.compile(rb"(?:flag|ctf|HTB|FLAG)\{?[ -~]{0,60}", re.I)
_PACKER_RX = re.compile(rb"UPX!|UPX0|UPX1|\.themida|vmp[0-9]|aspack|mpress|"
                        rb"petite|molebox|enigma", re.I)


def _magic(data):
    h = data[:16]
    if h.startswith(b"MZ"):
        if len(data) > 0x40:
            peoff = struct.unpack("<I", data[0x3C:0x40])[0]
            if peoff + 6 < len(data) and data[peoff:peoff + 4] == b"PE\0\0":
                clr = _pe_clr(data, peoff)
                return ("pe-dotnet" if clr else "pe-native"), \
                    {"machine": hex(struct.unpack("<H", data[peoff + 4:peoff + 6])[0]),
                     "clr": clr}
        return "pe-mz-unparsed", {}
    if h.startswith(b"\x7fELF"):
        return "elf", {"class": "64" if h[4] == 2 else "32",
                       "type": {1: "relocatable", 2: "executable",
                                3: "shared"}.get(
                           struct.unpack("<H", data[16:18])[0], "?"),
                       "machine": hex(struct.unpack("<H", data[18:20])[0])}
    if h[0] == 0x42 and h[2:4] == b"\x0d\x0a" or h[:4] == b"\xa7\x0d\x0d\x0a":
        return "pyc", {}
    if h.startswith(b"\xca\xfe\xba\xbe"):
        return "java-class", {"version": struct.unpack(">H", h[6:8])[0]}
    if h.startswith(b"dex\n"):
        return "dex", {}
    if h.startswith(b"\x00asm"):
        return "wasm", {}
    if h.startswith(b"PK\x03\x04"):
        return ("apk-or-jar" if b"AndroidManifest" in data[:1 << 20] or
                b"META-INF/MANIFEST.MF" in data[:1 << 20] else "zip"), {}
    if h.startswith(b"\x1f\x8b"):
        return "gzip", {}
    if h.startswith(b"hsqs"):
        return "squashfs", {}
    if h.startswith(b"ustar", 1) or data[257:262] == b"ustar":
        return "tar", {}
    if h.startswith(b"Rar!\x1a\x07"):
        return "rar", {}
    if h.startswith(b"7z\xbc\xaf\x27\x1c"):
        return "7z", {}
    if h.startswith(b"SQLite format 3"):
        return "sqlite", {}
    if len(data) > 0x438 + 2 and data[0x438:0x43A] == b"\x53\xef":
        return "ext-image", {}
    if h.startswith(b"\x89PNG") or h.startswith(b"\xff\xd8\xff") or \
            h[:4] in (b"GIF8", b"%PDF") or h.startswith(b"RIFF"):
        return "media-doc", {}
    return None, {}


def _pe_clr(data, peoff):
    coff = peoff + 4
    nsec = struct.unpack("<H", data[coff + 2:coff + 4])[0]
    optsz = struct.unpack("<H", data[coff + 16:coff + 18])[0]
    opt = coff + 20
    if opt + optsz > len(data):
        return False
    magic = struct.unpack("<H", data[opt:opt + 2])[0]
    dd_base = opt + (96 if magic == 0x10B else 112 if magic == 0x20B else 0)
    if dd_base + 15 * 8 + 8 > len(data):
        return False
    cli_rva = struct.unpack("<I", data[dd_base + 14 * 8:dd_base + 14 * 8 + 4])[0]
    return cli_rva != 0


def _entropy_windows(data, size=4096):
    if not data:
        return []
    out = []
    for i in range(0, min(len(data), 1 << 20), size):
        w = data[i:i + size]
        c = [0] * 256
        for b in w:
            c[b] += 1
        e = -sum(n / len(w) * math.log2(n / len(w)) for n in c if n)
        out.append(round(e, 2))
    return out


def _strings(data, minlen=8):
    runs, cur = [], bytearray()
    for b in data[:1 << 22]:
        if 32 <= b < 127:
            cur.append(b)
        else:
            if len(cur) >= minlen:
                runs.append(bytes(cur))
            cur = bytearray()
    if len(cur) >= minlen:
        runs.append(bytes(cur))
    return runs


def _utf16(data, minlen=6):
    runs, cur = [], bytearray()
    i = 0
    while i + 1 < min(len(data), 1 << 22):
        c = struct.unpack("<H", data[i:i + 2])[0]
        if 32 <= c < 127:
            cur.append(c)
        else:
            if len(cur) >= minlen:
                runs.append(bytes(cur))
            cur = bytearray()
        i += 2
    if len(cur) >= minlen:
        runs.append(bytes(cur))
    return runs


_ROUTES = {
    "elf": ("pwn-binary-triage / rev-native-check",
            "tools/pwn_triage.py for protections; then rev-triage"),
    "pe-native": ("rev-native-check", "disassembler of choice"),
    "pe-dotnet": ("rev-managed-code", "dnSpy/ILSpy; references/managed-code.md"),
    "pyc": ("rev-bytecode-vm", "marshal/dis or decompiler per version"),
    "java-class": ("rev-bytecode-vm", "javap -c or a decompiler"),
    "dex": ("rev-bytecode-vm", "jadx / baksmali"),
    "wasm": ("rev-bytecode-vm", "wasm-decompile / wasm2wat"),
    "apk-or-jar": ("rev-bytecode-vm", "unzip; dex/classes inside"),
    "zip": ("unpack first", "unzip; re-identify contents"),
    "gzip": ("unpack first", "gunzip; re-identify"),
    "squashfs": ("rev-triage firmware", "references/firmware-analysis.md; unsquashfs"),
    "tar": ("unpack first", "tar -xf; re-identify"),
    "sqlite": ("forensics or misc", "sqlite3 CLI"),
    "ext-image": ("forensics-disk-image",
                  "references/deleted-and-unallocated.md"),
    "media-doc": ("forensics-stego / osint-media-metadata",
                  "tools/forensics/carve_scan.py first pass"),
}


def identify(path, want_strings=True, want_entropy=True):
    data = open(path, "rb").read()
    fmt, detail = _magic(data)
    out = {"file": path, "bytes": len(data), "format": fmt or "unknown",
           "detail": detail}
    if want_entropy:
        wins = _entropy_windows(data)
        avg = sum(wins) / len(wins) if wins else 0
        out["entropy_avg"] = round(avg, 2)
        if avg > 7.2 and len(data) > 1024:
            out["entropy_note"] = ("flat-high entropy — packed, encrypted, "
                                   "or compressed content")
    if want_strings:
        runs = _strings(data) + _utf16(data)
        flag_hits = [r.decode("utf-8", "replace") for r in runs
                     if _FLAG_RX.search(r)][:10]
        pack_hits = sorted({_PACKER_RX.search(r).group(0).decode()
                            for r in runs if _PACKER_RX.search(r)})
        out["flag_strings"] = flag_hits
        out["packer_strings"] = pack_hits
        if pack_hits:
            out["entropy_note"] = out.get("entropy_note", "") + \
                f" packer markers: {pack_hits}"
    route = _ROUTES.get(fmt)
    if route:
        out["route"] = {"class": route[0], "open": route[1]}
    else:
        out["route"] = {"class": "manual",
                        "open": "unknown format — strings/carve_scan next"}
    return out


def _selftest() -> int:
    import tempfile
    # minimal ELF64
    elf = b"\x7fELF\x02\x01\x01\x00" + b"\x00" * 8 + \
        struct.pack("<HHI", 2, 0x3E, 1) + b"\x00" * 64
    # PE with CLR data directory (dir 14 at opt+96+14*8 for PE32)
    opt = bytearray(0xE0)
    struct.pack_into("<H", opt, 0, 0x10B)          # PE32 magic
    struct.pack_into("<II", opt, 96 + 14 * 8, 0x2000, 72)  # CLI header rva/sz
    pe = (b"MZ" + b"\x00" * (0x3C - 2) + struct.pack("<I", 0x80) +
          b"\x00" * (0x80 - 0x40) +
          b"PE\0\0" + struct.pack("<HHIIIHH", 0x14C, 3, 0, 0, 0, 0xE0, 0x210F) +
          bytes(opt) + b"\x00" * 0x100)
    with tempfile.TemporaryDirectory() as td:
        p1, p2 = os.path.join(td, "a.elf"), os.path.join(td, "b.exe")
        open(p1, "wb").write(elf)
        open(p2, "wb").write(bytes(pe))
        r1 = identify(p1, want_strings=False, want_entropy=False)
        r2 = identify(p2, want_strings=False, want_entropy=False)
    assert r1["format"] == "elf" and r1["detail"]["class"] == "64", r1
    assert r2["format"] == "pe-dotnet", r2
    print("file_type selftest: ok")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", nargs="?")
    ap.add_argument("--strings", action="store_true", help="include string hits")
    ap.add_argument("--entropy", action="store_true", help="include entropy")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if not args.file:
        ap.print_help()
        return 2
    # strings+entropy default on; flags exist to silence linters/readers
    out = identify(args.file, want_strings=True, want_entropy=True)
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
