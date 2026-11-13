#!/usr/bin/env python3
"""exfat_read.py -- list/extract files on an exFAT image.

USB sticks and SD cards in CTF handouts are exFAT far more often
than FAT32; fat_read does not cover it. Layout (VBR @0):
"EXFAT   " @3, FAT offset/length @80/84 (sectors), cluster-heap
offset @88 (sectors), cluster count @92, root dir cluster @96,
sector/cluster shifts @108/109. Cluster N data =
(heap + (N-2)*spc) sectors. FAT entry N = u32 at fat*N, 0xFFFFFFFF
EOC. Directory entries are 32 bytes: 0x85 file (secondary count @1,
attrs @4, DOS times @8/12/16), 0xC0 stream extension (bit1 of @1 =
"no FAT chain, contiguous", valid len @8, first cluster @20, data
len @24), 0xC1 name piece (15 UTF-16 chars @2). Deleted entries
keep the same layout with the type byte's high bit clear
(0x05/0x40/0x41) -- still reportable when slack survives.

  python3 tools/forensics/exfat_read.py image.img list
  python3 tools/forensics/exfat_read.py image.img get /FLAG.TXT
  python3 tools/forensics/exfat_read.py --selftest
"""
import argparse
import json
import struct
import sys
from pathlib import Path

EOC = 0xFFFFFFFF


def _dos_dt(v):
    try:
        return "%04d-%02d-%02d %02d:%02d:%02d" % (
            1980 + (v >> 25), (v >> 21) & 15, (v >> 16) & 31,
            (v >> 11) & 31, (v >> 5) & 63, (v & 31) * 2)
    except Exception:
        return "0x%x" % v


class ExFAT:
    def __init__(self, path, offset=0):
        d = Path(path).read_bytes()[offset:]
        if len(d) < 512 or d[3:11] != b"EXFAT   ":
            raise ValueError("not an exFAT image")
        self.d = d
        self.bps = 1 << d[108]
        self.spc = 1 << d[109]
        self.fat_off = struct.unpack("<I", d[80:84])[0] * self.bps
        self.fat_len = struct.unpack("<I", d[84:88])[0] * self.bps
        self.heap = struct.unpack("<I", d[88:92])[0] * self.bps
        self.ccount = struct.unpack("<I", d[92:96])[0]
        self.root_cl = struct.unpack("<I", d[96:100])[0]

    def _cl_off(self, n):
        return self.heap + (n - 2) * self.spc * self.bps

    def _fat(self, n):
        off = self.fat_off + n * 4
        if off + 4 > self.fat_off + self.fat_len or off + 4 > len(self.d):
            return EOC
        return struct.unpack("<I", self.d[off:off + 4])[0]

    def _chain(self, start, contiguous=False):
        cls = []
        if contiguous:
            cls = [start]
        else:
            seen = set()
            n = start
            while 2 <= n < EOC and n not in seen and len(cls) < self.ccount + 2:
                seen.add(n)
                cls.append(n)
                n = self._fat(n)
        return cls

    def _read(self, start, length, contiguous=False):
        if contiguous:
            need = (length + self.spc * self.bps - 1) // (self.spc * self.bps)
            cls = [start + i for i in range(need)]
        else:
            cls = self._chain(start)
        out = b"".join(
            self.d[self._cl_off(c):self._cl_off(c) + self.spc * self.bps]
            for c in cls)
        return out[:length] if length else out

    def _dir_entries(self, data):
        """Group a directory stream into (file, stream, [names]) tuples;
        deleted sets (type 0x05/0x40/0x41) are reported flagged."""
        ents = []
        i = 0
        while i + 32 <= len(data):
            e = data[i:i + 32]
            t = e[0]
            if t == 0x00:
                break
            if t in (0x85, 0x05):
                deleted = t == 0x05
                nsec = e[1]
                grp = [e]
                j = i + 32
                strm, names = None, []
                for _ in range(nsec):
                    s = data[j:j + 32]
                    if len(s) < 32:
                        break
                    st = s[0]
                    if st in (0xC0, 0x40):
                        strm = s
                        deleted = deleted or st == 0x40
                    elif st in (0xC1, 0x41):
                        names.append(s)
                        deleted = deleted or st == 0x41
                    j += 32
                name = "".join(
                    n[2:32].decode("utf-16-le", "replace").rstrip("\x00")
                    for n in names)
                if strm is not None and name:
                    attrs = struct.unpack("<H", e[4:6])[0]
                    flags = strm[1]
                    ents.append({
                        "name": name, "dir": bool(attrs & 0x10),
                        "deleted": deleted,
                        "size": struct.unpack("<Q", strm[24:32])[0],
                        "valid_len": struct.unpack("<Q", strm[8:16])[0],
                        "cluster": struct.unpack("<I", strm[20:24])[0],
                        "contiguous": bool(flags & 0x02),
                        "modified": _dos_dt(
                            struct.unpack("<I", e[12:16])[0])})
                    i = j
                    continue
            i += 32
        return ents

    def _walk(self, path_parts):
        """Return the entry for path_parts walking down from root."""
        # root dir: cluster chain via FAT (root has no stream ext; the
        # chain length is bounded by cluster count)
        ents = None
        data = self._read(self.root_cl, 0)
        for part in path_parts:
            ents = self._dir_entries(data)
            hit = next((e for e in ents
                        if e["name"].upper() == part.upper()), None)
            if hit is None:
                return None, ents
            data = self._read(hit["cluster"], hit["valid_len"]
                              or hit["size"], hit["contiguous"])
        return hit, self._dir_entries(data)

    def list(self, path="/"):
        parts = [p for p in path.split("/") if p]
        data = self._read(self.root_cl, 0)
        for part in parts:
            ents = self._dir_entries(data)
            hit = next((e for e in ents if e["dir"]
                        and e["name"].upper() == part.upper()), None)
            if hit is None:
                return {"error": "dir not found: %s" % part,
                        "entries": ents}
            data = self._read(hit["cluster"], hit["valid_len"]
                              or hit["size"], hit["contiguous"])
        return {"path": path, "entries": self._dir_entries(data)}

    def get(self, path):
        parts = [p for p in path.split("/") if p]
        hit, _ = self._walk(parts)
        if hit is None or hit["dir"]:
            return {"error": "not found: %s" % path}
        blob = self._read(hit["cluster"], hit["valid_len"]
                          or hit["size"], hit["contiguous"])
        return {"name": hit["name"], "size": len(blob),
                "data_hex": blob[:64].hex(),
                "data": blob}

    def info(self):
        return {"bps": self.bps, "spc": self.spc,
                "fat_offset": self.fat_off, "heap_offset": self.heap,
                "cluster_count": self.ccount,
                "root_cluster": self.root_cl}


