#!/usr/bin/env python3
"""php_ser_gen.py -- emit exact PHP serialize() bytes from a spec.

php_ser_parse.py reads a stream; this one WRITES one. Length prefixes
are the classic failure when hand-editing a payload, so the tool
counts them. Input is a JSON spec so the payload is data, not code:

  python3 tools/php_ser_gen.py --spec '{"user":"admin","role":1}'
  python3 tools/php_ser_gen.py --spec '{"O":"User","props":{"is_admin":true}}'
  python3 tools/php_ser_gen.py --str S 'a\\x3cscript\\x3e'  # S: hex-escape form

Object spec: {"O": "<Class>", "props": {...}}  ->  O:N:"Class":N:{...}
Reference:  {"R": n}  ->  R:n;
The special string type {"S": "value"}  ->  S:N:"value";  which carries
\\xNN hex escapes server-side and survives filters that `s:` does not.
"""
import argparse
import json
import sys


def _str_bytes(s: str) -> bytes:
    return s.encode("utf-8", "surrogatepass")


def gen(v):
    if v is None:
        return b"N;"
    if isinstance(v, bool):
        return b"b:%d;" % int(v)
    if isinstance(v, int):
        return b"i:%d;" % v
    if isinstance(v, float):
        return b"d:%.17G;" % v
    if isinstance(v, str):
        b = _str_bytes(v)
        return b's:%d:"%s";' % (len(b), b)
    if isinstance(v, dict):
        if "O" in v:                       # object injection
            cls = _str_bytes(str(v["O"]))
            props = v.get("props", {})
            body = b"".join(gen(k if isinstance(k, str) else str(k))
                            + gen(val) for k, val in props.items())
            return b'O:%d:"%s":%d:{%s}' % (len(cls), cls,
                                          len(props), body)
        if "R" in v:                       # reference
            return b"R:%d;" % int(v["R"])
        if "S" in v:                       # escaped-string type
            b = _str_bytes(str(v["S"]))
            return b'S:%d:"%s";' % (len(b), b)
        # plain array (dict = assoc array)
        body = b"".join(gen(k) + gen(val) for k, val in v.items())
        return b"a:%d:{%s}" % (len(v), body)
    if isinstance(v, list):
        body = b"".join(gen(i) + gen(val) for i, val in enumerate(v))
        return b"a:%d:{%s}" % (len(v), body)
    raise TypeError(f"cannot serialize {type(v).__name__}")


def _selftest():
    assert gen({"user": "admin", "role": 1}) == \
        b'a:2:{s:4:"user";s:5:"admin";s:4:"role";i:1;}'
    assert gen({"O": "User", "props": {"is_admin": True}}) == \
        b'O:4:"User":1:{s:8:"is_admin";b:1;}'
    assert gen(["a", "b"]) == b'a:2:{i:0;s:1:"a";i:1;s:1:"b";}'
    assert gen({"S": "x\\x3c"}) == b'S:5:"x\\x3c";'
    assert gen({"R": 2}) == b"R:2;"
    # length counted on BYTES not chars: multibyte char
    out = gen({"k": "é"})                   # é = 2 bytes utf-8
    assert out == b'a:1:{s:1:"k";s:2:"\xc3\xa9";}', out
    # round-trip through the parser: what we emit must parse back
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import php_ser_parse
    blob = gen({"O": "A", "props": {"x": [1, {"S": "y"}]}})
    val, end, objs = php_ser_parse.parse(blob)
    assert end == len(blob)
    print("php_ser_gen selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="emit PHP serialize() "
                                 "bytes from a JSON spec")
    ap.add_argument("--spec", help="JSON spec (dict/list/scalar; "
                    '{"O":cls,"props":{...}} for objects)')
    ap.add_argument("--str", dest="raw", help="serialize one literal "
                    "string")
    ap.add_argument("--str-type", choices=["s", "S"], default="s",
                    help="with --str: plain or escaped-string type")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if a.raw is not None:
        print(gen({"S": a.raw} if a.str_type == "S" else a.raw)
              .decode("utf-8"))
        return
    if not a.spec:
        ap.error("--spec or --str required")
    print(gen(json.loads(a.spec)).decode("utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
