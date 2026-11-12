#!/usr/bin/env python3
"""e01_read.py -- EnCase EWF1 (.E01) sector reader.

`ewfmount`/libewf are absent, but EWF1's structure is stable: a 76B
file header, then sections -- 'volume' (media/chunk geometry),
'table' (a 4-byte-offset array whose bit 31 marks zlib-compressed
chunks), 'sectors' (the data), plus hash/digest/done. Chunks are
sectors-per-chunk * bytes-per-sector (commonly 64*512 = 32KiB). This
tool reads guest sectors through the table like fat_read reads FAT
images, so an .E01 handout feeds part_table/fat_read/ext_read without
libewf. Single-segment images only; a multi-segment set is reported
honestly.

  python3 tools/forensics/e01_read.py disk.E01 info
  python3 tools/forensics/e01_read.py disk.E01 read 0 512
  python3 tools/forensics/e01_read.py disk.E01 dump guest.img
  python3 tools/forensics/e01_read.py --selftest
"""
import argparse
import json
import struct
import sys
import zlib


class E01:
    def __init__(self, path):
        self.f = open(path, "rb")
        h = self.f.read(76)
        if not h.startswith(b"EVF\x09\x0d\x0a\xff\x00"):
            raise ValueError("not EWF1 (bad signature)")
        self.sections = []
        off = 76
        while True:
            self.f.seek(off)
            sh = self.f.read(76)
            if len(sh) < 76:
                break
            stype = sh[:16].split(b"\x00")[0].decode(
                "ascii", "replace")
            nxt, size = struct.unpack("<QQ", sh[16:32])
            self.sections.append({"type": stype, "off": off,
                                  "size": size, "data_off": off + 76})
            if nxt <= off or nxt == 0:
                break
            off = nxt
        self._vol = self._table = None

    def _sect(self, stype):
        for s in self.sections:
            if s["type"] == stype:
                return s
        return None

    def volume(self):
        if self._vol is None:
            s = self._sect("volume")
            if not s:
                raise ValueError("no volume section")
            self.f.seek(s["data_off"])
            d = self.f.read(1048)
            (media, _r1, chunks, spc, bps, nsec) = struct.unpack(
                "<B3sIIIQ", d[:24])
            self._vol = {"media_type": media, "chunks": chunks,
                         "sectors_per_chunk": spc,
                         "bytes_per_sector": bps,
                         "sector_count": nsec}
        return self._vol

    def table(self):
        if self._table is None:
            s = self._sect("table")
            if not s:
                raise ValueError("no table section")
            self.f.seek(s["data_off"])
            cnt = struct.unpack("<I", self.f.read(4))[0]
            self.f.read(20)
            self._table = [struct.unpack("<I", self.f.read(4))[0]
                           for _ in range(cnt)]
        return self._table

    def chunk(self, i):
        v = self.volume()
        ent = self.table()[i]
        comp = bool(ent & 0x80000000)
        off = ent & 0x7FFFFFFF
        import os
        nxt = self.table()[i + 1] & 0x7FFFFFFF \
            if i + 1 < len(self.table()) else os.path.getsize(
            self.f.name)
        self.f.seek(off)
        raw = self.f.read(nxt - off)
        want = v["sectors_per_chunk"] * v["bytes_per_sector"]
        if comp:
            return zlib.decompress(raw)
        return raw.ljust(want, b"\x00")[:want]

    def read(self, off, size):
        v = self.volume()
        csize = v["sectors_per_chunk"] * v["bytes_per_sector"]
        out = bytearray()
        while len(out) < size:
            i = off // csize
            if i >= v["chunks"]:
                break
            data = self.chunk(i)
            st = off % csize
            take = min(csize - st, size - len(out))
            out += data[st:st + take]
            off += take
        return bytes(out)

    def info(self):
        v = self.volume()
        return {**v, "sections": [s["type"] for s in self.sections],
                "guest_size": v["sector_count"] * v["bytes_per_sector"]}


def _selftest():
    spc, bps = 4, 512
    csize = spc * bps
    payload = b"flag{e01_chunk}".ljust(csize, b"\x00")
    comp = zlib.compress(payload)
    vol = struct.pack("<B3sIIIQ", 0, b"\x00" * 3, 1, spc, bps, spc)
    vol = vol.ljust(1048, b"\x00")
    hdr_off, tab_off = 76, 76 + 76 + 1048
    sec_off = tab_off + 76 + 28
    def sect(t, body, nxt):
        return (t.ljust(16, b"\x00") + struct.pack("<QQ", nxt,
                76 + len(body)) + b"\x00" * 40 + b"\x00" * 4 + body)
    chunk_off = sec_off + 76
    tab = struct.pack("<I", 1) + b"\x00" * 20 + struct.pack(
        "<I", chunk_off | 0x80000000)
    img = (b"EVF\x09\x0d\x0a\xff\x00" + b"\x00" * 68
           + sect(b"volume", vol, tab_off)
           + sect(b"table", tab, sec_off)
           + sect(b"sectors", comp, 0))
    import tempfile, os
    fd, path = tempfile.mkstemp(suffix=".E01")
    os.write(fd, img)
    os.close(fd)
    e = E01(path)
    assert e.info()["sector_count"] == spc
    got = e.read(0, 15)
    assert got == b"flag{e01_chunk}", got
    assert e.read(csize, 8) == b""       # beyond chunk count
    print("e01_read selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="EnCase EWF1 reader")
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
    e = E01(a.path)
    if a.cmd == "info":
        print(json.dumps(e.info(), indent=1))
    elif a.cmd == "read":
        off, size = int(a.args[0], 0), int(a.args[1], 0)
        sys.stdout.buffer.write(e.read(off, size))
    elif a.cmd == "dump":
        v = e.volume()
        csize = v["sectors_per_chunk"] * v["bytes_per_sector"]
        out = open(a.args[0], "wb")
        for i in range(v["chunks"]):
            out.write(e.chunk(i))
        print(json.dumps({"wrote": a.args[0],
                          "size": v["sector_count"] * v[
                              "bytes_per_sector"]}))


if __name__ == "__main__":
    raise SystemExit(main())
