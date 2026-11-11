#!/usr/bin/env python3
"""wasm_info.py -- WASM module inventory: sections, imports, exports.

WASM rev challenges ship a .wasm with the check compiled in and no
source. wabt/wasm2wat are absent; the module header is simple: magic
\\0asm, 4-byte version, then sections (u8 id, u32 LEB size, body).
This lists every section, decodes the import table (module.name ->
kind), the export table (name -> kind/index), the name section's
function names, and function/code counts — enough to locate the
deciding check before writing an interpreter.

  python3 tools/wasm_info.py mod.wasm
  python3 tools/wasm_info.py mod.wasm --names
  python3 tools/wasm_info.py --selftest
"""
import argparse
import json
import sys

SECT = {0: "custom", 1: "type", 2: "import", 3: "function",
        4: "table", 5: "memory", 6: "global", 7: "export",
        8: "start", 9: "element", 10: "code", 11: "data",
        12: "datacount"}
KIND = {0: "func", 1: "table", 2: "mem", 3: "global"}


def uleb(b, i):
    v, s = 0, 0
    while i < len(b):
        c = b[i]
        i += 1
        v |= (c & 0x7F) << s
        if not c & 0x80:
            return v, i
        s += 7
    return v, i


def _name(b, i):
    ln, i = uleb(b, i)
    return b[i:i + ln].decode("utf-8", "replace"), i + ln


def sections(data):
    if data[:4] != b"\x00asm":
        return {"error": "not wasm"}
    ver = int.from_bytes(data[4:8], "little")
    secs, off = [], 8
    while off + 2 <= len(data):
        sid = data[off]
        sz, p = uleb(data, off + 1)
        secs.append({"id": sid, "name": SECT.get(sid, "?"),
                     "size": sz, "offset": p})
        off = p + sz
    return {"version": ver, "sections": secs}


def imports(data, secs):
    s = next((x for x in secs if x["id"] == 2), None)
    if not s:
        return []
    b = data[s["offset"]:s["offset"] + s["size"]]
    n, i = uleb(b, 0)
    out = []
    for _ in range(n):
        mod, i = _name(b, i)
        nm, i = _name(b, i)
        kind = b[i] if i < len(b) else -1
        i += 1
        if kind == 0:
            _ti, i = uleb(b, i)
        elif kind == 1:
            i += 2
        elif kind == 2:
            fl, i = uleb(b, i)
            _mn, i = uleb(b, i)
            if fl:
                _mx, i = uleb(b, i)
        elif kind == 3:
            i += 2
        out.append({"module": mod, "name": nm,
                    "kind": KIND.get(kind, kind)})
    return out


def exports(data, secs):
    s = next((x for x in secs if x["id"] == 7), None)
    if not s:
        return []
    b = data[s["offset"]:s["offset"] + s["size"]]
    n, i = uleb(b, 0)
    out = []
    for _ in range(n):
        nm, i = _name(b, i)
        kind = b[i] if i < len(b) else -1
        idx, i = uleb(b, i + 1)
        out.append({"name": nm, "kind": KIND.get(kind, kind),
                    "index": idx})
    return out


def fn_names(data, secs):
    s = next((x for x in secs if x["id"] == 0), None)
    # find custom section literally named 'name'
    for x in secs:
        if x["id"] != 0:
            continue
        b = data[x["offset"]:x["offset"] + x["size"]]
        nm, i = _name(b, 0)
        if nm != "name":
            continue
        # subsections: id 1 = function names
        while i < len(b):
            sid = b[i]
            sz, j = uleb(b, i + 1)
            sub = b[j:j + sz]
            if sid == 1:
                cnt, k = uleb(sub, 0)
                names = {}
                for _ in range(cnt):
                    ix, k = uleb(sub, k)
                    n2, k = _name(sub, k)
                    names[ix] = n2
                return names
            i = j + sz
    return {}


def _selftest():
    def sec(i, body):
        return bytes([i]) + bytes([len(body)]) + body
    # import section: 1 import env.check func type 0
    imp = b"\x01" + b"\x03env\x05check" + b"\x00\x00"
    # export section: 1 export "run" func idx 0
    exp = b"\x01" + b"\x03run" + b"\x00\x00"
    # name section: custom 'name' + subsection 1: {0:"main"}
    sub = b"\x01" + b"\x00" + b"\x04main"
    nam = b"\x04name" + bytes([1, len(sub)]) + sub
    mod = (b"\x00asm\x01\x00\x00\x00" + sec(2, imp) + sec(3, b"\x01\x00")
           + sec(7, exp) + sec(0, nam) + sec(10, b"\x01\x02\x00\x0b"))
    s = sections(mod)
    assert len(s["sections"]) == 5, s
    im = imports(mod, s["sections"])
    assert im[0]["name"] == "check" and im[0]["module"] == "env", im
    ex = exports(mod, s["sections"])
    assert ex[0] == {"name": "run", "kind": "func", "index": 0}, ex
    fn = fn_names(mod, s["sections"])
    assert fn.get(0) == "main", fn
    print("wasm_info selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="WASM module inventory")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--names", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("wasm path required")
    data = open(a.path, "rb").read()
    s = sections(data)
    if "error" in s:
        sys.exit(s["error"])
    out = {"version": s["version"], "sections": s["sections"],
           "imports": imports(data, s["sections"]),
           "exports": exports(data, s["sections"])}
    if a.names:
        out["function_names"] = fn_names(data, s["sections"])
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
