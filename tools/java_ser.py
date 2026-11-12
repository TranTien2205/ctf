#!/usr/bin/env python3
"""java_ser.py -- Java serialization stream inventory (aced 0005).

A captured `rO0AB...` blob is a ysoserial payload or a session object
before it is anything else. The stream is self-describing enough to
walk without Java: TC_OBJECT/TC_CLASSDESC carry class names and field
names, TC_STRING the UTF values, TC_REFERENCE the object graph. This
lists every classdesc (the gadget-chain surface), every string, and
every unsupported/truncated token -- reporting parse position so a
hand-trimmed blob is still readable up to the point it breaks.

  python3 tools/java_ser.py payload.ser
  python3 tools/java_ser.py --b64 rO0ABXNy...
  python3 tools/java_ser.py --hex aced0005...
  python3 tools/java_ser.py --selftest

Analysis only; it never deserialises.
"""
import argparse
import base64
import json
import struct
import sys

TC = {0x70: "NULL", 0x71: "REFERENCE", 0x72: "CLASSDESC", 0x73: "OBJECT",
      0x74: "STRING", 0x75: "ARRAY", 0x76: "CLASS", 0x77: "BLOCKDATA",
      0x78: "ENDBLOCKDATA", 0x79: "RESET", 0x7a: "BLOCKDATALONG",
      0x7b: "EXCEPTION", 0x7c: "LONGSTRING", 0x7d: "PROXYCLASSDESC",
      0x7e: "ENUM"}

PRIM_SIZE = {"B": 1, "C": 2, "D": 8, "F": 4, "I": 4, "J": 8, "S": 2,
             "Z": 1}
BASE_WIRE_HANDLE = 0x7E0000


def _utf(b, i, long_=False):
    if long_:
        n = struct.unpack(">q", b[i:i + 8])[0]
        i += 8
    else:
        n = struct.unpack(">H", b[i:i + 2])[0]
        i += 2
    return b[i:i + n].decode("utf-8", "replace"), i + n


class _P:
    def __init__(self, data):
        self.b, self.i = data, 4
        self.classes, self.strings = [], []
        self.handles, self.depth = 0, 0
        self.trunc = None

    def u1(self):
        v = self.b[self.i]
        self.i += 1
        return v

    def u4(self):
        v = struct.unpack(">I", self.b[self.i:self.i + 4])[0]
        self.i += 4
        return v

    def utf(self, long_=False):
        s, self.i = _utf(self.b, self.i, long_)
        return s

    def content(self, limit=8):
        """Walk one content element; returns when a full element read."""
        while self.i < len(self.b) and self.depth < 200:
            tc = self.b[self.i]
            if tc not in TC:
                self.trunc = "unknown token 0x%02x at %d" % (tc, self.i)
                return
            self.i += 1
            if tc == 0x70:
                return                                    # NULL
            if tc == 0x71:
                self.u4()
                return                                    # REFERENCE
            if tc == 0x72:
                self.classdesc()
                return
            if tc == 0x74:
                s = self.utf()
                self.strings.append(s)
                return
            if tc == 0x7c:
                s = self.utf(long_=True)
                self.strings.append(s)
                return
            if tc == 0x77:
                n = self.u1()
                self.i += n
                return                                    # BLOCKDATA
            if tc == 0x7a:
                n = self.u4()
                self.i += n
                return
            if tc == 0x78:
                return                                    # ENDBLOCKDATA
            if tc == 0x73:
                self.depth += 1
                self.newobject()
                return
            if tc == 0x75:
                self.depth += 1
                self.array()
                return
            if tc == 0x76:
                self.depth += 1
                self.content()                            # the classdesc
                return
            if tc == 0x7e:
                self.depth += 1
                self.enum()
                return
            if tc == 0x7d:
                self.proxydesc()
                return
            if tc == 0x79 or tc == 0x7b:
                return
            return
        if self.i < len(self.b):
            self.trunc = "depth guard at %d" % self.i

    def classdesc(self):
        name = self.utf()
        suid_lo = struct.unpack(">Q", self.b[self.i:self.i + 8])[0]
        self.i += 8                                       # serialVersionUID
        flags = self.u1()
        nfields = struct.unpack(">H", self.b[self.i:self.i + 2])[0]
        self.i += 2
        fields = []
        for _ in range(nfields):
            tcode = chr(self.u1())
            fn = self.utf()
            f = {"name": fn, "type": tcode}
            if tcode in ("L", "["):
                self.depth += 1
                self.content()                            # className1 ref
            fields.append(f)
        self.depth += 1
        self.content()                                    # annotations -> ENDBLOCK
        self.depth += 1
        self.content()                                    # superclass
        self.classes.append({"name": name,
                             "suid": "%016x" % suid_lo,
                             "flags": hex(flags), "fields": fields})

    def newobject(self):
        self.depth += 1
        self.content()                                    # classdesc
        # field values follow; without the desc we cannot type them --
        # strings/refs are still walkable as content elements until
        # ENDBLOCKDATA or stream end. Walk until end, bounded.
        while self.i < len(self.b):
            tc = self.b[self.i]
            if tc in (0x74, 0x7c):
                self.i += 1
                s = self.utf(long_=(tc == 0x7c))
                self.strings.append(s)
            elif tc == 0x71:
                self.i += 1
                self.u4()
            elif tc == 0x70:
                self.i += 1
            elif tc == 0x77 or tc == 0x7a:
                self.i += 1
                n = self.u1() if tc == 0x77 else self.u4()
                self.i += n
            elif tc == 0x78:
                self.i += 1
                continue
            else:
                self.i += 4 if self.i + 4 <= len(self.b) else 0
                break

    def array(self):
        self.depth += 1
        self.content()                                    # classdesc
        n = self.u4()
        for _ in range(min(n, 10000)):
            self.depth += 1
            self.content()

    def enum(self):
        self.depth += 1
        self.content()                                    # enum classdesc
        self.depth += 1
        self.content()                                    # constant name

    def proxydesc(self):
        n = self.u4()
        for _ in range(n):
            self.utf()                                    # interface names
        self.depth += 1
        self.content()
        self.depth += 1
        self.content()


