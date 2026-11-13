#!/usr/bin/env python3
"""vhd_read.py -- read a VHD virtual disk without the VHD toolchain.

A `.vhd` handout is either a fixed disk (raw bytes + a 512-byte
footer) or a dynamic/differencing disk (footer, a 'cxsparse' dynamic
header, and a Block Allocation Table mapping 2MiB-ish guest blocks to
sector offsets). This tool walks footer -> dynamic header -> BAT,
reading guest sectors like qcow2_read reads qcow2 -- flat output for
part_table/fat_read/ext_read. Differencing disks get a parent
locator; a missing parent is reported, not guessed.

  python3 tools/forensics/vhd_read.py disk.vhd info
  python3 tools/forensics/vhd_read.py disk.vhd read 0 512
  python3 tools/forensics/vhd_read.py disk.vhd dump guest.img
  python3 tools/forensics/vhd_read.py --selftest
"""
import argparse
import json
import struct
import sys


class Vhd:
    def __init__(self, path):
        self.f = open(path, "rb")
        import os
        self.size_on_disk = os.path.getsize(path)
        self.f.seek(self.size_on_disk - 512)
        foot = self.f.read(512)
        if foot[:8] != b"conectix":
            raise ValueError("not VHD (no conectix footer)")
        (_c, _feat, _ver, self.data_off, _ts, _app, _av, _os,
         self.orig_size, self.cur_size, _geom, dtype, _ck) = \
            struct.unpack(">8sIIQIIIIQQIII", foot[:68])
        self.dtype = dtype                        # 2=fixed 3=dynamic 4=diff
        self._bat = self._dyn = None
        if dtype in (3, 4):
            self.f.seek(self.data_off)
            dyn = self.f.read(1024)
            if dyn[:8] != b"cxsparse":
                raise ValueError("dynamic VHD without cxsparse header")
            (_c, _doff, self.tab_off, _hv, max_ent, self.bsize,
             _ck) = struct.unpack(">8sQQIIII", dyn[:40])
            self.max_ent = max_ent
            if dtype == 4:
                self.parent = self._parent_locator(dyn)
        self.bitmap_size = ((self.bsize // 512) // 8 + 511) // 512 * 512 \
            if self.dtype in (3, 4) else 0

    def _parent_locator(self, dyn):
        # parent locator entries start at dyn offset 576: 8 x 24B
        for i in range(8):
            o = 576 + i * 24
            plat, _dspace, dlen, _r, doff = struct.unpack(
                ">4sIIII", dyn[o:o + 20])
            if plat.strip(b"\x00") and doff:
                self.f.seek(doff)
                return self.f.read(dlen).decode("utf-16-le", "replace")
        return None

    def bat(self):
        if self._bat is None:
            self.f.seek(self.tab_off)
            self._bat = [struct.unpack(">I", self.f.read(4))[0]
                         for _ in range(self.max_ent)]
        return self._bat

    def block(self, i):
        ent = self.bat()[i]
        if ent == 0xFFFFFFFF:
            return b"\x00" * self.bsize
        self.f.seek(ent * 512 + self.bitmap_size)
        return self.f.read(self.bsize)

    def read(self, off, size):
        if self.dtype == 2:
            self.f.seek(off)
            return self.f.read(size)
        out = bytearray()
        while len(out) < size:
            i = off // self.bsize
            if i >= self.max_ent:
                break
            data = self.block(i)
            st = off % self.bsize
            take = min(self.bsize - st, size - len(out))
            out += data[st:st + take]
            off += take
        return bytes(out)

    def info(self):
        return {"type": {2: "fixed", 3: "dynamic", 4: "differencing"}.get(
            self.dtype, self.dtype),
            "virtual_size": self.cur_size,
            "block_size": getattr(self, "bsize", None),
            "bat_entries": getattr(self, "max_ent", None),
            "parent": getattr(self, "parent", None)
            if self.dtype == 4 else None}


def _selftest():
    bsize = 512 * 512                        # small block for fixture
    bitmap = 512
    nblocks = 1
    data = b"flag{vhd_guest}".ljust(bsize, b"\x00")
    tab_off = 1536
    blk_off_sectors = 5                      # sector offset = 2560
    dyn = (b"cxsparse" + struct.pack(">QQII", 0, tab_off, 1, nblocks)
           + struct.pack(">I", bsize) + struct.pack(">I", 0)
           + b"\x00" * 16 + struct.pack(">I", 0))
    dyn = dyn.ljust(1024, b"\x00")
    bat = struct.pack(">I", blk_off_sectors)
    body = b"\x00" * bitmap + data
    pad_to_blk = blk_off_sectors * 512 - (1536 + len(bat))
    head = dyn + bat + b"\x00" * pad_to_blk + body
    # footer: data_offset = 512 (dyn header right after)
    foot = (b"conectix" + struct.pack(">IIQ", 0, 0x10000, 512)
            + b"\x00" * 16 + struct.pack(">QQ", bsize, bsize)
            + struct.pack(">III", 0, 3, 0))
    foot = foot.ljust(512, b"\x00")
    img = foot + head + foot          # dynamic VHD leads with a copy
    import tempfile, os
    fd, path = tempfile.mkstemp(suffix=".vhd")
    os.write(fd, img)
    os.close(fd)
    v = Vhd(path)
    assert v.info()["type"] == "dynamic"
    got = v.read(0, 15)
    assert got == b"flag{vhd_guest}", got
    print("vhd_read selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="VHD reader")
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
    v = Vhd(a.path)
    if a.cmd == "info":
        print(json.dumps(v.info(), indent=1))
    elif a.cmd == "read":
        off, size = int(a.args[0], 0), int(a.args[1], 0)
        sys.stdout.buffer.write(v.read(off, size))
    elif a.cmd == "dump":
        out = open(a.args[0], "wb")
        for off in range(0, v.cur_size, v.bsize):
            out.write(v.block(off // v.bsize))
        print(json.dumps({"wrote": a.args[0], "size": v.cur_size}))


if __name__ == "__main__":
    raise SystemExit(main())
