#!/usr/bin/env python3
"""dotnet_info.py -- .NET assembly metadata inventory (ECMA-335).

file_type flags `pe-dotnet` and rev-managed-code routes to dnSpy /
ilspycmd -- both absent here. The always-available floor this adds:
the CLR header's metadata root ("BSJB"), its #~ compressed table
stream, and the #Strings/#US heaps. Walked correctly, TypeDef and
MethodDef give every type and method name in the binary -- the same
level-1 inventory jclass_info gives for Java -- and #US (the user
string heap) is where literal flag-check strings live.

Table row sizes depend on heap-width bits and each table's row
count, so every table 0x00-0x2C is sized from spec, and coded
indexes are sized by tag width and the largest target table.

  python3 tools/dotnet_info.py app.exe
  python3 tools/dotnet_info.py app.exe --strings
  python3 tools/dotnet_info.py --selftest
"""
import argparse
import json
import struct

# column index kinds -> how wide the coded/simple index is
STR, GUID, BLOB = "str", "guid", "blob"

# coded index: (tag bits, target table ids)
CODED = {
    "TypeDefOrRef": (2, [0x02, 0x01, 0x1B]),
    "HasConstant": (2, [0x04, 0x08, 0x17]),
    "HasCustomAttribute": (5, [0x06, 0x04, 0x01, 0x02, 0x08, 0x09,
                               0x0A, 0x00, 0x0E, 0x17, 0x14, 0x11,
                               0x1A, 0x1B, 0x20, 0x23, 0x26, 0x27,
                               0x28, 0x2A, 0x2C]),
    "HasFieldMarshal": (1, [0x04, 0x08]),
    "HasDeclSecurity": (2, [0x02, 0x06, 0x20]),
    "MemberRefParent": (3, [0x02, 0x01, 0x1A, 0x06, 0x1B]),
    "HasSemantics": (1, [0x14, 0x17]),
    "MethodDefOrRef": (1, [0x06, 0x0A]),
    "MemberForwarded": (1, [0x04, 0x06]),
    "Implementation": (2, [0x26, 0x23, 0x27]),
    "CustomAttributeType": (3, [0x06, 0x0A]),
    "ResolutionScope": (2, [0x00, 0x1A, 0x23, 0x01]),
    "TypeOrMethodDef": (1, [0x02, 0x06]),
}

# table id -> column spec; "t<N>" = simple index into table N (hex),
# "c:Name" = coded index, STR/GUID/BLOB = heap index, "u2"/"u4"/"u8"
# = fixed width. ECMA-335 numbering.
TABLES = {
    0x00: ["u2", STR, GUID, GUID, GUID],
    0x01: ["c:ResolutionScope", STR, STR],
    0x02: ["u4", STR, STR, "c:TypeDefOrRef", "t4", "t6"],
    0x04: ["u2", STR, BLOB],
    0x06: ["u4", "u2", "u2", STR, BLOB, "t8"],
    0x08: ["u2", "u2", STR],
    0x09: ["t2", "c:TypeDefOrRef"],
    0x0A: ["c:MemberRefParent", STR, BLOB],
    0x0B: ["u2", "c:HasConstant", BLOB],
    0x0C: ["c:HasCustomAttribute", "c:CustomAttributeType", BLOB],
    0x0D: ["c:HasFieldMarshal", BLOB],
    0x0E: ["u2", "c:HasDeclSecurity", BLOB],
    0x0F: ["u4", "t4"],
    0x10: ["u4", "t4"],
    0x11: [BLOB],
    0x12: ["t2", "t14"],
    0x14: ["u2", STR, "c:TypeDefOrRef"],
    0x15: ["t2", "t17"],
    0x17: ["u2", STR, BLOB],
    0x18: ["u2", "t6", "c:HasSemantics"],
    0x19: ["t2", "c:MethodDefOrRef", "c:MethodDefOrRef"],
    0x1A: [STR],
    0x1B: [BLOB],
    0x1C: ["u2", "c:MemberForwarded", STR, "t1A"],
    0x1D: ["u4", "t4"],
    0x20: ["u4", "u2", "u2", "u2", "u2", "u4", BLOB, STR, STR],
    0x21: ["u4", "t20"],
    0x22: ["u4", "u4", "u4", "t20"],
    0x23: ["u2", "u2", "u2", "u2", "u4", BLOB, STR, STR, BLOB],
    0x24: ["u4", "t23"],
    0x25: ["u4", "u4", "u4", "t23"],
    0x26: ["u4", STR, BLOB],
    0x27: ["u4", STR, "c:Implementation"],
    0x28: ["u4", "u4", STR, "c:Implementation"],
    0x2A: ["u2", "u2", "t2", "c:TypeDefOrRef"],
    0x2B: ["c:MethodDefOrRef", BLOB],
    0x2C: ["c:TypeOrMethodDef", "c:TypeDefOrRef"],
}

TNAMES = {0x02: "TypeDef", 0x01: "TypeRef", 0x06: "MethodDef",
          0x0A: "MemberRef", 0x04: "Field", 0x08: "Param"}


