#!/usr/bin/env python3
"""cfb_parse.py -- read an OLE compound file (CFB): streams + DestList.

Usage:
  python3 tools/forensics/cfb_parse.py file.bin list
  python3 tools/forensics/cfb_parse.py file.bin get 'StreamName'
  python3 tools/forensics/cfb_parse.py x.automaticDestinations-ms destlist
  python3 tools/forensics/cfb_parse.py --selftest

CFB: 512-byte header (signature D0CF11E0A1B11AE1, sector shift @30,
mini cutoff @56, FAT/DIFAT/MiniFAT roots), then 512-byte sectors.
Directory entries are 128 bytes: UTF-16LE name, type (5 root / 2
stream / 1 storage), start sector + size at +116/+120. Streams under
4096 bytes live in the root's mini stream via MiniFAT chains.
DestList (libyal/dtformats): 32-byte header (version @0, count @4),
entries: hostname @72 (16 ASCII), entry number @88, last-modified
FILETIME @100, pin status @108, then u16 char count + UTF-16 path at
112 (v1) or 128 (v3/4).
"""
import argparse
import json
import struct
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

EPOCH = datetime(1601, 1, 1)
FREE, END, FATSEC, DIFSEC = 0xFFFFFFFF, 0xFFFFFFFE, 0xFFFFFFFD, 0xFFFFFFFC


def _ft(b):
    v = struct.unpack("<Q", b[:8])[0]
    return (EPOCH + timedelta(microseconds=v / 10)).isoformat() if v else None


class CFB:
    def __init__(self, path):
        d = Path(path).read_bytes()
        if d[:8] != b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1":
            raise ValueError("not a CFB file")
        self.d = d
        self.ssz = 1 << struct.unpack("<H", d[30:32])[0]
        self.cutoff = struct.unpack("<I", d[56:60])[0]
        self.dir0 = struct.unpack("<I", d[48:52])[0]
        self.mfat0 = struct.unpack("<I", d[60:64])[0]
        self.mfatn = struct.unpack("<I", d[64:68])[0]
        difat = list(struct.unpack("<109I", d[76:76 + 436]))
        pos = struct.unpack("<I", d[68:72])[0]
        for _ in range(struct.unpack("<I", d[72:76])[0]):
            sec = self._sec(pos)
            difat += struct.unpack(f"<{self.ssz // 4 - 1}I", sec[:-4])
            pos = struct.unpack("<I", sec[-4:])[0]
        self.fat = []
        for s in difat:
            if s < FATSEC:
                self.fat += struct.unpack(f"<{self.ssz // 4}I",
                                          self._sec(s))
        self._dirs = None
        self._minifat = self._chain(self.mfat0)
        self._ministream = None

    def _sec(self, n):
        off = 512 + n * self.ssz
        return self.d[off:off + self.ssz]

    def _chain(self, start):
        out, s = bytearray(), start
        while s not in (END, FREE) and s < len(self.fat):
            out += self._sec(s)
            s = self.fat[s]
        return bytes(out)

    def _minichain(self, start):
        if self._ministream is None:
            root = self.dirs()[0]
            self._ministream = self._chain(root["start"])
        out, s = bytearray(), start
        while s not in (END, FREE) and s < len(self._minifat):
            out += self._ministream[s * 64:s * 64 + 64]
            s = struct.unpack("<I",
                              self._minifat[s * 4:s * 4 + 4])[0]
        return bytes(out)

    def dirs(self):
        if self._dirs is None:
            raw = self._chain(self.dir0)
            self._dirs = []
            for i in range(0, len(raw) - 127, 128):
                e = raw[i:i + 128]
                nl = struct.unpack("<H", e[64:66])[0]
                if nl < 2:
                    continue
                self._dirs.append({
                    "name": e[:nl - 2].decode("utf-16-le", "replace"),
                    "type": e[66],
                    "start": struct.unpack("<I", e[116:120])[0],
                    "size": struct.unpack("<Q", e[120:128])[0]})
        return self._dirs

    def stream(self, name):
        for e in self.dirs():
            if e["name"] == name and e["type"] == 2:
                raw = (self._minichain(e["start"])
                       if e["size"] < self.cutoff else
                       self._chain(e["start"]))
                return raw[:e["size"]]
        return None


