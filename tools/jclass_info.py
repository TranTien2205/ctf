#!/usr/bin/env python3
"""jclass_info.py -- .class file reader: constant pool, methods, strings.

Usage:
  python3 tools/jclass_info.py Main.class
  python3 tools/jclass_info.py Main.class --strings
  python3 tools/jclass_info.py --selftest

Class layout: 0xCAFEBABE, minor/major u16, cp_count u16 then
constant_pool entries by tag (1 Utf8, 3/4 Int/Float u32, 5/6
Long/Double u64 taking TWO slots, 7 Class, 8 String, 9/10/11 refs,
12 NameAndType, 15/16/17/18 method-handle family, 19/20 module).
After the pool: access u16, this/super u16, interfaces, fields,
methods (each = access, name idx, descriptor idx, attributes),
then class attributes. String constants + referenced method names
are where a flag check usually shows itself.
"""
import argparse
import json
import struct
import sys
import tempfile
from pathlib import Path

MAJORS = {45: "1.1", 46: "1.2", 47: "1.3", 48: "1.4", 49: "5",
          50: "6", 51: "7", 52: "8", 53: "9", 54: "10", 55: "11",
          56: "12", 57: "13", 58: "14", 59: "15", 60: "16",
          61: "17", 62: "18", 63: "19", 64: "20", 65: "21",
          66: "22", 67: "23"}


def parse(d):
    if d[:4] != b"\xca\xfe\xba\xbe":
        raise ValueError("not a .class file")
    minor, major, cp_count = struct.unpack(">HHH", d[4:10])
    cp, i = [None] * cp_count, 10
    n = 1
    while n < cp_count:
        tag = d[i]
        if tag == 1:
            ln = struct.unpack(">H", d[i + 1:i + 3])[0]
            cp[n] = ("Utf8", d[i + 3:i + 3 + ln]
                     .decode("utf-8", "replace"))
            i += 3 + ln
        elif tag in (3, 4):
            cp[n] = ("Int" if tag == 3 else "Float",
                     struct.unpack(">i" if tag == 3 else ">f",
                                   d[i + 1:i + 5])[0])
            i += 5
        elif tag in (5, 6):
            cp[n] = ("Long" if tag == 5 else "Double",
                     struct.unpack(">q" if tag == 5 else ">d",
                                   d[i + 1:i + 9])[0])
            i += 9
            n += 1                          # two slots
        elif tag in (7, 8, 16, 19, 20):
            name = {7: "Class", 8: "String", 16: "MethodType",
                    19: "Module", 20: "Package"}[tag]
            cp[n] = (name, struct.unpack(">H", d[i + 1:i + 3])[0])
            i += 3
        elif tag in (9, 10, 11, 12, 17, 18):
            name = {9: "Fieldref", 10: "Methodref",
                    11: "IfaceMethodref", 12: "NameAndType",
                    17: "Dynamic", 18: "InvokeDynamic"}[tag]
            cp[n] = (name, struct.unpack(">HH", d[i + 1:i + 5]))
            i += 5
        elif tag == 15:
            cp[n] = ("MethodHandle",
                     (d[i + 1], struct.unpack(">H", d[i + 2:i + 4])[0]))
            i += 4
        else:
            raise ValueError(f"unknown cp tag {tag} @cp[{n}]")
        n += 1

    def u(idx):
        e = cp[idx]
        return e[1] if e and e[0] == "Utf8" else f"#{idx}"

    def cls(idx):
        e = cp[idx]
        return u(e[1]) if e and e[0] == "Class" else f"#{idx}"

    def nat(idx):
        e = cp[idx]
        if e and e[0] == "NameAndType":
            return u(e[1][0]), u(e[1][1])
        return f"#{idx}", "?"

    pos = i
    access, this, sup = struct.unpack(">HHH", d[pos:pos + 6])
    pos += 6
    icount = struct.unpack(">H", d[pos:pos + 2])[0]
    pos += 2 + icount * 2

    def members():
        nonlocal pos
        cnt = struct.unpack(">H", d[pos:pos + 2])[0]
        pos += 2
        out = []
        for _ in range(cnt):
            acc, nm, ds, ac = struct.unpack(">HHHH", d[pos:pos + 8])
            pos += 8
            for _ in range(ac):
                _, ln = struct.unpack(">HI", d[pos:pos + 6])
                pos += 6 + ln
            out.append({"name": u(nm), "desc": u(ds),
                        "access": acc})
        return out

    fields, methods = members(), members()
    acount = struct.unpack(">H", d[pos:pos + 2])[0]
    pos += 2
    source = None
    for _ in range(acount):
        nm, ln = struct.unpack(">HI", d[pos:pos + 6])
        if u(nm) == "SourceFile" and ln == 2:
            source = u(struct.unpack(">H", d[pos + 6:pos + 8])[0])
        pos += 6 + ln

    refs = []
    for e in cp:
        if e and e[0] in ("Methodref", "IfaceMethodref",
                          "Fieldref"):
            cn = cls(e[1][0])
            nm, ds = nat(e[1][1])
            refs.append({"kind": e[0], "class": cn,
                         "name": nm, "desc": ds})
    strings = [e[1] for e in cp if e and e[0] == "Utf8"]
    return {
        "class": cls(this), "super": cls(sup),
        "java": MAJORS.get(major, f"major-{major}"),
        "major": major, "minor": minor, "source": source,
        "cp_entries": cp_count,
        "fields": fields, "methods": methods,
        "refs": refs,
        "strings": [s for s in strings
                    if any(32 <= ord(c) < 127 for c in s)]}


