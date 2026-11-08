#!/usr/bin/env python3
"""PE sections, imports, exports — the Windows half of elf_info.

rev-triage's deciding-check hunt on a .exe: the import table names
what it calls (strcmp-ish CRT, crypto APIs, network), the section
table names where code lives (UPX0/UPX1 out a packer instantly), the
export table names what it offers. Stdlib PE parsing: DOS header ->
PE sig -> COFF + optional header -> section table -> import/export
directory RVA walks.

  python3 tools/pe_info.py ./bin.exe
  python3 tools/pe_info.py ./bin.exe --imports-only
  python3 tools/pe_info.py --selftest

Static reading only. Packed sections are flagged by entropy-ish name
and by raw-vs-virtual size mismatch; unpacking still needs the real
packer tool.
"""
import argparse, json, struct, sys

MACHINE = {0x14C: "x86", 0x8664: "x86-64", 0x1C0: "ARM",
           0xAA64: "ARM64", 0x1F0: "PowerPC"}
CHARS = {0x20000000: "X", 0x40000000: "R", 0x80000000: "W"}


def _cstr(data, off):
    end = data.find(b"\x00", off)
    return data[off:end].decode("latin1", "replace")


def parse_pe(data):
    if data[:2] != b"MZ":
        return {"error": "not PE — file_type.py routes other formats"}
    peoff = struct.unpack("<I", data[0x3C:0x40])[0]
    if data[peoff:peoff + 4] != b"PE\x00\x00":
        return {"error": "no PE signature at e_lfanew"}
    coff = peoff + 4
    machine, nsec, _ts, _ps, _ns, optsz, chars = struct.unpack(
        "<HHIIIHH", data[coff:coff + 20])
    opt = coff + 20
    magic = struct.unpack("<H", data[opt:opt + 2])[0]
    is64 = magic == 0x20B
    if magic not in (0x10B, 0x20B):
        return {"error": "unknown optional-header magic 0x%x" % magic}
    entry = struct.unpack("<I", data[opt + 16:opt + 20])[0]
    imagebase = struct.unpack("<Q" if is64 else "<I",
                              data[opt + 24:opt + (32 if is64 else 28)])[0]
    # data directories: after fixed optional header (96 for 32, 112 for 64)
    dd = opt + (112 if is64 else 96)
    dirs = {}
    for i, name in enumerate(["export", "import", "resource", "exception",
                              "security", "reloc", "debug", "arch",
                              "global", "tls", "config", "bound",
                              "iat", "delay", "clr", "reserved"]):
        rva, sz = struct.unpack("<II", data[dd + i * 8:dd + i * 8 + 8])
        if rva:
            dirs[name] = (rva, sz)
    secs = []
    soff = opt + optsz
    for i in range(nsec):
        o = soff + i * 40
        if o + 40 > len(data):
            break
        nm = data[o:o + 8].rstrip(b"\x00").decode("latin1", "replace")
        vsz, va, rsz, roff = struct.unpack("<IIII", data[o + 8:o + 24])
        ch = struct.unpack("<I", data[o + 36:o + 40])[0]
        secs.append({"name": nm, "vsize": vsz, "rva": va, "raw_size": rsz,
                     "raw_off": roff,
                     "flags": "".join(v for k, v in CHARS.items()
                                      if ch & k)})

    def rva2off(rva):
        for s in secs:
            if s["rva"] <= rva < s["rva"] + max(s["vsize"], s["raw_size"]):
                return s["raw_off"] + (rva - s["rva"])
        return None

    imports = {}
    if "import" in dirs:
        off = rva2off(dirs["import"][0])
        if off is not None:
            for i in range(256):
                d = data[off + i * 20:off + i * 20 + 20]
                if len(d) < 20:
                    break
                oft, _t, _f, nrva, ft = struct.unpack("<IIIII", d)
                if not (oft or nrva or ft):
                    break
                dll = _cstr(data, rva2off(nrva) or 0)
                thunk_rva = oft or ft
                toff = rva2off(thunk_rva)
                funcs = []
                tsz = 8 if is64 else 4
                if toff is not None:
                    for j in range(1024):
                        tv = struct.unpack(
                            "<Q" if is64 else "<I",
                            data[toff + j * tsz:
                                 toff + j * tsz + tsz])[0]
                        if not tv:
                            break
                        if is64 and tv & (1 << 63) or \
                           not is64 and tv & (1 << 31):
                            funcs.append("ord%d" % (tv & 0xFFFF))
                        else:
                            noff = rva2off(tv)
                            if noff:
                                funcs.append(_cstr(data, noff + 2))
                imports[dll] = funcs
    exports = []
    if "export" in dirs:
        off = rva2off(dirs["export"][0])
        if off is not None:
            try:
                # +20 nfuncs, +24 nnames, +28 funcs rva, +32 names rva
                nn = struct.unpack("<I", data[off + 24:off + 28])[0]
                fn = struct.unpack("<I", data[off + 32:off + 36])[0]
                noff = rva2off(fn)
                if noff:
                    for i in range(nn):
                        nrva = struct.unpack(
                            "<I", data[noff + i * 4:noff + i * 4 + 4])[0]
                        s = rva2off(nrva)
                        if s:
                            exports.append(_cstr(data, s))
            except (struct.error, IndexError):
                pass
    packed = [s["name"] for s in secs
              if s["name"].upper().startswith(("UPX", ".MPRESS", "ASPACK",
                                               "PEC", "THEMIDA", ".VMP"))
              or (s["raw_size"] == 0 and s["vsize"] > 0)]
    interesting = [f for funcs in imports.values() for f in funcs
                   if any(k in f.lower() for k in
                          ("cmp", "str", "mem", "crypt", "aes", "rc4",
                           "md5", "sha", "xor", "chk", "verif", "pass",
                           "decrypt"))]
    return {"machine": MACHINE.get(machine, hex(machine)),
            "bits": 64 if is64 else 32,
            "entry_rva": hex(entry), "image_base": hex(imagebase),
            "characteristics": hex(chars),
            "sections": secs,
            "imports": imports,
            "exports": exports,
            "packed_suspects": packed,
            "deciding_check_hints": interesting,
            "note": "static read only — packed_suspects names sections, "
                    "unpacking still needs the real tool"}


