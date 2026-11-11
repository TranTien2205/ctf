#!/usr/bin/env python3
"""dex_info.py -- DEX (Android bytecode) strings + class inventory.

APK rev challenges ship classes.dex; dex2jar/jadx are absent. The
DEX header is fixed 0x70 bytes: string_ids (u32 offsets to
uleb128-length + MUTF-8), type_ids (u32 -> string index), class_defs
(u32 -> type index). This lists every string with flag-format hits
flagged, every class descriptor, and the checksum/map summary.

  python3 tools/dex_info.py classes.dex
  python3 tools/dex_info.py classes.dex --strings | less
  python3 tools/dex_info.py --selftest

Static read only — no disassembly (that is bytecode depth, and the
smali format wants baksmali). Enough to name the check and the
interesting constants before choosing a path.
"""
import argparse
import json
import re
import struct
import sys


def _uleb(b, i):
    v, s = 0, 0
    while i < len(b):
        c = b[i]
        i += 1
        v |= (c & 0x7F) << s
        if not c & 0x80:
            return v, i
        s += 7
    return v, i


def parse(data):
    if data[:4] != b"dex\n":
        return {"error": "not dex"}
    (ver, _csum) = data[4:8], data[8:12]
    fsz = struct.unpack("<I", data[0x20:0x24])[0]
    (nstr, soff, ntyp, toff) = struct.unpack("<4I", data[0x38:0x48])
    (ncls, coff) = struct.unpack("<2I", data[0x60:0x68])
    strings = []
    for i in range(nstr):
        so = struct.unpack("<I", data[soff + i * 4:soff + i * 4 + 4])[0]
        _ulen, p = _uleb(data, so)
        end = data.find(b"\x00", p)
        strings.append(data[p:end].decode("utf-8", "replace"))
    types = [struct.unpack("<I", data[toff + i * 4:toff + i * 4 + 4])[0]
             for i in range(ntyp)]
    classes = []
    for i in range(ncls):
        cidx, acc, sup, _if, srcf, _ann, cdo, _sv = struct.unpack(
            "<8I", data[coff + i * 32:coff + i * 32 + 32])
        classes.append({
            "descriptor": strings[types[cidx]] if cidx < len(types)
            and types[cidx] < len(strings) else f"type#{cidx}",
            "access": hex(acc),
            "super": strings[types[sup]]
            if sup != 0xFFFFFFFF and sup < len(types)
            and types[sup] < len(strings) else None,
            "source": strings[srcf]
            if srcf != 0xFFFFFFFF and srcf < len(strings) else None})
    flag_hits = [s for s in strings
                 if re.search(r"[A-Za-z0-9_]+\{[^}]{3,}\}", s)]
    interesting = [s for s in strings if re.search(
        r"(?i)(flag|pass|check|secret|key|verify|correct|wrong)", s)
        and s not in flag_hits]
    return {"version": ver.decode(), "file_size": fsz,
            "strings": len(strings), "types": ntyp,
            "classes": classes,
            "flag_strings": flag_hits,
            "interesting_strings": interesting,
            "all_strings": None}        # populated only with --strings


def _selftest():
    strs = [b"Lcom/evil/Check;", b"Lflag;", b"flag{dex_parse_ok}",
            b"wrong_password", b"java/lang/Object", b"Check.java"]
    n = len(strs)
    sid, tid, cid = 0x100, 0x100 + 4 * n, 0x100 + 4 * n + 8
    sbase = cid + 32
    sdata = b""
    soffs = []
    for s in strs:
        soffs.append(sbase + len(sdata))
        sdata += bytes([len(s)]) + s + b"\x00"
    img = bytearray(sbase + len(sdata))
    img[sbase:sbase + len(sdata)] = sdata
    img[0:8] = b"dex\n035\x00"
    struct.pack_into("<I", img, 0x20, len(img))
    struct.pack_into("<4I", img, 0x38, n, sid, 2, tid)
    struct.pack_into("<2I", img, 0x60, 1, cid)
    for i, o in enumerate(soffs):
        struct.pack_into("<I", img, sid + i * 4, o)
    struct.pack_into("<II", img, tid, 0, 1)   # type0->str0, type1->str1
    struct.pack_into("<8I", img, cid,
                     0, 1, 0xFFFFFFFF, 0, 5, 0, 0, 0)
    d = parse(bytes(img))
    assert d["flag_strings"] == ["flag{dex_parse_ok}"], d
    assert d["classes"][0]["descriptor"] == "Lcom/evil/Check;"
    assert d["classes"][0]["source"] == "Check.java"
    assert any("password" in s for s in d["interesting_strings"])
    print("dex_info selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="DEX inventory")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--strings", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("dex path required")
    data = open(a.path, "rb").read()
    d = parse(data)
    if "error" not in d and a.strings:
        (nstr, soff) = struct.unpack("<2I", data[0x38:0x40])
        d["all_strings"] = [
            data[(p := _uleb(data, struct.unpack(
                "<I", data[soff + i * 4:soff + i * 4 + 4])[0])[1]):
                 data.find(b"\x00", p)].decode("utf-8", "replace")
            for i in range(nstr)]
    print(json.dumps(d, indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
