#!/usr/bin/env python3
"""cramfs_read.py -- cramfs image listing and extraction.

Older firmware dumps still ship cramfs: a 64-byte superblock
(magic 0x28cd3d45, 'Compressed ROMFS'), then a table of packed
12-byte inodes (mode/uid/size+gid/namelen+offset) followed by
namelen*4-aligned names, then file bodies in zlib-compressed 4KiB
blocks. `cramfsck`/`fsck.cramfs` are not assumed. `list` walks the
directory inode tree; `get PATH` inflates a file's block pointers
one by one (the on-disk layout stores one u32 pointer per 4KiB
block at the file's offset*4 address).

  python3 tools/forensics/cramfs_read.py fs.cramfs list
  python3 tools/forensics/cramfs_read.py fs.cramfs get /flag.txt
  python3 tools/forensics/cramfs_read.py --selftest
"""
import argparse
import json
import struct
import sys
import zlib

MAGIC = 0x28CD3D45


def _inode(data, off):
    mode, uid, sz_gid, nm_off = struct.unpack("<HHI I", data[off:off+12])
    size = sz_gid & 0xFFFFFF
    gid = sz_gid >> 24
    namelen = (nm_off & 0x3F) * 4
    boff = (nm_off >> 6) * 4
    name = data[off + 12:off + 12 + namelen].rstrip(
        b"\x00").decode("utf-8", "replace")
    return {"mode": mode, "uid": uid, "gid": gid, "size": size,
            "name": name, "blocks_off": boff,
            "is_dir": (mode & 0xF000) == 0x4000,
            "is_file": (mode & 0xF000) == 0x8000}


def _ls(data, ino_off, depth=0):
    if depth > 32:
        return []
    ino = _inode(data, ino_off)
    out = []
    if ino["is_dir"]:
        p = ino["blocks_off"]
        end = p + ino["size"]
        while p < end and p + 12 <= len(data):
            child = _inode(data, p)
            _sz_gid, nm_off = struct.unpack("<II", data[p + 4:p + 12])
            nl = (nm_off & 0x3F) * 4
            if nl == 0:
                break
            step = 12 + ((nl + 3) & ~3)
            rec = dict(child)
            rec["at"] = p
            out.append(rec)
            out.extend(_ls(data, p, depth + 1))
            p += step
    return out


def _read(data, ino):
    nblocks = (ino["size"] + 4095) // 4096
    p = ino["blocks_off"]
    body = b""
    ptrs = [struct.unpack("<I", data[p + 4 * i:p + 4 * i + 4])[0]
            for i in range(nblocks)]
    for off in ptrs:
        if off == 0:
            continue
        body += zlib.decompress(data[off:])
    return body[:ino["size"]]


def parse(data, path=None):
    if len(data) < 64 or struct.unpack("<I", data[:4])[0] != MAGIC:
        return {"error": "not cramfs (bad magic)"}
    size, flags, name = struct.unpack("<II", data[4:12])[0], \
        struct.unpack("<I", data[8:12])[0], \
        data[48:64].rstrip(b"\x00").decode("utf-8", "replace")
    root = _ls(data, 64)
    if path:
        for ino in root:
            if ino["is_file"] and ino["name"] == path.lstrip("/"):
                return {"content": _read(data, ino)}
        return {"error": "path not found"}
    return {"fs_size": size, "name": name, "files": [
        {"name": i["name"], "size": i["size"], "mode": oct(i["mode"]),
         "dir": i["is_dir"]} for i in root]}


def _selftest():
    # one root dir inode containing one file inode
    name = b"flag.txt\x00\x00\x00"
    nl_field = ((12) >> 2) & 0x3F                    # namelen*4 = 12
    fblocks = 0x1000                               # blocks ptr area
    ino_file = struct.pack("<HHII", 0x81A4, 0,
                           17 | (0 << 24),
                           nl_field | ((fblocks >> 2) << 6)) + name
    dblocks = 64 + 12 + 4                          # root blocks_off
    dirsize = len(ino_file)
    ino_dir = struct.pack("<HHII", 0x41ED, 0,
                          dirsize | (0 << 24),
                          (1) | ((dblocks >> 2) << 6)) + b"/\x00\x00\x00"
    hdr = bytearray(64)
    struct.pack_into("<I", hdr, 0, MAGIC)
    struct.pack_into("<I", hdr, 4, 64 + len(ino_dir) + dirsize + 8)
    hdr[48:64] = b"TestFS".ljust(16, b"\x00")
    body = b"flag{cramfs_ok}"
    comp = zlib.compress(body)
    img = bytearray(bytes(hdr) + ino_dir)
    img = img.ljust(dblocks, b"\x00")
    img += ino_file
    img = img.ljust(fblocks, b"\x00")
    comp_off = fblocks + 4
    img += struct.pack("<I", comp_off)
    img += comp
    m = parse(bytes(img))
    names = [f["name"] for f in m.get("files", [])]
    assert "flag.txt" in names, m
    r = parse(bytes(img), "flag.txt")
    assert r["content"] == body, r
    print("cramfs_read selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="cramfs reader")
    ap.add_argument("path", nargs="?")
    ap.add_argument("cmd", nargs="?", default="list")
    ap.add_argument("arg", nargs="?")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("path required")
    r = parse(open(a.path, "rb").read(), a.arg if a.cmd == "get" else None)
    if a.cmd == "get" and "content" in r:
        sys.stdout.buffer.write(r["content"])
        return
    print(json.dumps(r, indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