def destlist(raw):
    ver, count = struct.unpack("<II", raw[:8])
    # v1: u16 path size @112, path @114; v3+: u16 @128, path @130
    soff = 128 if ver >= 3 else 112
    rows, pos = [], 32
    for _ in range(count):
        e = raw[pos:pos + soff + 2]
        if len(e) < soff + 2:
            break
        n = struct.unpack("<H", e[soff:soff + 2])[0]
        path_off = pos + soff + 2
        rows.append({
            "hostname": e[72:88].split(b"\x00")[0].decode("ascii",
                                                         "replace"),
            "entry": struct.unpack("<I", e[88:92])[0],
            "mtime": _ft(e[100:108]),
            "pinned": struct.unpack("<i", e[108:112])[0] != -1,
            "path": raw[path_off:path_off + n * 2]
            .decode("utf-16-le", "replace")})
        pos = path_off + n * 2 + 4  # trailing u32 per dtformats
    return {"version": ver, "entries": rows}


def _selftest():
    # one-sector file: dir sector 0 (root entry + stream entry), then
    # stream data sector 1, FAT sector 2, minifat unused (size >= cutoff)
    payload = b"X" * 4096 + b"flag{cfb}"
    ssz = 512
    need = (len(payload) + ssz - 1) // ssz    # stream sectors
    nsec = 1 + need + 1                       # dir + stream + fat
    fatsec = nsec - 1
    d = bytearray(512 + nsec * ssz)
    d[:8] = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"
    struct.pack_into("<H", d, 30, 9)
    struct.pack_into("<I", d, 48, 0)          # dir at sector 0
    struct.pack_into("<I", d, 56, 4096)
    struct.pack_into("<I", d, 60, END)
    struct.pack_into("<II", d, 68, END, 0)
    struct.pack_into("<109I", d, 76,
                     *([fatsec] + [FREE] * 108))
    # directory entries
    def ent(i, name, typ, start, size):
        b = name.encode("utf-16-le") + b"\x00\x00"
        o = 512 + i * 128
        d[o:o + len(b)] = b
        struct.pack_into("<H", d, o + 64, len(b))
        d[o + 66] = typ
        struct.pack_into("<I", d, o + 116, start)
        struct.pack_into("<Q", d, o + 120, size)
    ent(0, "Root Entry", 5, END, 0)
    ent(1, "DestList", 2, 1, len(payload))
    d[512 + ssz:512 + ssz + len(payload)] = payload
    # FAT: dir chain = [0], stream = [1..need], fatsec marks itself
    fat = [FREE] * (ssz // 4)
    fat[0] = END
    for i in range(1, 1 + need):
        fat[i] = i + 1 if i < need else END
    fat[fatsec] = FATSEC
    d[512 + fatsec * ssz:512 + (fatsec + 1) * ssz] = \
        struct.pack(f"<{ssz // 4}I", *fat)
    tmp = Path(tempfile.mkdtemp()) / "t.cfb"
    tmp.write_bytes(bytes(d))
    c = CFB(tmp)
    names = [e["name"] for e in c.dirs()]
    assert names == ["Root Entry", "DestList"], names
    s = c.stream("DestList")
    assert s == payload, len(s or b"")
    # destlist: version 3 header + one entry
    p = "c:\\flag\\x.txt".encode("utf-16-le")
    e = bytearray(130)
    e[72:72 + 4] = b"HOST"
    struct.pack_into("<I", e, 88, 3)
    struct.pack_into("<Q", e, 100, 133000000000000000)
    struct.pack_into("<i", e, 108, -1)
    struct.pack_into("<H", e, 128, len(p) // 2)   # v3: size @128, path @130
    blob = struct.pack("<II", 3, 1) + b"\x00" * 24 + bytes(e) \
        + p + b"\x00" * 4
    r = destlist(blob)
    assert r["entries"][0]["path"].startswith("c:\\flag"), r
    assert r["entries"][0]["hostname"] == "HOST", r
    print("cfb_parse selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="read OLE compound files")
    ap.add_argument("file", nargs="?")
    ap.add_argument("cmd", nargs="?", default="list",
                    choices=["list", "get", "destlist"])
    ap.add_argument("name", nargs="?")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.file:
        ap.error("file required")
    c = CFB(a.file)
    if a.cmd == "list":
        print(json.dumps([{k: v for k, v in e.items()}
                          for e in c.dirs()], indent=1))
    elif a.cmd == "get":
        if not a.name:
            ap.error("get needs a stream name")
        s = c.stream(a.name)
        if s is None:
            print(json.dumps({"error": "stream not found"}))
            return 1
        print(json.dumps({"name": a.name, "size": len(s),
                          "hex": s[:4096].hex()}))
    elif a.cmd == "destlist":
        s = c.stream("DestList")
        if s is None:
            print(json.dumps({"error": "no DestList stream"}))
            return 1
        print(json.dumps(destlist(s), indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
