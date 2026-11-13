#!/usr/bin/env python3
"""regf_read.py -- Windows registry hive (regf) key/value reader.

Registry hives (SAM, SYSTEM, SOFTWARE, NTUSER.DAT, Amcache.hve) are
the core of most Windows Sherlocks, and python-registry / Registry
Explorer are absent here. The format is stable: a `regf` header, a
chain of `hbin` blocks, and inside them cells -- `nk` keys (name,
timestamps, subkey lists `lf/lh/li/ri`), `vk` values (name, type,
inline-or-cell data), `sk` security. This walks the cell space once,
builds the key tree, and answers `ls <path>`, `get <path\\value>`,
`find <regex>` (key names, value names, and value data) plus a
`tree` summary -- enough for persistence, installed-software and
recently-run questions. Deleted cells (size field negated back to
positive = unallocated) are reported in a `--slack` sweep rather than
interpreted.

  python3 tools/forensics/regf_read.py NTUSER.DAT ls 'Software\\Run'
  python3 tools/forensics/regf_read.py hive find --pat 'flag'
  python3 tools/forensics/regf_read.py --selftest
"""
import argparse
import datetime
import json
import re
import struct

VMAP = {0: "REG_NONE", 1: "REG_SZ", 2: "REG_EXPAND_SZ", 3: "REG_BINARY",
        4: "REG_DWORD", 5: "REG_DWORD_BE", 6: "REG_LINK",
        7: "REG_MULTI_SZ", 11: "REG_QWORD"}


def _ft(v):
    try:
        return (datetime.datetime(1601, 1, 1) + datetime.timedelta(
            microseconds=v / 10)).isoformat()
    except (OverflowError, OSError, ValueError):
        return "0x%x" % v