def _mkimg():
    """Minimal exFAT image: VBR, 1 FAT sector, heap with root dir
    holding two files (one contiguous, one FAT-chained, one deleted)."""
    bps, spc = 512, 1
    fat_off, heap_off = 24, 40
    img = bytearray(heap_off * bps + 6 * bps)
    img[0:3] = b"\xeb\x76\x90"
    img[3:11] = b"EXFAT   "
    struct.pack_into("<IIII", img, 80, fat_off, 1, heap_off, 6)
    struct.pack_into("<I", img, 96, 2)          # root dir = cluster 2
    img[108], img[109] = 9, 0                  # 512B, 1 sec/cluster
    img[510:512] = b"\x55\xaa"
    fat = fat_off * bps
    struct.pack_into("<I", img, fat + 3 * 4, EOC)   # FLAG.TXT: cl3 alone
    struct.pack_into("<I", img, fat + 4 * 4, 6)     # BIG.BIN: cl4 -> cl6
    struct.pack_into("<I", img, fat + 6 * 4, EOC)
    # root dir (cluster 2): FLAG.TXT contiguous @ cl3, BIG.BIN chained,
    # GONE.TXT deleted set (0x05/0x40/0x41)
    def file_ent(name, attrs, size, cl, flags, deleted=False):
        grp = bytearray(32 * (2 + (len(name) + 14) // 15))
        grp[0] = 0x05 if deleted else 0x85
        grp[1] = (len(grp) // 32) - 1
        struct.pack_into("<H", grp, 4, attrs)
        grp[32] = 0x40 if deleted else 0xC0
        grp[33] = flags
        grp[35] = len(name)
        struct.pack_into("<Q", grp, 40, size)
        struct.pack_into("<I", grp, 52, cl)
        struct.pack_into("<Q", grp, 56, size)
        pos = 64
        for i in range(0, len(name), 15):
            grp[pos] = 0x41 if deleted else 0xC1
            chunk = name[i:i + 15].encode("utf-16-le")
            grp[pos + 2:pos + 2 + len(chunk)] = chunk
            pos += 32
        return grp
    root = heap_off * bps
    ents = file_ent("FLAG.TXT", 0x20, 14, 3, 0x03) + \
        file_ent("BIG.BIN", 0x20, 700, 4, 0x01) + \
        file_ent("GONE.TXT", 0x20, 5, 5, 0x03, deleted=True)
    img[root:root + len(ents)] = ents
    cl = lambda n: heap_off * bps + (n - 2) * 512
    img[cl(3):cl(3) + 14] = b"flag{exfat_ok!}"
    img[cl(4):cl(4) + 512] = b"B" * 512          # BIG.BIN cluster 1
    img[cl(6):cl(6) + 188] = b"B" * 188          # BIG.BIN cluster 2
    img[cl(5):cl(5) + 5] = b"stale"              # GONE.TXT slack
    return bytes(img)


def _selftest():
    import tempfile, os
    img = _mkimg()
    with tempfile.NamedTemporaryFile(suffix=".img", delete=False) as t:
        t.write(img)
        p = t.name
    try:
        fs = ExFAT(p)
        assert fs.info()["root_cluster"] == 2
        ls = fs.list("/")
        names = [e["name"] for e in ls["entries"]]
        assert "FLAG.TXT" in names and "GONE.TXT" in names, names
        gone = next(e for e in ls["entries"] if e["name"] == "GONE.TXT")
        assert gone["deleted"] is True
        ok = next(e for e in ls["entries"] if e["name"] == "FLAG.TXT")
        assert ok["contiguous"] is True and ok["size"] == 14
        got = fs.get("/FLAG.TXT")
        assert got["data"].rstrip(b"\x00")[:14] == b"flag{exfat_ok!"
        big = fs.get("/BIG.BIN")
        assert big["size"] == 700 and big["data"][:4] == b"BBBB"
        print("exfat_read selftest: ok")
    finally:
        os.unlink(p)


def main():
    ap = argparse.ArgumentParser(description="exFAT list/extract")
    ap.add_argument("image", nargs="?")
    ap.add_argument("cmd", nargs="?", choices=["info", "list", "get"])
    ap.add_argument("path", nargs="?", default="/")
    ap.add_argument("--offset", type=int, default=0,
                    help="byte offset of the exFAT VBR in a disk image")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.image:
        ap.error("image required")
    fs = ExFAT(a.image, offset=a.offset)
    if a.cmd in (None, "info"):
        out = fs.info()
    elif a.cmd == "list":
        out = fs.list(a.path)
    else:
        out = fs.get(a.path)
        blob = out.pop("data", None)
        if blob is not None:
            print(json.dumps(out, indent=1))
            sys.stdout.buffer.write(blob)
            return
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
