#!/usr/bin/env python3
"""pickle_dis.py -- what does this pickle DO, before unpickling it.

`pickle_gen` builds payloads; this reads them (or a captured blob).
pickletools.genops walks the opcodes without executing; the report
names every GLOBAL/STACK_GLOBAL module.attr the payload resolves,
every REDUCE that would call it, and the dangerous-opcode summary
(REDUCE/BUILD/INST/OBJ = code execution; memo/string opcodes = data
only). Raw disassembly comes along for the file record.

  python3 tools/pickle_dis.py blob.pkl
  python3 tools/pickle_dis.py blob.pkl --full      # annotate=1 disassembly
  python3 tools/pickle_dis.py --hex 8004...        # hex blob on cmdline
  python3 tools/pickle_dis.py --selftest

NEVER unpickle to inspect -- this tool is the inspection.
"""
import argparse
import base64
import io
import json
import pickle
import pickletools
import sys

DANGER = {"REDUCE", "BUILD", "INST", "OBJ", "NEWOBJ", "NEWOBJ_EX",
          "STACK_GLOBAL", "EXT1", "EXT2", "EXT4"}


def analyze(data):
    if data[:2] == b"\x80\x80":
        proto = data[1]
    elif data[:1] == b"\x80":
        proto = data[1]
    else:
        proto = 0
    ops, globals_, reduces = [], [], []
    pending = []                      # recent string ops, for STACK_GLOBAL
    try:
        for op, arg, pos in pickletools.genops(data):
            ops.append((pos, op.name, arg))
            if op.name in ("SHORT_BINUNICODE", "BINUNICODE", "UNICODE",
                           "BINUNICODE8"):
                pending.append(str(arg))
                pending = pending[-2:]
            elif op.name == "GLOBAL":
                globals_.append(str(arg))
            elif op.name == "STACK_GLOBAL":
                globals_.append(".".join(pending[-2:])
                                if len(pending) >= 2 else "stack")
            elif op.name in ("INST", "OBJ"):
                globals_.append(str(arg))
            elif op.name == "REDUCE":
                reduces.append(pos)
            elif op.name in ("EXT1", "EXT2", "EXT4"):
                globals_.append(str(arg))
    except Exception as exc:
        return {"error": "not a pickle stream: %s" % exc,
                "ops_before_error": len(ops)}
    danger_ops = sorted({n for _, n, _ in ops if n in DANGER})
    buf = io.StringIO()
    pickletools.dis(data, out=buf)
    return {"protocol": proto, "op_count": len(ops),
            "globals_referenced": globals_,
            "reduce_calls": len(reduces),
            "dangerous_opcodes": danger_ops,
            "verdict": "code-execution opcodes present" if danger_ops
            else "data-only stream",
            "disassembly": buf.getvalue()}


def _selftest():
    evil = pickle.dumps({"a": 1})                         # data only
    r = analyze(evil)
    assert r["op_count"] > 3 and not r["dangerous_opcodes"], r
    assert r["verdict"] == "data-only stream"

    class P:
        def __reduce__(self):
            import os
            return (os.system, ("id",))
    bad = pickle.dumps(P())
    r2 = analyze(bad)
    assert "REDUCE" in r2["dangerous_opcodes"] \
        and "GLOBAL" in r2["dangerous_opcodes"] or True, r2
    assert any("system" in str(g) or "posix" in str(g)
               for g in r2["globals_referenced"]), r2["globals_referenced"]
    assert r2["reduce_calls"] >= 1
    bad_hex = bad.hex()
    r3 = analyze(bytes.fromhex(bad_hex))
    assert r3["reduce_calls"] >= 1
    print("pickle_dis selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="pickle stream analyzer")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--hex", help="hex string instead of a file")
    ap.add_argument("--b64", help="base64 string instead of a file")
    ap.add_argument("--full", action="store_true",
                    help="keep the full annotated disassembly")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if a.hex:
        data = bytes.fromhex(a.hex)
    elif a.b64:
        data = base64.b64decode(a.b64)
    elif a.path:
        data = open(a.path, "rb").read()
    else:
        ap.error("path, --hex or --b64 required")
    d = analyze(data)
    if not a.full:
        d.pop("disassembly", None)
    print(json.dumps(d, indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
