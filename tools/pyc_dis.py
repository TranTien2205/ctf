#!/usr/bin/env python3
"""pyc_dis.py -- disassemble a .pyc with the stdlib (no decompiler).

Usage:
  python3 tools/pyc_dis.py file.pyc
  python3 tools/pyc_dis.py file.pyc --strings
  python3 tools/pyc_dis.py --selftest

Reads the magic, names the CPython version (the marshal format is
version-locked - a wrong-version file is reported, not misread),
locates the code object past the 12- or 16-byte header, and dumps
dis output plus constants, names and flag-shaped strings for every
nested code object.
"""
import argparse
import dis
import json
import marshal
import re
import struct
import sys
import tempfile
import types
from pathlib import Path

# u16 of the first two magic bytes -> CPython version (source:
# CPython Lib/importlib/_bootstrap_external.py MAGIC_NUMBER history)
_MAGICS = {
    3394: "3.10", 3439: "3.11", 3531: "3.12", 3571: "3.13",
    3340: "3.9", 3420: "3.11a", 3300: "3.8", 3400: "3.9a",
    20121: "2.7", 3310: "3.8a", 3350: "3.10a", 3450: "3.12a",
}


def load_pyc(path):
    raw = Path(path).read_bytes()
    if len(raw) < 12:
        return {"error": "too small for a .pyc"}
    magic = struct.unpack("<H", raw[:2])[0]
    ver = _MAGICS.get(magic)
    # 12-byte header pre-3.7, 16 bytes since (flags+hash/timestamp)
    for hlen in (16, 12):
        try:
            co = marshal.loads(raw[hlen:])
            if isinstance(co, types.CodeType):
                return {"magic": magic, "version_hint": ver,
                        "header": hlen, "code": co}
        except Exception:
            continue
    return {"error": "marshal.loads failed at 16 and 12 - version "
                     "mismatch or not a code object",
            "magic": magic, "version_hint": ver}


def _walk(co, out):
    out.append(co)
    for c in co.co_consts:
        if isinstance(c, types.CodeType):
            _walk(c, out)
    return out


def report(path, strings_only=False):
    r = load_pyc(path)
    if "code" not in r:
        return r
    cos = _walk(r.pop("code"), [])
    objs = []
    for co in cos:
        strs = [c for c in co.co_consts if isinstance(c, str)]
        objs.append({
            "name": co.co_name, "argcount": co.co_argcount,
            "consts_strings": strs,
            "names": list(co.co_names),
            "flags": [s for s in strs if re.search(
                r"(flag|ctf|key|pass|secret)", s, re.I)],
            "dis": None if strings_only else "\n".join(
                f"{i.offset:4d} {i.opname:24s} {i.argrepr}"
                for i in dis.get_instructions(co))})
    r["objects"] = objs
    return r


def _selftest():
    src = ("def f(p):\n"
           "    return 'flag{pyc_dis}' if p == 'open' else None\n")
    co = compile(src, "<t>", "exec")
    tmp = Path(tempfile.mkdtemp()) / "t.pyc"
    tmp.write_bytes(struct.pack("<II", _magic(), 0)
                    + b"\x00" * 8 + marshal.dumps(co))
    out = report(tmp)
    objs = out["objects"]
    assert objs[0]["name"] == "f" or any(
        o["name"] == "f" for o in objs), objs
    fns = [o for o in objs if o["name"] == "f"]
    assert fns and "flag{pyc_dis}" in fns[0]["consts_strings"], fns
    assert "cmp_op" in fns[0]["dis"] or "COMPARE" in fns[0]["dis"], \
        fns[0]["dis"]
    print("pyc_dis selftest: ok")


def _magic():
    import importlib.util
    return struct.unpack("<H",
                         importlib.util.MAGIC_NUMBER[:2])[0]


def main():
    ap = argparse.ArgumentParser(
        description="disassemble a .pyc with the stdlib")
    ap.add_argument("file", nargs="?")
    ap.add_argument("--strings", action="store_true",
                    help="constants/names only, skip dis listing")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.file:
        ap.error("file required")
    print(json.dumps(report(a.file, a.strings), indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
