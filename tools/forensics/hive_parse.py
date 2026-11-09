#!/usr/bin/env python3
"""hive_parse.py -- read an offline Windows registry hive (regf).

Usage:
  python3 tools/forensics/hive_parse.py hive.dat tree
  python3 tools/forensics/hive_parse.py hive.dat get 'Path/To/Key'
  python3 tools/forensics/hive_parse.py NTUSER.DAT userassist
  python3 tools/forensics/hive_parse.py --selftest

regf: 4096-byte header ("regf", root-cell offset at 0x24), then hbins
("hbin") holding cells: nk key node, vk value, lf/lh/li/ri subkey
lists. Offsets inside cells are relative to the first hbin's data area
(file offset minus 0x1000). Values with the data-size high bit set keep
their data inline in the data-offset field. Names flag 0x20 = Latin-1,
else UTF-16LE. userassist: ROT13 value names under UserAssist, blob
layouts v5 (XP, count @4, FILETIME @8) and v7 (count @4, FILETIME @60).
"""
import argparse
import codecs
import json
import struct
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

EPOCH = datetime(1601, 1, 1)
TYPES = {1: "SZ", 2: "EXPAND_SZ", 3: "BINARY", 4: "DWORD",
         5: "DWORD_BE", 6: "LINK", 7: "MULTI_SZ", 11: "QWORD"}


def _ft(b):
    v = struct.unpack("<Q", b[:8])[0]
    return (EPOCH + timedelta(microseconds=v / 10)).isoformat() if v else None


class Hive:
    def __init__(self, path):
        self.data = Path(path).read_bytes()
        if self.data[:4] != b"regf":
            raise ValueError("not a registry hive (no regf signature)")
        self.root = struct.unpack("<I", self.data[0x24:0x28])[0]

    def cell(self, off):
        """cell content (size field skipped) at hbin-relative offset."""
        if off < 0:
            return None
        pos = 0x1020 + off          # first hbin data = 0x1000 + 0x20
        size = struct.unpack("<i", self.data[pos:pos + 4])[0]
        if size >= 0:
            return None  # free cell
        return self.data[pos + 4:pos + 4 - size]

    def _name(self, raw, compressed):
        return raw.decode("latin-1" if compressed else "utf-16-le",
                          "replace")

    def nk(self, off):
        c = self.cell(off)
        if not c or c[:2] != b"nk":
            return None
        flags = struct.unpack("<H", c[2:4])[0]
        nlen, clen = struct.unpack("<HH", c[72:76])
        return {"off": off, "time": _ft(c[4:12]),
                "name": self._name(c[76:76 + nlen], flags & 0x20),
                "nsub": struct.unpack("<I", c[20:24])[0],
                "sublist": struct.unpack("<i", c[28:32])[0],
                "nsub_v": struct.unpack("<I", c[24:28])[0],
                "sublist_v": struct.unpack("<i", c[32:36])[0],
                "nval": struct.unpack("<I", c[36:40])[0],
                "vallist": struct.unpack("<i", c[40:44])[0],
                "class": self._name(self.cell(
                    struct.unpack("<i", c[48:52])[0] or -1) or b"",
                    False) if clen else ""}

    def sub_offsets(self, off):
        """walk a subkey list cell (lf/lh/li/ri) -> child nk offsets."""
        out = []
        c = self.cell(off) if off >= 0 else None
        if not c:
            return out
        sig, n = c[:2], struct.unpack("<H", c[2:4])[0]
        if sig in (b"lf", b"lh"):
            out += [struct.unpack("<I", c[4 + i * 8:8 + i * 8])[0]
                    for i in range(n)]
        elif sig in (b"li", b"ri"):
            for i in range(n):
                o = struct.unpack("<I", c[4 + i * 4:8 + i * 4])[0]
                out += self.sub_offsets(o) if sig == b"ri" else [o]
        return out

    def values(self, node):
        offs = self.cell(node["vallist"]) if node["vallist"] >= 0 else b""
        out = []
        for i in range(node["nval"]):
            voff = struct.unpack("<I", offs[i * 4:i * 4 + 4])[0]
            v = self.cell(voff)
            if not v or v[:2] != b"vk":
                continue
            nlen = struct.unpack("<H", v[2:4])[0]
            dsize = struct.unpack("<I", v[4:8])[0]
            dtype = struct.unpack("<I", v[12:16])[0]
            vflags = struct.unpack("<H", v[16:18])[0]
            if dsize & 0x80000000:
                dsize &= 0x7FFFFFFF
                raw = v[8:8 + dsize]
            else:
                raw = self.cell(struct.unpack("<I", v[8:12])[0]) or b""
            out.append({"name": self._name(v[20:20 + nlen],
                                           vflags & 1) or "(default)",
                        "type": TYPES.get(dtype, hex(dtype)),
                        "raw": raw[:dsize]})
        return out

    def find(self, path):
        """walk ROOT/Sub/Key -> (nk, path-parts) or (None, [])."""
        node, cur = self.nk(self.root), []
        if not node:
            return None, []
        parts = [p for p in path.strip("/\\").replace("\\", "/")
                 .split("/") if p]
        if parts and parts[0].lower() == node["name"].lower():
            parts = parts[1:]
        cur = [node]
        for want in parts:
            nxt = None
            for off in self.sub_offsets(node["sublist"]) + \
                      self.sub_offsets(node["sublist_v"]):
                k = self.nk(off)
                if k and k["name"].lower() == want.lower():
                    nxt = k
                    break
            if not nxt:
                return None, [n["name"] for n in cur]
            node, cur = nxt, cur + [nxt]
        return node, [n["name"] for n in cur]

    def tree(self, node=None, prefix="", out=None):
        out = [] if out is None else out
        node = self.nk(self.root) if node is None else node
        if not node:
            return out
        path = f"{prefix}/{node['name']}" if prefix else node["name"]
        out.append({"path": path, "time": node["time"],
                    "subkeys": node["nsub"], "values": node["nval"]})
        for off in self.sub_offsets(node["sublist"]) + \
                  self.sub_offsets(node["sublist_v"]):
            self.tree(self.nk(off), path, out)
        return out