def analyze(data):
    if data[:4] != b"\xac\xed\x00\x05":
        return {"error": "not a java serialization stream (no aced0005)"}
    p = _P(data)
    try:
        p.content()
        while p.i < len(data) and not p.trunc:
            p.content()
    except (IndexError, struct.error, ValueError) as exc:
        p.trunc = "%s at %d" % (exc, p.i)
    out = {"classes": p.classes, "strings": p.strings[:200],
           "class_count": len(p.classes),
           "consumed": p.i, "trailing": len(data) - p.i}
    if p.trunc:
        out["stopped_at"] = p.trunc
    gadgets = [c["name"] for c in p.classes if any(
        k in c["name"] for k in
        ("InvokerTransformer", "ChainedTransformer", "TemplatesImpl",
         "AnnotationInvocationHandler", "PriorityQueue",
         "BadAttributeValueExpException", "HashMap", "Hashtable",
         "TreeMap", "LazyMap", "Factory", "XString", "MethodClosure"))]
    if gadgets:
        out["known_gadget_classes"] = gadgets
    return out


def _selftest():
    # aced0005 + TC_STRING "hi" + TC_CLASSDESC for Lpkg/Evil with one
    # I-field, annotations ENDBLOCKDATA, super=NULL
    s = (b"\xac\xed\x00\x05"
         b"\x74\x00\x02hi"
         b"\x72\x00\x0aLpkg/Evil;" + b"\x00" * 8
         + b"\x02" + b"\x00\x01"
         + b"I" + b"\x00\x03cnt"
         + b"\x78" + b"\x70")
    d = analyze(s)
    assert d["strings"] == ["hi"], d
    assert d["classes"][0]["name"] == "Lpkg/Evil;", d["classes"]
    assert d["classes"][0]["fields"] == [{"name": "cnt", "type": "I"}]
    print("java_ser selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="Java serialization inventory")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--b64", help="base64 stream")
    ap.add_argument("--hex", help="hex stream")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if a.b64:
        data = base64.b64decode(a.b64)
    elif a.hex:
        data = bytes.fromhex(a.hex)
    elif a.path:
        data = open(a.path, "rb").read()
    else:
        ap.error("path, --b64 or --hex required")
    print(json.dumps(analyze(data), indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
