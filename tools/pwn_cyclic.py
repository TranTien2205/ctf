#!/usr/bin/env python3
"""pwn_cyclic.py — CLI over tools/pwnstatic/cyclic.py. Stdlib only.

    python3 tools/pwn_cyclic.py 200            # print a 200-byte pattern
    python3 tools/pwn_cyclic.py --find 0x6161616c   # offset of a faulting register value
    python3 tools/pwn_cyclic.py --find laaa          # same, as the visible 4-char chunk
    python3 tools/pwn_cyclic.py --selftest
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pwnstatic import cyclic as _cyc          # noqa: E402


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("length", nargs="?", type=int, help="emit a pattern of this length")
    ap.add_argument("--find", metavar="NEEDLE",
                    help="offset of a 4-byte chunk: 'laaa', 0x… int, or 4 bytes via stdin")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if args.find is not None:
        try:
            needle = args.find if not args.find == "-" else sys.stdin.buffer.read(4)
            pos = _cyc.cyclic_find(needle)
        except ValueError as exc:
            print(json.dumps({"error": str(exc)}))
            return 2
        out = {"needle": args.find, "offset": pos}
        if pos == -1:
            out["note"] = "chunk not in the unique region — wrong alphabet, wrong n, or truncated value"
        print(json.dumps(out))
        return 0 if pos != -1 else 1
    if args.length is None:
        ap.print_help()
        return 2
    try:
        sys.stdout.buffer.write(_cyc.cyclic(args.length) + b"\n")
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}))
        return 2
    return 0


def _selftest() -> int:
    pat = _cyc.cyclic(256)
    assert pat[:8] == b"aaaabaaa"           # same head as pwntools cyclic()
    assert _cyc.cyclic_find(b"aaaa") == 0
    assert _cyc.cyclic_find(b"baaa") == 4
    assert _cyc.cyclic_find(pat[100:104]) == 100
    assert _cyc.cyclic_find("laaa") == _cyc.cyclic_find(b"laaa")
    # every 4-byte window is unique — that is the entire point
    seen = {pat[i:i + 4] for i in range(len(pat) - 3)}
    assert len(seen) == len(pat) - 3
    # a register reads little-endian: value 0x6161616c is bytes 'laaa'
    assert _cyc.cyclic_find(0x6161616C) == _cyc.cyclic_find(b"laaa")
    assert _cyc.cyclic_find(b"\x00\x01\x02\x03") == -1   # bytes outside the alphabet
    print("pwn_cyclic selftest: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