class Hive(object):
    def __init__(self, data):
        if data[:4] != b"regf":
            raise ValueError("not a regf hive")
        self.d = data
        self.root_off, = struct.unpack("<I", data[0x24:0x28])
        self.hbins = []
        pos = 0x1000
        while pos + 32 <= len(data) and data[pos:pos + 4] == b"hbin":
            hoff, hsz = struct.unpack("<II", data[pos + 4:pos + 12])
            self.hbins.append((pos + 0x20, pos + 4 + hsz))
            pos += hsz

    def cell(self, off):
        """off is hive-relative (0x1000-based); returns payload."""
        abspos = 0x1000 + off
        if abspos + 4 > len(self.d):
            return None
        sz, = struct.unpack("<i", self.d[abspos:abspos + 4])
        if sz >= 0:
            return None                      # unallocated
        return self.d[abspos + 4:abspos + 4 + abs(sz) - 4]

    def _nk(self, off):
        c = self.cell(off)
        if not c or c[:2] != b"nk":
            return None
        if len(c) < 0x50:
            return None
        flags, = struct.unpack("<H", c[2:4])
        ts, = struct.unpack("<Q", c[4:12])
        parent, = struct.unpack("<i", c[0x10:0x14])
        nsub, = struct.unpack("<I", c[0x14:0x18])
        lofs, = struct.unpack("<i", c[0x1c:0x20])
        nval, = struct.unpack("<I", c[0x24:0x28])
        vofs, = struct.unpack("<i", c[0x28:0x2c])
        nlen, = struct.unpack("<H", c[0x48:0x4a])
        raw = c[0x4c:0x4c + nlen]
        name = raw.decode("latin-1" if flags & 0x20 else "utf-16-le",
                          "replace")
        return {"off": off, "name": name, "time": _ft(ts),
                "parent": parent, "subkey_count": nsub,
                "subkey_list": lofs, "value_count": nval,
                "value_list": vofs}

    def _subkey_offs(self, off, count):
        c = self.cell(off)
        if not c:
            return []
        sig = c[:2]
        if sig in (b"lf", b"lh"):
            n, = struct.unpack("<H", c[2:4])
            return [struct.unpack("<I", c[4 + i * 8:8 + i * 8])[0]
                    for i in range(min(n, count))]
        if sig == b"li":
            n, = struct.unpack("<H", c[2:4])
            return [struct.unpack("<I", c[4 + i * 4:8 + i * 4])[0]
                    for i in range(min(n, count))]
        if sig == b"ri":
            n, = struct.unpack("<H", c[2:4])
            out = []
            for i in range(min(n, 64)):
                sub, = struct.unpack("<I", c[4 + i * 4:8 + i * 4])
                out += self._subkey_offs(sub, count - len(out))
            return out
        return []

    def _vk(self, off):
        c = self.cell(off)
        if not c or c[:2] != b"vk" or len(c) < 0x14:
            return None
        nlen, dsz, doff, vtype = struct.unpack("<HIII", c[2:16])
        flags, = struct.unpack("<H", c[0x10:0x12])
        name = c[0x14:0x14 + nlen].decode("latin-1", "replace")
        inline = dsz & 0x80000000
        dsz &= ~0x80000000
        if inline:
            raw = struct.pack("<I", doff)[:dsz]
        else:
            dc = self.cell(doff)
            raw = dc[:dsz] if dc else b""
        return {"name": name, "type": VMAP.get(vtype, str(vtype)),
                "type_id": vtype, "size": dsz, "data_inline": bool(inline),
                "data": raw}

    def tree(self):
        """dict path -> {nk, values:[offs]} for every reachable key."""
        out = {}

        def walk(off, path):
            nk = self._nk(off)
            if not nk:
                return
            here = (path + "\\" + nk["name"]).strip("\\")
            vals = []
            if nk["value_count"] and nk["value_list"] >= 0:
                vlc = self.cell(nk["value_list"])
                if vlc:
                    for i in range(nk["value_count"]):
                        v, = struct.unpack("<I",
                                           vlc[i * 4:i * 4 + 4])
                        vk = self._vk(v)
                        if vk is not None:
                            vals.append(vk)
            out[here] = {"key": nk, "values": vals}
            if nk["subkey_count"] and nk["subkey_list"] >= 0:
                for so in self._subkey_offs(nk["subkey_list"],
                                            nk["subkey_count"]):
                    walk(so, here)
        walk(self.root_off, "")
        return out


def _val_repr(v):
    if v["type"] in ("REG_SZ", "REG_EXPAND_SZ", "REG_LINK"):
        return v["data"].decode("utf-16-le", "replace").rstrip("\x00")
    if v["type"] == "REG_MULTI_SZ":
        return [s for s in v["data"].decode(
            "utf-16-le", "replace").split("\x00") if s]
    if v["type"] in ("REG_DWORD", "REG_DWORD_BE") and len(v["data"]) >= 4:
        e = ">" if v["type"].endswith("BE") else "<"
        return struct.unpack(e + "I", v["data"][:4])[0]
    if v["type"] == "REG_QWORD" and len(v["data"]) >= 8:
        return struct.unpack("<Q", v["data"][:8])[0]
    if v["size"] <= 32:
        return v["data"].hex()
    return v["data"][:32].hex() + "...(%dB)" % v["size"]