def _val_text(v):
    t, r = v["type"], v["raw"]
    if t in ("SZ", "EXPAND_SZ"):
        return r.decode("utf-16-le", "replace").rstrip("\x00")
    if t == "MULTI_SZ":
        return [s for s in r.decode("utf-16-le", "replace")
                .split("\x00") if s]
    if t in ("DWORD", "DWORD_BE") and len(r) >= 4:
        return struct.unpack("<I" if t == "DWORD" else ">I", r[:4])[0]
    if t == "QWORD" and len(r) >= 8:
        return struct.unpack("<Q", r[:8])[0]
    return r.hex()


def userassist(hv):
    node, _ = hv.find("Software/Microsoft/Windows/CurrentVersion/"
                      "Explorer/UserAssist")
    rows = []
    if not node:
        return rows
    for goff in hv.sub_offsets(node["sublist"]):
        guid = hv.nk(goff)
        if not guid:
            continue
        for coff in hv.sub_offsets(guid["sublist"]):
            ck = hv.nk(coff)
            if not ck or ck["name"].lower() != "count":
                continue
            for v in hv.values(ck):
                d = v["raw"]
                name = codecs.decode(v["name"], "rot_13")
                row = {"guid": guid["name"], "path_rot13": name}
                if len(d) == 16:        # XP blob
                    row.update(count=struct.unpack("<I", d[4:8])[0] - 5,
                               time=_ft(d[8:16]))
                elif len(d) in (68, 72):  # Vista/7+ blob
                    row.update(count=struct.unpack("<I", d[4:8])[0],
                               focus_ms=struct.unpack("<I", d[12:16])[0],
                               time=_ft(d[60:68]))
                else:
                    row["note"] = f"unknown {len(d)}-byte blob"
                rows.append(row)
    return rows


def _cell(content):
    """content -> full cell: negative size header + pad to 8."""
    size = 4 + len(content)
    pad = (-size) % 8
    return struct.pack("<i", -(size + pad)) + content + b"\x00" * pad


