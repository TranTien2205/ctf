#!/usr/bin/env python3
"""ext_read.py -- ext2/3/4 filesystem reader: list dirs, read files.

The disk-image skill's Linux half: fls/icat are external, so this
walks the superblock, group descriptors and inode tables directly.
Both block addressing schemes: ext2-style direct/single-indirect
i_block arrays and ext4 extent trees (header 0xF30A, leaf extents,
one level of index nodes).

  python3 tools/forensics/ext_read.py fs.img sb
  python3 tools/forensics/ext_read.py fs.img ls /etc
  python3 tools/forensics/ext_read.py fs.img get /flag.txt
  python3 tools/forensics/ext_read.py fs.img --offset 1048576 ls /
  python3 tools/forensics/ext_read.py --selftest

Deleted entries are NOT recovered (that needs the journal); the
freed-space story for ext belongs to the journal layer, which is out
of scope here — fat_read covers FAT deletion. Read-only; JSON out.
"""
import argparse
import json
import struct
import sys

FT = {0: "unknown", 1: "file", 2: "dir", 3: "cdev", 4: "bdev",
      5: "fifo", 6: "sock", 7: "symlink"}


class Ext:
    def __init__(self, data, offset=0):
        self.d, self.off = data, offset
        sb = data[offset + 1024:offset + 2048]
        if struct.unpack("<H", sb[56:58])[0] != 0xEF53:
            raise ValueError("no ext superblock at offset+1024")
        self.sb = {
            "inodes": struct.unpack("<I", sb[0:4])[0],
            "blocks": struct.unpack("<I", sb[4:8])[0],
            "free_blocks": struct.unpack("<I", sb[12:16])[0],
            "log_block": struct.unpack("<I", sb[24:28])[0],
            "blocks_per_group": struct.unpack("<I", sb[32:36])[0],
            "inodes_per_group": struct.unpack("<I", sb[40:44])[0],
            "first_ino": struct.unpack("<I", sb[84:88])[0],
            "inode_size": struct.unpack("<H", sb[88:90])[0],
            "feature_ro_compat": struct.unpack("<I", sb[100:104])[0],
            "feature_incompat": struct.unpack("<I", sb[96:100])[0],
            "volume": sb[120:136].split(b"\x00")[0].decode(
                "utf-8", "replace"),
        }
        self.bs = 1024 << self.sb["log_block"]
        self.isz = self.sb["inode_size"] or 128
        gd_off = offset + (2048 if self.bs == 1024 else self.bs)
        self.gdt = data[gd_off:gd_off + 32 *
                        ((self.sb["blocks"] +
                          self.sb["blocks_per_group"] - 1) //
                         self.sb["blocks_per_group"])]

    def block(self, n):
        o = self.off + n * self.bs
        return self.d[o:o + self.bs]

    def inode(self, n):
        g = (n - 1) // self.sb["inodes_per_group"]
        idx = (n - 1) % self.sb["inodes_per_group"]
        itable = struct.unpack("<I", self.gdt[g * 32 + 8:g * 32 + 12])[0]
        raw = self.block(itable)[idx * self.isz:(idx + 1) * self.isz]
        mode, size_lo = struct.unpack("<HxxI", raw[0:8])
        size = size_lo
        if mode & 0x8000:
            size |= struct.unpack("<I", raw[108:112])[0] << 32
        return {"mode": mode, "size": size,
                "type": FT.get((mode >> 12) & 0xF, "file"),
                "i_block": raw[40:100]}

    def _extents(self, ib, ino_size):
        magic = struct.unpack("<H", ib[0:2])[0]
        out = []
        if magic != 0xF30A:
            return None
        nodes = [ib]
        seen = 0
        while nodes and seen < 4096:
            buf = nodes.pop()
            magic, n, _m, depth = struct.unpack("<HHHH", buf[0:8])
            if magic != 0xF30A:
                continue
            seen += 1
            if depth == 0:
                for i in range(n):
                    b, ln, hi, lo = struct.unpack(
                        "<IIHH", buf[12 + i * 12:24 + i * 12])
                    out.append((b, ln, (hi << 32) | lo))
            else:
                for i in range(n):
                    _eb, lo, hi = struct.unpack(
                        "<IIH", buf[12 + i * 6:18 + i * 6])
                    nodes.append(self.block((hi << 32) | lo))
        out.sort()
        return out

    def _blocks(self, ino):
        ib = ino["i_block"]
        ext = self._extents(ib, ino["size"])
        if ext is not None:
            blocks = []
            for _lblk, ln, phys in ext:
                blocks.extend(range(phys, phys + ln))
            return blocks[: (ino["size"] + self.bs - 1) // self.bs]
        ptrs = struct.unpack("<15I", ib)
        blocks = [p for p in ptrs[:12] if p]
        if ptrs[12]:
            blocks.extend(p for p in struct.unpack(
                f"<{self.bs // 4}I", self.block(ptrs[12])) if p)
        return blocks[: (ino["size"] + self.bs - 1) // self.bs]

    def read(self, ino):
        return b"".join(self.block(b) for b in self._blocks(ino))[
            :ino["size"]]

    def ls(self, ino_n):
        ino = self.inode(ino_n)
        raw = self.read(ino)
        out, o = [], 0
        while o + 8 <= len(raw):
            i_n, rec, nl, ft = struct.unpack("<IHBB", raw[o:o + 8])
            if i_n and nl:
                name = raw[o + 8:o + 8 + nl].decode("utf-8", "replace")
                out.append({"name": name, "inode": i_n,
                            "type": FT.get(ft, "?")})
            if rec < 8:
                break
            o += rec
        return out

    def resolve(self, path):
        n = 2
        for part in [p for p in path.split("/") if p]:
            hit = next((e for e in self.ls(n) if e["name"] == part),
                       None)
            if not hit:
                raise KeyError(f"{part}: not found")
            n = hit["inode"]
        return n


def _selftest():
    bs, isz, ipg = 1024, 128, 64
    img = bytearray(bs * 40)
    sb = memoryview(img)[1024:2048]
    struct.pack_into("<IIIII", sb, 0, 32, 40, 8, 30, 0)  # ino,blk,r,free
    struct.pack_into("<I", sb, 24, 0)                    # bs=1024
    struct.pack_into("<III", sb, 32, 40, 40, ipg)
    struct.pack_into("<II", sb, 84, 11, isz)
    struct.pack_into("<H", sb, 56, 0xEF53)
    sb[120:128] = b"testfs\x00\x00"
    gdt = memoryview(img)[2048:2080]
    struct.pack_into("<I", gdt, 8, 5)                    # inode table blk 5
    del sb, gdt
    itab = 5 * bs

    def put_inode(n, mode, size, i_block):
        o = itab + (n - 1) * isz
        struct.pack_into("<HxxI", img, o, mode, size)
        img[o + 40:o + 100] = i_block

    # dir block 20: ".", "..", "flag.txt"(ino 3)
    dblk = 20 * bs
    for off, i_n, name in ((0, 2, b"."), (12, 2, b".."),
                           (24, 3, b"flag.txt")):
        struct.pack_into("<IHBB", img, dblk + off, i_n, 12,
                         len(name), 2 if name.startswith(b".") else 1)
        img[dblk + off + 8:dblk + off + 8 + len(name)] = name
    root_ib = struct.pack("<15I", 20, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                          0, 0, 0, 0, 0)
    put_inode(2, 0o40755, bs, root_ib)
    fdat = b"flag{ext4_extent_cover}\x00" + b"\x00" * (bs - 25)
    img[21 * bs:22 * bs] = fdat
    # ext4-style extent inode for the file: magic F30A, 1 leaf extent
    ex = struct.pack("<HHHHI", 0xF30A, 1, 4, 0, 0) + \
        struct.pack("<IIHH", 0, 1, 0, 21)
    put_inode(3, 0o100644, 24, ex + b"\x00" * (60 - len(ex)))
    e = Ext(bytes(img))
    assert e.sb["volume"] == "testfs" and e.bs == 1024
    names = [x["name"] for x in e.ls(2)]
    assert "flag.txt" in names, names
    n = e.resolve("/flag.txt")
    assert n == 3
    assert e.read(e.inode(3)) == b"flag{ext4_extent_cover}\x00"
    print("ext_read selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="ext2/3/4 reader")
    ap.add_argument("image", nargs="?")
    ap.add_argument("cmd", nargs="?", choices=["sb", "ls", "get"])
    ap.add_argument("path", nargs="?", default="/")
    ap.add_argument("--offset", type=int, default=0,
                    help="byte offset of the ext filesystem")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not (a.image and a.cmd):
        ap.error("image and cmd required")
    try:
        e = Ext(open(a.image, "rb").read(), a.offset)
    except ValueError as ex:
        sys.exit(str(ex))
    if a.cmd == "sb":
        print(json.dumps(e.sb, indent=1))
    elif a.cmd == "ls":
        try:
            n = e.resolve(a.path)
        except KeyError as ex:
            sys.exit(str(ex))
        print(json.dumps({"path": a.path, "inode": n,
                          "entries": e.ls(n)}, indent=1))
    else:
        try:
            n = e.resolve(a.path)
        except KeyError as ex:
            sys.exit(str(ex))
        sys.stdout.buffer.write(e.read(e.inode(n)))


if __name__ == "__main__":
    raise SystemExit(main())