def _u16(d, o):
    return struct.unpack("<H", d[o:o + 2])[0]


def _u32(d, o):
    return struct.unpack("<I", d[o:o + 4])[0]


def _pe_sections(d):
    """Return (sections, clr_dir_rva). sections = [(name,vsize,va,raw)]."""
    if d[:2] != b"MZ":
        return None
    pe = _u32(d, 0x3C)
    if d[pe:pe + 4] != b"PE\x00\x00":
        return None
    nsec = _u16(d, pe + 6)
    optsz = _u16(d, pe + 20)
    oh = pe + 24
    magic = _u16(d, oh)
    dd = oh + (96 if magic == 0x10B else 112 if magic == 0x20B else 0)
    if not dd:
        return None
    clr = _u32(d, dd + 14 * 8)
    secs = []
    sbase = oh + optsz
    for i in range(nsec):
        s = sbase + 40 * i
        secs.append((d[s:s + 8].rstrip(b"\x00").decode("latin-1"),
                     _u32(d, s + 8), _u32(d, s + 12), _u32(d, s + 20)))
    return secs, clr


def _rva2off(secs, rva):
    for _n, vs, va, raw in secs:
        if va <= rva < va + max(vs, 1):
            return raw + rva - va
    return None


class Meta:
    def __init__(self, d, off):
        if d[off:off + 4] != b"BSJB":
            raise ValueError("no BSJB metadata root")
        vlen = _u32(d, off + 12)
        p = off + 16 + ((vlen + 3) & ~3)
        streams = _u16(d, p + 2)
        p += 4
        self.streams = {}
        for _ in range(streams):
            so, ss = _u32(d, p), _u32(d, p + 4)
            p += 8
            e = d.index(b"\x00", p)
            name = d[p:e].decode("ascii", "replace")
            p = e + 1
            while (p - off) % 4:
                p += 1
            self.streams[name] = d[off + so:off + so + ss]
        self.strings = self.streams.get("#Strings", b"")
        self.us = self.streams.get("#US", b"")
        tilde = self.streams.get("#~") or self.streams.get("#-")
        self.rows = {}
        self.widths = {}
        if tilde:
            self._tables(tilde)

    def _tables(self, t):
        heap = t[6]
        valid = struct.unpack("<Q", t[8:16])[0]
        p = 24
        for tid in range(0x2D):
            if valid >> tid & 1:
                self.rows[tid] = _u32(t, p)
                p += 4
        self.widths = {
            STR: 4 if heap & 0x01 else 2,
            GUID: 4 if heap & 0x02 else 2,
            BLOB: 4 if heap & 0x04 else 2}
        self.tab_base = p

    def _tidx(self, tid):
        return 4 if self.rows.get(tid, 0) >= 0x10000 else 2

    def _cidx(self, name):
        bits, tids = CODED[name]
        big = max(self.rows.get(t, 0) for t in tids)
        return 4 if big >= (1 << (16 - bits)) else 2

    def _colw(self, col):
        if col in ("u2",):
            return 2
        if col in ("u4", "u8"):
            return 8 if col == "u8" else 4
        if col in self.widths:
            return self.widths[col]
        if col.startswith("t"):
            return self._tidx(int(col[1:], 16))
        return self._cidx(col[2:])

    def _row_off(self, tid):
        off = self.tab_base
        for t in sorted(self.rows):
            if t >= tid:
                break
            spec = TABLES.get(t)
            if spec is None:
                return None
            off += sum(self._colw(c) for c in spec) * self.rows[t]
        return off

    def _str(self, idx):
        if not 0 < idx < len(self.strings):
            return ""
        e = self.strings.index(b"\x00", idx)
        return self.strings[idx:e].decode("utf-8", "replace")

    def _idx(self, buf, off, w):
        return _u16(buf, off) if w == 2 else _u32(buf, off)

    def typedefs(self):
        tilde = self.streams.get("#~") or self.streams.get("#-")
        if not tilde or 0x02 not in self.rows:
            return []
        off = self._row_off(0x02)
        spec = TABLES[0x02]
        w = [self._colw(c) for c in spec]
        row = sum(w)
        out = []
        for i in range(self.rows[0x02]):
            r = off + i * row
            ns = self._str(self._idx(tilde, r + w[0] + w[1],
                                   self.widths[STR]))
            nm = self._str(self._idx(tilde, r + w[0], self.widths[STR]))
            out.append({"rid": i + 1, "name": nm, "namespace": ns})
        return out

    def methods(self):
        tilde = self.streams.get("#~") or self.streams.get("#-")
        if not tilde or 0x06 not in self.rows:
            return []
        off = self._row_off(0x06)
        spec = TABLES[0x06]
        w = [self._colw(c) for c in spec]
        row = sum(w)
        sw = self.widths[STR]
        noff = w[0] + w[1] + w[2]
        out = []
        for i in range(self.rows[0x06]):
            r = off + i * row
            out.append({"rid": i + 1,
                        "rva": _u32(tilde, r),
                        "name": self._str(self._idx(tilde, r + noff, sw))})
        return out

    def memberrefs(self):
        tilde = self.streams.get("#~") or self.streams.get("#-")
        if not tilde or 0x0A not in self.rows:
            return []
        off = self._row_off(0x0A)
        spec = TABLES[0x0A]
        w = [self._colw(c) for c in spec]
        row = sum(w)
        sw = self.widths[STR]
        out = []
        for i in range(min(self.rows[0x0A], 5000)):
            r = off + i * row
            out.append(self._str(self._idx(tilde, r + w[0], sw)))
        return out

    def user_strings(self):
        d = self.us
        out = []
        i = 1
        while i < len(d):
            b = d[i]
            if (b & 0xE0) == 0xC0:
                ln = ((b & 0x1F) << 24) | (d[i + 1] << 16) | \
                     (d[i + 2] << 8) | d[i + 3]
                n = 4
            elif (b & 0xC0) == 0x80:
                ln = ((b & 0x3F) << 8) | d[i + 1]
                n = 2
            else:
                ln, n = b & 0x7F, 1
            if ln == 0 or i + n + ln > len(d):
                i += 1
                continue
            s = d[i + n:i + n + ln - 1].decode("utf-16-le", "replace")
            if s.strip():
                out.append({"offset": i, "string": s})
            i += n + ln
        return out[:2000]


