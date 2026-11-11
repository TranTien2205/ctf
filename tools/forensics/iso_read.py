#!/usr/bin/env python3
"""iso_read.py -- ISO9660 reader: list paths, pull file extents.

.iso is a common forensics carrier (challenge bundles, hidden
tracks) and `isoinfo`/`bsdtar` are absent. This reads the Primary
Volume Descriptor at sector 16, walks variable-length directory
records (both-endian LBA/size fields, flags bit 2 = directory),
and reads file extents.

  python3 tools/forensics/iso_read.py cd.iso ls /
  python3 tools/forensics/iso_read.py cd.iso ls / -r
  python3 tools/forensics/iso_read.py cd.iso get /FLAG.TXT;1
  python3 tools/forensics/iso_read.py --selftest

Rock Ridge / Joliet supplementary names are reported when present
but the ISO name is the index. Version suffixes (`;1`) are kept —
that is the on-disc name and the get key. JSON out.
"""
import argparse
import json
import struct
import sys

SEC = 2048


def _both_endian_32(b, off):
    return struct.unpack("<I", b[off:off + 4])[0]


def _dirents(data, lba, size):
    raw = data[lba * SEC:lba * SEC + size]
    out, o = [], 0
    while o < len(raw):
        ln = raw[o]
        if ln == 0:
            o = (o // SEC + 1) * SEC
            continue
        if o + ln > len(raw):
            break
        rec = raw[o:o + ln]
        ext = _both_endian_32(rec, 2)
        dsz = _both_endian_32(rec, 10)
        flags = rec[25]
        nl = rec[32]
        name = rec[33:33 + nl]
        nm = ("\x00" if name == b"\x00" else
              "\x01" if name == b"\x01" else
              name.decode("latin-1", "replace"))
        out.append({"name": nm, "lba": ext, "size": dsz,
                    "dir": bool(flags & 2), "offset": o})
        o += ln
    return out


class Iso:
    def __init__(self, data):
        self.d = data
        pvd = data[16 * SEC:17 * SEC]
        if pvd[1:6] != b"CD001":
            raise ValueError("no PVD at sector 16")
        root = pvd[156:190]
        self.root_lba = _both_endian_32(root, 2)
        self.root_size = _both_endian_32(root, 10)
        self.pvd = {"volume_id": pvd[40:72].decode(
            "latin-1", "replace").strip(),
            "vol_size_sectors": struct.unpack("<I", pvd[80:84])[0],
            "logical_block_size": struct.unpack("<H", pvd[128:130])[0],
            "root_lba": self.root_lba}

    def ls(self, lba=None, size=None):
        return _dirents(self.d, lba or self.root_lba,
                        size or self.root_size)

    def find(self, lba=None, size=None, prefix=""):
        out = []
        for e in self.ls(lba, size):
            if e["name"] in ("\x00", "\x01"):
                continue
            p = prefix + "/" + e["name"]
            e2 = dict(e, path=p)
            out.append(e2)
            if e["dir"]:
                out.extend(self.find(e["lba"], e["size"], p))
        return out

    def read(self, e):
        o = e["lba"] * SEC
        return self.d[o:o + e["size"]]


def _selftest():
    img = bytearray(64 * SEC)

    def drec(lba, size, flags, name):
        nb = name if isinstance(name, bytes) else name.encode()
        ln = 33 + len(nb) + (len(nb) % 2 == 0)
        r = bytearray(ln)
        r[0] = ln
        struct.pack_into("<II", r, 2, lba, lba)
        struct.pack_into("<II", r, 10, size, size)
        r[25] = flags
        r[32] = len(nb)
        r[33:33 + len(nb)] = nb
        return bytes(r)

    root = (drec(20, SEC, 2, b"\x00") + drec(20, SEC, 2, b"\x01")
            + drec(30, 30, 0, b"FLAG.TXT;1")
            + drec(22, SEC, 2, b"SUBDIR"))
    img[16 * SEC:16 * SEC + 2048] = b"\x01CD001\x00" + b"\x00" * 2038
    pvd = memoryview(img)[16 * SEC:17 * SEC]
    pvd[40:60] = b"CTFVOL".ljust(20)
    struct.pack_into("<I", pvd, 80, 64)
    struct.pack_into("<H", pvd, 128, 2048)
    pvd[156:156 + len(drec(20, SEC, 2, b"\x00"))] = \
        drec(20, SEC, 2, b"\x00")
    del pvd
    img[20 * SEC:20 * SEC + len(root)] = root
    img[30 * SEC:30 * SEC + 30] = b"flag{iso_directory_walk}\x00" + \
        b"\x00" * 5
    sub = drec(20, SEC, 2, b"\x00") + drec(20, SEC, 2, b"\x01") + \
        drec(31, 11, 0, b"DEEP.TXT;1")
    img[22 * SEC:22 * SEC + len(sub)] = sub
    img[31 * SEC:31 * SEC + 11] = b"deep secret"
    i = Iso(bytes(img))
    assert i.pvd["volume_id"].startswith("CTFVOL")
    names = [e["name"] for e in i.ls()]
    assert "FLAG.TXT;1" in names and "SUBDIR" in names, names
    allp = i.find()
    paths = [e["path"] for e in allp]
    assert "/SUBDIR/DEEP.TXT;1" in paths, paths
    fe = next(e for e in allp if e["name"] == "FLAG.TXT;1")
    assert i.read(fe)[:25] == b"flag{iso_directory_walk}\x00"
    print("iso_read selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="ISO9660 reader")
    ap.add_argument("image", nargs="?")
    ap.add_argument("cmd", nargs="?", choices=["pvd", "ls", "get"])
    ap.add_argument("path", nargs="?", default="/")
    ap.add_argument("-r", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not (a.image and a.cmd):
        ap.error("image and cmd required")
    try:
        i = Iso(open(a.image, "rb").read())
    except ValueError as ex:
        sys.exit(str(ex))
    if a.cmd == "pvd":
        print(json.dumps(i.pvd, indent=1))
        return
    allents = i.find()
    if a.cmd == "ls":
        if a.r:
            print(json.dumps(allents, indent=1))
        else:
            pref = a.path.rstrip("/") or ""
            print(json.dumps([e for e in allents
                              if e["path"].rsplit("/", 1)[0] == pref],
                             indent=1))
        return
    hit = next((e for e in allents if e["path"] == a.path), None)
    if not hit:
        sys.exit(f"{a.path}: not found")
    sys.stdout.buffer.write(i.read(hit))


if __name__ == "__main__":
    raise SystemExit(main())