def _selftest() -> int:
    """Minimal 32-bit PE: DOS stub + PE + 1 section + import dir for
    one DLL with one named function."""
    dll_name = b"KERNEL32.dll\x00"
    fname = b"\x00\x00MessageBoxA\x00"
    # layout: DOS hdr -> PE@0x80 -> section table inside header zone,
    # then one section raw at 0x280 mapped to rva 0x100
    data = bytearray(0x400)
    data[:2] = b"MZ"
    peoff = 0x80
    struct.pack_into("<I", data, 0x3C, peoff)
    data[peoff:peoff + 4] = b"PE\x00\x00"
    coff = peoff + 4
    struct.pack_into("<HHIIIHH", data, coff, 0x14C, 1, 0, 0, 0, 224,
                     0x010F)
    opt = coff + 20
    struct.pack_into("<H", data, opt, 0x10B)          # PE32
    struct.pack_into("<I", data, opt + 16, 0x1000)    # entry rva
    struct.pack_into("<I", data, opt + 28, 0x400000)  # image base
    # import dir -> rva 0x100 (raw 0x280 via the section below)
    struct.pack_into("<II", data, opt + 96 + 8, 0x100, 40)
    soff = opt + 224
    data[soff:soff + 8] = b".text\x00\x00\x00"
    struct.pack_into("<IIII", data, soff + 8, 0x200, 0x100, 0x200, 0x280)
    struct.pack_into("<I", data, soff + 36, 0x60000020)
    # import descriptor at raw 0x280 (rva 0x100)
    # ILT at rva 0x130 (raw 0x2B0), name rva 0x140 (raw 0x2C0),
    # hint/name rva 0x150 (raw 0x2D0)
    struct.pack_into("<IIIII", data, 0x280, 0x130, 0, 0, 0x140, 0x130)
    struct.pack_into("<I", data, 0x2B0, 0x150)   # ILT[0]->hintname
    data[0x2C0:0x2C0 + len(dll_name)] = dll_name
    data[0x2D0:0x2D0 + len(fname)] = fname
    d = parse_pe(bytes(data))
    assert d["machine"] == "x86" and d["bits"] == 32, d
    assert "KERNEL32.dll" in d["imports"], d["imports"]
    assert d["imports"]["KERNEL32.dll"] == ["MessageBoxA"], d["imports"]
    print("pe_info selftest: ok")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("path", nargs="?")
    ap.add_argument("--imports-only", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("a binary path is required")
    d = parse_pe(open(a.path, "rb").read())
    if a.imports_only:
        d = {"imports": d.get("imports"),
             "deciding_check_hints": d.get("deciding_check_hints"),
             "packed_suspects": d.get("packed_suspects")}
    print(json.dumps(d, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