def _nk(name, sublist=-1, nsub=0, vallist=-1, nval=0, ts=133e15):
    nb = name.encode("latin-1")
    return (b"nk" + struct.pack("<H", 0x20) + struct.pack("<Q", int(ts))
            + b"\x00" * 4 + struct.pack("<i", -1)
            + struct.pack("<I", nsub) + b"\x00" * 4
            + struct.pack("<i", sublist) + struct.pack("<i", -1)
            + struct.pack("<I", nval) + struct.pack("<i", vallist)
            + b"\x00" * 8 + b"\x00" * 20
            + struct.pack("<HH", len(nb), 0) + nb)


def _vk(name, dtype, doff, dsize):
    nb = name.encode("latin-1")
    return (b"vk" + struct.pack("<H", len(nb))
            + struct.pack("<II", dsize, doff)
            + struct.pack("<I", dtype) + struct.pack("<HH", 1, 0) + nb)


def _selftest():
    # build cells in order, tracking each one's hbin-relative offset
    offs, cells, pos = {}, [], 0

    def put(content):
        nonlocal pos
        c = _cell(content)
        cells.append(c)
        o, pos = pos, pos + len(c)
        return o

    data = "flag{x}".encode("utf-16-le") + b"\x00\x00"
    # full-size placeholders: offsets patched in place, size unchanged
    offs["root"] = put(_nk("ROOT"))
    offs["sub"] = put(_nk("Sub"))
    offs["lf"] = put(b"lf" + struct.pack("<H", 1)
                     + struct.pack("<I", offs["sub"]))
    offs["vlist"] = put(b"\x00" * 4)          # one vk offset, patched
    offs["vk"] = put(_vk("Val", 1, 0, 0))
    offs["data"] = put(data)
    cells[0] = _cell(_nk("ROOT", sublist=offs["lf"], nsub=1))
    cells[1] = _cell(_nk("Sub", vallist=offs["vlist"], nval=1))
    cells[3] = _cell(struct.pack("<I", offs["vk"]))
    cells[4] = _cell(_vk("Val", 1, offs["data"], len(data)))
    body = b"".join(cells)
    hive = bytearray(0x1000 + max(0x1000, len(body) + 0x20))
    hive[:4] = b"regf"
    struct.pack_into("<I", hive, 0x24, 0)
    struct.pack_into("<I", hive, 0x28, len(body))
    hive[0x1000:0x1004] = b"hbin"
    struct.pack_into("<I", hive, 0x1008, len(body) + 0x20)
    hive[0x1020:0x1020 + len(body)] = body
    tmp = Path(tempfile.mkdtemp()) / "t.dat"
    tmp.write_bytes(bytes(hive))
    hv = Hive(tmp)
    t = hv.tree()
    assert [r["path"] for r in t] == ["ROOT", "ROOT/Sub"], t
    node, _ = hv.find("Sub")
    vals = hv.values(node)
    assert vals[0]["name"] == "Val" and \
        _val_text(vals[0]) == "flag{x}", (vals, _val_text(vals[0]))
    print("hive_parse selftest: ok")


def main():
    ap = argparse.ArgumentParser(
        description="read an offline registry hive (regf)")
    ap.add_argument("hive", nargs="?")
    ap.add_argument("cmd", nargs="?", default="tree",
                    choices=["tree", "get", "userassist"])
    ap.add_argument("key", nargs="?")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.hive:
        ap.error("hive required")
    hv = Hive(a.hive)
    if a.cmd == "tree":
        print(json.dumps(hv.tree(), indent=1))
    elif a.cmd == "get":
        if not a.key:
            ap.error("get needs a key path")
        node, seen = hv.find(a.key)
        if not node:
            print(json.dumps({"error": "key not found",
                              "walked": seen}))
            return 1
        vals = [{"name": v["name"], "type": v["type"],
                 "value": _val_text(v)} for v in hv.values(node)]
        print(json.dumps({"key": "/".join(seen), "time": node["time"],
                          "values": vals}, indent=1))
    elif a.cmd == "userassist":
        print(json.dumps(userassist(hv), indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
