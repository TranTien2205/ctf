#!/usr/bin/env python3
"""fat_read.py -- list/extract files on a FAT12/16/32 image.

Usage:
  python3 tools/forensics/fat_read.py image.img list
  python3 tools/forensics/fat_read.py image.img list --deleted
  python3 tools/forensics/fat_read.py image.img get /DIR/FILE.TXT
  python3 tools/forensics/fat_read.py --selftest

BPB @0: bytes/sector @11, sectors/cluster @13, reserved @14,
FAT count @16, root entries @17, total sectors @19/32, FAT size
@22 (u16) or @36 (u32 on FAT32), root cluster @44. FAT12 vs 16 vs
32 is decided by cluster count. Directory entries are 32 bytes:
8.3 name @0 (0xE5 first byte = deleted), attr @11 (0x0F = LFN
piece, 0x08 volume, 0x10 dir), cluster @20 lo + @26 hi (FAT32),
size @28. LFN pieces assemble the long name in reverse order.
"""
import argparse
import json
import struct
import sys
import tempfile
from pathlib import Path

FREE, EOC = 0x000, 0xFF8


class FAT:
    def __init__(self, path):
        d = Path(path).read_bytes()
        if len(d) < 512:
            raise ValueError("image too small")
        self.d = d
        bps = struct.unpack("<H", d[11:13])[0]
        spc = d[13]
        self.res = struct.unpack("<H", d[14:16])[0]
        nfat = d[16]
        self.rootent = struct.unpack("<H", d[17:19])[0]
        tot = struct.unpack("<H", d[19:21])[0] or \
            struct.unpack("<I", d[32:36])[0]
        fsz = struct.unpack("<H", d[22:24])[0] or \
            struct.unpack("<I", d[36:40])[0]
        self.bps, self.spc = bps, spc
        self.fat0 = self.res * bps
        self.fatbytes = fsz * bps
        root_secs = (self.rootent * 32 + bps - 1) // bps
        self.root_dir = self.fat0 + nfat * self.fatbytes
        self.data0 = self.root_dir + root_secs * bps
        self.clusters = (tot - self.data0 // bps) // spc
        # cluster-count rule per Microsoft FAT spec
        self.kind = ("fat12" if self.clusters < 4085 else
                     "fat16" if self.clusters < 65525 else "fat32")
        self.eoc = {"fat12": 0xFF8, "fat16": 0xFFF8,
                    "fat32": 0x0FFFFFF8}[self.kind]
        self.root_cl = struct.unpack("<I", d[44:48])[0] \
            if self.kind == "fat32" else None

    def _fat(self, n):
        if self.kind == "fat12":
            off = self.fat0 + n * 3 // 2
            v = struct.unpack("<H", self.d[off:off + 2])[0]
            return v >> 4 if n & 1 else v & 0xFFF
        w = 2 if self.kind == "fat16" else 4
        v = struct.unpack("<H" if w == 2 else "<I",
                          self.d[self.fat0 + n * w:
                                 self.fat0 + n * w + w])[0]
        return v & 0x0FFFFFFF if w == 4 else v

    def chain(self, start):
        out, c, seen = [], start, set()
        while c not in seen and 2 <= c < self.eoc and \
                len(out) < 4096:
            seen.add(c)
            out.append(c)
            c = self._fat(c)
        return out

    def _clu(self, n):
        off = self.data0 + (n - 2) * self.spc * self.bps
        return self.d[off:off + self.spc * self.bps]

    def _dirdata(self, cluster):
        if cluster is None:                    # FAT12/16 root area
            return self.d[self.root_dir:self.root_dir +
                          self.rootent * 32]
        return b"".join(self._clu(c) for c in self.chain(cluster))

    def entries(self, cluster=None):
        raw = self._dirdata(cluster)
        out, lfn = [], []
        for i in range(0, len(raw) - 31, 32):
            e = raw[i:i + 32]
            if e[0] == 0:
                break
            attr = e[11]
            if attr == 0x0F:                   # LFN piece
                seq = e[0] & 0x3F
                part = e[1:11] + e[14:26] + e[28:32]
                lfn.insert(0 if e[0] & 0x40 else len(lfn),
                           (seq, part))
                lfn.sort(key=lambda t: t[0])
                continue
            deleted = e[0] == 0xE5
            name83 = (b"?" + e[1:8]).decode("ascii", "replace") \
                if deleted else e[:8].decode("ascii", "replace")
            name83 = name83.rstrip()
            ext = e[8:11].decode("ascii", "replace").rstrip()
            if ext:
                name83 += "." + ext
            long_name = ""
            if lfn:
                try:
                    long_name = b"".join(p for _, p in lfn) \
                        .decode("utf-16-le", "replace") \
                        .split("\x00")[0]
                except Exception:
                    pass
            lfn = []
            cl = (struct.unpack("<H", e[26:28])[0] |
                  (struct.unpack("<H", e[20:22])[0] << 16))
            out.append({"name": long_name or name83,
                        "name83": name83, "attr": attr,
                        "dir": bool(attr & 0x10),
                        "vol": bool(attr & 0x08),
                        "deleted": deleted, "cluster": cl,
                        "size": struct.unpack("<I", e[28:32])[0],
                        "raw0": e[0]})
        return out

    def tree(self, cluster=None, prefix="", out=None, depth=0):
        out = [] if out is None else out
        for e in self.entries(cluster):
            if e["vol"] or e["name83"] in (".", ".."):
                continue
            p = f"{prefix}/{e['name']}"
            out.append(dict(e, path=p))
            if e["dir"] and not e["deleted"] and depth < 12:
                self.tree(e["cluster"], p, out, depth + 1)
        return out

    def read_file(self, cluster, size):
        return b"".join(self._clu(c)
                        for c in self.chain(cluster))[:size]


def _selftest():
    # minimal FAT16: BPB + 1 FAT + root dir + 2 data clusters
    bps, spc, res, nfat, fsz, rent = 512, 1, 1, 1, 1, 16
    root_secs = rent * 32 // bps
    total = res + nfat * fsz + root_secs + 4
    img = bytearray(total * bps)
    struct.pack_into("<HB", img, 11, bps, spc)
    struct.pack_into("<H", img, 14, res)
    img[16] = nfat
    struct.pack_into("<H", img, 17, rent)
    struct.pack_into("<H", img, 19, total)
    struct.pack_into("<H", img, 22, fsz)
    img[510:512] = b"\x55\xaa"
    # FAT12 entries (12-bit packed): cl0/1 media, cl2->EOC, cl3->EOC
    f0 = res * bps
    img[f0:f0 + 6] = bytes([0xF0, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
    rdir = f0 + fsz * bps
    def dent(i, name, ext, attr, cl, size, deleted=False):
        e = bytearray(32)
        e[:8] = name.ljust(8)
        e[8:11] = ext.ljust(3)
        if deleted:
            e[0] = 0xE5
        e[11] = attr
        struct.pack_into("<H", e, 26, cl)
        struct.pack_into("<I", e, 28, size)
        img[rdir + i * 32:rdir + i * 32 + 32] = e
    dent(0, b"FLAG", b"TXT", 0x20, 2, 20)
    dent(1, b"OLD", b"BIN", 0x20, 3, 10, deleted=True)
    img[rdir + 2 * 32] = 0
    data0 = rdir + root_secs * bps
    img[data0:data0 + 20] = b"flag{fat16_deleted!!}"
    img[data0 + bps:data0 + bps + 10] = b"deleted123"
    tmp = Path(tempfile.mkdtemp()) / "t.img"
    tmp.write_bytes(bytes(img))
    f = FAT(tmp)
    t = f.tree()
    names = {e["name83"] for e in t}
    assert "FLAG.TXT" in names and "?LD.BIN" in \
        {e["name83"] for e in t if e["deleted"]}, names
    fl = [e for e in t if e["name83"] == "FLAG.TXT"][0]
    assert f.read_file(fl["cluster"], fl["size"]).startswith(
        b"flag{fat16")
    od = [e for e in t if e["deleted"]][0]
    assert f.read_file(od["cluster"], od["size"]) == b"deleted123"
    print("fat_read selftest: ok")


def main():
    ap = argparse.ArgumentParser(
        description="list/extract files on a FAT image")
    ap.add_argument("file", nargs="?")
    ap.add_argument("cmd", nargs="?", default="list",
                    choices=["list", "get"])
    ap.add_argument("path", nargs="?")
    ap.add_argument("--deleted", action="store_true",
                    help="list only deleted entries")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.file:
        ap.error("file required")
    f = FAT(a.file)
    if a.cmd == "list":
        t = f.tree()
        if a.deleted:
            t = [e for e in t if e["deleted"]]
        print(json.dumps({"fat": f.kind, "entries": t}, indent=1))
    else:
        if not a.path:
            ap.error("get needs a path")
        want = a.path.strip("/").lower()
        hit = [e for e in f.tree() if e["path"].lstrip("/").lower()
               == want or e["name"].lower() == want]
        if not hit:
            print(json.dumps({"error": "path not found"}))
            return 1
        e = hit[0]
        data = f.read_file(e["cluster"], e["size"])
        print(json.dumps({k: e[k] for k in ("path", "size",
                                            "deleted", "cluster")},
                         indent=1))
        try:
            print(data.decode("utf-8"))
        except UnicodeDecodeError:
            print(data.hex())


if __name__ == "__main__":
    raise SystemExit(main())
