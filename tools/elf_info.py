#!/usr/bin/env python3
"""ELF symbols, sections, imports and entry — readelf/nm absent.

rev-triage's deciding-check hunt starts from imports and symbol names
(strcmp, memcmp, crypto calls name the check for you). This is the
bounded stdlib read: ELF header, section table, .dynsym + .symtab name
lists, DT_NEEDED shared libraries, program headers for entry/segments.

  python3 tools/elf_info.py ./bin
  python3 tools/elf_info.py ./bin --symbols-only
  python3 tools/elf_info.py --selftest

Static reading only — no disassembly, and it says so. Stripped
binaries report 'no symtab'; dynamic symbols still answer 'what does
it call'. 32-bit and 64-bit, both endiannesses.
"""
import argparse, json, struct, sys

EMACHINE = {3: "x86", 62: "x86-64", 40: "ARM", 183: "AArch64",
            8: "MIPS", 243: "RISC-V", 20: "PPC", 42: "SuperH"}
ETYPE = {1: "REL", 2: "EXEC", 3: "DYN", 4: "CORE"}


def _cstr(strtab, off):
    end = strtab.find(b"\x00", off)
    return strtab[off:end].decode("utf-8", "replace") if off < len(strtab) \
        else ""


def parse_elf(data):
    if data[:4] != b"\x7fELF":
        return {"error": "not ELF — file_type.py routes other formats"}
    cls, e = (64, "<") if data[4] == 2 else (32, ">")
    if data[5] == 2:
        e = ">"
    if cls == 64:
        (etype, mach, _ver, entry, phoff, shoff, _fl, _eh, phentsz,
         phnum, shentsz, shnum, shstr) = struct.unpack(
            e + "HHIQQQIHHHHHH", data[16:64])
    else:
        (etype, mach, _ver, entry, phoff, shoff, _fl, _eh, phentsz,
         phnum, shentsz, shnum, shstr) = struct.unpack(
            e + "HHIIIIIHHHHHH", data[16:52])
    secs = []
    for i in range(shnum):
        o = shoff + i * shentsz
        if o + shentsz > len(data):
            break
        if cls == 64:
            name, typ, flags, addr, off, sz = struct.unpack(
                e + "IIQQQQ", data[o:o + 40])[:6]
            link = struct.unpack(e + "I", data[o + 40:o + 44])[0]
            entsz = struct.unpack(e + "Q", data[o + 56:o + 64])[0]
        else:
            name, typ, flags, addr, off, sz = struct.unpack(
                e + "IIIIII", data[o:o + 24])[:6]
            link = struct.unpack(e + "I", data[o + 40:o + 44])[0]
            entsz = struct.unpack(e + "I", data[o + 36:o + 40])[0]
        secs.append({"name_off": name, "type": typ, "addr": addr,
                     "off": off, "size": sz, "link": link,
                     "entsize": entsz})
    shstrtab = b""
    if shstr < len(secs):
        s = secs[shstr]
        shstrtab = data[s["off"]:s["off"] + s["size"]]
    for s in secs:
        s["name"] = _cstr(shstrtab, s["name_off"])

    def secdata(name):
        for s in secs:
            if s["name"] == name:
                return s, data[s["off"]:s["off"] + s["size"]]
        return None, b""

    dynsym, symtab, dynsym_all = [], [], []
    for tab_name, into in ((".dynsym", dynsym), (".symtab", symtab)):
        s, blob = secdata(tab_name)
        if not s:
            continue
        strs_sec = secs[s["link"]] if s["link"] < len(secs) else None
        strs = data[strs_sec["off"]:strs_sec["off"] + strs_sec["size"]] \
            if strs_sec else b""
        entsz = s["entsize"] or (24 if cls == 64 else 16)
        for o in range(0, len(blob) - entsz + 1, entsz):
            if cls == 64:
                no, info, _oth, _sh, _v, _sz = struct.unpack(
                    e + "IBBHQQ", blob[o:o + 24])
            else:
                no, _v, _sz, info, _oth, _sh = struct.unpack(
                    e + "IIIBBH", blob[o:o + 16])
            nm = _cstr(strs, no)
            if tab_name == ".dynsym":
                dynsym_all.append(nm)
            if nm:
                into.append(nm)
    relocs = []
    for s in secs:
        if s["type"] not in (4, 9) or not s["name"]:
            continue                      # SHT_RELA=4, SHT_REL=9
        s2, blob = secdata(s["name"])
        entsz = s["entsize"] or (24 if (cls == 64 and s["type"] == 4)
                                 else 16 if cls == 64
                                 else 12 if s["type"] == 4 else 8)
        for o in range(0, len(blob) - entsz + 1, entsz):
            if cls == 64:
                off, info = struct.unpack(e + "QQ", blob[o:o + 16])
                si, typ = info >> 32, info & 0xFFFFFFFF
            else:
                off, info = struct.unpack(e + "II", blob[o:o + 8])
                si, typ = info >> 8, info & 0xFF
            relocs.append({"section": s["name"], "offset": hex(off),
                           "symbol": dynsym_all[si]
                           if si < len(dynsym_all) else None,
                           "type": typ})
    needed = []
    s, dyn = secdata(".dynamic")
    strs = b""
    for cand in (".dynstr", ".strtab"):
        _s2, strs = secdata(cand)
        if strs:
            break
    if dyn and strs:
        entsz = 16 if cls == 64 else 8
        for o in range(0, len(dyn) - entsz + 1, entsz):
            if cls == 64:
                tag, val = struct.unpack(e + "qQ", dyn[o:o + 16])
            else:
                tag, val = struct.unpack(e + "iI", dyn[o:o + 8])
            if tag == 0:
                break
            if tag == 1:
                needed.append(_cstr(strs, val))
    imports = [s for s in dynsym if not s.startswith("_")]
    interesting = [s for s in imports
                   if any(k in s.lower() for k in
                          ("cmp", "str", "mem", "crypt", "aes", "rc4",
                           "md5", "sha", "xor", "chk", "verif", "pass"))]
    return {"class": cls, "type": ETYPE.get(etype, etype),
            "machine": EMACHINE.get(mach, mach),
            "entry": hex(entry),
            "needed_libs": needed,
            "sections": [{"name": s["name"], "addr": hex(s["addr"]),
                          "size": s["size"]} for s in secs if s["name"]],
            "dynamic_symbols": dynsym,
            "static_symbols": symtab if symtab else "no symtab (stripped?)",
            "relocations": relocs,
            "got_write_targets": [r for r in relocs
                                  if r["section"].endswith(".plt")
                                  and r["symbol"]],
            "deciding_check_hints": interesting,
            "note": "static read only — no disassembly; interesting "
                    "imports name the check, they do not prove it"}


