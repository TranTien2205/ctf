#!/usr/bin/env python3
"""ELF symbols, sections, imports and entry — readelf/nm absent.

rev-triage's deciding-check hunt starts from imports and symbol names
(strcmp, memcmp, crypto calls name the check for you). This is the
bounded stdlib read: ELF header, section table, .dynsym + .symtab name
lists, DT_NEEDED shared libraries, program headers, and — for ET_CORE
files — the PT_NOTE payload: NT_PRSTATUS registers and pid, NT_PRPSINFO
argv, and the NT_FILE memory-to-path map that names where the flag
lived in the dead process.

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
    phdrs = []
    for i in range(phnum):
        o = phoff + i * phentsz
        if o + phentsz > len(data):
            break
        if cls == 64:
            pt, fl, po, va, _pa, fsz, _msz, _al = struct.unpack(
                e + "IIQQQQQQ", data[o:o + 56])
        else:
            pt, po, va, _pa, fsz, _msz, fl, _al = struct.unpack(
                e + "IIIIIIII", data[o:o + 32])
        phdrs.append({"type": pt, "off": po, "vaddr": va,
                      "filesz": fsz, "flags": fl})
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
    notes = {}
    if etype == 4:                                   # ET_CORE
        for p in phdrs:
            if p["type"] != 4:                       # PT_NOTE
                continue
            blob = data[p["off"]:p["off"] + p["filesz"]]
            q = 0
            while q + 12 <= len(blob):
                nsz, dsz, ntyp = struct.unpack(e + "III", blob[q:q + 12])
                name = blob[q + 12:q + 12 + nsz].rstrip(b"\x00")
                desc_off = (q + 12 + nsz + 3) & ~3
                desc = blob[desc_off:desc_off + dsz]
                q = (desc_off + dsz + 3) & ~3
                if ntyp == 1:                        # NT_PRSTATUS
                    if len(desc) >= 112 + 27 * 8:
                        r = struct.unpack(e + "27Q",
                                          desc[112:112 + 216])
                        names = ["r15", "r14", "r13", "r12", "rbp",
                                 "rbx", "r11", "r10", "r9", "r8",
                                 "rax", "rcx", "rdx", "rsi", "rdi",
                                 "orig_rax", "rip", "cs", "eflags",
                                 "rsp", "ss", "fs_base", "gs_base",
                                 "ds", "es", "fs", "gs"]
                        notes["prstatus_regs"] = {
                            n: hex(v) for n, v in zip(names, r)}
                    if len(desc) >= 48:
                        notes["prstatus_pid"] = struct.unpack(
                            e + "i", desc[32:36])[0]
                elif ntyp == 2:                      # NT_FPREGSET
                    notes.setdefault("fpregset_sizes", []).append(len(desc))
                elif ntyp == 3:                      # NT_PRPSINFO
                    if len(desc) >= 124:
                        notes["prpsinfo"] = {
                            "fname": desc[28:44].rstrip(b"\x00").decode(
                                "utf-8", "replace"),
                            "psargs": desc[44:124].rstrip(b"\x00").decode(
                                "utf-8", "replace")}
                elif ntyp == 0x46494C45:             # NT_FILE
                    if len(desc) >= 16:
                        cnt, _pgsz = struct.unpack(e + "QQ", desc[:16])
                        moff = 16
                        maps = []
                        for _ in range(cnt):
                            if moff + 24 > len(desc):
                                break
                            st, en, fo = struct.unpack(
                                e + "QQQ", desc[moff:moff + 24])
                            maps.append({"start": hex(st),
                                         "end": hex(en),
                                         "file_ofs": fo})
                            moff += 24
                        fnames = desc[moff:].split(b"\x00")
                        for m, fn in zip(maps, fnames):
                            m["file"] = fn.decode("utf-8", "replace")
                        notes["mapped_files"] = maps
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
    out = {"class": cls, "type": ETYPE.get(etype, etype),
           "machine": EMACHINE.get(mach, mach),
           "entry": hex(entry),
           "program_headers": phdrs,
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
    if notes:
        out["core_notes"] = notes
    return out


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

    # ET_CORE with one PT_NOTE: NT_PRSTATUS + NT_FILE
    pr = bytearray(112 + 27 * 8)
    struct.pack_into(e + "i", pr, 32, 4242)          # pid
    struct.pack_into(e + "27Q", pr, 112,
                     *range(27))                     # regs r15..gs
    ps = bytearray(124)
    ps[28:44] = b"flagd\x00".ljust(16, b"\x00")
    ps[44:124] = b"./flagd --secret\x00".ljust(80, b"\x00")
    nf = struct.pack(e + "QQ", 1, 0x1000)
    nf += struct.pack(e + "QQQ", 0x7F0000, 0x7F1000, 0)
    nf += b"/home/u/flag.txt\x00"
    def note(nm, typ, desc):
        nb = nm + b"\x00"
        out = struct.pack(e + "III", len(nb), len(desc), typ) + nb
        out += b"\x00" * ((4 - len(out) % 4) % 4) + desc
        out += b"\x00" * ((4 - len(out) % 4) % 4)
        return out
    nblob = (note(b"CORE", 1, bytes(pr)) + note(b"CORE", 3, bytes(ps))
             + note(b"LINUX", 0x46494C45, nf))
    c = bytearray(64 + 56 + len(nblob))
    c[:4] = b"\x7fELF"
    c[4], c[5] = 2, 1
    struct.pack_into(e + "HHIQQQIHHHHHH", c, 16, 4, 62, 1, 0,
                     64, 0, 0, 64, 56, 1, 0, 0, 0)
    struct.pack_into(e + "IIQQQQQQ", c, 64, 4, 0, 120, 0, 0,
                     len(nblob), len(nblob), 4)
    c[120:120 + len(nblob)] = nblob
    cd = parse_elf(bytes(c))
    assert cd["type"] == "CORE", cd["type"]
    regs = cd["core_notes"]["prstatus_regs"]
    assert regs["rip"] == hex(16), regs
    assert cd["core_notes"]["prstatus_pid"] == 4242
    maps = cd["core_notes"]["mapped_files"]
    assert maps[0]["file"] == "/home/u/flag.txt", maps
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
