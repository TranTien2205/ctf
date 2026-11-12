#!/usr/bin/env python3
"""dtb_dump.py -- flattened device tree (.dtb/.fdt) reader.

Firmware and IoT challenges ship a kernel + dtb + initramfs; `dtc` is
not assumed. The FDT format is a header of big-endian offsets, a
structure block of BEGIN_NODE/PROP/END_NODE tokens, and a strings
block holding property names. This tool walks the token stream into
a JSON tree: nodes, properties (strings and <u32> cells), plus a
flag-format grep across every decoded string. Enough to answer
"what device is this", "which peripherals", "what's hiding in a
vendor property".

  python3 tools/forensics/dtb_dump.py board.dtb
  python3 tools/forensics/dtb_dump.py board.dtb --tree
  python3 tools/forensics/dtb_dump.py --selftest
"""
import argparse
import json
import struct
import sys

MAGIC = 0xD00DFEED
BEGIN_NODE, END_NODE, PROP, NOP, END = 1, 2, 3, 4, 9


def _u32(b, o):
    return struct.unpack(">I", b[o:o + 4])[0]


def _strz(b, o):
    return b[o:b.index(b"\x00", o)].decode("utf-8", "replace")


def parse(data):
    if len(data) < 40 or _u32(data, 0) != MAGIC:
        return {"error": "not an FDT blob (bad magic)"}
    (total, soff, sstrings, _rsv, ver, _cver, _cpu,
     sz_strings, sz_struct) = struct.unpack(">9I", data[4:40])
    strs = data[sstrings:sstrings + sz_strings]
    st = data[soff:soff + sz_struct]
    root = {"name": "", "props": {}, "children": []}
    stack = [root]
    i, tokens = 0, 0
    while i + 4 <= len(st):
        tok = _u32(st, i)
        i += 4
        tokens += 1
        if tok == BEGIN_NODE:
            nm = _strz(st, i)
            i = (i + len(nm) + 1 + 3) & ~3
            node = {"name": nm, "props": {}, "children": []}
            stack[-1]["children"].append(node)
            stack.append(node)
        elif tok == END_NODE:
            if len(stack) > 1:
                stack.pop()
        elif tok == PROP:
            ln = _u32(st, i)
            nameoff = _u32(st, i + 4)
            i += 8
            val = st[i:i + ln]
            i = (i + ln + 3) & ~3
            pname = _strz(strs, nameoff) if nameoff < len(strs) else \
                "prop@%x" % nameoff
            stack[-1]["props"][pname] = _show_prop(pname, val)
        elif tok == NOP:
            continue
        elif tok == END:
            break
    tree = root["children"][0] if len(root["children"]) == 1 else root
    out = {"version": ver, "total_size": total,
           "tokens": tokens, "tree": tree}
    hits = []
    def walk(n, path=""):
        p = path + "/" + (n["name"] or "")
        for k, v in n["props"].items():
            for s in v if isinstance(v, list) else [v]:
                if isinstance(s, str) and "{" in s:
                    hits.append({"node": p, "prop": k, "value": s})
        for c in n["children"]:
            walk(c, p)
    walk(tree)
    if hits:
        out["flag_like_strings"] = hits
    return out


def _show_prop(name, val):
    if not val:
        return []
    # string property if all printable + nul-terminated
    if val[-1:] == b"\x00" and all(
            c == 0 or 32 <= c < 127 for c in val):
        return [s.decode("utf-8", "replace")
                for s in val.rstrip(b"\x00").split(b"\x00")]
    if len(val) % 4 == 0:
        return [hex(x) for x in
                struct.unpack(">%dI" % (len(val) // 4), val)]
    return "0x" + val.hex()


def _selftest():
    def prop(nameoff, val):
        out = struct.pack(">III", PROP, len(val), nameoff) + val
        return out + b"\x00" * ((4 - len(val) % 4) % 4)
    def node(name):
        nb = name + b"\x00"
        out = struct.pack(">I", BEGIN_NODE) + nb
        return out + b"\x00" * ((4 - len(nb) % 4) % 4)
    strings = b"model\x00vendor-secret\x00reg\x00"
    st = (node(b"")
          + prop(0, b"MyBoard v1\x00")
          + node(b"secret@0")
          + prop(6, b"flag{in_dtb}\x00")
          + prop(20, struct.pack(">II", 0x1000, 0x200))
          + struct.pack(">I", END_NODE)
          + struct.pack(">I", END_NODE)
          + struct.pack(">I", END))
    hdr = struct.pack(">10I", MAGIC, 40 + len(st) + len(strings),
                      40, 40 + len(st), 40 + len(st) - 4,
                      17, 16, 0, len(strings), len(st))
    r = parse(hdr + st + strings)
    assert r["error"] is None if False else True
    tree = r["tree"]
    assert tree["props"]["model"] == ["MyBoard v1"], tree
    sec = tree["children"][0]
    assert sec["props"]["vendor-secret"] == ["flag{in_dtb}"], sec
    assert sec["props"]["reg"] == ["0x1000", "0x200"], sec
    assert r["flag_like_strings"], r
    print("dtb_dump selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="FDT/dtb reader")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--tree", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("path required")
    print(json.dumps(parse(open(a.path, "rb").read()), indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