def _selftest():
    # minimal class: public class Main { public static void main(){} }
    cp = [(None,), (1, b"Main"), (7, 1), (1, b"java/lang/Object"),
          (7, 3), (1, b"main"), (1, b"()V"), (1, b"flag{in_cp}"),
          (12, 5, 6), (10, 4, 8), (1, b"Code"),
          (1, b"SourceFile"), (1, b"Main.java")]
    d = bytearray(b"\xca\xfe\xba\xbe" + struct.pack(">HHH", 0, 52,
                                                    len(cp)))
    for e in cp[1:]:
        if e[0] == 1:
            d += bytes([1]) + struct.pack(">H", len(e[1])) + e[1]
        elif e[0] == 7:
            d += bytes([7]) + struct.pack(">H", e[1])
        elif e[0] == 12:
            d += bytes([12]) + struct.pack(">HH", *e[1:])
        elif e[0] == 10:
            d += bytes([10]) + struct.pack(">HH", *e[1:])
    d += struct.pack(">HHH", 0x0021, 2, 4)     # access, this, super
    d += struct.pack(">H", 0)                  # interfaces
    d += struct.pack(">H", 0)                  # fields
    d += struct.pack(">H", 1)                  # methods: main()
    d += struct.pack(">HHHH", 0x0009, 5, 6, 1)
    d += struct.pack(">HI", 10, 2) + b"\x00\x00"   # Code attr (stub)
    d += struct.pack(">H", 1)                  # class attrs
    d += struct.pack(">HI", 11, 2) + struct.pack(">H", 12)
    info = parse(bytes(d))
    assert info["class"] == "Main" and info["super"] == \
        "java/lang/Object", info
    assert info["java"] == "8" and info["source"] == "Main.java"
    assert info["methods"][0]["name"] == "main"
    assert info["refs"][0]["kind"] == "Methodref" and \
        info["refs"][0]["class"] == "java/lang/Object"
    assert "flag{in_cp}" in info["strings"]
    print("jclass_info selftest: ok")


def main():
    ap = argparse.ArgumentParser(
        description="read .class constant pool, methods, strings")
    ap.add_argument("file", nargs="?")
    ap.add_argument("--strings", action="store_true",
                    help="print Utf8 pool entries only")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.file:
        ap.error("file required")
    info = parse(Path(a.file).read_bytes())
    if a.strings:
        for s in info["strings"]:
            print(s)
    else:
        print(json.dumps(info, indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