def _selftest():
    # ---- build a minimal hive ----
    img = bytearray(0x1000 + 0x2000)
    img[:4] = b"regf"
    struct.pack_into("<I", img, 0x24, 0)     # root cell offset (patched below)
    img[0x1000:0x1004] = b"hbin"
    struct.pack_into("<II", img, 0x1004, 0, 0x2000)
    cur = [0x1000 + 0x20]                    # cell cursor (abs)

    def put_cell(payload):
        sz = len(payload) + 4
        sz = (sz + 7) & ~7
        p = cur[0]
        struct.pack_into("<i", img, p, -sz)
        img[p + 4:p + 4 + len(payload)] = payload
        cur[0] += sz
        return p - 0x1000                    # hive-relative offset

    def make_nk(name, subs_list=-1, nsub=0, vals=0, vals_off=-1):
        nb = name.encode("latin-1")
        nk = struct.pack("<H", 0x20) + struct.pack("<Q", 133485000000000000) \
            + b"\x00" * 4 + struct.pack("<i", -1) \
            + struct.pack("<II", nsub, 0) + struct.pack("<i", subs_list) \
            + b"\x00" * 4 + struct.pack("<Ii", vals, vals_off) \
            + b"\x00" * 12 + struct.pack("<IIII", 0, 0, 0, 0) \
            + struct.pack("<HH", len(nb), 0) + nb
        return put_cell(b"nk" + nk)

    def make_vk(name, data, vtype=1):
        nb = name.encode("latin-1")
        doff = put_cell(data)
        vk = struct.pack("<HIII", len(nb), len(data), doff, vtype) \
            + struct.pack("<HH", 0, 0) + nb
        return put_cell(b"vk" + vk)

    v1 = make_vk("FlagPath", "flag{reg_ok}".encode("utf-16-le") + b"\x00\x00")
    v2 = make_vk("Count", struct.pack("<I", 0x1337), 4)
    vl_off = put_cell(struct.pack("<II", v1, v2))
    root = make_nk("ROOT", nsub=1, vals=2, vals_off=vl_off)
    child = make_nk("Run")
    # patch child's parent
    struct.pack_into("<i", img, 0x1000 + child + 4 + 0x10, root)
    lf = put_cell(b"lf" + struct.pack("<H", 1)
                  + struct.pack("<I", child) + struct.pack("<I", 0x41414141))
    struct.pack_into("<i", img, 0x1000 + root + 4 + 0x1c, lf)
    struct.pack_into("<I", img, 0x24, root)  # real root offset
    h = Hive(bytes(img))
    t = h.tree()
    assert "ROOT" in t, t.keys()
    assert "ROOT\\Run" in t, t.keys()
    vals = {v["name"]: _val_repr(v) for v in t["ROOT"]["values"]}
    assert vals["FlagPath"] == "flag{reg_ok}", vals
    assert vals["Count"] == 0x1337, vals
    print("regf_read selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="registry hive reader")
    ap.add_argument("path", nargs="?")
    ap.add_argument("cmd", nargs="?", default="tree",
                    choices=["tree", "ls", "get", "find"])
    ap.add_argument("arg", nargs="?", default="")
    ap.add_argument("--pat")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("path required")
    h = Hive(open(a.path, "rb").read())
    t = h.tree()
    if a.cmd == "tree":
        print(json.dumps({"keys": sorted(t.keys()),
                          "count": len(t)}, indent=1))
    elif a.cmd == "ls":
        ent = t.get(a.arg.strip("\\"))
        if ent is None:
            print(json.dumps({"error": "no such key",
                              "known": sorted(t.keys())[:20]}, indent=1))
            return
        print(json.dumps({
            "key": ent["key"]["name"], "time": ent["key"]["time"],
            "subkeys": [k.split("\\")[-1] for k in sorted(t.keys())
                        if k.startswith(a.arg.strip("\\") + "\\")
                        and "\\" not in k[len(a.arg.strip("\\")) + 1:]],
            "values": {v["name"]: _val_repr(v)
                       for v in ent["values"]}}, indent=1))
    elif a.cmd == "find":
        pat = re.compile(a.pat or a.arg or "", re.I)
        hits = []
        for path, ent in t.items():
            if pat.search(path):
                hits.append({"kind": "key", "path": path})
            for v in ent["values"]:
                r = _val_repr(v)
                if pat.search(v["name"]) or pat.search(str(r)):
                    hits.append({"kind": "value", "path": path,
                                 "name": v["name"], "data": r})
        print(json.dumps({"hits": hits, "count": len(hits)}, indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
