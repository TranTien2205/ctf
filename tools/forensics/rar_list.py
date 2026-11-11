#!/usr/bin/env python3
"""rar_list.py -- RAR4/RAR5 archive member listing without unrar/7z.

`unrar`/`7z` are external; a .rar handout still needs an answer to
"what is inside, and is anything encrypted". RAR4 headers are
fixed-layout (HEAD_CRC/type/flags/size); RAR5 headers are uleb128
vints. Both are walkable read-only; this lists member names, packed
and unpacked sizes, directory/encrypted flags, and reports split
volumes or RAR5-encrypted headers honestly instead of guessing.

  python3 tools/forensics/rar_list.py a.rar
  python3 tools/forensics/rar_list.py a.rar --names   # names only
  python3 tools/forensics/rar_list.py --selftest

Metadata only: it does NOT decompress members (RAR compression is a
proprietary codec — no stdlib path).
"""
import argparse
import json
import struct
import sys

RAR4_MARK = b"Rar!\x1a\x07\x00"
RAR5_MARK = b"Rar!\x1a\x07\x01\x00"


def _vint(b, i):
    v, s = 0, 0
    while i < len(b):
        c = b[i]
        i += 1
        v |= (c & 0x7F) << s
        if not c & 0x80:
            return v, i
        s += 7
    raise ValueError("truncated vint")


def _rar4(data):
    out, i = [], len(RAR4_MARK)
    while i + 7 <= len(data):
        _crc, htype, flags, hsize = struct.unpack("<HBHH", data[i:i + 7])
        if htype == 0x7B or hsize < 7:
            break                                # end arc / corrupt
        if htype == 0x74:                        # file header
            h = data[i:i + hsize]
            pack, unp = struct.unpack("<II", h[7:15])
            host, method = h[15], h[25]
            nsize = struct.unpack("<H", h[26:28])[0]
            extra = 32
            if flags & 0x100:                    # LHD_LARGE
                hi_p, hi_u = struct.unpack("<II", h[32:40])
                pack |= hi_p << 32
                unp |= hi_u << 32
                extra = 40
            name = h[extra:extra + nsize]
            if flags & 0x200:                    # LHD_UNICODE name
                name = name.split(b"\x00")[0]
            out.append({"name": name.decode("utf-8", "replace"),
                        "packed": pack, "size": unp,
                        "method": method,
                        "dir": bool(flags & 0xE0 == 0xE0),
                        "encrypted": bool(flags & 0x04),
                        "split": bool(flags & 0x01)})
        add = struct.unpack("<I", data[i + 7:i + 11])[0] \
            if flags & 0x8000 else 0
        i += hsize + add
    return out


def _rar5(data):
    out, i = [], len(RAR5_MARK)
    while i + 5 <= len(data):
        try:
            hsize, p = _vint(data, i + 4)
        except ValueError:
            break
        hend = p + hsize
        if hend > len(data):
            break
        htype, p = _vint(data, p)
        hflags, p = _vint(data, p)
        if hflags & 1:
            _extra, p = _vint(data, p)
        dsize = 0
        if hflags & 2:
            dsize, p = _vint(data, p)
        if htype == 5:
            break                                # end of archive
        if htype == 4:
            return {"files": out,
                    "note": "RAR5 encryption header present: member "
                            "metadata itself is encrypted"}
        if htype in (2, 3) and p < hend:         # file or service
            body = data[p:hend]
            fflags, q = _vint(body, 0)
            unp, q = _vint(body, q)
            _attr, q = _vint(body, q)
            if fflags & 2:
                q += 4                           # mtime
            if fflags & 4:
                q += 4                           # crc32
            _comp, q = _vint(body, q)
            _host, q = _vint(body, q)
            nsize, q = _vint(body, q)
            name = body[q:q + nsize].decode("utf-8", "replace")
            out.append({"name": name, "packed": dsize, "size": unp,
                        "dir": bool(fflags & 1),
                        "encrypted": bool(hflags & 4)})
        i = hend + dsize
    return {"files": out}


def _selftest():
    def r4(name, pack, unp):
        h = struct.pack("<HBHH", 0, 0x74, 0x8000, 32 + len(name)) \
            + struct.pack("<II", pack, unp) + b"\x03" \
            + b"\x00" * 4 + b"\x00" * 4 + b"\x11\x30" \
            + struct.pack("<H", len(name)) + b"\x00" * 4
        return h + name + b"\x00" * pack
    img = RAR4_MARK + struct.pack("<HBHH", 0, 0x73, 0, 13) + b"\x00" * 6 \
        + r4(b"flag.txt", 20, 40) \
        + struct.pack("<HBHH", 0, 0x7B, 0, 7)
    files = _rar4(img)
    assert files[0]["name"] == "flag.txt" and files[0]["size"] == 40, files

    def v(vv):
        b = bytearray()
        while True:
            c = vv & 0x7F
            vv >>= 7
            b.append(c | 0x80 if vv else c)
            if not vv:
                return bytes(b)
    name = b"note.txt"
    body = v(0) + v(40) + v(0) + v(0) + v(0) + v(len(name)) + name
    inner = v(2) + v(2) + v(20) + body        # type, flags, dsize, body
    hdr = b"\x00" * 4 + v(len(inner)) + inner
    img5 = RAR5_MARK + hdr + b"\x00" * 20 \
        + b"\x00" * 4 + v(3) + v(5) + v(0) + b"\x00"
    d5 = _rar5(img5)
    assert d5["files"][0]["name"] == "note.txt" \
        and d5["files"][0]["size"] == 40, d5
    print("rar_list selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="RAR member listing")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--names", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("rar path required")
    data = open(a.path, "rb").read()
    if data.startswith(RAR4_MARK):
        res = {"format": "rar4", "files": _rar4(data)}
    elif data.startswith(RAR5_MARK):
        res = dict(_rar5(data), format="rar5")
    else:
        res = {"error": "not a rar"}
    if a.names and "files" in res:
        print("\n".join(f["name"] for f in res["files"]))
        return
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
