#!/usr/bin/env python3
"""qcow2_read.py -- read a qcow2 virtual disk without qemu-img.

`qemu-img` / `guestmount` are absent here, but the qcow2 v2/v3 layout
is documented: a BE header, an L1 table of L2-table pointers, and L2
tables of cluster descriptors. A descriptor's bit 63 marks the
cluster allocated, bit 62 marks it compressed (named and counted, not
decompressed -- convert with qemu-img if one appears), bit 61 (v3)
means reads-as-zero. This tool reads guest bytes
through the L1/L2 walk so a `.qcow2` handout can feed the rest of the
toolkit: pipe `read` output into part_table, fat_read or ext_read.

  python3 tools/forensics/qcow2_read.py disk.qcow2 info
  python3 tools/forensics/qcow2_read.py disk.qcow2 read 0 512
  python3 tools/forensics/qcow2_read.py disk.qcow2 dump guest.img
  python3 tools/forensics/qcow2_read.py --selftest
"""
import argparse
import json
import struct
import sys

OFL_COPIED = 1 << 63
OFL_COMPRESSED = 1 << 62
OFL_ZERO = 1 << 61
OFF_MASK = 0x3FFFFFFFFFFFFFFF


class Qcow2:
    def __init__(self, path):
        self.f = open(path, "rb")
        h = self.f.read(104)
        if h[:4] != b"QFI\xfb":
            raise ValueError("not qcow2")
        (self.version, back_off, back_sz, self.cluster_bits, self.vsize,
         self.crypt, self.l1_size, self.l1_off) = struct.unpack(
            ">IQIIQIIQ", h[4:4 + 44])
        self.csize = 1 << self.cluster_bits
        self.l2_entries = self.csize // 8
        self.backing = None
        if back_off:
            self.f.seek(back_off)
            self.backing = self.f.read(back_sz).decode(
                "utf-8", "replace")
        self._l1 = None
        self.compressed = 0

    def l1(self):
        if self._l1 is None:
            self.f.seek(self.l1_off)
            self._l1 = struct.unpack(
                ">%dQ" % self.l1_size, self.f.read(8 * self.l1_size))
        return self._l1

    def cluster(self, voff):
        """return data bytes for the cluster holding virtual offset."""
        gci = voff // self.csize
        l1i = gci // self.l2_entries
        if l1i >= self.l1_size:
            return b"\x00" * self.csize
        e = self.l1()[l1i]
        l2off = e & 0x00FFFFFFFFFFFE00
        if not l2off or not e & OFL_COPIED:
            return b"\x00" * self.csize
        self.f.seek(l2off)
        l2 = struct.unpack(">%dQ" % self.l2_entries,
                           self.f.read(self.csize))
        e2 = l2[gci % self.l2_entries]
        doff = e2 & OFF_MASK
        if e2 & OFL_ZERO or (not e2 & OFL_COPIED and not doff):
            return b"\x00" * self.csize
        if e2 & OFL_COMPRESSED:
            self.compressed += 1
            raise NotImplementedError(
                "compressed cluster at guest offset %d -- convert with "
                "qemu-img or carve around it" % voff)
        self.f.seek(doff)
        return self.f.read(self.csize)

    def read(self, off, size):
        out = bytearray()
        while len(out) < size and off < self.vsize:
            cl = off // self.csize * self.csize
            data = self.cluster(off)
            start = off - cl
            take = min(self.csize - start, size - len(out))
            out += data[start:start + take]
            off += take
        return bytes(out)

    def info(self):
        return {"version": self.version, "virtual_size": self.vsize,
                "cluster_bits": self.cluster_bits,
                "cluster_size": self.csize, "l1_entries": self.l1_size,
                "backing_file": self.backing,
                "encryption": self.crypt}


def _selftest():
    import io
    cbits = 16
    csz = 1 << cbits
    l1off = csz                    # after header (padded to cluster)
    l2off = l1off + csz
    dataoff = l2off + csz
    vsize = csz                    # one cluster virtual
    hdr = b"QFI\xfb" + struct.pack(
        ">IQIIQIIQ", 2, 0, 0, cbits, vsize, 0, 1, l1off)
    hdr = hdr.ljust(l1off, b"\x00")
    l1 = struct.pack(">Q", l2off | OFL_COPIED).ljust(csz, b"\x00")
    l2 = struct.pack(">Q", dataoff | OFL_COPIED).ljust(csz, b"\x00")
    body = b"flag{qcow2_guest}".ljust(csz, b"\x00")
    img = hdr + l1 + l2 + body
    import tempfile, os
    fd, path = tempfile.mkstemp(suffix=".qcow2")
    os.write(fd, img)
    os.close(fd)
    q = Qcow2(path)
    assert q.info()["virtual_size"] == vsize
    got = q.read(0, 17)
    assert got == b"flag{qcow2_guest}", got
    assert q.read(csz, 4) == b""     # beyond virtual size
    print("qcow2_read selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="qcow2 reader")
    ap.add_argument("path", nargs="?")
    ap.add_argument("cmd", nargs="?", default="info",
                    choices=["info", "read", "dump"])
    ap.add_argument("args", nargs="*")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("path required")
    q = Qcow2(a.path)
    if a.cmd == "info":
        print(json.dumps(q.info(), indent=1))
    elif a.cmd == "read":
        off, size = int(a.args[0], 0), int(a.args[1], 0)
        sys.stdout.buffer.write(q.read(off, size))
    elif a.cmd == "dump":
        out = open(a.args[0], "wb")
        for off in range(0, q.vsize, q.csize):
            out.write(q.cluster(off))
        print(json.dumps({"wrote": a.args[0], "size": q.vsize,
                          "compressed_clusters": q.compressed}))


if __name__ == "__main__":
    raise SystemExit(main())