def _selftest() -> int:
    """Hand-built 64-bit ELF: .dynsym(2 syms) + .dynstr + .dynamic(NEEDED)
    + .shstrtab, laid out sequentially after the ELF header."""
    e = "<"
    dynstr = b"\x00strcmp\x00evil_check\x00libc.so.6\x00"
    sym = struct.pack(e + "IBBHQQ", 1, 0x12, 0, 0, 0, 0)
    sym += struct.pack(e + "IBBHQQ", 8, 0x12, 0, 0, 0, 0)
    dyn = struct.pack(e + "qQ", 1, 19) + struct.pack(e + "qQ", 0, 0)
    rela = struct.pack(e + "QQq", 0x404018, (0 << 32) | 7, 0)
    shstr = (b"\x00.dynsym\x00.dynstr\x00.dynamic\x00.shstrtab\x00"
             b".rela.plt\x00")
    names = {n: shstr.index(n.encode())
             for n in (".dynsym", ".dynstr", ".dynamic", ".shstrtab",
                       ".rela.plt")}
    # layout: hdr(64) | dynsym | dynstr | dynamic | rela | shstr | shdrs
    dynsym_off, dynstr_off = 64, 64 + len(sym)
    dyn_off = dynstr_off + len(dynstr)
    rela_off = dyn_off + len(dyn)
    shstr_off = rela_off + len(rela)
    shoff = (shstr_off + len(shstr) + 63) & ~63
    shnum, shstrndx = 6, 4
    body = bytearray(shoff + shnum * 64)
    body[:4] = b"\x7fELF"
    body[4], body[5] = 2, 1
    struct.pack_into(e + "HHIQQQIHHHHHH", body, 16, 2, 62, 1, 0x401000,
                     0, shoff, 0, 64, 0, 0, 64, shnum, shstrndx)
    body[dynsym_off:dynsym_off + len(sym)] = sym
    body[dynstr_off:dynstr_off + len(dynstr)] = dynstr
    body[dyn_off:dyn_off + len(dyn)] = dyn
    body[rela_off:rela_off + len(rela)] = rela
    body[shstr_off:shstr_off + len(shstr)] = shstr
    for i, (nm, typ, off, sz, link, es) in enumerate([
            (".dynsym", 11, dynsym_off, len(sym), 2, 24),
            (".dynstr", 3, dynstr_off, len(dynstr), 0, 0),
            (".dynamic", 6, dyn_off, len(dyn), 2, 16),
            (".shstrtab", 3, shstr_off, len(shstr), 0, 0),
            (".rela.plt", 4, rela_off, len(rela), 1, 24)]):
        struct.pack_into(e + "IIQQQQIIQQ", body,
                         shoff + (i + 1) * 64, names[nm], typ, 0, 0,
                         off, sz, link, 0, 8, es)
    d = parse_elf(bytes(body))
    assert d["machine"] == "x86-64", d
    assert "strcmp" in d["dynamic_symbols"], d["dynamic_symbols"]
    assert "evil_check" in d["dynamic_symbols"]
    assert "libc.so.6" in d["needed_libs"], d["needed_libs"]
    assert any("cmp" in s for s in d["deciding_check_hints"])
    got = d["got_write_targets"]
    assert got and got[0]["symbol"] == "strcmp" \
        and got[0]["offset"] == "0x404018", got
    print("elf_info selftest: ok")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("path", nargs="?")
    ap.add_argument("--symbols-only", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("a binary path is required")
    d = parse_elf(open(a.path, "rb").read())
    if a.symbols_only:
        d = {"dynamic_symbols": d.get("dynamic_symbols"),
             "static_symbols": d.get("static_symbols"),
             "deciding_check_hints": d.get("deciding_check_hints")}
    print(json.dumps(d, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