def parse(path):
    d = open(path, "rb").read()
    pe = _pe_sections(d)
    if not pe:
        return {"error": "not a PE"}
    secs, clr = pe
    if not clr:
        return {"error": "PE has no CLR header (native, not .NET)"}
    coff = _rva2off(secs, clr)
    meta_rva = _u32(d, coff + 8)
    moff = _rva2off(secs, meta_rva)
    m = Meta(d, moff)
    out = {"streams": sorted(m.streams),
           "tables": {TNAMES.get(k, hex(k)): v
                      for k, v in sorted(m.rows.items()) if v},
           "typedefs": m.typedefs(),
           "methods": m.methods(),
           "memberrefs": m.memberrefs()}
    return out, m


def _selftest():
    """Build a tiny BSJB blob: #~ + #Strings + #US, one typedef,
    one method, one user string."""
    strs = b"\x00MainCls\x00Program\x00CheckFlag\x00"
    tilde = bytearray(24 + 2 * 4 + 14 + 14)  # hdr+counts+td row+mdef row
    tilde[4], tilde[5] = 2, 0
    valid = (1 << 0x02) | (1 << 0x06)
    struct.pack_into("<Q", tilde, 8, valid)
    struct.pack_into("<II", tilde, 24, 1, 1)   # 1 typedef, 1 method
    # typedef row: flags u4, name str16(1), ns str16(9), extends coded2,
    # fieldlist t4(2), methodlist t6(2)
    struct.pack_into("<IHHHHH", tilde, 32, 0, 1, 9, 0, 1, 1)
    # method row: rva u4, impl u2, flags u2, name str16(17), sig blob,
    # paramlist t8
    row2 = 32 + 14
    struct.pack_into("<IHHHHH", tilde, row2, 0x2050, 0, 0, 17, 1, 1)
    #   ^ rva     ^ impl+flags ^ name=17 ("CheckFlag") ^ sig ^ paramlist
    us = b"\x00" + bytes([1 + 2 * len("flag{net_ok}")]) + \
        "flag{net_ok}".encode("utf-16-le") + b"\x01"
    def sh(off_size_name):
        return off_size_name
    # assemble metadata root
    names = [(b"#~\x00", bytes(tilde)), (b"#Strings\x00", strs),
             (b"#US\x00", us)]
    hdr_len = 16 + 12 + 4            # fixed hdr + version str + flags/cnt
    shead = bytearray()
    data = bytearray()
    base = hdr_len + sum(8 + ((len(n[0]) + 3) & ~3) for n in names)
    for name, blob in names:
        shead += struct.pack("<II", base + len(data), len(blob))
        shead += name + b"\x00" * ((4 - len(name) % 4) % 4)
        data += blob
    md = b"BSJB" + struct.pack("<HHII", 1, 1, 0, 12) + \
        b"v4.0.30319\x00\x00" \
        + struct.pack("<HH", 0, len(names)) + bytes(shead) + bytes(data)
    # fake it into a PE-less buffer via a direct Meta call
    m = Meta(md, 0)
    td = m.typedefs()
    assert td[0]["name"] == "MainCls" and td[0]["namespace"] == "Program", td
    mm = m.methods()
    assert mm[0]["name"] == "CheckFlag" and mm[0]["rva"] == 0x2050, mm
    u = m.user_strings()
    assert u and u[0]["string"] == "flag{net_ok}", u
    print("dotnet_info selftest: ok")


def main():
    ap = argparse.ArgumentParser(
        description=".NET metadata inventory (ECMA-335)")
    ap.add_argument("pe", nargs="?")
    ap.add_argument("--strings", action="store_true",
                    help="dump the #US user-string heap")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.pe:
        ap.error("pe required")
    out, m = parse(a.pe)
    if a.strings:
        out["user_strings"] = m.user_strings()
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
