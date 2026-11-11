#!/usr/bin/env python3
"""macho_info.py -- Mach-O inventory: segments, sections, dylibs, syms.

ELF and PE have readers; macOS binaries were the missing third.
Parses the 32/64-bit header, walks load commands for LC_SEGMENT_64 /
LC_SEGMENT (sections), LC_LOAD_DYLIB imports, LC_SYMTAB / LC_DYSYMTAB
symbols with names, LC_MAIN entry point, and fat/universal headers
(which contain per-arch slices to re-run against).

  python3 tools/macho_info.py ./bin
  python3 tools/macho_info.py ./bin --symbols-only
  python3 tools/macho_info.py ./bin --slice 1   # fat binary arch slice
  python3 tools/macho_info.py --selftest

Static read only. Encrypted/packed sections are flagged via the
encryption-info commands when present.
"""
import argparse
import json
import struct
import sys

MAGICS = {0xFEEDFACE: ("32", ">"), 0xCEFAEDFE: ("32", "<"),
          0xFEEDFACF: ("64", ">"), 0xCFFAEDFE: ("64", "<"),
          0xCAFEBABE: ("fat", ">"), 0xBEBAFECA: ("fat", "<")}
CPU = {7: "x86", 0x1000007: "x86-64", 12: "ARM", 0x100000C: "ARM64"}
FTYPE = {1: "object", 2: "executable", 6: "dylib", 8: "bundle",
         11: "dyld-cache"}

LC_NAMES = {0x19: "LC_SEGMENT_64", 0x1: "LC_SEGMENT",
            0x2: "LC_SYMTAB", 0xB: "LC_DYSYMTAB", 0xC: "LC_LOAD_DYLIB",
            0xD: "LC_ID_DYLIB", 0x80000028: "LC_MAIN",
            0x21: "LC_ENCRYPTION_INFO", 0x2C: "LC_ENCRYPTION_INFO_64"}


def _cstr(b, off):
    end = b.find(b"\x00", off)
    return b[off:end].decode("utf-8", "replace") if 0 <= off < len(b) \
        else ""


def parse_thin(data):
    if len(data) < 28:
        return {"error": "truncated"}
    magic = struct.unpack(">I", data[0:4])[0]
    cls, e = MAGICS.get(magic, (None, "<"))
    if not cls or cls == "fat":
        return {"error": "not a thin macho"}
    if cls == "64":
        (cpu, _sub, ftype, ncmds, _sc, _fl, _r) = struct.unpack(
            e + "IIIIIII", data[4:32])
        off = 32
    else:
        (cpu, _sub, ftype, ncmds, _sc, _fl) = struct.unpack(
            e + "IIIIII", data[4:28])
        off = 28
    secs, syms, libs, cmds = [], [], [], []
    entry, symtab = None, None
    for _ in range(ncmds):
        if off + 8 > len(data):
            break
        cmd, csz = struct.unpack(e + "II", data[off:off + 8])
        body = data[off:off + csz]
        cmds.append(LC_NAMES.get(cmd, hex(cmd)))
        if cmd in (0x19, 0x1):                    # segments
            if cmd == 0x19:
                nsec = struct.unpack(e + "I", body[64:68])[0]
                so = 72
                for i in range(nsec):
                    s = body[so + i * 80:so + (i + 1) * 80]
                    secs.append({
                        "sect": _cstr(s, 0), "seg": _cstr(s, 16),
                        "addr": hex(struct.unpack(e + "Q", s[32:40])[0]),
                        "size": struct.unpack(e + "Q", s[40:48])[0]})
            else:
                nsec = struct.unpack(e + "I", body[48:52])[0]
                so = 56
                for i in range(nsec):
                    s = body[so + i * 68:so + (i + 1) * 68]
                    secs.append({
                        "sect": _cstr(s, 0), "seg": _cstr(s, 16),
                        "addr": hex(struct.unpack(e + "I", s[32:36])[0]),
                        "size": struct.unpack(e + "I", s[36:40])[0]})
        elif cmd == 0x2:
            symtab = struct.unpack(e + "IIII", body[8:24])
        elif cmd in (0xC, 0xD):
            name_off = struct.unpack(e + "I", body[8:12])[0]
            libs.append(_cstr(body, name_off))
        elif cmd == 0x80000028:
            entry = hex(struct.unpack(e + "Q", body[8:16])[0])
        elif cmd in (0x21, 0x2C):
            crypt = struct.unpack(e + "III", body[8:20])
            if crypt[2]:
                libs.append(f"ENCRYPTED region id={crypt[2]}")
        off += csz
    if symtab:
        soff, nsyms, stroff, _ssz = symtab
        entsz = 16 if cls == "64" else 12
        strs = data[stroff:]
        for i in range(nsyms):
            o = soff + i * entsz
            if o + entsz > len(data):
                break
            si = struct.unpack(e + "I", data[o:o + 4])[0]
            nm = _cstr(strs, si)
            if nm:
                syms.append(nm)
    return {"class": cls, "cpu": CPU.get(cpu, hex(cpu)),
            "filetype": FTYPE.get(ftype, hex(ftype)),
            "entryoff": entry, "load_commands": cmds,
            "sections": secs, "dylibs": libs,
            "symbols": syms or "no symtab"}


