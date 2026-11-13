#!/usr/bin/env python3
"""jffs2_read.py -- JFFS2 node walk for firmware dumps.

JFFS2 shows up on NOR-flash handouts (`dump.bin` from an IoT device)
where `jefferson`/`mtd-utils` are absent. Every node starts with
magic 0x1985, a nodetype, and total length: DIRENT (0xE002) carries
parent+name, INODE (0xE003) carries metadata + compressed data
(compr byte: 6=COPY uncompressed, 8=ZLIB). This tool walks nodes,
lists names with sizes/inodes, and extracts INODE data for COPY and
ZLIB compression -- other compressors are named, not guessed.

  python3 tools/forensics/jffs2_read.py flash.jffs2 list
  python3 tools/forensics/jffs2_read.py flash.jffs2 get <ino>
  python3 tools/forensics/jffs2_read.py --selftest
"""
import argparse
import json
import struct
import sys
import zlib

MAGIC = 0x1985
COMPR = {0: "RTIME", 1: "ZERO", 2: "RUBINMIPS", 3: "COPY",
         4: "DYNRUBIN", 5: "RTIME2", 6: "COPY", 7: "DYNRUBIN",
         8: "ZLIB", 9: "LZO"}


def walk(data):
    nodes = []
    i = 0
    while i + 12 <= len(data):
        if data[i:i + 4] in (b"\xff" * 4, b"\x00" * 4):
            i += 4
            continue
        magic, typ, totlen, _crc = struct.unpack(
            "<HHII", data[i:i + 12])
        if magic != MAGIC or totlen < 12 or i + totlen > len(data):
            i += 4
            continue
        body = data[i:i + totlen]
        if typ == 0xE002 and totlen >= 40:
            (_mg, _t, _tl, _c, pino, _ver, ino, _mtime,
             nsize, _utype, _un, _ncrc, _ncrc2) = struct.unpack(
                "<HHIIIIIIBBHII", body[:40])
            name = body[40:40 + nsize].decode("utf-8", "replace")
            nodes.append({"type": "dirent", "ino": ino,
                          "parent_ino": pino, "name": name})
        elif typ == 0xE003 and totlen >= 68:
            (_mg, _t, _tl, _c, ino, _ver, mode, _uid, _gid,
             isize, _at, _mt, _ct, doff, _csize, dsize,
             compr, _uc, _fl, _nc, _dc) = struct.unpack(
                "<HHIIIIIHHIIIIIIIBBHII", body[:68])
            nodes.append({"type": "inode", "ino": ino, "mode": oct(mode),
                          "isize": isize, "dsize": dsize,
                          "compr": COMPR.get(compr, "0x%x" % compr),
                          "data_off": i + 68})
        i += (totlen + 3) & ~3
    return nodes


def get(data, ino):
    out = b""
    for n in walk(data):
        if n["type"] != "inode" or n["ino"] != ino:
            continue
        raw = data[n["data_off"]:n["data_off"] + n["dsize"]]
        if n["compr"] == "ZLIB":
            raw = zlib.decompress(raw)
        elif n["compr"] not in ("COPY",):
            return {"error": "compression %s -- named, not decoded"
                    % n["compr"]}
        out += raw
    return {"ino": ino, "data": out}


def _selftest():
    def dirent(pino, ino, name):
        nb = name.encode()
        tot = 40 + len(nb)
        b = struct.pack("<HHIIIIIIBBHII", MAGIC, 0xE002, tot, 0,
                        pino, 1, ino, 0, len(nb), 8, 0, 0, 0) + nb
        return b + b"\x00" * ((4 - tot % 4) % 4)
    def inode(ino, body, compr=6):
        raw = body if compr == 6 else zlib.compress(body)
        h = struct.pack("<HHIIIIIHHIIIIIIIBBHII", MAGIC, 0xE003,
                        68 + len(raw), 0, ino, 1, 0o100644, 0, 0,
                        len(body), 0, 0, 0, 0, len(raw), len(raw),
                        compr, 0, 0, 0, 0)
        return h + raw
    img = dirent(1, 7, "flag.txt") + inode(7, b"flag{jffs2_node}")
    img += inode(8, b"x", 8)
    nodes = walk(img)
    names = [n.get("name") for n in nodes if n["type"] == "dirent"]
    assert "flag.txt" in names, nodes
    r = get(img, 7)
    assert r["data"] == b"flag{jffs2_node}", r
    z = get(img, 8)
    assert z["data"] == b"x", z
    print("jffs2_read selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="JFFS2 reader")
    ap.add_argument("path", nargs="?")
    ap.add_argument("cmd", nargs="?", default="list")
    ap.add_argument("arg", nargs="?")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("path required")
    data = open(a.path, "rb").read()
    if a.cmd == "get":
        r = get(data, int(a.arg, 0))
        if "data" in r:
            sys.stdout.buffer.write(r["data"])
        else:
            print(json.dumps(r))
        return
    print(json.dumps({"nodes": walk(data)}, indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
