#!/usr/bin/env python3
"""squashfs_read.py -- list/extract a squashfs image (zlib only).

Usage:
  python3 tools/forensics/squashfs_read.py fs.sqsh list
  python3 tools/forensics/squashfs_read.py fs.sqsh get /path/file
  python3 tools/forensics/squashfs_read.py --selftest

Superblock @0: magic 0x73717368, compressor u16 @0x14 (1=gzip),
block_size @0x0C, root inode ref @0x20, table starts @0x40 (inode),
@0x48 (dir), @0x50 (frag). Metadata blocks carry a 2-byte header:
bit15 = uncompressed, low 15 = size (zlib-deflated otherwise).
Inode refs are u64 = (table offset << 16) | byte offset inside the
decompressed block. Basic dir inode type 1 and basic file inode
type 2 are decoded; files tail into a fragment via frag table
lookup when frag != 0xFFFFFFFF. Other compressors/inode types are
reported, not guessed.
"""
import argparse
import json
import struct
import sys
import tempfile
import zlib
from pathlib import Path

GZIP, TYPES = 1, {1: "dir", 2: "file", 3: "symlink", 8: "ldir",
                  9: "lfile"}


class SquashFS:
    def __init__(self, path):
        d = Path(path).read_bytes()
        if d[:4] != b"hsqs":
            raise ValueError("not squashfs (magic hsqs missing)")
        self.d = d
        self.bsz = struct.unpack("<I", d[0x0C:0x10])[0]
        self.comp = struct.unpack("<H", d[0x14:0x16])[0]
        self.root_ref = struct.unpack("<Q", d[0x20:0x28])[0]
        self.itab = struct.unpack("<Q", d[0x40:0x48])[0]
        self.dtab = struct.unpack("<Q", d[0x48:0x50])[0]
        self.ftab = struct.unpack("<Q", d[0x50:0x58])[0]
        self.frags = struct.unpack("<I", d[0x10:0x14])[0]
        if self.comp != GZIP:
            raise ValueError(
                f"compressor id {self.comp} - only gzip/zlib "
                "(id 1) is decoded here")

    def _mblk(self, off):
        h = struct.unpack("<H", self.d[off:off + 2])[0]
        n = h & 0x7FFF
        raw = self.d[off + 2:off + 2 + n]
        return raw if h & 0x8000 else zlib.decompress(raw), off + 2 + n

    def _inode(self, ref):
        blk_off, inner = ref >> 16, ref & 0xFFFF
        buf, nxt = self._mblk(self.itab + blk_off)
        return self._parse_inode(buf[inner:])

    def _parse_inode(self, b):
        itype = struct.unpack("<H", b[:2])[0]
        if itype == 1:      # basic dir: 4H + I I I I + H H + I
            (start, nlink, size, off, parent) = struct.unpack(
                "<IIHHI", b[16:32])
            return {"type": "dir", "start": start, "size": size,
                    "off": off}
        if itype == 2:      # basic file
            (start, frag, boff, size) = struct.unpack(
                "<IIII", b[16:32])
            nblk = (size + self.bsz - 1) // self.bsz if \
                frag == 0xFFFFFFFF else size // self.bsz
            blocks = [struct.unpack("<I", b[32 + i * 4:36 + i * 4])[0]
                      for i in range(nblk)]
            return {"type": "file", "start": start, "frag": frag,
                    "boff": boff, "size": size, "blocks": blocks}
        return {"type": TYPES.get(itype, hex(itype)),
                "unsupported": itype}

    def listdir(self, ref):
        """read the dir inode's dir-table block -> name->ref map."""
        node = self._inode(ref)
        if node["type"] != "dir":
            return None
        buf, _ = self._mblk(self.dtab + node["start"])
        pos, out = node["off"], {}
        end = pos + node["size"] - 3   # size counts '.' entry
        while pos < end and pos + 12 <= len(buf):
            count, dstart, dino = struct.unpack("<III",
                                                buf[pos:pos + 12])
            pos += 12
            for _ in range(count + 1):
                off, diff, typ, nlen = struct.unpack("<HhHH",
                                                     buf[pos:pos + 8])
                name = buf[pos + 8:pos + 8 + nlen + 1].decode(
                    "utf-8", "replace")
                # inode ref = header start_block<<16 | entry offset
                out[name] = (dstart << 16) | off
                pos += 8 + nlen + 1
        return out

    def tree(self, ref=None, prefix="", out=None, depth=0):
        out = [] if out is None else out
        ref = self.root_ref if ref is None else ref
        node = self._inode(ref)
        entries = self.listdir(ref)
        for name, eref in sorted((entries or {}).items()):
            if name in (".", ".."):
                continue
            p = f"{prefix}/{name}"
            n = self._inode(eref)
            out.append({"path": p, "type": n["type"],
                        "size": n.get("size")})
            if n["type"] == "dir" and depth < 16:
                self.tree(eref, p, out, depth + 1)
        return out

    def read_file(self, ref):
        n = self._inode(ref)
        if n["type"] != "file":
            return None
        parts, pos = [], n["start"]
        for i, blen in enumerate(n["blocks"]):
            n_, unc = blen & 0xFFFFFF, blen & 0x1000000
            chunk = self.d[pos:pos + n_]
            pos += n_
            parts.append(chunk if unc else zlib.decompress(chunk))
        data = b"".join(parts)[:n["size"]]
        if n["frag"] != 0xFFFFFFFF and self.frags:
            # frag table: u64 block addresses per fragment, stored as
            # metadata inside the frag table itself
            fb, _ = self._mblk(self.ftab + (n["frag"] // 512) * 8)
            ent = struct.unpack("<QII", fb[(n["frag"] % 512) * 16:
                                          (n["frag"] % 512) * 16 + 16])
            fr, _ = self._mblk(ent[0])
            data += fr[n["boff"]:n["boff"] + ent[1]]
            data = data[:n["size"]]
        return data


def _find(hv, path):
    cur = hv.root_ref
    node = hv._inode(cur)
    for part in [p for p in path.split("/") if p]:
        if node["type"] != "dir":
            return None
        ents = hv.listdir(cur)
        cur = ents.get(part)
        if cur is None:
            return None
        node = hv._inode(cur)
    return cur, node


def _mblk(raw, compress=True):
    body = zlib.compress(raw) if compress else raw
    flag = 0 if compress else 0x8000
    return struct.pack("<H", flag | len(body)) + body


def _selftest():
    # one-dir/one-file image: file inode then dir inode in itab,
    # one dir-table header+entry, plain-text data block
    fbody = b"flag{squashfs_stdlib}"
    dinode = struct.pack("<HHHHIIIIHHI", 1, 0o40755, 0, 0, 0, 2,
                         0, 1, 29 + 3, 0, 1)
    finode = struct.pack("<HHHHIIIIII", 2, 0o100644, 0, 0, 0, 1,
                         0, 0xFFFFFFFF, 0, len(fbody)) + \
        struct.pack("<I", 0x1000000 | len(fbody))
    itab_body = bytearray(finode + dinode)
    name = b"flag.txt"
    dentry = struct.pack("<III", 0, 0, 1) + \
        struct.pack("<HhHH", 0, 0, 2, len(name) - 1) + name
    dtab = _mblk(dentry)
    itab_off = 96
    # compressed itab length depends on the patched start value;
    # iterate until data_off stabilises
    data_off = 0
    for _ in range(4):
        struct.pack_into("<I", itab_body, 16, data_off)
        itab = _mblk(bytes(itab_body))
        new = itab_off + len(itab) + len(dtab)
        if new == data_off:
            break
        data_off = new
    dtab_off = itab_off + len(itab)
    fref = 0
    dref = len(finode)
    # dir inode start points at dtab block offset 0 (relative)
    sb = bytearray(96)
    struct.pack_into("<I", sb, 0, 0x73717368)
    struct.pack_into("<I", sb, 0x0C, 131072)
    struct.pack_into("<I", sb, 0x10, 0)
    struct.pack_into("<H", sb, 0x14, 1)
    struct.pack_into("<Q", sb, 0x20, dref)
    struct.pack_into("<Q", sb, 0x40, itab_off)
    struct.pack_into("<Q", sb, 0x48, dtab_off)
    struct.pack_into("<Q", sb, 0x50, 0xFFFFFFFF)
    img = bytes(sb) + itab + dtab + fbody
    tmp = Path(tempfile.mkdtemp()) / "t.sqsh"
    tmp.write_bytes(img)
    sq = SquashFS(tmp)
    t = sq.tree()
    assert t and t[0]["path"] == "/flag.txt" and t[0]["size"] == \
        len(fbody), t
    ref, node = _find(sq, "/flag.txt")
    assert node["type"] == "file", node
    assert sq.read_file(ref) == fbody
    print("squashfs_read selftest: ok")


def main():
    ap = argparse.ArgumentParser(
        description="list/extract a squashfs image (zlib only)")
    ap.add_argument("file", nargs="?")
    ap.add_argument("cmd", nargs="?", default="list",
                    choices=["list", "get"])
    ap.add_argument("path", nargs="?")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.file:
        ap.error("file required")
    sq = SquashFS(a.file)
    if a.cmd == "list":
        print(json.dumps(sq.tree(), indent=1))
    else:
        if not a.path:
            ap.error("get needs a path")
        found = _find(sq, a.path)
        if not found:
            print(json.dumps({"error": "path not found"}))
            return 1
        ref, node = found
        data = sq.read_file(ref) if node["type"] == "file" else None
        print(json.dumps({"path": a.path, "type": node["type"],
                          "size": node.get("size"),
                          "data": data.decode("utf-8", "replace")
                          if data else None}))


if __name__ == "__main__":
    raise SystemExit(main())