def parse(data, slice_no=0):
    magic = struct.unpack(">I", data[0:4])[0]
    cls, e = MAGICS.get(magic, (None, None))
    if cls == "fat":
        nfat = struct.unpack(e + "I", data[4:8])[0]
        slices = []
        for i in range(nfat):
            o = 8 + i * 20
            cpu, _sub, off, sz, _al = struct.unpack(
                e + "IIIII", data[o:o + 20])
            slices.append({"slice": i, "cpu": CPU.get(cpu, hex(cpu)),
                           "offset": off, "size": sz})
        if slice_no >= len(slices):
            return {"fat": True, "slices": slices,
                    "error": f"slice {slice_no} out of range"}
        s = slices[slice_no]
        out = parse_thin(data[s["offset"]:s["offset"] + s["size"]])
        out["fat"] = True
        out["slices"] = slices
        out["slice"] = slice_no
        return out
    return parse_thin(data)


def _selftest():
    e = "<"
    text = b"__text\x00" + b"\x00" * 9 + b"__TEXT\x00" + b"\x00" * 9 \
        + struct.pack(e + "QQQQIIII", 0x1000, 0x40, 0, 0x40, 3, 7, 0, 0)
    seg = struct.pack(e + "II16sQQQQiiII",
                      0x19, 72 + 80, b"__TEXT\x00" + b"\x00" * 10,
                      0, 0x1000, 0, 0x1000, 7, 5, 1, 0) + text
    strs = b"\x00evil_check\x00strncmp\x00"
    symt = struct.pack(e + "IIIIII", 2, 24, 0x400, 2, 0x500, len(strs))
    dl = b"libx.dylib\x00"
    dylib = struct.pack(e + "IIIIII", 0xC, 24 + len(dl) + 8, 24,
                        0, 0, 0) + dl + b"\x00" * 8
    main = struct.pack(e + "IIQ", 0x80000028, 24, 0x40)
    cmds = seg + symt + dylib + main
    ncmds = 4
    hdr = struct.pack(e + "IIIIIIII", 0xFEEDFACF, 0x1000007, 3, 2,
                      ncmds, len(cmds), 0, 0)
    img = bytearray(0x600)
    img[:32 + len(cmds)] = hdr + cmds
    img[0x400:0x400 + 32] = struct.pack(e + "IBBHQ",
                                        1, 0xF, 0, 0, 0x1000) + \
        struct.pack(e + "IBBHQ", 12, 0xF, 0, 0, 0x1010)
    img[0x500:0x500 + len(strs)] = strs
    d = parse(bytes(img))
    assert d["cpu"] == "x86-64" and d["filetype"] == "executable", d
    assert any(s["sect"] == "__text" for s in d["sections"]), d
    assert "libx.dylib" in d["dylibs"], d["dylibs"]
    assert "evil_check" in d["symbols"] and "strncmp" in d["symbols"]
    assert d["entryoff"] == "0x40"
    print("macho_info selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="Mach-O inventory")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--symbols-only", action="store_true")
    ap.add_argument("--slice", type=int, default=0)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("binary path required")
    d = parse(open(a.path, "rb").read(), a.slice)
    if a.symbols_only:
        d = {"symbols": d.get("symbols"), "dylibs": d.get("dylibs")}
    print(json.dumps(d, indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
