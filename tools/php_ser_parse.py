#!/usr/bin/env python3
"""php_ser_parse.py -- PHP serialize() format to JSON + object inventory.

PHP session files, cached objects and unserialize() sinks all carry the
`a:N:{...}` grammar: types i/d/b/s/a/O/R/r/C with length prefixes. This
parses the stream into JSON, lists every serialized OBJECT class name
(the object-injection surface), and flags `O:` entries whose class is
not in the handout — that is the gadget to hunt in source.

  python3 tools/php_ser_parse.py session.ser
  python3 tools/php_ser_parse.py --str 'a:1:{s:4:"name";s:3:"bob";}'
  python3 tools/php_ser_parse.py --selftest
"""
import argparse
import json
import re
import sys


def parse(b, i=0):
    """-> (value, next_index, objects_seen)."""
    objs = []
    t = b[i:i + 1]
    if t == b"N":
        return None, i + 2, objs
    if t in (b"i", b"d", b"b"):
        j = b.index(b";", i)
        v = b[i + 2:j]
        if t == b"i":
            return int(v), j + 1, objs
        if t == b"b":
            return v == b"1", j + 1, objs
        try:
            return float(v), j + 1, objs
        except ValueError:
            return v.decode("utf-8", "replace"), j + 1, objs
    if t == b"s":
        j = b.index(b":", i + 2)
        ln = int(b[i + 2:j])
        start = j + 2                                   # :"
        return b[start:start + ln].decode("utf-8", "replace"), \
            start + ln + 2, objs                        # +";
    if t == b"a":
        j = b.index(b":", i + 2)
        n = int(b[i + 2:j])
        p = j + 2                                       # :{
        out = {}
        for _ in range(n):
            k, p, o1 = parse(b, p)
            objs += o1
            v, p, o2 = parse(b, p)
            objs += o2
            out[str(k) if isinstance(k, (int, float)) else k] = v
        return out, p + 1, objs                         # +}
    if t in (b"O", b"C"):
        j = b.index(b":", i + 2)
        ln = int(b[i + 2:j])
        cls = b[j + 2:j + 2 + ln].decode("utf-8", "replace")
        objs.append(cls)
        # after "<class>" comes ":<count>:{" (O) or ":<len>:{<data>}" (C)
        q = b.index(b":", j + 2 + ln + 1)               # colon after quote
        j2 = b.index(b":", q + 1)                       # colon after count
        n = int(b[q + 1:j2])
        p = j2 + 2                                      # skip :{
        if t == b"C":                                   # custom serialized
            return {"__class__": cls,
                    "data": b[p:p + n]
                    .decode("utf-8", "replace")}, p + n + 1, objs
        props = {}
        for _ in range(n):
            k, p, o1 = parse(b, p)
            objs += o1
            v, p, o2 = parse(b, p)
            objs += o2
            props[str(k)] = v
        return {"__class__": cls, "props": props}, p + 1, objs
    if t in (b"R", b"r"):
        j = b.index(b";", i)
        return {"$ref": int(b[i + 2:j])}, j + 1, objs
    raise ValueError("unknown type %r at %d" % (t, i))


def analyze(data):
    v, end, objs = parse(data)
    return {"value": v, "objects": sorted(set(objs)),
            "object_count": len(objs),
            "consumed": end, "trailing": len(data) - end}


def _selftest():
    s = b'a:2:{s:4:"name";s:3:"bob";s:4:"role";O:8:"StdClass":1:' \
        b'{s:5:"admin";b:1;}}'
    d = analyze(s)
    assert d["value"]["name"] == "bob", d
    assert d["objects"] == ["StdClass"], d
    assert d["value"]["role"]["props"]["admin"] is True
    s2 = b'O:4:"Evil":2:{s:3:"cmd";s:2:"id";s:3:"log";a:1:{i:0;s:1:"x";}}'
    d2 = analyze(s2)
    assert d2["objects"] == ["Evil"] and d2["object_count"] == 1
    s3 = b'i:42;s:3:"x y"'
    print("php_ser_parse selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="PHP serialize parser")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--str", help="literal serialized string")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if a.str:
        data = a.str.encode()
    elif a.path:
        data = open(a.path, "rb").read()
    else:
        ap.error("path or --str required")
    try:
        print(json.dumps(analyze(data), indent=1))
    except (ValueError, IndexError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
